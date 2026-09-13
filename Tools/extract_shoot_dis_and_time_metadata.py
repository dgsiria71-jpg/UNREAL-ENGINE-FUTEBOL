"""Extract minimal canonical IL2CPP metadata for shootDisAndTime recovery."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED = {
    "dump.cs": "4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe",
    "script.json": "d15222efc79ebfe50074f385c0f5e5af4960fb43c5cf55a383ea32cba34ae799",
    "global-metadata.dat": "92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e",
    "libil2cpp.so": "2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_identity(path: Path, key: str) -> str:
    actual = sha256(path)
    if actual != EXPECTED[key]:
        raise ValueError(f"{key} SHA mismatch: {actual}")
    return actual


def render(dump: Path, script: Path, metadata: Path, binary: Path) -> str:
    identities = {
        key: require_identity(path, key)
        for key, path in {
            "dump.cs": dump,
            "script.json": script,
            "global-metadata.dat": metadata,
            "libil2cpp.so": binary,
        }.items()
    }
    text = dump.read_text(encoding="utf-8-sig")
    required = (
        "public class ShootSpeedConfigItem // TypeDefIndex: 7953",
        "public XNumber ySpeedMin; // 0x98",
        "public List<XNumber> ySpeedMax; // 0xA0",
        "public List<List<int>> shootDisAndTime; // 0x108",
        "public static readonly XNumber zero; // 0x8",
        "public static readonly XNumber thousand; // 0x50",
        "public static XNumber op_Division(XNumber lhs, XNumber rhs) { }",
    )
    missing = [line for line in required if line not in text]
    if missing:
        raise ValueError(f"dump.cs anchors missing: {missing!r}")

    return f"""FOOTBALL SHOOT DIS AND TIME IL2CPP METADATA EXCERPT
POLICY: exact textual facts copied from canonical Il2CppDumper dump.cs; names do not prove behavior without ARM64 dataflow
LIBIL2CPP_SHA256: {identities['libil2cpp.so']}
GLOBAL_METADATA_SHA256: {identities['global-metadata.dat']}
DUMP_CS_SHA256: {identities['dump.cs']}
SCRIPT_JSON_SHA256: {identities['script.json']}

### ShootSpeedConfigItem
public class ShootSpeedConfigItem // TypeDefIndex: 7953
public XNumber ySpeedMin; // 0x98
public List<XNumber> ySpeedMax; // 0xA0
public List<List<int>> shootDisAndTime; // 0x108

### XNumber
public static readonly XNumber zero; // 0x8
public static readonly XNumber thousand; // 0x50
public static XNumber op_Division(XNumber lhs, XNumber rhs) {{ }}
"""


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "artifacts" / "native-recovery" / "20260913-163217-9cdb54d0" / "02_shoot_dis_and_time_metadata.txt",
    )
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render(
            source_root / ".local" / "tools" / "Il2CppDumper" / "dump.cs",
            source_root / ".local" / "tools" / "Il2CppDumper" / "script.json",
            source_root / ".local" / "il2cpp" / "global-metadata.dat",
            source_root / ".local" / "il2cpp" / "libil2cpp.so",
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(f"SHOOT_DIS_AND_TIME_METADATA: GREEN output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
