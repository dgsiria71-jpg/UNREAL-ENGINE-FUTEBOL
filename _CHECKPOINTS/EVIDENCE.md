# Evidence log
E0001: git status --short --branch -> ## No commits yet on master (exit 0); git log -3 --oneline -> fatal: your current branch master does not have any commits yet (nonzero expected).
E0002: Python SHA256 of Downloads/FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip -> 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac (exit 0). Integrity only.
E0003: git switch -c codex/unreal-football-foundation -> Switched to a new branch codex/unreal-football-foundation (exit 0).
E0004: MSVC reference build via Visual Studio 2026 VsDevCmd (x64), compiling Tests/physics_reference_tests.cpp + Reference/FootballCore/FixedPoint.cpp + Reference/FootballSimulation/BallContact.cpp with /std:c++17 /W4 /permissive- -> exit 0. Executed .local/build/reference/FootballReferenceTests.exe -> `FOOTBALL_REFERENCE_TESTS: 2/2 GREEN`. This validates the engine-independent fixed-point/contact gate only; it does not close spmove/GetVHor/GetVVer or prove v0.3.
E0005: MSVC x64 reference command re-run from repository root -> .local/build/reference/FootballReferenceTests.exe output `FOOTBALL_REFERENCE_TESTS: 2/2 GREEN` (exit 0). This covers fixed-point primitives and the authoritative/semantic/velocity contact admission gate only.
E0006: `python -m unittest discover -s Tests -p "test_*.py" -v` -> 2 tests OK (exit 0); `python Tools/Unreal/validate_content.py` -> `FOOTBALL_CONTENT_VALIDATION: GREEN (read-only provenance checks)` (exit 0); `Football.uproject | ConvertFrom-Json` -> `UPROJECT_JSON_GREEN modules=1 plugins=5` (exit 0).
E0007: `python Tools/Unreal/import_normalized_data.py` -> Recovery/Normalized/unreal_import_plan.json (exit 0). Plan retains all source hashes and explicitly lists unresolved spmove semantics as blocked.
E0008: Targeted rg/zip inspection of the extracted v0.2 baseline and migration_v1_1 archive found metadata/config evidence for spmoveInUseData, GetVHor/GetVVer/GetKickVelocity, spmoveactiondata (2163 bytes) and spmoveconfig (3587 bytes), but no persisted 92/92 workspace or native method body. v0.3 therefore remains blocked by source evidence, not by a failing test.
E0009: After aligning validators to the manifest schema (`sources` and `semantic_gates`), `python Tools/Unreal/validate_content.py` passes with `FOOTBALL_CONTENT_VALIDATION: GREEN (read-only provenance checks)`. `python -m unittest discover -s Tests -p "test_*.py" -v` passes 2/2 for the normalized contract. No Unreal Editor/UBT execution was attempted because the executable was not found.
E0010: Extended MSVC x64 reference build from `.local/build/reference` (sources include MatchSimulation.cpp) -> exit 0; executable output `FOOTBALL_REFERENCE_TESTS: 5/5 GREEN`. The added tests prove deterministic player movement, rejection of unresolved contacts, and a resolved authoritative contact reaching a goal and resetting. The velocity used by the goal test is injected as an explicit resolved fixture; it is not claimed as recovered spmove behavior.
E0011: Added `Tests/test_unreal_scaffold.py`; full repository Python discovery now runs 5/5 tests OK. The static checks cover required UE plugin declarations, Game/Client/Server target files, and the absence of a `ball_impulse` field/fallback in the Unreal contact adapter.
E0012: Renamed the project descriptor to `Football.uproject` so UBT target discovery matches `Football.Target.cs`, `FootballClient.Target.cs`, and `FootballServer.Target.cs`. JSON parse and the 5/5 Python scaffold tests pass; no stale `FootballUnreal` references remain outside ignored scratch.
E0013: Rechecked `C:\Users\dg71\AppData\Local\UnrealEngine\5.6` and sibling 5.x folders. They contain only launcher metadata/Saved manifests (1-3 tiny files per version); no `UnrealEditor.exe`, `UnrealEditor-Cmd.exe`, `UnrealBuildTool.dll`, or Build.bat is present. The UE compile/package blocker is confirmed. Visual Studio 2026 MSVC is available and used for the reference build.
E0014: Added FootballDataAssets.h (Primary Data Asset contracts with provenance and unresolved flags) and FootballInputContracts.h (Enhanced Input intent plus owner/tick command). Extended static scaffold tests; `python -m unittest discover -s Tests -p "test_*.py" -v` -> 7/7 OK.
E0015: Added the UE command queue boundary to UFootballSimulationSubsystem and a replicated AFootballBallActor. `python -m unittest discover -s Tests -p "test_*.py" -v` -> 7/7 OK; reference executable remains `FOOTBALL_REFERENCE_TESTS: 5/5 GREEN`; content validator remains GREEN. The actor replicates snapshots with DOREPLIFETIME and refuses client-side authoritative writes.
E0016: Combined post-change verification from the repository root: content validation GREEN; Python unittest discovery 7/7 OK; reference executable FOOTBALL_REFERENCE_TESTS 5/5 GREEN. A trailing-whitespace scan over source/docs/checkpoints found none. Workspace currently has 56 non-scratch files and no commit yet.
E0017: Bounded `Tools/recovery_discovery.py` scan completed in 7.7 seconds: `RECOVERY_DISCOVERY: candidates=5 archives=625`. The five path matches are unrelated assets/cache names; no advanced Physics Recovery workspace is present. Relevant mobile entries are limited to config/controller/native archives, including football-dream-be-a-pro-1-226-19.zip (a separate, hash-different Unity build); it is recorded as a candidate source and not mixed into the canonical v0.2 baseline. Report: Recovery/Normalized/recovery_discovery_report.json.
E0018: `python Tools/spmove_inventory.py` completed and wrote `Recovery/Normalized/spmove_inventory.json`. Canonical migration and the separate football-dream candidate share an identical 2163-byte spmoveactiondata entry (SHA f319f154...), but their spmoveconfig entries differ (3587 vs 3856 bytes and different SHA). The report keeps both provenance lines and leaves all velocity semantics unknown.
E0019: Full Python discovery after spmove inventory: 9/9 tests OK, including canonical/candidate blob identity and explicit unknown gate checks. `python -m py_compile` passes for all recovery, Unreal, and Blender automation scripts.
E0020: Re-executed the exact extracted v0.2 command from `07_TESTS`: `python -m unittest discover -v` -> 67 tests in 6.674s, `OK`, exit 0. The documented C:\mnt\data animation fixture was present; this confirms the stable v0.2 baseline only and does not close the native spmove gate.

