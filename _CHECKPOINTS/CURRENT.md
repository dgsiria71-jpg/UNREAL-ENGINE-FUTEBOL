# Current checkpoint

Updated: 2026-09-13. Project NOT COMPLETE.
Official branch after reviewed merge: `main`.
GitHub is the canonical source of truth.

## Active recovery increment

- worktree branch: `codex/shoot-dis-and-time`
- base HEAD: `1870232f51aaab412ca1d2c3a4a79d3a016b03da` (`origin/main`)
- task completed in this increment: source-bound `shootDisAndTime` lookup, milliseconds conversion, ballistic vertical kernel and native-order clamp
- current next task: compose the complete executable new-path GetVVer around the recovered upstream target-height/energy path and surviving spmove modifiers
- Physics v0.3 remains BLOCKED

Files changed by this increment:

- `Tools/analyze_shoot_dis_and_time.py`
- `Tools/extract_shoot_dis_and_time_metadata.py`
- `Tools/normalize_shoot_dis_and_time.py`
- `Reference/FootballPhysics/ShootDisAndTime.h`
- `Tests/test_shoot_dis_and_time_semantics.py`
- `Tests/shoot_dis_and_time_semantics_test.cpp`
- `Tests/CMakeLists.txt`
- `Recovery/Normalized/shoot_dis_and_time_static_trace.json`
- `Recovery/Normalized/shoot_dis_and_time_config_5800.json`
- `Recovery/Physics/SHOOT_DIS_AND_TIME_RECOVERY.md`
- the source-bound metadata excerpt beside the canonical shoot listing
- recovery manifest, physics handoffs and this checkpoint

Latest local validation:

- focused RED: 4 expected failures while analyzer, reference and persisted evidence were absent
- focused GREEN: 5/5 `test_shoot_dis_and_time_semantics`
- C++ local build: MSVC 19.51; 4/4 CTests GREEN, including `ShootDisAndTimeSemantics`
- full Python discovery: 99 tests GREEN, 5 skipped because their optional local fixtures are absent
- native evidence bindings: CURRENT
- Unreal persisted content validation: GREEN

Confirmed in this increment:

- `ShootSpeedConfigItem +0x108` is metadata-bound to `List<List<int>> shootDisAndTime`
- outer table axis uses floor/ceiling neighbors of `XVector3.magnitude(vHor)`
- inner row axis uses integer neighbors of horizontal shoot distance
- table values are integer milliseconds converted through `XNumber.thousand`
- missing row intervals yield zero; paired row times use the nonzero sample when only one is zero
- final flight time is fixed-point interpolated across distance and horizontal speed
- vertical solve preserves `(delta_y - vertical_accel_raw*t*t/2)/t` operation order
- final y speed uses the native `ySpeedMin/ySpeedMax` comparison order
- canonical config 5800 source anchor `[20][25]=1327 ms` reproduces `flightTime raw=1359` and `vY raw=7828`

Still unknown:

- complete executable upstream target-height/energy-protection path
- surviving post-vector spmove modifiers `0x3FC` and `0x41A` in complete GetVVer
- full GetKickVelocity runtime behavior and BALL_CONTACT binding
- malformed/null table exception behavior outside canonical data preconditions

Known preserved dirty baseline outside this increment:

- `Docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `Docs/PROJECT_SOURCE_OF_TRUTH.md`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`

These four paths are Windows case-collision/user-state files and must not be staged by this branch.

Exact resume command:

```powershell
Set-Location 'C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL\.local\worktrees\shoot-dis-and-time'
git status --short --branch
python Tools/analyze_shoot_dis_and_time.py
python -m unittest discover -s Tests -p 'test_*.py'
```

## Canonical architecture and source policy

- Windows PC / Unreal Engine 5.x
- C++ primary gameplay/simulation core; Blueprint complementary
- Blender is the 3D source of truth
- mobile build `1-221-5` is the canonical recovery baseline
- build `1-226-19` remains isolated until explicitly compared and approved
- Neymar v1.9 remains PAUSED

## Repository publication

Recovered master is published through Git LFS:

- `artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`
- bytes `794639566`
- SHA-256/LFS OID `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`
- publication commit `c58cd352fa79bb791a9b8d4d6bff88a098cdbc20`

Historical package audit/delta evidence is published under `artifacts/audits/` and `artifacts/package-deltas/`. It confirmed physically present historical deliveries and showed that several packages are complementary rather than superseding. The two `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11` copies are exact archive duplicates.

The original historical 92/92 advanced workspace bytes are still **not** proven recovered. Do not manufacture a 92/92 status from newer tests.

