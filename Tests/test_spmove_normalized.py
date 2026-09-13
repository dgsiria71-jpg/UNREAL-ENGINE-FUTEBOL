import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Recovery" / "Normalized" / "spmove_normalized.json"


@unittest.skipUnless(
    SOURCE.is_file(),
    "spmove_normalized.json is a local regeneration artifact; preserved source archive required",
)
class SpmoveNormalizedTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_canonical_tables_are_decoded_and_schema_bounded(self):
        canonical = self.report["canonical_source"]
        self.assertEqual(canonical["relation"], "canonical_baseline")
        self.assertEqual(canonical["action"]["record_count"], 48)
        self.assertEqual(canonical["config"]["record_count"], 292)
        self.assertEqual(canonical["action"]["decoded_bytes"], 4332)
        self.assertEqual(canonical["config"]["decoded_bytes"], 11880)
        self.assertEqual(canonical["action"]["records"][0]["id"], 1)
        self.assertEqual(canonical["action"]["records"][0]["fancy_id"], 102)
        self.assertEqual(canonical["config"]["records"][0]["id"], 100201)
        self.assertEqual(canonical["config"]["records"][0]["logic_id"], 999)

    def test_candidate_is_separate_and_gate_remains_open(self):
        candidate = self.report["separate_candidate_source"]
        self.assertEqual(candidate["relation"], "separate_hash_different_mobile_build")
        self.assertEqual(candidate["action"]["record_count"], 48)
        self.assertEqual(candidate["config"]["record_count"], 312)
        self.assertNotIn("records", candidate["config"])
        self.assertEqual(
            self.report["semantic_status"],
            "record_schema_confirmed_velocity_semantics_unresolved",
        )
        self.assertIn("spmoveInUseData VHor modifier", self.report["unknown"])
        self.assertIn("GetKickVelocity final physical composition", self.report["unknown"])


if __name__ == "__main__":
    unittest.main()
