# Shoot velocity static recovery — canonical ARM64 evidence

Status: **PARTIAL / source-bound / Physics v0.3 still BLOCKED**.

Canonical source:

- `artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`
- original Windows SHA-256: `ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58`
- Git fresh-checkout LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- Git LF content is accepted only after CRLF reconstruction hashes back to the original source SHA.
- machine-readable trace: `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
- analyzer: `Tools/analyze_shoot_velocity_dataflow.py`

This document supersedes earlier static interpretations where they conflict with the exact later dataflow described below. It does **not** claim executable/runtime equivalence.

## GetVHor

Function span: `0x016E6A80..0x016E84A4`.

The old/new config split remains confirmed through `ShootSpeedConfigItem.useNewMethod +0x90`.

### New path

The static map chain is now instruction-bound:

- `energyMapNew +0xB8` provides the bracket/key side;
- `vHorMapNew +0xC0` provides mapped horizontal speed values;
- interpolation/remap helper call: `0x016E6DE0 -> 0x126BF1C`;
- player property id `0x3B` is read before the second map stage;
- `shootStrongMapNew +0xC8` / `vHorRateNew +0xD0` feed the second interpolation/remap call at `0x016E6FEC`;
- new-path clamp bounds are loaded from `+0xA8` at `0x016E72C0`.

### Old path

- `Flist_vHor +0x18` / `vHorList +0x20` feed the old interpolation/remap call at `0x016E73B0`;
- `speed_vHor +0x74` is loaded at `0x016E745C`;
- old-path clamp bounds are loaded from `+0x78` at `0x016E794C`.

### Shared horizontal-vector constructor

Both paths converge on the shared clamp and fixed-point constructor. The final multiply shape is source-bound to `+0x200` bias followed by `>>10`, matching the 1024 fixed-point scale already recovered in `FixedPoint`.

Normal return slots are overwritten at:

- `0x016E79D4`: packed first two components;
- `0x016E79D8`: third component.

The surviving base layout is:

`XVector3(x = dir0 * speed, y = 0, z = dir1 * speed)`

with fixed-point scaling.

### Important correction: pre-base VHor spmove blocks

Earlier work correctly identified `0x3FE` index 0 and `0x3FC` index 1 accesses and the temporary vector rewrites. The new complete control/dataflow review adds an important correction:

- new-path logic-id loads: `0x016E7038` (`0x3FE`) and `0x016E7170` (`0x3FC`);
- old-path logic-id loads: `0x016E76C4` (`0x3FE`) and `0x016E77FC` (`0x3FC`);
- their temporary vector values do **not** survive the normal GetVHor return path because the same vector slots are subsequently overwritten by the shared base constructor at `0x016E79D4/0x016E79D8`.

This proves **no surviving value contribution on the normal return path**. It does not prove the calls can be deleted: exceptions or side effects remain possible until those callees are fully characterized.

## GetVVer

Function span: `0x016E84A4..0x016EA55C`.

The old/new field-family split remains confirmed, and the major structural dataflow is now instruction-bound.

### New path

The function first derives a planar/distance-like scalar from packed inputs (`0x016E85C8..0x016E85FC`, ending at the already-known sqrt helper).

The subsequent source-bound map chain is:

- `shootDisMap +0xE8` at `0x016E8630`;
- `outEnergyMaxMap +0x100` at `0x016E8768`;
- interpolation/remap at `0x016E8804`;
- `ySpeedMax +0xA0` at `0x016E8830`;
- `energyMapNew +0xB8` at `0x016E8908`;
- interpolation/remap at `0x016E89F4`;
- `shootPointHUpMap +0xF8` at `0x016E8B2C`, interpolation at `0x016E8BC8`;
- `shootPointHDownMap +0xF0` at `0x016E8D08`, interpolation at `0x016E8DA4`;
- `shootPropertyMapNew +0xD8` at `0x016E8DF4`;
- `energyToleranceMap +0xE0` at `0x016E8F08`, interpolation at `0x016E8FA8`;
- `energyNeedProtect +0x94` at `0x016E8FBC`;
- `shootPointH` pair at `0x016E91E4`, clamped/written through `0x016E921C`;
- `shootDisAndTime +0x108` at `0x016E92E4`;
- `ySpeedMin +0x98` at `0x016E9CB4`;
- base vertical-vector construction at `0x016E9D08..0x016E9D48`.

Unlike the pre-base GetVHor rewrites, the post-vector GetVVer spmove modifiers **do survive** into the normal return path:

- `0x3FC` load at `0x016E9DF0`;
- `0x41A` load at `0x016E9F30`;
- both rewrite the constructed vector and remain live into the shared return at `0x016EA52C`.

Their canonical index-2 parameter families remain the previously recovered values; this document does not manufacture missing selection/units semantics.

### Old path

- `Flist_vVer +0x28` at `0x016E9FCC`;
- `vVerList +0x30` at `0x016EA0E4`;
- base interpolation/remap call at `0x016EA188`;
- base vector construction at `0x016EA1B0..0x016EA1F0`;
- `speed_vVer +0x80` at `0x016EA318`, entering external call `0x1968E24` at `0x016EA330`;
- optional `0x3FB` spmove block starts at `0x016EA418` and its final rewritten vector at `0x016EA4F0..0x016EA528` survives to return.

Shared return range: `0x016EA52C..0x016EA554`.

ABI: `XVector3` is returned packed as `x0(low32=x, high32=y)` plus `w1=z`.

## GetKickVelocity

Function span: `0x016EBAD8..0x016EBF14`.

Confirmed call/composition structure:

1. `GetVHor` call at `0x016EBBA8`;
2. horizontal result is post-processed/scaled before vertical calculation;
3. `GetVVer` call at `0x016EBEAC`;
4. final range `0x016EBED8..0x016EBF04` adds adjusted GetVHor and GetVVer component-by-component and repacks the `XVector3` return.

Therefore the final join is now statically proven as:

`adjusted_GetVHor + GetVVer` componentwise.

This is not yet a complete implementation because all upstream GetVVer arithmetic/helper semantics and the final `BALL_CONTACT.velocity` binding have not been closed.

## What remains unknown

- exact arithmetic semantics of every `0x126BF1C` remap/interpolation call;
- the complete `shootDisAndTime` nested lookup/time arithmetic in the new GetVVer path;
- semantic identity/equations of external calls such as `0x1968E24` in the old path;
- exceptional-path behavior for manager/property calls;
- final `BALL_CONTACT.velocity` integration and original-runtime differential equivalence.

## Gate

Physics Recovery v0.3 remains **BLOCKED**. No fallback velocity is permitted. The next evidence step is to disassemble and identify the unresolved helper callees, then turn the now-bound static structure into executable fixed-point equations and validate them before touching the v0.3 release gate.
