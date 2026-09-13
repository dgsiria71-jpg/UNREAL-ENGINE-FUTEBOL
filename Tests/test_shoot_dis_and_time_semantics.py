import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_dis_and_time.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_dis_and_time_static_trace.json"
HEADER = ROOT / "Reference" / "FootballPhysics" / "ShootDisAndTime.h"
METADATA = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "02_shoot_dis_and_time_metadata.txt"
CONFIG = ROOT / "Recovery" / "Normalized" / "shoot_dis_and_time_config_5800.json"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("Tools/analyze_shoot_dis_and_time.py is missing")
    spec = importlib.util.spec_from_file_location("analyze_shoot_dis_and_time", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShootDisAndTimeRecoveryTests(unittest.TestCase):
    def test_analyzer_and_reference_exist(self):
        self.assertTrue(TOOL.is_file(), "shootDisAndTime analyzer is missing")
        self.assertTrue(HEADER.is_file(), "shootDisAndTime C++ reference is missing")
        self.assertTrue(METADATA.is_file(), "shootDisAndTime metadata excerpt is missing")

    def test_nested_lookup_and_time_conversion_are_closed(self):
        trace = load_tool().analyze(SOURCE)
        lookup = trace["shootDisAndTime"]
        self.assertEqual(lookup["field_type"], "List<List<int>>")
        self.assertEqual(lookup["outer_axis"], "XVector3.magnitude(vHor), integer floor/ceiling neighbors")
        self.assertEqual(lookup["inner_axis"], "horizontal shoot distance, integer floor/ceiling neighbors")
        self.assertEqual(lookup["table_value_unit"], "integer milliseconds")
        self.assertEqual(lookup["milliseconds_to_seconds"], "XNumber(table_ms) / XNumber.thousand")
        self.assertEqual(lookup["zero_pair_policy"], "use the nonzero row result; zero only when both row results are zero")
        self.assertTrue(lookup["normal_path_equation_recovered"])

    def test_canonical_config_5800_table_is_normalized(self):
        config = load_tool().load_json(CONFIG)
        self.assertEqual(config["source"]["decoded_sha256"], "f437f83465a541bc85f07e1cab655afd59a2fb927233302a40a1d09b6355d0ad")
        self.assertEqual(config["source"]["records"], 28)
        self.assertEqual(config["source"]["bytes_consumed"], 133872)
        self.assertEqual(config["config"]["shoot_dis_and_time_ms"][20][25], 1327)
        self.assertEqual(config["confirmed_anchor"]["flight_time_raw"], 1359)

    def test_ballistic_solver_and_clamp_are_closed(self):
        trace = load_tool().analyze(SOURCE)
        solver = trace["vertical_solver"]
        self.assertEqual(solver["formula"], "(vertical_delta - fixed_mul(fixed_mul(flight_time, vertical_accel_raw), flight_time) / 2) / flight_time")
        self.assertEqual(solver["zero_time_result"], "XNumber.zero")
        self.assertEqual(solver["clamp"], "max(ySpeedMin, min(ySpeedMax, solved_y_speed)) using native comparison order")
        self.assertEqual(trace["physics_v0_3_gate"], "BLOCKED")

    def test_persisted_trace_matches_fresh_analysis(self):
        module = load_tool()
        self.assertTrue(OUTPUT.is_file(), "persisted shootDisAndTime trace is missing")
        self.assertEqual(module.load_json(OUTPUT), module.analyze(SOURCE))


if __name__ == "__main__":
    unittest.main()
