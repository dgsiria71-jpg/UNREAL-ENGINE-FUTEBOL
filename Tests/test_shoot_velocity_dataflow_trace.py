import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "analyze_shoot_velocity_dataflow.py"
SOURCE = ROOT / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "01_disassembly_shoot.txt"


class ShootVelocityDataflowTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TOOL.is_file():
            cls.module = None
            return
        spec = importlib.util.spec_from_file_location("shoot_velocity_dataflow", TOOL)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def analyze(self):
        self.assertTrue(TOOL.is_file(), "canonical shoot velocity dataflow analyzer is missing")
        self.assertTrue(SOURCE.is_file(), "canonical committed shoot disassembly is missing")
        return self.module.analyze(SOURCE)

    def test_getvhor_base_path_and_overwrite_are_bound(self):
        report = self.analyze()
        self.assertEqual(
            report["source_sha256"],
            "ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58",
        )
        vhor = report["GetVHor"]
        self.assertEqual(vhor["new_path"]["energy_to_vhor_interpolate_call"], "0x016E6DE0")
        self.assertEqual(vhor["new_path"]["strength_to_rate_interpolate_call"], "0x016E6FEC")
        self.assertEqual(vhor["new_path"]["clamp_bounds_load"], "0x016E72C0")
        self.assertEqual(vhor["old_path"]["energy_to_vhor_interpolate_call"], "0x016E73B0")
        self.assertEqual(vhor["old_path"]["clamp_bounds_load"], "0x016E794C")
        self.assertEqual(vhor["base_vector"]["return_slots_write"], ["0x016E79D4", "0x016E79D8"])
        self.assertEqual(vhor["base_vector"]["layout"], "XVector3(x=dir0*speed,y=0,z=dir1*speed)")

    def test_pre_base_spmove_vector_results_are_overwritten_on_normal_return_path(self):
        report = self.analyze()
        dead = report["GetVHor"]["pre_base_spmove_blocks"]
        self.assertEqual(dead["logic_ids"], ["0x3FE", "0x3FC"])
        self.assertFalse(dead["normal_return_value_contribution"])
        self.assertEqual(dead["overwritten_by"], ["0x016E79D4", "0x016E79D8"])
        self.assertTrue(dead["calls_may_still_throw_or_have_side_effects"])

    def test_getkickvelocity_final_join_is_componentwise_addition(self):
        report = self.analyze()
        kick = report["GetKickVelocity"]
        self.assertEqual(kick["GetVHor_call"], "0x016EBBA8")
        self.assertEqual(kick["GetVVer_call"], "0x016EBEAC")
        self.assertEqual(kick["final_join_range"], "0x016EBED8..0x016EBF04")
        self.assertEqual(kick["final_join"], "adjusted_GetVHor + GetVVer componentwise")
        self.assertEqual(report["physics_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
