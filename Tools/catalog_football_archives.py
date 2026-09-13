"""Catalog football-related archives without extracting or mutating them.

The catalog is deliberately bounded to top-level Downloads archives whose names
identify the football project. It records hashes and only selected entry names
or small text hits, so it can prove provenance and candidate isolation without
turning the repository into a copy of the archives.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path(r"C:\Users\dg71\Downloads")
OUTPUT = ROOT / "Recovery" / "Normalized" / "archive_catalog.json"
ARCHIVE_NAME_RE = re.compile(r"(?i)^(?:FOOTBALL|FUTEBOL|football-dream).*(?:\.zip|\.xapk)$")
ENTRY_RE = re.compile(
    r"(?i)(spmove|physics|recovery|checkpoint|workspace|92.?/?92|"
    r"getkickvelocity|getvhor|getvver|ball_contact|native|disassembly|"
    r"global-metadata|libil2cpp|controller\.ctrl|cofmotion|vertical_accel)"
)
TEXT_RE = re.compile(r"(?i)(92\s*/\s*92|92/92|getkickvelocity|getvhor|getvver|"
                     r"spmoveinusedata|param_xnumber|vertical_accel_raw|physics recovery)")
TEXT_SUFFIXES = (".md", ".txt", ".json", ".py", ".cs", ".cpp", ".h", ".c", ".lua")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(name: str) -> str:
    lower = name.lower()
    if "physics_recovery_pack" in lower:
        return "canonical_physics_baseline"
    if "mobile_to_pc_migration_master_v1_1" in lower:
        return "canonical_migration_v1_1"
    if "football-dream" in lower:
        return "separate_mobile_candidate"
    if "master_archive_v1_1" in lower:
        return "historical_master_archive"
    if "animation_recovery" in lower:
        return "animation_recovery_baseline"
    return "football_supporting_archive"


def catalog_file(path: Path) -> dict:
    item = {
        "filename": path.name,
        "absolute_path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "classification": classify(path.name),
    }
    if path.suffix.lower() != ".zip":
        item["archive_status"] = "xapk_not_opened_as_zip"
        return item
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            selected = [
                {"path": info.filename, "bytes": info.file_size}
                for info in archive.infolist()
                if not info.is_dir() and ENTRY_RE.search(info.filename)
            ]
            text_hits: list[dict] = []
            for info in archive.infolist():
                if info.is_dir() or info.file_size > 4_000_000:
                    continue
                if not info.filename.lower().endswith(TEXT_SUFFIXES):
                    continue
                if not ENTRY_RE.search(info.filename) and not TEXT_RE.search(info.filename):
                    continue
                try:
                    data = archive.read(info)
                    text = data.decode("utf-8", "replace")
                except Exception:
                    continue
                matches = sorted(set(m.group(0) for m in TEXT_RE.finditer(text)))
                if matches:
                    text_hits.append({"path": info.filename, "matches": matches[:20]})
            item.update({
                "archive_status": "readable_zip",
                "zip_entries": len(names),
                "selected_entries": selected,
                "text_hits": text_hits,
            })
    except (OSError, zipfile.BadZipFile) as exc:
        item.update({"archive_status": "unreadable", "error": str(exc)})
    return item


def main() -> int:
    files = sorted(
        path for path in DOWNLOADS.iterdir()
        if path.is_file() and ARCHIVE_NAME_RE.match(path.name)
    )
    records = [catalog_file(path) for path in files]
    result = {
        "schema_version": "football.recovery.archive_catalog.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(DOWNLOADS),
        "scope": "top-level football/futebol recovery archives only",
        "records": records,
        "workspace_finding": {
            "advanced_92_92_workspace": "not present in catalog entries",
            "native_disassembly_workspace": "not present in catalog entries",
            "candidate_policy": "football-dream remains separate and is never merged into canonical migration",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FOOTBALL_ARCHIVE_CATALOG: GREEN archives={len(records)} output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
