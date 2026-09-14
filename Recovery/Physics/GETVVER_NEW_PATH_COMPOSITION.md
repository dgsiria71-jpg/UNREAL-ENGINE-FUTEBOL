# New-path GetVVer composition recovery

Status: the canonical new-method raw-map chain, branch-level `PlayerProperty.GetShootProperty` selector, target-height path, `shootDisAndTime` ballistic solve, base vertical vector, and surviving `0x3FC` / `0x41A` scaling are source-bound and executable within the recovered boundary. **Whole-function GetVVer native differential equivalence is not yet claimed.** Physics v0.3 remains **BLOCKED**.

## Canonical evidence

Mobile baseline: `football-dream-be-a-pro-1-221-5`.

Primary GetVVer listing:

- `artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`
- GetVVer native range: `0x016E84A4..0x016EA55C`
- normalized-LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- canonical ARM64 `libil2cpp.so` SHA-256: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Current upstream metadata/native evidence:

- upload ID `20260913-234939-ff28866f`
- `artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt`
- bytes `59637`
- SHA-256 `4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3`
- exact source identities inside the report:
  - `dump.cs` `4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe`
  - `script.json` `d15222efc79ebfe50074f385c0f5e5af4960fb43c5cf55a383ea32cba34ae799`
  - `global-metadata.dat` `92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e`
  - `libil2cpp.so` `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

The earlier 5,491-byte upload remains historical evidence, but this 59,637-byte publication supersedes it for the current new-path GetVVer trace.

## Exact helper identities already closed

`0x14DEFDC..0x14DEFE8` is exactly `GoalDoor$$get_Height`.

`0x1B60CC8..0x1B60D14` is exactly `XNumber$$create`. The observed GetVVer call `XNumber.create(0,100)` returns raw `102`, so the nonpositive target-height branch uses a fixed downward bias, not randomness.

## `0x1968398` is now identified

The new publication gives an exact ScriptMethod boundary:

```text
0x01968398 .. 0x019687C8
PlayerProperty$$GetShootProperty
```

GetVVer preserves its original `w1` at `0x016E84EC`, reloads that same value at `0x016E8DC4`, and calls `PlayerProperty.GetShootProperty` at `0x016E8DCC`. Therefore the scalar sent into `shootPropertyMapNew` is no longer an anonymous caller-supplied value.

The exact first-level value-producing callees visible in the published body include:

- `Football$$get_position2D`
- `GoalDoor$$getCenter`
- `XIntMath$$Sqrt_Long`
- `XGoalExtension$$InCollection`
- `PropertySingle$$calMain`
- `PlayerProperty$$getShootPropertyWithSpmove`
- `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`

## Recovered branch-level PlayerProperty selector

`Reference/FootballPhysics/PlayerPropertySelector.h` implements the branch/value selection that is directly instruction-bound in `PlayerProperty.GetShootProperty` while leaving unresolved property-value lookup internals behind a resolver callback.

Confirmed branches:

```text
action 0x16B3 -> property id 0x15
action 0x22C5 -> property id 0x16

otherwise:
    if XGoalExtension.InCollection(action, 0x13):
        base = property id 0x14
        optional runtime bonus = PropertySingle.calMain(0x30, runtime value)
        return base + bonus when enabled

    distance = |Football.position2D - GoalDoor.center|

    if distance > AI threshold at +0x148:
        return property id 0x10

    near property depends on position-Y comparison against AI field +0x24:
        threshold >= positionY -> property id 0x0F
        threshold <  positionY -> property id 0x11

    if distance < AI threshold at +0x14C:
        return near property

    otherwise blend near property with property 0x10
```

The mid-interval ratio is fixed-point:

```text
numerator   = upper_threshold - distance
denominator = upper_threshold - lower_threshold

if numerator == 0 or denominator == 0:
    ratio = 0
else:
    n = numerator * 1024
    q = trunc(n / denominator)
    r = n - q * denominator
    ratio = q + trunc(2*r / denominator)

result = fixed_mul(near_value, ratio)
       + fixed_mul(far_value, 1024 - ratio)
```

This is executable through `ResolvePlayerProperty`, but it is deliberately **not** labeled whole-function equivalent yet because the actual property-value resolver internals and some runtime source fields are still unresolved.

## Exact new-method config fields

Published metadata establishes:

```text
+0x94  energyNeedProtect      XNumber
+0x98  ySpeedMin             XNumber
+0xA0  ySpeedMax             List<XNumber>
+0xB0  shootPointH           XVector2
+0xB8  energyMapNew          List<XNumber>
+0xD8  shootPropertyMapNew   List<XNumber>
+0xE0  energyToleranceMap    List<XNumber>
+0xE8  shootDisMap           List<XNumber>
+0xF0  shootPointHDownMap    List<XNumber>
+0xF8  shootPointHUpMap      List<XNumber>
+0x100 outEnergyMaxMap       List<XNumber>
+0x108 shootDisAndTime       List<List<int>>
```

## Raw-map producer chain

The five source-bound remap stages are:

```text
horizontal_distance + shootDisMap(+0xE8)
    -> outEnergyMaxMap(+0x100)      => out_energy

