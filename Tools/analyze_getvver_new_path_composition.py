"""Bind the new-path GetVVer composition and its recovered raw-map producers."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
UPSTREAM = ROOT / "artifacts" / "native-recovery" / "getvver-upstream" / "20260913-204613-86a0f84a" / "01_getvver_upstream_evidence.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "getvver_new_path_composition_static_trace.json"
SOURCE_LF_SHA256 = "c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4"
UPSTREAM_SHA256 = "416a4f3abef88c117aa21bb66c4500f83474442e6e78a494d84ac1b4914d224f"
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def _lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _norm(value: str) -> str:
    return " ".join(value.strip().split())


def parse_instructions(path: Path) -> dict[int, str]:
    result: dict[int, str] = {}
    for raw in _lf_bytes(path).decode("utf-8").splitlines():
        match = LINE_RE.match(raw.strip())
        if match:
            result[int(match.group("address"), 16)] = _norm(match.group("instruction"))
    return result


def require(instructions: dict[int, str], address: int, expected: str) -> None:
    actual = instructions.get(address)
    wanted = _norm(expected)
    if actual != wanted:
        raise ValueError(f"0x{address:08X}: expected {wanted!r}, got {actual!r}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _require_upstream_evidence(path: Path) -> tuple[str, dict[int, str]]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != UPSTREAM_SHA256:
        raise ValueError(f"GetVVer upstream evidence SHA mismatch: {digest}")
    text = path.read_text(encoding="utf-8")
    required_text = (
        "METADATA_NAME: GoalDoor$$get_Height",
        "METADATA_NAME: XNumber$$create",
        "0xA0 | List<XNumber> | ySpeedMax",
        "0xB8 | List<XNumber> | energyMapNew",
        "0xD8 | List<XNumber> | shootPropertyMapNew",
        "0xE0 | List<XNumber> | energyToleranceMap",
        "0xE8 | List<XNumber> | shootDisMap",
        "0xF0 | List<XNumber> | shootPointHDownMap",
        "0xF8 | List<XNumber> | shootPointHUpMap",
        "0x100 | List<XNumber> | outEnergyMaxMap",
    )
    for token in required_text:
        if token not in text:
            raise ValueError(f"missing upstream evidence token: {token}")
    ins = parse_instructions(path)
    # Exact helper bodies from ScriptMethod-bounded evidence. These anchors are
    # sufficient for the observed XNumber.create(0,100) call used by GetVVer;
    # they do not claim a generic reimplementation of XNumber.create.
    require(ins, 0x014DEFDC, "ldr x8, [x0, #0x18]")
    require(ins, 0x014DEFE0, "ldr w0, [x8, #0x24]")
    require(ins, 0x014DEFE4, "ret")
    require(ins, 0x01B60CE0, "mov w8, #0x200")
    require(ins, 0x01B60CE4, "bfi w8, w11, #0xa, #0x16")
    require(ins, 0x01B60CF0, "smull x8, w8, w11")
    require(ins, 0x01B60CF8, "asr x8, x8, #0x26")
    require(ins, 0x01B60D08, "add w8, w8, w10, lsl #10")
    require(ins, 0x01B60D0C, "mul w0, w8, w9")
    require(ins, 0x01B60D10, "ret")
    return digest, ins


def analyze(source: Path = SOURCE, upstream: Path = UPSTREAM) -> dict:
    source_sha = hashlib.sha256(_lf_bytes(source)).hexdigest()
    if source_sha != SOURCE_LF_SHA256:
        raise ValueError(f"shoot disassembly normalized SHA mismatch: {source_sha}")
    upstream_sha, _ = _require_upstream_evidence(upstream)
    ins = parse_instructions(source)

    anchors = (
        # Raw-map producer 1: horizontal distance over shootDisMap -> outEnergyMaxMap.
        (0x016E8630, "ldr x20, [x22, #0xe8]"),
        (0x016E8768, "ldr x26, [x22, #0x100]"),
        (0x016E87EC, "mov x0, x24"),
        (0x016E87F0, "mov x1, x20"),
        (0x016E87F4, "mov x2, x19"),
        (0x016E87F8, "mov x3, x21"),
        (0x016E87FC, "mov x4, x25"),
        (0x016E8804, "bl #0x126bf1c"),
        # Raw-map producer 2: current energy over energyMapNew -> ySpeedMax.
        (0x016E8830, "ldr x8, [x22, #0xa0]"),
        (0x016E8908, "ldr x20, [x22, #0xb8]"),
        (0x016E89DC, "mov x0, x25"),
        (0x016E89E0, "mov x1, x20"),
        (0x016E89E4, "mov x2, x21"),
        (0x016E89E8, "mov x3, x19"),
        (0x016E89EC, "mov x4, x26"),
        (0x016E89F4, "bl #0x126bf1c"),
        # Raw-map producers 3/4: distance -> shoot-point up/down rates.
        (0x016E8B2C, "ldr x26, [x22, #0xf8]"),
        (0x016E8BC8, "bl #0x126bf1c"),
        (0x016E8D08, "ldr x21, [x22, #0xf0]"),
        (0x016E8DA4, "bl #0x126bf1c"),
        # Runtime shoot-property scalar then property-map -> tolerance-map.
        (0x016E8DB8, "ldr x0, [x27, #0x1b0]"),
        (0x016E8DCC, "bl #0x1968398"),
        (0x016E8DF4, "ldr x19, [x22, #0xd8]"),
        (0x016E8F08, "ldr x27, [x22, #0xe0]"),
        (0x016E8FA8, "bl #0x126bf1c"),
        # energy-protection selection around out-energy/current-energy/tolerance.
        (0x016E8FBC, "ldr w19, [x22, #0x94]"),
        (0x016E8FD8, "ldur x8, [x29, #-0x70]"),
        (0x016E8FDC, "sub w8, w8, w19"),
        (0x016E8FE0, "cmp w8, w21"),
        (0x016E900C, "add w8, w26, w8"),
        (0x016E9010, "cmp w21, w8"),
        (0x016E9040, "sub x20, x21, x26"),
        (0x016E9048, "sub x19, x9, x19"),
        (0x016E9060, "cmp w20, w19"),
        (0x016E9064, "csel x8, x20, x19, gt"),
        (0x016E9094, "sub x19, x19, x9"),
        (0x016E9098, "cmp w19, #0"),
        # point-height positive and nonpositive branches.
        (0x016E90F0, "ldr x8, [sp, #0x18]"),
        (0x016E9100, "madd x8, x9, x8, x10"),
        (0x016E9104, "lsr x20, x8, #0xa"),
        (0x016E9140, "ldr x20, [sp, #8]"),
        (0x016E9144, "tbz w19, #0x1f, #0x16e9164"),
        (0x016E9160, "neg x19, x19"),
        (0x016E9188, "mov w1, #0x64"),
        (0x016E918C, "mov w0, wzr"),
        (0x016E9190, "mov x2, xzr"),
        (0x016E9194, "madd x19, x9, x8, x10"),
        (0x016E9198, "bl #0x1b60cc8"),
        (0x016E919C, "add x8, x0, x19, lsr #10"),
        (0x016E91A0, "neg x20, x8"),
        # GoalDoor.get_Height, clamp and reference subtraction.
        (0x016E91A4, "ldr x8, [x27, #0x50]"),
        (0x016E91AC, "ldr x0, [x8, #0x120]"),
        (0x016E91B8, "bl #0x14defdc"),
        (0x016E91E4, "ldp w21, w23, [x22, #0xb0]"),
        (0x016E91E8, "add x19, x19, x20"),
        (0x016E9208, "cmp w23, w19"),
        (0x016E920C, "csel x8, x23, x19, lt"),
        (0x016E9210, "cmp w21, w19"),
        (0x016E9214, "csel x8, x21, x8, gt"),
        (0x016E9218, "sub x8, x8, x9"),
        (0x016E9220, "str x8, [sp, #0x28]"),
        # base vertical vector.
        (0x016E9D08, "ldr x12, [sp, #0x10]"),
        (0x016E9D0C, "sxtw x8, w23"),
        (0x016E9D10, "sxtw x9, w19"),
        (0x016E9D18, "asr x11, x23, #0x20"),
        (0x016E9D1C, "madd x8, x9, x8, x10"),
        (0x016E9D20, "madd x11, x9, x11, x10"),
        (0x016E9D24, "madd x9, x9, x12, x10"),
        (0x016E9D28, "lsr x21, x8, #0xa"),
        (0x016E9D2C, "lsr x24, x11, #0xa"),
        (0x016E9D30, "lsr x8, x9, #0xa"),
        # surviving 0x3FC modifier, parameter[2] at array element +0x28.
        (0x016E9DF0, "mov w1, #0x3fc"),
        (0x016E9DFC, "bl #0x196807c"),
        (0x016E9E28, "ldr x8, [x19, #0x10]"),
        (0x016E9E30, "ldrsw x19, [x8, #0x28]"),
        (0x016E9E58, "madd x8, x8, x19, x9"),
        (0x016E9E5C, "madd x10, x10, x19, x9"),
        (0x016E9E60, "madd x9, x19, x23, x9"),
        # surviving 0x41A modifier with the same parameter index and fixed scaling.
        (0x016E9F30, "mov w1, #0x41a"),
        (0x016E9F3C, "bl #0x196807c"),
        (0x016E9F5C, "ldr x8, [x19, #0x10]"),
        (0x016E9F64, "ldrsw x19, [x8, #0x28]"),
        (0x016E9F94, "mul x10, x10, x19"),
        (0x016E9F98, "madd x8, x8, x19, x9"),
        (0x016E9F9C, "madd x9, x19, x23, x9"),
        (0x016E9FA0, "add x21, x11, x10, lsl #22"),
        (0x016E9FA8, "bfxil x21, x8, #0xa, #0x20"),
        (0x016E9FC8, "cbnz w20, #0x16ea52c"),
    )
    for address, expected in anchors:
        require(ins, address, expected)

    return {
        "schema_version": "football.recovery.getvver_new_path_composition.v2",
        "analysis_status": "raw-map producers and resolved-scalar composition instruction-bound",
        "behavior_validated": False,
        "source": {
            "shoot_disassembly": source.relative_to(ROOT).as_posix(),
            "shoot_disassembly_lf_sha256": source_sha,
            "upstream_evidence": upstream.relative_to(ROOT).as_posix(),
            "upstream_evidence_sha256": upstream_sha,
            "binary_sha256": "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
        },
        "raw_map_producers": {
            "out_energy": {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "outEnergyMaxMap +0x100", "call": "0x016E8804"},
            "y_speed_max": {"input": "current_energy", "axis": "energyMapNew +0xB8", "values": "ySpeedMax +0xA0", "call": "0x016E89F4"},
            "point_up_rate": {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "shootPointHUpMap +0xF8", "call": "0x016E8BC8"},
            "point_down_rate": {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "shootPointHDownMap +0xF0", "call": "0x016E8DA4"},
            "energy_tolerance": {"input": "shoot_property_input_from_0x1968398", "axis": "shootPropertyMapNew +0xD8", "values": "energyToleranceMap +0xE0", "call": "0x016E8FA8"},
            "unresolved_runtime_input": "0x1968398 output",
            "executable_header": "Reference/FootballPhysics/GetVVerNewPathConfig.h",
            "host_guard_policy": "canonical ascending equal-length paired maps only; malformed/out-of-coverage native behavior is not claimed",
        },
        "target_height_path": {
            "energy_need_protect_offset": "+0x94",
            "selected_energy_equation": "if out_energy-energy_need_protect >= current_energy or current_energy >= out_energy+energy_tolerance: current_energy; else max(current_energy-energy_tolerance, out_energy-energy_need_protect)",
            "height_adjustment_positive": "fixed_mul(selected_energy-out_energy, point_up_rate)",
            "downward_bias_helper": "XNumber$$create",
            "downward_bias_call": "XNumber.create(0,100)",
            "downward_bias_raw": 102,
            "height_adjustment_nonpositive": "-(fixed_mul(abs(selected_energy-out_energy), point_down_rate) + XNumber.create(0,100))",
            "base_target_height_helper": "GoalDoor$$get_Height",
            "base_target_height_call": "0x016E91B8 -> 0x14DEFDC",
            "point_h_bounds_load": "0x016E91E4, ShootSpeedConfigItem shootPointH +0xB0/+0xB4 pair",
            "vertical_delta": "native_clamp(GoalDoor.get_Height + height_adjustment, point_h_min, point_h_max) - reference_y",
        },
        "vector_composition": {
            "base_vector_range": "0x016E9D08..0x016E9D48",
            "base_vector": "vertical_direction * solved_y_speed using native fixed_mul",
            "modifier_order": ["0x3FC", "0x41A"],
            "modifier_parameter_index": 2,
            "modifier_semantics": "scale all three vector components by parameter[2] using native fixed_mul",
            "normal_return_value_contribution": True,
            "new_path_exit": "0x016E9FC8 -> 0x016EA52C when new-path flag remains set",
        },
        "executable_boundary": {
            "map_header": "Reference/FootballPhysics/GetVVerNewPathConfig.h",
            "map_entry": "ResolveNewGetVVerMapOutputs",
            "composition_header": "Reference/FootballPhysics/GetVVerNewPath.h",
            "composition_entry": "ComposeNewGetVVerFromResolvedScalars",
            "inputs_still_resolved_upstream": [
                "shoot_property_input from call 0x1968398",
                "GoalDoor instance supplying GoalDoor.get_Height",
                "vertical_direction and modifier activation/ratios from caller/runtime state",
            ],
            "claim": "raw ShootSpeedConfigItem map production is executable for canonical covered intervals, then feeds the recovered resolved-scalar composition; not yet a whole-function native differential clone",
        },
        "physics_v0_3_gate": "BLOCKED",
        "next_gate": "identify 0x1968398 and bind runtime modifier activation/ratios, then differential-validate complete new-path GetVVer",
    }


def main() -> int:
    trace = analyze()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"GETVVER_NEW_PATH_COMPOSITION: GREEN output={OUTPUT} gate={trace['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
