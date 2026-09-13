"""Regenerate bounded support disassembly for GetShootSpeedVRate recovery.

Reads the preserved canonical ARM64 binary and Il2CppDumper script metadata.
Output remains under .local until reviewed and explicitly published.
"""
from __future__ import annotations

from pathlib import Path

import disassemble_shoot_helpers as base


def main() -> int:
    base.DEFAULT_TARGETS = (
        base.Target("xnumber_div_int", 0x1B6B37C, 0x200),
        base.Target("xrandom_next_int", 0x1929D88, 0x500),
    )
    base.MAX_ADJACENT_CALLEES = 0
    base.OUTPUT = (
        base.ROOT
        / ".local"
        / "recovery-output"
        / "shoot_speed_v_rate_support_disassembly.txt"
    )
    result = base.main()
    if result == 0:
        lines = [line.rstrip() for line in base.OUTPUT.read_text(encoding="utf-8").splitlines()]
        base.OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
