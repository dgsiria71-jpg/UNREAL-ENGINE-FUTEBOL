import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_helper_semantics.py"
SOURCE = (
    ROOT
    / "artifacts"
    / "native-recovery"
    / "shoot-helpers"
    / "20260913-175551-3fafba6a"
    / "01_shoot_helper_disassembly.txt"
)
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_helper_semantics_static_trace.json"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("Tools/analyze_shoot_helper_semantics.py is missing")
    spec = importlib.util.spec_from_file_location("analyze_shoot_helper_semantics", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShootHelperSemanticRecoveryTests(unittest.TestCase):
    def test_canonical_helper_evidence_is_present(self):
        self.assertTrue(SOURCE.is_file())
        normalized = SOURCE.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        self.assertEqual(len(normalized), 184617)

    def test_analyzer_closes_normal_path_remap_semantics_without_overclaiming(self):
        module = load_tool()
        trace = module.analyze(SOURCE)
        self.assertEqual(
            trace["source_sha256"],
            "284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58",
        )
        self.assertEqual(
            trace["binary_sha256"],
            "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
        )
        remap = trace["remap_0x126BF1C"]
        self.assertEqual(remap["normal_return_end"], "0x0126C074")
        self.assertFalse(remap["metadata_exact_boundary"])
        self.assertTrue(remap["normal_path_formula_recovered"])
        self.assertEqual(remap["equal_input_bounds"], "return_out_min")
        self.assertEqual(remap["ratio_fraction_bits"], 10)
        self.assertEqual(remap["ratio_zero_raw"], 0)
        self.assertEqual(remap["lerp_helper"], "0x0126C3FC")
        self.assertIn("q + trunc(2*r/d)", remap["ratio_formula"])

    def test_lerp_helper_matches_recovered_fixed_point_shape(self):
        module = load_tool()
        trace = module.analyze(SOURCE)
        lerp = trace["lerp_0x126C3FC"]
        self.assertEqual(lerp["normal_return_end"], "0x0126C534")
        self.assertEqual(lerp["t_clamp_raw"], [0, 1024])
        self.assertEqual(lerp["multiply_bias"], 512)
        self.assertEqual(lerp["fraction_bits"], 10)
        self.assertEqual(
            lerp["formula"],
            "out_min + fixed_mul(out_max - out_min, clamp(t, 0, 1024))",
        )

    def test_old_vver_helper_identity_and_value_chain_are_exactly_bound(self):
        module = load_tool()
        trace = module.analyze(SOURCE)
        helper = trace["old_vver_0x1968E24"]
        self.assertTrue(helper["exact_function_boundary"])
        self.assertEqual(helper["metadata_name"], "PlayerProperty$$GetShootSpeedVRate")
        self.assertEqual(helper["end"], "0x0196916C")
        self.assertEqual(helper["first_value_callee"], "PlayerProperty$$GetShootVerRate")
        self.assertEqual(helper["random_callee"], "XRandom$$Range")
        self.assertEqual(helper["config_singleton_callee"], "XBaseLocalSetting<AIParameterConfig>$$get_Singleton")
        self.assertEqual(helper["caller_speed_vver_load"], "0x016EA318:+0x80->w3")
        self.assertEqual(helper["caller_callsite"], "0x016EA330")
        self.assertFalse(helper["full_equation_recovered"])

    def test_spmove_ratio_helper_is_exact_forwarder(self):
        module = load_tool()
        trace = module.analyze(SOURCE)
        helper = trace["spmove_ratio_0x196807C"]
        self.assertTrue(helper["exact_function_boundary"])
        self.assertEqual(helper["metadata_name"], "PlayerProperty$$GetSpmoveDataRatio")
        self.assertEqual(helper["manager_offset"], "+0x28")
        self.assertEqual(helper["no_ratio_mask"], 1)
        self.assertEqual(helper["tail_target"], "0x01B72814")
        self.assertEqual(helper["tail_semantics"], "SpmoveManager.GetSpmoveDataNoRatio")

    def test_persisted_trace_matches_fresh_analysis(self):
        module = load_tool()
        self.assertTrue(OUTPUT.is_file(), "persisted helper semantic trace is missing")
        self.assertEqual(module.load_json(OUTPUT), module.analyze(SOURCE))


if __name__ == "__main__":
    unittest.main()
