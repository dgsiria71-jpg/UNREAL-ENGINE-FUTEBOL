"""Disassemble the native spmove buffer deserializers for schema evidence.

The listing is generated from the canonical Android ARM64 library. It is used
only to check field-write anchors and never executes mobile code.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / ".local" / "il2cpp" / "spmove_deserialize_disassembly.txt"
RANGES = [
    ("SpmoveActionDataConfigItemBuffer.deserialize", 0x1F7DCDC, 0x1F7DEAC),
    ("SpmoveConfigConfigItemBuffer.deserialize", 0x1F7DEAC, 0x1F7E0AC),
]


def file_offset(blob: bytes, address: int) -> int:
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
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("capstone is required; install it in ignored .local/pydeps") from exc
    blob = BINARY.read_bytes()
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    lines: list[str] = []
    for name, start, end in RANGES:
        start_offset = file_offset(blob, start)
        end_offset = file_offset(blob, end - 4) + 4
        lines.append(f"### {name} {start:08X}-{end:08X}")
        instructions = list(decoder.disasm(blob[start_offset:end_offset], start))
        if len(instructions) != (end - start) // 4:
            raise ValueError(f"{name}: incomplete instruction decode")
        for instruction in instructions:
            operands = f" {instruction.op_str}" if instruction.op_str else ""
            lines.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "SPMOVE_DESERIALIZE_DISASSEMBLY: GREEN "
        f"ranges={len(RANGES)} binary_sha256={hashlib.sha256(blob).hexdigest()} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
