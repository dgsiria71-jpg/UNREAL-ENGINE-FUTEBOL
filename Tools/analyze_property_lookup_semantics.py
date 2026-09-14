"""Bind exact property lookup semantics from the published GetVVer evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts/native-recovery/getvver-upstream/20260914-011043-a18f1783/01_getvver_upstream_evidence.txt"
OUTPUT = ROOT / "Recovery/Normalized/property_lookup_semantics_static_trace.json"
EXPECTED_LF_SHA256 = "7053c4a888ac29355b83cea7ecc71f582a71fc2e3e6731f146a9ee569dcb6784"


def canonical_lf(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def require_all(text: str, needles: tuple[str, ...], label: str) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise ValueError(f"{label} evidence is incomplete: {missing}")


def analyze() -> dict:
    raw = EVIDENCE.read_bytes()
    normalized = canonical_lf(raw)
    actual = hashlib.sha256(normalized).hexdigest()
    if actual != EXPECTED_LF_SHA256:
        raise ValueError(f"evidence SHA mismatch: expected {EXPECTED_LF_SHA256}, got {actual}")
    text = normalized.decode("utf-8")

    require_all(text, (
        "METADATA_NAME: PlayerProperty$$GetPropertyValue",
        "01967D4C: ldr      x0, [x0, #0x28]",
        "01967D60: bl       #0x1b72794",
        "01967D78: bl       #0x1b726c0",
        "01967D84: ldr      x0, [x20, #0x20]",
        "01967D88: ldr      w2, [x21, #0x40]",
        "01967D94: bl       #0x1b6fd80",
        "01967D9C: ldr      x0, [x20, #0x10]",
        "01967DA8: bl       #0x1b718d8",
    ), "PlayerProperty.GetPropertyValue")
    require_all(text, (
        "METADATA_NAME: XProperty.XPropertyManager$$GetPropertyValue",
        "01B71914: ldr      x8, [x20, #0x10]",
        "01B7191C: ldr      w9, [x8, #0x18]",
        "01B71928: add      x8, x8, w19, sxtw #3",
        "01B7192C: ldr      x8, [x8, #0x20]",
        "01B71934: ldr      w0, [x8, #0x14]",
    ), "XPropertyManager.GetPropertyValue")
    require_all(text, (
        "## SHOOT_CONFIG_FIELDS_0x20_0x160",
        "0x24 | XNumber | shootAirBallHeighLimit",
        "0x148 | XNumber | dis_shootlong",
        "0x14C | XNumber | dis_shoot",
        "## FOOTBALL_FIELDS_0x90_0xA0",
        "0x98 | BallKickParam | lastKickParam",
        "NESTED_BONUS_TYPE: BallKickParam",
        "0x40 | BiographyUtility.BiographyPointType | biographyPointType",
        "0x44 | XNumber | BiographyPassProperty",
    ), "GetShootProperty metadata bindings")
    require_all(text, (
        "METADATA_NAME: PlayerProperty$$getShootPropertyWithSpmove",
        "01968888: bl       #0x1967d38",
        "019688AC: cmp      w21, #0",
        "019688C0: bl       #0x1b718d8",
    ), "getShootPropertyWithSpmove")

    return {
        "schema_version": "football.recovery.property_lookup_semantics.v1",
        "source_build": "football-dream-be-a-pro-1-221-5",
        "evidence": {
            "path": EVIDENCE.relative_to(ROOT).as_posix(),
            "sha256_lf": actual,
            "binary_sha256": "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
            "boundary_policy": "exact only when established by script.json ScriptMethod metadata",
        },
        "player_property_lookup": {
            "range": "0x01967D38..0x01967DC4",
            "metadata_name": "PlayerProperty$$GetPropertyValue",
            "arguments": ["property_type", "spmove_logic_id"],
            "spmove_manager_offset": "0x28",
            "buffer_manager_offset": "0x20",
            "property_manager_offset": "0x10",
            "spmove_path": "if enabled config exists and logic check passes, resolve buffer property using config field +0x40",
            "fallback": "manager_property.GetPropertyValue(property_type)",
        },
        "property_manager_lookup": {
            "range": "0x01B718D8..0x01B71958",
            "metadata_name": "XProperty.XPropertyManager$$GetPropertyValue",
            "array_offset": "0x10",
            "array_length_offset": "0x18",
            "array_data_offset": "0x20",
            "element_stride_bytes": 8,
            "value_field_offset": "0x14",
            "invalid_access": "native managed null/range exception paths; no synthetic fallback value",
        },
        "shoot_property_with_spmove": {
            "range": "0x019687C8..0x019688DC",
            "primary": "GetPropertyValue(property_type, mapped_spmove_logic_id)",
            "fallback_condition": "resolved raw XNumber <= 0",
            "fallback": "manager_property.GetPropertyValue(property_type)",
        },
        "corrected_metadata_bindings": {
            "threshold_config": "ShootConfig",
            "ShootConfig+0x24": "shootAirBallHeighLimit",
            "ShootConfig+0x148": "dis_shootlong",
            "ShootConfig+0x14C": "dis_shoot",
            "Football+0x98": "lastKickParam",
            "BallKickParam+0x40": "biographyPointType",
            "BallKickParam+0x44": "BiographyPassProperty",
        },
        "whole_getvver_equivalent": False,
        "physics_v0_3_gate": "BLOCKED",
        "remaining_unknowns": [
            "runtime spmove modifier 0x3FC/0x41A activation and parameter[2] ratios",
            "whole-function native differential vectors across GetVVer branches",
            "caller-visible final GetKickVelocity behavior and BALL_CONTACT.velocity binding",
        ],
    }


def main() -> int:
    payload = analyze()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PROPERTY_LOOKUP_SEMANTICS: GREEN output={OUTPUT} gate={payload['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
