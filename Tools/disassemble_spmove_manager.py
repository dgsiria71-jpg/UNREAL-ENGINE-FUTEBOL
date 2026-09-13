"""Disassemble the native spmove manager regions used by physics recovery.

This is an offline ARM64 inspection helper. It writes a deterministic text
listing for the analyzer; it never executes the mobile binary and never changes
runtime physics behavior.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / ".local" / "il2cpp" / "spmove_manager_disassembly.txt"
RANGES = [
    ("GetMaxSpmoveConfigByIds", 0x1B7264C, 0x1B72758),
    ("GetSpmoveData", 0x1B72758, 0x1B72794),
    ("GetSpmoveConfigByLogicId", 0x1B72794, 0x1B72814),
    ("GetSpmoveDataNoRatio", 0x1B72814, 0x1B72848),
    ("GetSpmovesConfigByLogicId", 0x1B72988, 0x1B72B38),
    ("GetSpmoveIds", 0x1B72DA8, 0x1B72E40),
]


def file_offset(blob: bytes, address: int) -> int:
    """Map an ELF virtual address/RVA to a file offset using PT_LOAD."""
    if blob[:4] != b"\x7fELF" or blob[4] != 2 or blob[5] != 1:
        raise ValueError("expected 64-bit little-endian ELF")
    phoff = struct.unpack_from("<Q", blob, 32)[0]
    phentsize, phnum = struct.unpack_from("<HH", blob, 54)
    for index in range(phnum):
        offset = phoff + index * phentsize
        p_type, _flags, p_offset, p_vaddr, _paddr, p_filesz, _memsz, _align = struct.unpack_from(
            "<IIQQQQQQ", blob, offset
        )
        if p_type == 1 and p_vaddr <= address < p_vaddr + p_filesz:
            return p_offset + (address - p_vaddr)
    raise ValueError(f"address 0x{address:X} is outside file-backed PT_LOAD")


def main() -> int:
    if not BINARY.is_file():
        raise FileNotFoundError(BINARY)
    sys.path.insert(0, str(ROOT / ".local" / "pydeps"))
    try:
        from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, Cs
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise SystemExit("capstone is required; install it in the ignored .local/pydeps environment") from exc

    blob = BINARY.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    lines: list[str] = []
    for name, start, end in RANGES:
        start_offset = file_offset(blob, start)
        end_offset = file_offset(blob, end - 4) + 4
        if end_offset <= start_offset:
            raise ValueError(f"invalid range {name}")
        lines.append(f"### {name} {start:08X}-{end:08X}")
        instructions = list(decoder.disasm(blob[start_offset:end_offset], start))
        expected_count = (end - start) // 4
        if len(instructions) != expected_count:
            raise ValueError(
                f"{name}: decoded {len(instructions)} instructions, expected {expected_count}"
            )
        for instruction in instructions:
            operands = f" {instruction.op_str}" if instruction.op_str else ""
            lines.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "SPMOVE_MANAGER_DISASSEMBLY: GREEN "
        f"ranges={len(RANGES)} bytes={len(blob)} sha256={digest} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
