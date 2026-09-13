import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_velocity_dataflow.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
PERSISTED = ROOT / "Recovery" / "Normalized" / "shoot_velocity_dataflow_static_trace.json"


class PersistedShootVelocityDataflowTests(unittest.TestCase):
    def test_persisted_trace_is_exact_analyzer_output(self):
        self.assertTrue(PERSISTED.is_file(), "persisted shoot velocity trace is missing")
        spec = importlib.util.spec_from_file_location("shoot_velocity_dataflow", TOOL)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = module.analyze(SOURCE)
        actual = json.loads(PERSISTED.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
