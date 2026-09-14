# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Canonical baseline entering this increment

The latest user-published main commit is `e74afbcd3c311d1bafdee1044d2a3280d5f2ce23` (`Publish GetVVer upstream native evidence`). It added canonical upload:

- upload ID `20260913-234939-ff28866f`
- `artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt`
- bytes `59637`
- SHA-256 `4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3`

Canonical ARM64 source identity remains `libil2cpp.so` SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`.

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains **isolated / not consumed**.

## Active bounded slice

PR #13: `Recover source-bound GetVVer player property selector`  
Branch: `chatgpt/getvver-property-semantics`.

The new publication closes the previous anonymous native target:

```text
0x01968398..0x019687C8
PlayerProperty$$GetShootProperty
exact boundary: script.json:next-method
```

GetVVer stores original `w1` at `0x016E84EC`, reloads it at `0x016E8DC4`, and calls `PlayerProperty.GetShootProperty` at `0x016E8DCC`. The result feeds `shootPropertyMapNew(+0xD8) -> energyToleranceMap(+0xE0)` before the existing energy-protection/vertical solve.

## Newly executable selector boundary

`Reference/FootballPhysics/PlayerPropertySelector.h` now implements the instruction-bound branch/value selection while keeping actual property-value lookup behind a resolver callback.

Confirmed branches:

```text
action 0x16B3 -> property 0x15
action 0x22C5 -> property 0x16

if InCollection(action, 0x13):
    property 0x14
    + optional PropertySingle.calMain(0x30, runtime value)

else:
    distance = 2D Football.position to GoalDoor.center

    distance > AI +0x148 -> property 0x10

    near property:
        AI +0x24 >= positionY -> 0x0F
        AI +0x24 <  positionY -> 0x11

    distance < AI +0x14C -> near property

    middle interval -> fixed-point blend:
        ratio = (upper-distance)/(upper-lower)
        using q + trunc(2*r/d)
        zero numerator/denominator -> 0
        result = fixed_mul(near, ratio)
               + fixed_mul(far, 1024-ratio)
```

Exact first-level value callees in the published body include:

- `Football$$get_position2D`
- `GoalDoor$$getCenter`
- `XIntMath$$Sqrt_Long`
- `XGoalExtension$$InCollection`
- `PropertySingle$$calMain`
- `PlayerProperty$$getShootPropertyWithSpmove`
- `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`

`Reference/FootballPhysics/GetVVerNewPathConfig.h` now exposes `ComposeNewGetVVerFromPlayerProperty`, which resolves this selector and feeds the scalar into the already recovered raw-map and fixed-point GetVVer composition.

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
    -> shootDisAndTime ballistic solve
    -> ySpeedMin / ySpeedMax clamp
    -> vertical_direction * solved_y_speed
    -> 0x3FC parameter[2]
    -> 0x41A parameter[2]
    -> shared GetVVer return
```

The highest-level recovered host entry in this slice is `ComposeNewGetVVerFromPlayerProperty`.

## TDD evidence in PR #13

Selector RED:

- commit `93cf1edd5408c54b6528d374bc731d6398311efa`
- Actions run `34801287309`
- expected compile failure: `PlayerPropertySelector.h` absent

Selector GREEN after correcting only a C `assert` macro test syntax issue:

- commit `29ac8e76373fc07df9765963c99e0775715eecd4`
- Actions run `34801381432` — **SUCCESS**

Integration RED:

- commit `df459ab5b7afe7bb216b187069e97f8f2426a14d`
- Actions run `34801475096`
- expected compile failure: `ComposeNewGetVVerFromPlayerProperty` absent

Integration GREEN:

- commit `28251f4cb56602ed64ec14542ba6b21606d66da7`
- Actions run `34801518576` — **SUCCESS**

Evidence-rebinding RED:

- commit `ed4d797dcebeb4248419389b8f5757ff9ade5b35`
- Actions run `34801599176`
- C++ `6/6` GREEN; Python failed only on old upstream evidence SHA binding

Analyzer/anchor GREEN candidate:

- commit `0ff9a744831c637bcdd158ec555ef5cb80ea923e`
- Actions run `34801770214`
- all C++ `6/6` and new ARM64/metadata anchors passed; only the intentionally stale persisted v2 trace remained failing

The persisted trace is now schema `football.recovery.getvver_new_path_composition.v3` and points at the 59,637-byte upload. A fresh full CI run after documentation/manifest updates is required before merge.

## Still unresolved before complete GetVVer equivalence

Do **not** label GetVVer whole-function equivalent yet. Still open:

- `PlayerProperty.getShootPropertyWithSpmove` second-level callee `0x1967D38`;
- fallback property lookup `0x1B718D8`;
- semantic field names/units for `AIParameterConfig +0x24/+0x148/+0x14C`;
- collection bonus runtime producer behind `+0x98/+0x40/+0x44`;
- runtime Football/GoalDoor object wiring;
- real runtime activation and ratio production for `0x3FC` and `0x41A`;
- native/original differential vectors for the whole composed new path;
- old-path GetVVer remains a separately preserved track.

Do **not** advance final GetKickVelocity or `BALL_CONTACT.velocity` until this gate closes.

## Stable preserved baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 tests `67/67 GREEN`
- `83/83` source tables byte-exact
- spmove selection `4,672/4,672`
- spmove producer `2,640/2,640`

Historical original 92/92 advanced-workspace bytes are still **not** proven recovered.

## Next bounded recovery target

After PR #13 closes GREEN:

1. source-bind `0x1967D38` and `0x1B718D8` without guessing names;
2. recover exact metadata identities for AI threshold fields around `+0x24/+0x148/+0x14C` if available;
3. identify the collection-bonus producer fields;
4. bind real runtime activation/ratios for `0x3FC` and `0x41A`;
5. build native/original differential vectors for complete new-path GetVVer;
6. only then proceed to complete `GetKickVelocity -> BALL_CONTACT.velocity -> regression -> Physics v0.3`.

## Workspace safety

Known user local modifications must not be reset, cleaned, overwritten, or staged blindly:

- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`
- `docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `docs/PROJECT_SOURCE_OF_TRUTH.md`

Do not run destructive reset/clean/stash operations against the user's primary checkout.
