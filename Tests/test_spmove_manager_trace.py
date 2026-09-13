import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SpmoveManagerStaticTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_manager_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_runtime_param_boundary_is_anchored(self):
        self.assertEqual(
            self.report["analysis_status"],
            "manager_selection_control_flow_only",
        )
        self.assertFalse(self.report["behavior_validated"])
        boundary = self.report["normalized_boundary"]
        self.assertEqual(boundary["field"], "param_Xnumber")
        self.assertEqual(boundary["record_offset"], "0x10")
        self.assertEqual(boundary["status"], "runtime_field_not_serialized")
        operations = {item["operation"] for item in self.report["confirmed_data_flow"]}
        self.assertIn("GetSpmoveData", operations)
        self.assertIn("GetSpmoveDataNoRatio", operations)

    def test_selector_chain_and_gate_remain_explicit(self):
        spans = {item["name"]: item for item in self.report["method_spans"]}
        self.assertEqual(spans["GetSpmoveData"]["start"], "0x01B72758")
        self.assertEqual(spans["GetSpmoveConfigByLogicId"]["start"], "0x01B72794")
        self.assertEqual(spans["GetSpmoveIds"]["start"], "0x01B72DA8")
        self.assertEqual(self.report["physics_gate"], "blocked")
        self.assertIn("param_Xnumber units and relation to VHor/VVer/GetKickVelocity", self.report["unknown"])
        self.assertIn("runtime behavior on representative inputs", self.report["unknown"])

    def test_no_overclaim_of_selection_semantics(self):
        self.assertIn("exact meaning of helper 0x2C6A4F8 and dictionary/list lookup semantics", self.report["unknown"])
        self.assertIn("which config wins when multiple IDs are present", self.report["unknown"])


if __name__ == "__main__":
    unittest.main()
