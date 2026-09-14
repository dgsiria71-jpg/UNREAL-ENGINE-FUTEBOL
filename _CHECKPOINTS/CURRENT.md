# Current checkpoint

Updated: 2026-09-13. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Canonical main baseline

PR #10 merged as `d51ffa91399e6efc9e33d249a1ea24ac203a8253`.
Post-merge Actions run `34793654111` completed **SUCCESS**: C++ compile/CTest and persisted-evidence validation passed.

That merge closed the bounded new-method GetVVer raw-map producer composition while preserving conservative gates:

- `0x1B60CC8` is exactly `XNumber$$create`; the observed `XNumber.create(0,100)` call contributes raw `102`, not randomness;
- `0x14DEFDC` is exactly `GoalDoor$$get_Height`;
- five new-method map producers are executable from exact `ShootSpeedConfigItem` metadata fields;
- `ComposeNewGetVVerFromRawMaps` feeds those outputs into the recovered fixed-point target-height, `shootDisAndTime`, base-vector, and surviving `0x3FC`/`0x41A` composition;
- `0x1968398`, runtime modifier activation/ratio production, and whole-function native differential equivalence remain unresolved.

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains **isolated / not consumed**.

## Active bounded slice

Branch: `chatgpt/getvver-shoot-property-evidence`.

Goal: obtain source-bound identity/body evidence for the still-unknown native call `0x1968398`, which supplies the scalar used as input to `shootPropertyMapNew` before `energyToleranceMap` remapping.

The existing read-only upstream extractor has been extended to request three targets:

```text
0x14DEFDC  goal_door_height_14DEFDC
0x1B60CC8  xnumber_create_1B60CC8
0x1968398  shoot_property_1968398
```

The first two labels now reflect the exact identities already proven by the previous publication. The third deliberately remains a neutral address-based label until `ScriptMethod` metadata or other source evidence identifies it.

The extractor still follows the same boundary policy:

- only an exact `ScriptMethod` start plus next method may establish an exact function boundary;
- otherwise the report says `exact=false` and emits only a bounded inspection window;
- direct first-level callees are emitted as bounded/exact sections under the same policy;
- canonical local IL2CPP inputs are read-only and hash-validated before extraction.

## TDD for the evidence-target extension

RED 1:

- commit `f12635c69a2bd5c5c206f8408958afc9b7b20704`
- Actions run `34793707664`
- C++ 5/5 remained GREEN
- Python failed only because target `0x1968398` was not yet present in the extractor

RED 2 tightened the naming contract so the already-disproved `downward_random_1B60CC8` label cannot return:

- commit `168cad2bf8527a061ced50ac1991b1aad7159d1d`
- Actions run `34793743461`
- expected Python failures remained scoped to the absent new target / stale labels

GREEN implementation:

- commit `d073e4914683a032654bf64a094b69a792554695`
- Actions run `34793790557` — **SUCCESS**
- C++ compile/CTest and Python/persisted-evidence validation passed

A fresh CI run is required after checkpoint/PR changes and before merge.

## Required local evidence handoff after this branch merges

The same one-click Windows handoff can be run again; no manual searching for `0x1968398` is required:

```powershell
cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL"
git switch main
git pull --ff-only origin main
.\tools\EXTRAIR_GETVVER_UPSTREAM.bat
```

Expected behavior:

```text
validate canonical dump.cs/script.json/global-metadata.dat/libil2cpp.so hashes
    -> copy exact ShootSpeedConfigItem metadata fields
    -> resolve/disassemble GoalDoor.get_Height
    -> resolve/disassemble XNumber.create
    -> resolve/disassemble target 0x1968398
    -> include bounded first-level direct callees
    -> write .local/recovery-output/getvver_upstream_evidence.txt
    -> publish under artifacts/native-recovery/getvver-upstream/<upload-id>/
```

The prior publication remains preserved:

- upload ID `20260913-204613-86a0f84a`
- file `artifacts/native-recovery/getvver-upstream/20260913-204613-86a0f84a/01_getvver_upstream_evidence.txt`
- bytes `5491`
- SHA-256 `416a4f3abef88c117aa21bb66c4500f83474442e6e78a494d84ac1b4914d224f`

## Current executable GetVVer boundary

`Reference/FootballPhysics/GetVVerNewPathConfig.h` binds:

```text
horizontal_distance + shootDisMap(+0xE8)
    -> outEnergyMaxMap(+0x100)      => out_energy

current_energy + energyMapNew(+0xB8)
    -> ySpeedMax(+0xA0)             => y_speed_max

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHUpMap(+0xF8)      => point_up_rate

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHDownMap(+0xF0)    => point_down_rate

output(0x1968398) + shootPropertyMapNew(+0xD8)
    -> energyToleranceMap(+0xE0)    => energy_tolerance
```

The five remap call sites are `0x016E8804`, `0x016E89F4`, `0x016E8BC8`, `0x016E8DA4`, and `0x016E8FA8`.

Canonical host guards require equal-length ascending paired maps and covered input intervals. Those guards are portability/safety behavior and are **not** claims about malformed native exception behavior.

`Reference/FootballPhysics/GetVVerNewPath.h` then applies:

```text
protected-energy selection
    -> positive/nonpositive target-height adjustment
    -> fixed XNumber.create(0,100) bias on nonpositive branch
    -> GoalDoor.get_Height + adjustment
    -> shootPointH clamp - reference_y
    -> recovered shootDisAndTime ballistic solve
    -> ySpeedMin/resolved ySpeedMax clamp
    -> vertical_direction * solved_y_speed
    -> optional 0x3FC parameter[2]
    -> optional 0x41A parameter[2]
```

## Still unresolved before complete GetVVer equivalence

- exact identity and value semantics of `0x1968398`;
- real runtime activation and concrete ratio production for `0x3FC` and `0x41A`;
- native/original differential vectors for the fully composed new path;
- old-path GetVVer remains a separate preserved recovery track.

Do **not** advance to final GetKickVelocity implementation until the complete GetVVer gate is closed.

## Canonical evidence identities

Primary GetVVer listing:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- normalized-LF SHA-256 `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- original ARM64 binary SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Canonical metadata identities:

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

The historical original 92/92 advanced workspace bytes are still **not** proven recovered.

## Next after the new evidence arrives

1. source-bind `0x1968398` without guessing its name;
2. implement its caller-visible shoot-property scalar semantics if the evidence is sufficient;
3. bind real runtime activation/ratios for `0x3FC` and `0x41A`;
4. produce native/original differential vectors for complete new-path GetVVer;
5. only then advance `GetKickVelocity -> BALL_CONTACT.velocity -> full regression -> Physics v0.3`.

## Workspace safety

Known user-state / Windows case-collision paths remain outside recovery branches and must not be reset, cleaned, or staged blindly:

- `Docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `Docs/PROJECT_SOURCE_OF_TRUTH.md`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`

Do not run destructive reset/clean/stash operations against the user's primary checkout.
