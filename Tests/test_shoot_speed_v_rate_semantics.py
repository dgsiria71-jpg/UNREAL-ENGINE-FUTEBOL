import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_speed_v_rate.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "shoot-helpers" / "20260913-175551-3fafba6a" / "01_shoot_helper_disassembly.txt"
METADATA = ROOT / "artifacts" / "native-recovery" / "shoot-helpers" / "20260913-175551-3fafba6a" / "03_shoot_speed_v_rate_metadata.txt"
SUPPORT = ROOT / "artifacts" / "native-recovery" / "shoot-helpers" / "20260913-175551-3fafba6a" / "02_shoot_speed_v_rate_support_disassembly.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_speed_v_rate_static_trace.json"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("Tools/analyze_shoot_speed_v_rate.py is missing")
    spec = importlib.util.spec_from_file_location("analyze_shoot_speed_v_rate", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShootSpeedVRateRecoveryTests(unittest.TestCase):
    def test_metadata_and_analyzer_exist(self):
        self.assertTrue(METADATA.is_file(), "source-bound metadata excerpt is missing")
        self.assertTrue(TOOL.is_file(), "shoot-speed V-rate analyzer is missing")

    def test_equation_and_caller_visible_contract_are_closed(self):
        trace = load_tool().analyze(SOURCE, SUPPORT, METADATA)
        helper = trace["GetShootSpeedVRate"]
        self.assertEqual(helper["signature"], "GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) -> XNumber")
        self.assertEqual(helper["force_ratio"], "F / 100 using XNumber.op_Division(XNumber,int)")
        self.assertEqual(helper["base_formula"], "one + fixed_mul(fixed_mul(fixed_mul(GetShootVerRate(goal_child), c), force_ratio), force_ratio)")
        self.assertEqual(helper["ai_config_field"], "AIParameterConfig.disArea")
        self.assertEqual(helper["ai_config_field_offset"], "+0x80")
        self.assertEqual(helper["positive_c_bound"], "min(one, base + disArea_raw)")
        self.assertEqual(helper["negative_c_bound"], "max(one, base - disArea_raw)")
        self.assertEqual(helper["return_formula"], "XRandom.Range(sign_selected_bound, c)")
        self.assertTrue(helper["normal_return_equation_recovered"])
        self.assertFalse(helper["random_sample_resolved_without_rng_state"])

    def test_xrandom_range_caller_visible_arithmetic_is_closed(self):
        trace = load_tool().analyze(SOURCE, SUPPORT, METADATA)
        random = trace["XRandom.Range"]
        self.assertEqual(random["sample_domain"], "integer 0..1000 inclusive from Random.Range(1001)")
        self.assertEqual(random["formula"], "from + divide_by_int((to - from) * sample, 1000)")
        self.assertEqual(random["endpoints"], {"sample_0": "from", "sample_1000": "to"})

    def test_persisted_trace_matches_fresh_analysis(self):
        module = load_tool()
        self.assertTrue(OUTPUT.is_file(), "persisted shoot-speed V-rate trace is missing")
        self.assertEqual(module.load_json(OUTPUT), module.analyze(SOURCE, SUPPORT, METADATA))


if __name__ == "__main__":
    unittest.main()
