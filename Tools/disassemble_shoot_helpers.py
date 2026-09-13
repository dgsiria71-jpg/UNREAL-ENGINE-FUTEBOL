"""Read-only extractor for the small ARM64 helper regions used by shoot recovery."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / ".local" / "il2cpp" / "shoot_helper_disassembly.txt"

class Target(NamedTuple):
    name: str
    address: int
    fallback_bytes: int

class ResolvedRange(NamedTuple):
    target: Target
    start: int
    end: int
    boundary_source: str
    exact_function_boundary: bool
    metadata_name: str | None

DEFAULT_TARGETS = (
    Target("interpolate_remap_126BF1C", 0x126BF1C, 0x1000),
    Target("old_vver_helper_1968E24", 0x1968E24, 0x1000),
    Target("player_spmove_data_ratio_196807C", 0x196807C, 0x600),
)
MAX_EXACT_FUNCTION_BYTES = 0x20000
ADJACENT_WINDOW_BYTES = 0x200
MAX_ADJACENT_CALLEES = 48
CALL_RE = re.compile(r"#?0x([0-9a-fA-F]+)$")


def _as_address(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str):
        for base in (0, 16):
            try:
                return int(value.strip(), base)
            except ValueError:
                pass
    return None


def collect_script_methods(payload: Any) -> list[tuple[int, str]]:
    found: set[tuple[int, str]] = set()
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            address = next((_as_address(node[k]) for k in ("Address", "address", "RVA", "rva") if k in node and _as_address(node[k]) is not None), None)
            if address is not None:
                name = next((str(node[k]).strip() for k in ("Name", "name", "Signature") if node.get(k)), f"method_0x{address:X}")
                found.add((address, name))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(payload)
    return sorted(found)


def resolve_target_range(target: Target, methods: list[tuple[int, str]]) -> ResolvedRange:
    names = [name for address, name in methods if address == target.address]
    later = sorted({address for address, _ in methods if address > target.address}) if names else []
    if later and 0 < later[0] - target.address <= MAX_EXACT_FUNCTION_BYTES and (later[0] - target.address) % 4 == 0:
        return ResolvedRange(target, target.address, later[0], "script.json:next-method", True, names[0])
    return ResolvedRange(target, target.address, target.address + target.fallback_bytes, "bounded-fallback-window", False, names[0] if names else None)


def select_first_level_callees(direct_calls: dict[str, list[int]], *, primary_starts: set[int]) -> list[int]:
    values = {address for items in direct_calls.values() for address in items}
    return sorted(values - primary_starts)[:MAX_ADJACENT_CALLEES]


def build_summary(*, binary_sha256: str, metadata_path: Path | None, resolved_ranges: list[ResolvedRange], direct_calls: dict[str, list[int]]) -> dict[str, Any]:
    return {
        "schema_version": "football.recovery.shoot_helper_disassembly.v1",
        "binary_sha256": binary_sha256,
        "metadata": metadata_path.as_posix() if metadata_path else None,
        "targets": [{
            "name": item.target.name,
            "start": f"0x{item.start:08X}",
            "end": f"0x{item.end:08X}",
            "boundary_source": item.boundary_source,
            "exact_function_boundary": item.exact_function_boundary,
            "metadata_name": item.metadata_name,
            "direct_call_targets": [f"0x{x:08X}" for x in direct_calls.get(item.target.name, [])],
        } for item in resolved_ranges],
        "adjacent_window_bytes": ADJACENT_WINDOW_BYTES,
        "adjacent_callee_limit": MAX_ADJACENT_CALLEES,
        "policy": "static read-only extraction; fallback windows never claim exact function boundaries",
    }


def _metadata() -> tuple[Path | None, list[tuple[int, str]]]:
    for path in (ROOT / ".local" / "il2cpp" / "script.json", ROOT / ".local" / "tools" / "Il2CppDumper" / "script.json"):
        if path.is_file():
            return path, collect_script_methods(json.loads(path.read_text(encoding="utf-8-sig")))
    return None, []


def _validate_binary(blob: bytes) -> None:
    if len(blob) < 64 or blob[:4] != b"\x7fELF" or blob[4] != 2 or blob[5] != 1:
        raise ValueError("expected 64-bit little-endian ELF")
    machine = struct.unpack_from("<H", blob, 18)[0]
    if machine != 183:
        raise ValueError(f"expected AArch64 ELF (e_machine=183), got {machine}")


def _decode(decoder, blob: bytes, file_offset, item: ResolvedRange):
    start_offset = file_offset(blob, item.start)
    end_offset = file_offset(blob, item.end - 4) + 4
    instructions = list(decoder.disasm(blob[start_offset:end_offset], item.start))
    if len(instructions) != (item.end - item.start) // 4:
        raise ValueError(f"incomplete decode for {item.target.name}")
    return instructions


def _direct_calls(instructions) -> list[int]:
    direct: list[int] = []
    for instruction in instructions:
        if instruction.mnemonic != "bl":
            continue
        match = CALL_RE.search(instruction.op_str.strip())
        if match:
            direct.append(int(match.group(1), 16))
    return sorted(set(direct))


def _append_listing(lines: list[str], item: ResolvedRange, instructions, *, label: str) -> None:
    lines.append(f"### {label} {item.target.name} {item.start:08X}-{item.end:08X} boundary={item.boundary_source} exact={'true' if item.exact_function_boundary else 'false'}")
    if item.metadata_name:
        lines.append(f"METADATA_NAME: {item.metadata_name}")
    for instruction in instructions:
        operands = f" {instruction.op_str}" if instruction.op_str else ""
        lines.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")


def main() -> int:
    if not BINARY.is_file():
        raise FileNotFoundError(BINARY)
    sys.path.insert(0, str(ROOT / "Tools"))
    sys.path.insert(0, str(ROOT / ".local" / "pydeps"))
    from disassemble_spmove_manager import file_offset
    try:
        from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, Cs
    except ImportError as exc:
        raise SystemExit("capstone missing from .local/pydeps") from exc

    blob = BINARY.read_bytes()
    _validate_binary(blob)
    digest = hashlib.sha256(blob).hexdigest()
    metadata_path, methods = _metadata()
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    resolved = [resolve_target_range(target, methods) for target in DEFAULT_TARGETS]
    calls: dict[str, list[int]] = {}
    lines = [
        "FOOTBALL SHOOT HELPER STATIC EXTRACTION",
        f"BINARY_SHA256: {digest}",
        f"METADATA: {metadata_path.as_posix() if metadata_path else 'NONE'}",
        "POLICY: READ_ONLY; exact=false means bounded inspection window, not a proven full body",
        "",
    ]

    for item in resolved:
        instructions = _decode(decoder, blob, file_offset, item)
        calls[item.target.name] = _direct_calls(instructions)
        _append_listing(lines, item, instructions, label="TARGET")
        lines.append("DIRECT_CALL_TARGETS: " + (", ".join(f"0x{x:08X}" for x in calls[item.target.name]) or "NONE"))
        lines.append("")

    lines.append("## FIRST_LEVEL_DIRECT_CALLEE_WINDOWS")
    primary_starts = {item.start for item in resolved}
    emitted = 0
    for address in select_first_level_callees(calls, primary_starts=primary_starts):
        item = resolve_target_range(Target(f"callee_{address:08X}", address, ADJACENT_WINDOW_BYTES), methods)
        try:
            instructions = _decode(decoder, blob, file_offset, item)
        except ValueError as exc:
            lines.append(f"### CALLEE {address:08X} SKIPPED: {exc}")
            continue
        _append_listing(lines, item, instructions, label="CALLEE")
        lines.append("")
        emitted += 1
    lines.append(f"FIRST_LEVEL_CALLEES_EMITTED: {emitted}")
    lines.append("")

    summary = build_summary(binary_sha256=digest, metadata_path=metadata_path, resolved_ranges=resolved, direct_calls=calls)
    lines.append("## SUMMARY_JSON")
    lines.append(json.dumps(summary, sort_keys=True))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"SHOOT_HELPER_EXTRACTION: GREEN targets={len(resolved)} callees={emitted} output={OUTPUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
