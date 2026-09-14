# New-path GetVVer composition recovery

Status: raw new-method map producers plus resolved-scalar composition are instruction-bound and executable for the canonical covered data contract. Physics v0.3 remains **BLOCKED**.

## Evidence boundary

Canonical mobile baseline remains build `1-221-5`.

Primary native listing:

- `GetVVer`: `0x016E84A4..0x016EA55C`
- `artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`
- normalized-LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- originating ARM64 `libil2cpp.so` SHA-256: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Published upstream metadata/helper evidence:

- `artifacts/native-recovery/getvver-upstream/20260913-204613-86a0f84a/01_getvver_upstream_evidence.txt`
- published SHA-256: `416a4f3abef88c117aa21bb66c4500f83474442e6e78a494d84ac1b4914d224f`
- source identities inside the report are the canonical `dump.cs`, `script.json`, `global-metadata.dat`, and `libil2cpp.so` hashes already used by the recovery chain.

This report resolved two previously opaque callees and provided exact metadata field names for the new-method config. The recovery below supersedes the earlier temporary `downward_random_offset_raw` interpretation.

## Corrected helper identities

### `0x1B60CC8` is `XNumber.create`

The helper has an exact `ScriptMethod` boundary `0x01B60CC8..0x01B60D14` and metadata name `XNumber$$create`.

The GetVVer caller at `0x016E9188..0x016E9198` passes:

```text
w0 = 0
w1 = 100
x2 = 0
call XNumber.create
```

For this exact observed call, the recovered helper body produces fixed-point raw `102`, i.e. the native representation used here for `0.1` on the 1024 scale. The reference deliberately exposes only this bounded observed constant through `GetVVerDownwardBias()`; it does **not** claim a complete generic clone of `XNumber.create`.

Therefore the nonpositive target-height branch is corrected to:

```text
height_adjustment = -(
    fixed_mul(abs(selected_energy - out_energy), point_down_rate)
    + XNumber.create(0, 100)
)
```

There is no recovered RNG/random input in this block.

### `0x14DEFDC` is `GoalDoor.get_Height`

The helper has exact boundary `0x014DEFDC..0x014DEFE8` and metadata name `GoalDoor$$get_Height`.

Its body is only:

```text
ldr x8, [x0, #0x18]
ldr w0, [x8, #0x24]
ret
```

So the scalar entering the target-height clamp is the caller-visible result of `GoalDoor.get_Height`, not an unidentified generic height helper.

## Exact new-method config fields used by GetVVer

The published `ShootSpeedConfigItem` metadata establishes these relevant fields without name inference:

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

`ySpeedMax` is therefore a map/list producer output in the new path, not a scalar config field.

## Raw-map producer chain

The five recovered `0x126BF1C` remap stages are now bound to exact metadata fields and executable through `Reference/FootballPhysics/GetVVerNewPathConfig.h`.

For canonical ascending paired maps and inputs inside a covered interval:

```text
out_energy = remap(
    horizontal_distance,
    shootDisMap,
    outEnergyMaxMap)

y_speed_max = remap(
    current_energy,
    energyMapNew,
    ySpeedMax)

point_up_rate = remap(
    horizontal_distance,
    shootDisMap,
    shootPointHUpMap)

point_down_rate = remap(
    horizontal_distance,
    shootDisMap,
    shootPointHDownMap)

energy_tolerance = remap(
    shoot_property_input,
    shootPropertyMapNew,
    energyToleranceMap)
```

Instruction-bound call sites are respectively:

```text
0x016E8804
0x016E89F4
0x016E8BC8
0x016E8DA4
0x016E8FA8
```

The last producer's scalar input is returned by native call `0x1968398` at `0x016E8DCC`. Its identity/semantics are still unresolved, so `shoot_property_input` remains an explicit runtime input. No name is fabricated for `0x1968398`.

`RemapPairedShootMapCanonical` uses the already source-bound `ShootRemapClamped`. Its equal-length/ascending/out-of-range checks are **host guards for canonical recovered data**, not claims about malformed/null native exception behavior.

## Energy protection and target height

With the raw producer outputs resolved:

