"""Extract the minimal IL2CPP metadata facts used by shoot V-rate recovery."""
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
        "dump.cs": require_identity(dump, "dump.cs"),
        "script.json": require_identity(script, "script.json"),
        "global-metadata.dat": require_identity(metadata, "global-metadata.dat"),
        "libil2cpp.so": require_identity(binary, "libil2cpp.so"),
    }
    text = dump.read_text(encoding="utf-8-sig")
    required = (
        "public XNumber GetShootVerRate(XGoalTypeEnum goal_child) { }",
        "public XNumber GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) { }",
        "public class AIParameterConfig : XBaseLocalSetting<AIParameterConfig> // TypeDefIndex: 8907",
        "public int disArea; // 0x80",
        "public static readonly XNumber zero; // 0x8",
        "public static readonly XNumber one; // 0xC",
        "public static readonly XNumber hundred; // 0x4C",
        "public static XNumber op_Division(XNumber lhs, int rhs) { }",
        "private static int NextInt(int n) { }",
        "public static XNumber Range(XNumber min, XNumber max) { }",
    )
    missing = [line for line in required if line not in text]
    if missing:
        raise ValueError(f"dump.cs anchors missing: {missing!r}")

    return f"""FOOTBALL SHOOT SPEED V-RATE IL2CPP METADATA EXCERPT
POLICY: exact textual facts copied from canonical Il2CppDumper dump.cs; no runtime behavior is inferred from names alone
LIBIL2CPP_SHA256: {identities['libil2cpp.so']}
GLOBAL_METADATA_SHA256: {identities['global-metadata.dat']}
DUMP_CS_SHA256: {identities['dump.cs']}
SCRIPT_JSON_SHA256: {identities['script.json']}

### PlayerProperty methods
// RVA: 0x1968C34 Offset: 0x1968C34 VA: 0x1968C34
public XNumber GetShootVerRate(XGoalTypeEnum goal_child) {{ }}
// RVA: 0x1968E24 Offset: 0x1968E24 VA: 0x1968E24
public XNumber GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) {{ }}

### AIParameterConfig field
public class AIParameterConfig : XBaseLocalSetting<AIParameterConfig> // TypeDefIndex: 8907
public int disArea; // 0x80

### XNumber static fields and division overload
public static readonly XNumber zero; // 0x8
public static readonly XNumber one; // 0xC
public static readonly XNumber hundred; // 0x4C
// RVA: 0x1B6B37C Offset: 0x1B6B37C VA: 0x1B6B37C
public static XNumber op_Division(XNumber lhs, int rhs) {{ }}

### XRandom methods
// RVA: 0x1929D88 Offset: 0x1929D88 VA: 0x1929D88
private static int NextInt(int n) {{ }}
// RVA: 0x192A0C4 Offset: 0x192A0C4 VA: 0x192A0C4
public static XNumber Range(XNumber min, XNumber max) {{ }}
"""


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=root)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    dump = source_root / ".local" / "tools" / "Il2CppDumper" / "dump.cs"
    script = source_root / ".local" / "tools" / "Il2CppDumper" / "script.json"
    metadata = source_root / ".local" / "il2cpp" / "global-metadata.dat"
    binary = source_root / ".local" / "il2cpp" / "libil2cpp.so"
    output = root / ".local" / "recovery-output" / "shoot_speed_v_rate_metadata.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(dump, script, metadata, binary), encoding="utf-8", newline="\n")
    print(f"SHOOT_SPEED_V_RATE_METADATA: GREEN output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