## Stable physics baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 suite: 67/67 GREEN
- 83/83 source tables byte-exact
- spmove selection: 4,672/4,672 native comparisons match
- spmove producer: preserved 2,640/2,640 native comparisons match
- open-all collector boundary: 292 serialized configs, 290 enabled, 2 disabled, 56 child refs, 68 logic buckets, 346 entries

## Canonical shoot disassembly

Source:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- original Windows SHA-256: `ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58`
- fresh Git LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- source identity is checked by CRLF reconstruction plus exact ARM64 instruction anchors
- analyzer: `Tools/analyze_shoot_velocity_dataflow.py`
- persisted evidence: `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
- detailed handoff: `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`

## GetVHor recovery

Function `0x016E6A80..0x016E84A4`.

Old/new field families remain confirmed. The static dataflow binds both interpolation/remap stages, clamp bounds and the shared fixed-point horizontal vector constructor.

Critical correction: the pre-base `0x3FE`/`0x3FC` spmove vector rewrites previously identified in GetVHor are overwritten by the shared normal-return constructor at `0x016E79D4/0x016E79D8`. Therefore they have **no surviving value contribution on the normal GetVHor return path**. Their callees may still throw or have side effects; this is not a dead-call/removal claim.

The surviving base vector uses fixed-point `+512` then `>>10` multiplication and has layout:

`XVector3(x = dir0 * speed, y = 0, z = dir1 * speed)`.

## GetVVer recovery

Function `0x016E84A4..0x016EA55C`.

The new path is statically bound through:

`shootDisMap -> outEnergyMaxMap -> energyMapNew/ySpeedMax -> shootPointHUpMap -> shootPointHDownMap -> shootPropertyMapNew/energyToleranceMap -> energyNeedProtect -> shootPointH clamp -> shootDisAndTime -> ySpeedMin -> base vector`.

Key interpolation/remap calls are bound at `0x016E8804`, `0x016E89F4`, `0x016E8BC8`, `0x016E8DA4`, and `0x016E8FA8`.

Post-vector new-path spmove modifiers `0x3FC` and `0x41A` **do survive** into the normal shared return. Old path binds `Flist_vVer`, `vVerList`, the base interpolation at `0x016EA188`, `speed_vVer +0x80`, external call `0x1968E24`, and the surviving post-vector `0x3FB` modifier.

Shared GetVVer return is `0x016EA52C..0x016EA554`; ABI is packed `XVector3` in `x0(low32=x, high32=y)` plus `w1=z`.

The complete GetVVer arithmetic semantics are **not** yet claimed recovered.

## GetKickVelocity composition

Function `0x016EBAD8..0x016EBF14`:

- calls GetVHor at `0x016EBBA8`;
- post-processes the horizontal result;
- calls GetVVer at `0x016EBEAC`;
- final `0x016EBED8..0x016EBF04` joins **adjusted GetVHor + GetVVer componentwise** and repacks the `XVector3` ABI.

This closes the static final-join shape, not the full original runtime behavior.

## Published shoot-helper extraction and new semantic recovery

The one-click extractor has now been executed successfully against the user's canonical local ARM64 `libil2cpp.so` and its output is committed:

`artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt`

- text SHA-256: `284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58`
- binary SHA-256 recorded by the extractor: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`
- analyzer: `Tools/analyze_shoot_helper_semantics.py`
- persisted trace: `Recovery/Normalized/shoot_helper_semantics_static_trace.json`
- detailed evidence note: `Recovery/Physics/SHOOT_HELPER_SEMANTICS.md`

The Windows handoff now writes generated evidence to `.local/recovery-output/shoot_helper_disassembly.txt`, separate from the native-input directory, and publishes it through the generic GitHub uploader. The original `libil2cpp.so` remains read-only and unmodified.

### `0x126BF1C` normal-path remap arithmetic

The extraction window remains conservatively labelled `exact=false` because no trustworthy `ScriptMethod` boundary was available. The normal return is nevertheless instruction-bound at `0x0126C074`, with a new independent prologue at `0x0126C078`.

Recovered normal behavior:

- arguments map to `(input, in_min, in_max, out_min, out_max)` in `x0..x4`;
- equal input bounds return `out_min` directly;
- input is clamped using the native comparison order;
- the 10-bit fixed-point inverse-lerp ratio uses the recovered divide shape `q + trunc(2*r/d)`;
- a zero numerator selects raw ratio zero without dividing;
- the result is passed to helper `0x126C3FC`.

`0x126C3FC` is also a bounded extraction window rather than a metadata-proven function boundary, but its normal return is closed at `0x0126C534`. It clamps `t` to raw `[0,1024]` and computes:

`out_min + fixed_mul(out_max - out_min, t)`

