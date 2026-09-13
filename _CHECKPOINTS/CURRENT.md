# Current checkpoint

Updated: 2026-09-13. Project **NOT COMPLETE**.  
GitHub `main` is the canonical source of truth.

## Current recovery increment

- branch under review: `chatgpt/getvver-new-path-compose`
- base: `94ebc1685f8c25680dede4bbc9ae8aae75f358e3` (post-PR #7 `main`)
- completed slice: executable/source-bound **new-path GetVVer composition from already-resolved scalar/map outputs**
- Physics v0.3: **BLOCKED**
- build `1-226-19`: **isolated / not consumed**

The new executable boundary is intentionally narrower than the whole original function. It does **not** claim raw-config/native whole-function equivalence yet.

## New material in this increment

- `Reference/FootballPhysics/GetVVerNewPath.h`
- `Tools/analyze_getvver_new_path_composition.py`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`
- `Recovery/Physics/GETVVER_NEW_PATH_COMPOSITION.md`
- `Tests/test_getvver_new_path_composition.py`
- `Tests/getvver_new_path_composition_test.cpp`
- `Tests/CMakeLists.txt`

## TDD / verification

Scoped RED:

- commit `9644e50fb334438e0b457f720baf898b050c5e27`
- Actions run `34787911597`
- failure was the intended missing production header `Reference/FootballPhysics/GetVVerNewPath.h`

During GREEN, one test vector was corrected after CTest proved its arithmetic expectation was wrong; this was a test-fixture correction, not a hidden production-code workaround.

Latest verified GREEN before this checkpoint update:

- branch commit `2abc4b21a1d09f10a70e5dda9df0e76f7d67e7b0`
- Actions run `34788057471` — **SUCCESS**
- C++ compile + CTest: GREEN
- Python/persisted-evidence validation: GREEN

A fresh CI run is required again after the documentation/checkpoint commits before merge.

## What is now instruction-bound and executable

The existing recovered map/remap outputs can now be composed through the remaining new-path arithmetic:

1. energy-protection selection around `0x016E8FBC..0x016E9068`;
2. target-height adjustment:
   - positive energy delta -> fixed multiply by point-up rate;
   - nonpositive energy delta -> negative fixed multiply by point-down rate plus explicit caller-visible random-offset input;
3. base target-height + adjustment clamp at `0x016E91E4..0x016E921C`;
4. recovered `shootDisAndTime` flight-time / ballistic vertical kernel;
5. base vertical-vector construction at `0x016E9D08..0x016E9D48`;
6. surviving post-vector spmove modifiers in native order:
   - `0x3FC`
   - `0x41A`
7. both modifier blocks consume serialized `parameter[2]` and scale all three live vector components with native fixed-point multiplication.

The energy-protection selection recovered for already-resolved inputs is:

```text
protected_floor = out_energy - energy_need_protect

if protected_floor >= current_energy:
    selected_energy = current_energy
else if current_energy >= out_energy + energy_tolerance:
    selected_energy = current_energy
else:
    selected_energy = max(current_energy - energy_tolerance,
                          protected_floor)
```

Then:

```text
delta = selected_energy - out_energy

if delta > 0:
    height_adjustment = fixed_mul(delta, point_up_rate)
else:
    height_adjustment = -(fixed_mul(abs(delta), point_down_rate)
                          + downward_random_offset_raw)

vertical_delta = native_clamp(base_target_height + height_adjustment,
                              point_h_min,
                              point_h_max) - reference_y
```

The caller-visible outputs of helpers `0x1B60CC8` and `0x14DEFDC` remain explicit inputs. Their semantic identities/state are not fabricated by this slice.

## Canonical source evidence

Primary listing:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- normalized-LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- originating ARM64 `libil2cpp.so` SHA-256: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Detailed current handoffs:

- `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`
- `Recovery/Physics/SHOOT_HELPER_SEMANTICS.md`
- `Recovery/Physics/SHOOT_SPEED_V_RATE_RECOVERY.md`
- `Recovery/Physics/SHOOT_DIS_AND_TIME_RECOVERY.md`
- `Recovery/Physics/GETVVER_NEW_PATH_COMPOSITION.md`

Normalized traces:

- `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
- `Recovery/Normalized/shoot_helper_semantics_static_trace.json`
- `Recovery/Normalized/shoot_speed_v_rate_static_trace.json`
- `Recovery/Normalized/shoot_dis_and_time_static_trace.json`
- `Recovery/Normalized/getvver_new_path_composition_static_trace.json`

## Stable preserved baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 tests: 67/67 GREEN
- 83/83 source tables byte-exact
- spmove selection: 4,672/4,672 native comparisons
- spmove producer: 2,640/2,640 native comparisons

`shootDisAndTime` config 5800 remains normalized from the SHA-bound v0.2 source:

- 28 records
- 133872/133872 bytes consumed
- `[20][25] = 1327 ms`
- `flightTime raw = 1359`
- historical vertical vector anchor `vY raw = 7828`

## Remaining GetVVer gate

Do **not** claim complete GetVVer yet. Remaining work includes:

- bind/normalize the upstream production of the new-path scalar/map outputs rather than passing those outputs into the executable boundary;
- resolve enough caller-visible behavior for `0x1B60CC8` and `0x14DEFDC` to reproduce the required runtime inputs deterministically;
- bind real runtime activation/ratios for `0x3FC` and `0x41A`;
- generate native/original differential vectors for complete new-path GetVVer;
- preserve old-path GetVVer recovery separately.

After full GetVVer validation:

`GetVHor + GetVVer -> GetKickVelocity -> BALL_CONTACT.velocity -> complete regression -> only then Physics v0.3`.

## Physics v0.3 gate

Physics v0.3 remains **BLOCKED**. No fallback or approximate velocity is permitted to bypass missing native evidence.

## Workspace safety

Known user-state / Windows case-collision paths remain outside recovery branches and must not be reset/staged blindly:

- `Docs/ARCHIVE_LINEAGE_AND_HASHES.md`
- `Docs/PROJECT_SOURCE_OF_TRUTH.md`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.bat`
- `Tools/PUBLICAR_MASTER_NO_GITHUB.ps1`

Do not run destructive reset/clean/stash operations against the user's primary checkout.

## Resume rule

Do not restart architecture. Continue from the files listed above. The next bounded slice should close **upstream new-path GetVVer input production and differential validation**, not move to Unreal rendering and not package Physics v0.3.
