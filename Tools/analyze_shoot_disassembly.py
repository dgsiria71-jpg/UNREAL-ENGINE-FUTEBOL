"""Create a bounded, reviewable trace from the saved ARM64 shoot disassembly.

This tool extracts control-flow facts only. It does not decompile arithmetic,
execute Android code, or change the unresolved physics gate.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "disassembly_shoot.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "native_static_trace.json"

SECTION_RE = re.compile(
    r"^###\s+(?P<name>[A-Za-z0-9_]+)\s+"
    r"(?P<start>[0-9A-Fa-f]+)-(?P<end>[0-9A-Fa-f]+)\s*$"
)
INSN_RE = re.compile(
    r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<mnemonic>[A-Za-z0-9.]+)"
    r"(?:\s+(?P<operands>.*?))?\s*$"
)
CALL_RE = re.compile(r"^#?(0x[0-9A-Fa-f]+)$")
MASK_RE = re.compile(r"#(0x[0-9A-Fa-f]+)")


def parse() -> list[dict]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)
    sections: list[dict] = []
    current: dict | None = None
    for raw in INPUT.read_text(encoding="utf-8").splitlines():
        match = SECTION_RE.match(raw.strip())
        if match:
            current = {
                "name": match.group("name"),
                "start": "0x" + match.group("start").upper(),
                "end": "0x" + match.group("end").upper(),
                "_calls": Counter(),
                "_masks": Counter(),
                "_branches": Counter(),
                "_memory_offsets": Counter(),
                "_instruction_count": 0,
            }
            sections.append(current)
            continue
        if current is None:
            continue
        instruction = INSN_RE.match(raw.strip())
        if not instruction:
            continue
        current["_instruction_count"] += 1
        mnemonic = instruction.group("mnemonic")
        operands = instruction.group("operands") or ""
        if mnemonic == "bl":
            target = CALL_RE.match(operands.strip())
            if target:
                current["_calls"][target.group(1).upper()] += 1
        if mnemonic.startswith("b"):
            current["_branches"][mnemonic] += 1
        if mnemonic in {"tst", "and", "ubfx", "bfxil", "bfi"}:
            for mask in MASK_RE.findall(operands):
                current["_masks"][mask.upper()] += 1
        for offset in re.findall(r"#(0x[0-9A-Fa-f]+)", operands):
            if "[" in operands:
                current["_memory_offsets"][offset.upper()] += 1

    result: list[dict] = []
    for section in sections:
        calls = section.pop("_calls")
        masks = section.pop("_masks")
        branches = section.pop("_branches")
        offsets = section.pop("_memory_offsets")
        instruction_count = section.pop("_instruction_count")
        entry = {
            **section,
            "instruction_count": instruction_count,
            "call_targets": [
                {"target": target, "count": count}
                for target, count in sorted(calls.items())
            ],
            "literal_mask_operands": [
                {"mask": mask, "count": count}
                for mask, count in sorted(masks.items())
            ],
            "branch_mnemonics": [
                {"mnemonic": mnemonic, "count": count}
                for mnemonic, count in sorted(branches.items())
            ],
            "memory_offsets": [
                {"offset": offset, "count": count}
                for offset, count in sorted(offsets.items())
            ],
        }
        result.append(entry)
    return result


def main() -> int:
    sections = parse()
    by_name = {item["name"]: item for item in sections}
    expected = {
        "GetVHor": ("0x016E6A80", "0x016E84A4"),
        "GetVVer": ("0x016E84A4", "0x016EA55C"),
        "GetKickVelocity": ("0x016EBAD8", "0x016EBF14"),
    }
    errors: list[str] = []
    for name, (start, end) in expected.items():
        item = by_name.get(name)
        if item is None:
            errors.append("missing section " + name)
            continue
        if item["start"] != start or item["end"] != end:
            errors.append(name + " span changed")
    kick = by_name.get("GetKickVelocity", {})
    kick_targets = {item["target"] for item in kick.get("call_targets", [])}
    if "0X16E6A80" not in kick_targets or "0X16E84A4" not in kick_targets:
        errors.append("GetKickVelocity no longer shows both helper calls")
    if errors:
        for error in errors:
            print("NATIVE_TRACE_ERROR: " + error)
        return 1
    report = {
        "schema_version": "football.recovery.native_static_trace.v1",
        "source": ".local/il2cpp/disassembly_shoot.txt",
        "source_scope": "canonical Android ARM64 libil2cpp.so",
        "analysis_status": "control_flow_and_literal_masks_only",
        "behavior_validated": False,
        "method_spans": sections,
        "confirmed_interpretation": [
            "GetKickVelocity contains direct calls to GetVHor and GetVVer",
            "literal masks are recorded without assigning equation semantics",
            "branch and memory-offset lists are hints for manual review only",
        ],
        "unknown": [
            "arithmetic equations",
            "config record selection",
            "spmoveInUseData producer semantics",
            "coordinate basis and units",
            "runtime behavior on representative inputs",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "NATIVE_TRACE: GREEN "
        f"sections={len(sections)} output={OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
