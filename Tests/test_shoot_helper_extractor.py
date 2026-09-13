import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "disassemble_shoot_helpers.py"
WRAPPER = ROOT / "tools" / "EXTRAIR_HELPERS_SHOOT.bat"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("shoot helper extractor is missing")
    spec = importlib.util.spec_from_file_location("disassemble_shoot_helpers", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ShootHelperExtractorTests(unittest.TestCase):
    def test_extractor_and_one_click_wrapper_exist(self):
        self.assertTrue(TOOL.is_file(), "Tools/disassemble_shoot_helpers.py is missing")
        self.assertTrue(WRAPPER.is_file(), "tools/EXTRAIR_HELPERS_SHOOT.bat is missing")

    def test_wrapper_supports_py_launcher_and_python_fallback(self):
        wrapper = WRAPPER.read_text(encoding="utf-8").lower()
        self.assertIn("where py", wrapper)
        self.assertIn("where python", wrapper)
        self.assertIn("publicar_inbox_no_github.ps1", wrapper)

    def test_wrapper_captures_runtime_errorlevel_inside_parenthesized_py_branch(self):
        wrapper = WRAPPER.read_text(encoding="utf-8").lower()
        self.assertIn("enabledelayedexpansion", wrapper)
        self.assertIn("!errorlevel!", wrapper)

    def test_default_targets_cover_current_unresolved_value_helpers(self):
        module = load_tool()
        targets = {target.name: target for target in module.DEFAULT_TARGETS}
        self.assertEqual(targets["interpolate_remap_126BF1C"].address, 0x126BF1C)
        self.assertEqual(targets["old_vver_helper_1968E24"].address, 0x1968E24)
        self.assertEqual(targets["player_spmove_data_ratio_196807C"].address, 0x196807C)
        self.assertGreaterEqual(targets["interpolate_remap_126BF1C"].fallback_bytes, 0x400)

    def test_script_json_method_collection_accepts_nested_il2cppdumper_shape(self):
        module = load_tool()
        payload = {
            "ScriptMethod": [
                {"Address": 0x126BF1C, "Name": "InterpolationHelper"},
                {"Address": 0x126C080, "Name": "NextMethod"},
            ],
            "nested": {"items": [{"Address": "0x1968E24", "Name": "OldVVerHelper"}]},
        }
        methods = module.collect_script_methods(payload)
        self.assertIn((0x126BF1C, "InterpolationHelper"), methods)
        self.assertIn((0x126C080, "NextMethod"), methods)
        self.assertIn((0x1968E24, "OldVVerHelper"), methods)

    def test_resolve_range_uses_next_known_method_when_available(self):
        module = load_tool()
        target = module.Target("probe", 0x126BF1C, 0x800)
        methods = [
            (0x126BEF0, "Previous"),
            (0x126BF1C, "Target"),
            (0x126C080, "Next"),
            (0x126C400, "Later"),
        ]
        resolved = module.resolve_target_range(target, methods)
        self.assertEqual(resolved.start, 0x126BF1C)
        self.assertEqual(resolved.end, 0x126C080)
        self.assertEqual(resolved.boundary_source, "script.json:next-method")

    def test_resolve_range_falls_back_to_bounded_window_without_metadata(self):
        module = load_tool()
        target = module.Target("probe", 0x1968E24, 0x600)
        resolved = module.resolve_target_range(target, [])
        self.assertEqual(resolved.start, 0x1968E24)
        self.assertEqual(resolved.end, 0x1969424)
        self.assertEqual(resolved.boundary_source, "bounded-fallback-window")

    def test_first_level_callee_selection_is_deduplicated_and_excludes_primary_targets(self):
        module = load_tool()
        self.assertGreaterEqual(module.ADJACENT_WINDOW_BYTES, 0x100)
        selected = module.select_first_level_callees(
            {
                "one": [0x1000, 0x2000, 0x3000],
                "two": [0x2000, 0x4000],
            },
            primary_starts={0x1000, 0x4000},
        )
        self.assertEqual(selected, [0x2000, 0x3000])

    def test_summary_is_machine_readable_and_does_not_claim_exact_body_for_fallback(self):
        module = load_tool()
        target = module.Target("probe", 0x1968E24, 0x600)
        resolved = module.resolve_target_range(target, [])
        summary = module.build_summary(
            binary_sha256="a" * 64,
            metadata_path=None,
            resolved_ranges=[resolved],
            direct_calls={"probe": [0x1234, 0x5678]},
        )
        encoded = json.dumps(summary)
        self.assertIn("bounded-fallback-window", encoded)
        self.assertFalse(summary["targets"][0]["exact_function_boundary"])
        self.assertEqual(summary["targets"][0]["direct_call_targets"], ["0x00001234", "0x00005678"])


if __name__ == "__main__":
    unittest.main()
