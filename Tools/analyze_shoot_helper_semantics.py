"""Recover bounded shoot-helper semantics from the published ARM64 listing.

This analyzer is intentionally conservative. It closes only arithmetic and
forwarding behavior that is directly anchored in the canonical 1-221-5 helper
listing. It does not claim the complete GetShootSpeedVRate equation or the final
BALL_CONTACT velocity path.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "artifacts"
    / "native-recovery"
    / "shoot-helpers"
    / "20260913-175551-3fafba6a"
    / "01_shoot_helper_disassembly.txt"
)
CALLER_SOURCE = (
    ROOT
    / "artifacts"
    / "native-recovery"
    / "20260913-163217-9cdb54d0"
    / "01_disassembly_shoot.txt"
)
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_helper_semantics_static_trace.json"
SOURCE_SHA256 = "284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58"
BINARY_SHA256 = "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496"

HEADER_RE = re.compile(
    r"^###\s+(?P<label>TARGET|CALLEE)\s+(?P<name>\S+)\s+"
    r"(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s+"
    r"boundary=(?P<boundary>\S+)\s+exact=(?P<exact>true|false)$"
)
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")


@dataclass
class Block:
    label: str
    name: str
    start: int
    end: int
    boundary: str
    exact: bool
    metadata_name: str | None


def _norm(instruction: str) -> str:
    return " ".join(instruction.strip().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse(path: Path):
    blocks: dict[int, Block] = {}
    instructions: dict[int, str] = {}
    current: Block | None = None
    binary_sha: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("BINARY_SHA256:"):
            binary_sha = raw.split(":", 1)[1].strip()
            continue
        header = HEADER_RE.match(raw.strip())
        if header:
            current = Block(
                label=header.group("label"),
                name=header.group("name"),
                start=int(header.group("start"), 16),
                end=int(header.group("end"), 16),
                boundary=header.group("boundary"),
                exact=header.group("exact") == "true",
                metadata_name=None,
            )
            blocks[current.start] = current
            continue
        if raw.startswith("METADATA_NAME:") and current is not None:
            current.metadata_name = raw.split(":", 1)[1].strip()
            continue
        match = LINE_RE.match(raw.strip())
        if match:
            instructions[int(match.group("address"), 16)] = _norm(match.group("instruction"))

    if binary_sha is None:
        raise ValueError("helper listing is missing BINARY_SHA256")
    return binary_sha, blocks, instructions


def parse_plain_instructions(path: Path) -> dict[int, str]:
    instructions: dict[int, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = LINE_RE.match(raw.strip())
        if match:
            instructions[int(match.group("address"), 16)] = _norm(match.group("instruction"))
    return instructions


def require(ins: dict[int, str], address: int, expected: str) -> None:
    actual = ins.get(address)
    wanted = _norm(expected)
    if actual != wanted:
        raise ValueError(f"0x{address:08X}: expected {wanted!r}, got {actual!r}")


def require_block(
    blocks: dict[int, Block],
    start: int,
    *,
    end: int,
    exact: bool,
    metadata_name: str | None,
) -> Block:
    block = blocks.get(start)
    if block is None:
        raise ValueError(f"missing block 0x{start:08X}")
    if block.end != end or block.exact != exact or block.metadata_name != metadata_name:
        raise ValueError(
            f"block 0x{start:08X} mismatch: end=0x{block.end:08X} "
            f"exact={block.exact} metadata={block.metadata_name!r}"
        )
    return block


def analyze(path: Path = SOURCE) -> dict:
    source_sha = _sha256(path)
    if source_sha != SOURCE_SHA256:
        raise ValueError(f"helper source SHA mismatch: {source_sha}")

    binary_sha, blocks, ins = parse(path)
    if binary_sha != BINARY_SHA256:
        raise ValueError(f"binary SHA mismatch: {binary_sha}")

    remap_block = require_block(
        blocks,
        0x126BF1C,
        end=0x126CF1C,
        exact=False,
        metadata_name=None,
    )
    lerp_block = require_block(
        blocks,
        0x126C3FC,
        end=0x126C5FC,
        exact=False,
        metadata_name=None,
    )
    old_vver = require_block(
        blocks,
        0x1968E24,
        end=0x196916C,
        exact=True,
        metadata_name="PlayerProperty$$GetShootSpeedVRate",
    )
    spmove_ratio = require_block(
        blocks,
        0x196807C,
        end=0x196808C,
        exact=True,
        metadata_name="PlayerProperty$$GetSpmoveDataRatio",
    )
    require_block(
        blocks,
        0x1968C34,
        end=0x1968E24,
        exact=True,
        metadata_name="PlayerProperty$$GetShootVerRate",
    )
    require_block(
        blocks,
        0x192A0C4,
        end=0x192A1E0,
        exact=True,
        metadata_name="XRandom$$Range",
    )
    singleton = blocks.get(0x1FF58AC)
    if singleton is None or not singleton.exact or singleton.metadata_name != "XBaseLocalSetting<AIParameterConfig>$$get_Singleton":
        raise ValueError("AIParameterConfig singleton callee identity mismatch")

    # 0x126BF1C: argument preservation, equal-range guard, sequential clamp,
    # fixed-point inverse-lerp ratio, and final lerp call.
    for address, expected in (
        (0x126BF3C, "mov x20, x4"),
        (0x126BF40, "mov x19, x3"),
        (0x126BF44, "mov x21, x2"),
        (0x126BF48, "mov x22, x1"),
        (0x126BF4C, "mov x23, x0"),
        (0x126BF6C, "cmp w22, w21"),
        (0x126BF70, "b.eq #0x126c05c"),
        (0x126BF9C, "cmp w23, w21"),
        (0x126BFA0, "csel x9, x21, x23, gt"),
        (0x126BFA4, "cmp w23, w22"),
        (0x126BFAC, "csel x23, x22, x9, lt"),
        (0x126BFC8, "ldrb w8, [x25, #0xe1a]"),
        (0x126BFCC, "sub x23, x23, x22"),
        (0x126BFF8, "sub x8, x21, x22"),
        (0x126C000, "sbfiz x9, x23, #0xa, #0x20"),
        (0x126C008, "sdiv x10, x9, x8"),
        (0x126C00C, "msub x9, x10, x8, x9"),
        (0x126C010, "lsl x9, x9, #1"),
        (0x126C014, "sdiv x8, x9, x8"),
        (0x126C018, "add w8, w8, w10"),
        (0x126C040, "ldr w8, [x8, #8]"),
        (0x126C044, "mov w2, w8"),
        (0x126C048, "and x0, x19, #0xffffffff"),
        (0x126C04C, "and x1, x20, #0xffffffff"),
        (0x126C054, "bl #0x126c3fc"),
        (0x126C05C, "and x0, x19, #0xffffffff"),
        (0x126C074, "ret"),
        (0x126C078, "str x21, [sp, #-0x30]!"),
    ):
        require(ins, address, expected)

    # 0x126C3FC: t is clamped to XNumber zero/one, then the recovered
    # +512 >> 10 multiply is applied before adding out_min.
    for address, expected in (
        (0x126C414, "mov x21, x2"),
        (0x126C418, "mov x20, x1"),
        (0x126C41C, "mov x19, x0"),
        (0x126C468, "tbnz w21, #0x1f, #0x126c4c0"),
        (0x126C474, "cmp w21, #0x401"),
        (0x126C47C, "b.lt #0x126c4f4"),
        (0x126C498, "ldr x8, [x0, #0xb8]"),
        (0x126C49C, "add x8, x8, #0xc"),
        (0x126C4E4, "ldr x8, [x0, #0xb8]"),
        (0x126C4E8, "add x8, x8, #8"),
        (0x126C4EC, "ldr w21, [x8]"),
        (0x126C4F4, "and x21, x21, #0xffffffff"),
        (0x126C50C, "sub w8, w20, w19"),
        (0x126C510, "sxtw x9, w21"),
        (0x126C514, "sxtw x8, w8"),
        (0x126C518, "mov x10, #0x200"),
        (0x126C51C, "madd x8, x9, x8, x10"),
        (0x126C520, "lsr x8, x8, #0xa"),
        (0x126C524, "add w0, w8, w19"),
        (0x126C534, "ret"),
        (0x126C538, "sub sp, sp, #0x40"),
    ):
        require(ins, address, expected)

    # Exact GetShootSpeedVRate structure. The identity and value-producing
    # callees are closed, but the complete input/config units are still open.
    for address, expected in (
        (0x1968E6C, "ldr x8, [x22, #0x30]"),
        (0x1968E70, "mov w1, w21"),
        (0x1968E74, "ldr x0, [x8, #0x1b0]"),
        (0x1968E78, "bl #0x1968c34"),
        (0x196905C, "ldr x0, [x8]"),
        (0x1969060, "bl #0x1ff58ac"),
        (0x196906C, "ldr w9, [x0, #0x80]"),
        (0x19690E4, "ldr x0, [x8]"),
        (0x19690E8, "bl #0x1ff58ac"),
        (0x19690F4, "ldr w9, [x0, #0x80]"),
        (0x1969144, "mov x0, x20"),
        (0x1969148, "mov x1, x19"),
        (0x1969150, "bl #0x192a0c4"),
        (0x1969168, "ret"),
    ):
        require(ins, address, expected)

    # Exact spmove-ratio forwarder.
    for address, expected in (
        (0x196807C, "ldr x0, [x0, #0x28]"),
        (0x1968080, "and w2, w2, #1"),
        (0x1968084, "mov x3, xzr"),
        (0x1968088, "b #0x1b72814"),
    ):
        require(ins, address, expected)

    caller = parse_plain_instructions(CALLER_SOURCE)
    require(caller, 0x16EA318, "ldr w3, [x22, #0x80]")
    require(caller, 0x16EA31C, "ldr w1, [sp, #0x54]")
    require(caller, 0x16EA320, "mov x2, x20")
    require(caller, 0x16EA324, "mov x4, xzr")
    require(caller, 0x16EA330, "bl #0x1968e24")

    return {
        "schema_version": "football.recovery.shoot_helper_semantics_static_trace.v1",
        "source": "artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt",
        "source_sha256": source_sha,
        "binary_sha256": binary_sha,
        "analysis_status": "static_helper_semantics_partial_confirmed",
        "behavior_validated": False,
        "remap_0x126BF1C": {
            "extraction_window": [f"0x{remap_block.start:08X}", f"0x{remap_block.end:08X}"],
            "metadata_exact_boundary": remap_block.exact,
            "normal_return_end": "0x0126C074",
            "normal_path_formula_recovered": True,
            "arguments": {
                "x0": "input",
                "x1": "in_min",
                "x2": "in_max",
                "x3": "out_min",
                "x4": "out_max",
            },
            "equal_input_bounds": "return_out_min",
            "input_clamp": "input < in_min ? in_min : (input > in_max ? in_max : input)",
            "ratio_fraction_bits": 10,
            "ratio_zero_raw": 0,
            "ratio_formula": "n=(bounded-in_min)*1024; d=in_max-in_min; q=trunc(n/d); r=n-q*d; ratio=q + trunc(2*r/d)",
            "lerp_helper": "0x0126C3FC",
            "formula": "lerp(out_min, out_max, inverse_lerp_fixed(input,in_min,in_max) after native sequential clamp)",
            "confidence": "confirmed normal-return arithmetic; extraction window itself is not a metadata-proven function boundary",
        },
        "lerp_0x126C3FC": {
            "extraction_window": [f"0x{lerp_block.start:08X}", f"0x{lerp_block.end:08X}"],
            "metadata_exact_boundary": lerp_block.exact,
            "normal_return_end": "0x0126C534",
            "t_clamp_raw": [0, 1024],
            "multiply_bias": 512,
            "fraction_bits": 10,
            "formula": "out_min + fixed_mul(out_max - out_min, clamp(t, 0, 1024))",
            "confidence": "confirmed normal-return arithmetic; extraction window itself is not a metadata-proven function boundary",
        },
        "old_vver_0x1968E24": {
            "start": "0x01968E24",
            "end": "0x0196916C",
            "exact_function_boundary": old_vver.exact,
            "metadata_name": old_vver.metadata_name,
            "first_value_callee_address": "0x01968C34",
            "first_value_callee": "PlayerProperty$$GetShootVerRate",
            "config_singleton_address": "0x01FF58AC",
            "config_singleton_callee": "XBaseLocalSetting<AIParameterConfig>$$get_Singleton",
            "config_field_offset": "+0x80",
            "random_callee_address": "0x0192A0C4",
            "random_callee": "XRandom$$Range",
            "caller_speed_vver_load": "0x016EA318:+0x80->w3",
            "caller_callsite": "0x016EA330",
            "caller_registers": {"w1": "GetVVer stack argument +0x54", "x2": "GetVVer x20", "w3": "ShootSpeedConfigItem +0x80", "x4": "null"},
            "full_equation_recovered": False,
            "remaining_unknowns": [
                "semantic units/ranges of all GetShootSpeedVRate inputs",
                "semantic name/units of AIParameterConfig field +0x80",
                "complete branch-by-branch equation and randomization bounds",
            ],
        },
        "spmove_ratio_0x196807C": {
            "start": "0x0196807C",
            "end": "0x0196808C",
            "exact_function_boundary": spmove_ratio.exact,
            "metadata_name": spmove_ratio.metadata_name,
            "manager_offset": "+0x28",
            "no_ratio_mask": 1,
            "tail_target": "0x01B72814",
            "tail_semantics": "SpmoveManager.GetSpmoveDataNoRatio",
            "forwarding_semantics_recovered": True,
        },
        "physics_v0_3_gate": "BLOCKED",
        "still_required": [
            "close nested shootDisAndTime arithmetic/time path",
            "close the full GetShootSpeedVRate equation/units or prove the exact needed caller result behavior",
            "turn GetVHor/GetVVer into executable source-bound equations and validate",
            "close final GetKickVelocity behavior and bind BALL_CONTACT.velocity",
            "complete regression before packaging v0.3",
        ],
    }


def main() -> int:
    trace = analyze(SOURCE)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "SHOOT_HELPER_SEMANTICS: GREEN "
        f"source_sha256={trace['source_sha256']} gate={trace['physics_v0_3_gate']} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
