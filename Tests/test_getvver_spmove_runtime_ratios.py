import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'Tools/analyze_getvver_spmove_runtime_ratios.py'
OUTPUT = ROOT / 'Recovery/Normalized/getvver_spmove_runtime_ratios.json'

class GetVVerSpmoveRuntimeRatiosTests(unittest.TestCase):
    def test_level_matrix_and_open_all_selection_are_persisted(self):
        self.assertTrue(TOOL.is_file(), 'runtime ratio analyzer is missing')
        subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, check=True)
        data=json.loads(OUTPUT.read_text(encoding='utf-8'))
        self.assertEqual(data['modifiers']['0x3FC']['param2_raw_by_level'], [900,800,700,600,500])
        self.assertEqual(data['modifiers']['0x41A']['param2_raw_by_level'], [900,800,700,600,500])
        self.assertEqual(data['open_all_selection']['0x3FC']['selected_child_id'], 102005)
        self.assertEqual(data['open_all_selection']['0x41A']['selected_child_id'], 105005)
        self.assertEqual(data['open_all_selection']['0x3FC']['param2_raw'], 500)
        self.assertEqual(data['open_all_selection']['0x41A']['param2_raw'], 500)
        self.assertEqual(data['activation']['0x3FC']['flag'], 'ShootLongKick')
        self.assertEqual(data['activation']['0x41A']['flag'], 'shootPush')
        self.assertFalse(data['whole_getvver_equivalent'])
        self.assertEqual(data['physics_v0_3_gate'], 'BLOCKED')

if __name__ == '__main__': unittest.main()
