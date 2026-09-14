import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "Tools" / "extract_getvver_upstream_evidence.py"
BAT = ROOT / "tools" / "EXTRAIR_GETVVER_UPSTREAM.bat"


def load_tool():
    if not TOOL.is_file():
        raise AssertionError("GetVVer upstream extractor is missing")
    spec = importlib.util.spec_from_file_location("extract_getvver_upstream_evidence", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GetVVerUpstreamExtractorTests(unittest.TestCase):
    def test_tool_and_windows_handoff_exist(self):
        self.assertTrue(TOOL.is_file(), "GetVVer upstream extractor is missing")
        self.assertTrue(BAT.is_file(), "GetVVer upstream .bat handoff is missing")

    def test_extracts_ordered_shoot_speed_fields_without_guessing_names(self):
        module = load_tool()
        dump = """
public class Other // TypeDefIndex: 1
{
    public int no; // 0x10
}
public class ShootSpeedConfigItem // TypeDefIndex: 7953
{
    public List<XNumber> energyMapNew; // 0xB8
    public List<XNumber> vHorMapNew; // 0xC0
    public List<XNumber> shootStrongMapNew; // 0xC8
    public List<XNumber> vHorRateNew; // 0xD0
    public List<XNumber> shootPropertyMapNew; // 0xD8
    public List<XNumber> energyToleranceMap; // 0xE0
    public List<XNumber> shootDisMap; // 0xE8
    public List<XNumber> shootPointHDownMap; // 0xF0
    public List<XNumber> shootPointHUpMap; // 0xF8
    public List<XNumber> outEnergyMaxMap; // 0x100
    public List<List<int>> shootDisAndTime; // 0x108

    public void IgnoreMethod() { }
}
public class Next // TypeDefIndex: 2
{
    public int no; // 0x10
}
"""
        fields = module.extract_shoot_speed_fields(dump)
        self.assertEqual([item["offset"] for item in fields], [
            "0xB8", "0xC0", "0xC8", "0xD0", "0xD8", "0xE0",
            "0xE8", "0xF0", "0xF8", "0x100", "0x108",
        ])
        self.assertEqual(fields[0]["name"], "energyMapNew")
        self.assertEqual(fields[-1]["name"], "shootDisAndTime")

    def test_extracts_ai_and_player_property_metadata_fields_by_exact_class_name(self):
        module = load_tool()
        dump = """
public class AIParameterConfig // TypeDefIndex: 10
{
    public XNumber positionGate; // 0x24
    public int ignored; // 0x30
    public XNumber farGate; // 0x148
    public XNumber nearGate; // 0x14C
}
public class PlayerProperty // TypeDefIndex: 11
{
    public int before; // 0x90
    public CollectionBonusState bonusState; // 0x98
    public int after; // 0xA0
}
public class CollectionBonusState // TypeDefIndex: 12
{
    public bool enabled; // 0x40
    public int value; // 0x44
}
"""
        ai = module.extract_class_fields(dump, "AIParameterConfig", 0x20, 0x150)
        self.assertEqual([(x["offset"], x["name"]) for x in ai], [
            ("0x24", "positionGate"), ("0x30", "ignored"),
            ("0x148", "farGate"), ("0x14C", "nearGate"),
        ])
        player = module.extract_class_fields(dump, "PlayerProperty", 0x90, 0xA0)
        self.assertEqual(player[1]["offset"], "0x98")
        self.assertEqual(player[1]["type"], "CollectionBonusState")
        nested = module.extract_fields_for_declared_type(dump, player[1]["type"], 0x40, 0x44)
        self.assertEqual([(x["offset"], x["name"]) for x in nested], [
            ("0x40", "enabled"), ("0x44", "value"),
        ])

    def test_target_ranges_only_claim_exact_when_scriptmethod_proves_it(self):
        module = load_tool()
        methods = [
            (0x14DEFDC, "Known.TargetHeight"),
            (0x14DF100, "Next.Method"),
        ]
        exact = module.resolve_requested_targets(methods)[0]
        fallback = module.resolve_requested_targets([])[0]
        self.assertTrue(exact.exact_function_boundary)
        self.assertEqual(exact.metadata_name, "Known.TargetHeight")
        self.assertFalse(fallback.exact_function_boundary)
        self.assertEqual(fallback.boundary_source, "bounded-fallback-window")

    def test_known_target_labels_follow_published_exact_identities(self):
        module = load_tool()
        ranges = {item.start: item for item in module.resolve_requested_targets([])}
        self.assertEqual(ranges[0x14DEFDC].target.name, "goal_door_height_14DEFDC")
        self.assertEqual(ranges[0x1B60CC8].target.name, "xnumber_create_1B60CC8")
        self.assertNotIn("random", ranges[0x1B60CC8].target.name.lower())

    def test_requests_property_lookup_callees_without_guessing_identity(self):
        module = load_tool()
        by_start = {item.start: item for item in module.resolve_requested_targets([])}
        self.assertIn(0x1968398, by_start)
        self.assertIn(0x1967D38, by_start)
        self.assertIn(0x1B718D8, by_start)
        self.assertEqual(by_start[0x1968398].target.name, "shoot_property_1968398")
        self.assertEqual(by_start[0x1967D38].target.name, "property_lookup_1967D38")
        self.assertEqual(by_start[0x1B718D8].target.name, "property_fallback_1B718D8")
        self.assertFalse(by_start[0x1967D38].exact_function_boundary)
        self.assertFalse(by_start[0x1B718D8].exact_function_boundary)

        methods = [
            (0x1967D38, "Exact.Lookup.Name"),
            (0x1967E00, "Next.Lookup.Method"),
            (0x1B718D8, "Exact.Fallback.Name"),
            (0x1B71920, "Next.Fallback.Method"),
        ]
        exact = {item.start: item for item in module.resolve_requested_targets(methods)}
        self.assertTrue(exact[0x1967D38].exact_function_boundary)
        self.assertEqual(exact[0x1967D38].metadata_name, "Exact.Lookup.Name")
        self.assertTrue(exact[0x1B718D8].exact_function_boundary)
        self.assertEqual(exact[0x1B718D8].metadata_name, "Exact.Fallback.Name")

    def test_render_marks_sources_read_only_and_includes_deeper_metadata(self):
        module = load_tool()
        fields = [{"type": "List<XNumber>", "name": "shootDisMap", "offset": "0xE8", "line": "public List<XNumber> shootDisMap; // 0xE8"}]
        ai_fields = [{"type": "XNumber", "name": "farGate", "offset": "0x148", "line": "public XNumber farGate; // 0x148"}]
        player_fields = [{"type": "CollectionBonusState", "name": "bonusState", "offset": "0x98", "line": "public CollectionBonusState bonusState; // 0x98"}]
        nested_fields = [{"type": "bool", "name": "enabled", "offset": "0x40", "line": "public bool enabled; // 0x40"}]
        ranges = module.resolve_requested_targets([])
        text = module.render_report(
            identities={"dump.cs": "a", "script.json": "b", "global-metadata.dat": "c", "libil2cpp.so": "d"},
            fields=fields,
            ai_fields=ai_fields,
            player_property_fields=player_fields,
            nested_bonus_type="CollectionBonusState",
            nested_bonus_fields=nested_fields,
            metadata_path=Path("script.json"),
            resolved_ranges=ranges,
            listings={item.target.name: [f"{item.start:08X}: ret"] for item in ranges},
            direct_calls={item.target.name: [] for item in ranges},
        )
        self.assertIn("POLICY: READ_ONLY", text)
        self.assertIn("AI_PARAMETER_CONFIG_FIELDS", text)
        self.assertIn("farGate", text)
        self.assertIn("PLAYER_PROPERTY_FIELDS", text)
        self.assertIn("bonusState", text)
        self.assertIn("NESTED_BONUS_TYPE: CollectionBonusState", text)
        self.assertIn("0x01967D38", text)
        self.assertIn("0x01B718D8", text)
        self.assertNotIn("downward_random_1B60CC8", text)

    def test_write_output_survives_path_write_text_bad_fd_and_emits_utf8_lf(self):
        module = load_tool()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "report.txt"
            with mock.patch.object(Path, "write_text", side_effect=OSError(9, "Bad file descriptor")):
                module.write_output(output, "alpha\r\nbeta\rgamma\n")
            self.assertEqual(output.read_bytes(), b"alpha\nbeta\ngamma\n")


if __name__ == "__main__":
    unittest.main()
