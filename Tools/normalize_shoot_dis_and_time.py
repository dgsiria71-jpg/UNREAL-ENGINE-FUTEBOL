"""Normalize the canonical config-5800 shootDisAndTime table from Physics v0.2."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = Path(r"C:\Users\dg71\Downloads\FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip")
ENTRY = "FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2/01_SOURCE/decoded/shootspeed.bin"
PACK_SHA256 = "7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac"
SHOOTSPEED_SHA256 = "f437f83465a541bc85f07e1cab655afd59a2fb927233302a40a1d09b6355d0ad"
OUTPUT = ROOT / "Recovery" / "Normalized" / "shoot_dis_and_time_config_5800.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_i32(data: bytes, offset: int) -> tuple[int, int]:
    if offset + 4 > len(data):
        raise ValueError("truncated int32")
    return struct.unpack_from("<i", data, offset)[0], offset + 4


def read_i32_list(data: bytes, offset: int) -> tuple[list[int], int]:
    count, offset = read_i32(data, offset)
    if count < 0 or count > 100000:
        raise ValueError(f"invalid list count {count}")
    end = offset + count * 4
    if end > len(data):
        raise ValueError("truncated int32 list")
    return list(struct.unpack_from(f"<{count}i", data, offset)) if count else [], end


def parse(data: bytes) -> tuple[list[dict], int]:
    count, offset = read_i32(data, 0)
    if count < 0 or count > 100000:
        raise ValueError(f"invalid record count {count}")
    records = []
    for record_index in range(count):
        record_id, offset = read_i32(data, offset)
        identify, offset = read_i32(data, offset)
        for _ in range(8):
            _, offset = read_i32_list(data, offset)
        for _ in range(12):
            _, offset = read_i32(data, offset)
        _, offset = read_i32_list(data, offset)
        if offset >= len(data):
            raise ValueError(f"truncated bool at record {record_index}")
        use_new_method = bool(data[offset])
        offset += 1
        _, offset = read_i32(data, offset)
        y_speed_min_raw, offset = read_i32(data, offset)
        y_speed_max_raw, offset = read_i32_list(data, offset)
        for _ in range(4):
            _, offset = read_i32(data, offset)
        for _ in range(10):
            _, offset = read_i32_list(data, offset)
        outer_count, offset = read_i32(data, offset)
        if outer_count < 0 or outer_count > 100000:
            raise ValueError(f"invalid outer count {outer_count}")
        table = []
        for _ in range(outer_count):
            row, offset = read_i32_list(data, offset)
            table.append(row)
        records.append({
            "id": record_id,
            "identify": identify,
            "use_new_method": use_new_method,
            "y_speed_min_raw": y_speed_min_raw,
            "y_speed_max_raw": y_speed_max_raw,
            "shoot_dis_and_time_ms": table,
        })
    return records, offset


def normalize(pack: Path) -> dict:
    if hashlib.sha256(pack.read_bytes()).hexdigest() != PACK_SHA256:
        raise ValueError("Physics v0.2 pack SHA mismatch")
    with zipfile.ZipFile(pack) as archive:
        data = archive.read(ENTRY)
    data_sha = sha256_bytes(data)
    if data_sha != SHOOTSPEED_SHA256:
        raise ValueError(f"shootspeed SHA mismatch: {data_sha}")
    records, consumed = parse(data)
    if consumed != len(data) or len(records) != 28:
        raise ValueError(f"shootspeed parse mismatch: records={len(records)} consumed={consumed}/{len(data)}")
    matches = [record for record in records if record["id"] == 5800 and record["identify"] == 0]
    if len(matches) != 1:
        raise ValueError(f"expected one config 5800/0, got {len(matches)}")
    selected = matches[0]
    table = selected["shoot_dis_and_time_ms"]
    if len(table) <= 20 or len(table[20]) <= 25 or table[20][25] != 1327:
        raise ValueError("canonical config 5800 table anchor mismatch")
    return {
        "schema_version": "football.normalized.shoot_dis_and_time.v1",
        "source": {
            "archive_filename": pack.name,
            "archive_sha256": PACK_SHA256,
            "zip_entry": ENTRY,
            "decoded_bytes": len(data),
            "decoded_sha256": data_sha,
            "records": len(records),
            "bytes_consumed": consumed,
        },
        "config": selected,
        "confirmed_anchor": {
            "vhor_integer_index": 20,
            "distance_integer_index": 25,
            "table_milliseconds": 1327,
            "flight_time_raw": 1359,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--physics-pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = normalize(args.physics_pack.resolve())
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"SHOOT_DIS_AND_TIME_NORMALIZE: GREEN records={result['source']['records']} bytes={result['source']['bytes_consumed']} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
