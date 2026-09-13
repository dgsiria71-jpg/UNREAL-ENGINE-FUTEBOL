import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpmoveCollectedInventoryTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery/Normalized/spmove_collected_open_all.json")
            .read_text(encoding="utf-8")
        )
        self.source = json.loads(
            (ROOT / "Recovery/Normalized/spmove_normalized.json")
            .read_text(encoding="utf-8")
        )

    def test_all_canonical_children_resolve_into_complete_inventory(self):
        self.assertEqual(self.report["status"], "open_all_collection_shape_complete")
        self.assertEqual(
            self.report["counts"],
            {
                "serialized_config_records": 292,
                "enabled_config_records": 290,
                "disabled_config_records": 2,
                "child_references": 56,
                "logic_buckets": 68,
                "inventory_entries": 346,
                "missing_child_configs": 0,
            },
        )
        self.assertEqual(self.report["physics_v0_3_gate"], "blocked")

    def test_every_self_and_child_relation_matches_normalized_configs(self):
        records = [
            item for item in self.source["canonical_source"]["config"]["records"]
            if item["enable"] != 0
        ]
        by_id = {item["id"]: item for item in records}
        buckets = {item["logic_id"]: item["entries"] for item in self.report["buckets"]}
        for config in records:
            self.assertIn(
                {"child_id": config["id"], "father_id": 0},
                buckets[config["logic_id"]],
            )
            for child_id in config["child_spmove_ids"]:
                child = by_id[child_id]
                self.assertIn(
                    {"child_id": child_id, "father_id": config["id"]},
                    buckets[child["logic_id"]],
                )

    def test_velocity_logic_buckets_are_available_without_closing_velocity(self):
        buckets = {item["logic_id"]: item["entries"] for item in self.report["buckets"]}
        self.assertEqual([item["child_id"] for item in buckets[0x3FE]],
                         [102201, 102202, 102203, 102204, 102205])
        self.assertIn({"child_id": 102004, "father_id": 108001}, buckets[0x3FC])
        self.assertIn({"child_id": 105004, "father_id": 108001}, buckets[0x41A])
        self.assertIn("complete GetVHor/GetVVer/GetKickVelocity composition",
                      self.report["unknown"])


if __name__ == "__main__":
    unittest.main()
