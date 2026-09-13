import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpmoveModifierAccessTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_modifier_access_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_access_trace_is_static_and_gate_remains_blocked(self):
        self.assertEqual(
            self.report["analysis_status"],
            "raw_param_index_and_fixed_point_operation_shape_only",
        )
        self.assertFalse(self.report["behavior_validated"])
        self.assertEqual(self.report["physics_gate"], "blocked")
        self.assertEqual(len(self.report["anchors"]), 15)

    def test_vhor_indices_and_raw_values(self):
        accesses = self.report["modifier_accesses"]
        self.assertEqual(accesses["0x3FE"]["param_index"], 0)
        self.assertEqual(accesses["0x3FE"]["list_data_offset"], "0x20")
        self.assertEqual(accesses["0x3FE"]["canonical_param_at_index"], [1500, 2000, 2500, 3000, 3500])
        self.assertEqual(accesses["0x3FC_vhor"]["param_index"], 1)
        self.assertEqual(accesses["0x3FC_vhor"]["list_data_offset"], "0x24")
        self.assertEqual(accesses["0x3FC_vhor"]["canonical_param_at_index"], [4000, 4500, 5000, 5500, 6000])
        self.assertIn("sqrt_long", accesses["0x3FE"]["combination"])
        self.assertIn("sqrt_long", accesses["0x3FC_vhor"]["combination"])

    def test_vver_uses_third_parameter_for_three_flags(self):
        accesses = self.report["modifier_accesses"]
        for key, expected in (("0x3FC_vver", [900, 800, 700, 600, 500]),
                              ("0x41A_vver", [900, 800, 700, 600, 500]),
                              ("0x3FB_vver", [300, 600, 900, 1200, 1500])):
            self.assertEqual(accesses[key]["param_index"], 2)
            self.assertEqual(accesses[key]["list_data_offset"], "0x28")
            self.assertEqual(accesses[key]["canonical_param_at_index"], expected)
            self.assertEqual(accesses[key]["status"], "list_index_and_operation_shape_only")

    def test_report_does_not_promote_operation_shape_to_equations(self):
        unknown = " ".join(self.report["unknown"])
        self.assertIn("exact VHor/VVer equations", unknown)
        self.assertIn("units", unknown)
        self.assertIn("which config level", unknown)


if __name__ == "__main__":
    unittest.main()
