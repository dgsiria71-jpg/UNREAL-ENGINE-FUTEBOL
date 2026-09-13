import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NativeStaticTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "native_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_method_spans_and_gate(self):
        spans = {item["name"]: item for item in self.report["method_spans"]}
        self.assertEqual(spans["GetVHor"]["start"], "0x016E6A80")
        self.assertEqual(spans["GetVVer"]["start"], "0x016E84A4")
        self.assertEqual(spans["GetKickVelocity"]["start"], "0x016EBAD8")
        self.assertFalse(self.report["behavior_validated"])
        self.assertEqual(self.report["physics_gate"], "blocked")

    def test_kick_velocity_calls_both_helpers(self):
        kick = next(item for item in self.report["method_spans"] if item["name"] == "GetKickVelocity")
        targets = {item["target"] for item in kick["call_targets"]}
        self.assertIn("0X16E6A80", targets)
        self.assertIn("0X16E84A4", targets)

    def test_spmove_masks_are_recorded_without_semantic_claim(self):
        vhor = next(item for item in self.report["method_spans"] if item["name"] == "GetVHor")
        vver = next(item for item in self.report["method_spans"] if item["name"] == "GetVVer")
        vhor_masks = {item["mask"] for item in vhor["literal_mask_operands"]}
        vver_masks = {item["mask"] for item in vver["literal_mask_operands"]}
        self.assertIn("0XFF000000", vhor_masks)
        self.assertIn("0XFF0000000000", vhor_masks)
        self.assertIn("0XFF", vver_masks)
        self.assertIn("0XFF00000000", vver_masks)
        self.assertIn("arithmetic equations", self.report["unknown"])


if __name__ == "__main__":
    unittest.main()
