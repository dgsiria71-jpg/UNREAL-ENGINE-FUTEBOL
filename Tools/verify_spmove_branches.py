"""Execute complete spmove modifier regions with selected-property fixtures.

GetSpmoveDataRatio is the ONLY hooked call: it returns already-selected
List<XNumber> records (or null) and validates the requested ID/noRatio ABI.
Normalization, sqrt, flags, guards, list indices, arithmetic, and sequencing
execute original canonical ARM64 instructions. Does not validate the manager.
"""
import hashlib
import json
import random
import struct
import subprocess
from pathlib import Path
from verify_native_vector_math import NativeVectorOracle, REGIONS
from verify_native_kernels import (ROOT, BINARY, EXPECTED_SHA, TYPE_SLOT,
                                   STACK, MASK32, MASK64, packed, digest)
from recover_native_sqrt_table import recover
from disassemble_spmove_runtime import file_offset
from unicorn import arm64_const as regs

SPANS={
    'vhor_a':(0x16E7020,0x16E7294),
    'vhor_b':(0x16E76AC,0x16E7920),
    'vver_ballistic':(0x16E9D4C,0x16E9FC4),
    'vver_head':(0x16EA364,0x16EA52C),
}
PROPERTY=0x196807C
GOAL=TYPE_SLOT+0x3000
PLAYER=TYPE_SLOT+0x3400
PROBE=ROOT/'.local/build/reference/SpmoveBranchesProbe.exe'


class NativeBranches(NativeVectorOracle):
    def __init__(self,blob,table):
        self.active=None
        self.lookups=[]
        self.available={}
        super().__init__(blob,table)
        for base,size in [(0x16E7000,0x4000),(0x1968000,0x1000),(0x4365000,0x1000)]:
            self.mu.mem_map(base,size)
        for start,end in SPANS.values():
            self.mu.mem_write(start,blob[file_offset(blob,start):file_offset(blob,end-4)+4])
        self.mu.mem_write(PROPERTY,blob[file_offset(blob,PROPERTY):file_offset(blob,PROPERTY)+16])
        self.mu.mem_write(0x4365E29,b'\x01')
        self.mu.mem_write(GOAL+0x1B0,struct.pack('<Q',PLAYER))

    def guard(self,mu,address,size,_):
        if address==PROPERTY:
            if self.get('x0')!=PLAYER or self.get('x2')!=1 or self.get('x3')!=0:
                raise AssertionError('Unexpected property ABI')
            key=self.get('x1')
            if key not in (0x3FE,0x3FC,0x41A,0x3FB): raise AssertionError('Unexpected property ID')
            self.lookups.append(key)
            self.set('x0',self.available.get(key,0))
            self.set('pc',self.get('x30'))
            return
        allowed=REGIONS+[SPANS[self.active]]
        if size!=4 or not any(s<=address<e for s,e in allowed):
            raise RuntimeError(f'Unexpected instruction at {address:#x}')

    def get(self,name): return self.mu.reg_read(getattr(regs,'UC_ARM64_REG_'+name.upper()))
    def set(self,name,value): self.mu.reg_write(getattr(regs,'UC_ARM64_REG_'+name.upper()),value&MASK64)

    def branch(self,name,flags,present,x,y,z,first,long_kick,push,head):
        self.active=name
        self.lookups=[]
        self.available={}
        for i in range(31):self.set(f'x{i}',0)
        self.set('nzcv',0)
        self.set('sp',STACK)
        self.set('x29',STACK+0xF0)
        self.mu.mem_write(STACK-0x100,bytes(0x300))
        for index,(key,values) in enumerate([(0x3FE,[first,0,0]),(0x3FC,[0,long_kick,long_kick]),
                                             (0x41A,[0,0,push]),(0x3FB,[0,0,head])]):
            if present&(1<<index):
                pointer=TYPE_SLOT+0x4000+index*0x200
                self.available[key]=pointer
                self.mu.mem_write(pointer,bytes(0x200))
                self.mu.mem_write(pointer+0x10,struct.pack('<QI',pointer+0x100,3))
                self.mu.mem_write(pointer+0x120,struct.pack('<iii',*values))
        self.mu.mem_write(STACK+0x20,struct.pack('<Q',flags))
        self.mu.mem_write(STACK+0x68,struct.pack('<Q',flags))
        self.set('x28',TYPE_SLOT)
        if name.startswith('vhor'):
            self.set('x19',TYPE_SLOT)
            self.set('x23',GOAL)
            out=STACK+0x48
            self.mu.mem_write(out,struct.pack('<iii',x,y,z))
        else:
            out=STACK+0x88
            self.mu.mem_write(out,struct.pack('<iii',x,y,z))
            self.mu.mem_write(STACK+0x78,struct.pack('<Q',z&MASK32))
            self.set('x27',GOAL)
            if name=='vver_ballistic':
                self.set('x21',packed(x,y))
                self.set('x23',x&MASK32)
                self.set('x24',y&MASK32)
                self.set('x25',0x4365000)
            else:
                self.set('x13',flags)
                self.set('x8',(x&MASK32)<<10)
                self.set('x9',(z&MASK32)<<10)
                self.set('x21',(y&MASK32)<<32)
                self.set('x19',y&MASK32)
                self.set('x24',TYPE_SLOT)
                self.set('x26',TYPE_SLOT)
        start,end=SPANS[name]
        self.mu.emu_start(start,end,count=4096)
        if self.get('pc')!=end: raise RuntimeError('Native modifier region did not finish')
        return struct.unpack('<iii',self.mu.mem_read(out,12))


