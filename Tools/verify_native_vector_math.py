"""Verify native sqrt/normalization and composed modifiers against canonical ARM64.

Uses recovered metadata table; does not stub sqrt/normalize instructions.
Initialized-class memory fixtures replace IL2CPP startup only. Selection of
Spmove property lists remains outside the validated boundary.
"""
import hashlib
import json
import random
import struct
import subprocess
from pathlib import Path
from verify_native_kernels import (ROOT, BINARY, EXPECTED_SHA, PROBE, MASK64,
    TYPE_SLOT, TYPE_OBJECT, STACK, signed32, NativeKernel, digest)
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as regs
import unicorn
from disassemble_spmove_runtime import file_offset
from recover_native_sqrt_table import recover

REGIONS = [(0x1B64760, 0x1B64E50), (0x1936B4C, 0x1936C88)]
HALT = TYPE_SLOT + 0xF000


class NativeVectorOracle:
    def __init__(self, blob, table):
        self.mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        for start, end in REGIONS:
            self.mu.mem_map(start & ~0xFFF, ((end+0xFFF)&~0xFFF)-(start&~0xFFF))
            self.mu.mem_write(start, blob[file_offset(blob,start):file_offset(blob,end-4)+4])
        for base, size in [(TYPE_SLOT,0x10000),(0x4110000,0x1000),
                           (0x4368000,0x2000),(0x407F000,0x1000)]:
            self.mu.mem_map(base,size)
        self.mu.mem_write(TYPE_SLOT, struct.pack('<Q',TYPE_OBJECT))
        self.mu.mem_write(0x41102E8, struct.pack('<Q',TYPE_SLOT))
        self.mu.mem_write(0x407F9E8, struct.pack('<Q',TYPE_SLOT))
        self.mu.mem_write(TYPE_OBJECT+0xB8, struct.pack('<Q',TYPE_SLOT+0x400))
        self.mu.mem_write(TYPE_SLOT+0x418, struct.pack('<Q',TYPE_SLOT+0x1000))
        self.mu.mem_write(TYPE_SLOT+0x1020, struct.pack('<256i',*table))
        self.mu.mem_write(0x4368E5F,b'\x01')
        self.mu.mem_write(0x4369DE2,b'\x01')
        self.mu.hook_add(UC_HOOK_CODE, self.guard)

    def guard(self, mu, address, size, _):
        if size != 4 or not any(start<=address<end for start,end in REGIONS):
            raise RuntimeError(f'Unexpected native instruction {address:#x}')

    def run(self, method, a=0, vector=(0,0,0)):
        for i in range(31):
            self.mu.reg_write(getattr(regs, f'UC_ARM64_REG_X{i}'),0)
        self.mu.reg_write(regs.UC_ARM64_REG_NZCV,0)
        self.mu.reg_write(regs.UC_ARM64_REG_SP,STACK)
        self.mu.reg_write(regs.UC_ARM64_REG_X30,HALT)
        self.mu.mem_write(STACK-0x100,bytes(0x200))
        if method=='sqrt_long':
            address = REGIONS[0][0]
            self.mu.reg_write(regs.UC_ARM64_REG_X0,a & MASK64)
        else:
            address = REGIONS[1][0]
            self.mu.mem_write(TYPE_SLOT+0x800,struct.pack('<iii',*vector))
            self.mu.reg_write(regs.UC_ARM64_REG_X0,TYPE_SLOT+0x800)
        self.mu.emu_start(address,HALT,count=512)
        if self.mu.reg_read(regs.UC_ARM64_REG_PC)!=HALT:
            raise RuntimeError('Native method did not return')
        x0=self.mu.reg_read(regs.UC_ARM64_REG_X0)
        if method=='sqrt_long':
            return signed32(x0),0,0
        x1=self.mu.reg_read(regs.UC_ARM64_REG_X1)
        return signed32(x0),signed32(x0>>32),signed32(x1)