current_energy + energyMapNew(+0xB8)
    -> ySpeedMax(+0xA0)             => y_speed_max

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHUpMap(+0xF8)      => point_up_rate

horizontal_distance + shootDisMap(+0xE8)
    -> shootPointHDownMap(+0xF0)    => point_down_rate

PlayerProperty.GetShootProperty result + shootPropertyMapNew(+0xD8)
    -> energyToleranceMap(+0xE0)    => energy_tolerance
```

Native remap calls: `0x016E8804`, `0x016E89F4`, `0x016E8BC8`, `0x016E8DA4`, `0x016E8FA8`.

`ComposeNewGetVVerFromPlayerProperty` now resolves the recovered PlayerProperty selector and feeds that result into the existing raw-map composition.

## Downstream vertical composition

The already recovered downstream path remains:

```text
protected-energy selection
    -> point-up / point-down target-height adjustment
    -> fixed XNumber.create(0,100) downward bias on nonpositive branch
    -> GoalDoor.get_Height + adjustment
    -> shootPointH min/max clamp
    -> subtract reference_y
    -> recovered shootDisAndTime lookup / ballistic solve
    -> ySpeedMin / resolved ySpeedMax clamp
    -> vertical_direction * solved_y_speed
    -> optional 0x3FC parameter[2]
    -> optional 0x41A parameter[2]
    -> shared GetVVer return
```

The `0x3FC` and `0x41A` modifiers both survive the normal new-path return and scale all three live vector components using native fixed-point multiplication.

## Current executable boundary

Executable source-bound pieces now include:

- `Reference/FootballPhysics/ShootRemap.h`
- `Reference/FootballPhysics/ShootDisAndTime.h`
- `Reference/FootballPhysics/GetVVerNewPath.h`
- `Reference/FootballPhysics/GetVVerNewPathConfig.h`
- `Reference/FootballPhysics/PlayerPropertySelector.h`

The highest-level recovered entry in this slice is:

```text
ComposeNewGetVVerFromPlayerProperty
```

This closes the previous anonymous `0x1968398` scalar boundary, but still accepts runtime/environment inputs that have not yet been source-bound end-to-end.

## TDD evidence for PlayerProperty increment

Selector RED:

- commit `93cf1edd5408c54b6528d374bc731d6398311efa`
- Actions run `34801287309`
- expected failure: missing `PlayerPropertySelector.h`

Selector implementation exposed only a test-macro syntax problem; after correcting the test expression, the first selector GREEN was:

- commit `29ac8e76373fc07df9765963c99e0775715eecd4`
- Actions run `34801381432` — **SUCCESS**

Integration RED:

- commit `df459ab5b7afe7bb216b187069e97f8f2426a14d`
- Actions run `34801475096`
- expected failure: `ComposeNewGetVVerFromPlayerProperty` absent

Integration GREEN:

- commit `28251f4cb56602ed64ec14542ba6b21606d66da7`
- Actions run `34801518576` — **SUCCESS**

Evidence rebinding RED:

- commit `ed4d797dcebeb4248419389b8f5757ff9ade5b35`
- Actions run `34801599176`
- C++ `6/6` GREEN; Python failed only because analyzer was still bound to the old 5,491-byte evidence SHA.

Analyzer GREEN candidate:

- commit `0ff9a744831c637bcdd158ec555ef5cb80ea923e`
- Actions run `34801770214`
- all native/metadata anchors and C++ `6/6` passed; only the intentionally stale persisted v2 JSON remained RED.

The v3 trace is now persisted at `Recovery/Normalized/getvver_new_path_composition_static_trace.json`; a fresh full CI run is required after documentation/checkpoint updates before merge.

## Remaining gate

Do **not** claim complete GetVVer equivalence yet. Remaining source gaps include:

- `PlayerProperty.getShootPropertyWithSpmove` second-level callee `0x1967D38`;
- fallback property lookup `0x1B718D8`;
- semantic names/units for `AIParameterConfig +0x24/+0x148/+0x14C`;
- runtime producer behind collection-bonus object/fields `+0x98/+0x40/+0x44`;
- runtime Football/GoalDoor object wiring;
- real activation and concrete ratio production for `0x3FC` and `0x41A`;
- whole-function native/original differential vectors for the composed new path.

Only after those gates close should work advance to complete `GetKickVelocity`, `BALL_CONTACT.velocity`, full regression, and Physics v0.3.

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains **isolated / not consumed**.
