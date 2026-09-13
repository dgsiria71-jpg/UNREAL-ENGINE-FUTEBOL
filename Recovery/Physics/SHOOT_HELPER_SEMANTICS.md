# Shoot helper semantic recovery — canonical 1-221-5

This note records what is now directly supported by the published ARM64 helper extraction. It is a bounded recovery artifact, not a claim that the complete kick/ball equation is finished.

## Canonical evidence

Published source:

`artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt`

- text SHA-256: `284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58`
- canonical ARM64 `libil2cpp.so` SHA-256 recorded by the extractor: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`
- analyzer: `Tools/analyze_shoot_helper_semantics.py`
- persisted machine-readable trace: `Recovery/Normalized/shoot_helper_semantics_static_trace.json`

The analyzer rechecks exact instruction anchors before emitting any conclusion.

## `0x126BF1C` — fixed-point shoot remap

The extraction window is bounded (`exact=false`) because no trustworthy `ScriptMethod` boundary was available for this address. The normal-return body is nevertheless closed by instruction flow: it returns at `0x0126C074`, and a new independent prologue begins at `0x0126C078`.

Argument mapping on the recovered normal path:

- `x0`: input
- `x1`: input minimum
- `x2`: input maximum
- `x3`: output minimum
- `x4`: output maximum

Recovered behavior:

1. If `in_min == in_max`, return `out_min` directly.
2. Clamp the input using the native comparison order:
   `input < in_min ? in_min : (input > in_max ? in_max : input)`.
3. Form the 10-bit fixed-point ratio with the already recovered native divide rule:
   - `n = (bounded - in_min) * 1024`
   - `d = in_max - in_min`
   - `q = trunc(n / d)`
   - `r = n - q*d`
   - `ratio = q + trunc(2*r / d)`
4. If the numerator is zero, use raw ratio zero without dividing.
5. Pass `(out_min, out_max, ratio)` to helper `0x126C3FC`.

This also exposed an important host-boundary issue: the older generic `FootballCore::RemapClamped` throws on equal input bounds because it calls `InverseLerp` first. That generic helper remains untouched so the older differential evidence bound to `FixedPoint.h` stays valid. The shoot-specific recovered implementation is isolated in `Reference/FootballPhysics/ShootRemap.h` and must be used for this native shoot path.

## `0x126C3FC` — fixed-point lerp helper

This extraction window is also bounded (`exact=false`), but its normal return is closed at `0x0126C534`, followed by another prologue at `0x0126C538`.

Recovered behavior:

- clamp `t` to raw `[0, 1024]`;
- compute `out_max - out_min`;
- multiply by `t` with the recovered `+512`, `>>10` XNumber multiply;
- add `out_min`.

Equivalent recovered shape:

`out_min + fixed_mul(out_max - out_min, clamp(t, 0, 1024))`

## `0x1968E24` — exact `PlayerProperty.GetShootSpeedVRate`

Il2CppDumper `ScriptMethod` metadata provides an exact function boundary:

- start: `0x01968E24`
- end: `0x0196916C`
- metadata name: `PlayerProperty$$GetShootSpeedVRate`

The recovered body directly binds these value-producing callees:

- `0x01968C34` → `PlayerProperty$$GetShootVerRate`
- `0x01FF58AC` → `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`
- AI parameter field observed at singleton offset `+0x80`
- `0x0192A0C4` → `XRandom$$Range`

The old GetVVer caller is also bound:

- `0x016EA318`: loads `ShootSpeedConfigItem +0x80` into `w3`
- `0x016EA31C`: loads the stack argument into `w1`
- `0x016EA320`: moves GetVVer `x20` into `x2`
- `0x016EA324`: passes null in `x4`
- `0x016EA330`: calls `0x1968E24`

This closes identity and the structural value chain. It does **not** yet close the complete branch-by-branch equation, input units, meaning of the AI parameter at `+0x80`, or all randomization bounds. `full_equation_recovered` therefore remains false.

## `0x196807C` — exact `PlayerProperty.GetSpmoveDataRatio`

Exact `ScriptMethod` boundary:

- start: `0x0196807C`
- end: `0x0196808C`
- metadata name: `PlayerProperty$$GetSpmoveDataRatio`

The four-instruction body is fully bound:

- load manager pointer from `PlayerProperty +0x28`;
- mask the low bit of the no-ratio argument;
- zero `x3`;
- tail-call `0x01B72814`, the already recovered `SpmoveManager.GetSpmoveDataNoRatio` path.

## Source-bound executable helper

`Reference/FootballPhysics/ShootRemap.h` now carries the recovered `0x126BF1C → 0x126C3FC` normal-path arithmetic without changing the older generic fixed-point helper or invalidating its existing differential evidence.

`Tests/remap_native_semantics_test.cpp` covers:

- the historical generic equal-bound guard remains separate;
- native shoot equal-bound behavior returns `out_min`;
- lower clamp;
- upper clamp;
- midpoint fixed-point interpolation.

This is source-bound static recovery. It is not a claim of a whole-function native differential run for GetVHor/GetVVer.

## Remaining v0.3 gate

Physics v0.3 remains **BLOCKED**. Still required:

1. close the nested `shootDisAndTime` arithmetic/time path;
2. close the full `GetShootSpeedVRate` equation/units, or prove exactly the caller-visible result behavior needed by GetVVer;
3. compose executable source-bound GetVHor/GetVVer behavior and validate it against original/native evidence;
4. close final GetKickVelocity behavior beyond the already recovered componentwise join;
5. bind the resolved result to `BALL_CONTACT.velocity` and remove unresolved placeholder/fallback behavior;
6. run complete regression;
7. only then package Physics v0.3.
