# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**. Physics v0.3 is **BLOCKED**. GitHub `main` is canonical.

## Branch and HEAD

- working branch: `codex/getvver-property-lookup`
- branch HEAD before this checkpoint update: `bdfc20c` (`Recover GetVVer property lookup semantics`)
- branch base: GitHub `main` commit `642888c9c64470f7f027aba4a0bec412e9f31e00`
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

GitHub Actions for this branch is pending until the branch is pushed. Do not replace this statement with success until the remote run completes.

## Current task

Close the second-level property lookup boundary used by `PlayerProperty.GetShootProperty`, correct the metadata-class bindings in the upstream extractor, and preserve an executable reference without claiming whole-function `GetVVer` equivalence.

## Files changed by the current increment

- `Tools/extract_getvver_upstream_evidence.py`
- `Tools/analyze_property_lookup_semantics.py`
- `Tools/analyze_getvver_new_path_composition.py`
- `Reference/FootballPhysics/PropertyLookup.h`
- `Tests/property_lookup_test.cpp`
- `Tests/test_property_lookup_semantics.py`
- `Tests/test_getvver_upstream_extractor.py`
- `Tests/CMakeLists.txt`
- `Recovery/Normalized/property_lookup_semantics_static_trace.json`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`
- `Recovery/Normalized/recovery_manifest.json`
- `Recovery/Physics/PROPERTY_LOOKUP_SEMANTICS.md`
- `Recovery/Physics/GETVVER_NEW_PATH_COMPOSITION.md`
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

## INFERRED

- The Il2CppDumper label `XBaseLocalSetting<AIParameterConfig>.get_Singleton` is a shared generic native body label at this callsite; caller-visible offsets and exact `dump.cs` fields prove the object consumed by `GetShootProperty` is `ShootConfig`. This is an evidence-based callsite inference, not a rename of the shared native body.

## UNKNOWN

- concrete runtime property arrays and the selected spmove buffer contents for representative players/actions;
- runtime activation and parameter `[2]` ratio producers for `0x3FC` and `0x41A`;
- whole-function native differential vectors for the complete new-path `GetVVer` composition;
- final caller-visible `GetKickVelocity` behavior beyond the static vector join;
- final `BALL_CONTACT.velocity` binding.

## Blockers

Physics v0.3 remains blocked until the full gate is satisfied:

```text
runtime 0x3FC / 0x41A activation and ratios
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
cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL\.local\worktrees\getvver-property-lookup"
git status --short
py -3 -m unittest discover -s Tests -p "test_*.py"
& "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe" --test-dir .local/build-property-lookup -C Release --output-on-failure
```

## Next exact step

Finish validation, commit the checkpoint-bound increment, push `codex/getvver-property-lookup`, open a PR, require GitHub Actions GREEN, and merge. Then trace the runtime producers that feed `GetSpmoveDataRatio(0x3FC/0x41A)` and extract representative parameter `[2]` values for native differential vectors.
