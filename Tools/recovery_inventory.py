from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
from datetime import datetime, timezone

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
PATTERNS = ("spmove", "getkickvelocity", "getvhor", "getvver", "vertical_accel_raw", "ball_contact", "physics", "controller", "cofmotion", "global-metadata.dat", "libil2cpp")
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def selected_entries(z: zipfile.ZipFile):
    out = []
    for i in z.infolist():
        low = i.filename.lower()
        if i.is_dir() or not any(p in low for p in PATTERNS):
            continue
        out.append({"path": i.filename, "size": i.file_size, "crc": f"{i.CRC & 0xffffffff:08x}"})
    return out
def find_text(z: zipfile.ZipFile, needle: bytes):
    rows = []
    for i in z.infolist():
        if i.is_dir() or i.file_size > 4_000_000:
            continue
        low = i.filename.lower()
        if not low.endswith((".md",".txt",".json",".py",".cs",".cpp",".h",".c")):
            continue
        b = z.read(i)
        if needle.lower() in b.lower():
            rows.append(i.filename)
    return rows
records = []
for source_id, filename in SOURCES:
    path = DOWNLOADS / filename
    if not path.exists():
        records.append({"source_id": source_id, "filename": filename, "status": "missing"})
        continue
    with zipfile.ZipFile(path) as z:
        entry_names = z.namelist()
        rec = {
            "source_id": source_id,
            "filename": filename,
            "absolute_path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "zip_entries": len(entry_names),
            "selected_entries": selected_entries(z),
            "text_hits": {
                "spmoveInUseData": find_text(z, b"spmoveInUseData"),
                "GetKickVelocity": find_text(z, b"GetKickVelocity"),
                "GetVHor": find_text(z, b"GetVHor"),
                "GetVVer": find_text(z, b"GetVVer"),
                "92/92": find_text(z, b"92/92"),
            },
        }
        if source_id == "physics_v0_2":
            manifest = json.loads(z.read("FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2/03_PARSED/SOURCE_COVERAGE.json"))
            rec["declared_coverage"] = manifest
        if source_id == "animation_v1_0":
            stats = json.loads(z.read("FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0/01_CONTROLLER/CONTROLLER_STATS.json"))
            rec["controller_stats"] = stats
        records.append(rec)
result = {
    "schema_version": "football.recovery.inventory.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "engine_target": "Unreal Engine 5.x",
    "normalization_status": "schema_confirmed_velocity_unresolved",
    "source_of_truth": "mobile recovery archives plus Blender source assets",
    "normalized_artifacts": {
        "spmove": "Recovery/Normalized/spmove_normalized.json",
        "physics_contract": "Recovery/Normalized/physics_runtime_contract.json",
        "native_static_trace": "Recovery/Normalized/native_static_trace.json",
        "cal_spmove_trace": "Recovery/Normalized/cal_spmove_static_trace.json",
        "spmove_manager_trace": "Recovery/Normalized/spmove_manager_static_trace.json",
        "spmove_deserialize_trace": "Recovery/Normalized/spmove_deserialize_static_trace.json",
        "spmove_runtime_trace": "Recovery/Normalized/spmove_runtime_static_trace.json",
        "spmove_modifier_access_trace": "Recovery/Normalized/spmove_modifier_access_static_trace.json",
        "native_sqrt_table": "Recovery/Normalized/native_sqrt_table.json",
        "native_kernel_validation": "Recovery/Normalized/native_kernel_validation.json",
        "native_vector_validation": "Recovery/Normalized/native_vector_validation.json",
        "native_spmove_branch_validation": "Recovery/Normalized/native_spmove_branch_validation.json",
        "archive_catalog": "Recovery/Normalized/archive_catalog.json",
        "native_spmove_selection_validation": "Recovery/Normalized/native_spmove_selection_validation.json",
        "native_spmove_producer_validation": "Recovery/Normalized/native_spmove_producer_validation.json",
        "mobile_source_matrix": "Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json",
        "feature_coverage": "Recovery/Normalized/feature_coverage.json",
        "playable_match_contract": "Recovery/Normalized/playable_match_contract.json",
    },
    "sources": records,
    "semantic_gates": {
        "physics_v0_3": "blocked_until_spmove_VHor_VVer_GetVHor_GetVVer_GetKickVelocity_BALL_CONTACT_regression",
        "vertical_accel_field": "vertical_accel_raw",
        "neymar": "v1.9_preserved_paused",
    },
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUTPUT} sources={len(records)}")
