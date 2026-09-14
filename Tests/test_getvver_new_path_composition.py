import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_getvver_new_path_composition.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"
UPSTREAM = ROOT / "artifacts" / "native-recovery" / "getvver-upstream" / "20260913-204613-86a0f84a" / "01_getvver_upstream_evidence.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "getvver_new_path_composition_static_trace.json"
HEADER = ROOT / "Reference" / "FootballPhysics" / "GetVVerNewPath.h"
CONFIG_HEADER = ROOT / "Reference" / "FootballPhysics" / "GetVVerNewPathConfig.h"


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
    def test_analyzer_and_references_exist(self):
        self.assertTrue(TOOL.is_file(), "GetVVer new-path analyzer is missing")
        self.assertTrue(HEADER.is_file(), "GetVVer new-path C++ reference is missing")
        self.assertTrue(CONFIG_HEADER.is_file(), "GetVVer raw-map producer reference is missing")
        self.assertTrue(UPSTREAM.is_file(), "published GetVVer upstream evidence is missing")

    def test_energy_protection_target_height_and_native_bias_are_instruction_bound(self):
        trace = load_tool().analyze(SOURCE, UPSTREAM)
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
        self.assertEqual(target["downward_bias_helper"], "XNumber$$create")
        self.assertEqual(target["downward_bias_call"], "XNumber.create(0,100)")
        self.assertEqual(target["downward_bias_raw"], 102)
        self.assertEqual(
            target["height_adjustment_nonpositive"],
            "-(fixed_mul(abs(selected_energy-out_energy), point_down_rate) + XNumber.create(0,100))",
        )
        self.assertEqual(target["base_target_height_helper"], "GoalDoor$$get_Height")
        self.assertEqual(
            target["vertical_delta"],
            "native_clamp(GoalDoor.get_Height + height_adjustment, point_h_min, point_h_max) - reference_y",
        )

    def test_raw_new_method_map_producers_are_bound_to_exact_metadata_fields(self):
        trace = load_tool().analyze(SOURCE, UPSTREAM)
        producers = trace["raw_map_producers"]
        self.assertEqual(
            producers["out_energy"],
            {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "outEnergyMaxMap +0x100", "call": "0x016E8804"},
        )
        self.assertEqual(
            producers["y_speed_max"],
            {"input": "current_energy", "axis": "energyMapNew +0xB8", "values": "ySpeedMax +0xA0", "call": "0x016E89F4"},
        )
        self.assertEqual(
            producers["point_up_rate"],
            {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "shootPointHUpMap +0xF8", "call": "0x016E8BC8"},
        )
        self.assertEqual(
            producers["point_down_rate"],
            {"input": "horizontal_distance", "axis": "shootDisMap +0xE8", "values": "shootPointHDownMap +0xF0", "call": "0x016E8DA4"},
        )
        self.assertEqual(
            producers["energy_tolerance"],
            {"input": "shoot_property_input_from_0x1968398", "axis": "shootPropertyMapNew +0xD8", "values": "energyToleranceMap +0xE0", "call": "0x016E8FA8"},
        )
        self.assertEqual(producers["unresolved_runtime_input"], "0x1968398 output")

    def test_base_vector_and_surviving_modifiers_are_bound(self):
        trace = load_tool().analyze(SOURCE, UPSTREAM)
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
        self.assertEqual(module.load_json(OUTPUT), module.analyze(SOURCE, UPSTREAM))


if __name__ == "__main__":
    unittest.main()
