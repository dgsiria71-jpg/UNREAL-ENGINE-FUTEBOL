# Current checkpoint

Updated: 2026-09-13. Project NOT COMPLETE.
Official branch after reviewed merge: `main`.
GitHub is the canonical source of truth.

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

## Canonical shoot disassembly is now committed

Source:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- original Windows SHA-256: `ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58`
- fresh Git LF SHA-256: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`
- source identity is checked by CRLF reconstruction plus exact ARM64 instruction anchors
- analyzer: `Tools/analyze_shoot_velocity_dataflow.py`
- persisted evidence: `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
- detailed handoff: `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`

## New GetVHor recovery

Function `0x016E6A80..0x016E84A4`.

Old/new field families remain confirmed. The static dataflow now binds both interpolation/remap stages, clamp bounds and the shared fixed-point horizontal vector constructor.

Critical correction: the pre-base `0x3FE`/`0x3FC` spmove vector rewrites previously identified in GetVHor are overwritten by the shared normal-return constructor at `0x016E79D4/0x016E79D8`. Therefore they have **no surviving value contribution on the normal GetVHor return path**. Their callees may still throw or have side effects; this is not a dead-call/removal claim.

The surviving base vector uses fixed-point `+512` then `>>10` multiplication and has layout:

`XVector3(x = dir0 * speed, y = 0, z = dir1 * speed)`.

## New GetVVer recovery

Function `0x016E84A4..0x016EA55C`.

The new path is now statically bound through:

`shootDisMap -> outEnergyMaxMap -> energyMapNew/ySpeedMax -> shootPointHUpMap -> shootPointHDownMap -> shootPropertyMapNew/energyToleranceMap -> energyNeedProtect -> shootPointH clamp -> shootDisAndTime -> ySpeedMin -> base vector`.

Key interpolation/remap calls are bound at `0x016E8804`, `0x016E89F4`, `0x016E8BC8`, `0x016E8DA4`, and `0x016E8FA8`.

Post-vector new-path spmove modifiers `0x3FC` and `0x41A` **do survive** into the normal shared return. Old path binds `Flist_vVer`, `vVerList`, the base interpolation at `0x016EA188`, `speed_vVer +0x80`, external call `0x1968E24`, and the surviving post-vector `0x3FB` modifier.

Shared GetVVer return is `0x016EA52C..0x016EA554`; ABI is packed `XVector3` in `x0(low32=x, high32=y)` plus `w1=z`.

The complete arithmetic semantics are **not** yet claimed recovered.

## GetKickVelocity composition

Function `0x016EBAD8..0x016EBF14`:

- calls GetVHor at `0x016EBBA8`;
- post-processes the horizontal result;
- calls GetVVer at `0x016EBEAC`;
- final `0x016EBED8..0x016EBF04` joins **adjusted GetVHor + GetVVer componentwise** and repacks the `XVector3` ABI.

This closes the static final-join shape, not the full original runtime behavior.

## TDD / validation evidence for the static recovery increment

Branch work follows RED -> GREEN:

- `bd9b5ce1...`: RED because canonical shoot analyzer did not exist.
- `04d697999f42b2e04e08213c38e13babfde63cd1`: first static GetVHor/GetKickVelocity analyzer GREEN on Actions run `34779420198`.
- `0c220280137110c3e07eddbfa0402e5e56b8d1df`: GetVVer RED with four expected missing-field errors.
- `ad9bd0f1cb63bcdb05eeeced9d5a12c85f15d7f6`: GetVVer structural bindings GREEN on Actions run `34779664099`.
- `22e712a1698f7c806d7d01e669b9fb444979e695`: persisted-evidence RED solely because the new JSON did not yet exist.
- `cb6d6f7a0c949146d3329acee71315630121c66b`: persisted trace exact-equality gate GREEN on Actions run `34779833106`.

## One-click shoot-helper extraction handoff

The next local evidence acquisition step is now implemented without changing runtime physics:

