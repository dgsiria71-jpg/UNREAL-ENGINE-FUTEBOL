# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**. Physics v0.3 is **BLOCKED**. GitHub `main` is canonical.

## Branch and HEAD

- working branch: `codex/getvver-spmove-runtime-ratios`
- canonical merged baseline: `9e31b7908dfd91d0b99b81fd3b82e75e3f250f3d` (PR #15)
- branch base: GitHub `main` commit `9e31b7908dfd91d0b99b81fd3b82e75e3f250f3d`
- canonical build: `football-dream-be-a-pro-1-221-5`
- build `1-226-19`: isolated and not consumed
- Neymar v1.9: preserved and paused

The canonical root checkout still contains exactly four protected user modifications and they were not staged or rewritten:

- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`
- `docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `docs/PROJECT_SOURCE_OF_TRUTH.md`

## Last GREEN tests

- focused Python: `9/9` GREEN
- complete Python discovery: `115` run, `110` GREEN, `5` optional skips, zero failures
- C++ CTest Release/MSVC: `7/7` GREEN
- new `PropertyLookupTest`: GREEN
- property lookup static analyzer: GREEN; gate remains BLOCKED
- GetVVer new-path analyzer: GREEN after canonical-LF SHA validation fix on Windows

PR #15 final run #205 / `34805749973` and post-merge main run #206 / `34805792714` completed **SUCCESS**.

## Current task

Join the validated spmove activation, selection, and parameter traces to bind the runtime ratio matrix for the surviving `0x3FC` and `0x41A` GetVVer modifiers.

## Files changed by the current increment

- `Tools/analyze_getvver_spmove_runtime_ratios.py`
- `Tests/test_getvver_spmove_runtime_ratios.py`
- `Recovery/Normalized/getvver_spmove_runtime_ratios.json`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`
- `Recovery/Normalized/recovery_manifest.json`
- `Recovery/Physics/GETVVER_SPMOVE_RUNTIME_RATIOS.md`
- `_CHECKPOINTS/CURRENT.md`

## CONFIRMED

- upload `20260914-010116-072c3bfd` identified exact ScriptMethod boundaries:
  - `0x01967D38..0x01967DC4` = `PlayerProperty.GetPropertyValue(PropertyType, SpmoveLogicId)`
  - `0x01B718D8..0x01B71958` = `XProperty.XPropertyManager.GetPropertyValue(PropertyType)`
- the corrected metadata upload is `20260914-011043-a18f1783`, 88,994 bytes, canonical LF SHA-256 `7053c4a888ac29355b83cea7ecc71f582a71fc2e3e6731f146a9ee569dcb6784`.
- `PlayerProperty.GetPropertyValue` selects the spmove buffer path only when an enabled config exists and its logic check passes; otherwise it reads the base property manager.
- selected spmove buffer property id is loaded from the config at `+0x40`.
- `XPropertyManager.GetPropertyValue` indexes its entry array and returns the raw `XNumber` at entry `+0x14`; invalid storage follows managed exception paths.
- `getShootPropertyWithSpmove` falls back to the base property when the spmove-aware raw value is `<= 0`.
- GetShootProperty threshold fields are:
  - `ShootConfig +0x24` = `shootAirBallHeighLimit`
  - `ShootConfig +0x148` = `dis_shootlong`
  - `ShootConfig +0x14C` = `dis_shoot`
- collection bonus fields are:
  - `Football +0x98` = `lastKickParam`
  - `BallKickParam +0x40` = `biographyPointType`
  - `BallKickParam +0x44` = `BiographyPassProperty`
- raw checkout CRLF must be normalized to LF before comparing the documented upstream evidence SHA on Windows.

- `0x3FC` and `0x41A` level 1..5 param `[2]` values are exactly `900, 800, 700, 600, 500` in the recovered canonical records.
- open-all selection chooses child `102005` for `0x3FC` and `105005` for `0x41A`, both yielding raw factor `500/1024`.
- activation is `ShootLongKick` for `0x3FC` and `shootPush` for `0x41A`; GetVVer also requires magnitude >= 1 and a non-null selected list.
- when both activate, native order is `0x3FC` then `0x41A`, with fixed-point rounding after each component multiplication.

## INFERRED

- The Il2CppDumper label `XBaseLocalSetting<AIParameterConfig>.get_Singleton` is a shared generic native body label at this callsite; caller-visible offsets and exact `dump.cs` fields prove the object consumed by `GetShootProperty` is `ShootConfig`. This is an evidence-based callsite inference, not a rename of the shared native body.

## UNKNOWN

- concrete runtime property arrays and the selected spmove buffer contents for representative players/actions;
- actual eligible spmove inventory for each runtime player/action; open-all is only a deterministic fixture;
- whole-function native differential vectors for the complete new-path `GetVVer` composition;
- final caller-visible `GetKickVelocity` behavior beyond the static vector join;
- final `BALL_CONTACT.velocity` binding.

## Blockers

Physics v0.3 remains blocked until the full gate is satisfied:

```text
explicit eligible inventories + representative modifier vectors
 -> whole GetVVer differential validation
 -> complete GetKickVelocity
 -> BALL_CONTACT.velocity
 -> no unresolved/pending impulse
 -> full regression
 -> Physics Recovery v0.3
```

Do not rename `vertical_accel_raw` without proof. Do not fabricate the historical 92/92 workspace.

## Exact resume command

```powershell
cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL\.local\worktrees\getvver-spmove-runtime-ratios"
git status --short
py -3 -m unittest discover -s Tests -p "test_*.py"
py -3 Tools/analyze_getvver_spmove_runtime_ratios.py
```

## Next exact step

Commit and publish this bounded runtime-ratio increment. Then build representative GetVVer differential vectors for none, `0x3FC`, `0x41A`, and both, using explicit eligible inventories; do not treat open-all as every player runtime state.
