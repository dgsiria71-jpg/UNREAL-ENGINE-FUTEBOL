import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpmoveDeserializeStaticTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "spmove_deserialize_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_config_serialized_fields_match_schema(self):
        fields = {item["name"]: item for item in self.report["serialized_fields"]["spmoveconfig"]}
        self.assertEqual(set(fields), {
            "id", "enable", "logicId", "childSpmoveIds", "level", "odds",
            "param", "buffId", "IsBuffId", "order",
        })
        self.assertFalse(self.report["behavior_validated"])

    def test_param_xnumber_is_explicitly_omitted_from_buffer_reader(self):
        omitted = self.report["omitted_runtime_fields"]
        self.assertEqual(len(omitted), 1)
        self.assertEqual(omitted[0]["name"], "param_Xnumber")
        self.assertEqual(omitted[0]["offset"], "0x10")
        self.assertIn("no store at +0x10", omitted[0]["deserializer_evidence"])
        self.assertEqual(self.report["physics_gate"], "blocked")

    def test_action_schema_has_speed_fix_rate(self):
        fields = {item["name"]: item for item in self.report["serialized_fields"]["spmoveactiondata"]}
        self.assertEqual(fields["speed_fix_rate"]["offset"], "0x38")
        self.assertIn("whether a constructor or manager post-processing populates param_Xnumber", self.report["unknown"])


if __name__ == "__main__":
    unittest.main()
