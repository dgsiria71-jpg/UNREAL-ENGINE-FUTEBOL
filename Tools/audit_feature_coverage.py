"""Generate an evidence-based recovery/runtime coverage matrix."""
from __future__ import annotations
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"
OUTPUT_JSON = ROOT / "Recovery" / "Normalized" / "feature_coverage.json"
OUTPUT_MD = ROOT / "Docs" / "FEATURE_RECOVERY_COVERAGE.md"

ARCHIVES = {
    "animation": ("FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip", "91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64"),
    "physics": ("FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip", "7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac"),
    "migration": ("FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip", "c1c7d5352f94241c5aed771666ad5f723b24593ac7cf8c3bc9bfb0e7d175e1eb"),
    "pc_3d": ("FOOTBALL_PC_3D_READY_PACK_v0_2.zip", "e287e1140dd704479292e5516996484641ed326a027f5c8302577eadd3393226"),
    "ecosystem": ("FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip", "cea86e1e18f7aa58f924302bae542ebf2782217b32594d315aff3ff423efe813"),
}

def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()

def archive(name: str, expected: str) -> dict:
    path = DOWNLOADS / name
    if not path.is_file():
        return {"name": name, "present": False, "hash_matches": False, "entries": 0}
    with zipfile.ZipFile(path) as source:
        entries, bad = len(source.infolist()), source.testzip()
    actual = digest(path)
    return {"name": name, "present": True, "bytes": path.stat().st_size,
            "sha256": actual, "hash_matches": actual == expected,
            "entries": entries, "crc": "green" if bad is None else f"failed:{bad}"}

def row(name, source, normalized, executable, unreal, validated, evidence, gaps):
    return {"feature": name, "source_recovery": source, "normalized": normalized,
            "executable_reference": executable, "unreal_integration": unreal,
            "runtime_validated": validated, "evidence": evidence, "gaps": gaps}

def build_report() -> dict:
    no_ue = "not compiled or played in Unreal Editor on this machine"
    features = [
        row("Fixed-point physics and vectors", "confirmed", "confirmed", "native_differential_green", "contracts_scaffolded", "headless_only",
            ["FixedPoint", "NativeVectorMath", "13,685 kernel and 15,956 vector comparisons"], [no_ue, "native divide-by-zero fallback"]),
        row("Final kick velocity and ball contact", "partial", "inventory_shape_confirmed_velocity_partial", "collection_shape_tested_plus_partial_native_differential", "guarded_contract_scaffolded", "blocked",
            ["spmove branch/selection/producer native comparisons", "290 enabled configs -> 346 open-all inventory entries in 68 logic buckets", "BallContact rejects unresolved velocity"],
            ["real-player inventory source/eligibility/RNG", "GetVHor/GetVVer bases", "GetKickVelocity composition", "BALL_CONTACT.velocity regression"]),
        row("Animation controller and COFMotion", "confirmed_data_format", "catalogued_not_runtime_database", "exporter_and_previews_only", "planned", "not_validated",
            ["13,722 COFMotions", "20,213 states", "50,127 leaves", "40/40 xplayable clips", "48 GLB examples/previews"],
            ["2,769 logical action mappings", "bulk animation database", "retarget validation", "Pose Search/Motion Matching", "Animation Blueprint/IK/Control Rig", no_ue]),
        row("Collision, tackle, interception and goalkeeper", "confirmed_tables", "archive_schema_only", "simple_authored_headless_behaviour", "contracts_scaffolded", "not_mobile_equivalent",
            ["collision/tackle/intercept/GK source tables", "PlayableMatch fixture"],
            ["recovered collision resolution", "contact windows", "fouls/cards/advantage", "goalkeeper recovered equations"]),
        row("Pass, shot, dribble and defense", "confirmed_source_tables", "partial", "simple_authored_headless_behaviour", "input_and_simulation_scaffolded", "not_mobile_equivalent",
            ["ActionFit/ActionSpeed/ShootSpeed/PassSpeed/Dribble/Tackle sources", "six PlayableMatch actions"],
            ["mobile action selection/tuning", "first touch/through pass/cross/volley/header", "placed/curved/chipped/lob shots", "complete dribbles and defense"]),
        row("3D players, ball and stadium", "confirmed_partial_pc_exports", "asset_packages_only", "not_executed", "not_imported", "not_validated",
            ["ball.glb", "player_cristiano_rigged_named.glb", "placed stadium core GLBs"],
            ["ASTC texture transcode", "PBR materials", "deformable cloth", "complete crowd/flags/railings", "LODs/physics assets", "Unreal import/review"]),
        row("Game AI", "config_sources_present", "not_normalized_as_complete_ai", "not_implemented", "module_architecture_only", "not_validated",
            ["AI/config entries in migration archive", "AI architecture documentation"],
            ["Player/Team/Tactical/GK AI", "Manager/Club/Background AI", "difficulty and performance tests"]),
        row("Cameras and field views", "mobile_camera_sources_present", "not_normalized", "not_implemented", "planned", "not_validated",
            ["camera-named migration sources", "Broadcast and Player Career camera requirements"],
            ["Broadcast camera", "Player Career camera", "ball awareness/occlusion/comfort/transitions", "in-motion review"]),
        row("Match modes", "design_and_mobile_sources_present", "mode_roster_contract", "3v3_5v5_11v11_headless_fixture", "gameplay_scaffold_only", "headless_only",
            ["PlayableMatch", "playable_match_contract.json"],
            ["complete rules/restarts", "rendered field/cameras", "AI rosters", "real 5v5/11v11", "Career/co-op/Dedicated Server"]),
    ]
    return {"schema_version": "football.recovery.feature_coverage.v1",
            "mobile_source": "football-dream-be-a-pro-1-221-5",
            "engine_target": "Unreal Engine 5.x",
            "overall_status": "partial_recovery_and_headless_foundation_not_a_complete_game",
            "unreal_available": False,
            "archives": {key: archive(*value) for key, value in ARCHIVES.items()},
            "features": features,
            "summary": {"all_requested_systems_recovered": False,
                        "all_requested_systems_integrated": False,
                        "playable_unreal_match": False,
                        "animation_runtime_complete": False,
                        "mobile_ai_runtime_recovered": False,
                        "camera_runtime_complete": False,
                        "physics_v0_3_gate": "blocked"}}

