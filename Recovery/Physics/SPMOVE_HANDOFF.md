# spmove physics handoff

> Current executable recovery: see [EXECUTABLE_RECOVERY.md](EXECUTABLE_RECOVERY.md).
> C++ multiply/divide, native sqrt/normalization and selected-property spmove
> branches now have ARM64 differential evidence. Earlier static-only findings
> below are historical; complete velocity and property selection remain pending.


Status: BLOCKED at the evidence gate. This file records the source-backed
schema and the exact work required to produce Physics Recovery v0.3. It
intentionally does not manufacture a velocity.

## Proven source evidence

- Baseline archive: FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip
- Baseline SHA-256: 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac
- The baseline runtime schedules kickOutFrame at frame / 30 seconds and keeps
  ball_impulse unset.
- Metadata records ShootUtility.GetVHor token 0x06000559 with 7 parameters,
  GetVVer token 0x0600055A with 9 parameters, and GetKickVelocity token
  0x06000561 with 5 parameters.
- Metadata records XGoal_ShootBase.spmoveInUseData and
  GoalStateData.Shoot.spmoveInUseData, plus calSpmoveInUse.
- The migration archive contains binary config sources:
  02_GAMEPLAY_DATA/config/match/spmoveactiondata (2163 bytes)
  spmoveconfig (3587 bytes).
- The staged v0.2 tests pass after supplying the documented local animation
  fixture: 67/67 tests GREEN. This proves table parsing and bridge contracts,
  not the missing native selection semantics.

## Normalized binary schema now confirmed

The raw compressed entries are standard LZ4 raw blocks. The decoder and the
byte-exact 83-pair verification are maintained in Tools/decode_lz4_raw.py.

The canonical migration build is normalized in
Recovery/Normalized/spmove_normalized.json:

- spmoveactiondata: 2163 compressed bytes, 4332 decoded bytes, 48 records.
- Each action record consumes id, gear, condition, an int list anim_list,
  fancyId, an int list spmove_check_ids, and two XNumber raw
  speed_fix_rate values. The parser consumes the decoded stream exactly with
  no trailing bytes.
- spmoveconfig: 3587 compressed bytes, 11880 decoded bytes, 292 records.
- Each config record consumes id, enable, logicId, an int list
  childSpmoveIds, level, odds, an int list param, buffId, one-byte IsBuffId,
  and order. The parser consumes the decoded stream exactly with no trailing
  bytes.
- SpmoveConfigConfigItem.param_Xnumber is a runtime field at offset 0x10 in the
  IL2CPP type and is absent from this serialized blob. It remains an explicit
  derivation boundary; no fixed-point values are guessed here.
- The separate football-dream build has identical action bytes but a different
  spmoveconfig (3856 compressed bytes, 312 decoded records). It remains a
  separate provenance line and is never merged into the canonical baseline.

This schema confirmation is useful integration input. It does not identify
which config record or parameter produces a given VHor/VVer branch.

## Native static evidence now available

Il2CppDumper v6.7.46 and Capstone were run on the canonical Android ARM64
libil2cpp.so and global-metadata.dat. The durable review record is
Recovery/Physics/NATIVE_STATIC_EVIDENCE.md; generated dump and disassembly
remain ignored scratch files under .local.

The dump confirms these method RVAs and signatures:

- GetVHor: 0x16E6A80, Player, ShootSpeedConfigItem, XVector2, XNumber,
  goal_child, roll, SpmoveInUse -> XVector3.
- GetVVer: 0x16E84A4, Player, goal_child, ShootSpeedConfigItem, XNumber,
  vHor, SpmoveInUse, shootPoint, ballPos, out shootPoint3V -> XVector3.
- GetKickHorSpd: 0x16EB860.
- GetKickVelocity: 0x16EBAD8.
- calSpmoveInUse: 0x14C5548.

The IL2CPP type dump confirms Shoot.SpmoveInUse is seven bool bytes:
shootPush, CalmShoot, SAngleShoot, ShootFirst, Head, ShootLongKick,
SwantonBomb.

Static control-flow facts are limited but useful:

1. GetKickVelocity calls ShootSpeedModule.GetConfigByType, masks the seven
   spmove bytes, calls GetVHor, then calls GetVVer with saved spmove and
   position arguments.
2. GetVHor has old/new method branches and tests ShootFirst (byte 3) and
   ShootLongKick (byte 5).
