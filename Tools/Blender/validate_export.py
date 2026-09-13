"""Read-only Blender export preflight for generic football player assets.

Neymar v1.9 remains a preserved fixture. This script validates an object
collection and does not start a Neymar production pass.
"""
from __future__ import annotations

try:
    import bpy  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Run this script inside Blender's Python environment") from exc


REQUIRED_COLLECTIONS = ("FootballPlayer", "FootballAnimation")


def main() -> int:
    missing = [name for name in REQUIRED_COLLECTIONS if bpy.data.collections.get(name) is None]
    if missing:
        print("BLENDER_PREFLIGHT_ERROR: missing collections: " + ", ".join(missing))
        return 1
    print("BLENDER_PREFLIGHT: GREEN; no asset mutation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
