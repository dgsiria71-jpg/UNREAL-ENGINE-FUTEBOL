"""Disassemble runtime spmove construction and property forwarding regions.

The listing is generated from the canonical Android ARM64 libil2cpp.so. It is
an offline, source-backed inspection artifact: the mobile code is not executed
and no unresolved physics value is emitted from this tool.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / ".local" / "il2cpp" / "spmove_runtime_disassembly.txt"
RANGES = [
    ("SpmoveModule.OnGameStart", 0x1449504, 0x1449858),
    ("SpmoveConfigConfigItem.getSuccessByOdds", 0x19A4394, 0x19A4424),
    ("Player.GetSpmoveData", 0x1968070, 0x196807C),
    ("Player.GetSpmoveDataRatio", 0x196807C, 0x196808C),
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
        expected_count = (end - start) // 4
        if len(instructions) != expected_count:
            raise ValueError(f"{name}: decoded {len(instructions)} instructions, expected {expected_count}")
        for instruction in instructions:
            operands = f" {instruction.op_str}" if instruction.op_str else ""
            lines.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "SPMOVE_RUNTIME_DISASSEMBLY: GREEN "
        f"ranges={len(RANGES)} bytes={len(blob)} sha256={hashlib.sha256(blob).hexdigest()} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
