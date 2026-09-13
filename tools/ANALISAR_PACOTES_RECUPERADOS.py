from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
DOWNLOADS = HOME / "Downloads"
PROJECT = HOME / "Documents" / "ChatGPT" / "JOGO DE FUTEBOL"
OUT_DIR = PROJECT / ".local" / "package-delta-audit"

TARGET_NAMES = [
    "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_STAGE1_XPLAYABLE.zip",
    "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1.zip",
    "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip",
    "FOOTBALL_PC_3D_READY_PACK_v0_1.zip",
    "FOOTBALL_PC_3D_READY_PACK_v0_2.zip",
    "FOOTBALL_PLAYER_SYSTEMS_REFERENCE_PACK_v0_1.zip",
    "FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip",
    "FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip",
    "FOOTBALL_VISUAL_PRESENTATION_ARCHITECTURE_v1.zip",
    "FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip",
    "FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip",
    "FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip",
    "FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip",
    "FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11 (1).zip",
]

PAIR_COMPARISONS = [
    ("FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1.zip", "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip"),
    ("FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_STAGE1_XPLAYABLE.zip", "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip"),
    ("FOOTBALL_PC_3D_READY_PACK_v0_1.zip", "FOOTBALL_PC_3D_READY_PACK_v0_2.zip"),
    ("FOOTBALL_PLAYER_SYSTEMS_REFERENCE_PACK_v0_1.zip", "FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip"),
    ("FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip", "FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip"),
    ("FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip", "FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11 (1).zip"),
]

TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".py", ".cpp", ".h", ".cs", ".lua", ".ini"}
KEY_RE = re.compile(
    r"(?i)(92\s*/\s*92|GetVHor|GetVVer|GetKickVelocity|BALL_CONTACT|disassembly_shoot|"
    r"spmove|controller\.ctrl|cofmotion|xplayable|physics|animation|player|stadium|ball|unreal)"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_stream(f) -> str:
    h = hashlib.sha256()
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def normalize_entry(name: str) -> str:
    p = name.replace("\\", "/").lstrip("/")
    parts = [x for x in p.split("/") if x]
    if len(parts) > 1 and (
        parts[0].upper().startswith("FOOTBALL_")
        or parts[0].upper().startswith("FUTEBOL_")
    ):
        parts = parts[1:]
    return "/".join(parts)


def inspect_zip(path: Path) -> dict:
    archive_sha = sha256_file(path)
    entries = []
    text_hits = []
    by_hash = Counter()
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            normalized = normalize_entry(info.filename)
            with zf.open(info) as src:
                entry_sha = sha256_stream(src)
            by_hash[entry_sha] += 1
            entries.append(
                {
                    "path": normalized,
                    "original_path": info.filename,
                    "bytes": info.file_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": entry_sha,
                }
            )

            suffix = Path(normalized).suffix.lower()
            if suffix in TEXT_SUFFIXES and info.file_size <= 4_000_000:
                try:
                    raw = zf.read(info)
                    text = raw.decode("utf-8", "replace")
                except Exception:
                    continue
                matches = sorted({m.group(0) for m in KEY_RE.finditer(text)})
                if matches:
                    text_hits.append(
                        {
                            "path": normalized,
                            "matches": matches[:30],
                        }
                    )

    return {
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": archive_sha,
        "entry_count": len(entries),
        "duplicate_payload_hashes_inside_archive": sum(1 for c in by_hash.values() if c > 1),
        "entries": entries,
        "text_hits": text_hits,
    }


def compare_archives(a: dict, b: dict) -> dict:
    a_by_path = {e["path"]: e for e in a["entries"]}
    b_by_path = {e["path"]: e for e in b["entries"]}
    a_paths = set(a_by_path)
    b_paths = set(b_by_path)
    common = a_paths & b_paths
    changed = [
        p for p in common
        if a_by_path[p]["sha256"] != b_by_path[p]["sha256"]
    ]
    same = [
        p for p in common
        if a_by_path[p]["sha256"] == b_by_path[p]["sha256"]
    ]
    return {
        "a": a["name"],
        "b": b["name"],
        "same_archive_sha": a["sha256"] == b["sha256"],
        "same_paths_same_content": len(same),
        "same_paths_changed_content": len(changed),
        "only_in_a_count": len(a_paths - b_paths),
        "only_in_b_count": len(b_paths - a_paths),
        "changed_paths": sorted(changed)[:500],
        "only_in_a": sorted(a_paths - b_paths)[:500],
        "only_in_b": sorted(b_paths - a_paths)[:500],
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    found: dict[str, Path] = {}
    missing = []
    for name in TARGET_NAMES:
        p = DOWNLOADS / name
        if p.exists():
            found[name] = p
        else:
            missing.append(name)

    packages = {}
    for name, path in found.items():
        print(f"ANALYZE {name}", flush=True)
        packages[name] = inspect_zip(path)

    comparisons = []
    for a_name, b_name in PAIR_COMPARISONS:
        if a_name in packages and b_name in packages:
            comparisons.append(compare_archives(packages[a_name], packages[b_name]))

    sha_groups = defaultdict(list)
    for pkg in packages.values():
        sha_groups[pkg["sha256"]].append(pkg["name"])
    exact_archive_duplicates = [
        {"sha256": sha, "files": names}
        for sha, names in sorted(sha_groups.items())
        if len(names) > 1
    ]

    result = {
        "schema_version": "football.recovered.package.delta.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": "Downloads",
        "policy": {
            "read_only": True,
            "canonical_mobile": "1-221-5",
            "isolated_mobile": "1-226-19",
            "note": "This report compares recovered delivery archives only; it does not merge them.",
        },
        "packages": list(packages.values()),
        "comparisons": comparisons,
        "exact_archive_duplicates": exact_archive_duplicates,
        "missing_targets": missing,
    }

    json_path = OUT_DIR / "RECOVERED_PACKAGE_DELTA_REPORT.json"
    md_path = OUT_DIR / "RECOVERED_PACKAGE_DELTA_REPORT.md"
    csv_path = OUT_DIR / "RECOVERED_PACKAGE_INDEX.csv"

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["name", "bytes", "sha256", "entry_count", "text_hit_count"])
        for pkg in packages.values():
            w.writerow([pkg["name"], pkg["bytes"], pkg["sha256"], pkg["entry_count"], len(pkg["text_hits"])])

    lines = [
        "# RECOVERED PACKAGE DELTA REPORT",
        "",
        f"Generated UTC: `{result['generated_utc']}`",
        "",
        f"Packages analyzed: **{len(packages)}**",
        f"Missing targets: **{len(missing)}**",
        "",
        "## Package identities",
        "",
        "| Package | Entries | Bytes | SHA-256 |",
        "|---|---:|---:|---|",
    ]
    for pkg in packages.values():
        lines.append(f"| `{pkg['name']}` | {pkg['entry_count']} | {pkg['bytes']} | `{pkg['sha256']}` |")

    lines += ["", "## Exact archive duplicates", ""]
    if exact_archive_duplicates:
        for group in exact_archive_duplicates:
            lines.append(f"- `{group['sha256']}`: " + ", ".join(f"`{x}`" for x in group["files"]))
    else:
        lines.append("- none")

    lines += ["", "## Pairwise deltas", ""]
    for c in comparisons:
        lines += [
            f"### `{c['a']}` → `{c['b']}`",
            "",
            f"- exact same archive: `{c['same_archive_sha']}`",
            f"- same path + same content: **{c['same_paths_same_content']}**",
            f"- same path + changed content: **{c['same_paths_changed_content']}**",
            f"- only in A: **{c['only_in_a_count']}**",
            f"- only in B: **{c['only_in_b_count']}**",
            "",
        ]
        if c["only_in_b"]:
            lines.append("First entries only in B:")
            for p in c["only_in_b"][:40]:
                lines.append(f"- `{p}`")
            lines.append("")
        if c["changed_paths"]:
            lines.append("First changed paths:")
            for p in c["changed_paths"][:40]:
                lines.append(f"- `{p}`")
            lines.append("")

    lines += ["## Native/physics keyword evidence", ""]
    for pkg in packages.values():
        hits = [h for h in pkg["text_hits"] if any(k.lower() in " ".join(h["matches"]).lower() for k in ["92/92", "getvhor", "getvver", "getkickvelocity", "ball_contact", "disassembly_shoot", "spmove"])]
        if hits:
            lines.append(f"### `{pkg['name']}`")
            for hit in hits[:80]:
                lines.append(f"- `{hit['path']}`: {', '.join(hit['matches'])}")
            lines.append("")

    if missing:
        lines += ["## Missing target archives", ""]
        for name in missing:
            lines.append(f"- `{name}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"GREEN: {json_path}")
    print(f"GREEN: {md_path}")
    print(f"GREEN: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
