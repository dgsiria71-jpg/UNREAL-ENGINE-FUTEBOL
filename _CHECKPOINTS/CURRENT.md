# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Canonical main baseline

PR #13, `Recover source-bound GetVVer player property selector`, merged as:

`c12e61cf21b070f15860346e283c2cb92a9d5bd6`

Post-merge `Reference code validation` run #183 / `34802035409` completed **SUCCESS**. The follow-up checkpoint commit `ed2776863d71da7442502eebb0a91d9cdb3d0d1d` also passed run #184 / `34802089841` **SUCCESS**.

Canonical upstream evidence currently consumed by the executable recovery:

- upload ID `20260913-234939-ff28866f`
- `artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt`
- bytes `59637`
- SHA-256 `4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3`
- canonical ARM64 binary SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains **isolated / not consumed**.

## Closed in PR #13

`0x01968398..0x019687C8` is exactly `PlayerProperty$$GetShootProperty`, with `script.json:next-method` boundary provenance.

GetVVer stores original `w1` at `0x016E84EC`, reloads it at `0x016E8DC4`, and calls `PlayerProperty.GetShootProperty` at `0x016E8DCC`. Its result feeds `shootPropertyMapNew(+0xD8) -> energyToleranceMap(+0xE0)`.

`Reference/FootballPhysics/PlayerPropertySelector.h` implements the instruction-bound branch/value selector, and `ComposeNewGetVVerFromPlayerProperty` feeds that selector into the recovered raw-map/fixed-point new-path GetVVer composition.

Confirmed branch-level behavior includes special actions `0x16B3 -> property 0x15`, `0x22C5 -> property 0x16`, collection id `0x13` / property `0x14`, far property `0x10`, position properties `0x0F` / `0x11`, and the native fixed-point middle-distance blend.

This remains **not** a whole-function GetShootProperty/GetVVer equivalence claim.

## Active bounded slice — PR #14

PR #14: `Extend GetVVer property lookup evidence recovery`  
Branch: `chatgpt/getvver-property-lookup-evidence`.

Goal: obtain exact source-bound evidence for the remaining property-value internals and metadata fields without guessing identities.

The read-only extractor now requests five native targets:

```text
0x14DEFDC  goal_door_height_14DEFDC
0x1B60CC8  xnumber_create_1B60CC8
0x1968398  shoot_property_1968398
0x1967D38  property_lookup_1967D38
0x1B718D8  property_fallback_1B718D8
```

The final two labels are intentionally address-based until canonical `ScriptMethod` metadata proves their names.

The extractor also copies exact `dump.cs` field declarations for:

- `AIParameterConfig` window `0x20..0x160`, including the fields physically occupying the runtime-used `+0x24/+0x148/+0x14C` offsets;
- `PlayerProperty` window `0x90..0xA0`, including the declared type at `+0x98`;
- the declared nested `PlayerProperty +0x98` type at offsets `+0x40/+0x44` when that class is directly present in `dump.cs`.

No semantic field names are invented: names/types are copied from metadata or remain unresolved.

## PR #14 TDD / verification

Deep-evidence RED:

- commit `4a8f961376228938a5f547cb482942a973f6ca30`
- run #187 / `34802181960`
- C++ `6/6` remained GREEN
- Python failed only because the deeper metadata helpers/render inputs/targets did not exist yet

Deep-evidence GREEN:

- commit `b7f5693614d8b188fe38e272fd613cc5bcaea165`
- run #189 / `34802255444` — **SUCCESS**

Windows output-preservation RED:

- commit `5d118acf2e616994b619c6be001fb0215078ffc4`
- run #191 / `34802298175`
- C++ `6/6` remained GREEN
- the only new failure required the `.bat` to preserve an existing report before Python rewrites the fixed output pathname

Windows output-preservation GREEN:

- commit `6b9bb80361d4541fe4a2be66e83947497e6ea4d5`
- run #193 / `34802399858` — **SUCCESS**

The `.bat` now automatically moves any existing `getvver_upstream_evidence.txt` to a timestamped `getvver_upstream_evidence_previous_*.txt` before launching Python. This removes the manual rename step that was required after the observed Windows `Errno 9` overwrite failure while preserving the previous local evidence.

## Required handoff after PR #14 merges

Run only:

```powershell
cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL"
git switch main
git pull --ff-only origin main
.\tools\EXTRAIR_GETVVER_UPSTREAM.bat
```

Expected flow:

```text
preserve previous fixed-name report automatically
    -> validate canonical local source hashes
    -> copy ShootSpeedConfigItem metadata
    -> copy AIParameterConfig / PlayerProperty / nested bonus metadata windows
    -> resolve/disassemble five requested native targets
    -> include bounded first-level direct callees
    -> generate .local/recovery-output/getvver_upstream_evidence.txt
    -> publish to artifacts/native-recovery/getvver-upstream/<new-upload-id>/
```

The resulting new Upload ID / SHA must be consumed before assigning exact identities to `0x1967D38` or `0x1B718D8`.

## Current executable new-path chain

```text
PlayerProperty branch selector
    -> shootPropertyMapNew / energyToleranceMap

horizontal distance
    -> shootDisMap / outEnergyMaxMap
    -> shootPointHUpMap
    -> shootPointHDownMap

current energy
    -> energyMapNew / ySpeedMax

resolved map outputs
    -> protected-energy selection
    -> target-height adjustment
    -> fixed XNumber.create(0,100) bias on nonpositive branch
    -> GoalDoor.get_Height
    -> shootPointH clamp - reference_y
    -> recovered shootDisAndTime ballistic solve
    -> ySpeedMin / ySpeedMax clamp
    -> vertical_direction * solved_y_speed
    -> surviving 0x3FC parameter[2]
    -> surviving 0x41A parameter[2]
    -> shared GetVVer return
```

Highest recovered host entry: `ComposeNewGetVVerFromPlayerProperty`.

## Still unresolved before complete GetVVer equivalence

- exact identity/body semantics of `0x1967D38` and `0x1B718D8` until the new publication is consumed;
- exact metadata names/units for runtime-used `AIParameterConfig +0x24/+0x148/+0x14C` until the new publication is consumed;
- exact type/field names behind `PlayerProperty +0x98`, nested `+0x40/+0x44`, where metadata permits;
- runtime Football/GoalDoor object wiring;
- real runtime activation and concrete ratio production for `0x3FC` and `0x41A`;
- native/original whole-path differential vectors;
- old-path GetVVer remains separately preserved.

Do **not** advance final `GetKickVelocity` or `BALL_CONTACT.velocity` until this gate closes.

## Stable preserved baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 tests `67/67 GREEN`
- `83/83` source tables byte-exact
- spmove selection `4,672/4,672`
- spmove producer `2,640/2,640`

Historical original 92/92 advanced-workspace bytes remain **not proven recovered**.

## Workspace safety

Known user local modifications must not be reset, cleaned, overwritten, or staged blindly:

- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`
- `docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `docs/PROJECT_SOURCE_OF_TRUTH.md`

Do not run destructive reset/clean/stash operations against the user's primary checkout.
