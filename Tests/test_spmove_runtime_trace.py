import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpmoveRuntimeStaticTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_runtime_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_report_is_static_and_gate_stays_blocked(self):
        self.assertEqual(
            self.report["analysis_status"],
            "param_runtime_population_and_property_call_sites_only",
        )
        self.assertFalse(self.report["behavior_validated"])
        self.assertEqual(self.report["physics_gate"], "blocked")

    def test_runtime_param_population_is_anchored(self):
        anchors = self.report["anchors"]
        self.assertEqual(anchors["on_game_start_param_xnumber_store"]["address"], "0x01449638")
        self.assertEqual(anchors["on_game_start_param_add"]["address"], "0x014496A4")
        population = self.report["param_runtime_population"]
        self.assertEqual(population["list_creation"]["field"], "SpmoveConfigConfigItem.param_Xnumber")
        self.assertEqual(population["list_creation"]["offset"], "0x10")
        self.assertEqual(population["serialized_param_copy"]["source_offset"], "0x38")
        observed = population["canonical_observation"]
        self.assertEqual(observed["config_record_count"], 292)
        self.assertGreater(observed["records_with_empty_param_raw"], 0)
        self.assertLess(observed["records_with_empty_param_raw"], observed["config_record_count"])

    def test_odds_and_player_forwarding_are_separate_boundaries(self):
        odds = self.report["odds_path"]
        self.assertEqual(odds["scale"], "odds << 10 (XNumber raw scaling; 1024 factor)")
        self.assertEqual(odds["helper_target"], "0x192A1E0")
        forwarding = self.report["player_forwarding"]
        self.assertIn("tail-call XSpmoveManager.GetSpmoveData", forwarding["get_spmove_data"])
        self.assertIn("GetSpmoveDataNoRatio", forwarding["get_spmove_data_ratio"])

    def test_property_ids_align_with_canonical_logic_ids_without_claiming_selection(self):
        alignment = self.report["property_logic_id_alignment"]
        for key in ("0x417", "0x418", "0x3FE", "0x3FC", "0x41A", "0x3FB", "0x40B"):
            self.assertEqual(alignment[key]["property_id_decimal"], int(key, 16))
            self.assertEqual(alignment[key]["canonical_logic_id"], int(key, 16))
            self.assertEqual(alignment[key]["record_count"], 5)
            self.assertEqual(alignment[key]["levels"], [1, 2, 3, 4, 5])
            self.assertEqual(alignment[key]["status"], "numeric_property_to_logic_id_alignment_only")
        self.assertIn("selected config", " ".join(self.report["unknown"]))

    def test_all_shoot_property_call_sites_are_recorded(self):
        sites = self.report["property_call_sites"]
        self.assertEqual(len(sites), 7)
        self.assertEqual(
            [site["property_id"] for site in sites],
            [0x3FE, 0x3FC, 0x3FE, 0x3FC, 0x3FC, 0x41A, 0x3FB],
        )
        self.assertTrue(all(site["ratio_argument"] == "w2=1" for site in sites))
        self.assertTrue(all(site["fourth_argument"] == "x3=0" for site in sites))
        self.assertIn("property units", " ".join(self.report["unknown"]))


if __name__ == "__main__":
    unittest.main()
