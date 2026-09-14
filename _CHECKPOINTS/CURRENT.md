# Current checkpoint

Updated: 2026-09-13. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Current recovery increment

- active branch: `chatgpt/getvver-upstream-producers`
- branch base was refreshed to `fc151ea5c6ffac75fdb218ddae20ff66e1ef47a2`, the user-published GetVVer upstream evidence commit on `main`
- current slice: corrected helper identities + executable raw new-method GetVVer map producers + integrated raw-map front end
- Physics v0.3: **BLOCKED**
- build `1-226-19`: **isolated / not consumed**

This increment supersedes the earlier temporary interpretation that call `0x1B60CC8` supplied a random offset. The published canonical evidence proves it is `XNumber$$create`; the exact observed GetVVer call `XNumber.create(0,100)` contributes fixed raw `102`. `0x14DEFDC` is exactly `GoalDoor$$get_Height`.

## Published upstream evidence

User publication:

- upload ID `20260913-204613-86a0f84a`
- file `artifacts/native-recovery/getvver-upstream/20260913-204613-86a0f84a/01_getvver_upstream_evidence.txt`
- bytes `5491`
- published SHA-256 `416a4f3abef88c117aa21bb66c4500f83474442e6e78a494d84ac1b4914d224f`
- manifest `manifests/uploads/20260913-204613-86a0f84a.json`
- original local canonical inputs were preserved

The evidence contains exact `ShootSpeedConfigItem` metadata names through `+0x108`, exact ScriptMethod boundaries for `GoalDoor$$get_Height` and `XNumber$$create`, and bounded ARM64 bodies from canonical build `1-221-5`.

## What is now executable

### Corrected target-height path

`Reference/FootballPhysics/GetVVerNewPath.h` now implements:

```text
selected_energy
    -> delta = selected_energy - out_energy

if delta > 0:
    fixed_mul(delta, point_up_rate)
else:
    -(fixed_mul(abs(delta), point_down_rate)
      + XNumber.create(0,100))

GoalDoor.get_Height + adjustment
    -> native shootPointH clamp
    -> subtract reference_y
    -> recovered shootDisAndTime vertical kernel
```

The bounded reference exposes `GetVVerDownwardBias()` as raw `102` for the exact observed `XNumber.create(0,100)` call. It does **not** claim a generic implementation of every `XNumber.create` input.

### Raw new-method map producers

`Reference/FootballPhysics/GetVVerNewPathConfig.h` binds these exact metadata pairs:

```text
horizontal_distance + shootDisMap(+0xE8)
    -> outEnergyMaxMap(+0x100)      => out_energy

current_energy + energyMapNew(+0xB8)
    -> ySpeedMax(+0xA0)             => y_speed_max

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHUpMap(+0xF8)      => point_up_rate

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHDownMap(+0xF0)    => point_down_rate

shoot_property_input + shootPropertyMapNew(+0xD8)
    -> energyToleranceMap(+0xE0)    => energy_tolerance
```

All five use the already recovered shoot-specific remap semantics at native call sites `0x016E8804`, `0x016E89F4`, `0x016E8BC8`, `0x016E8DA4`, and `0x016E8FA8`.

`ComposeNewGetVVerFromRawMaps` now resolves those maps and feeds the recovered fixed-point vertical composition, `shootDisAndTime`, base vector, and surviving `0x3FC` then `0x41A` modifiers.

Canonical host guards require equal-length ascending paired maps and a covered input interval. Those guards are portability/safety rules and are **not** claims about malformed native exception behavior.

## Still unresolved inside new-path GetVVer

- native call `0x1968398` produces the scalar used as input to `shootPropertyMapNew`; its identity/semantics are not yet named or guessed
- real runtime activation and concrete ratio production for surviving spmove logic `0x3FC` and `0x41A`
- whole-function native/original differential vectors for the fully composed new path
- old-path GetVVer remains a separate preserved recovery track

Therefore complete GetVVer equivalence is **not** yet claimed.

## TDD / verification evidence

First scoped RED for upstream producers:

- commit `9dca5cd40d347a0eae6be6ba981b7472b960be4c`
- Actions `34793147491`
- expected failure: `GetVVerNewPathConfig.h` was absent

First GREEN:

- commit `15bfad43a374d6b64976aada6c09d68b44afb913`
- Actions `34793282267` — **SUCCESS**
- C++ build/CTest and Python/persisted-evidence checks passed

Second scoped RED for integrated raw-map composition:

- commit `dfc1ee97c45e9097232968d99960f7d7c685ea5a`
- Actions `34793403729`
- expected failure: `ShootSpeedNewMethodConfig` and `ComposeNewGetVVerFromRawMaps` were absent

Second GREEN before documentation:

- commit `87aed845f02e997e9634147fbcafab62442933e8`
- Actions `34793434887` — **SUCCESS**
- C++ build/CTest and Python/persisted-evidence checks passed

A fresh full CI run is required after this documentation/checkpoint update and before merge.

## Current recovery material

- `Reference/FootballPhysics/GetVVerNewPath.h`
- `Reference/FootballPhysics/GetVVerNewPathConfig.h`
- `Reference/FootballPhysics/ShootRemap.h`
- `Reference/FootballPhysics/ShootDisAndTime.h`
- `Tools/analyze_getvver_new_path_composition.py`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`
- `Recovery/Physics/GETVVER_NEW_PATH_COMPOSITION.md`
- `Tests/getvver_new_path_composition_test.cpp`
- `Tests/test_getvver_new_path_composition.py`

## Canonical source identities

Primary GetVVer listing:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- normalized-LF SHA-256 `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- original ARM64 binary SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Canonical local metadata identities embedded in the upstream report:

- `dump.cs` `4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe`
- `script.json` `d15222efc79ebfe50074f385c0f5e5af4960fb43c5cf55a383ea32cba34ae799`
- `global-metadata.dat` `92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e`

## Stable preserved baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 tests `67/67 GREEN`
- `83/83` source tables byte-exact
- spmove selection `4,672/4,672`
- spmove producer `2,640/2,640`

The historical original 92/92 advanced workspace bytes are still **not** proven recovered. Do not manufacture a 92/92 status from current tests.

## Next bounded slice

Do not move to GetKickVelocity yet. Next:

1. identify/disassemble native call `0x1968398` using exact metadata-boundary policy;
2. bind the resulting shoot-property scalar producer;
3. bind real runtime activation/ratio inputs for `0x3FC` and `0x41A`;
4. build native/original differential vectors for complete new-path GetVVer;
5. only after full GetVVer equivalence advance `GetKickVelocity -> BALL_CONTACT.velocity -> full regression -> Physics v0.3`.

## Physics v0.3 gate

Physics v0.3 remains **BLOCKED**. No fallback or approximate ball velocity may bypass missing native evidence.

## Workspace safety

Known user-state / Windows case-collision paths remain outside recovery branches and must not be reset, cleaned, or staged blindly:

- `Docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `Docs/PROJECT_SOURCE_OF_TRUTH.md`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`

Do not run destructive reset/clean/stash operations against the user's primary checkout.
