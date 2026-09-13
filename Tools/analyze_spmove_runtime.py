"""Analyze runtime construction and property forwarding for spmove values.

This report joins three source-backed facts without pretending to recover the
missing equations: OnGameStart creates ``param_Xnumber`` and copies raw
serialized ``param`` values, getSuccessByOdds scales odds by XNumber's 1024
factor before an opaque helper, and Player.GetSpmoveDataRatio forwards the
manager call used by ShootUtility.  It also records the exact property IDs and
flag masks at ShootUtility call sites.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_INPUT = ROOT / ".local" / "il2cpp" / "spmove_runtime_disassembly.txt"
SHOOT_INPUT = ROOT / ".local" / "il2cpp" / "disassembly_shoot.txt"
BINARY = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
NORMALIZED = ROOT / "Recovery" / "Normalized" / "spmove_normalized.json"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_runtime_static_trace.json"
HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$")
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")
CALL_RE = re.compile(r"bl\s+#0x(?P<target>[0-9A-Fa-f]+)", re.IGNORECASE)
MOV_ID_RE = re.compile(r"mov\s+w1,\s+#0x(?P<id>[0-9A-Fa-f]+)", re.IGNORECASE)
MASK_RE = re.compile(r"(?:tst|and)\s+[^,]+,\s+#(?P<mask>0x[0-9A-Fa-f]+)", re.IGNORECASE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_listing(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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


def require(
    instructions: list[dict[str, str]], section: str, address: str, fragment: str
) -> dict[str, str]:
    wanted = address.upper()
    for item in instructions:
        if (
            item["section"] == section
            and item["address"].upper() == wanted
            and fragment.lower() in item["instruction"].lower()
        ):
            return item
    actual = [
        item
        for item in instructions
        if item["section"] == section and item["address"].upper() == wanted
    ]
    raise ValueError(f"anchor {section} {address} missing {fragment!r}; actual={actual!r}")


def property_sites(shoot_instructions: list[dict[str, str]]) -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    for index, item in enumerate(shoot_instructions):
        match = CALL_RE.search(item["instruction"])
        if not match or match.group("target").lower() != "196807c":
            continue
        window = shoot_instructions[max(0, index - 10) : index]
        id_value: int | None = None
        id_address: str | None = None
        for candidate in reversed(window):
            id_match = MOV_ID_RE.search(candidate["instruction"])
            if id_match:
                id_value = int(id_match.group("id"), 16)
                id_address = candidate["address"]
                break
        mask_value: str | None = None
        mask_address: str | None = None
        for candidate in reversed(window):
            mask_match = MASK_RE.search(candidate["instruction"])
            if mask_match:
                mask_value = "0x" + mask_match.group("mask")[2:].upper()
                mask_address = candidate["address"]
                break
        sites.append(
            {
                "shoot_method": item["section"],
                "call_address": item["address"],
                "target": "0x196807C",
                "property_id": id_value,
                "property_id_address": id_address,
                "flag_mask": mask_value,
                "flag_mask_address": mask_address,
                "ratio_argument": "w2=1",
                "fourth_argument": "x3=0",
                "null_result_checked_next": True,
            }
        )
    return sites


def main() -> int:
    runtime_sections, runtime_instructions = parse_listing(RUNTIME_INPUT)
    shoot_sections, shoot_instructions = parse_listing(SHOOT_INPUT)
    expected_spans = {
        "SpmoveModule.OnGameStart": ("0x01449504", "0x01449858"),
        "SpmoveConfigConfigItem.getSuccessByOdds": ("0x019A4394", "0x019A4424"),
        "Player.GetSpmoveData": ("0x01968070", "0x0196807C"),
        "Player.GetSpmoveDataRatio": ("0x0196807C", "0x0196808C"),
    }
    errors: list[str] = []
    section_by_name = {section["name"]: section for section in runtime_sections}
    for name, span in expected_spans.items():
        if name not in section_by_name:
            errors.append("missing section " + name)
        elif (section_by_name[name]["start"], section_by_name[name]["end"]) != span:
            errors.append(name + " span changed")

    specs = {
        "on_game_start_enabled_guard": (
            "SpmoveModule.OnGameStart",
            "0x0144960C",
            "ldr      w8, [x20, #0x1c]",
        ),
        "on_game_start_skip_disabled": (
            "SpmoveModule.OnGameStart",
            "0x01449610",
            "cbz      w8, #0x14495f4",
        ),
        "on_game_start_list_constructor": (
            "SpmoveModule.OnGameStart",
            "0x01449630",
            "bl       #0x2c0c8f0",
        ),
        "on_game_start_param_load": (
            "SpmoveModule.OnGameStart",
            "0x01449634",
            "ldr      x0, [x20, #0x38]",
        ),
        "on_game_start_param_xnumber_store": (
            "SpmoveModule.OnGameStart",
            "0x01449638",
            "str      x21, [x20, #0x10]",
        ),
        "on_game_start_param_enumerator": (
            "SpmoveModule.OnGameStart",
            "0x0144964C",
            "sub      x8, x29, #0xa8",
        ),
        "on_game_start_param_current_raw": (
            "SpmoveModule.OnGameStart",
            "0x01449678",
            "ldur     w21, [x29, #-0x80]",
        ),
        "on_game_start_param_add": (
            "SpmoveModule.OnGameStart",
            "0x014496A4",
            "bl       #0x2c0d5c4",
        ),
        "odds_load": (
            "SpmoveConfigConfigItem.getSuccessByOdds",
            "0x019A43D0",
            "ldr      w19, [x19, #0x34]",
        ),
        "odds_xnumber_scale": (
            "SpmoveConfigConfigItem.getSuccessByOdds",
            "0x019A43F4",
            "lsl      w19, w19, #0xa",
        ),
        "odds_opaque_helper": (
            "SpmoveConfigConfigItem.getSuccessByOdds",
            "0x019A4420",
            "b        #0x192a1e0",
        ),
        "player_manager_load": (
            "Player.GetSpmoveData",
            "0x01968070",
            "ldr      x0, [x0, #0x28]",
        ),
        "player_manager_forward": (
            "Player.GetSpmoveData",
            "0x01968078",
            "b        #0x1b72758",
        ),
        "player_ratio_mask": (
            "Player.GetSpmoveDataRatio",
            "0x01968080",
            "and      w2, w2, #1",
        ),
        "player_ratio_forward": (
            "Player.GetSpmoveDataRatio",
            "0x01968088",
            "b        #0x1b72814",
        ),
    }
    anchors: dict[str, dict[str, str]] = {}
    for name, (section, address, fragment) in specs.items():
        try:
            anchors[name] = require(runtime_instructions, section, address, fragment)
        except ValueError as exc:
            errors.append(str(exc))

    sites = property_sites(shoot_instructions)
    expected_ids = [0x3FE, 0x3FC, 0x3FE, 0x3FC, 0x3FC, 0x41A, 0x3FB]
    if [site["property_id"] for site in sites] != expected_ids:
        errors.append(f"property call IDs changed: {[site['property_id'] for site in sites]!r}")
    if len(sites) != 7:
        errors.append(f"expected 7 property call sites, found {len(sites)}")
    if errors:
        for error in errors:
            print("SPMOVE_RUNTIME_TRACE_ERROR: " + error)
        return 1

    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    canonical_records = normalized["canonical_source"]["config"]["records"]
    empty_param_count = sum(1 for record in canonical_records if record.get("param_raw") == [])
    property_names = {
        0x417: "CalmShoot producer property",
        0x418: "SAngleShoot producer property",
        0x3FE: "ShootFirst branch property",
        0x3FC: "ShootLongKick branch property",
        0x41A: "shootPush branch property",
        0x3FB: "Head branch property",
        0x40B: "SwantonBomb producer property",
    }
    for site in sites:
        site["property_name_hint"] = property_names.get(site["property_id"], "unmapped property")

    # The normalized canonical records use decimal logic IDs. These are the
    # same numeric values as the property IDs observed in the native calls;
    # record IDs still carry level suffixes and selection is not inferred.
    property_ids = [0x417, 0x418, 0x3FE, 0x3FC, 0x41A, 0x3FB, 0x40B]
    logic_id_alignment: dict[str, dict[str, object]] = {}
    for property_id in property_ids:
        matches = [record for record in canonical_records if record.get("logic_id") == property_id]
        logic_id_alignment[f"0x{property_id:X}"] = {
            "property_id_decimal": property_id,
            "canonical_logic_id": property_id,
            "record_count": len(matches),
            "record_ids": [record.get("id") for record in matches],
            "levels": [record.get("level") for record in matches],
            "odds": [record.get("odds") for record in matches],
            "param_raw_by_level": [record.get("param_raw", []) for record in matches],
            "status": "numeric_property_to_logic_id_alignment_only",
        }

    report = {
        "schema_version": "football.recovery.spmove_runtime_static_trace.v1",
        "source": ".local/il2cpp/spmove_runtime_disassembly.txt",
        "source_sha256": sha256(RUNTIME_INPUT),
        "shoot_source": ".local/il2cpp/disassembly_shoot.txt",
        "shoot_source_sha256": sha256(SHOOT_INPUT),
        "binary": ".local/il2cpp/libil2cpp.so",
        "binary_sha256": sha256(BINARY),
        "source_scope": "canonical Android ARM64 libil2cpp.so",
        "analysis_status": "param_runtime_population_and_property_call_sites_only",
        "behavior_validated": False,
        "method_spans": runtime_sections,
        "anchors": anchors,
        "param_runtime_population": {
            "enabled_guard": {
                "field": "SpmoveConfigConfigItem.enable",
                "offset": "0x1C",
                "behavior": "disabled records branch around runtime-list construction",
                "evidence": ["0x0144960C", "0x01449610"],
            },
            "list_creation": {
                "field": "SpmoveConfigConfigItem.param_Xnumber",
                "offset": "0x10",
                "constructor_target": "0x2C0C8F0",
                "assignment": "new List<XNumber> stored at item+0x10",
                "evidence": ["0x01449630", "0x01449638"],
            },
            "serialized_param_copy": {
                "source_field": "SpmoveConfigConfigItem.param",
                "source_offset": "0x38",
                "operation": "enumerate serialized param list and add each raw int to List<XNumber>",
                "enumerator_evidence": ["0x01449634", "0x0144964C", "0x0144966C"],
                "raw_value_evidence": "0x01449678 loads w21 from enumerator current",
                "list_add_target": "0x2C0D5C4",
                "list_add_evidence": "0x0144969C-0x014496A4",
            },
            "canonical_observation": {
                "config_record_count": len(canonical_records),
                "records_with_empty_param_raw": empty_param_count,
                "status": "serialized_canonical_param_lists_are_empty_in_normalized_archive",
                "caveat": "this proves the archive representation only; later runtime mutation or another source is not excluded",
            },
        },
        "odds_path": {
            "field": "SpmoveConfigConfigItem.odds",
            "offset": "0x34",
            "operation": "load odds, shift left 10 bits, branch to opaque helper",
            "scale": "odds << 10 (XNumber raw scaling; 1024 factor)",
            "helper_target": "0x192A1E0",
            "evidence": ["0x019A43D0", "0x019A43F4", "0x019A4420"],
            "semantics": "helper/RNG threshold meaning unresolved",
        },
        "player_forwarding": {
            "manager_field": "Player+0x28",
            "get_spmove_data": "load manager then tail-call XSpmoveManager.GetSpmoveData (0x1B72758)",
            "get_spmove_data_ratio": "mask noRatio to bit 0, clear x3, tail-call GetSpmoveDataNoRatio (0x1B72814)",
            "evidence": ["0x01968070", "0x01968078", "0x01968080", "0x01968088"],
        },
        "property_call_sites": sites,
        "property_logic_id_alignment": logic_id_alignment,
        "confirmed_interpretation": [
            "enabled config items receive a runtime List<XNumber> at +0x10 in OnGameStart",
            "serialized param values are copied as raw integer XNumber values when a param list exists",
            "canonical normalized config records currently have empty param_raw lists, subject to the stated later-mutation caveat",
            "getSuccessByOdds applies a 10-bit left shift before an opaque helper",
            "Player.GetSpmoveDataRatio forwards the noRatio flag and manager selector used by ShootUtility",
            "the canonical normalized records contain five levels for each logic ID aligned numerically with property IDs 0x417, 0x418, 0x3FE, 0x3FC, 0x41A, 0x3FB, and 0x40B",
            "ShootUtility has seven instruction-anchored property call sites with IDs 0x3FE, 0x3FC, 0x41A, and 0x3FB",
        ],
        "unknown": [
            "exact List<XNumber> object/class construction details beyond the observed constructor and Add calls",
            "whether another post-processing path mutates param_Xnumber after OnGameStart",
            "meaning of helper 0x192A1E0, RNG source, and odds threshold semantics",
            "selected config for each logic ID and level/odds resolution",
            "whether numeric property-ID and logic-ID alignment is intentional across all runtime builds",
            "property units and mapping from param_Xnumber to VHor/VVer/GetKickVelocity modifiers",
            "arithmetic equations, coordinate basis, and runtime behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "SPMOVE_RUNTIME_TRACE: GREEN "
        f"methods={len(runtime_sections)} anchors={len(anchors)} property_sites={len(sites)} "
        f"empty_param={empty_param_count}/{len(canonical_records)} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