```text
protected_floor = out_energy - energyNeedProtect

if protected_floor >= current_energy:
    selected_energy = current_energy
else if current_energy >= out_energy + energy_tolerance:
    selected_energy = current_energy
else:
    selected_energy = max(
        current_energy - energy_tolerance,
        protected_floor)
```

Then:

```text
delta = selected_energy - out_energy

if delta > 0:
    height_adjustment = fixed_mul(delta, point_up_rate)
else:
    height_adjustment = -(
        fixed_mul(abs(delta), point_down_rate)
        + XNumber.create(0, 100)
    )

vertical_delta = native_clamp(
    GoalDoor.get_Height + height_adjustment,
    shootPointH.min,
    shootPointH.max
) - reference_y
```

## Recovered ballistic and vector composition

`vertical_delta` feeds the already recovered `shootDisAndTime` kernel in `Reference/FootballPhysics/ShootDisAndTime.h`:

```text
flight_time = lookup shootDisAndTime(vHor magnitude, horizontal distance)
solved_y_speed = (vertical_delta - vertical_accel_raw*t*t/2) / t
solved_y_speed = native clamp(ySpeedMin, resolved ySpeedMax)
```

The base vector at `0x016E9D08..0x016E9D48` is:

```text
base_vver = vertical_direction * solved_y_speed
```

using native fixed-point multiplication.

The normal new path then applies surviving post-vector spmove modifiers in native order:

```text
0x3FC parameter[2]
0x41A parameter[2]
```

Both scale all three live vector components and survive into the shared GetVVer return.

## Executable boundaries

`Reference/FootballPhysics/GetVVerNewPath.h` contains:

- `SelectProtectedEnergy`
- `GetVVerDownwardBias`
- `ComputePointHeightAdjustment`
- `ComputeVerticalDelta`
- `BuildVerticalVector`
- `ApplyGetVVerModifier`
- `ComposeNewGetVVerFromResolvedScalars`

`Reference/FootballPhysics/GetVVerNewPathConfig.h` contains:

- exact-name `ShootSpeedNewMethodMaps`
- bounded `ShootSpeedNewMethodConfig`
- `RemapPairedShootMapCanonical`
- `ResolveNewGetVVerMapOutputs`
- `ComposeNewGetVVerFromRawMaps`

The raw-map front end now resolves the five recovered map outputs and feeds them directly into the previously recovered fixed-point composition. It still accepts the unresolved `0x1968398` caller-visible output, `GoalDoor.get_Height`, vertical direction, and spmove activation/ratios as runtime inputs.

## TDD / CI evidence for the upstream producer increment

First RED:

- commit `9dca5cd40d347a0eae6be6ba981b7472b960be4c`
- Actions run `34793147491`
- failure: the test required missing production header `GetVVerNewPathConfig.h`

First GREEN after map producers, fixed `XNumber.create(0,100)` bias, analyzer and persisted trace:

- commit `15bfad43a374d6b64976aada6c09d68b44afb913`
- Actions run `34793282267` — **SUCCESS**

Second RED required integration of the raw producers into the vertical composition:

- commit `dfc1ee97c45e9097232968d99960f7d7c685ea5a`
- Actions run `34793403729`
- failure: `ShootSpeedNewMethodConfig` and `ComposeNewGetVVerFromRawMaps` did not yet exist

Second GREEN:

- commit `87aed845f02e997e9634147fbcafab62442933e8`
- Actions run `34793434887` — **SUCCESS**
- C++ build/CTest and Python/persisted-evidence validation passed.

A fresh CI run is required after documentation/checkpoint changes before merge.

## Remaining gate

This still does **not** establish whole-function/native differential equivalence for GetVVer. Remaining requirements are:

- identify and recover enough behavior for call `0x1968398` to produce the shoot-property input rather than passing it in;
- bind real runtime activation and concrete recovered ratios for `0x3FC` and `0x41A` from canonical state;
- construct native/original differential vectors for the complete new path;
- preserve the old GetVVer path separately;
- only after complete GetVVer validation advance final `GetKickVelocity` behavior and `BALL_CONTACT.velocity`.

Physics v0.3 remains **BLOCKED**. No fallback or approximate ball velocity is permitted to bypass this gate.
