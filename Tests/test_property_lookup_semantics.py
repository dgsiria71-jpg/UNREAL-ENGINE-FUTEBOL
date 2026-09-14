import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_property_lookup_semantics.py"
OUTPUT = ROOT / "Recovery" / "Normalized" / "property_lookup_semantics_static_trace.json"

class PropertyLookupSemanticsTests(unittest.TestCase):
    def test_exact_native_property_lookup_contract_is_persisted(self):
        self.assertTrue(TOOL.is_file(), "property lookup analyzer is missing")
        subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, check=True)
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(payload["source_build"], "football-dream-be-a-pro-1-221-5")
        self.assertEqual(payload["player_property_lookup"]["metadata_name"], "PlayerProperty$$GetPropertyValue")
        self.assertEqual(payload["property_manager_lookup"]["metadata_name"], "XProperty.XPropertyManager$$GetPropertyValue")
        self.assertEqual(payload["player_property_lookup"]["fallback"], "manager_property.GetPropertyValue(property_type)")
        self.assertEqual(payload["property_manager_lookup"]["value_field_offset"], "0x14")
        self.assertFalse(payload["whole_getvver_equivalent"])
        self.assertEqual(payload["physics_v0_3_gate"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
