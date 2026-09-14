# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Canonical main baseline

PR #13, `Recover source-bound GetVVer player property selector`, merged as:

`c12e61cf21b070f15860346e283c2cb92a9d5bd6`

Post-merge `Reference code validation` run #183 / `34802035409` completed **SUCCESS**: C++ compile, all 6 CTests, Python contracts, persisted-evidence checks, and content validation passed.

The canonical upstream evidence consumed by this merge is:

- upload ID `20260913-234939-ff28866f`
- `artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt`
- bytes `59637`
- SHA-256 `4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3`
- canonical ARM64 binary SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains **isolated / not consumed**.

## What PR #13 closed

The previous anonymous native target is now exact:

```text
0x01968398..0x019687C8
PlayerProperty$$GetShootProperty
boundary: script.json:next-method
```

GetVVer stores original `w1` at `0x016E84EC`, reloads it at `0x016E8DC4`, and calls `PlayerProperty.GetShootProperty` at `0x016E8DCC`. Its result feeds:

```text
shootPropertyMapNew(+0xD8)
    -> energyToleranceMap(+0xE0)
```

`Reference/FootballPhysics/PlayerPropertySelector.h` now implements the instruction-bound branch/value selector, and `ComposeNewGetVVerFromPlayerProperty` feeds that selector directly into the recovered raw-map and fixed-point new-path GetVVer composition.

Confirmed branch-level selector behavior:

```text
action 0x16B3 -> property 0x15
action 0x22C5 -> property 0x16

if InCollection(action, 0x13):
    property 0x14
    + optional PropertySingle.calMain(0x30, runtime value)

else:
    distance = |Football.position2D - GoalDoor.center|

    distance > AI +0x148 -> property 0x10

    near property:
        AI +0x24 >= positionY -> 0x0F
        AI +0x24 <  positionY -> 0x11

    distance < AI +0x14C -> near property

    middle interval:
        ratio = (upper-distance)/(upper-lower)
        using q + trunc(2*r/d)
        zero numerator/denominator -> 0
        result = fixed_mul(near, ratio)
               + fixed_mul(far, 1024-ratio)
```

Exact first-level value callees published for `GetShootProperty` include:

- `Football$$get_position2D`
- `GoalDoor$$getCenter`
- `XIntMath$$Sqrt_Long`
- `XGoalExtension$$InCollection`
- `PropertySingle$$calMain`
- `PlayerProperty$$getShootPropertyWithSpmove`
- `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`

The persisted trace is now schema `football.recovery.getvver_new_path_composition.v3`, and the recovery manifest points to the 59,637-byte upstream publication.

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

Highest recovered host entry for this path:

`ComposeNewGetVVerFromPlayerProperty`.

This is still **not** a whole-function native differential clone.

## PR #13 TDD / verification trail

- RED `93cf1edd5408c54b6528d374bc731d6398311efa`, run `34801287309`: selector production header absent.
- selector GREEN `29ac8e76373fc07df9765963c99e0775715eecd4`, run `34801381432`: **SUCCESS**.
- integration RED `df459ab5b7afe7bb216b187069e97f8f2426a14d`, run `34801475096`: `ComposeNewGetVVerFromPlayerProperty` absent.
- integration GREEN `28251f4cb56602ed64ec14542ba6b21606d66da7`, run `34801518576`: **SUCCESS**.
- evidence RED `ed4d797dcebeb4248419389b8f5757ff9ade5b35`, run `34801599176`: C++ 6/6 GREEN; old upstream SHA binding rejected.
- analyzer candidate `0ff9a744831c637bcdd158ec555ef5cb80ea923e`, run `34801770214`: all new ARM64/metadata anchors and C++ 6/6 passed; only stale persisted v2 trace remained RED.
- final PR head `c2870faeede01128ee77f8351b96e2ba98c4bd2a`, run `34801960638`: **SUCCESS**.
- merge `c12e61cf21b070f15860346e283c2cb92a9d5bd6`, post-merge run `34802035409`: **SUCCESS**.

## Still unresolved before complete GetVVer equivalence

Do **not** claim whole-function GetShootProperty or GetVVer equivalence. Still open:

- `PlayerProperty.getShootPropertyWithSpmove` second-level callee `0x1967D38`;
- fallback property lookup `0x1B718D8`;
- semantic field names/units for `AIParameterConfig +0x24/+0x148/+0x14C`;
- collection bonus runtime producer behind `PlayerProperty +0x98` and nested `+0x40/+0x44`;
- runtime Football/GoalDoor object wiring;
- real runtime activation and concrete ratio production for `0x3FC` and `0x41A`;
- native/original whole-path differential vectors;
- old-path GetVVer remains a separately preserved recovery track.

Do **not** advance final `GetKickVelocity` or `BALL_CONTACT.velocity` until this gate closes.

## Next bounded recovery target

1. source-bind `0x1967D38` and `0x1B718D8` without guessing identities;
2. copy exact metadata fields for `AIParameterConfig` around `+0x24/+0x148/+0x14C`;
3. identify the `PlayerProperty +0x98` collection-bonus object and nested `+0x40/+0x44` fields where metadata permits;
4. then bind real runtime activation/ratios for `0x3FC` and `0x41A`;
5. build native/original differential vectors for complete new-path GetVVer;
6. only after that proceed to `GetKickVelocity -> BALL_CONTACT.velocity -> full regression -> Physics v0.3`.

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
