"""Recover GetShootSpeedVRate normal-return arithmetic from canonical ARM64 evidence.

The result is source-bound static recovery. It closes the caller-visible equation
and the discrete XRandom.Range interpolation, while leaving the RNG state and the
full GetShootVerRate property-selection behavior outside this slice.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "native-recovery" / "shoot-helpers" / "20260913-175551-3fafba6a"
SOURCE = BASE / "01_shoot_helper_disassembly.txt"
SUPPORT = BASE / "02_shoot_speed_v_rate_support_disassembly.txt"
METADATA = BASE / "03_shoot_speed_v_rate_metadata.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_speed_v_rate_static_trace.json"

SOURCE_LF_SHA256 = "284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58"
SUPPORT_LF_SHA256 = "64a5a6db69fe3d21f78a056fd81728f21e03465d4283581a8627d98bc6db90bd"
METADATA_LF_SHA256 = "3556db3a9e1457ab1626c1950f4d90c44d859fadefbf142e2e60a6556b6f5bf3"
BINARY_SHA256 = "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496"

LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


def _lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _lf_sha256(path: Path) -> str:
    return hashlib.sha256(_lf_bytes(path)).hexdigest()


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


def _verify_metadata(path: Path) -> None:
    text = _lf_bytes(path).decode("utf-8")
    required = (
        "LIBIL2CPP_SHA256: 2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
        "GLOBAL_METADATA_SHA256: 92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e",
        "DUMP_CS_SHA256: 4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe",
        "public XNumber GetShootVerRate(XGoalTypeEnum goal_child) { }",
        "public XNumber GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) { }",
        "public int disArea; // 0x80",
        "public static readonly XNumber zero; // 0x8",
        "public static readonly XNumber one; // 0xC",
        "public static XNumber op_Division(XNumber lhs, int rhs) { }",
        "private static int NextInt(int n) { }",
        "public static XNumber Range(XNumber min, XNumber max) { }",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise ValueError(f"metadata anchors missing: {missing!r}")


def analyze(
    source: Path = SOURCE,
    support: Path = SUPPORT,
    metadata: Path = METADATA,
) -> dict:
    source_sha = _lf_sha256(source)
    support_sha = _lf_sha256(support)
    metadata_sha = _lf_sha256(metadata)
    if source_sha != SOURCE_LF_SHA256:
        raise ValueError(f"helper source normalized SHA mismatch: {source_sha}")
    if support_sha != SUPPORT_LF_SHA256:
        raise ValueError(f"support source normalized SHA mismatch: {support_sha}")
    if metadata_sha != METADATA_LF_SHA256:
        raise ValueError(f"metadata source normalized SHA mismatch: {metadata_sha}")
    _verify_metadata(metadata)

    ins = parse_instructions(source)
    support_ins = parse_instructions(support)

    # Exact GetShootSpeedVRate parameter capture and GetShootVerRate input.
    anchors = (
        (0x1968E40, "mov x19, x3"),
        (0x1968E44, "mov x20, x2"),
        (0x1968E48, "mov w21, w1"),
        (0x1968E70, "mov w1, w21"),
        (0x1968E78, "bl #0x1968c34"),
        # fixed_mul(GetShootVerRate(goal_child), c)
        (0x1968EAC, "sxtw x9, w19"),
        (0x1968EB0, "sxtw x10, w21"),
        (0x1968EB4, "mov x11, #0x200"),
        (0x1968EB8, "madd x21, x10, x9, x11"),
        (0x1968ED8, "lsr x21, x21, #0xa"),
        # First F / 100 and multiply. F==0 selects XNumber.zero.
        (0x1968EDC, "cbz w20, #0x1968f1c"),
        (0x1968EE8, "smull x10, w20, w8"),
        (0x1968EFC, "msub w9, w10, w9, w20"),
        (0x1968F18, "b #0x1968f4c"),
        (0x1968F44, "ldr x9, [x0, #0xb8]"),
        (0x1968F48, "ldr w9, [x9, #8]"),
        (0x1968F58, "madd x21, x10, x9, x11"),
        (0x1968F78, "lsr x21, x21, #0xa"),
        # Second F / 100 and multiply, followed by XNumber.one.
        (0x1968F7C, "cbz w20, #0x1968fc4"),
        (0x1968FEC, "ldr w20, [x9, #0xc]"),
        (0x1969004, "madd x10, x11, x10, x12"),
        (0x1969008, "add x21, x20, x10, lsr #10"),
        # c sign split, disArea raw delta and one-sided clamp.
        (0x196900C, "cmp w8, w19"),
        (0x1969014, "b.le #0x19690a0"),
        (0x196906C, "ldr w9, [x0, #0x80]"),
        (0x1969074, "add x22, x21, x9"),
        (0x1969094, "cmp w20, w22"),
        (0x1969098, "csel x20, x21, x20, gt"),
        (0x19690F4, "ldr w9, [x0, #0x80]"),
        (0x19690FC, "sub x22, x21, x9"),
        (0x196911C, "cmp w20, w22"),
        (0x1969120, "csel x20, x21, x20, lt"),
        # Caller-visible randomized return.
        (0x1969144, "mov x0, x20"),
        (0x1969148, "mov x1, x19"),
        (0x1969150, "bl #0x192a0c4"),
        (0x1969168, "ret"),
        # XRandom.Range interpolation around NextInt(1001).
        (0x192A128, "sub x20, x20, x19"),
        (0x192A144, "mov w0, #0x3e9"),
        (0x192A148, "bl #0x1929d88"),
        (0x192A154, "mul w20, w0, w20"),
        (0x192A164, "sbfiz x8, x20, #0xa, #0x20"),
        (0x192A174, "sdiv x11, x8, x9"),
        (0x192A178, "msub x8, x11, x9, x8"),
        (0x192A180, "sdiv x8, x8, x9"),
        (0x192A184, "add w8, w8, w11"),
        (0x192A1CC, "add w0, w8, w19"),
    )
    for address, expected in anchors:
        require(ins, address, expected)

    # Exact support methods prove the inlined division rule and NextInt range.
    for address, expected in (
        (0x1B6B3C0, "sdiv w8, w20, w19"),
        (0x1B6B3C4, "msub w9, w8, w19, w20"),
        (0x1B6B3C8, "lsl w9, w9, #1"),
        (0x1B6B3CC, "sdiv w9, w9, w19"),
        (0x1B6B3D0, "add w8, w9, w8"),
        (0x1929DC0, "cmp w19, #0"),
        (0x1929E18, "sub w8, w19, #1"),
        (0x1929E44, "udiv w9, w0, w19"),
        (0x1929E48, "msub w0, w9, w19, w0"),
        (0x1929E54, "b.lt #0x1929e20"),
        (0x1929E64, "ret"),
    ):
        require(support_ins, address, expected)

    return {
        "schema_version": "football.recovery.shoot_speed_v_rate_static_trace.v1",
        "analysis_status": "static_normal_return_equation_confirmed_rng_state_unresolved",
        "behavior_validated": False,
        "sources": {
            "helper_disassembly": source.relative_to(ROOT).as_posix(),
            "helper_disassembly_lf_sha256": source_sha,
            "support_disassembly": support.relative_to(ROOT).as_posix(),
            "support_disassembly_lf_sha256": support_sha,
            "metadata_excerpt": metadata.relative_to(ROOT).as_posix(),
            "metadata_excerpt_lf_sha256": metadata_sha,
            "binary_sha256": BINARY_SHA256,
        },
        "fixed_point": {
            "fraction_bits": 10,
            "one_raw": 1024,
            "multiply_bias": 512,
            "divide_by_int_formula": "q=trunc(lhs_raw/rhs); r=lhs_raw-q*rhs; result_raw=q+trunc(2*r/rhs)",
        },
        "GetShootSpeedVRate": {
            "span": "0x01968E24..0x0196916C",
            "signature": "GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) -> XNumber",
            "arguments": {
                "w1": "goal_child",
                "x2": "F XNumber raw; divided by integer 100 before use",
                "x3": "c XNumber raw; sign selects the bound branch and value is the second Range endpoint",
            },
            "force_ratio": "F / 100 using XNumber.op_Division(XNumber,int)",
            "force_ratio_zero_behavior": "F raw zero selects XNumber.zero without division",
            "force_ratio_uses": 2,
            "base_formula": "one + fixed_mul(fixed_mul(fixed_mul(GetShootVerRate(goal_child), c), force_ratio), force_ratio)",
            "ai_config_field": "AIParameterConfig.disArea",
            "ai_config_field_storage_type": "int",
            "ai_config_field_offset": "+0x80",
            "ai_config_field_runtime_use": "direct signed raw delta in XNumber-domain arithmetic",
            "positive_c_condition": "zero <= c",
            "positive_c_bound": "min(one, base + disArea_raw)",
            "negative_c_condition": "zero > c",
            "negative_c_bound": "max(one, base - disArea_raw)",
            "return_formula": "XRandom.Range(sign_selected_bound, c)",
            "normal_return_equation_recovered": True,
            "random_sample_resolved_without_rng_state": False,
        },
        "XRandom.Range": {
            "span": "0x0192A0C4..0x0192A1E0",
            "signature": "Range(XNumber from, XNumber to) -> XNumber",
            "sample_source": "XRandom.NextInt(1001)",
            "sample_domain": "integer 0..1000 inclusive from Random.Range(1001)",
            "formula": "from + divide_by_int((to - from) * sample, 1000)",
            "product_width": "signed 32-bit wrapped multiply before division",
            "endpoints": {"sample_0": "from", "sample_1000": "to"},
            "rng_state_transition_recovered": False,
        },
        "confirmed_interpretation": [
            "F is an XNumber parameter normalized by the integer 100 and applied twice with native fixed-point rounding.",
            "AIParameterConfig +0x80 is metadata-bound to int disArea and is consumed directly as a signed raw fixed-point-domain delta.",
            "The sign of c selects a one-sided bound around one before XRandom.Range interpolates from that bound to c.",
            "XRandom.Range has a closed caller-visible discrete interpolation equation, but the random sample cannot be predicted without the original RNG state.",
        ],
        "remaining_unknowns": [
            "GetShootVerRate property-selection semantics and all goal-child-specific source values",
            "semantic design intent and authored unit convention of AIParameterConfig.disArea beyond its proven raw runtime use",
            "original RNG state and sequence at each call",
            "exception and type-initialization paths outside the normal return",
        ],
        "physics_v0_3_gate": "BLOCKED",
        "next_gate": "recover nested shootDisAndTime arithmetic/time path and compose the legacy GetVVer executable path",
    }


def main() -> int:
    trace = analyze()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"SHOOT_SPEED_V_RATE: GREEN output={OUTPUT} gate={trace['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
