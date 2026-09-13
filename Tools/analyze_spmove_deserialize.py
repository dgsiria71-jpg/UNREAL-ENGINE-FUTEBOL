"""Analyze native spmove buffer-deserializer field writes.

This report separates serialized schema evidence from runtime construction. A
missing store in the buffer reader is evidence that a field is not serialized
there; it is not a claim that the field can never be populated elsewhere.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "spmove_deserialize_disassembly.txt"
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_deserialize_static_trace.json"
SECTION_RE = re.compile(r"^###\s+(?P<name>[^ ]+)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$")
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def parse() -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)
    sections: dict[str, dict[str, str]] = {}
    instructions: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in INPUT.read_text(encoding="utf-8").splitlines():
        header = SECTION_RE.match(raw.strip())
        if header:
            current = {
                "name": header.group("name"),
                "start": "0x" + header.group("start").upper(),
                "end": "0x" + header.group("end").upper(),
            }
            sections[current["name"]] = current
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


def require(items: list[dict[str, str]], address: str, fragment: str) -> dict[str, str]:
    for item in items:
        if item["address"].upper() == address.upper() and fragment.lower() in item["instruction"].lower():
            return item
    actual = [item for item in items if item["address"].upper() == address.upper()]
    raise ValueError(f"anchor {address} missing {fragment!r}; actual={actual!r}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sections, instructions = parse()
    expected = {
        "SpmoveActionDataConfigItemBuffer.deserialize": ("0x01F7DCDC", "0x01F7DEAC"),
        "SpmoveConfigConfigItemBuffer.deserialize": ("0x01F7DEAC", "0x01F7E0AC"),
    }
    errors: list[str] = []
    for name, span in expected.items():
        if name not in sections or (sections[name]["start"], sections[name]["end"]) != span:
            errors.append(f"{name} span changed or missing")

    action_fields = [
        ("id", 0x10, "0x01F7DD84", "str      w0, [x21, #0x10]"),
        ("gear", 0x14, "0x01F7DDA8", "str      w0, [x21, #0x14]"),
        ("condition", 0x18, "0x01F7DDCC", "str      w0, [x21, #0x18]"),
        ("anim_list", 0x20, "0x01F7DDF4", "str      x0, [x21, #0x20]"),
        ("fancyId", 0x28, "0x01F7DE18", "str      w0, [x21, #0x28]"),
        ("spmove_check_ids", 0x30, "0x01F7DE38", "str      x0, [x21, #0x30]"),
        ("speed_fix_rate", 0x38, "0x01F7DE84", "str      x0, [x21, #0x38]"),
    ]
    config_fields = [
        ("id", 0x18, "0x01F7DF54", "str      w0, [x21, #0x18]"),
        ("enable", 0x1C, "0x01F7DF78", "str      w0, [x21, #0x1c]"),
        ("logicId", 0x20, "0x01F7DF9C", "str      w0, [x21, #0x20]"),
        ("childSpmoveIds", 0x28, "0x01F7DFC4", "str      x0, [x21, #0x28]"),
        ("level", 0x30, "0x01F7DFE8", "str      w0, [x21, #0x30]"),
        ("odds", 0x34, "0x01F7E00C", "str      w0, [x21, #0x34]"),
        ("param", 0x38, "0x01F7E02C", "str      x0, [x21, #0x38]"),
        ("buffId", 0x40, "0x01F7E050", "str      w0, [x21, #0x40]"),
        ("IsBuffId", 0x44, "0x01F7E068", "strb     w8, [x21, #0x44]"),
        ("order", 0x48, "0x01F7E08C", "str      w0, [x21, #0x48]"),
    ]
    anchors: dict[str, dict[str, str]] = {}
    for fields, prefix in ((action_fields, "action"), (config_fields, "config")):
        for field, _offset, address, fragment in fields:
            try:
                anchors[f"{prefix}_{field}"] = require(instructions, address, fragment)
            except ValueError as exc:
                errors.append(str(exc))
    config_instructions = [
        item for item in instructions if item["section"] == "SpmoveConfigConfigItemBuffer.deserialize"
    ]
    param_stores = [
        item for item in config_instructions
        if item["instruction"].lower().startswith("str") and "#0x10" in item["instruction"].lower()
    ]
    if param_stores:
        errors.append("config deserializer unexpectedly stores a field at +0x10")
    if errors:
        for error in errors:
            print("SPMOVE_DESERIALIZE_TRACE_ERROR: " + error)
        return 1

    report = {
        "schema_version": "football.recovery.spmove_deserialize_static_trace.v1",
        "source": ".local/il2cpp/spmove_deserialize_disassembly.txt",
        "source_sha256": sha256(INPUT),
        "binary": ".local/il2cpp/libil2cpp.so",
        "binary_sha256": sha256(BINARY) if BINARY.is_file() else None,
        "source_scope": "canonical Android ARM64 libil2cpp.so",
        "analysis_status": "deserializer_field_writes_only",
        "behavior_validated": False,
        "method_spans": list(sections.values()),
        "anchors": anchors,
        "serialized_fields": {
            "spmoveactiondata": [
                {"name": field, "offset": f"0x{offset:X}", "store": address}
                for field, offset, address, _fragment in action_fields
            ],
            "spmoveconfig": [
                {"name": field, "offset": f"0x{offset:X}", "store": address}
                for field, offset, address, _fragment in config_fields
            ],
        },
        "omitted_runtime_fields": [
            {
                "name": "param_Xnumber",
                "offset": "0x10",
                "type_evidence": "SpmoveConfigConfigItem.param_Xnumber",
                "deserializer_evidence": "no store at +0x10 in SpmoveConfigConfigItemBuffer.deserialize",
                "status": "runtime_field_not_serialized_in_this_buffer",
            }
        ],
        "confirmed_interpretation": [
            "the config buffer reader writes id, enable, logicId, childSpmoveIds, level, odds, param, buffId, IsBuffId, and order",
            "the config buffer reader does not write param_Xnumber at offset 0x10",
            "action buffer field writes match the normalized byte-consumption schema",
        ],
        "unknown": [
            "whether a constructor or manager post-processing populates param_Xnumber",
            "the source and units of any runtime-derived XNumber list",
            "selection, odds, level, and buff application semantics",
            "runtime behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("SPMOVE_DESERIALIZE_TRACE: GREEN sections=" + str(len(sections)) + " anchors=" + str(len(anchors)) + " output=" + str(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
