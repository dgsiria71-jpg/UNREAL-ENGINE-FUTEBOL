"""Recover verified GetVHor/GetVVer/GetKickVelocity dataflow from ARM64 evidence.

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
ORIGINAL_SOURCE_SHA256 = "ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58"


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_source_identity(path: Path) -> tuple[str, str]:
    """Return (original_source_sha, repository_content_sha).

    The Windows source was uploaded with CRLF line endings and the upload manifest
    records ORIGINAL_SOURCE_SHA256. Git's normal text clean filter stored this .txt
    with LF line endings, so a fresh Linux checkout has a different byte SHA. We
    verify identity by reconstructing CRLF from the repository text and requiring
    that hash to match the upload-manifest/source SHA. No instruction text changes
    are tolerated because exact anchors are checked separately below.
    """
    raw = path.read_bytes()
    repository_sha = hash_bytes(raw)
    if repository_sha == ORIGINAL_SOURCE_SHA256:
        return ORIGINAL_SOURCE_SHA256, repository_sha

    lf = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    reconstructed_crlf = lf.replace(b"\n", b"\r\n")
    reconstructed_sha = hash_bytes(reconstructed_crlf)
    if reconstructed_sha != ORIGINAL_SOURCE_SHA256:
        raise ValueError(
            "unexpected disassembly identity: "
            f"repository_sha={repository_sha} reconstructed_crlf_sha={reconstructed_sha}"
        )
    return ORIGINAL_SOURCE_SHA256, repository_sha


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
    source_sha, repository_sha = verify_source_identity(path)

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
        # GetVVer new path map chain.
        ("0x016E8630", "ldr      x20, [x22, #0xe8]", "GetVVer"),
        ("0x016E8768", "ldr      x26, [x22, #0x100]", "GetVVer"),
        ("0x016E8804", "bl       #0x126bf1c", "GetVVer"),
        ("0x016E8830", "ldr      x8, [x22, #0xa0]", "GetVVer"),
        ("0x016E8908", "ldr      x20, [x22, #0xb8]", "GetVVer"),
        ("0x016E89F4", "bl       #0x126bf1c", "GetVVer"),
        ("0x016E8B2C", "ldr      x26, [x22, #0xf8]", "GetVVer"),
        ("0x016E8BC8", "bl       #0x126bf1c", "GetVVer"),
        ("0x016E8D08", "ldr      x21, [x22, #0xf0]", "GetVVer"),
        ("0x016E8DA4", "bl       #0x126bf1c", "GetVVer"),
        ("0x016E8DF4", "ldr      x19, [x22, #0xd8]", "GetVVer"),
        ("0x016E8F08", "ldr      x27, [x22, #0xe0]", "GetVVer"),
        ("0x016E8FA8", "bl       #0x126bf1c", "GetVVer"),
        ("0x016E8FBC", "ldr      w19, [x22, #0x94]", "GetVVer"),
        ("0x016E91E4", "ldp      w21, w23, [x22, #0xb0]", "GetVVer"),
        ("0x016E921C", "str      w8, [x25, #4]", "GetVVer"),
        ("0x016E92E4", "ldr      x8, [x22, #0x108]", "GetVVer"),
        ("0x016E9CB4", "ldr      w19, [x22, #0x98]", "GetVVer"),
        ("0x016E9D08", "ldr      x12, [sp, #0x10]", "GetVVer"),
        ("0x016E9D40", "stur     x21, [x29, #-0x68]", "GetVVer"),
        ("0x016E9D44", "str      x8, [sp, #0x78]", "GetVVer"),
        ("0x016E9D48", "stur     w8, [x29, #-0x60]", "GetVVer"),
        ("0x016E9DF0", "mov      w1, #0x3fc", "GetVVer"),
        ("0x016E9F30", "mov      w1, #0x41a", "GetVVer"),
        # GetVVer old path and surviving modifier.
        ("0x016E9FCC", "ldr      x20, [x22, #0x28]", "GetVVer"),
        ("0x016EA0E4", "ldr      x24, [x22, #0x30]", "GetVVer"),
        ("0x016EA188", "bl       #0x126bf1c", "GetVVer"),
        ("0x016EA1B0", "ldr      x11, [sp, #0x58]", "GetVVer"),
        ("0x016EA1E8", "stur     x24, [x29, #-0x68]", "GetVVer"),
        ("0x016EA1EC", "str      x9, [sp, #0x78]", "GetVVer"),
        ("0x016EA1F0", "stur     w9, [x29, #-0x60]", "GetVVer"),
        ("0x016EA318", "ldr      w3, [x22, #0x80]", "GetVVer"),
        ("0x016EA330", "bl       #0x1968e24", "GetVVer"),
        ("0x016EA418", "mov      w1, #0x3fb", "GetVVer"),
        ("0x016EA4F0", "sxtw     x9, w21", "GetVVer"),
        ("0x016EA520", "stur     x21, [x29, #-0x68]", "GetVVer"),
        ("0x016EA524", "str      x9, [sp, #0x78]", "GetVVer"),
        ("0x016EA528", "stur     w9, [x29, #-0x60]", "GetVVer"),
        # Shared GetVVer return ABI.
        ("0x016EA52C", "ldr      x8, [sp, #0x78]", "GetVVer"),
        ("0x016EA530", "mov      x0, x21", "GetVVer"),
        ("0x016EA54C", "mov      w1, w8", "GetVVer"),
        ("0x016EA554", "ret", "GetVVer"),
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
        "source_sha256": source_sha,
        "repository_content_sha256": repository_sha,
        "repository_text_normalization": "Git LF checkout verified against original CRLF source SHA",
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
            "status": "structural_static_dataflow_bound_full_equations_unresolved",
            "new_path": {
                "shoot_distance_source_range": "0x016E85C8..0x016E85FC",
                "shoot_distance_map_load": "0x016E8630",
                "out_energy_max_map_load": "0x016E8768",
                "shoot_distance_to_out_energy_interpolate_call": "0x016E8804",
                "y_speed_max_map_load": "0x016E8830",
                "energy_map_new_load": "0x016E8908",
                "energy_to_y_speed_max_interpolate_call": "0x016E89F4",
                "shoot_point_h_up_map_load": "0x016E8B2C",
                "shoot_distance_to_point_up_interpolate_call": "0x016E8BC8",
                "shoot_point_h_down_map_load": "0x016E8D08",
                "shoot_distance_to_point_down_interpolate_call": "0x016E8DA4",
                "shoot_property_map_new_load": "0x016E8DF4",
                "energy_tolerance_map_load": "0x016E8F08",
                "property_to_energy_tolerance_interpolate_call": "0x016E8FA8",
                "energy_need_protect_load": "0x016E8FBC",
                "shoot_point_h_clamp_range": "0x016E91E4..0x016E921C",
                "shoot_dis_and_time_load": "0x016E92E4",
                "y_speed_min_load": "0x016E9CB4",
                "vector_construction_range": "0x016E9D08..0x016E9D48",
                "post_vector_spmove_modifiers": {
                    "logic_ids": ["0x3FC", "0x41A"],
                    "logic_id_loads": ["0x016E9DF0", "0x016E9F30"],
                    "normal_return_value_contribution": True,
                    "return_target": "0x016EA52C",
                    "interpretation": (
                        "Both modifier blocks operate on the already constructed vertical vector and "
                        "their rewritten vector state remains live into the shared return path."
                    ),
                },
            },
            "old_path": {
                "Flist_vVer_load": "0x016E9FCC",
                "vVerList_load": "0x016EA0E4",
                "base_interpolate_call": "0x016EA188",
                "vector_construction_range": "0x016EA1B0..0x016EA1F0",
                "speed_vVer_load": "0x016EA318",
                "speed_vVer_external_call": "0x016EA330",
                "post_vector_spmove_modifier": {
                    "logic_id": "0x3FB",
                    "logic_id_load": "0x016EA418",
                    "normal_return_value_contribution": True,
                    "final_write_range": "0x016EA4F0..0x016EA528",
                },
            },
            "return_range": "0x016EA52C..0x016EA554",
            "return_abi": "XVector3 packed as x0(low32=x, high32=y) plus w1=z",
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
            "GetVVer new path statically binds the distance/energy/point-height/property map chain, clamp, base vector construction, and surviving 0x3FC/0x41A vector modifiers.",
            "GetVVer old path statically binds Flist_vVer/vVerList interpolation, speed_vVer use, base vector construction, and the surviving 0x3FB vector modifier.",
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