def cases():
    rng=random.Random(0x53504D4F564542)
    flag_cases=[0,1,1<<24,1<<32,1<<40,(1<<24)|(1<<40),1|(1<<40),
                (1<<56)-1,0xFE<<24,0x80<<40,0xFF<<32,0xFF]
    vectors=[(0,0,0),(1,-1,1),(1023,0,0),(3072,4096,0),(0,24000,0),
             (-14000,1,-24000),(2147483647,-2147483648,2147483647)]
    for flags in flag_cases:
        for present in range(16):
            for v in vectors:
                yield flags,present,*v,1500,900,700,600
    for _ in range(600):
        yield (rng.choice(flag_cases),rng.randrange(16),
               *(rng.randint(-200000,200000) for _ in range(3)),
               *(rng.choice([0,1,-1,300,900,1500,3500,6000,-2147483648,2147483647]) for _ in range(4)))


def main():
    table=recover()
    blob=BINARY.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=EXPECTED_SHA:raise ValueError('binary mismatch')
    sources=['Reference/FootballCore/FixedPoint.h','Reference/FootballPhysics/SpmoveModifiers.h',
             'Reference/FootballPhysics/NativeVectorMath.h','Reference/FootballPhysics/NativeSqrtTable.h',
             'Reference/FootballPhysics/SpmoveBranches.h','Tests/spmove_branches_probe.cpp']
    if any((ROOT/p).stat().st_mtime>PROBE.stat().st_mtime for p in sources):
        raise RuntimeError('Rebuild Tools/build_reference.cmd')
    oracle=NativeBranches(blob,table['values'])
    groups={}
    inputs=list(cases())
    for name in SPANS:
        expected=[]
        lookup_counts={}
        for case in inputs:
            expected.append(oracle.branch(name,*case))
            key=','.join(hex(v) for v in oracle.lookups) or 'none'
            lookup_counts[key]=lookup_counts.get(key,0)+1
        payload=''.join(name+' '+' '.join(map(str,c))+'\n' for c in inputs)
        result=subprocess.run([str(PROBE)],input=payload,text=True,capture_output=True,check=True)
        actual=[tuple(map(int,line.split())) for line in result.stdout.splitlines()]
        if len(actual)!=len(expected):raise AssertionError('C++ output count mismatch')
        for i,(a,b) in enumerate(zip(expected,actual)):
            if a!=b:raise AssertionError(f'{name} input={inputs[i]} ARM64={a} C++={b}')
        start,end=SPANS[name]
        groups[name]={'start':hex(start),'end_exclusive':hex(end),'cases':len(inputs),'mismatches':0,
                      'observed_property_sequences':lookup_counts,
                      'input_sha256':hashlib.sha256(payload.encode()).hexdigest(),
                      'native_output_sha256':hashlib.sha256(json.dumps(expected).encode()).hexdigest()}
        print(f'NATIVE_SPMOVE_BRANCH {name}: {len(inputs)}/{len(inputs)} MATCH')
    report={'schema_version':'football.recovery.native_spmove_branches.v1',
            'status':'selected_property_branch_differential_pass','binary_sha256':EXPECTED_SHA,
            'metadata_sha256':table['metadata_sha256'],'groups':groups,
            'cases':sum(g['cases'] for g in groups.values()),
            'hooked_boundary':{'address':hex(PROPERTY),'method':'Player.GetSpmoveDataRatio',
                               'behavior':'injected already-selected List<XNumber> or null; noRatio ABI asserted'},
            'cpp_source_sha256':{p:digest(ROOT/p) for p in sources},
            'cpp_executable_sha256':digest(PROBE),'tool_sha256':digest(Path(__file__)),
            'excluded':['which level/record is selected','calSpmoveInUse eligibility',
                        'GetVHor/GetVVer base calculation','GetKickVelocity/BALL_CONTACT'],
            'physics_v0_3_gate':'blocked'}
    report['text_digest_canonicalization'] = 'UTF-8 without BOM, LF line endings'
    report['verification_source_sha256'] = {p: digest(ROOT/p) for p in ['Tools/disassemble_spmove_runtime.py', 'Tools/recover_native_sqrt_table.py', 'Tools/verify_native_kernels.py', 'Tools/verify_native_vector_math.py', 'Tools/verify_spmove_branches.py']}
    (ROOT/'Recovery/Normalized/native_spmove_branch_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'NATIVE_SPMOVE_BRANCH_DIFFERENTIAL: {report["cases"]}/{report["cases"]} MATCH')


if __name__=='__main__':main()