3. GetVVer tests shootPush (byte 0), ShootLongKick (byte 5), and Head (byte 4)
   in separate branches.
4. The final method combines packed vector components after the two helper
   calls, with intermediate player/state adjustments whose semantics are not
   yet reviewed.
5. calSpmoveInUse is a distinct producer of the seven flags, but its body has
   not been translated into an executable, reviewed reference implementation.

The native code is Android ARM64 and cannot be executed as the Windows x64
runtime. Static disassembly is not behavior validation.

## Not proven

The persisted workspace still does not contain the promised 92/92 implementation
or an original-runtime behavior oracle. The following remain unknown:

- exact spmoveInUseData VHor modifier;
- exact spmoveInUseData VVer modifier;
- config selection and mapping from logicId/param to each modifier;
- list indexing, interpolation, coordinate basis, clamping, and unit scaling;
- exact fixed-point arithmetic in the old and new branches;
- final five-parameter GetKickVelocity composition;
- exact producer semantics in calSpmoveInUse;
- proof that any candidate archive shares the canonical build version.

No field at runtime +0x1C0 is renamed; it remains vertical_accel_raw.

## Required gate

1. Recover the exact spmoveInUseData VHor modifier.
2. Recover the exact spmoveInUseData VVer modifier.
3. Implement and test final GetVHor and GetVVer.
4. Implement and test final GetKickVelocity.
5. Emit BALL_CONTACT.velocity from that resolved result.
6. Remove the unresolved ball_impulse placeholder from the runtime bridge.
7. Run the complete regression and record command/output.
8. Only then package FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip.

Until all eight steps have source-backed evidence, v0.3 remains blocked and the
Unreal adapter must reject contacts whose velocity is not resolved.

## Next bounded action

Translate the ARM64 basic blocks and their called helpers into a reviewed
intermediate trace, beginning with calSpmoveInUse and the old/new branch split
in GetVHor/GetVVer. Compare each branch to the normalized curve fields without
assuming a field-to-equation mapping. Seek a matching 92/92 workspace or an
original-runtime oracle in parallel. Any static result updates this handoff
only after review; it does not silently close the gate.

## Producer progress: calSpmoveInUse

The producer now has a separate instruction-anchored trace in
Recovery/Normalized/cal_spmove_static_trace.json. It confirms the reset and
all seven byte-write destinations:

- ShootFirst is byte 3 and receives calShootFirst & 1.
- CalmShoot is byte 1, guarded by InCollection type 0x0F and property id 0x417.
- shootPush is byte 0, guarded by InCollection type 0x20 and property id 0x41A.
- SAngleShoot is byte 2, guarded by a distance/config branch and property id
  0x418.
- ShootLongKick is byte 5, guarded by interpolated distance, type 0x0F, and
  property id 0x3FC.
- Head is byte 4, guarded by interpolated distance, type 0x10, and property
  id 0x3FB.
- SwantonBomb is byte 6, guarded by goal IDs 0x16B6/0x16B3 and property id
  0x40B.

This is a meaningful producer recovery increment. It still does not prove the
collection-ID meanings, threshold units, property-list contents, or how each
flag changes the VHor/VVer equations. The eight-step v0.3 gate is therefore
unchanged.

## Manager trace: runtime `param_Xnumber` boundary

The manager regions were disassembled from the same canonical Android ARM64
library with `Tools/disassemble_spmove_manager.py` and checked by
`Tools/analyze_spmove_manager.py`. The durable report is
`Recovery/Normalized/spmove_manager_static_trace.json`.

Instruction-anchored facts:

- `GetSpmoveData` calls `GetSpmoveConfigByLogicId` and, after a non-empty
  result, returns the selected config's field at `config + 0x10`.
- `GetSpmoveDataNoRatio` uses the same selector and returns `config + 0x10`
  only when its `noRatio` input is set.
- `GetSpmoveConfigByLogicId` obtains a logic-ID list through private
  `GetSpmoveIds` and delegates selection to `GetMaxSpmoveConfigByIds`.
- `GetMaxSpmoveConfigByIds` delegates to `GetMaxSpmoveIdByIds` and a config
  lookup; the result remains nullable.
- The selector also reaches a level/odds path, but this trace does not assign
  meanings to helper calls or claim which candidate wins.

