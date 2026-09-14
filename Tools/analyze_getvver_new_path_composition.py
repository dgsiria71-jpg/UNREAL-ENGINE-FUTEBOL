"""Bind the new-path GetVVer composition and recovered PlayerProperty selector."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
UPSTREAM = ROOT / "artifacts" / "native-recovery" / "getvver-upstream" / "20260913-234939-ff28866f" / "01_getvver_upstream_evidence.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "getvver_new_path_composition_static_trace.json"
SOURCE_LF_SHA256 = "c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4"
UPSTREAM_SHA256 = "4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3"
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
        "### shoot_property_1968398 start=0x01968398 end=0x019687C8 boundary=script.json:next-method exact=true",
        "METADATA_NAME: PlayerProperty$$GetShootProperty",
        "METADATA_NAME: Football$$get_position2D",
        "METADATA_NAME: XGoalExtension$$InCollection",
        "METADATA_NAME: GoalDoor$$getCenter",
        "METADATA_NAME: PlayerProperty$$getShootPropertyWithSpmove",
        "METADATA_NAME: PropertySingle$$calMain",
        "METADATA_NAME: XIntMath$$Sqrt_Long",
        "METADATA_NAME: XBaseLocalSetting<AIParameterConfig>$$get_Singleton",
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
    # Exact small helpers already used by the target-height path.
    require(ins, 0x014DEFDC, "ldr x8, [x0, #0x18]")
    require(ins, 0x014DEFE0, "ldr w0, [x8, #0x24]")
    require(ins, 0x014DEFE4, "ret")
    require(ins, 0x01B60CE0, "mov w8, #0x200")
    require(ins, 0x01B60D08, "add w8, w8, w10, lsl #10")
    require(ins, 0x01B60D0C, "mul w0, w8, w9")
    require(ins, 0x01B60D10, "ret")

    # PlayerProperty.GetShootProperty exact ScriptMethod body. These anchors
    # bind branch-level value semantics only; second-level property lookup
    # internals remain outside this increment.
    require(ins, 0x019683BC, "mov w20, w1")
    require(ins, 0x0196845C, "bl #0x1ff58ac")
    require(ins, 0x0196846C, "bl #0x1379748")
    require(ins, 0x01968488, "bl #0x14df68c")
    require(ins, 0x01968518, "bl #0x1b64760")
    require(ins, 0x0196851C, "mov w8, #0x16b3")
    require(ins, 0x01968528, "mov w8, #0x22c5")
    require(ins, 0x01968534, "mov w1, #0x16")
    require(ins, 0x01968540, "mov w1, #0x15")
    require(ins, 0x0196854C, "bl #0x19687c8")
    require(ins, 0x01968578, "mov w1, #0x13")
    require(ins, 0x01968584, "bl #0x13b01dc")
    require(ins, 0x0196858C, "mov w1, #0x14")
    require(ins, 0x01968598, "bl #0x19687c8")
    require(ins, 0x019685B0, "mov w0, #0x30")
    require(ins, 0x019685B8, "bl #0x1ac8d78")
    require(ins, 0x019685DC, "add w19, w20, w19")
    require(ins, 0x019685E8, "ldr w24, [x22, #0x148]")
    require(ins, 0x0196860C, "mov w1, #0x10")
    require(ins, 0x01968620, "ldr w24, [x22, #0x14c]")
    require(ins, 0x01968670, "lsr x8, x21, #0x20")
    require(ins, 0x01968674, "cmp w22, w8")
    require(ins, 0x0196867C, "mov w1, #0x11")
    require(ins, 0x019686B8, "sub x23, x26, x23")
    require(ins, 0x019686D8, "cbz w23, #0x1968704")
    require(ins, 0x019686DC, "sub x8, x24, x27")
    require(ins, 0x019686E4, "sbfiz x9, x23, #0xa, #0x20")
    require(ins, 0x019686EC, "sdiv x10, x9, x8")
    require(ins, 0x019686F0, "msub x9, x10, x8, x9")
    require(ins, 0x019686F4, "lsl x9, x9, #1")
    require(ins, 0x019686F8, "sdiv x8, x9, x8")
    require(ins, 0x019686FC, "add w23, w8, w10")
    require(ins, 0x01968720, "ldr x8, [x0, #0xb8]")
    require(ins, 0x01968724, "ldr w23, [x8, #8]")
    require(ins, 0x0196874C, "mov w1, #0xf")
    require(ins, 0x01968754, "mov w1, #0xf")
    require(ins, 0x01968760, "bl #0x19687c8")
    require(ins, 0x01968784, "sxtw x8, w21")
    require(ins, 0x01968790, "madd x8, x8, x9, x21")
    require(ins, 0x01968794, "mov w1, #0x10")
    require(ins, 0x019687A0, "lsr x22, x8, #0xa")
    require(ins, 0x019687A4, "bl #0x19687c8")
    require(ins, 0x019687A8, "mov w8, #0x400")
    require(ins, 0x019687B8, "madd x8, x9, x8, x21")
    require(ins, 0x019687BC, "lsr x8, x8, #0xa")
    require(ins, 0x019687C0, "add w19, w8, w22")

    return digest, ins


def analyze(source: Path = SOURCE, upstream: Path = UPSTREAM) -> dict:
    source_sha = hashlib.sha256(_lf_bytes(source)).hexdigest()
    if source_sha != SOURCE_LF_SHA256:
        raise ValueError(f"shoot disassembly normalized SHA mismatch: {source_sha}")
    upstream_sha, _ = _require_upstream_evidence(upstream)
    ins = parse_instructions(source)

    anchors = (
        # GetVVer preserves original w1 and forwards it to GetShootProperty.
        (0x016E84EC, "str w1, [sp, #0x54]"),
        (0x016E8DB8, "ldr x0, [x27, #0x1b0]"),
        (0x016E8DC4, "ldr w1, [sp, #0x54]"),
        (0x016E8DCC, "bl #0x1968398"),
        # Raw-map producer 1: horizontal distance over shootDisMap -> outEnergyMaxMap.
        (0x016E8630, "ldr x20, [x22, #0xe8]"),
        (0x016E8768, "ldr x26, [x22, #0x100]"),
        (0x016E8804, "bl #0x126bf1c"),
        # Raw-map producer 2: current energy over energyMapNew -> ySpeedMax.
        (0x016E8830, "ldr x8, [x22, #0xa0]"),
        (0x016E8908, "ldr x20, [x22, #0xb8]"),
        (0x016E89F4, "bl #0x126bf1c"),
        # Raw-map producers 3/4: distance -> shoot-point up/down rates.
        (0x016E8B2C, "ldr x26, [x22, #0xf8]"),
        (0x016E8BC8, "bl #0x126bf1c"),
        (0x016E8D08, "ldr x21, [x22, #0xf0]"),
        (0x016E8DA4, "bl #0x126bf1c"),
        # PlayerProperty scalar then property-map -> tolerance-map.
        (0x016E8DF4, "ldr x19, [x22, #0xd8]"),
        (0x016E8F08, "ldr x27, [x22, #0xe0]"),
        (0x016E8FA8, "bl #0x126bf1c"),
        # energy-protection selection.
        (0x016E8FBC, "ldr w19, [x22, #0x94]"),
        (0x016E8FDC, "sub w8, w8, w19"),
        (0x016E8FE0, "cmp w8, w21"),
        (0x016E900C, "add w8, w26, w8"),
        (0x016E9010, "cmp w21, w8"),
        (0x016E9060, "cmp w20, w19"),
        (0x016E9064, "csel x8, x20, x19, gt"),
        # point-height positive/nonpositive branches and fixed downward bias.
        (0x016E9100, "madd x8, x9, x8, x10"),
        (0x016E9104, "lsr x20, x8, #0xa"),
        (0x016E9188, "mov w1, #0x64"),
        (0x016E918C, "mov w0, wzr"),
        (0x016E9198, "bl #0x1b60cc8"),
        (0x016E919C, "add x8, x0, x19, lsr #10"),
        (0x016E91A0, "neg x20, x8"),
        # GoalDoor.get_Height, clamp and reference subtraction.
        (0x016E91B8, "bl #0x14defdc"),
        (0x016E91E4, "ldp w21, w23, [x22, #0xb0]"),
        (0x016E9208, "cmp w23, w19"),
        (0x016E920C, "csel x8, x23, x19, lt"),
        (0x016E9210, "cmp w21, w19"),
        (0x016E9214, "csel x8, x21, x8, gt"),
        (0x016E9218, "sub x8, x8, x9"),
        # base vertical vector and surviving modifiers.
        (0x016E9D08, "ldr x12, [sp, #0x10]"),
        (0x016E9D28, "lsr x21, x8, #0xa"),
        (0x016E9DF0, "mov w1, #0x3fc"),
        (0x016E9DFC, "bl #0x196807c"),
        (0x016E9E30, "ldrsw x19, [x8, #0x28]"),
        (0x016E9F30, "mov w1, #0x41a"),
        (0x016E9F3C, "bl #0x196807c"),
        (0x016E9F64, "ldrsw x19, [x8, #0x28]"),
        (0x016E9FC8, "cbnz w20, #0x16ea52c"),
    )
    for address, expected in anchors:
        require(ins, address, expected)

    return {
        "schema_version": "football.recovery.getvver_new_path_composition.v3",
        "analysis_status": "raw-map composition plus PlayerProperty.GetShootProperty branch selector instruction-bound",
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
            "energy_tolerance": {"input": "PlayerProperty.GetShootProperty result", "axis": "shootPropertyMapNew +0xD8", "values": "energyToleranceMap +0xE0", "call": "0x016E8FA8"},
            "executable_header": "Reference/FootballPhysics/GetVVerNewPathConfig.h",
            "host_guard_policy": "canonical ascending equal-length paired maps only; malformed/out-of-coverage native behavior is not claimed",
        },
        "player_property_selector": {
            "metadata_name": "PlayerProperty$$GetShootProperty",
            "range": "0x01968398..0x019687C8",
            "boundary_source": "script.json:next-method",
            "getvver_call": "0x016E8DCC",
            "getvver_argument": "original GetVVer w1 stored at 0x016E84EC and reloaded at 0x016E8DC4",
            "special_action_properties": {"0x16B3": "0x15", "0x22C5": "0x16"},
            "collection_id": "0x13",
            "collection_property": "0x14",
            "collection_bonus": "optional PropertySingle.calMain(0x30, runtime value) added after property 0x14",
            "far_property": "0x10",
            "position_properties": {"threshold_ge_position_y": "0x0F", "threshold_lt_position_y": "0x11"},
            "blend_ratio": "(upper_threshold-distance)/(upper_threshold-lower_threshold) in XNumber raw with q + trunc(2*r/d); zero numerator/denominator -> 0",
            "blend_equation": "fixed_mul(near_property, ratio) + fixed_mul(far_property, 1024-ratio)",
            "distance_source": "2D Football position to GoalDoor center followed by XIntMath.Sqrt_Long",
            "exact_first_level_value_callees": [
                "Football$$get_position2D",
                "GoalDoor$$getCenter",
                "XIntMath$$Sqrt_Long",
                "XGoalExtension$$InCollection",
                "PropertySingle$$calMain",
                "PlayerProperty$$getShootPropertyWithSpmove",
                "XBaseLocalSetting<AIParameterConfig>$$get_Singleton",
            ],
            "executable_header": "Reference/FootballPhysics/PlayerPropertySelector.h",
            "executable_entry": "ResolvePlayerProperty",
            "whole_function_equivalent": False,
            "unresolved_internal_sources": [
                "PlayerProperty.getShootPropertyWithSpmove second-level callee 0x1967D38",
                "fallback property lookup 0x1B718D8",
                "semantic field names/units for AIParameterConfig +0x24/+0x148/+0x14C",
                "collection bonus producer object/fields +0x98/+0x40/+0x44",
                "runtime Football/GoalDoor object wiring",
            ],
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
            "property_header": "Reference/FootballPhysics/PlayerPropertySelector.h",
            "property_entry": "ResolvePlayerProperty",
            "composition_entry": "ComposeNewGetVVerFromPlayerProperty",
            "inputs_still_resolved_upstream": [
                "property-value lookup internals behind 0x1967D38 / 0x1B718D8",
                "AIParameterConfig threshold semantic names and units",
                "collection bonus runtime producer",
                "GoalDoor instance supplying GoalDoor.get_Height",
                "runtime Football/GoalDoor object wiring",
                "vertical_direction and modifier activation/ratios from caller/runtime state",
            ],
            "claim": "branch-level PlayerProperty.GetShootProperty selection can now feed the recovered raw maps and fixed-point GetVVer composition; whole-function native differential equivalence is not yet claimed",
        },
        "physics_v0_3_gate": "BLOCKED",
        "next_gate": "recover GetShootProperty second-level property lookup/AI threshold field identities and bind runtime 0x3FC/0x41A activation/ratios before whole-function differential validation",
    }


def main() -> int:
    trace = analyze()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"GETVVER_NEW_PATH_COMPOSITION: GREEN output={OUTPUT} gate={trace['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
