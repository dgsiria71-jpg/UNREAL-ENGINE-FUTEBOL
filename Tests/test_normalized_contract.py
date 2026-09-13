import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NormalizedContractTests(unittest.TestCase):
    def test_contract_keeps_unresolved_physics_explicit(self):
        contract = json.loads(
            (ROOT / "Recovery" / "Normalized" / "physics_runtime_contract.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(contract["fixed_point"]["one_raw"], 1024)
        self.assertEqual(contract["animation_timing"]["clip_sample_rate_fps"], 30)
        self.assertEqual(contract["runtime_fields"]["0x1C0"]["name"], "vertical_accel_raw")
        self.assertEqual(contract["spmove"]["gate"], "blocked")
        self.assertEqual(contract["ball_contact"]["unresolved_fallback"], "forbidden")
        runtime = contract["spmove"]["runtime_static_evidence"]
        self.assertEqual(runtime["property_logic_id_alignment"]["status"], "numeric_property_to_logic_id_alignment_only")
        self.assertEqual(runtime["property_logic_id_alignment"]["levels_per_group"], [1, 2, 3, 4, 5])

    def test_manifest_and_contract_agree_on_engine_and_neymar_policy(self):
        manifest = json.loads(
            (ROOT / "Recovery" / "Normalized" / "recovery_manifest.json")
            .read_text(encoding="utf-8")
        )
        contract = json.loads(
            (ROOT / "Recovery" / "Normalized" / "physics_runtime_contract.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["engine_target"], contract["engine_target"])
        self.assertEqual(manifest["semantic_gates"]["neymar"], contract["neymar"]["status"])


if __name__ == "__main__":
    unittest.main()