with the already recovered `+512`, `>>10` fixed multiply.

A source-bound implementation now exists at `Reference/FootballPhysics/ShootRemap.h`. It is intentionally separate from the older generic `FootballCore::RemapClamped`: the latter remains whole-file SHA-bound by existing native differential evidence, so changing it without regenerating those native reports would invalidate provenance. `Tests/remap_native_semantics_test.cpp` covers equal bounds, lower clamp, upper clamp and midpoint behavior for the shoot-specific helper while preserving the older generic evidence boundary.

### `0x1968E24` exact identity and value chain

Il2CppDumper `ScriptMethod` metadata provides an exact boundary:

- start `0x01968E24`
- end `0x0196916C`
- `PlayerProperty$$GetShootSpeedVRate`

Directly bound value-producing callees include:

- `0x01968C34` -> `PlayerProperty$$GetShootVerRate`
- `0x01FF58AC` -> `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`
- observed AI config field at singleton offset `+0x80`
- `0x0192A0C4` -> `XRandom$$Range`

The old GetVVer caller is also bound at `0x016EA318..0x016EA330`, including the `ShootSpeedConfigItem +0x80` load into `w3` and the call to `0x1968E24`.

The follow-up trace `Recovery/Normalized/shoot_speed_v_rate_static_trace.json` now closes the normal-return equation, binds `+0x80` to `int disArea`, and closes the caller-visible discrete range interpolation. Upstream `GetShootVerRate` values, designer-facing `disArea` convention and original RNG state remain unresolved.

### `0x196807C` exact forwarding semantics

Exact metadata boundary:

- start `0x0196807C`
- end `0x0196808C`
- `PlayerProperty$$GetSpmoveDataRatio`

The four-instruction body loads the manager from `PlayerProperty +0x28`, masks the low bit of the no-ratio argument, zeroes `x3`, and tail-calls the already recovered `SpmoveManager.GetSpmoveDataNoRatio` at `0x01B72814`.

## TDD / verification evidence for helper-semantic increment

- `a0693931147de82a4f5d452d4bf9bc49c5ba4621`: RED because the semantic analyzer/persisted evidence did not yet exist.
- `da92bf249f26455046296450afd99068ea677f28`: semantic anchors pass; only persisted-trace gate remains RED.
- `c0211fb9df40e605d358b473f7bd2bfe37d0f65f`: persisted trace exact-equality gate GREEN, Actions run `34784114057` SUCCESS.
- `bd9bab264b8fbca8202c9f9e1e742f0d065a98a1`: CTest RED proves the older generic `RemapClamped` does not have the native shoot equal-bound behavior; it throws on divide-by-zero.
- `c3d022de7c2fd728a1fe3b88f7875bceabc44cbb`: exploratory generic-helper edit makes the new CTest pass but correctly trips five stale native-evidence bindings for `FixedPoint.h`; this change was not accepted as the final architecture.
- `e1f3280a923e9633f61e949c5dc07c25f0f02a85`: restores the previously validated `FixedPoint.h` evidence boundary.
- `800b3a69a9dd7331c8b5ca8ec5b89370fcaf8d63`: scoped RED for missing `Reference/FootballPhysics/ShootRemap.h`, Actions run `34784265785`.
- `e49a16a4b0e561c60977952bd7e0ed7e2099bba0`: source-bound shoot remap GREEN, Actions run `34784291595` SUCCESS; C++ build, two CTests, Python/native evidence checks and Unreal persisted-content validation all pass.
- `2be52efc63182592db3f048725ff53d55ea949a9`: helper semantic trace registered in the recovery manifest, Actions run `34784415498` SUCCESS.

## Physics v0.3 gate remains BLOCKED

Do not package v0.3 yet. Remaining required evidence includes:

1. close the nested `shootDisAndTime` arithmetic/time path in new GetVVer;
2. supply the now-closed `GetShootSpeedVRate` equation with recovered upstream property/config/RNG inputs;
3. compose executable source-bound GetVHor/GetVVer behavior and validate it against original/native evidence;
4. close final GetKickVelocity behavior, not just the static componentwise join;
5. bind the resolved result to `BALL_CONTACT.velocity`, remove unresolved fallback/placeholder behavior, and run complete regression;
6. only then consider `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip`.

## Resume rule

Do not restart architecture. Continue from `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`, `Recovery/Physics/SHOOT_HELPER_SEMANTICS.md`, `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`, `Recovery/Normalized/shoot_helper_semantics_static_trace.json`, and the committed helper disassembly. Historical documentation never overrides current binary/instruction evidence. Preserve provenance and keep `1-226-19` isolated.
