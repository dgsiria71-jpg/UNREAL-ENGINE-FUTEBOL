import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CalSpmoveStaticTraceTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(
            (ROOT / "Recovery" / "Normalized" / "cal_spmove_static_trace.json")
            .read_text(encoding="utf-8")
        )

    def test_producer_span_and_all_flag_writes_are_anchored(self):
        self.assertEqual(self.report["method_span"]["rva"], "0x14C5548")
        self.assertFalse(self.report["behavior_validated"])
        self.assertEqual(len(self.report["confirmed_writes"]), 7)
        flags = {item["flag"] for item in self.report["confirmed_writes"]}
        self.assertEqual(
            flags,
            {
                "shootPush",
                "CalmShoot",
                "SAngleShoot",
                "ShootFirst",
                "Head",
                "ShootLongKick",
                "SwantonBomb",
            },
        )

    def test_producer_keeps_velocity_gate_open(self):
        self.assertEqual(self.report["physics_gate"], "blocked")
        self.assertIn("runtime behavior on representative inputs", self.report["unknown"])
        shoot_first = next(
            item for item in self.report["confirmed_writes"] if item["flag"] == "ShootFirst"
        )
        self.assertEqual(shoot_first["byte_offset"], 3)
        self.assertIn("calShootFirst", shoot_first["source"])


if __name__ == "__main__":
    unittest.main()
