"""Extract the source-backed flag writes from calSpmoveInUse ARM64 listing.

The output is an intermediate static trace. It validates instruction anchors
and records flag/condition relationships without pretending to execute the
Android native code.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "cal_spmove_disassembly.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "cal_spmove_static_trace.json"
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def load_lines() -> dict[str, str]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)
    result: dict[str, str] = {}
    for raw in INPUT.read_text(encoding="utf-8").splitlines():
        match = LINE_RE.match(raw.strip())
        if match:
            result[match.group("address").upper()] = match.group("instruction").strip()
    return result


def require(lines: dict[str, str], address: str, fragment: str) -> None:
    actual = lines.get(address.upper())
    if actual is None or fragment not in actual:
        raise ValueError(
            f"anchor {address} missing fragment {fragment!r}; actual={actual!r}"
        )


def main() -> int:
    lines = load_lines()
    anchors = {
        "reset_spmove": ("014C55A0", "bl       #0x14e5a4c"),
        "shoot_first_input": ("014C55A8", "and      w8, w22, #1"),
        "shoot_first_store": ("014C55AC", "strb     w8, [x19, #0xab]"),
        "calm_collection": ("014C55F8", "mov      w1, #0xf"),
        "calm_property": ("014C561C", "mov      w1, #0x417"),
        "calm_store": ("014C5630", "strb     w8, [x19, #0xa9]"),
        "push_collection": ("014C5634", "mov      w1, #0x20"),
        "push_property": ("014C5658", "mov      w1, #0x41a"),
        "push_store": ("014C566C", "strb     w8, [x21]"),
        "angle_property": ("014C58E4", "mov      w1, #0x418"),
        "angle_store": ("014C58F8", "strb     w8, [x19, #0xaa]"),
        "distance_interpolation": ("014C59A4", "bl       #0x1566ab4"),
        "long_collection": ("014C59D0", "mov      w1, #0xf"),
        "long_property": ("014C59F4", "mov      w1, #0x3fc"),
        "long_store": ("014C5A08", "strb     w8, [x19, #0xad]"),
        "head_collection": ("014C5A0C", "mov      w1, #0x10"),
        "head_property": ("014C5A30", "mov      w1, #0x3fb"),
        "head_store": ("014C5A44", "strb     w8, [x19, #0xac]"),
        "swanton_goal_a": ("014C5A48", "mov      w8, #0x16b6"),
        "swanton_goal_b": ("014C5A54", "mov      w8, #0x16b3"),
        "swanton_property": ("014C5A70", "mov      w1, #0x40b"),
        "swanton_store": ("014C5A84", "strb     w8, [x19, #0xae]"),
    }
    errors: list[str] = []
    for name, (address, fragment) in anchors.items():
        try:
            require(lines, address, fragment)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print("CAL_SPMOVE_TRACE_ERROR: " + error)
        return 1

    source_bytes = INPUT.read_bytes()
    report = {
        "schema_version": "football.recovery.cal_spmove_static_trace.v1",
        "source": ".local/il2cpp/cal_spmove_disassembly.txt",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "method_span": {
            "name": "calSpmoveInUse",
            "start": "0x014C5548",
            "end": "0x014C5AA8",
            "rva": "0x14C5548",
        },
        "analysis_status": "flag_writes_and_condition_anchors_only",
        "behavior_validated": False,
        "flag_layout": [
            {"offset": 0, "name": "shootPush"},
            {"offset": 1, "name": "CalmShoot"},
            {"offset": 2, "name": "SAngleShoot"},
            {"offset": 3, "name": "ShootFirst"},
            {"offset": 4, "name": "Head"},
            {"offset": 5, "name": "ShootLongKick"},
            {"offset": 6, "name": "SwantonBomb"},
        ],
        "confirmed_writes": [
            {
                "flag": "ShootFirst",
                "byte_offset": 3,
                "native_store": "0x014C55AC [x19,#0xAB]",
                "source": "calShootFirst low bit (w2 -> w22 -> and #1)",
            },
            {
                "flag": "CalmShoot",
                "byte_offset": 1,
                "native_store": "0x014C5630 [x19,#0xA9]",
                "condition": "InCollection(goal_child, 0x0F) and GetSpmoveData(0x417) is non-null",
            },
            {
                "flag": "shootPush",
                "byte_offset": 0,
                "native_store": "0x014C566C [x21] where x21 = x19 + 0xA8",
                "condition": "InCollection(goal_child, 0x20) and GetSpmoveData(0x41A) is non-null",
            },
            {
                "flag": "SAngleShoot",
                "byte_offset": 2,
                "native_store": "0x014C58F8 [x19,#0xAA]",
                "condition": "distance/config branch followed by GetSpmoveData(0x418) is non-null",
            },
            {
                "flag": "ShootLongKick",
                "byte_offset": 5,
                "native_store": "0x014C5A08 [x19,#0xAD]",
                "condition": "interpolated distance threshold, InCollection(goal_child, 0x0F), and GetSpmoveData(0x3FC) is non-null",
            },
            {
                "flag": "Head",
                "byte_offset": 4,
                "native_store": "0x014C5A44 [x19,#0xAC]",
                "condition": "interpolated distance threshold, InCollection(goal_child, 0x10), and GetSpmoveData(0x3FB) is non-null",
            },
            {
                "flag": "SwantonBomb",
                "byte_offset": 6,
                "native_store": "0x014C5A84 [x19,#0xAE]",
                "condition": "goal_child equals 0x16B6 or 0x16B3 and GetSpmoveData(0x40B) is non-null",
            },
        ],
        "confirmed_calls": {
            "reset": "0x14E5A4C",
            "in_collection": "0x13B01DC",
            "get_spmove_data": "0x1968070",
            "get_shoot_ball_pos": "0x1382664",
            "check_ball_pos": "0x16DB8F4",
            "goal_door_positions": ["0x14DEFA8", "0x14DEF74"],
            "goal_door_center": "0x14DF68C",
            "sqrt_long": "0x1B64760",
            "interpolation": "0x1566AB4",
        },
        "unknown": [
            "semantic names of InCollection type IDs",
            "meaning and units of AI/config fields at offsets 0x170, 0x174, and 0x178",
            "exact distance/threshold branches that guard SAngleShoot, ShootLongKick, and Head",
            "meaning of each PlayerProperty.GetSpmoveData list and its XNumber contents",
            "interaction between the seven flags and GetVHor/GetVVer equations",
            "runtime behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("CAL_SPMOVE_TRACE: GREEN writes=7 output=" + str(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
