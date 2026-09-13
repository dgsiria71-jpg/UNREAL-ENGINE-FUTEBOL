import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Recovery" / "Normalized" / "recovery_manifest.json"


class RepositoryPortabilityTests(unittest.TestCase):
    def test_persisted_manifest_is_utf8_and_only_requires_committed_artifacts(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(manifest["schema_version"], "football.recovery.inventory.v2")
        self.assertEqual(manifest["repository_portability"], "fresh_checkout_supported")

        for name, relative in manifest["normalized_artifacts"].items():
            self.assertTrue((ROOT / relative).is_file(), f"{name}: {relative}")

        local_only = manifest["local_regeneration_artifacts"]
        self.assertEqual(
            local_only["spmove"]["path"],
            "Recovery/Normalized/spmove_normalized.json",
        )
        self.assertEqual(
            local_only["archive_catalog"]["path"],
            "Recovery/Normalized/archive_catalog.json",
        )
        for item in local_only.values():
            self.assertEqual(item["status"], "local_source_required")
            self.assertFalse(item.get("required_for_fresh_checkout_ci", True))


if __name__ == "__main__":
    unittest.main()