E0021: Tools/decode_lz4_raw.py ran against the extracted v0.2 source/compressed
and source/decoded directories and produced LZ4_RAW_VERIFY: GREEN checked=83.
Every pair decoded byte-for-byte with strict bounds and expected-size checks.
This validates the codec and pairs, not the unresolved velocity semantics.

E0022: Tools/normalize_spmove.py decoded the canonical migration blobs and
wrote Recovery/Normalized/spmove_normalized.json. Canonical
spmoveactiondata: 2163 compressed bytes -> 4332 decoded bytes -> 48 records.
Canonical spmoveconfig: 3587 compressed bytes -> 11880 decoded bytes -> 292
records. The separate football-dream candidate has 312 config records and
remains a separate provenance line. No VHor/VVer value was inferred.

E0023: Full repository Python discovery after LZ4 and normalization work:
python -m unittest discover -s Tests -p "test_*.py" -v -> 15 tests OK, exit 0.
The new tests cover raw LZ4 literals/overlap/error bounds, canonical record
counts and decoded sizes, candidate isolation, and the still-open velocity
gate.

E0024: Il2CppDumper-win-v6.7.46 ran against the canonical Android
libil2cpp.so/global-metadata.dat and generated dump.cs, il2cpp.h, script.json,
and stringliteral.json in ignored .local scratch. The dump and script agree on
GetVHor 0x16E6A80, GetVVer 0x16E84A4, GetKickHorSpd 0x16EB860,
GetKickVelocity 0x16EBAD8, and calSpmoveInUse 0x14C5548, including their
signatures. This is static metadata evidence only.

