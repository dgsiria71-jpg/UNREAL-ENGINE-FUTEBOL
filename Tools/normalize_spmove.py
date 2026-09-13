"""Decode the recovered spmove tables into engine-independent JSON.

This tool is deliberately scoped to the binary schema that is visible in the
IL2CPP type dump: record layout and fixed-point values are preserved, while the
VHor/VVer/GetKickVelocity selection semantics remain explicitly unresolved.
The canonical migration build and the separate football-dream build are never
merged.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path(r"C:\Users\dg71\Downloads")

# Import the local raw-block decoder without requiring Tools to be a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_lz4_raw import decode_lz4_raw  # noqa: E402

SOURCES = (
    {
        "source_id": "migration_v1_1_canonical",
        "archive": DOWNLOADS / "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip",
        "relation": "canonical_baseline",
        "action_path": "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER/02_GAMEPLAY_DATA/config/match/spmoveactiondata",
        "config_path": "FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER/02_GAMEPLAY_DATA/config/match/spmoveconfig",
    },
    {
        "source_id": "football_dream_candidate",
        "archive": DOWNLOADS / "football-dream-be-a-pro-1-226-19.zip",
        "relation": "separate_hash_different_mobile_build",
        "action_path": "assets/config/match/spmoveactiondata",
        "config_path": "assets/config/match/spmoveconfig",
    },
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_i32(data: bytes, offset: int) -> tuple[int, int]:
    end = offset + 4
    if end > len(data):
        raise ValueError(f"truncated int32 at offset {offset}")
    return int.from_bytes(data[offset:end], "little", signed=True), end


def read_u32(data: bytes, offset: int) -> tuple[int, int]:
    end = offset + 4
    if end > len(data):
        raise ValueError(f"truncated uint32 at offset {offset}")
    return int.from_bytes(data[offset:end], "little", signed=False), end


def read_i32_list(data: bytes, offset: int, *, context: str) -> tuple[list[int], int]:
    count, offset = read_i32(data, offset)
    if count < 0 or count > 100_000:
        raise ValueError(f"{context}: invalid list count {count}")
    values: list[int] = []
    for _ in range(count):
        value, offset = read_i32(data, offset)
        values.append(value)
    return values, offset


def parse_action_table(decoded: bytes) -> list[dict]:
    """Parse SpmoveActionDataConfigItem records.

    IL2CPP field order in the recovered type is: id, gear, condition,
    anim_list, fancyId, spmove_check_ids, speed_fix_rate (XVector2).
    """
    count, offset = read_u32(decoded, 0)
    if count > 100_000:
        raise ValueError(f"invalid action record count {count}")
    records: list[dict] = []
    for index in range(count):
        start = offset
        record_id, offset = read_i32(decoded, offset)
        gear, offset = read_i32(decoded, offset)
        condition, offset = read_i32(decoded, offset)
        anim_list, offset = read_i32_list(decoded, offset, context=f"action[{index}].anim_list")
        fancy_id, offset = read_i32(decoded, offset)
        checks, offset = read_i32_list(decoded, offset, context=f"action[{index}].spmove_check_ids")
        speed_x, offset = read_i32(decoded, offset)
        speed_y, offset = read_i32(decoded, offset)
        records.append(
            {
                "record_index": index,
                "id": record_id,
                "gear": gear,
                "condition": condition,
                "anim_list": anim_list,
                "fancy_id": fancy_id,
                "spmove_check_ids": checks,
                "speed_fix_rate_xnumber_raw": [speed_x, speed_y],
                "source_offset": start,
                "source_bytes": offset - start,
            }
        )
    if offset != len(decoded):
        raise ValueError(f"action table has {len(decoded) - offset} trailing bytes")
    return records


def parse_config_table(decoded: bytes) -> list[dict]:
    """Parse SpmoveConfigConfigItem records.

    The serialized order is id, enable, logicId, childSpmoveIds, level, odds,
    param, buffId, one-byte IsBuffId, order.  `param_Xnumber` is a runtime
    field and is not serialized in the recovered blob; it is kept as an
    explicit derivation boundary instead of being guessed here.
    """
    count, offset = read_u32(decoded, 0)
    if count > 100_000:
        raise ValueError(f"invalid config record count {count}")
    records: list[dict] = []
    for index in range(count):
        start = offset
        record_id, offset = read_i32(decoded, offset)
        enable, offset = read_i32(decoded, offset)
        logic_id, offset = read_i32(decoded, offset)
        child_ids, offset = read_i32_list(decoded, offset, context=f"config[{index}].childSpmoveIds")
        level, offset = read_i32(decoded, offset)
        odds, offset = read_i32(decoded, offset)
        params, offset = read_i32_list(decoded, offset, context=f"config[{index}].param")
        buff_id, offset = read_i32(decoded, offset)
        if offset >= len(decoded):
            raise ValueError(f"config[{index}].IsBuffId is truncated")
        is_buff_id = bool(decoded[offset])
        offset += 1
        order, offset = read_i32(decoded, offset)
        records.append(
            {
                "record_index": index,
                "id": record_id,
                "enable": enable,
                "logic_id": logic_id,
                "child_spmove_ids": child_ids,
                "level": level,
                "odds": odds,
                "param_raw": params,
                "buff_id": buff_id,
                "is_buff_id": is_buff_id,
                "order": order,
                "param_xnumber_derivation": "runtime_field_not_serialized",
                "source_offset": start,
                "source_bytes": offset - start,
            }
        )
    if offset != len(decoded):
        raise ValueError(f"config table has {len(decoded) - offset} trailing bytes")
    return records


def decode_entry(archive: zipfile.ZipFile, path: str, parser) -> dict:
    compressed = archive.read(path)
    decoded = decode_lz4_raw(compressed)
    records = parser(decoded)
    return {
        "path": path,
        "compressed_bytes": len(compressed),
        "compressed_sha256": sha256(compressed),
        "decoded_bytes": len(decoded),
        "decoded_sha256": sha256(decoded),
        "record_count": len(records),
        "records": records,
    }


def load_source(source: dict, *, include_records: bool) -> dict:
    archive_path: Path = source["archive"]
    result = {
        "source_id": source["source_id"],
        "archive": str(archive_path),
        "relation": source["relation"],
        "archive_present": archive_path.is_file(),
    }
    if not archive_path.is_file():
        return result
    result["archive_bytes"] = archive_path.stat().st_size
    result["archive_sha256"] = sha256(archive_path.read_bytes())
    with zipfile.ZipFile(archive_path) as archive:
        action = decode_entry(archive, source["action_path"], parse_action_table)
        config = decode_entry(archive, source["config_path"], parse_config_table)
    if not include_records:
        action.pop("records")
        config.pop("records")
    result["action"] = action
    result["config"] = config
    return result


def main() -> int:
    canonical = load_source(SOURCES[0], include_records=True)
    candidate = load_source(SOURCES[1], include_records=False)
    report = {
        "schema_version": "football.recovery.spmove.normalized.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixed_point": {"name": "XNumber", "one_raw": 1024},
        "compression": {
            "codec": "LZ4 raw block",
            "decoder": "Tools/decode_lz4_raw.py",
            "byte_exact_against_v0_2_pairs": "verified_separately",
        },
        "semantic_status": "record_schema_confirmed_velocity_semantics_unresolved",
        "canonical_source": canonical,
        "separate_candidate_source": candidate,
        "confirmed": [
            "spmoveactiondata raw LZ4 block decodes to 48 records",
            "SpmoveActionDataConfigItem field layout and variable lists are byte-exact",
            "spmoveconfig raw LZ4 block decodes to 292 canonical records",
            "SpmoveConfigConfigItem serialized field layout and one-byte IsBuffId are byte-exact",
            "speed_fix_rate values are XNumber raw pairs",
            "param_Xnumber is a runtime field absent from the serialized blob",
        ],
        "unknown": [
            "spmoveInUseData VHor modifier",
            "spmoveInUseData VVer modifier",
            "GetVHor/GetVVer selection and interpolation semantics",
            "GetKickVelocity final physical composition",
            "mapping from spmove logicId/param_raw to those modifiers",
        ],
        "runtime_rule": "Do not use these records to admit BALL_CONTACT.velocity until the remaining selection semantics are proven.",
    }
    output = ROOT / "Recovery" / "Normalized" / "spmove_normalized.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        "SPMOVE_NORMALIZE: GREEN "
        f"canonical_action={canonical.get('action', {}).get('record_count', 0)} "
        f"canonical_config={canonical.get('config', {}).get('record_count', 0)} "
        f"output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