- extractor: `Tools/disassemble_shoot_helpers.py`
- one-click Windows entry point: `tools/EXTRAIR_HELPERS_SHOOT.bat`
- local input: `.local/il2cpp/libil2cpp.so`
- optional Il2CppDumper metadata: `.local/il2cpp/script.json` or `.local/tools/Il2CppDumper/script.json`
- local output: `.local/il2cpp/shoot_helper_disassembly.txt`
- primary targets: `0x126BF1C`, `0x1968E24`, and `0x196807C`
- first-level `bl` targets observed inside the extracted primary windows are also emitted, capped at 48, using 0x200-byte bounded windows when an exact method boundary is unavailable
- an exact function boundary is claimed only from Il2CppDumper `ScriptMethod` entries when the target itself is present and the next-method boundary is sane/aligned; address-bearing `ScriptMetadata` and other groups are ignored for method boundaries; every fallback is labelled `exact=false`
- the ELF is validated as 64-bit little-endian AArch64 before extraction
- the mobile binary is read only; it is never executed or modified
- the BAT supports both the Windows `py -3` launcher and a `python` fallback, propagates the real runtime exit code, verifies that the TXT was produced, and then calls `PUBLICAR_INBOX_NO_GITHUB.ps1`
- publication destination pattern: `artifacts/native-recovery/shoot-helpers/<upload-id>/`
- the generic publisher also writes `manifests/uploads/<upload-id>.json` and preserves the local original/output

TDD evidence for this handoff:

- `ca3b94e1ca47ba0b8d69a34c7e09ea08f3454161`: initial RED; six expected failures because extractor/wrapper did not exist, Actions `34780953362`.
- `912ea7594babbff509e401f77fcb4f678266c5d3`: first bounded extractor GREEN, Actions `34781115819`.
- `211246958767195f6ee9a869b0a7f7d98a1eb228`: RED for missing first-level callee extraction and launcher fallback, Actions `34781161520`.
- `a91311615fc8eb8e5ba8249f177043e7c2a48a44`: callee extraction + launcher fallback GREEN, Actions `34781221264`.
- `790ba3a1aeadf354d5419c8ad52bd89fdfe637a4`: RED exposing stale `%ERRORLEVEL%` capture inside the parenthesized `py -3` branch, Actions `34781298854`.
- `43b315125309f1a771caff6037e9c29ddd2832cc`: runtime errorlevel capture fixed with delayed expansion; Actions `34781345344` SUCCESS.
- `fc4e6974819cbed75b426d2699e966bf285a1eab`: RED proving generic address-bearing metadata could be mistaken for a method boundary, Actions `34781471122`.
- `40bee53e0573f2b59956d8bce69976354933638f`: exact-boundary candidates restricted to `ScriptMethod`; Actions `34781512632` SUCCESS.

This tool has **not yet been executed against the user's local `libil2cpp.so` in this checkpoint**. Therefore no new helper body, helper semantic identity, or physics equation is claimed here. The next user-side action after pulling `main` is exactly:

`tools\EXTRAIR_HELPERS_SHOOT.bat`

After its publication succeeds, consume the resulting TXT from GitHub and continue the helper-level recovery from that evidence.

## Physics v0.3 gate remains BLOCKED

Do not package v0.3 yet. Remaining required evidence includes:

1. identify/recover the exact semantics of interpolation/remap helper `0x126BF1C`;
2. close the nested `shootDisAndTime` arithmetic/time path in new GetVVer;
3. identify/recover external old-path helper `0x1968E24` and any other value-producing opaque callees;
4. turn the source-bound structure into executable fixed-point GetVHor/GetVVer equations and validate them against native/original evidence;
5. close final GetKickVelocity behavior, not just the static componentwise join;
6. bind resolved result to `BALL_CONTACT.velocity`, remove unresolved fallback/placeholder behavior, and run complete regression;
7. only then consider `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip`.

## Resume rule

Do not restart architecture. Continue from `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`, `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`, and the next published `shoot_helper_disassembly.txt`. Historical documentation never overrides current binary/instruction evidence. Preserve provenance and keep `1-226-19` isolated.
