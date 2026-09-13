"""Build the canonical open-all spmove inventory from normalized mobile data.

The transform implements only the collection shape proven by
XSpmoveManager.getSpmoveIdDict and IL2CPP field layouts. It does not infer a
real player's owned spmoveIds, eligibility, odds, RNG, or velocity semantics.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Recovery" / "Normalized" / "spmove_normalized.json"
TRACE = ROOT / "Recovery" / "Normalized" / "spmove_inventory_collector_static_trace.json"
RUNTIME_TRACE = ROOT / "Recovery" / "Normalized" / "spmove_runtime_static_trace.json"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_collected_open_all.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    if trace.get("analysis_status") != "inventory_collection_shape_static_confirmed":
        raise ValueError("collector trace does not prove the normalized collection shape")
    all_records = source["canonical_source"]["config"]["records"]
    runtime_trace = json.loads(RUNTIME_TRACE.read_text(encoding="utf-8"))
    guard = runtime_trace.get("param_runtime_population", {}).get("enabled_guard", {})
    if guard.get("field") != "SpmoveConfigConfigItem.enable":
        raise ValueError("runtime trace does not prove the enabled-record guard")
    records = [record for record in all_records if int(record["enable"]) != 0]
    configs: dict[int, dict] = {}
    for record in records:
        config_id = int(record["id"])
        if config_id in configs:
            raise ValueError(f"duplicate config id {config_id}")
        configs[config_id] = record

    buckets: dict[int, list[dict[str, int]]] = defaultdict(list)
    child_references = 0
    for root in records:  # explicit decoded-record order; no Dictionary order claim
        root_logic_id = int(root["logic_id"])
        buckets[root_logic_id]
        for raw_child_id in root["child_spmove_ids"]:
            child_id = int(raw_child_id)
            child_references += 1
            child = configs.get(child_id)
            if child is None:
                raise ValueError(f"missing child config {child_id} referenced by {root['id']}")
            buckets[int(child["logic_id"])].append(
                {"child_id": child_id, "father_id": int(root["id"])}
            )
        buckets[root_logic_id].append(
            {"child_id": int(root["id"]), "father_id": 0}
        )

    serialized_buckets = [
        {"logic_id": logic_id, "entries": buckets[logic_id]}
        for logic_id in sorted(buckets)
    ]
    return {
        "schema_version": "football.recovery.spmove_collected_inventory.v1",
        "status": "open_all_collection_shape_complete",
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": sha256(SOURCE),
            "source_id": source["canonical_source"]["source_id"],
            "config_records": len(records),
        },
        "native_trace": {
            "collector_path": TRACE.relative_to(ROOT).as_posix(),
            "collector_sha256": sha256(TRACE),
            "runtime_path": RUNTIME_TRACE.relative_to(ROOT).as_posix(),
            "runtime_sha256": sha256(RUNTIME_TRACE),
            "method": trace["source_scope"],
            "enabled_guard": guard,
            "behavior_validated": trace["behavior_validated"],
        },
        "collection_mode": "open_all",
        "ordering": {
            "root_order": "canonical decoded spmoveconfig record order",
            "runtime_dictionary_values_order": "unproven",
            "selection_impact": "normal velocity selector uses maximum signed child_id",
        },
        "counts": {
            "serialized_config_records": len(all_records),
            "enabled_config_records": len(records),
            "disabled_config_records": len(all_records) - len(records),
            "child_references": child_references,
            "logic_buckets": len(serialized_buckets),
            "inventory_entries": sum(len(bucket["entries"]) for bucket in serialized_buckets),
            "missing_child_configs": 0,
        },
        "buckets": serialized_buckets,
        "unknown": [
            "real player spmoveIds source and lifetime",
            "eligibility and ownership filters before the player inventory snapshot",
            "odds and RNG behavior after collection",
            "managed Dictionary.Values ordering in the original runtime",
            "complete GetVHor/GetVVer/GetKickVelocity composition",
        ],
        "physics_v0_3_gate": "blocked",
    }


def main() -> int:
    report = build()
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    print(
        "SPMOVE_COLLECTED_OPEN_ALL: GREEN "
        f"configs={counts['enabled_config_records']} children={counts['child_references']} "
        f"buckets={counts['logic_buckets']} entries={counts['inventory_entries']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