E0025: Capstone ARM64 disassembly of the canonical native library confirms
GetKickVelocity calls config lookup, masks the seven-byte SpmoveInUse value,
calls GetVHor and GetVVer, and combines packed vector components. Branches
test ShootFirst (byte 3) and ShootLongKick (byte 5) in GetVHor, and shootPush
(byte 0), ShootLongKick (byte 5), and Head (byte 4) in GetVVer. The exact
equations, config mapping, producer semantics, and final composition remain
unresolved; the v0.3 gate stays blocked.

E0026: Added durable Recovery/Physics/NATIVE_STATIC_EVIDENCE.md and updated
Recovery/Physics/SPMOVE_HANDOFF.md plus
Recovery/Normalized/physics_runtime_contract.json to record the normalized
schema and partial native evidence without changing the blocked gate.
vertical_accel_raw remains the name for runtime +0x1C0 and no ball_impulse
fallback is emitted.

E0027: Tools/analyze_shoot_disassembly.py parsed the saved Capstone listing
into Recovery/Normalized/native_static_trace.json. It found four expected
method spans, direct GetVHor/GetVVer calls in GetKickVelocity, branch counts,
literal masks, and memory-offset hints. The trace labels itself
control-flow-and-literal-masks-only and keeps behavior_validated=false and the
physics gate blocked.

E0028: Full repository Python discovery after adding the bounded native trace
test -> 18 tests OK, exit 0. Content validation remains GREEN and the decoded
schema/native trace artifacts are present.

E0029: Corrected validation command python -m compileall -q Tools Reference
Tests completed with exit 0. Follow-up checks completed with
UPROJECT_JSON_GREEN module=Football modules=1 plugins=5,
FOOTBALL_CONTENT_VALIDATION: GREEN, the repository Python suite 18/18 OK,
and FOOTBALL_REFERENCE_TESTS: 5/5 GREEN. The earlier wildcard py_compile error
was a command-shape error only and is not treated as a product failure.

E0030: Tools/analyze_cal_spmove.py validated instruction anchors in the
canonical calSpmoveInUse ARM64 span 0x014C5548-0x014C5AA8 and wrote
Recovery/Normalized/cal_spmove_static_trace.json. The producer reset and all
seven flag writes are recorded; ShootFirst is sourced from calShootFirst & 1,
and the other writes are guarded by collection/property/goal branches. The
trace is behavior_validated=false and does not close the velocity gate.

E0031: Full repository Python discovery after the producer trace:
python -m unittest discover -s Tests -p "test_*.py" -v -> 20 tests OK, exit 0.
Content validation remains GREEN. The exact extracted v0.2 regression remains
67/67 GREEN and the C++ reference remains 5/5 GREEN.

E0032: Updated Tools/recovery_inventory.py and the generated manifest to
record normalized artifact paths and the reviewed
schema_confirmed_velocity_unresolved state. Added manifest tests; full Python
discovery now runs 22 tests OK. This keeps the schema layer importable while
preserving the blocked velocity gate.

