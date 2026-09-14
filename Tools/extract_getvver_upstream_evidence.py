"""Extract bounded native/metadata evidence needed to close new-path GetVVer.

This tool is deliberately read-only with respect to canonical IL2CPP inputs.
It emits one textual report outside the native-input directories so the result
can be committed and reviewed without publishing source binaries.
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
    Target("goal_door_height_14DEFDC", 0x14DEFDC, 0x1000),
    Target("xnumber_create_1B60CC8", 0x1B60CC8, 0x1000),
    Target("shoot_property_1968398", 0x1968398, 0x1000),
    # These two targets are deliberately address-labelled until ScriptMethod
    # metadata proves their identities on the canonical local dump.
    Target("property_lookup_1967D38", 0x1967D38, 0x1000),
    Target("property_fallback_1B718D8", 0x1B718D8, 0x1000),
)

FIELD_RE = re.compile(
    r"^\s*(?P<visibility>public|private|protected|internal)\s+"
    r"(?P<type>.+?)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;\s*//\s*"
    r"(?P<offset>0x[0-9A-Fa-f]+)\s*$"
)
CLASS_DECL_RE = re.compile(
    r"(?m)^\s*(?:public|private|protected|internal)?\s*"
    r"(?:(?:sealed|abstract|static)\s+)*class\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_`.]*)\b[^\n]*$"
)
SHOOT_SPEED_CLASS = "ShootSpeedConfigItem"


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


def _class_block(text: str, class_name: str) -> str:
    matches = list(CLASS_DECL_RE.finditer(text))
    for index, match in enumerate(matches):
        declared = match.group("name").split(".")[-1].split("`")[0]
        if declared != class_name:
            continue
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end]
    raise ValueError(f"missing metadata class: {class_name}")


def extract_class_fields(
    text: str,
    class_name: str,
    min_offset: int,
    max_offset: int,
) -> list[dict[str, str]]:
    """Copy exact dump.cs field declarations for one named class/window."""
    block = _class_block(text, class_name)
    fields: list[dict[str, str]] = []
    for raw in block.splitlines():
        match = FIELD_RE.match(raw)
        if not match:
            continue
        offset_value = int(match.group("offset"), 16)
        if not min_offset <= offset_value <= max_offset:
            continue
        fields.append({
            "type": match.group("type").strip(),
            "name": match.group("name"),
            "offset": f"0x{offset_value:X}",
            "line": raw.strip(),
        })
    fields.sort(key=lambda item: int(item["offset"], 16))
    return fields


def _simple_declared_type(type_name: str) -> str:
    value = type_name.strip().replace("global::", "")
    while value.endswith("[]"):
        value = value[:-2].strip()
    if "<" in value:
        value = value.split("<", 1)[0].strip()
    return value.rsplit(".", 1)[-1].split("`")[0]


def extract_fields_for_declared_type(
    text: str,
    type_name: str,
    min_offset: int,
    max_offset: int,
) -> list[dict[str, str]]:
    return extract_class_fields(text, _simple_declared_type(type_name), min_offset, max_offset)


def extract_shoot_speed_fields(text: str) -> list[dict[str, str]]:
    fields = extract_class_fields(text, SHOOT_SPEED_CLASS, 0x18, 0x108)
    if not fields:
        raise ValueError("ShootSpeedConfigItem field window 0x18..0x108 is empty")
    return fields


def resolve_requested_targets(methods: list[tuple[int, str]]):
    return [resolve_target_range(target, methods) for target in REQUESTED_TARGETS]


def _listing_text(instructions) -> list[str]:
    result = []
    for instruction in instructions:
        operands = f" {instruction.op_str}" if instruction.op_str else ""
        result.append(f"{instruction.address:08X}: {instruction.mnemonic:<8}{operands}")
    return result


def _append_fields(lines: list[str], title: str, fields: list[dict[str, str]]) -> None:
    lines.extend(["", title])
    if not fields:
        lines.append("NONE")
        return
    for item in fields:
        lines.append(f"{item['offset']} | {item['type']} | {item['name']} | {item['line']}")


def render_report(
    *,
    identities: dict[str, str],
    fields: list[dict[str, str]],
    shoot_config_fields: list[dict[str, str]] | None = None,
    football_fields: list[dict[str, str]] | None = None,
    nested_bonus_type: str | None = None,
    nested_bonus_fields: list[dict[str, str]] | None = None,
    metadata_path: Path | None,
    resolved_ranges,
    listings: dict[str, list[str]],
    direct_calls: dict[str, list[int]],
    callee_sections: list[dict[str, Any]] | None = None,
) -> str:
    shoot_config_fields = shoot_config_fields or []
    football_fields = football_fields or []
    nested_bonus_fields = nested_bonus_fields or []
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

    _append_fields(lines, "## SHOOT_SPEED_CONFIG_ITEM_FIELDS_0x18_0x108", fields)
    _append_fields(lines, "## SHOOT_CONFIG_FIELDS_0x20_0x160", shoot_config_fields)
    _append_fields(lines, "## FOOTBALL_FIELDS_0x90_0xA0", football_fields)
    lines.extend(["", f"NESTED_BONUS_TYPE: {nested_bonus_type or 'NONE'}"])
    _append_fields(lines, "## NESTED_BONUS_FIELDS_0x40_0x44", nested_bonus_fields)

    lines.extend(["", "## REQUESTED_HELPERS"])
    for item in resolved_ranges:
        name = item.target.name
        lines.append(
            f"### {name} start=0x{item.start:08X} end=0x{item.end:08X} "
            f"boundary={item.boundary_source} exact={'true' if item.exact_function_boundary else 'false'}"
        )
        lines.append(f"METADATA_NAME: {item.metadata_name or 'NONE'}")
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
        "schema_version": "football.recovery.getvver_upstream_evidence.v2",
        "policy": "read-only extraction; only ScriptMethod can establish exact native boundaries",
        "source_sha256": identities,
        "field_count": len(fields),
        "shoot_config_field_count": len(shoot_config_fields),
        "football_field_count": len(football_fields),
        "nested_bonus_type": nested_bonus_type,
        "nested_bonus_field_count": len(nested_bonus_fields),
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
    canonical_text = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(canonical_text.encode("utf-8"))


def main() -> int:
    sources = canonical_sources()
    identities = {key: require_identity(path, key) for key, path in sources.items()}

    dump_text = sources["dump.cs"].read_text(encoding="utf-8-sig")
    fields = extract_shoot_speed_fields(dump_text)
    # GetShootProperty loads x22 from the ShootConfig singleton and then reads
    # +0x24/+0x148/+0x14C. Its x21 value is a Football instance (proven by
    # Football.get_position2D) and +0x98 is Football.lastKickParam.
    shoot_config_fields = extract_class_fields(dump_text, "ShootConfig", 0x20, 0x160)
    football_fields = extract_class_fields(dump_text, "Football", 0x90, 0xA0)

    nested_bonus_type: str | None = None
    nested_bonus_fields: list[dict[str, str]] = []
    bonus_candidates = [item for item in football_fields if item["offset"] == "0x98"]
    if bonus_candidates:
        nested_bonus_type = bonus_candidates[0]["type"]
        try:
            nested_bonus_fields = extract_fields_for_declared_type(
                dump_text, nested_bonus_type, 0x40, 0x44
            )
        except ValueError:
            # The exact declared type is still reported even when its class
            # declaration is unavailable/indirect in this dump.
            nested_bonus_fields = []

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
        shoot_config_fields=shoot_config_fields,
        football_fields=football_fields,
        nested_bonus_type=nested_bonus_type,
        nested_bonus_fields=nested_bonus_fields,
        metadata_path=Path(".local/tools/Il2CppDumper/script.json"),
        resolved_ranges=resolved,
        listings=listings,
        direct_calls=direct_calls,
        callee_sections=callee_sections,
    )
    write_output(OUTPUT, report)
    print(
        "GETVVER_UPSTREAM_EXTRACTION: GREEN "
        f"fields={len(fields)} shoot_config_fields={len(shoot_config_fields)} football_fields={len(football_fields)} "
        f"targets={len(resolved)} callees={len(callee_sections)} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
