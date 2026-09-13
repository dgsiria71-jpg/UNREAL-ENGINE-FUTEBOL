from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

DOWNLOADS = Path(r"C:\Users\dg71\Downloads")
OUTPUT = Path("Recovery/Normalized/recovery_manifest.json")
SOURCES = [
    ("physics_v0_2", "FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip"),
    ("animation_v1_0", "FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip"),
    ("migration_v1_1", "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip"),
    ("pc_3d_v0_2", "FOOTBALL_PC_3D_READY_PACK_v0_2.zip"),
    ("ecosystem_v0_2", "FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip"),
    ("visual_assets_v0_1", "FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip"),
]
PATTERNS = (
    "spmove",
    "getkickvelocity",
    "getvhor",
    "getvver",
    "vertical_accel_raw",
    "ball_contact",
    "physics",
    "controller",
    "cofmotion",
    "global-metadata.dat",
    "libil2cpp",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def selected_entries(z: zipfile.ZipFile):
    out = []
    for info in z.infolist():
        low = info.filename.lower()
        if info.is_dir() or not any(pattern in low for pattern in PATTERNS):
            continue
        out.append(
            {
                "path": info.filename,
                "size": info.file_size,
                "crc": f"{info.CRC & 0xffffffff:08x}",
            }
        )
    return out


def find_text(z: zipfile.ZipFile, needle: bytes):
    rows = []
    for info in z.infolist():
        if info.is_dir() or info.file_size > 4_000_000:
            continue
        low = info.filename.lower()
        if not low.endswith((".md", ".txt", ".json", ".py", ".cs", ".cpp", ".h", ".c")):
            continue
        data = z.read(info)
        if needle.lower() in data.lower():
            rows.append(info.filename)
    return rows


records = []
for source_id, filename in SOURCES:
    path = DOWNLOADS / filename
    if not path.exists():
        records.append(
            {
                "source_id": source_id,
                "filename": filename,
                "status": "missing_local_archive",
            }
        )
        continue
    with zipfile.ZipFile(path) as archive:
        entry_names = archive.namelist()
        rec = {
            "source_id": source_id,
            "filename": filename,
            "status": "verified_local_archive_not_committed",
            "absolute_path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "zip_entries": len(entry_names),
            "selected_entries": selected_entries(archive),
            "text_hits": {
                "spmoveInUseData": find_text(archive, b"spmoveInUseData"),
                "GetKickVelocity": find_text(archive, b"GetKickVelocity"),
                "GetVHor": find_text(archive, b"GetVHor"),
                "GetVVer": find_text(archive, b"GetVVer"),
                "92/92": find_text(archive, b"92/92"),
            },
        }
        if source_id == "physics_v0_2":
            rec["declared_coverage"] = json.loads(
                archive.read(
                    "FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2/03_PARSED/SOURCE_COVERAGE.json"
                )
            )
        if source_id == "animation_v1_0":
            rec["controller_stats"] = json.loads(
                archive.read(
                    "FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0/01_CONTROLLER/CONTROLLER_STATS.json"
                )
            )
        records.append(rec)

result = {
    "schema_version": "football.recovery.inventory.v2",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "repository_portability": "fresh_checkout_supported",
    "engine_target": "Unreal Engine 5.x",
    "mobile_source": "football-dream-be-a-pro-1-221-5",
    "normalization_status": "schema_confirmed_velocity_unresolved",
    "source_of_truth": "verified mobile recovery archives plus committed normalized evidence and Blender source assets",
    "normalized_artifacts": {
        "spmove_collected_open_all": "Recovery/Normalized/spmove_collected_open_all.json",
        "physics_contract": "Recovery/Normalized/physics_runtime_contract.json",
        "native_static_trace": "Recovery/Normalized/native_static_trace.json",
        "cal_spmove_trace": "Recovery/Normalized/cal_spmove_static_trace.json",
        "spmove_manager_trace": "Recovery/Normalized/spmove_manager_static_trace.json",
        "spmove_deserialize_trace": "Recovery/Normalized/spmove_deserialize_static_trace.json",
        "spmove_runtime_trace": "Recovery/Normalized/spmove_runtime_static_trace.json",
        "spmove_modifier_access_trace": "Recovery/Normalized/spmove_modifier_access_static_trace.json",
        "spmove_inventory_collector_trace": "Recovery/Normalized/spmove_inventory_collector_static_trace.json",
        "spmove_inventory": "Recovery/Normalized/spmove_inventory.json",
        "velocity_base_regions_trace": "Recovery/Normalized/velocity_base_regions_static_trace.json",
        "native_sqrt_table": "Recovery/Normalized/native_sqrt_table.json",
        "native_kernel_validation": "Recovery/Normalized/native_kernel_validation.json",
        "native_vector_validation": "Recovery/Normalized/native_vector_validation.json",
        "native_spmove_branch_validation": "Recovery/Normalized/native_spmove_branch_validation.json",
        "native_spmove_selection_validation": "Recovery/Normalized/native_spmove_selection_validation.json",
        "native_spmove_producer_validation": "Recovery/Normalized/native_spmove_producer_validation.json",
        "mobile_source_matrix": "Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json",
        "feature_coverage": "Recovery/Normalized/feature_coverage.json",
        "playable_match_contract": "Recovery/Normalized/playable_match_contract.json",
        "unreal_import_plan": "Recovery/Normalized/unreal_import_plan.json",
        "original_reassembly": "Recovery/Normalized/original_reassembly.json",
    },
    "local_regeneration_artifacts": {
        "spmove": {
            "path": "Recovery/Normalized/spmove_normalized.json",
            "generator": "Tools/normalize_spmove.py",
            "status": "local_source_required",
            "required_for_fresh_checkout_ci": False,
            "expected_sha256": "6f013b7f32dfcd329f389fea0ae75acf127a06d4e93b7447d7c7f099fb809414",
        },
        "archive_catalog": {
            "path": "Recovery/Normalized/archive_catalog.json",
            "generator": "Tools/catalog_football_archives.py",
            "status": "local_source_required",
            "required_for_fresh_checkout_ci": False,
        },
    },
    "sources": records,
    "semantic_gates": {
        "physics_v0_3": "blocked_until_spmove_VHor_VVer_GetVHor_GetVVer_GetKickVelocity_BALL_CONTACT_regression",
        "vertical_accel_field": "vertical_accel_raw",
        "neymar": "v1.9_preserved_paused",
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"wrote {OUTPUT} sources={len(records)} schema={result['schema_version']}")
