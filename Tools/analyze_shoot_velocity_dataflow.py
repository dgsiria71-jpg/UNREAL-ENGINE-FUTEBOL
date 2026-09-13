"""Recover verified GetVHor/GetKickVelocity dataflow from committed ARM64 evidence.

This analyzer intentionally stays static and conservative. It binds exact ARM64
anchors in the canonical committed disassembly and records only dataflow that can
be proven from those instructions. It does not claim that GetVVer's full equations
or BALL_CONTACT are recovered.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "artifacts"
    / "native-recovery"
    / "20260913-163217-9cdb54d0"
    / "01_disassembly_shoot.txt"
)
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_velocity_dataflow_static_trace.json"

HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$")
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")
EXPECTED_SHA256 = "ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    instructions: dict[str, tuple[str, str]] = {}
    sections: dict[str, tuple[str, str]] = {}
    section: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        header = HEADER_RE.match(raw.strip())
        if header:
            section = header.group("name")
            sections[section] = (
                "0x" + header.group("start").upper(),
                "0x" + header.group("end").upper(),
            )
            continue
        line = LINE_RE.match(raw.strip())
        if line and section:
            address = "0x" + line.group("address").upper()
            instructions[address] = (section, line.group("instruction").strip())
    return instructions, sections


def require(
    instructions: dict[str, tuple[str, str]],
    address: str,
    expected: str,
    section: str,
) -> None:
    actual = instructions.get(address)
    wanted = (section, expected)
    if actual != wanted:
        raise ValueError(f"{address}: expected {wanted!r}, got {actual!r}")


def analyze(path: Path = SOURCE) -> dict:
    digest = sha256(path)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"unexpected disassembly SHA-256: {digest}")

    ins, sections = parse(path)
    if sections.get("GetVHor") != ("0x016E6A80", "0x016E84A4"):
        raise ValueError("GetVHor span mismatch")
    if sections.get("GetVVer") != ("0x016E84A4", "0x016EA55C"):
        raise ValueError("GetVVer span mismatch")
    if sections.get("GetKickVelocity") != ("0x016EBAD8", "0x016EBF14"):
        raise ValueError("GetKickVelocity span mismatch")

    anchors = [
        # GetVHor new path: map interpolation and rate interpolation.
        ("0x016E6DE0", "bl       #0x126bf1c", "GetVHor"),
        ("0x016E6DE8", "mov      w0, #0x3b", "GetVHor"),
        ("0x016E6FEC", "bl       #0x126bf1c", "GetVHor"),
        ("0x016E72C0", "ldp      w20, w21, [x21, #0xa8]", "GetVHor"),
        # GetVHor old path interpolation and bounds.
        ("0x016E73B0", "bl       #0x126bf1c", "GetVHor"),
        ("0x016E745C", "ldr      w22, [x21, #0x74]", "GetVHor"),
        ("0x016E794C", "ldp      w20, w21, [x21, #0x78]", "GetVHor"),
        # Clamp and final horizontal-vector construction.
        ("0x016E7988", "cmp      w21, w24", "GetVHor"),
        ("0x016E798C", "csel     x9, x21, x24, lt", "GetVHor"),
        ("0x016E7990", "cmp      w20, w24", "GetVHor"),
        ("0x016E7998", "csel     x20, x20, x9, gt", "GetVHor"),
        ("0x016E79C8", "madd     x8, x8, x10, x11", "GetVHor"),
        ("0x016E79D4", "str      x9, [sp, #0x48]", "GetVHor"),
        ("0x016E79D8", "str      w8, [sp, #0x50]", "GetVHor"),
        # Pre-base spmove blocks; their vector slots are later overwritten.
        ("0x016E7038", "mov      w1, #0x3fe", "GetVHor"),
        ("0x016E7170", "mov      w1, #0x3fc", "GetVHor"),
        ("0x016E76C4", "mov      w1, #0x3fe", "GetVHor"),
        ("0x016E77FC", "mov      w1, #0x3fc", "GetVHor"),
        # GetKickVelocity calls and final component-wise join.
        ("0x016EBBA8", "bl       #0x16e6a80", "GetKickVelocity"),
        ("0x016EBEAC", "bl       #0x16e84a4", "GetKickVelocity"),
        ("0x016EBED8", "and      x8, x19, #0xffffffff00000000", "GetKickVelocity"),
        ("0x016EBEDC", "add      w9, w19, w22", "GetKickVelocity"),
        ("0x016EBEE0", "add      w1, w20, w25", "GetKickVelocity"),
        ("0x016EBEE4", "add      x8, x8, x21", "GetKickVelocity"),
        ("0x016EBF00", "and      x8, x8, #0xffffffff00000000", "GetKickVelocity"),
        ("0x016EBF04", "orr      x0, x8, x9", "GetKickVelocity"),
    ]
    for address, expected, section in anchors:
        require(ins, address, expected, section)

    return {
        "schema_version": "football.recovery.shoot_velocity_dataflow_static_trace.v1",
        "source": "artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt",
        "source_sha256": digest,
        "analysis_status": "static_dataflow_partial_confirmed",
        "behavior_validated": False,
        "GetVHor": {
            "span": "0x016E6A80..0x016E84A4",
            "new_path": {
                "energy_to_vhor_interpolate_call": "0x016E6DE0",
                "interpolate_helper": "0x126BF1C",
                "player_property_id": "0x3B",
                "strength_to_rate_interpolate_call": "0x016E6FEC",
                "clamp_bounds_load": "0x016E72C0",
                "clamp_bounds_offset": "+0xA8",
            },
            "old_path": {
                "energy_to_vhor_interpolate_call": "0x016E73B0",
                "interpolate_helper": "0x126BF1C",
                "speed_vHor_load": "0x016E745C",
                "clamp_bounds_load": "0x016E794C",
                "clamp_bounds_offset": "+0x78",
            },
            "base_vector": {
                "clamp_range": "0x016E7988..0x016E7998",
                "construction_range": "0x016E79B0..0x016E79D8",
                "fixed_point_bias": 512,
                "fraction_bits": 10,
                "return_slots_write": ["0x016E79D4", "0x016E79D8"],
                "layout": "XVector3(x=dir0*speed,y=0,z=dir1*speed)",
            },
            "pre_base_spmove_blocks": {
                "logic_ids": ["0x3FE", "0x3FC"],
                "new_path_logic_id_loads": ["0x016E7038", "0x016E7170"],
                "old_path_logic_id_loads": ["0x016E76C4", "0x016E77FC"],
                "normal_return_value_contribution": False,
                "overwritten_by": ["0x016E79D4", "0x016E79D8"],
                "calls_may_still_throw_or_have_side_effects": True,
                "interpretation": (
                    "The blocks rewrite the temporary vector slots before the shared base-vector "
                    "construction. On the normal return path those slots are overwritten by the "
                    "writes at 0x016E79D4/0x016E79D8. This proves no surviving value contribution, "
                    "not that the calls are semantically removable."
                ),
            },
        },
        "GetVVer": {
            "span": "0x016E84A4..0x016EA55C",
            "status": "old_new_field_families_bound_but_full_equations_unresolved",
        },
        "GetKickVelocity": {
            "span": "0x016EBAD8..0x016EBF14",
            "GetVHor_call": "0x016EBBA8",
            "GetVHor_target": "0x016E6A80",
            "GetVVer_call": "0x016EBEAC",
            "GetVVer_target": "0x016E84A4",
            "horizontal_postprocessing_before_GetVVer": True,
            "final_join_range": "0x016EBED8..0x016EBF04",
            "final_join": "adjusted_GetVHor + GetVVer componentwise",
            "return_abi": "XVector3 packed as x0(low32=x, high32=y) plus w1=z",
        },
        "confirmed_interpretation": [
            "GetVHor new and old paths both converge on a shared clamped horizontal-vector constructor.",
            "The shared horizontal constructor uses fixed-point multiply with +512 bias and 10 fraction bits.",
            "Pre-base 0x3FE/0x3FC spmove vector rewrites do not survive the normal GetVHor return-value path because the vector slots are overwritten later.",
            "GetKickVelocity calls GetVHor, post-processes that horizontal vector, calls GetVVer, then adds the two vectors componentwise.",
        ],
        "unknown": [
            "full GetVVer arithmetic/interpolation/clamp equations",
            "semantic identity of all external calls in GetVHor/GetVVer/GetKickVelocity",
            "exceptional-path behavior beyond the anchored static dataflow",
            "BALL_CONTACT.velocity binding and end-to-end runtime equivalence",
        ],
        "physics_gate": "blocked",
    }


def main() -> int:
    report = analyze(SOURCE)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"SHOOT_VELOCITY_DATAFLOW: GREEN output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
