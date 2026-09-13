import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpmoveInventoryCollectorTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_inventory_collector_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_cache_and_manager_offsets_are_preserved(self):
        self.assertEqual(self.report["analysis_status"], "inventory_cache_control_flow_only")
        self.assertFalse(self.report["behavior_validated"])
        fields = self.report["normalized_boundary"]["manager_fields"]
        self.assertEqual(fields["dictionary"], "+0x10")
        self.assertEqual(fields["open_all"], "+0x28")
        self.assertEqual(fields["inventory_initialized"], "+0x29")
        self.assertEqual(fields["spmove_ids"], "+0x30")
        self.assertEqual(fields["matchrule_skill"], "+0x38")

    def test_both_inventory_paths_are_anchored(self):
        operations = {item["operation"] for item in self.report["confirmed_data_flow"]}
        self.assertIn("all_config_path", operations)
        self.assertIn("player_inventory_path", operations)
        anchors = self.report["anchors"]
        self.assertEqual(anchors["player_inventory_field"]["address"], "0x01B71FA8")
        self.assertEqual(anchors["config_children_list"]["address"], "0x01B71CBC")
        self.assertEqual(self.report["physics_gate"], "blocked")

    def test_unknowns_prevent_velocity_overclaim(self):
        unknown = self.report["unknown"]
        self.assertIn("eligibility, ownership, level, odds, and RNG filters after inventory collection", unknown)
        self.assertIn("representative runtime behavior on real player inventories", unknown)


if __name__ == "__main__":
    unittest.main()

