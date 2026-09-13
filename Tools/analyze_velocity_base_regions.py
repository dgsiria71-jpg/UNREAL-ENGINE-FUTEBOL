"""Bind GetVHor/GetVVer old/new base regions to recovered config fields.

This is a static ARM64/layout trace. It confirms which serialized field families
feed each path, but it does not claim the arithmetic equations or runtime output.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISASSEMBLY = ROOT / ".local" / "il2cpp" / "disassembly_shoot.txt"
DUMP_CS = ROOT / ".local" / "tools" / "Il2CppDumper" / "dump.cs"
OUTPUT = ROOT / "Recovery" / "Normalized" / "velocity_base_regions_static_trace.json"
HEADER_RE = re.compile(r"^###\s+(?P<name>.+?)\s+(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$")
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")
FIELD_RE = re.compile(r"^\s*public\s+.+?\s+(?P<name>[A-Za-z0-9_]+);\s*//\s*(?P<offset>0x[0-9A-Fa-f]+)\s*$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_instructions() -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    section: str | None = None
    for raw in DISASSEMBLY.read_text(encoding="utf-8").splitlines():
        header = HEADER_RE.match(raw.strip())
        if header:
            section = header.group("name")
            continue
        line = LINE_RE.match(raw.strip())
        if section and line:
            result[(section, "0x" + line.group("address").upper())] = line.group("instruction").strip()
    return result


def parse_config_layout() -> dict[str, str]:
    text = DUMP_CS.read_text(encoding="utf-8")
    start = text.index("public class ShootSpeedConfigItem //")
    end = text.index("\n\t// Methods", start)
    fields: dict[str, str] = {}
    for raw in text[start:end].splitlines():
        match = FIELD_RE.match(raw)
        if match:
            fields[match.group("name")] = match.group("offset").upper().replace("X", "x")
    return fields


def main() -> int:
    instructions = parse_instructions()
    layout = parse_config_layout()
    anchors = {
        "vhor_use_new_method": ("GetVHor", "0x016E6B64", "ldrb     w8, [x21, #0x90]", "useNewMethod"),
        "vhor_zero_selects_old": ("GetVHor", "0x016E6B70", "cbz      w8, #0x16e6c34", None),
        "vhor_new_energy_map": ("GetVHor", "0x016E6B74", "ldr      x22, [x21, #0xb8]", "energyMapNew"),
        "vhor_old_energy_map": ("GetVHor", "0x016E6C34", "ldr      x22, [x21, #0x18]", "Flist_vHor"),
        "vhor_new_speed_map": ("GetVHor", "0x016E6D3C", "ldr      x23, [x21, #0xc0]", "vHorMapNew"),
        "vhor_new_strength_map": ("GetVHor", "0x016E6E20", "ldr      x26, [x21, #0xc8]", "shootStrongMapNew"),
        "vhor_new_rate_map": ("GetVHor", "0x016E6F48", "ldr      x20, [x21, #0xd0]", "vHorRateNew"),
        "vhor_old_speed_map": ("GetVHor", "0x016E7310", "ldr      x20, [x21, #0x20]", "vHorList"),
        "vhor_old_speed_scalar": ("GetVHor", "0x016E745C", "ldr      w22, [x21, #0x74]", "speed_vHor"),
        "vver_use_new_method": ("GetVVer", "0x016E8564", "ldrb     w8, [x22, #0x90]", "useNewMethod"),
        "vver_zero_selects_old": ("GetVVer", "0x016E856C", "cbz      w8, #0x16e9fcc", None),
        "vver_new_distance_map": ("GetVVer", "0x016E8630", "ldr      x20, [x22, #0xe8]", "shootDisMap"),
        "vver_new_output_energy_map": ("GetVVer", "0x016E8768", "ldr      x26, [x22, #0x100]", "outEnergyMaxMap"),
        "vver_new_y_speed_max": ("GetVVer", "0x016E8830", "ldr      x8, [x22, #0xa0]", "ySpeedMax"),
        "vver_new_energy_map": ("GetVVer", "0x016E8858", "ldr      x20, [x22, #0xb8]", "energyMapNew"),
        "vver_new_point_up_map": ("GetVVer", "0x016E8B2C", "ldr      x26, [x22, #0xf8]", "shootPointHUpMap"),
        "vver_new_point_down_map": ("GetVVer", "0x016E8D08", "ldr      x21, [x22, #0xf0]", "shootPointHDownMap"),
        "vver_new_property_map": ("GetVVer", "0x016E8DF4", "ldr      x19, [x22, #0xd8]", "shootPropertyMapNew"),
        "vver_new_tolerance_map": ("GetVVer", "0x016E8F08", "ldr      x27, [x22, #0xe0]", "energyToleranceMap"),
        "vver_new_protect_energy": ("GetVVer", "0x016E8FBC", "ldr      w19, [x22, #0x94]", "energyNeedProtect"),
        "vver_new_point_range": ("GetVVer", "0x016E91E4", "ldp      w21, w23, [x22, #0xb0]", "shootPointH"),
        "vver_new_distance_time": ("GetVVer", "0x016E92E4", "ldr      x8, [x22, #0x108]", "shootDisAndTime"),
        "vver_new_y_speed_min": ("GetVVer", "0x016E9CB4", "ldr      w19, [x22, #0x98]", "ySpeedMin"),
        "vver_old_force_map": ("GetVVer", "0x016E9FCC", "ldr      x20, [x22, #0x28]", "Flist_vVer"),
        "vver_old_speed_map": ("GetVVer", "0x016EA0E4", "ldr      x24, [x22, #0x30]", "vVerList"),
        "vver_old_speed_scalar": ("GetVVer", "0x016EA318", "ldr      w3, [x22, #0x80]", "speed_vVer"),
    }
    errors: list[str] = []
    bound: dict[str, dict[str, str | None]] = {}
    for name, (section, address, expected, field) in anchors.items():
        actual = instructions.get((section, address))
        if actual != expected:
            errors.append(f"{name}: expected {expected!r}, got {actual!r}")
        if field and (layout.get(field) or "").lower() not in expected.lower():
            errors.append(f"{name}: dump layout {field}={layout.get(field)!r} does not match instruction")
        bound[name] = {"method": section, "address": address, "instruction": actual, "config_field": field,
                       "field_offset": layout.get(field) if field else None}
    if errors:
        for error in errors:
            print("VELOCITY_BASE_TRACE_ERROR: " + error)
        return 1

    report = {
        "schema_version": "football.recovery.velocity_base_regions_static_trace.v1",
        "source": ".local/il2cpp/disassembly_shoot.txt",
        "source_sha256": sha256(DISASSEMBLY),
        "dump_cs": ".local/tools/Il2CppDumper/dump.cs",
        "dump_cs_sha256": sha256(DUMP_CS),
        "analysis_status": "old_new_config_path_split_static_confirmed",
        "behavior_validated": False,
        "method_spans": {
            "GetVHor": {"start": "0x016E6A80", "end": "0x016E84A4"},
            "GetVVer": {"start": "0x016E84A4", "end": "0x016EA55C"},
        },
        "anchors": bound,
        "confirmed_paths": {
            "GetVHor": {
                "selector": "ShootSpeedConfigItem.useNewMethod +0x90",
                "new_when_nonzero_fields": ["energyMapNew", "vHorMapNew", "shootStrongMapNew", "vHorRateNew"],
                "old_when_zero_fields": ["Flist_vHor", "vHorList", "speed_vHor"],
            },
            "GetVVer": {
                "selector": "ShootSpeedConfigItem.useNewMethod +0x90",
                "new_when_nonzero_fields": ["shootDisMap", "outEnergyMaxMap", "ySpeedMax", "energyMapNew",
                    "shootPointHUpMap", "shootPointHDownMap", "shootPropertyMapNew", "energyToleranceMap",
                    "energyNeedProtect", "shootPointH", "shootDisAndTime", "ySpeedMin"],
                "old_when_zero_fields": ["Flist_vVer", "vVerList", "speed_vVer"],
            },
        },
        "confirmed_interpretation": [
            "both methods branch on the same useNewMethod field at +0x90",
            "a zero selector enters the legacy list path in both methods",
            "a nonzero selector enters the recovered New-suffixed/map-driven path in both methods",
            "field-family membership is proven statically; equations and output behavior remain unresolved",
        ],
        "unknown": [
            "complete interpolation and clamp sequence in each path",
            "full units and coordinate basis",
            "runtime representative behavior and exceptional managed paths",
            "final spmove modifier join, GetKickVelocity composition and BALL_CONTACT velocity",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"VELOCITY_BASE_TRACE: GREEN anchors={len(bound)} output={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())