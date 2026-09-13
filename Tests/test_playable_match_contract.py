import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PlayableMatchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(
            (ROOT / "Recovery" / "Normalized" / "playable_match_contract.json")
            .read_text(encoding="utf-8")
        )

    def test_modes_and_actions_are_explicit(self):
        self.assertEqual(
            [mode["id"] for mode in self.contract["modes"]],
            ["3v3", "5v5", "11v11"],
        )
        self.assertEqual(len(self.contract["actions"]), 5)
        self.assertIn("goalkeeper_save", {action["id"] for action in self.contract["actions"]})

    def test_provenance_keeps_mobile_gate_separate(self):
        provenance = self.contract["provenance"]
        self.assertEqual(provenance["kind"], "new_game_authored")
        self.assertIn("physics_v0_3_gate", provenance["mobile_recovery_semantics"])
        self.assertFalse(self.contract["simulation"]["ball_impulse_fallback"])

    def test_fixed_step_and_performance_are_targets_not_measurements(self):
        self.assertEqual(self.contract["simulation"]["fixed_step_hz"], 120)
        self.assertTrue(self.contract["simulation"]["render_interpolation"])
        self.assertEqual(self.contract["performance"]["target_fps"], 120)
        self.assertEqual(self.contract["performance"]["measurement_status"], "not_measured_on_this_machine")

    def test_unreal_import_plan_references_the_contract(self):
        plan = json.loads(
            (ROOT / "Recovery" / "Normalized" / "unreal_import_plan.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            plan["normalized_artifacts"]["playable_match_contract"],
            "Recovery/Normalized/playable_match_contract.json",
        )
        self.assertTrue(plan["playable_match"]["available"])


if __name__ == "__main__":
    unittest.main()
