"""Differential verification of recovered C++ kernels against canonical ARM64 bytes.

Runs bounded original instruction spans in Unicorn. Register/memory fixtures
represent the boundary after property selection and (where needed) native
normalization/magnitude. No mocked arithmetic helper is called, and any jump
outside the declared span fails closed. This is NOT whole-method or match proof.
"""
from __future__ import annotations

import hashlib
import json
import random
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.local' / 'pydeps'))
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as regs
import unicorn
from disassemble_spmove_runtime import file_offset

BINARY = ROOT / '.local/il2cpp/libil2cpp.so'
EXPECTED_SHA = '2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496'
PROBE = ROOT / '.local/build/reference/RecoveredKernelProbe.exe'
OUTPUT = ROOT / 'Recovery/Normalized/native_kernel_validation.json'
MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1
STACK = 0x09008000
TYPE_SLOT = 0x09000000
TYPE_OBJECT = 0x09000100

# End addresses are exclusive. No rewritten or generated machine instructions.
SPANS = {
    'multiply': (0x1B6B2B0, 0x1B6B2C4),
    'divide': (0x1B6B31C, 0x1B6B338),
    'vhor_first': (0x16E7104, 0x16E715C),
    'vhor_long': (0x16E7240, 0x16E7294),
    'vver_long': (0x16E9E4C, 0x16E9E84),
    'vver_push': (0x16E9F84, 0x16E9FB8),
    'vver_head': (0x16EA4D4, 0x16EA52C),
}


def signed32(value: int) -> int:
    value &= MASK32
    return value if value < (1 << 31) else value - (1 << 32)


def packed(x: int, y: int) -> int:
    return (x & MASK32) | ((y & MASK32) << 32)


class NativeKernel:
    def __init__(self, blob: bytes, name: str):
        self.name = name
        self.start, self.end = SPANS[name]
        offset = file_offset(blob, self.start)
        self.code = blob[offset:offset + self.end - self.start]
        self.mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        page = self.start & ~0xFFF
        limit = (self.end + 0xFFF) & ~0xFFF
        self.mu.mem_map(page, limit - page)
        self.mu.mem_write(self.start, self.code)
        self.mu.mem_map(TYPE_SLOT, 0x10000)
        self.mu.hook_add(UC_HOOK_CODE, self._guard)
        self.steps = 0

    def _guard(self, mu, address, size, _):
        if not self.start <= address < self.end or size != 4:
            raise RuntimeError(f'{self.name}: unexpected instruction address {address:#x}')
        self.steps += 1

    def set(self, register: str, value: int):
        self.mu.reg_write(getattr(regs, 'UC_ARM64_REG_' + register.upper()), value & MASK64)

    def get(self, register: str):
        return self.mu.reg_read(getattr(regs, 'UC_ARM64_REG_' + register.upper()))

    def run(self, a: int, b: int, x: int, y: int, z: int) -> tuple[int, int, int]:
        # Zero all GPRs/fixture memory each case to expose hidden dependencies.
        for index in range(31):
            self.set(f'x{index}', 0)
        self.set('nzcv', 0)
        self.set('sp', STACK)
        self.set('x29', STACK + 0xF0)
        self.mu.mem_write(TYPE_SLOT, bytes(0x10000))
        self.mu.mem_write(TYPE_SLOT, struct.pack('<Q', TYPE_OBJECT))
        # Class initialized; +0x12F flag 0 means no class-init call is taken.
        self.set('x8', TYPE_SLOT)
        self.set('x28', TYPE_SLOT)
        if self.name == 'multiply':
            self.set('x0', a)
            self.set('x1', b)
        elif self.name == 'divide':
            if b == 0:
                raise ValueError('native static-field fallback is outside this kernel')
            self.set('x20', a)
            self.set('x19', b)
        elif self.name.startswith('vhor'):
            self.set('x20', b)
            self.set('x22', a)
            if self.name == 'vhor_first':
                self.set('x24', packed(x, y))
                self.set('x25', z)
            else:
                self.set('x23', packed(x, y))
                self.set('x24', z)
        elif self.name in ('vver_long', 'vver_push'):
            self.set('x21', packed(x, y))
            self.set('x19', signed32(b))
            self.set('x23', signed32(z))
        elif self.name == 'vver_head':
            self.set('x21', a)
            self.set('x22', b)
            self.set('x19', packed(x, y))
            self.set('x20', z)
        self.steps = 0
        self.mu.emu_start(self.start, self.end, count=128)
        if self.get('pc') != self.end:
            raise RuntimeError(f'{self.name}: did not reach end, pc={self.get("pc"):#x}')
        if self.name == 'multiply':
            return signed32(self.get('x0')), 0, 0
        if self.name == 'divide':
            return signed32(self.get('x8')), 0, 0
        address = STACK + (0x48 if self.name.startswith('vhor') else 0x88)
        return struct.unpack('<iii', self.mu.mem_read(address, 12))