def make_markdown(report: dict) -> str:
    lines = ["# Cobertura real de recovery e implementação", "",
             "Gerado por Tools/audit_feature_coverage.py. Fonte recuperada, normalização, referência executável, integração Unreal e validação runtime são estados separados.", "",
             "**Conclusão:** a build mobile 1-221-5 preserva muito material, mas o jogo completo ainda não foi recuperado nem integrado. O runtime Unreal ainda não foi compilado ou jogado nesta máquina.", "",
             "| Sistema | Fonte | Normalizado | Executável | Unreal | Validação |",
             "|---|---|---|---|---|---|"]
    for item in report["features"]:
        values = [item["feature"], item["source_recovery"], item["normalized"],
                  item["executable_reference"], item["unreal_integration"], item["runtime_validated"]]
        lines.append("| " + " | ".join(value.replace("_", " ") for value in values) + " |")
    lines.extend(["", "## Lacunas por sistema", ""])
    for item in report["features"]:
        lines.extend([f"### {item['feature']}", ""])
        lines.extend(f"- {gap}" for gap in item["gaps"])
        lines.append("")
    lines.extend(["## Regra de evidência", "",
                  "Um ZIP presente prova preservação de fonte. Parser e catálogo provam leitura estrutural. Teste headless prova apenas o contrato exercitado. Integração Unreal exige importação, compilação e execução no engine; animação em movimento, câmeras, multiplayer e 120 FPS exigem validações próprias.", ""])
    return "\n".join(lines)

def main() -> int:
    report = build_report()
    OUTPUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(make_markdown(report), encoding="utf-8")
    bad = [key for key, value in report["archives"].items()
           if not value["present"] or not value["hash_matches"] or value["crc"] != "green"]
    print(f"FEATURE_COVERAGE: {'GREEN' if not bad else 'INCOMPLETE'} features={len(report['features'])} archives={len(report['archives'])} bad={bad}")
    return 0 if not bad else 1

if __name__ == "__main__":
    raise SystemExit(main())
