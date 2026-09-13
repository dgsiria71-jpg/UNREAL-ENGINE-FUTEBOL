import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SpmoveInventoryTests(unittest.TestCase):
    def test_canonical_and_candidate_action_blob_identity(self):
        report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_inventory.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(report["semantic_status"], "raw_identity_only")
        canonical, candidate = report["sources"]
        self.assertEqual(canonical["relation"], "canonical_baseline")
        self.assertEqual(candidate["relation"], "separate_hash_different_mobile_build")
        self.assertEqual(canonical["entries"][0]["sha256"], candidate["entries"][0]["sha256"])
        self.assertNotEqual(canonical["entries"][1]["sha256"], candidate["entries"][1]["sha256"])

    def test_inventory_does_not_close_physics_gate(self):
        report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_inventory.json")
            .read_text(encoding="utf-8")
        )
        unknowns = set(report["explicit_unknowns"])
        self.assertIn("spmoveInUseData VHor modifier", unknowns)
        self.assertIn("spmoveInUseData VVer modifier", unknowns)
        self.assertIn("GetKickVelocity composition", unknowns)


if __name__ == "__main__":
    unittest.main()