E0033: Tools/disassemble_spmove_manager.py generated a deterministic listing of six manager regions from the canonical ARM64 library; Tools/analyze_spmove_manager.py validated 14 instruction anchors and wrote Recovery/Normalized/spmove_manager_static_trace.json. The trace confirms GetSpmoveData/GetSpmoveDataNoRatio return selected config param_Xnumber at offset 0x10 after the logic-ID selector chain. This proves a runtime derivation boundary only; selection semantics and velocity behavior remain unknown, behavior_validated=false, and v0.3 remains blocked.
E0034: Added Tests/test_spmove_manager_trace.py; targeted manager tests pass 3/3.
E0035: Post-manager full verification from the repository root: `python Tools/disassemble_spmove_manager.py` -> `SPMOVE_MANAGER_DISASSEMBLY: GREEN ranges=6`; `python Tools/analyze_spmove_manager.py` -> `SPMOVE_MANAGER_TRACE: GREEN sections=6 anchors=14`; `python -m compileall -q Tools Reference Tests` exit 0; `python Tools/Unreal/validate_content.py` -> `FOOTBALL_CONTENT_VALIDATION: GREEN`; `python -m unittest discover -s Tests -p "test_*.py" -v` -> 25/25 OK; `.local\build\reference\FootballReferenceTests.exe` -> `FOOTBALL_REFERENCE_TESTS: 5/5 GREEN`. None of these results closes the Android-native velocity gate.
E0036: Tools/disassemble_spmove_deserialize.py generated the canonical ARM64 buffer-reader listing; Tools/analyze_spmove_deserialize.py validated 17 field-store anchors. The config reader writes ten serialized fields but has no store at `param_Xnumber +0x10`, while the action reader stores all seven normalized fields. A constructor/manager post-processing path may still populate the runtime list; behavior remains unvalidated and v0.3 stays blocked.
E0037: Added Tests/test_spmove_deserialize_trace.py; targeted deserializer tests pass 3/3.
E0038: Post-deserializer verification: `python Tools/disassemble_spmove_deserialize.py` -> `SPMOVE_DESERIALIZE_DISASSEMBLY: GREEN ranges=2`; `python Tools/analyze_spmove_deserialize.py` -> `SPMOVE_DESERIALIZE_TRACE: GREEN sections=2 anchors=17`; compileall exit 0; content validation GREEN; full repository suite 28/28 OK; C++ reference `FOOTBALL_REFERENCE_TESTS: 5/5 GREEN`. The gate remains blocked because these are static/schema checks.
E0039: Tools/catalog_football_archives.py hashed and indexed 16 top-level football/futebol archives in Downloads, including canonical v0.2/v1.1 sources, legacy/support packs, separate football-dream mobile builds, and historical master archives. The catalog records no advanced 92/92 or native-disassembly workspace entries and keeps candidates isolated.
E0040: Added Tests/test_archive_catalog.py; targeted archive-catalog tests pass 2/2.

E0041: Tools/disassemble_spmove_runtime.py generated four canonical ARM64
runtime regions (OnGameStart, getSuccessByOdds, Player forwarding);
Tools/analyze_spmove_runtime.py wrote
Recovery/Normalized/spmove_runtime_static_trace.json with 15 instruction
anchors and seven ShootUtility property call sites. It confirms enabled
config List<XNumber> construction at +0x10, serialized param copying from +0x38,
odds << 10, and Player manager forwarding. The canonical normalized archive
contains 183/292 records with empty param_raw. This is static evidence only;
behavior_validated=false and the v0.3 velocity gate remains blocked.

E0042: Added `Reference/FootballGameplay/PlayableMatch.*` and wired it into
the MSVC reference build. The headless fixture covers 3v3/5v5/11v11 rosters,
server ownership, acceleration/braking, possession, pass, shot, dribble,
tackle, goalkeeper save, goal and restart. Its velocities are explicitly
new-game-authored tuning and do not claim recovered mobile semantics. The
recompiled executable reports `FOOTBALL_REFERENCE_TESTS: 13/13 GREEN`
(exit 0). The Unreal Editor/UBT is still unavailable and the v0.3 gate remains
blocked.

E0043: Added `Tools/normalize_playable_match.py` and the authored contract
`Recovery/Normalized/playable_match_contract.json`; the Unreal import plan and
read-only content validator now require/reference it. Full repository Python
discovery reports `40/40 OK`, and the MSVC headless playable fixture remains
`FOOTBALL_REFERENCE_TESTS: 13/13 GREEN`. The contract explicitly marks its
velocity tuning `new_game_authored`, keeps `ball_impulse_fallback=false`, and
leaves the mobile v0.3 gate blocked.

E0044: Commit `5242e31ebc7ec30af4e5b58a5600f3bd52786c2a` created on branch
`codex/unreal-football-foundation`, capturing the durable Unreal foundation,
static recovery traces, normalized contracts, headless playable fixture and
40-test Python suite.

E0045: Pending modifier-access trace consolidated: five parameter groups,
15 instruction anchors, Python repository suite 45/45. This was static evidence
only; the executable increments below supersede that scope for implemented math.

E0046: Native ARM64 multiply/divide exposed fractional rounding errors in
Reference/FootballCore/FixedPoint.h. Recovered C++ kernels, generated probes and
Unicorn 2.1.4 installed under ignored .local/pydeps. Final differential run:
Tools/verify_native_kernels.py -> 13,685/13,685 MATCH, exit 0. Zero-divisor
native fallback remains excluded; old trivial exact-value tests were insufficient.

