"""Extract the bounded native/metadata evidence needed to close new-path GetVVer.

This tool is deliberately read-only with respect to the canonical IL2CPP inputs.
It emits one textual report outside the native-input directories so that the
result can be committed and reviewed without publishing the source binaries.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".local" / "recovery-output" / "getvver_upstream_evidence.txt"

EXPECTED_SHA256 = {
    "dump.cs": "4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe",
    "script.json": "d15222efc79ebfe50074f385c0f5e5af4960fb43c5cf55a383ea32cba34ae799",
    "global-metadata.dat": "92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e",
    "libil2cpp.so": "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
}

# Reuse the already-tested ScriptMethod-only boundary policy from the shoot
# helper extractor. Importing through Tools works both when run directly and
# when loaded by the unittest suite.
sys.path.insert(0, str(ROOT / "Tools"))
from disassemble_shoot_helpers import (  # noqa: E402
    ADJACENT_WINDOW_BYTES,
    Target,
    _decode,
    _direct_calls,
    _validate_binary,
    collect_script_methods,
    resolve_target_range,
    select_first_level_callees,
)

REQUESTED_TARGETS = (
    Target("base_target_height_14DEFDC", 0x14DEFDC, 0x1000),
    Target("downward_random_1B60CC8", 0x1B60CC8, 0x1000),
)

FIELD_RE = re.compile(
    r"^\s*(?P<visibility>public|private|protected|internal)\s+"
    r"(?P<type>.+?)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;\s*//\s*"
    r"(?P<offset>0x[0-9A-Fa-f]+)\s*$"
)
CLASS_MARKER = "public class ShootSpeedConfigItem // TypeDefIndex: 7953"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_identity(path: Path, key: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256(path)
    expected = EXPECTED_SHA256[key]
    if actual != expected:
        raise ValueError(f"{key} SHA mismatch: expected {expected}, got {actual}")
    return actual


def canonical_sources(root: Path = ROOT) -> dict[str, Path]:
    return {
        "dump.cs": root / ".local" / "tools" / "Il2CppDumper" / "dump.cs",
        "script.json": root / ".local" / "tools" / "Il2CppDumper" / "script.json",
        "global-metadata.dat": root / ".local" / "il2cpp" / "global-metadata.dat",
        "libil2cpp.so": root / ".local" / "il2cpp" / "libil2cpp.so",
    }


def extract_shoot_speed_fields(text: str) -> list[dict[str, str]]:
    """Return exact field declarations from the canonical ShootSpeedConfigItem.

    Names are copied from dump.cs rather than inferred from the serialized
    parser. Only the runtime field window relevant to the recovered shoot
    equations (0x18..0x108) is emitted.
    """
    start = text.find(CLASS_MARKER)
    if start < 0:
        raise ValueError(f"missing metadata class marker: {CLASS_MARKER}")
    next_class = text.find("\npublic class ", start + len(CLASS_MARKER))
    block = text[start: next_class if next_class >= 0 else len(text)]

    fields: list[dict[str, str]] = []
    for raw in block.splitlines():
        match = FIELD_RE.match(raw)
        if not match:
            continue
        offset_value = int(match.group("offset"), 16)
        if not 0x18 <= offset_value <= 0x108:
            continue
        fields.append({
            "type": match.group("type").strip(),
            "name": match.group("name"),
            "offset": f"0x{offset_value:X}",
            "line": raw.strip(),
        })
    if not fields:
        raise ValueError("ShootSpeedConfigItem field window 0x18..0x108 is empty")
    fields.sort(key=lambda item: int(item["offset"], 16))
    return fields


def resolve_requested_targets(methods: list[tuple[int, str]]):
    return [resolve_target_range(target, methods) for target in REQUESTED_TARGETS]


def _listing_text(instructions) -> list[str]:
    result = []
    for instruction in instructions:
        operands = f" {instruction.op_str}" if instruction.op_str else ""
        result.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")
    return result


def render_report(
    *,
    identities: dict[str, str],
    fields: list[dict[str, str]],
    metadata_path: Path | None,
    resolved_ranges,
    listings: dict[str, list[str]],
    direct_calls: dict[str, list[int]],
    callee_sections: list[dict[str, Any]] | None = None,
) -> str:
    lines = [
        "FOOTBALL GETVVER UPSTREAM STATIC EVIDENCE",
        "POLICY: READ_ONLY; metadata names are copied, not inferred; exact=false means bounded inspection window only",
        "CANONICAL_BUILD: football-dream-be-a-pro-1-221-5",
        f"METADATA_SOURCE: {metadata_path.as_posix() if metadata_path else 'NONE'}",
        "",
        "## SOURCE_IDENTITIES",
    ]
    for key in ("dump.cs", "script.json", "global-metadata.dat", "libil2cpp.so"):
        lines.append(f"{key}: {identities[key]}")

    lines.extend(["", "## SHOOT_SPEED_CONFIG_ITEM_FIELDS_0x18_0x108"])
    for item in fields:
        lines.append(f"{item['offset']} | {item['type']} | {item['name']} | {item['line']}")

    lines.extend(["", "## REQUESTED_HELPERS"])
    for item in resolved_ranges:
        name = item.target.name
        lines.append(
            f"### {name} start=0x{item.start:08X} end=0x{item.end:08X} "
            f"boundary={item.boundary_source} exact={'true' if item.exact_function_boundary else 'false'}"
        )
        if item.metadata_name:
            lines.append(f"METADATA_NAME: {item.metadata_name}")
        else:
            lines.append("METADATA_NAME: NONE")
        lines.extend(listings.get(name, []))
        calls = direct_calls.get(name, [])
        lines.append("DIRECT_CALL_TARGETS: " + (", ".join(f"0x{x:08X}" for x in calls) if calls else "NONE"))
        lines.append("")

    lines.append("## FIRST_LEVEL_DIRECT_CALLEE_WINDOWS")
    for section in callee_sections or []:
        lines.append(
            f"### {section['name']} start=0x{section['start']:08X} end=0x{section['end']:08X} "
            f"boundary={section['boundary_source']} exact={'true' if section['exact'] else 'false'}"
        )
        if section.get("metadata_name"):
            lines.append(f"METADATA_NAME: {section['metadata_name']}")
        lines.extend(section.get("listing", []))
        lines.append("")

    summary = {
        "schema_version": "football.recovery.getvver_upstream_evidence.v1",
        "policy": "read-only extraction; only ScriptMethod can establish exact native boundaries",
        "source_sha256": identities,
        "field_count": len(fields),
        "targets": [
            {
                "name": item.target.name,
                "start": f"0x{item.start:08X}",
                "end": f"0x{item.end:08X}",
                "boundary_source": item.boundary_source,
                "exact_function_boundary": item.exact_function_boundary,
                "metadata_name": item.metadata_name,
                "direct_calls": [f"0x{x:08X}" for x in direct_calls.get(item.target.name, [])],
            }
            for item in resolved_ranges
        ],
    }
    lines.extend(["## SUMMARY_JSON", json.dumps(summary, sort_keys=True), ""])
    return "\n".join(lines)


def write_output(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    sources = canonical_sources()
    identities = {key: require_identity(path, key) for key, path in sources.items()}

    dump_text = sources["dump.cs"].read_text(encoding="utf-8-sig")
    fields = extract_shoot_speed_fields(dump_text)
    script_payload = json.loads(sources["script.json"].read_text(encoding="utf-8-sig"))
    methods = collect_script_methods(script_payload)
    resolved = resolve_requested_targets(methods)

    blob = sources["libil2cpp.so"].read_bytes()
    _validate_binary(blob)

    sys.path.insert(0, str(ROOT / ".local" / "pydeps"))
    from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, Cs
    from disassemble_spmove_manager import file_offset

    decoder = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    listings: dict[str, list[str]] = {}
    direct_calls: dict[str, list[int]] = {}
    for item in resolved:
        instructions = _decode(decoder, blob, file_offset, item)
        listings[item.target.name] = _listing_text(instructions)
        direct_calls[item.target.name] = _direct_calls(instructions)

    callee_sections: list[dict[str, Any]] = []
    primary_starts = {item.start for item in resolved}
    for address in select_first_level_callees(direct_calls, primary_starts=primary_starts):
        item = resolve_target_range(Target(f"callee_{address:08X}", address, ADJACENT_WINDOW_BYTES), methods)
        try:
            instructions = _decode(decoder, blob, file_offset, item)
        except ValueError:
            continue
        callee_sections.append({
            "name": item.target.name,
            "start": item.start,
            "end": item.end,
            "boundary_source": item.boundary_source,
            "exact": item.exact_function_boundary,
            "metadata_name": item.metadata_name,
            "listing": _listing_text(instructions),
        })

    report = render_report(
        identities=identities,
        fields=fields,
        metadata_path=Path(".local/tools/Il2CppDumper/script.json"),
        resolved_ranges=resolved,
        listings=listings,
        direct_calls=direct_calls,
        callee_sections=callee_sections,
    )
    write_output(OUTPUT, report)
    print(
        "GETVVER_UPSTREAM_EXTRACTION: GREEN "
        f"fields={len(fields)} targets={len(resolved)} callees={len(callee_sections)} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
