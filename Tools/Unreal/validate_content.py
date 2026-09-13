"""Validate normalized recovery before importing it in Unreal Editor.

Run with Unreal's embedded Python (or from the Output Log Python console).
This tool is deliberately read-only: it checks provenance and gate status and
does not mutate the preserved mobile archives or the paused Neymar line.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import unreal  # type: ignore
except ImportError:  # allows static checks outside UE
    unreal = None


EXPECTED_PHYSICS_SHA256 = (
    "7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac"
)
EXPECTED_GATE = (
    "blocked_until_spmove_VHor_VVer_GetVHor_GetVVer_GetKickVelocity_"
    "BALL_CONTACT_regression"
)


def _log(message: str) -> None:
    if unreal is not None:
        unreal.log(message)
    else:
        print(message)


def validate_manifest(project_dir: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = project_dir / "Recovery" / "Normalized" / "recovery_manifest.json"
    if not manifest_path.is_file():
        return [f"missing manifest: {manifest_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = {
        item.get("source_id"): item
        for item in manifest.get("sources", [])
        if item.get("source_id")
    }
    physics = sources.get("physics_v0_2", {})
    if physics.get("sha256") != EXPECTED_PHYSICS_SHA256:
        errors.append("physics v0.2 SHA-256 does not match the canonical baseline")

    gates = manifest.get("semantic_gates", {})
    if gates.get("physics_v0_3") != EXPECTED_GATE:
        errors.append("physics v0.3 gate changed unexpectedly")
    if gates.get("vertical_accel_field") != "vertical_accel_raw":
        errors.append("vertical field was renamed before proof")
    if gates.get("neymar") != "v1.9_preserved_paused":
        errors.append("Neymar pause/preservation status changed")

    if manifest.get("engine_target") != "Unreal Engine 5.x":
        errors.append("engine target is not Unreal Engine 5.x")
    if manifest.get("normalization_status") != "schema_confirmed_velocity_unresolved":
        errors.append("normalization status is not the reviewed schema-confirmed unresolved state")

    normalized_path = project_dir / "Recovery" / "Normalized" / "spmove_normalized.json"
    if not normalized_path.is_file():
        errors.append("missing normalized spmove schema report")
    else:
        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        canonical = normalized.get("canonical_source", {})
        if canonical.get("action", {}).get("record_count") != 48:
            errors.append("canonical spmoveactiondata record count changed")
        if canonical.get("config", {}).get("record_count") != 292:
            errors.append("canonical spmoveconfig record count changed")
        if normalized.get("semantic_status") != "record_schema_confirmed_velocity_semantics_unresolved":
            errors.append("spmove semantic gate changed without review")
    if not (project_dir / "Recovery" / "Normalized" / "native_static_trace.json").is_file():
        errors.append("missing native static trace report")
    if not (project_dir / "Recovery" / "Normalized" / "cal_spmove_static_trace.json").is_file():
        errors.append("missing calSpmoveInUse producer trace")
    if not (project_dir / "Recovery" / "Normalized" / "spmove_manager_static_trace.json").is_file():
        errors.append("missing spmove manager static trace")
    if not (project_dir / "Recovery" / "Normalized" / "spmove_deserialize_static_trace.json").is_file():
        errors.append("missing spmove deserializer static trace")
    if not (project_dir / "Recovery" / "Normalized" / "spmove_runtime_static_trace.json").is_file():
        errors.append("missing spmove runtime static trace")
    if not (project_dir / "Recovery" / "Normalized" / "spmove_modifier_access_static_trace.json").is_file():
        errors.append("missing spmove modifier access static trace")
    gameplay_contract_path = project_dir / "Recovery" / "Normalized" / "playable_match_contract.json"
    if not gameplay_contract_path.is_file():
        errors.append("missing playable match contract")
    else:
        gameplay = json.loads(gameplay_contract_path.read_text(encoding="utf-8"))
        if gameplay.get("authority") != "server_authoritative":
            errors.append("playable match authority is not server_authoritative")
        if gameplay.get("performance", {}).get("target_fps") != 120:
            errors.append("playable match target FPS changed unexpectedly")
    catalog_path = project_dir / "Recovery" / "Normalized" / "archive_catalog.json"
    if not catalog_path.is_file():
        errors.append("missing football archive catalog")
    else:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if catalog.get("workspace_finding", {}).get("advanced_92_92_workspace") != "not present in catalog entries":
            errors.append("archive catalog workspace finding changed unexpectedly")
    if not (project_dir / "Recovery" / "Physics" / "NATIVE_STATIC_EVIDENCE.md").is_file():
        errors.append("missing durable native static evidence record")

    return errors


def run() -> int:
    project_dir = (
        Path(unreal.Paths.project_dir())
        if unreal is not None
        else Path(__file__).resolve().parents[2]
    )
    errors = validate_manifest(project_dir)
    if errors:
        for error in errors:
            _log("FOOTBALL_CONTENT_ERROR: " + error)
        return 1
    _log("FOOTBALL_CONTENT_VALIDATION: GREEN (read-only provenance checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
