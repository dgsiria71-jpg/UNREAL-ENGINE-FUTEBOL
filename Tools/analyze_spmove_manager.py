"""Record the static spmove-manager boundary used by physics recovery.

The mobile native code is Android ARM64 and is not executed here. This report
captures only instruction-anchored data flow: which selector is called, where
its result is read, and why ``param_Xnumber`` remains a runtime derivation
boundary instead of a serialized table field.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "spmove_manager_disassembly.txt"
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_manager_static_trace.json"
SECTION_RE = re.compile(
    r"^###\s+(?P<name>[A-Za-z0-9_]+)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$"
)
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def parse() -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)
    sections: dict[str, dict[str, str]] = {}
    entries: list[dict[str, str]] = []
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
            entries.append(
                {
                    "section": current["name"],
                    "address": "0x" + line.group("address").upper(),
                    "instruction": line.group("instruction").strip(),
                }
            )
    return sections, entries


def require(entries: list[dict[str, str]], address: str, fragment: str) -> dict[str, str]:
    wanted = address.upper()
    for item in entries:
        if item["address"].upper() == wanted and fragment.lower() in item["instruction"].lower():
            return item
    actual = [item for item in entries if item["address"].upper() == wanted]
    raise ValueError(f"anchor {address} missing {fragment!r}; actual={actual!r}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sections, entries = parse()
    expected_spans = {
        "GetMaxSpmoveConfigByIds": ("0x01B7264C", "0x01B72758"),
        "GetSpmoveData": ("0x01B72758", "0x01B72794"),
        "GetSpmoveConfigByLogicId": ("0x01B72794", "0x01B72814"),
        "GetSpmoveDataNoRatio": ("0x01B72814", "0x01B72848"),
        "GetSpmovesConfigByLogicId": ("0x01B72988", "0x01B72B38"),
        "GetSpmoveIds": ("0x01B72DA8", "0x01B72E40"),
    }
    errors: list[str] = []
    for name, (start, end) in expected_spans.items():
        item = sections.get(name)
        if item is None:
            errors.append("missing section " + name)
        elif (item["start"], item["end"]) != (start, end):
            errors.append(name + " span changed")
    anchor_specs = {
        "get_data_selector": ("0x01B72764", "bl       #0x1b72794"),
        "get_data_nonempty": ("0x01B72780", "tbz      w8, #0, #0x1b72788"),
        "get_data_param_return": ("0x01B72784", "ldr      x0, [x19, #0x10]"),
        "selector_logic_ids": ("0x01B727D8", "bl       #0x1b72da8"),
        "selector_max_config": ("0x01B727FC", "b        #0x1b7264c"),
        "no_ratio_selector": ("0x01B72824", "bl       #0x1b72794"),
        "no_ratio_flag": ("0x01B72834", "tbz      w19, #0, #0x1b7283c"),
        "no_ratio_param_return": ("0x01B72838", "ldr      x0, [x8, #0x10]"),
        "max_id_selector": ("0x01B72688", "bl       #0x1b72fd4"),
        "max_id_lookup": ("0x01B726B8", "b        #0x1449858"),
        "ids_dictionary": ("0x01B72DE8", "bl       #0x1b71aac"),
        "ids_lookup": ("0x01B72E04", "bl       #0x2c6a4f8"),
        "logic_config_iteration": ("0x01B72A90", "ldr      x2, [x24]"),
        "logic_level_check": ("0x01B72A60", "ldr      w1, [x21, #0x10]"),
    }
    anchors: dict[str, dict[str, str]] = {}
    for name, (address, fragment) in anchor_specs.items():
        try:
            anchors[name] = require(entries, address, fragment)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print("SPMOVE_MANAGER_TRACE_ERROR: " + error)
        return 1

    report = {
        "schema_version": "football.recovery.spmove_manager_static_trace.v1",
        "source": ".local/il2cpp/spmove_manager_disassembly.txt",
        "source_sha256": sha256(INPUT),
        "binary": ".local/il2cpp/libil2cpp.so",
        "binary_sha256": sha256(BINARY) if BINARY.is_file() else None,
        "source_scope": "canonical Android ARM64 libil2cpp.so",
        "analysis_status": "manager_selection_control_flow_only",
        "behavior_validated": False,
        "method_spans": list(sections.values()),
        "anchors": anchors,
        "confirmed_data_flow": [
            {
                "operation": "GetSpmoveData",
                "flow": "GetSpmoveConfigByLogicId(logic_id) -> selected config -> param_Xnumber at config+0x10",
                "evidence": ["0x01B72764", "0x01B72784"],
            },
            {
                "operation": "GetSpmoveDataNoRatio",
                "flow": "GetSpmoveConfigByLogicId(logic_id) -> if noRatio -> param_Xnumber at config+0x10",
                "evidence": ["0x01B72824", "0x01B72834", "0x01B72838"],
            },
            {
                "operation": "GetSpmoveConfigByLogicId",
                "flow": "logic_id -> private GetSpmoveIds -> GetMaxSpmoveConfigByIds",
                "evidence": ["0x01B727D8", "0x01B727FC"],
            },
            {
                "operation": "private GetSpmoveIds",
                "flow": "manager dictionary -> lookup by logic_id -> list/nullable result",
                "evidence": ["0x01B72DE8", "0x01B72E04"],
            },
            {
                "operation": "GetMaxSpmoveConfigByIds",
                "flow": "GetMaxSpmoveIdByIds -> config lookup; selected config is nullable",
                "evidence": ["0x01B72688", "0x01B726B8"],
            },
        ],
        "normalized_boundary": {
            "field": "param_Xnumber",
            "record_offset": "0x10",
            "status": "runtime_field_not_serialized",
            "implication": "spmoveconfig records alone cannot supply GetSpmoveData velocity/property values",
            "safe_action": "preserve the field as unresolved and require a separate runtime derivation or proved source",
        },
        "selection_hints_only": [
            "GetSpmovesConfigByLogicId iterates candidate configs and reaches a level/odds path",
            "GetMaxSpmoveConfigByIds delegates to GetMaxSpmoveIdByIds and a config lookup",
        ],
        "unknown": [
            "exact meaning of helper 0x2C6A4F8 and dictionary/list lookup semantics",
            "which config wins when multiple IDs are present",
            "level, odds, success, and IsBuffId semantics in the selector",
            "serialized-to-runtime construction of param_Xnumber",
            "param_Xnumber units and relation to VHor/VVer/GetKickVelocity",
            "runtime behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("SPMOVE_MANAGER_TRACE: GREEN sections=" + str(len(sections)) + " anchors=" + str(len(anchors)) + " output=" + str(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
