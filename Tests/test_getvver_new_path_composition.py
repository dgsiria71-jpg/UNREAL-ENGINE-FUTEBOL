import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_getvver_new_path_composition.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "getvver_new_path_composition_static_trace.json"
HEADER = ROOT / "Reference" / "FootballPhysics" / "GetVVerNewPath.h"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("GetVVer new-path analyzer is missing")
    spec = importlib.util.spec_from_file_location("analyze_getvver_new_path_composition", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GetVVerNewPathCompositionTests(unittest.TestCase):
    def test_analyzer_and_reference_exist(self):
        self.assertTrue(TOOL.is_file(), "GetVVer new-path analyzer is missing")
        self.assertTrue(HEADER.is_file(), "GetVVer new-path C++ reference is missing")

    def test_energy_protection_and_target_height_are_instruction_bound(self):
        trace = load_tool().analyze(SOURCE)
        target = trace["target_height_path"]
        self.assertEqual(target["energy_need_protect_offset"], "+0x94")
        self.assertEqual(
            target["selected_energy_equation"],
            "if out_energy-energy_need_protect >= current_energy or current_energy >= out_energy+energy_tolerance: current_energy; else max(current_energy-energy_tolerance, out_energy-energy_need_protect)",
        )
        self.assertEqual(
            target["height_adjustment_positive"],
            "fixed_mul(selected_energy-out_energy, point_up_rate)",
        )
        self.assertEqual(
            target["height_adjustment_nonpositive"],
            "-(fixed_mul(abs(selected_energy-out_energy), point_down_rate) + downward_random_offset_raw)",
        )
        self.assertEqual(
            target["vertical_delta"],
            "native_clamp(base_target_height + height_adjustment, point_h_min, point_h_max) - reference_y",
        )

    def test_base_vector_and_surviving_modifiers_are_bound(self):
        trace = load_tool().analyze(SOURCE)
        vector = trace["vector_composition"]
        self.assertEqual(vector["base_vector_range"], "0x016E9D08..0x016E9D48")
        self.assertEqual(vector["base_vector"], "vertical_direction * solved_y_speed using native fixed_mul")
        self.assertEqual(vector["modifier_order"], ["0x3FC", "0x41A"])
        self.assertEqual(vector["modifier_parameter_index"], 2)
        self.assertEqual(vector["modifier_semantics"], "scale all three vector components by parameter[2] using native fixed_mul")
        self.assertTrue(vector["normal_return_value_contribution"])

    def test_persisted_trace_matches_fresh_analysis(self):
        module = load_tool()
        self.assertTrue(OUTPUT.is_file(), "persisted GetVVer new-path trace is missing")
        self.assertEqual(module.load_json(OUTPUT), module.analyze(SOURCE))


if __name__ == "__main__":
    unittest.main()
