import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VelocityBaseRegionsTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "velocity_base_regions_static_trace.json").read_text(encoding="utf-8")
        )

    def test_shared_selector_splits_old_and_new_paths(self):
        self.assertEqual(self.report["analysis_status"], "old_new_config_path_split_static_confirmed")
        self.assertFalse(self.report["behavior_validated"])
        for method in ("GetVHor", "GetVVer"):
            self.assertEqual(self.report["confirmed_paths"][method]["selector"], "ShootSpeedConfigItem.useNewMethod +0x90")

    def test_vhor_field_families_are_separate(self):
        path = self.report["confirmed_paths"]["GetVHor"]
        self.assertEqual(path["old_when_zero_fields"], ["Flist_vHor", "vHorList", "speed_vHor"])
        self.assertIn("energyMapNew", path["new_when_nonzero_fields"])
        self.assertIn("vHorRateNew", path["new_when_nonzero_fields"])

    def test_vver_field_families_are_separate(self):
        path = self.report["confirmed_paths"]["GetVVer"]
        self.assertEqual(path["old_when_zero_fields"], ["Flist_vVer", "vVerList", "speed_vVer"])
        self.assertIn("shootDisAndTime", path["new_when_nonzero_fields"])
        self.assertIn("energyNeedProtect", path["new_when_nonzero_fields"])

    def test_trace_does_not_overclaim_equations(self):
        self.assertEqual(self.report["physics_gate"], "blocked")
        self.assertIn("complete interpolation and clamp sequence in each path", self.report["unknown"])
        self.assertIn("final spmove modifier join, GetKickVelocity composition and BALL_CONTACT velocity", self.report["unknown"])


if __name__ == "__main__":
    unittest.main()