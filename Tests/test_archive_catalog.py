import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FootballArchiveCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(
            (ROOT / "Recovery" / "Normalized" / "archive_catalog.json")
            .read_text(encoding="utf-8")
        )

    def test_catalog_contains_canonical_and_supporting_archives(self):
        records = {item["filename"]: item for item in self.catalog["records"]}
        self.assertIn("FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip", records)
        self.assertIn("FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip", records)
        self.assertIn("FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip", records)
        self.assertGreaterEqual(len(records), 10)
        self.assertEqual(records["FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip"]["classification"], "canonical_physics_baseline")

    def test_candidate_and_historical_lines_are_isolated(self):
        records = {item["filename"]: item for item in self.catalog["records"]}
        self.assertEqual(records["football-dream-be-a-pro-1-226-19.zip"]["classification"], "separate_mobile_candidate")
        self.assertEqual(records["FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip"]["classification"], "historical_master_archive")
        finding = self.catalog["workspace_finding"]
        self.assertEqual(finding["advanced_92_92_workspace"], "not present in catalog entries")
        self.assertEqual(finding["native_disassembly_workspace"], "not present in catalog entries")


if __name__ == "__main__":
    unittest.main()
