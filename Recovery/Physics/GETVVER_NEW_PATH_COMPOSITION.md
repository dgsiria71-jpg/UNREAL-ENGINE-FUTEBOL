# New-path GetVVer composition recovery

Status: resolved-scalar composition instruction-bound and executable. Physics v0.3 remains **BLOCKED**.

## Evidence boundary

The behavioral source remains the canonical ARM64 listing from mobile build `1-221-5`:

- `GetVVer`: `0x016E84A4..0x016EA55C`
- canonical listing: `artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`
- normalized-LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- originating `libil2cpp.so` SHA-256: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

This increment composes the already recovered `shootDisAndTime` vertical kernel with the instruction-bound energy-protection/target-height path, the base vertical-vector construction, and the surviving `0x3FC` / `0x41A` spmove modifiers.

It deliberately starts from **already-resolved scalar/map outputs**. It is not yet a raw-config, whole-function differential clone of `GetVVer`.

## Energy-protection selection

The relevant range begins at `0x016E8FBC`, where `ShootSpeedConfigItem +0x94` is loaded as the protection amount used by this path.

For already-resolved values:

- `out_energy`
- `current_energy`
- `energy_tolerance`
- `energy_need_protect`

normal-path selection is recovered as:

```text
protected_floor = out_energy - energy_need_protect

if protected_floor >= current_energy:
    selected_energy = current_energy
else if current_energy >= out_energy + energy_tolerance:
    selected_energy = current_energy
else:
    selected_energy = max(
        current_energy - energy_tolerance,
        protected_floor)
```

This follows the comparison/select order at `0x016E8FD8..0x016E9068`.

## Target-height adjustment

The delta is formed as:

```text
delta = selected_energy - out_energy
```

For `delta > 0`, the path at `0x016E90F0..0x016E9108` applies the already-resolved point-up rate:

```text
height_adjustment = fixed_mul(delta, point_up_rate)
```

For `delta <= 0`, the path at `0x016E9140..0x016E91A0` uses `abs(delta)`, the already-resolved point-down rate, and the caller-visible result of helper `0x1B60CC8`:

```text
height_adjustment = -(
    fixed_mul(abs(delta), point_down_rate)
    + downward_random_offset_raw)
```

The helper at `0x1B60CC8` is called with integer arguments `0` and `100`. Its exact identity/state semantics are **not** claimed by this slice; its caller-visible output is an explicit input to the executable reference.

A base target-height scalar is produced by call `0x016E91B8 -> 0x14DEFDC`. This helper is also left as an explicit upstream input rather than guessed.

The bounds pair loaded at `0x016E91E4` is then used with the original comparison order:

```text
vertical_delta =
    native_clamp(
        base_target_height + height_adjustment,
        point_h_min,
        point_h_max)
    - reference_y
```

## Recovered vertical kernel join

`vertical_delta` feeds the already recovered `shootDisAndTime` kernel in `Reference/FootballPhysics/ShootDisAndTime.h`:

```text
flight_time = lookup shootDisAndTime(vHor magnitude, horizontal distance)
solved_y_speed = (vertical_delta - vertical_accel_raw*t*t/2) / t
solved_y_speed = native clamp(ySpeedMin, ySpeedMax)
```

The previous slice already source-bound the table lookup, milliseconds conversion, zero-row fallback, fixed-point ballistic operation order and y-speed clamp.

## Base vector

At `0x016E9D08..0x016E9D48`, the solved scalar is multiplied into all three components of the vertical direction using the native fixed-point `+512 >> 10` rule:

```text
base_vver = vertical_direction * solved_y_speed
```

The executable reference represents this with `RecoveredXVector3` and `BuildVerticalVector`.

## Surviving spmove modifiers

The new path then conditionally applies, in order:

1. logic `0x3FC` at `0x016E9DF0`;
2. logic `0x41A` at `0x016E9F30`.

Both calls use `PlayerProperty.GetSpmoveDataRatio`, already identified exactly at `0x0196807C..0x0196808C`.

For both blocks, the value-producing parameter is the third serialized element (`parameter[2]`, backing-array offset `+0x28`). The block scales every live vector component using native fixed-point multiplication. The rewritten vector remains live into the new-path exit and shared `GetVVer` return.

The executable composition therefore applies:

```text
result = base_vver
if 0x3FC active:
    result *= ratio_3fc_parameter_2
if 0x41A active:
    result *= ratio_41a_parameter_2
```

This is a surviving return-value contribution, unlike the pre-base `GetVHor` rewrites that are overwritten later.

## Executable material

- `Reference/FootballPhysics/GetVVerNewPath.h`
  - `SelectProtectedEnergy`
  - `ComputePointHeightAdjustment`
  - `ComputeVerticalDelta`
  - `BuildVerticalVector`
  - `ApplyGetVVerModifier`
  - `ComposeNewGetVVerFromResolvedScalars`
- `Tools/analyze_getvver_new_path_composition.py`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`
- `Tests/test_getvver_new_path_composition.py`
- `Tests/getvver_new_path_composition_test.cpp`

## TDD evidence

The scoped RED was commit `9644e50fb334438e0b457f720baf898b050c5e27`.

GitHub Actions run `34787911597` failed in C++ compilation because `Reference/FootballPhysics/GetVVerNewPath.h` did not yet exist. Existing targets compiled up to the new target, proving the intended missing-production-code failure.

After implementation, an intermediate CTest exposed an arithmetic mistake in a test vector, not a production discrepancy. The vector was corrected so non-clamped and upper-clamped target-height behavior are tested separately.

The current branch head after that correction is `2abc4b21a1d09f10a70e5dda9df0e76f7d67e7b0`; Actions run `34788057471` completed **SUCCESS**, including C++ compilation/CTest and persisted-evidence validation.

## Remaining gate

This slice does **not** claim complete `GetVVer` equivalence. Still required before that claim:

- bind/normalize remaining upstream map-output production from the raw new-method configuration rather than supplying those outputs as scalar inputs;
- identify or caller-bind the required behavior of `0x1B60CC8` and `0x14DEFDC` sufficiently for deterministic reproduction;
- bind runtime activation and concrete recovered ratios for `0x3FC` / `0x41A` from real state;
- create native/original differential vectors for complete new-path `GetVVer`;
- then compose/validate final `GetKickVelocity` and `BALL_CONTACT.velocity`.

Physics v0.3 remains **BLOCKED**.
