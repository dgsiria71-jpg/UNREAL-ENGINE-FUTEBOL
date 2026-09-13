"""Recover shootDisAndTime flight-time lookup and vertical solve from ARM64."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_dis_and_time_static_trace.json"
METADATA = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "02_shoot_dis_and_time_metadata.txt"
SOURCE_LF_SHA256 = "c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4"
METADATA_LF_SHA256 = "2368fbaaee1a3bae0461a31603ad578adf76a963c97f9131982faa78a9838478"
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def _lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _norm(value: str) -> str:
    return " ".join(value.strip().split())


def parse_instructions(path: Path) -> dict[int, str]:
    result = {}
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


def analyze(source: Path = SOURCE, metadata: Path = METADATA) -> dict:
    source_sha = hashlib.sha256(_lf_bytes(source)).hexdigest()
    if source_sha != SOURCE_LF_SHA256:
        raise ValueError(f"shoot disassembly normalized SHA mismatch: {source_sha}")
    metadata_sha = hashlib.sha256(_lf_bytes(metadata)).hexdigest()
    if metadata_sha != METADATA_LF_SHA256:
        raise ValueError(f"shoot metadata normalized SHA mismatch: {metadata_sha}")
    metadata_text = _lf_bytes(metadata).decode("utf-8")
    for fact in ("public List<List<int>> shootDisAndTime; // 0x108", "public XNumber ySpeedMin; // 0x98", "public static readonly XNumber thousand; // 0x50"):
        if fact not in metadata_text:
            raise ValueError(f"shoot metadata fact missing: {fact}")
    ins = parse_instructions(source)

    anchors = (
        # |vHor|, outer floor/ceiling row indices.
        (0x016E9268, "sxtw x8, w9"),
        (0x016E9270, "mul x9, x9, x9"),
        (0x016E9274, "madd x8, x8, x8, x9"),
        (0x016E9284, "madd x20, x9, x9, x8"),
        (0x016E9298, "mov x0, x20"),
        (0x016E92A0, "bl #0x1b64760"),
        (0x016E92E4, "ldr x8, [x22, #0x108]"),
        (0x016E92EC, "ldr w8, [x8, #0x18]"),
        (0x016E92F0, "asr w9, w19, #0xa"),
        (0x016E92FC, "csel w8, w8, w9, gt"),
        (0x016E9354, "mov x0, x20"),
        (0x016E935C, "bl #0x1b64760"),
        (0x016E93B0, "add w19, w19, #0x3ff"),
        (0x016E93D4, "asr w9, w19, #0xa"),
        (0x016E93E0, "csel w26, w8, w9, gt"),
        # Inner distance interval and first row value pair.
        (0x016E9410, "ldr x21, [x22, #0x108]"),
        (0x016E9448, "ldr x8, [x8, #0x20]"),
        (0x016E9478, "lsl w21, w20, #0xa"),
        (0x016E947C, "cmp w21, w24"),
        (0x016E94A8, "lsl w25, w23, #0xa"),
        (0x016E94AC, "cmp w25, w24"),
        (0x016E9534, "ldr w8, [x8, #0x20]"),
        (0x016E9538, "ldrsw x20, [x9, #0x50]"),
        (0x016E953C, "lsl w27, w8, #0xa"),
        (0x016E954C, "sbfiz x8, x27, #0xa, #0x20"),
        (0x016E9560, "add w20, w8, w9"),
        (0x016E9604, "ldr w9, [x9, #0x20]"),
        (0x016E9608, "ldrsw x19, [x8, #0x50]"),
        (0x016E960C, "lsl w23, w9, #0xa"),
        (0x016E96B4, "mov x0, x24"),
        (0x016E96B8, "mov x2, x21"),
        (0x016E96BC, "mov x3, x25"),
        (0x016E96C0, "mov x4, x19"),
        (0x016E96C8, "bl #0x126bf1c"),
        # Second row and the outer interpolation/fallback.
        (0x016E96EC, "ldr x20, [x22, #0x108]"),
        (0x016E9758, "lsl w25, w23, #0xa"),
        (0x016E9788, "lsl w20, w21, #0xa"),
        (0x016E9824, "ldr w8, [x8, #0x20]"),
        (0x016E9828, "ldrsw x23, [x9, #0x50]"),
        (0x016E982C, "lsl w27, w8, #0xa"),
        (0x016E98F8, "ldr w9, [x9, #0x20]"),
        (0x016E98FC, "ldrsw x19, [x8, #0x50]"),
        (0x016E9900, "lsl w21, w9, #0xa"),
        (0x016E99B8, "mov x0, x24"),
        (0x016E99BC, "mov x2, x20"),
        (0x016E99C0, "mov x3, x25"),
        (0x016E99C4, "mov x4, x19"),
        (0x016E99CC, "bl #0x126bf1c"),
        (0x016E9A00, "cmp w9, w10"),
        (0x016E9A2C, "cmp w9, w19"),
        (0x016E9A94, "cmp w26, w19"),
        (0x016E9A98, "csel x26, x9, x19, eq"),
        (0x016E9AD4, "lsl w21, w26, #0xa"),
        (0x016E9ADC, "lsl w25, w9, #0xa"),
        (0x016E9AF4, "mov x0, x24"),
        (0x016E9B00, "mov x3, x20"),
        (0x016E9B04, "mov x4, x19"),
        (0x016E9B0C, "bl #0x126bf1c"),
        # Zero-time branch, ballistic solve and clamp.
        (0x016E9B48, "cmp w8, w26"),
        (0x016E9B50, "mov w20, wzr"),
        (0x016E9B98, "ldrsw x20, [x8, #0x1c0]"),
        (0x016E9BC4, "madd x10, x19, x20, x8"),
        (0x016E9BC8, "sbfx x10, x10, #0xa, #0x20"),
        (0x016E9BCC, "madd x8, x10, x19, x8"),
        (0x016E9BD0, "lsr x20, x8, #0xa"),
        (0x016E9BE0, "cinc w8, w20, lt"),
        (0x016E9BEC, "add w8, w9, w8, asr #1"),
        (0x016E9C40, "sub x20, x10, w8, uxtw"),
        (0x016E9C50, "sbfiz x8, x20, #0xa, #0x20"),
        (0x016E9C54, "sdiv x9, x8, x19"),
        (0x016E9C64, "add w8, w8, w9"),
        (0x016E9CB4, "ldr w19, [x22, #0x98]"),
        (0x016E9CE4, "cmp w20, w9"),
        (0x016E9CE8, "csel x9, x9, x20, gt"),
        (0x016E9CEC, "cmp w20, w19"),
        (0x016E9CF4, "csel x19, x19, x9, lt"),
    )
    for address, expected in anchors:
        require(ins, address, expected)

    return {
        "schema_version": "football.recovery.shoot_dis_and_time_static_trace.v1",
        "analysis_status": "static_normal_path_equation_confirmed",
        "behavior_validated": False,
        "sources": {
            "shoot_disassembly": source.relative_to(ROOT).as_posix(),
            "shoot_disassembly_lf_sha256": source_sha,
            "metadata_excerpt": metadata.relative_to(ROOT).as_posix(),
            "metadata_excerpt_lf_sha256": metadata_sha,
            "binary_sha256": "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
            "metadata_identity": "canonical Il2CppDumper dump.cs SHA-256 4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe",
        },
        "shootDisAndTime": {
            "field": "ShootSpeedConfigItem.shootDisAndTime",
            "field_offset": "+0x108",
            "field_type": "List<List<int>>",
            "outer_axis": "XVector3.magnitude(vHor), integer floor/ceiling neighbors",
            "outer_floor": "clamp(floor(vHor_magnitude), 0, outer_count-1)",
            "outer_ceiling": "clamp(ceiling(vHor_magnitude), 0, outer_count-1)",
            "inner_axis": "horizontal shoot distance, integer floor/ceiling neighbors",
            "inner_interval": "first i where i <= distance <= i+1; no interval produces zero for that row",
            "table_value_unit": "integer milliseconds",
            "milliseconds_to_seconds": "XNumber(table_ms) / XNumber.thousand",
            "row_interpolation": "ShootRemapClamped(distance, i, i+1, seconds(row[i]), seconds(row[i+1]))",
            "outer_interpolation": "ShootRemapClamped(vHor_magnitude, floor, ceiling, lower_row_time, upper_row_time)",
            "zero_pair_policy": "use the nonzero row result; zero only when both row results are zero",
            "normal_path_equation_recovered": True,
        },
        "vertical_solver": {
            "flight_time_source": "bilinear fixed-point shootDisAndTime lookup",
            "vertical_accel_source": "AIParameterConfig +0x1C0",
            "vertical_accel_name": "vertical_accel_raw",
            "formula": "(vertical_delta - fixed_mul(fixed_mul(flight_time, vertical_accel_raw), flight_time) / 2) / flight_time",
            "operation_order": ["flight_time * vertical_accel_raw", "previous * flight_time", "previous / integer 2", "vertical_delta - previous", "previous / flight_time"],
            "zero_time_result": "XNumber.zero",
            "y_speed_min_field": "ShootSpeedConfigItem.ySpeedMin +0x98",
            "y_speed_max_source": "previously selected ySpeedMax value",
            "clamp": "max(ySpeedMin, min(ySpeedMax, solved_y_speed)) using native comparison order",
        },
        "confirmed_interpretation": [
            "shootDisAndTime is sampled as a two-dimensional speed-by-distance table.",
            "Serialized integer table values are milliseconds and are divided by XNumber.thousand before interpolation.",
            "The selected flight time feeds an ordered fixed-point ballistic vertical solve.",
            "AIParameterConfig +0x1C0 remains named vertical_accel_raw; this recovery does not relabel it as gravity.",
        ],
        "remaining_unknowns": [
            "exception behavior for malformed, null, empty, or ragged tables outside canonical data preconditions",
            "complete upstream target-height and energy-protection behavior as an executable reference",
            "post-vector spmove modifiers and final GetVVer composition",
            "full GetKickVelocity and BALL_CONTACT.velocity runtime binding",
        ],
        "physics_v0_3_gate": "BLOCKED",
        "next_gate": "compose the complete new GetVVer executable path around the recovered flight-time and vertical-solver kernel",
    }


def main() -> int:
    trace = analyze()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"SHOOT_DIS_AND_TIME: GREEN output={OUTPUT} gate={trace['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
