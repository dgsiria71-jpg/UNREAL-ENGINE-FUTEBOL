"""Inventory raw spmove sources without assigning unproven semantics.

The canonical migration archive and a separate mobile build are reported
side-by-side. This tool computes entry identity and visible metadata only; it
does not decode the binary schema or infer velocity equations.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path(r"C:\Users\dg71\Downloads")
SOURCES = (
    {
        "source_id": "migration_v1_1_canonical",
        "archive": DOWNLOADS / "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip",
        "paths": (
            "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER/02_GAMEPLAY_DATA/config/match/spmoveactiondata",
            "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER/02_GAMEPLAY_DATA/config/match/spmoveconfig",
        ),
        "relation": "canonical_baseline",
    },
    {
        "source_id": "football_dream_candidate",
        "archive": DOWNLOADS / "football-dream-be-a-pro-1-226-19.zip",
        "paths": (
            "assets/config/match/spmoveactiondata",
            "assets/config/match/spmoveconfig",
        ),
        "relation": "separate_hash_different_mobile_build",
    },
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory_source(source: dict) -> dict:
    archive_path = source["archive"]
    result = {
        "source_id": source["source_id"],
        "archive": str(archive_path),
        "relation": source["relation"],
        "archive_present": archive_path.is_file(),
        "entries": [],
    }
    if not archive_path.is_file():
        return result

    with zipfile.ZipFile(archive_path) as archive:
        result["archive_bytes"] = archive_path.stat().st_size
        for path in source["paths"]:
            try:
                data = archive.read(path)
            except KeyError:
                result["entries"].append({"path": path, "present": False})
                continue
            result["entries"].append(
                {
                    "path": path,
                    "present": True,
                    "bytes": len(data),
                    "sha256": digest(data),
                    "prefix_hex": data[:32].hex(),
                    "suffix_hex": data[-32:].hex(),
                }
            )
    return result


def main() -> int:
    report = {
        "schema_version": "football.recovery.spmove.inventory.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "semantic_status": "raw_identity_only",
        "explicit_unknowns": [
            "spmove binary record schema",
            "spmoveInUseData VHor modifier",
            "spmoveInUseData VVer modifier",
            "GetVHor/GetVVer indexing and interpolation",
            "GetKickVelocity composition",
        ],
        "sources": [inventory_source(source) for source in SOURCES],
    }
    output = ROOT / "Recovery" / "Normalized" / "spmove_inventory.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"SPMOVE_INVENTORY: sources={len(report['sources'])} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
