# GetShootSpeedVRate recovery — canonical 1-221-5

Status: **normal-return equation source-bound; RNG state and upstream property semantics unresolved**.

## Evidence

- primary helper listing: `artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt`
- support listing: `artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/02_shoot_speed_v_rate_support_disassembly.txt`
- IL2CPP metadata excerpt: `artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/03_shoot_speed_v_rate_metadata.txt`
- analyzer: `Tools/analyze_shoot_speed_v_rate.py`
- trace: `Recovery/Normalized/shoot_speed_v_rate_static_trace.json`
- executable reference: `Reference/FootballPhysics/ShootSpeedVRate.h`

All three text inputs are normalized to LF before identity checks so the evidence has the same deterministic identity on Linux and Windows checkouts.

## Exact signature and field identity

The canonical Il2CppDumper metadata binds:

`GetShootSpeedVRate(XGoalTypeEnum goal_child, XNumber F, XNumber c) -> XNumber`

It also identifies `AIParameterConfig +0x80` as:

`int disArea`

The storage type is `int`. The ARM64 function consumes it directly as a signed raw delta in the same arithmetic domain as `XNumber.raw`. This proves runtime representation and use. It does not by itself prove the designer-facing authored unit or intent behind the field name.

## Normal-return equation

Let:

- `ver = GetShootVerRate(goal_child)`;
- `force_ratio = XNumber.op_Division(F, 100)`;
- `fixed_mul(a,b) = wrap32((a.raw*b.raw + 512) >> 10)`;
- `one.raw = 1024`.

The instruction order matters because fixed-point rounding is applied at every multiply:

`base = one + fixed_mul(fixed_mul(fixed_mul(ver, c), force_ratio), force_ratio)`

The force ratio is therefore applied **twice**. It must not be algebraically reassociated into one multiply because intermediate rounding and 32-bit wrapping are observable.

The sign of `c` selects the first endpoint:

- when `zero <= c`: `bound = min(one, base + disArea_raw)`;
- when `zero > c`: `bound = max(one, base - disArea_raw)`.

The normal return is:

`XRandom.Range(bound, c)`

## XRandom.Range caller-visible behavior

`XRandom.Range` calls `XRandom.NextInt(1001)`. The exact `NextInt` support body proves the returned integer is in `[0,1000]` for this positive non-power-of-two input, using rejection sampling before the modulo result is accepted.

For an accepted sample `s`:

`result = from + divide_by_int(wrap32((to - from) * s), 1000)`

where native integer division uses:

- `q = trunc(lhs_raw / rhs)`;
- `r = lhs_raw - q*rhs`;
- `result_raw = q + trunc(2*r/rhs)`.

Thus sample 0 returns the first endpoint and sample 1000 returns the second endpoint. The equation is executable when the accepted sample is provided. The original RNG state transition and the sample selected at a particular match tick remain unresolved.

## Caller in legacy GetVVer

The existing caller binding remains:

- `goal_child` from GetVVer stack `+0x54` into `w1`;
- `F` from GetVVer `x20` into `x2`;
- `c` from `ShootSpeedConfigItem.speed_vVer +0x80` into `w3`;
- call at `0x016EA330`.

The caller-visible equation needed for the legacy vertical-speed branch is now closed, conditional on:

1. the value returned by `GetShootVerRate(goal_child)`;
2. `disArea_raw`;
3. the accepted RNG sample.

## What remains

- close `GetShootVerRate` property selection and goal-child-specific values;
- bind the actual `disArea` source value from the canonical settings payload;
- recover or inject the authoritative RNG state/accepted sample at runtime;
- close the nested `shootDisAndTime` path used by new GetVVer;
- compose and differentially validate executable GetVVer/GetKickVelocity;
- bind the final resolved vector to `BALL_CONTACT.velocity`.

Physics v0.3 remains **BLOCKED**.
