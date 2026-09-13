import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FeatureCoverageTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "feature_coverage.json")
            .read_text(encoding="utf-8")
        )

    def test_archives_are_present_hash_bound_and_crc_clean(self):
        for source in self.report["archives"].values():
            self.assertTrue(source["present"])
            self.assertTrue(source["hash_matches"])
            self.assertEqual(source["crc"], "green")
            self.assertGreater(source["entries"], 0)

    def test_report_never_claims_complete_game(self):
        summary = self.report["summary"]
        self.assertFalse(summary["all_requested_systems_recovered"])
        self.assertFalse(summary["all_requested_systems_integrated"])
        self.assertFalse(summary["playable_unreal_match"])
        self.assertEqual(summary["physics_v0_3_gate"], "blocked")

    def test_requested_gaps_are_explicit(self):
        features = {item["feature"]: item for item in self.report["features"]}
        self.assertIn("placed/curved/chipped/lob shots", features["Pass, shot, dribble and defense"]["gaps"])
        self.assertIn("Player/Team/Tactical/GK AI", features["Game AI"]["gaps"])
        self.assertIn("Broadcast camera", features["Cameras and field views"]["gaps"])
        self.assertIn("2,769 logical action mappings", features["Animation controller and COFMotion"]["gaps"])


if __name__ == "__main__":
    unittest.main()
