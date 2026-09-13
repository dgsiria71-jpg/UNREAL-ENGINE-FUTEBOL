import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RecoveryManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (ROOT / "Recovery" / "Normalized" / "recovery_manifest.json")
            .read_text(encoding="utf-8")
        )

    def test_manifest_records_schema_normalization_without_closing_velocity_gate(self):
        self.assertEqual(
            self.manifest["normalization_status"],
            "schema_confirmed_velocity_unresolved",
        )
        self.assertEqual(
            self.manifest["semantic_gates"]["physics_v0_3"],
            "blocked_until_spmove_VHor_VVer_GetVHor_GetVVer_GetKickVelocity_BALL_CONTACT_regression",
        )

    def test_manifest_artifact_paths_exist(self):
        artifacts = self.manifest["normalized_artifacts"]
        for relative in artifacts.values():
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_manifest_registers_shoot_speed_v_rate_evidence(self):
        artifacts = self.manifest["normalized_artifacts"]
        self.assertEqual(
            artifacts["shoot_speed_v_rate_trace"],
            "Recovery/Normalized/shoot_speed_v_rate_static_trace.json",
        )
        sources = {item["source_id"]: item for item in self.manifest["sources"]}
        self.assertIn("shoot_speed_v_rate_support_disassembly", sources)
        self.assertIn("shoot_speed_v_rate_metadata", sources)
        self.assertEqual(
            sources["shoot_speed_v_rate_metadata"]["global_metadata_sha256"],
            "92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e",
        )


if __name__ == "__main__":
    unittest.main()
