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
        self.assertEqual(self.report["analysis_status"], "inventory_collection_shape_static_confirmed")
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
        entry_fields = self.report["normalized_boundary"]["entry_fields"]
        self.assertEqual(entry_fields["child_id"], "+0x10")
        self.assertEqual(entry_fields["father_id"], "+0x14")
        self.assertEqual(self.report["anchors"]["self_id_store"]["address"], "0x01B71EA0")
        self.assertEqual(self.report["anchors"]["inventory_self_id_store"]["address"], "0x01B7227C")
        self.assertEqual(self.report["physics_gate"], "blocked")

    def test_generic_helper_names_are_metadata_anchored(self):
        symbols = self.report["helper_symbols"]
        self.assertIn("List<int>$$GetEnumerator", symbols["0x2F19438"])
        self.assertIn("List<SpmoveIDCombine>$$Add", symbols["0x2F26798"])
        self.assertIn("SpmoveModule$$GetConfig", symbols["0x1449858"])
        self.assertEqual(self.report["helper_symbol_status"], "metadata_names_only")

    def test_dump_layout_names_close_combine_semantics(self):
        layout = self.report["layout_evidence"]
        self.assertIn("childId", layout["combine_child_id"])
        self.assertIn("fatherId", layout["combine_father_id"])
        self.assertIn("logicId", layout["config_logic_id"])
        self.assertTrue(self.report["dump_cs_sha256"])

    def test_unknowns_prevent_velocity_overclaim(self):
        unknown = self.report["unknown"]
        self.assertIn("eligibility, ownership, level, odds, and RNG filters after inventory collection", unknown)
        self.assertIn("representative runtime behavior on real player inventories", unknown)


if __name__ == "__main__":
    unittest.main()
