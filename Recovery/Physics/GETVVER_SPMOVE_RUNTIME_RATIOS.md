# GetVVer spmove runtime ratios

This increment joins four previously validated artifacts: the `GetVVer` modifier accesses, spmove runtime property records, the open-all collected inventory, and `calSpmoveInUse` flag writes.

For both surviving new-path modifiers, normalized levels 1 through 5 contain raw `param[2]` values `900, 800, 700, 600, 500`. These are fixed-point scale factors over 1024. `0x3FC` is guarded by `ShootLongKick`; `0x41A` is guarded by `shootPush`. GetVVer additionally requires a base-vector magnitude of at least one raw unit and a non-null ratio list.

Selection does not use config level, order, or odds directly. The recovered manager selects the greatest signed child ID among the eligible runtime inventory, then resolves that selected config. In the persisted open-all fixture, `0x3FC` selects child `102005` and `0x41A` selects child `105005`, so both use raw factor `500` (0.48828125). This open-all result is a deterministic recovery fixture; it is not a claim that every player/action owns the level-5 entries at runtime.

When both flags are active, native code applies `0x3FC` followed by `0x41A`, scaling every vector component with fixed-point rounding after each multiplication.

Artifacts:

- `Tools/analyze_getvver_spmove_runtime_ratios.py`
- `Recovery/Normalized/getvver_spmove_runtime_ratios.json`
- `Tests/test_getvver_spmove_runtime_ratios.py`

The next gate is representative differential vectors for no modifier, each modifier independently, and both modifiers, using explicit eligible inventories. Whole-function GetVVer equivalence and Physics v0.3 remain blocked.