def inputs():
    rng=random.Random(0x584E554D424552)
    # Every LUT bucket at every even shift in the signed 64-bit domain,
    # and nearby branch/perfect-square boundaries.
    square_values=set(range(-3,260))
    for shift in range(0,57,2):
        for index in range(64,256):
            value=index<<shift
            if value < (1<<63): square_values.add(value)
    for bit in range(63):
        for delta in (-1,0,1):
            square_values.add((1<<bit)+delta)
    square_values.update([-2**63,2**63-1])
    for _ in range(1000): square_values.add(rng.randint(0,2**63-1))
    sq=[(a,0,0,0,0) for a in sorted(square_values)]
    vec=[(0,0,0,0,0)]
    for value in [1,2,3,10,511,512,1000,1013,1014,1023,1024,1025,1033,1034,1035,32767,100000,2147483647,-2147483648]:
        for sign in (-1,1):
            value_signed=value*sign
            if not -2**31<=value_signed<2**31: continue
            for axis in range(3):
                v=[0,0,0];v[axis]=value_signed
                vec.append((0,0,*v))
    for _ in range(1500):
        vec.append((0,0,*(rng.randint(-200000,200000) for _ in range(3))))
    for _ in range(1500):
        vec.append((0,0,*(rng.randint(-2**31,2**31-1) for _ in range(3))))
    composed=[]
    for case in vec:
        param=rng.choice([300,500,600,700,800,900,1200,1500,2000,3500,4000,6000])
        composed.append((0,param,*case[2:]))
    return {'sqrt_long':sq,'normalize3':vec,'vhor_prepared':composed,'head_prepared':composed}


def main():
    table=recover()
    blob=BINARY.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=EXPECTED_SHA: raise ValueError('binary mismatch')
    sources=['Reference/FootballCore/FixedPoint.h','Reference/FootballPhysics/SpmoveModifiers.h',
             'Reference/FootballPhysics/NativeVectorMath.h','Reference/FootballPhysics/NativeSqrtTable.h',
             'Tests/recovered_kernel_probe.cpp']
    if any((ROOT/p).stat().st_mtime>PROBE.stat().st_mtime for p in sources):
        raise RuntimeError('Rebuild Tools/build_reference.cmd first')
    oracle=NativeVectorOracle(blob,table['values'])
    first=NativeKernel(blob,'vhor_first')
    head=NativeKernel(blob,'vver_head')
    groups={}
    for name,cases in inputs().items():
        native=[]
        for a,b,x,y,z in cases:
            if name in ('sqrt_long','normalize3'):
                out=oracle.run(name,a,(x,y,z))
            else:
                norm=oracle.run('normalize3',vector=(x,y,z))
                squared=(x*x+y*y+z*z)&MASK64
                signed_sq=squared if squared<2**63 else squared-2**64
                magnitude=oracle.run('sqrt_long',signed_sq)[0]
                out=(first if name=='vhor_prepared' else head).run(magnitude,b,*norm)
            native.append(out)
        payload=''.join(name+' '+' '.join(map(str,c))+'\n' for c in cases)
        result=subprocess.run([str(PROBE)],input=payload,text=True,capture_output=True,check=True)
        actual=[tuple(map(int,line.split())) for line in result.stdout.splitlines()]
        if len(actual)!=len(native): raise AssertionError('Probe output count mismatch')
        for i,(expected,observed) in enumerate(zip(native,actual)):
            if expected!=observed:
                raise AssertionError(f'{name}: input={cases[i]} ARM64={expected} C++={observed}')
        groups[name]={'cases':len(cases),'mismatches':0,
                      'input_sha256':hashlib.sha256(payload.encode()).hexdigest(),
                      'oracle_output_sha256':hashlib.sha256(json.dumps(native).encode()).hexdigest()}
        print(f'NATIVE_VECTOR {name}: {len(cases)}/{len(cases)} MATCH')
    report={'schema_version':'football.recovery.native_vector_validation.v1',
            'binary_sha256':EXPECTED_SHA,'metadata_sha256':table['metadata_sha256'],
            'table_sha256':table['payload_sha256'],'unicorn_version':unicorn.__version__,
            'native_regions':[{'start':hex(s),'end_exclusive':hex(e)} for s,e in REGIONS],
            'status':'native_vector_differential_pass','cases':sum(v['cases'] for v in groups.values()),
            'groups':groups,'cpp_source_sha256':{p:digest(ROOT/p) for p in sources},
            'tool_sha256':digest(Path(__file__)),'cpp_executable_sha256':digest(PROBE),
            'scope':'full Sqrt_Long/get_normalized bodies with initialized static fixtures; composed modifier kernels',
            'excluded':['IL2CPP startup','spmove selection and branch eligibility','whole GetVHor/GetVVer/GetKickVelocity','BALL_CONTACT integration'],
            'physics_v0_3_gate':'blocked'}
    report['text_digest_canonicalization'] = 'UTF-8 without BOM, LF line endings'
    report['verification_source_sha256'] = {p: digest(ROOT/p) for p in ['Tools/disassemble_spmove_runtime.py', 'Tools/recover_native_sqrt_table.py', 'Tools/verify_native_kernels.py', 'Tools/verify_native_vector_math.py', 'Tools/verify_spmove_branches.py']}
    (ROOT/'Recovery/Normalized/native_vector_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'NATIVE_VECTOR_DIFFERENTIAL: {report["cases"]}/{report["cases"]} MATCH')


if __name__=='__main__': main()