E0047: Recovered XIntMath.sqrtTable from canonical metadata field 56186,
payload 0x50376D, 256 int32s. SHA-1 matches 5F4A8854DFF73E49FE6168022DA8913860542337;
SHA-256 3874d640b10c011383ae39af98a0700a1e20266404218ad973caa918f9d0ee4a.
NativeVectorMath.h reproduces Sqrt_Long and XVector3.get_normalized, including
lookup discontinuities and near-unit behavior. Final Tools/verify_native_vector_math.py
-> 15,956/15,956 MATCH, exit 0. Native sqrt/normalize code runs without arithmetic stubs.

E0048: SpmoveBranches.h implements the selected-property modifier boundary.
Tools/verify_spmove_branches.py executes two VHor regions, VVer ballistic and
VVer Head with only GetSpmoveDataRatio returning fixture selected lists/null.
Final result 7,776/7,776 MATCH, exit 0, including original flag-byte tests,
null skips, indices, magnitude guards and sequence. Manager selection and whole
GetVHor/GetVVer remain outside scope. Initial verifier completed comparisons
but hit a missing Path import while serializing the report; the import was
corrected and the entire verifier was rerun successfully.

E0049: Tools/build_reference.cmd locates MSVC through vswhere, builds all
three executables with C++17 /W4 /WX, exit 0. FootballReferenceTests is
16/16 GREEN, with added regressions for fractional arithmetic, native sqrt/
normalization quirks, zero/missing parameters and malformed-list rejection.
All three native differential reports bind implementation and verifier hashes;
Tools/check_native_evidence.py reports CURRENT. Reports remain subset-scoped.

E0050: Final repository checks: compileall exit 0; Python discovery 45/45 OK;
read-only Unreal content validation GREEN; native evidence source bindings CURRENT.
Exact original extracted v0.2 suite rerun: 67/67 OK in 4.663s, exit 0. This does
not reconstruct the missing historical 92/92 checkpoint or close v0.3. Preserved
baseline archives and Neymar assets were not modified. No UE build/FPS result.

E0051: Text-source hash bindings now normalize UTF-8 BOM and line endings for
Git portability; binary hashes remain byte-exact. Repeated all three native
suites after this verifier change: 13,685 + 15,956 + 7,776 cases matched, exit 0.
An isolated scratch copy with LF line endings was accepted; deliberately changing
FixedPoint.h was rejected by all three reports. git diff --cached --check passed.


E0052: User adopted Bible v3 execution scope. Six Master Recovery parts assembled
in ignored local directory; expected SHA 4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2 matches, CRC passes, 62 entries. Bundle explicitly excludes original 92/92 workspace; Bible's availability claim is not borne out by these files. Raw sources preserved.

E0053: Critical source matrix 122 observations, 22 duplicate groups. Videos ARM64
and metadata match existing recovery, as do critical controller/spmove/shootspeed
payloads across inspected copies. 1-226-19 not consumed.

E0054: Native selection 4,672/4,672 MATCH. Original native manager selection and
modifier functions execute; collection access/allocation/runtime hooks and upstream
inventory snapshot are explicit. Producer 2,640/2,640 MATCH against original full
calSpmoveInUse range with external geometry/membership/curve/odds query fixtures.
Flags/reset/strict thresholds and native distance/sqrt verified; full eligibility
and full kick velocity remain unresolved. Source-bound reports persisted.

E0055: MSVC /W4 /WX reference build succeeds, C++ 18/18 GREEN. Python 47/47 OK,
including negative stale producer-source/config binding checks. Evidence validator
CURRENT. Unreal content provenance GREEN. Original v0.2 suite rerun 67/67 OK in
6.593s. No historical 92-suite reconstruction, UE build or measured FPS claimed.

E0056: Inventory/cache collector trace added from canonical ARM64
XSpmoveManager::getSpmoveIdDict at RVA 0x1B71AAC. Fifteen instruction anchors
cover cache invalidation, open-all/config enumeration, player spmoveIds +0x30,
entry stores +0x10/+0x14 and dictionary return. Static control-flow only;
helper types, inventory source, eligibility/RNG and +0x14 semantics remain
unknown. Physics v0.3 remains blocked.

