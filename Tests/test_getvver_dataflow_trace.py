import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_velocity_dataflow.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"


class GetVVerDataflowTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("shoot_velocity_dataflow", TOOL)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module
        cls.report = module.analyze(SOURCE)

    def test_new_path_map_chain_is_bound_without_claiming_full_equation(self):
        new = self.report["GetVVer"]["new_path"]
        self.assertEqual(new["shoot_distance_to_out_energy_interpolate_call"], "0x016E8804")
        self.assertEqual(new["energy_to_y_speed_max_interpolate_call"], "0x016E89F4")
        self.assertEqual(new["shoot_distance_to_point_up_interpolate_call"], "0x016E8BC8")
        self.assertEqual(new["shoot_distance_to_point_down_interpolate_call"], "0x016E8DA4")
        self.assertEqual(new["property_to_energy_tolerance_interpolate_call"], "0x016E8FA8")
        self.assertEqual(new["shoot_point_h_clamp_range"], "0x016E91E4..0x016E921C")
        self.assertEqual(new["shoot_dis_and_time_load"], "0x016E92E4")
        self.assertEqual(new["y_speed_min_load"], "0x016E9CB4")
        self.assertEqual(new["vector_construction_range"], "0x016E9D08..0x016E9D48")

    def test_new_path_vertical_spmove_modifiers_survive_to_return(self):
        mods = self.report["GetVVer"]["new_path"]["post_vector_spmove_modifiers"]
        self.assertEqual(mods["logic_ids"], ["0x3FC", "0x41A"])
        self.assertEqual(mods["logic_id_loads"], ["0x016E9DF0", "0x016E9F30"])
        self.assertTrue(mods["normal_return_value_contribution"])
        self.assertEqual(mods["return_target"], "0x016EA52C")

    def test_old_path_base_interpolation_and_modifier_survive(self):
        old = self.report["GetVVer"]["old_path"]
        self.assertEqual(old["base_interpolate_call"], "0x016EA188")
        self.assertEqual(old["vector_construction_range"], "0x016EA1B0..0x016EA1F0")
        self.assertEqual(old["speed_vVer_load"], "0x016EA318")
        mods = old["post_vector_spmove_modifier"]
        self.assertEqual(mods["logic_id"], "0x3FB")
        self.assertEqual(mods["logic_id_load"], "0x016EA418")
        self.assertTrue(mods["normal_return_value_contribution"])
        self.assertEqual(mods["final_write_range"], "0x016EA4F0..0x016EA528")

    def test_return_abi_is_shared_and_gate_remains_blocked(self):
        vver = self.report["GetVVer"]
        self.assertEqual(vver["return_range"], "0x016EA52C..0x016EA554")
        self.assertEqual(vver["return_abi"], "XVector3 packed as x0(low32=x, high32=y) plus w1=z")
        self.assertIn("full GetVVer arithmetic/interpolation/clamp equations", self.report["unknown"])
        self.assertEqual(self.report["physics_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