The IL2CPP type layout identifies `param_Xnumber` at offset `0x10`, while the
normalized `spmoveconfig` stream contains no value for that runtime field.
Therefore the tables are schema-complete but insufficient to reconstruct the
property values consumed by `GetSpmoveData`. A separate, source-backed runtime
derivation or behavior oracle is still required before VHor/VVer can be
resolved. The v0.3 gate remains BLOCKED.

## Buffer-reader evidence

`Tools/disassemble_spmove_deserialize.py` and
`Tools/analyze_spmove_deserialize.py` inspect the native
`SpmoveActionDataConfigItemBuffer.deserialize` and
`SpmoveConfigConfigItemBuffer.deserialize` methods. The config reader has
instruction-anchored stores for `id`, `enable`, `logicId`, `childSpmoveIds`,
`level`, `odds`, `param`, `buffId`, `IsBuffId`, and `order`; it has no store at
`SpmoveConfigConfigItem + 0x10`, the `param_Xnumber` field. The action reader
stores the seven normalized action fields, including `speed_fix_rate`.

This proves only what this buffer reader serializes. A constructor or manager
post-processing step could still populate `param_Xnumber`; that step and its
units remain unknown. The report is
`Recovery/Normalized/spmove_deserialize_static_trace.json`, and the v0.3 gate
stays BLOCKED.

## Archive search result

`Tools/catalog_football_archives.py` records hashes and selected entries for 16
football/futebol archives in Downloads. It includes the canonical physics and
migration baselines, legacy/support packs, two separate football-dream mobile
lines, and the historical v1.1 master archive. No persisted 92/92 or native
disassembly workspace was found in those entries; this is a bounded negative
result, so a newly supplied workspace may reopen the search.

## Runtime derivation trace: param_Xnumber e property calls

The new report `Recovery/Normalized/spmove_runtime_static_trace.json` is
source-backed ARM64 evidence only. It covers the runtime path between the
serialized config and the property calls used by ShootUtility:

- `SpmoveModule.OnGameStart` checks `enable` at `+0x1C`, creates a
  `List<XNumber>`, stores it at `param_Xnumber +0x10`, and enumerates the
  serialized `param` list at `+0x38`; each current value is passed to
  `List<XNumber>.Add` as a raw integer.
- In the canonical normalized config, 183 of 292 records have an empty
  `param_raw` list. This is an archive observation, not proof that a later
  runtime path cannot mutate the lists.
- `getSuccessByOdds` loads `odds` at `+0x34`, shifts it left by 10 bits, and
  enters opaque helper `0x192A1E0`. The XNumber scaling is anchored; RNG and
  threshold semantics are not.
- `Player.GetSpmoveData` and `Player.GetSpmoveDataRatio` load the player
  manager at `Player+0x28`; the ratio method masks `noRatio` to bit 0 and
  forwards to the manager selectors.
- ShootUtility has seven anchored property calls through
  `Player.GetSpmoveDataRatio`: IDs `0x3FE`, `0x3FC`, `0x3FE`, `0x3FC`, `0x3FC`,
  `0x41A`, and `0x3FB`, guarded by the corresponding packed flag masks.

This narrows the missing derivation boundary but does not recover the
VHor/VVer modifiers, config selection, units, or equations. `physics_gate`
therefore remains `blocked`; no velocity or `BALL_CONTACT` fallback is
admitted and v0.3 is not packaged.

## Modifier list-index trace

`Tools/analyze_spmove_modifier_access.py` writes
`Recovery/Normalized/spmove_modifier_access_static_trace.json` from the
canonical `GetVHor`/`GetVVer` listing. It anchors a concrete part of the
spmove modifier path:

- `GetVHor` reads the `0x3FE` list at index 0 (`+0x20`) and the `0x3FC` list
  at index 1 (`+0x24`); both values are added to a sqrt-derived raw value.
- `GetVVer` reads index 2 (`+0x28`) for `0x3FC`, `0x41A`, and `0x3FB`, then
  enters a fixed-point multiply-shaped sequence.
- The canonical level values at those indices are preserved: `0x3FE`
  `[1500, 2000, 2500, 3000, 3500]`, `0x3FC` VHor
  `[4000, 4500, 5000, 5500, 6000]`, `0x3FC`/`0x41A` VVer
  `[900, 800, 700, 600, 500]`, and `0x3FB` VVer
  `[300, 600, 900, 1200, 1500]`.

This is a list-index and operation-shape recovery increment. It does not
prove level selection, scaling, coordinates, equations or executable behavior;
`behavior_validated=false` and the v0.3 gate remains BLOCKED.