def corpus(name: str):
    rng = random.Random(0x53504D4F5645)
    edge = [-2147483648, -2147483647, -65537, -1025, -1024, -1023,
            -513, -512, -511, -3, -2, -1, 0, 1, 2, 3, 511, 512, 513,
            1023, 1024, 1025, 65537, 2147483646, 2147483647]
    if name in ('multiply', 'divide'):
        for a in edge:
            for b in edge:
                if name != 'divide' or b != 0:
                    yield a, b, 0, 0, 0
        for _ in range(1000):
            a, b = rng.randint(-2**31, 2**31-1), rng.randint(-2**31, 2**31-1)
            if name != 'divide' or b != 0:
                yield a, b, 0, 0, 0
    else:
        # Raw canonical per-level values + ties, zeros, negative factors,
        # wrapped magnitude sums/differences, all signs of packed components.
        params = [0, 1, -1, 511, 512, 513, 1024, 1500, 2000, 2500, 3000,
                  3500, 4000, 4500, 5000, 5500, 6000, 900, 800, 700, 600,
                  500, 300, 1200, -2147483648, 2147483647]
        vectors = [(0,0,0), (1024,0,0), (0,1024,0), (0,0,1024),
                   (-1024,-512,513), (511,-513,1), (2147483647,-2147483648,1025)]
        for b in params:
            for vector in vectors:
                for a in (0, 1, 1024, 30000, 2147483647, -2147483648):
                    yield a, b, *vector
        for _ in range(1000):
            yield tuple(rng.randint(-2**31,2**31-1) for _ in range(5))


def digest(path: Path):
    data = path.read_bytes()
    if path.suffix in ('.py', '.h', '.cpp'):
        data = data.decode('utf-8-sig').replace('\r\n', '\n').encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def main():
    blob = BINARY.read_bytes()
    if hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise RuntimeError('canonical libil2cpp.so hash mismatch')
    if not PROBE.is_file():
        raise RuntimeError('run Tools/build_reference.cmd first')
    source_paths = ['Reference/FootballCore/FixedPoint.h',
                    'Reference/FootballPhysics/SpmoveModifiers.h',
                    'Reference/FootballPhysics/NativeVectorMath.h',
                    'Reference/FootballPhysics/NativeSqrtTable.h',
                    'Tests/recovered_kernel_probe.cpp', 'Tools/verify_native_kernels.py']
    # Refuse stale probe. Content hashes below bind the complete evidence set.
    if any((ROOT/p).stat().st_mtime > PROBE.stat().st_mtime for p in source_paths[:-1]):
        raise RuntimeError('probe is older than its C++ sources; rebuild')
    groups = {}
    total = 0
    for name in SPANS:
        kernel = NativeKernel(blob, name)
        inputs = list(corpus(name))
        native = [kernel.run(*case) for case in inputs]
        payload = ''.join(name + ' ' + ' '.join(map(str, case)) + '\n' for case in inputs)
        process = subprocess.run([str(PROBE)], input=payload, text=True,
                                 capture_output=True, check=True)
        actual = [tuple(map(int, line.split())) for line in process.stdout.splitlines()]
        if len(actual) != len(native):
            raise AssertionError(f'{name}: probe output count mismatch')
        for i, (expected, observed) in enumerate(zip(native, actual)):
            if expected != observed:
                raise AssertionError(f'{name} input={inputs[i]} ARM64={expected} C++={observed}')
        groups[name] = {
            'start': hex(kernel.start), 'end_exclusive': hex(kernel.end),
            'instruction_bytes_sha256': hashlib.sha256(kernel.code).hexdigest(),
            'cases': len(inputs), 'mismatches': 0,
            'input_sha256': hashlib.sha256(payload.encode()).hexdigest(),
            'oracle_output_sha256': hashlib.sha256(json.dumps(native).encode()).hexdigest(),
        }
        total += len(inputs)
        print(f'NATIVE_KERNEL {name}: {len(inputs)}/{len(inputs)} MATCH')
    report = {
        'schema_version': 'football.recovery.native_kernel_validation.v1',
        'oracle': 'Unicorn ARM64 executing unmodified canonical machine-code spans',
        'unicorn_version': unicorn.__version__, 'binary_sha256': EXPECTED_SHA,
        'cpp_source_sha256': {p: digest(ROOT / p) for p in source_paths},
        'cpp_executable_sha256': digest(PROBE),
        'status': 'kernel_differential_pass', 'cases': total,
        'kernels': groups,
        'scope': 'arithmetic after branch/property/normalization boundary',
        'excluded': ['whole GetVHor/GetVVer/GetKickVelocity', 'property level selection',
                     'native normalization and sqrt', 'zero-divisor static fallback',
                     'BALL_CONTACT runtime integration', 'Unreal execution/performance'],
        'physics_v0_3_gate': 'blocked',
    }
    report['text_digest_canonicalization'] = 'UTF-8 without BOM, LF line endings'
    report['verification_source_sha256'] = {p: digest(ROOT/p) for p in ['Tools/disassemble_spmove_runtime.py', 'Tools/recover_native_sqrt_table.py', 'Tools/verify_native_kernels.py', 'Tools/verify_native_vector_math.py', 'Tools/verify_spmove_branches.py']}
    OUTPUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'NATIVE_KERNEL_DIFFERENTIAL: {total}/{total} MATCH (kernel scope only)')


if __name__ == '__main__':
    main()
