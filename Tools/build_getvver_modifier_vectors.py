"""Generate bounded GetVVer modifier vectors from recovered runtime ratios."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATIOS = ROOT / "Recovery/Normalized/getvver_spmove_runtime_ratios.json"
OUTPUT = ROOT / "Recovery/Normalized/getvver_spmove_modifier_vectors.json"


def canonical_sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def wrap_i32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value if value <= 0x7FFFFFFF else value - 0x100000000


def fixed_mul(a: int, b: int) -> int:
    biased = (a * b + 512) & 0xFFFFFFFFFFFFFFFF
    return wrap_i32(biased >> 10)


def scale(vector: list[int], factor: int) -> list[int]:
    return [fixed_mul(component, factor) for component in vector]


def build() -> dict:
    ratios = json.loads(RATIOS.read_text(encoding="utf-8"))
    long_group = ratios["modifiers"]["0x3FC"]
    push_group = ratios["modifiers"]["0x41A"]
    long_index = long_group["record_ids"].index(102003)
    push_index = push_group["record_ids"].index(105002)
    long_ratio = long_group["param2_raw_by_level"][long_index]
    push_ratio = push_group["param2_raw_by_level"][push_index]
    if (long_ratio, push_ratio) != (700, 800):
        raise ValueError("recovered representative child ratios changed")

    base = [-3000, 1537, 777]
    after_long = scale(base, long_ratio)
    after_push = scale(base, push_ratio)
    after_both = scale(after_long, push_ratio)
    combined_ratio = fixed_mul(long_ratio, push_ratio)

    return {
        "schema_version": "football.recovery.getvver_spmove_modifier_vectors.v1",
        "source_build": "football-dream-be-a-pro-1-221-5",
        "source": {
            "path": RATIOS.relative_to(ROOT).as_posix(),
            "canonical_lf_sha256": canonical_sha(RATIOS),
        },
        "base_vector_raw": base,
        "explicit_post_eligibility_inventories": {
            "0x3FC": {
                "eligible_child_ids": [102001, 102003],
                "selected_child_id": 102003,
                "selected_level": 3,
                "param2_raw": long_ratio,
            },
            "0x41A": {
                "eligible_child_ids": [105001, 105002],
                "selected_child_id": 105002,
                "selected_level": 2,
                "param2_raw": push_ratio,
            },
        },
        "flags": {"0x3FC": "byte 5 nonzero", "0x41A": "byte 0 nonzero"},
        "cases": {
            "none": {"active": [], "output_raw": base},
            "0x3FC": {"active": ["0x3FC"], "output_raw": after_long},
            "0x41A": {"active": ["0x41A"], "output_raw": after_push},
            "both": {
                "active": ["0x3FC", "0x41A"],
                "output_raw": after_both,
                "rounding": "fixed_mul is committed after 0x3FC and before 0x41A",
            },
        },
        "combined_ratio_shortcut": {
            "ratio_raw": combined_ratio,
            "output_x_raw": fixed_mul(base[0], combined_ratio),
            "native_order_output_x_raw": after_both[0],
            "allowed": False,
        },
        "executable_reference": {
            "adapter": "Reference/FootballPhysics/GetVVerSpmoveRuntime.h",
            "test": "Tests/getvver_spmove_modifier_vectors_test.cpp",
        },
        "scope": "representative source-bound host vectors using explicit post-eligibility inventories",
        "native_differential_validated": False,
        "whole_getvver_equivalent": False,
        "physics_v0_3_gate": "BLOCKED",
        "next_gate": "capture or execute matching canonical ARM64 GetVVer cases and compare whole-function outputs",
    }


def main() -> int:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"GETVVER_MODIFIER_VECTORS: GREEN output={OUTPUT} gate={payload['physics_v0_3_gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
