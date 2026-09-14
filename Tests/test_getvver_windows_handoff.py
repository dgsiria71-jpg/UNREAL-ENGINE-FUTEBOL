from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BAT = ROOT / "tools" / "EXTRAIR_GETVVER_UPSTREAM.bat"


class GetVVerWindowsHandoffTests(unittest.TestCase):
    def test_existing_output_is_preserved_before_python_rewrites_target(self):
        text = BAT.read_text(encoding="utf-8").lower()
        self.assertIn("previous", text)
        self.assertIn("move-item", text)
        self.assertIn("getvver_upstream_evidence.txt", text)
        self.assertLess(text.index("move-item"), text.index("extraindo evidencia upstream"))


if __name__ == "__main__":
    unittest.main()
