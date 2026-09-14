import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "build_getvver_modifier_vectors.py"
OUTPUT = ROOT / "Recovery" / "Normalized" / "getvver_spmove_modifier_vectors.json"
HEADER = ROOT / "Reference" / "FootballPhysics" / "GetVVerSpmoveRuntime.h"


class GetVVerModifierVectorTests(unittest.TestCase):
    def test_generated_vectors_are_current_and_bounded(self):
        self.assertTrue(TOOL.is_file(), "modifier-vector generator is missing")
        self.assertTrue(HEADER.is_file(), "GetVVer selector adapter is missing")
        subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, check=True)
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(payload["cases"]["none"]["output_raw"], [-3000, 1537, 777])
        self.assertEqual(payload["cases"]["0x3FC"]["output_raw"], [-2051, 1051, 531])
        self.assertEqual(payload["cases"]["0x41A"]["output_raw"], [-2344, 1201, 607])
        self.assertEqual(payload["cases"]["both"]["output_raw"], [-1602, 821, 415])
        self.assertEqual(payload["combined_ratio_shortcut"]["output_x_raw"], -1603)
        self.assertFalse(payload["native_differential_validated"])
        self.assertEqual(payload["physics_v0_3_gate"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
