"""Anchor the native spmove inventory/cache collector without overclaiming behavior.

The collector is an Android ARM64 listing. This analyzer records only
instruction-level facts safe to carry into the normalized runtime: cache
invalidation, open-all versus player-inventory branches, and the two
config-list construction paths. It deliberately leaves collection,
eligibility, and runtime object semantics unresolved.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".local" / "il2cpp" / "spmove_inventory_collector_disassembly.txt"
OUTPUT = ROOT / "Recovery" / "Normalized" / "spmove_inventory_collector_static_trace.json"
SCRIPT = ROOT / ".local" / "tools" / "Il2CppDumper" / "script.json"
DUMP = ROOT / ".local" / "tools" / "Il2CppDumper" / "dump.cs"
LINE_RE = re.compile(r"^(?P<address>[0-9A-Fa-f]+):\s+(?P<instruction>.*)$")

def parse() -> list[dict[str, str]]:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)
    entries = []
    for raw in INPUT.read_text(encoding="utf-8").splitlines():
        match = LINE_RE.match(raw.strip())
        if match:
            entries.append({"address": "0x" + match.group("address").upper(),
                            "instruction": match.group("instruction").strip()})
    return entries

def require(entries, address: str, fragment: str):
    for item in entries:
        if item["address"].upper() == address.upper() and fragment.lower() in item["instruction"].lower():
            return item
    actual = [item for item in entries if item["address"].upper() == address.upper()]
    raise ValueError(f"anchor {address} missing {fragment!r}; actual={actual!r}")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def helper_symbols() -> dict[str, list[str]]:
    if not SCRIPT.is_file():
        return {}
    methods = json.loads(SCRIPT.read_text(encoding="utf-8"))["ScriptMethod"]
    wanted = {
        "0x2C6A4F8": ["Dictionary<int, List<SpmoveIDCombine>>$$ContainsKey", "Dictionary<int, SpmoveConfigConfigItem>$$ContainsKey"],
        "0x2F19438": ["List<int>$$GetEnumerator"],
        "0x2F26798": ["List<SpmoveIDCombine>$$Add"],
        "0x2C6A284": ["Dictionary<int, List<SpmoveIDCombine>>$$Add"],
        "0x1E34BE4": ["ModuleSingleton<SpmoveModule>$$get_Instance"],
        "0x1449858": ["SpmoveModule$$GetConfig"],
        "0x2F25B64": ["List<SpmoveIDCombine>$$.ctor"],
        "0x2C6A188": ["Dictionary<int, List<SpmoveIDCombine>>$$get_Item"],
    }
    found = {}
    for address, names in wanted.items():
        addr = int(address, 16)
        available = {item.get("Name") for item in methods if item.get("Address") == addr}
        found[address] = [name for name in names if any(name in candidate for candidate in available)]
    return found

def main() -> int:
    entries = parse()
    anchor_specs = {
        "manager_cache_flag": ("0x01B71B20", "ldrb     w19, [x21, #0x29]"),
        "open_all_compare": ("0x01B71B5C", "ldrb     w8, [x21, #0x28]"),
        "cache_hit_branch": ("0x01B71B7C", "cbz      w19, #0x1b71b88"),
        "cache_clear": ("0x01B71B8C", "ldr      x0, [x25, #0x10]!"),
        "cache_mark_initialized": ("0x01B71B94", "strb     w8, [x25, #0x19]"),
        "all_config_branch": ("0x01B71BB4", "ldr      w8, [x21, #0x38]"),
        "config_logic_id": ("0x01B71C60", "ldr      w1, [x19, #0x20]"),
        "config_children_list": ("0x01B71CBC", "ldr      x0, [x19, #0x28]"),
        "child_logic_id": ("0x01B71D40", "ldr      w1, [x21, #0x20]"),
        "child_id_store": ("0x01B71DD4", "str      w20, [x22, #0x10]"),
        "parent_id_load": ("0x01B71DD8", "ldr      w8, [x19, #0x18]"),
        "child_parent_store": ("0x01B71DDC", "str      w8, [x22, #0x14]"),
        "self_id_load": ("0x01B71E9C", "ldr      w8, [x19, #0x18]"),
        "self_id_store": ("0x01B71EA0", "str      w8, [x21, #0x10]"),
        "player_inventory_field": ("0x01B71FA8", "ldr      x0, [x21, #0x30]"),
        "player_inventory_logic": ("0x01B72028", "ldr      w1, [x19, #0x20]"),
        "inventory_child_logic_id": ("0x01B72100", "ldr      w1, [x21, #0x20]"),
        "inventory_child_id_store": ("0x01B721A4", "str      w20, [x22, #0x10]"),
        "inventory_parent_id_load": ("0x01B721A8", "ldr      w8, [x19, #0x18]"),
        "inventory_parent_store": ("0x01B721AC", "str      w8, [x22, #0x14]"),
        "inventory_self_id_load": ("0x01B72278", "ldr      w8, [x19, #0x18]"),
        "inventory_self_id_store": ("0x01B7227C", "str      w8, [x21, #0x10]"),
        "return_dictionary": ("0x01B7235C", "ldr      x0, [x25]"),
    }
    errors = []
    anchors = {}
    for name, (address, fragment) in anchor_specs.items():
        try:
            anchors[name] = require(entries, address, fragment)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print("SPMOVE_INVENTORY_TRACE_ERROR: " + error)
        return 1
    binary = ROOT / ".local" / "il2cpp" / "libil2cpp.so"
    symbols = helper_symbols()
    dump_text = DUMP.read_text(encoding="utf-8-sig") if DUMP.is_file() else ""
    layout_markers = {
        "config_id": "public int id; // 0x18",
        "config_logic_id": "public int logicId; // 0x20",
        "config_children": "public List<int> childSpmoveIds; // 0x28",
        "combine_child_id": "public int childId; // 0x10",
        "combine_father_id": "public int fatherId; // 0x14",
    }
    missing_layout = [name for name, marker in layout_markers.items() if marker not in dump_text]
    if missing_layout:
        for name in missing_layout:
            print("SPMOVE_INVENTORY_TRACE_ERROR: missing dump.cs layout " + name)
        return 1
    report = {
        "schema_version": "football.recovery.spmove_inventory_collector_static_trace.v1",
        "source": ".local/il2cpp/spmove_inventory_collector_disassembly.txt",
        "source_sha256": sha256(INPUT),
        "binary": ".local/il2cpp/libil2cpp.so",
        "binary_sha256": sha256(binary) if binary.is_file() else None,
        "source_scope": "canonical Android ARM64 XSpmoveManager::getSpmoveIdDict",
        "analysis_status": "inventory_collection_shape_static_confirmed",
        "behavior_validated": False,
        "anchors": anchors,
        "script_json": ".local/tools/Il2CppDumper/script.json",
        "script_json_sha256": sha256(SCRIPT) if SCRIPT.is_file() else None,
        "dump_cs": ".local/tools/Il2CppDumper/dump.cs",
        "dump_cs_sha256": sha256(DUMP) if DUMP.is_file() else None,
        "layout_evidence": layout_markers,
        "helper_symbols": symbols,
        "helper_symbol_status": "metadata_names_only",
        "confirmed_data_flow": [
            {"operation": "cache_guard",
             "flow": "cached initialized flag +0x29 and open-all state +0x28 guard reuse; changed state clears dictionary +0x10 and marks initialized",
             "evidence": ["0x01B71B20", "0x01B71B5C", "0x01B71B7C", "0x01B71B8C", "0x01B71B94"]},
            {"operation": "all_config_path",
             "flow": "open-all or matchrule_skill==1 enumerates configs; each root adds (root.id, 0) to root.logicId and each listed child adds (childId, root.id) to the child config logicId bucket",
             "evidence": ["0x01B71BB4", "0x01B71C60", "0x01B71CC0", "0x01B71D40", "0x01B71DD4", "0x01B71DD8", "0x01B71DDC", "0x01B71E9C", "0x01B71EA0"]},
            {"operation": "player_inventory_path",
             "flow": "matchrule_skill==-1 reads manager spmoveIds +0x30; missing roots are skipped, while resolved roots use the same self/child expansion shape",
             "evidence": ["0x01B71F98", "0x01B71FA8", "0x01B72018", "0x01B72028", "0x01B72100", "0x01B721A4", "0x01B721A8", "0x01B721AC", "0x01B72278", "0x01B7227C"]},
            {"operation": "return",
             "flow": "returns manager dictionary object after population; null/error exits are present",
             "evidence": ["0x01B7235C"]},
        ],
        "normalized_boundary": {
            "manager_fields": {"dictionary": "+0x10", "config_list": "+0x18", "open_all": "+0x28",
                               "inventory_initialized": "+0x29", "spmove_ids": "+0x30",
                               "matchrule_skill": "+0x38"},
            "config_fields": {"id": "+0x18", "logic_id": "+0x20", "child_spmove_ids": "+0x28"},
            "entry_fields": {"child_id": "+0x10", "father_id": "+0x14"},
            "status": "collection_shape_confirmed_runtime_source_unresolved",
            "safe_action": "implement the engine-independent collection shape while keeping player inventory source and later eligibility/RNG explicit",
        },
        "unknown": [
            "exact managed dictionary/list allocation and exception semantics",
            "upstream source and lifetime of player spmoveIds at runtime",
            "eligibility, ownership, level, odds, and RNG filters after inventory collection",
            "cache lifetime and invalidation outside this method",
            "representative runtime behavior on real player inventories",
        ],
        "physics_gate": "blocked",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"SPMOVE_INVENTORY_TRACE: GREEN anchors={len(anchors)} output={OUTPUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
