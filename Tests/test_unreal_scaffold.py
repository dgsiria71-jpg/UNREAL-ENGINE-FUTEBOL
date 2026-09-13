import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UnrealScaffoldTests(unittest.TestCase):
    def test_project_declares_required_plugins_and_windows(self):
        project = json.loads((ROOT / "Football.uproject").read_text(encoding="utf-8"))
        self.assertIn("Windows", project["TargetPlatforms"])
        plugins = {item["Name"] for item in project["Plugins"]}
        self.assertTrue({"EnhancedInput", "PoseSearch", "IKRig", "ControlRig", "CommonUI"} <= plugins)

    def test_build_and_targets_keep_cpp_server_boundary(self):
        build = (ROOT / "Source" / "Football" / "Football.Build.cs").read_text(encoding="utf-8")
        self.assertIn('"EnhancedInput"', build)
        self.assertIn('"PoseSearch"', build)
        self.assertIn('"IKRig"', build)
        self.assertIn('"ControlRig"', build)
        for name, target_type in (
            ("Football.Target.cs", "TargetType.Game"),
            ("FootballClient.Target.cs", "TargetType.Client"),
            ("FootballServer.Target.cs", "TargetType.Server"),
        ):
            text = (ROOT / "Source" / "Football" / name).read_text(encoding="utf-8")
            self.assertIn(target_type, text)
            self.assertIn('ExtraModuleNames.Add("Football")', text)

    def test_contact_adapter_has_no_impulse_fallback(self):
        contract = (ROOT / "Source" / "Football" / "Public" /
                    "FootballNormalizedContracts.h").read_text(encoding="utf-8")
        subsystem = (ROOT / "Source" / "Football" / "Private" /
                     "FootballSimulationSubsystem.cpp").read_text(encoding="utf-8")
        ball_actor = (ROOT / "Source" / "Football" / "Private" /
                      "FootballBallActor.cpp").read_text(encoding="utf-8")
        self.assertNotRegex(contract, r"\bball_impulse\s*[:=]")
        self.assertNotIn("ball_impulse", subsystem)
        self.assertIn("bVelocityResolved", subsystem)
        self.assertIn("FixedStepSeconds", subsystem)
        self.assertIn("DOREPLIFETIME", ball_actor)
        self.assertIn("HasAuthority", ball_actor)

    def test_data_assets_preserve_provenance_and_unresolved_state(self):
        assets = (ROOT / "Source" / "Football" / "Public" /
                  "FootballDataAssets.h").read_text(encoding="utf-8")
        self.assertIn("UPrimaryDataAsset", assets)
        self.assertIn("ProvenanceHash", assets)
        self.assertIn("bVelocitySemanticsResolved", assets)
        self.assertIn("bProvisionalTuning", assets)

    def test_input_contract_is_intent_only(self):
        intent = (ROOT / "Source" / "Football" / "Public" /
                  "FootballInputContracts.h").read_text(encoding="utf-8")
        self.assertIn("FFootballInputIntent", intent)
        self.assertIn("FFootballGameplayCommand", intent)
        self.assertIn("OwnerPlayerId", intent)
        self.assertIn("EFootballGameplayAction", intent)
        self.assertIn("ActionStrength", intent)
        self.assertIn("TargetPlayerId", intent)
        self.assertNotIn("RecoveredVelocity", intent)
        self.assertNotIn("BallState", intent)


    def test_player_character_routes_intent_to_server_simulation(self):
        header = (ROOT / "Source" / "Football" / "Public" /
                  "FootballPlayerCharacter.h").read_text(encoding="utf-8")
        implementation = (ROOT / "Source" / "Football" / "Private" /
                          "FootballPlayerCharacter.cpp").read_text(encoding="utf-8")
        self.assertIn("ACharacter", header)
        self.assertIn("ServerSubmitInputIntent", header)
        self.assertIn("GetSubsystem<UFootballSimulationSubsystem>", implementation)
        self.assertIn("Command.OwnerPlayerId = PlayerId", implementation)
        self.assertIn("SetReplicateMovement(false)", implementation)

    def test_contact_provenance_is_explicit(self):
        contract = (ROOT / "Source" / "Football" / "Public" /
                    "FootballNormalizedContracts.h").read_text(encoding="utf-8")
        self.assertIn("EFootballContactProvenance", contract)
        self.assertIn("NewGameAuthored", contract)
        self.assertIn("MobileRecovered", contract)
        self.assertIn("Provenance", contract)


if __name__ == "__main__":
    unittest.main()