E0057: Inventory collector report now cross-checks eight generic helper targets
against local Il2CppDumper script metadata (ContainsKey, GetEnumerator,
constructor/Add/get_Item, SpmoveModule singleton and GetConfig). Metadata names
are persisted with script SHA; helper object layout and eligibility remain
unvalidated. Python inventory trace tests pass 4/4; v0.3 gate remains blocked.

E0058: Added engine-independent SpmoveInventoryCache adapter. It mirrors only
proven cache invalidation (initialized +0x29/open-all +0x28) and accepts explicit
unresolved source snapshots; no eligibility or RNG behavior is invented. MSVC
reference regression is now 19/19 GREEN.

E0059: Added generated feature coverage audit separating source recovery,
normalization, executable reference, Unreal integration and runtime validation.
Five critical archives (animation, physics, migration, PC 3D, ecosystem) are
physically present, SHA-bound and CRC GREEN. Audit confirms no complete-game,
complete-animation, mobile-AI or camera-runtime claim. Python suite is 54/54 OK;
Unreal content validation remains provenance-only GREEN.


E0060: `getSpmoveIdDict` static analysis expanded from 15 to 23 ARM64 anchors and
was cross-checked against dump.cs layouts. `SpmoveIDCombine +0x10/+0x14` is now
confirmed as childId/fatherId; config +0x18/+0x20/+0x28 is id/logicId/children.
Both native paths add self `(id,0)` and child `(childId,parent.id)` entries to the
appropriate logic bucket. `behavior_validated=false`; allocation, exceptions and
real-player source remain outside the claim.

E0061: `Tools/collect_spmove_inventory.py` combined the collector trace with the
previous OnGameStart enabled guard. Canonical open-all result: 292 serialized,
290 enabled, 2 disabled, 56 child references, zero missing child configs, 68
logic buckets and 346 inventory entries. Engine-independent C++ collector tests
cover open-all, player-root skipping, empty matchrule path and malformed child
rejection. MSVC C++17 /W4 /WX reference result: 21/21 GREEN.

E0062: Post-collector verification: selection native differential rerun
4,672/4,672 MATCH; source bindings CURRENT; Python repository suite 58/58 OK;
feature archive audit GREEN; Unreal content provenance GREEN; original extracted
Physics v0.2 suite 67/67 OK in 6.600s. GetVHor/GetVVer bases, final kick velocity,
BALL_CONTACT and v0.3 remain blocked.

E0063: User-authorized local tooling installation: official tagged
`@theisegoria/game-development-studio` source v1.0.2 compiled and installed as
global `game-dev`; version/capabilities/doctor run and doctor reports healthy.
Permanent main skill installed at C:\Users\dg71\.codex\skills\game-development-studio
with packaged content SHA-256 e11d373f4aef10e10b13f1aa2a1d00e2a467373951ecfe839ccc6208be464409.
The npm registry package returned 404, so installation used the official Git tag.
Upstream full tests are not GREEN on Windows: 387 passed, 78 failed, 22 skipped;
failures include POSIX process fixtures, directory fsync EPERM and missing openssl.

E0064: Published the spmove inventory collection increment to official GitHub
main through the GitHub API as c1c2a452c9e1abb27c38a2e5cff9f85a2e2a06d1.
The local terminal credential still identifies as dgrich33 and returned HTTP 403;
the authorized GitHub connector completed a non-force fast-forward from 1044d028.

E0065: Split the native GetVHor/GetVVer bases by ShootSpeedConfigItem.useNewMethod
at +0x90 and bound 26 instructions to dump.cs fields. Zero selects the legacy
Flist/vList/scalar families; nonzero selects the recovered map-driven fields.
This is static field-family proof only. Equations, units, runtime output,
GetKickVelocity and BALL_CONTACT remain blocked.

E0066: Published the GetVHor/GetVVer old/new config-path split and its 26-anchor
static trace to official GitHub main through the authorized connector as
36365baf382afd1a3b375280cd13a5f0c0b73291, fast-forward from 294c322c.
