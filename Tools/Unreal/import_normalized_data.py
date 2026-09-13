"""Import planning entry point for normalized recovery data.

The first pass validates source identity and emits an import plan. Actual
uasset creation belongs in the Unreal Editor process and must be added only
when a schema has a proved unit/coordinate mapping.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import unreal  # type: ignore
except ImportError:  # type: ignore
    unreal = None


def build_plan(project_dir: Path) -> dict:
    manifest_path = project_dir / "Recovery" / "Normalized" / "recovery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_summaries = {}
    for source in manifest.get("sources", []):
        source_id = source.get("source_id")
        if source_id:
            source_summaries[source_id] = {
                "filename": source.get("filename"),
                "bytes": source.get("bytes"),
                "sha256": source.get("sha256"),
                "zip_entries": source.get("zip_entries"),
            }

    gameplay_contract_path = project_dir / "Recovery" / "Normalized" / "playable_match_contract.json"
    gameplay_contract = json.loads(gameplay_contract_path.read_text(encoding="utf-8")) if gameplay_contract_path.is_file() else None

    return {
        "engine": "Unreal Engine 5.x",
        "source_of_truth_3d": "Blender",
        "physics_runtime": "authoritative_server",
        "sources": source_summaries,
        "semantic_gates": manifest.get("semantic_gates", {}),
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
            "native_spmove_selection_validation": "Recovery/Normalized/native_spmove_selection_validation.json",
            "native_spmove_producer_validation": "Recovery/Normalized/native_spmove_producer_validation.json",
            "mobile_source_matrix": "Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json",
            "archive_catalog": "Recovery/Normalized/archive_catalog.json",
            "playable_match_contract": "Recovery/Normalized/playable_match_contract.json",
        },
        "normalized_schema": {
            "codec": "LZ4 raw block",
            "canonical_action_records": 48,
            "canonical_config_records": 292,
            "candidate_config_records_isolated": 312,
            "velocity_semantics": "unresolved",
            "runtime_property_derivation": "partially_anchored_param_Xnumber_population_and_property_calls",
        },
        "playable_match": {
            "contract": "Recovery/Normalized/playable_match_contract.json",
            "available": gameplay_contract is not None,
            "provenance": gameplay_contract.get("provenance") if gameplay_contract else None,
        },
        "blocked": [
            "spmove inventory/eligibility dependencies, GetVHor/GetVVer bases and final contact velocity remain unresolved",
            "do not emit BALL_CONTACT velocity for unresolved actions",
        ],
        "next_importable": [
            "fixed-point XNumber primitives",
            "provenance-tagged animation metadata",
            "recovered clips after coordinate/unit validation",
        ],
    }


def run() -> int:
    project_dir = (
        Path(unreal.Paths.project_dir())
        if unreal is not None
        else Path(__file__).resolve().parents[2]
    )
    plan = build_plan(project_dir)
    output_path = project_dir / "Recovery" / "Normalized" / "unreal_import_plan.json"
    output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    if unreal is not None:
        unreal.log(f"Football import plan written: {output_path}")
    else:
        print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
