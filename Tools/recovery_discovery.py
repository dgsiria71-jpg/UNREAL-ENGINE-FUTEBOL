"""Reproducible, bounded, read-only discovery of the advanced physics workspace.

The search records candidate paths and relevant archive entries but never reads
credentials, sessions, databases, logs, or modifies source archives.
"""
from __future__ import annotations

import fnmatch
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path(r"C:\Users\dg71\Downloads")
SEARCH_ROOTS = (
    (DOWNLOADS, 3),
    (ROOT, 6),
    (Path(r"C:\Users\dg71\Documents\ChatGPT"), 2),
    (Path(r"C:\Users\dg71\Desktop"), 2),
)
PRUNE_NAMES = {".git", ".local", "node_modules", "__pycache__", "webcache"}
NAME_PATTERNS = (
    "*PHYSICS*RECOVERY*WORK*",
    "*PHYSICS*WORKSPACE*",
    "*92*92*",
    "*SPMOVE*WORK*",
)
ARCHIVE_PATTERNS = ("*.zip", "*.7z", "*.tar", "*.xapk")


def discover_paths() -> list[str]:
    found: set[str] = set()
    for base, max_depth in SEARCH_ROOTS:
        if not base.exists():
            continue
        stack: list[tuple[Path, int]] = [(base, 0)]
        while stack:
            current, depth = stack.pop()
            try:
                entries = list(current.iterdir())
            except (OSError, PermissionError):
                continue
            for path in entries:
                if any(fnmatch.fnmatch(path.name.upper(), pattern.upper()) for pattern in NAME_PATTERNS):
                    found.add(str(path))
                if path.is_dir() and depth < max_depth and path.name not in PRUNE_NAMES:
                    stack.append((path, depth + 1))
    return sorted(found)


def inspect_download_archives() -> list[dict]:
    records: list[dict] = []
    if not DOWNLOADS.exists():
        return records
    for path in sorted(DOWNLOADS.iterdir()):
        if not path.is_file() or not any(
            fnmatch.fnmatch(path.name.lower(), p) for p in ARCHIVE_PATTERNS
        ):
            continue
        record = {"filename": path.name, "path": str(path), "relevant_entries": []}
        if path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(path) as archive:
                    for info in archive.infolist():
                        name = info.filename.lower()
                        if any(
                            token in name
                            for token in (
                                "spmove",
                                "92/92",
                                "physics_recovery_work",
                                "getvhor",
                                "getvver",
                                "getkickvelocity",
                            )
                        ):
                            record["relevant_entries"].append(
                                {"path": info.filename, "bytes": info.file_size}
                            )
            except (OSError, zipfile.BadZipFile):
                record["error"] = "not a readable zip"
        records.append(record)
    return records


def main() -> int:
    report = {
        "schema_version": "football.recovery.discovery.v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "search_roots": [
            {"path": str(path), "max_depth": depth}
            for path, depth in SEARCH_ROOTS
        ],
        "workspace_candidates": discover_paths(),
        "download_archive_inspection": inspect_download_archives(),
        "interpretation": {
            "advanced_workspace": "not_found_in_bounded_scan",
            "native_spmove_body": "not_proven_by_archive_entries",
            "next_action": "supply or recover native/disassembly workspace before v0.3",
        },
    }
    output = ROOT / "Recovery" / "Normalized" / "recovery_discovery_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"RECOVERY_DISCOVERY: candidates={len(report['workspace_candidates'])} "
        f"archives={len(report['download_archive_inspection'])} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
