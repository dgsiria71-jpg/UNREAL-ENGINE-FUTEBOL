"""Record static parameter accesses inside the mobile GetVHor/GetVVer paths.

The normalized config and ARM64 listing are joined only at the level of raw
list index and fixed-point operation shape. No execution or unit/equation
claim is made; the Physics v0.3 gate remains blocked.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "disassembly_shoot.txt"
NORMALIZED = ROOT / "Recovery" / "Normalized" / "spmove_normalized.json"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_modifier_access_static_trace.json"
HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$")
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    sections: list[dict[str, str]] = []
    instructions: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        header = HEADER_RE.match(raw.strip())
        if header:
            current = {
                "name": header.group("name"),
                "start": "0x" + header.group("start").upper(),
                "end": "0x" + header.group("end").upper(),
            }
            sections.append(current)
            continue
        if current is None:
            continue
        line = LINE_RE.match(raw.strip())
        if line:
            instructions.append(
                {
                    "section": current["name"],
                    "address": "0x" + line.group("address").upper(),
                    "instruction": line.group("instruction").strip(),
                }
            )
    return sections, instructions


def require(instructions: list[dict[str, str]], section: str, address: str, fragment: str) -> dict[str, str]:
    for item in instructions:
        if item["section"] == section and item["address"].upper() == address.upper() and fragment.lower() in item["instruction"].lower():
            return item
    actual = [item for item in instructions if item["section"] == section and item["address"].upper() == address.upper()]
    raise ValueError(f"anchor {section} {address} missing {fragment!r}; actual={actual!r}")


def main() -> int:
    sections, instructions = parse(INPUT)
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    records = normalized["canonical_source"]["config"]["records"]
    errors: list[str] = []
    expected_sections = {
        "GetVHor": ("0x016E6A80", "0x016E84A4"),
        "GetVVer": ("0x016E84A4", "0x016EA55C"),
    }
    section_by_name = {section["name"]: section for section in sections}
    for name, span in expected_sections.items():
        if name not in section_by_name or (section_by_name[name]["start"], section_by_name[name]["end"]) != span:
            errors.append(name + " span changed or missing")

    anchor_specs = {
        "vhor_shoot_first_list_size": ("GetVHor", "0x016E70C8", "ldr      w8, [x26, #0x18]"),
        "vhor_shoot_first_param0": ("GetVHor", "0x016E70E8", "ldr      w20, [x8, #0x20]"),
        "vhor_shoot_first_add_sqrt": ("GetVHor", "0x016E7104", "add      x20, x20, x22"),
        "vhor_long_kick_list_size": ("GetVHor", "0x016E7200", "ldr      w8, [x25, #0x18]"),
        "vhor_long_kick_param1": ("GetVHor", "0x016E7224", "ldr      w20, [x8, #0x24]"),
        "vhor_long_kick_add_sqrt": ("GetVHor", "0x016E7240", "add      x20, x20, x22"),
        "vver_long_kick_items": ("GetVVer", "0x016E9E28", "ldr      x8, [x19, #0x10]"),
        "vver_long_kick_param2": ("GetVVer", "0x016E9E30", "ldrsw    x19, [x8, #0x28]"),
        "vver_long_kick_multiply": ("GetVVer", "0x016E9E58", "madd     x8, x8, x19, x9"),
        "vver_shoot_push_items": ("GetVVer", "0x016E9F5C", "ldr      x8, [x19, #0x10]"),
        "vver_shoot_push_param2": ("GetVVer", "0x016E9F64", "ldrsw    x19, [x8, #0x28]"),
        "vver_shoot_push_multiply": ("GetVVer", "0x016E9F98", "madd     x8, x8, x19, x9"),
        "vver_head_items": ("GetVVer", "0x016EA4B8", "ldr      x8, [x22, #0x10]"),
        "vver_head_param2": ("GetVVer", "0x016EA4C0", "ldr      w22, [x8, #0x28]"),
        "vver_head_multiply": ("GetVVer", "0x016EA50C", "madd     x8, x9, x8, x10"),
    }
    anchors: dict[str, dict[str, str]] = {}
    for name, (section, address, fragment) in anchor_specs.items():
        try:
            anchors[name] = require(instructions, section, address, fragment)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print("SPMOVE_MODIFIER_TRACE_ERROR: " + error)
        return 1

    groups = {
        "0x3FE": {"logic_id": 0x3FE, "method": "GetVHor", "flag": "ShootFirst", "param_index": 0, "list_data_offset": "0x20", "combination": "param[0] + sqrt_long(vector_sqr_raw)"},
        "0x3FC_vhor": {"logic_id": 0x3FC, "method": "GetVHor", "flag": "ShootLongKick", "param_index": 1, "list_data_offset": "0x24", "combination": "param[1] + sqrt_long(vector_sqr_raw)"},
        "0x3FC_vver": {"logic_id": 0x3FC, "method": "GetVVer", "flag": "ShootLongKick", "param_index": 2, "list_data_offset": "0x28", "combination": "fixed_point_vector_multiply_shape"},
        "0x41A_vver": {"logic_id": 0x41A, "method": "GetVVer", "flag": "shootPush", "param_index": 2, "list_data_offset": "0x28", "combination": "fixed_point_vector_multiply_shape"},
        "0x3FB_vver": {"logic_id": 0x3FB, "method": "GetVVer", "flag": "Head", "param_index": 2, "list_data_offset": "0x28", "combination": "fixed_point_vector_multiply_shape"},
    }
    for group in groups.values():
        matches = [record for record in records if record.get("logic_id") == group["logic_id"]]
        group["canonical_record_count"] = len(matches)
        group["canonical_levels"] = [record.get("level") for record in matches]
        group["canonical_param_at_index"] = [
            (record.get("param_raw") or [None] * (group["param_index"] + 1))[group["param_index"]]
            if len(record.get("param_raw") or []) > group["param_index"] else None
            for record in matches
        ]
        group["status"] = "list_index_and_operation_shape_only"

    report = {
        "schema_version": "football.recovery.spmove_modifier_access_static_trace.v1",
        "source": ".local/il2cpp/disassembly_shoot.txt",
        "source_sha256": sha256(INPUT),
        "binary": ".local/il2cpp/libil2cpp.so",
        "binary_sha256": normalized.get("canonical_source", {}).get("archive_sha256"),
        "source_scope": "canonical Android ARM64 libil2cpp.so",
        "analysis_status": "raw_param_index_and_fixed_point_operation_shape_only",
        "behavior_validated": False,
        "method_spans": [section_by_name[name] for name in expected_sections],
        "anchors": anchors,
        "modifier_accesses": groups,
        "confirmed_interpretation": [
            "GetVHor ShootFirst branch reads param_Xnumber list item index 0 at list-data offset +0x20 and adds it to a sqrt-derived raw value",
            "GetVHor ShootLongKick branch reads list item index 1 at list-data offset +0x24 and adds it to a sqrt-derived raw value",
            "GetVVer ShootLongKick, shootPush, and Head branches read list item index 2 at list-data offset +0x28 and feed fixed-point multiply-shaped code",
            "the normalized canonical groups preserve the raw parameter at each observed index for five levels where present",
        ],
        "unknown": [
            "whether the list values are scaled, clamped, or transformed later",
            "exact vector basis and meaning of the sqrt-derived value",
            "which config level the manager selects at runtime",
            "exact VHor/VVer equations and GetKickVelocity composition",
            "units and behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    # Bind the actual native hash instead of an archive hash; keep the field
    # explicit even though this report is created from the same binary.
    binary = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
    report["binary_sha256"] = sha256(binary) if binary.is_file() else None
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "SPMOVE_MODIFIER_TRACE: GREEN "
        f"groups={len(groups)} anchors={len(anchors)} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
