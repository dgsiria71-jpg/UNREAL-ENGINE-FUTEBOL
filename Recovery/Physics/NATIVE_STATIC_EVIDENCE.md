# Native static evidence for spmove physics

> Current executable recovery: see [EXECUTABLE_RECOVERY.md](EXECUTABLE_RECOVERY.md).
> C++ multiply/divide, native sqrt/normalization and selected-property spmove
> branches now have ARM64 differential evidence. Earlier static-only findings
> below are historical; complete velocity and property selection remain pending.


Status: PARTIAL, SOURCE-BACKED, NON-EXECUTABLE ON THIS HOST

This record preserves the static evidence recovered from the canonical Android
IL2CPP build. It is useful for narrowing the remaining spmoveInUseData
selection work, but it does not close Physics Recovery v0.3. The native binary
is ARM64 Android code and was not executed on this Windows x64 workstation.

## Inputs and provenance

- Canonical source archive: FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip.
- Extracted native library: .local/il2cpp/libil2cpp.so.
- Extracted metadata: .local/il2cpp/global-metadata.dat.
- Tool: Il2CppDumper-win-v6.7.46 generated dump.cs, il2cpp.h, and
  script.json under the ignored .local/tools/Il2CppDumper/ directory.
- Capstone ARM64 listing: .local/il2cpp/disassembly_shoot.txt.
- These generated files are scratch evidence and are intentionally excluded
  from release archives by .gitignore; this concise record is the durable
  review artifact.

## Method signatures and addresses

dump.cs and script.json agree on the following native methods:

| Method | RVA / file offset | Recovered signature |
| --- | ---: | --- |
| ShootUtility.GetVHor | 0x16E6A80 | (Player*, ShootSpeedConfigItem*, XVector2, XNumber, int goal_child, int roll, Shoot.SpmoveInUse) -> XVector3 |
| ShootUtility.GetVVer | 0x16E84A4 | (Player*, int goal_child, ShootSpeedConfigItem*, XNumber, XVector3 vHor, Shoot.SpmoveInUse, XVector2 shootPoint, XVector3 ballPos, out XVector3 shootPoint3V) -> XVector3 |
| ShootUtility.GetKickHorSpd | 0x16EB860 | (Player*, int goal_child, XVector2, XNumber, Shoot.SpmoveInUse) -> XVector3 |
| ShootUtility.GetKickVelocity | 0x16EBAD8 | (Player*, int goal_child, XVector2, XNumber, Shoot.SpmoveInUse) -> XVector3 |
| XGoal_ShootBase.calSpmoveInUse | 0x14C5548 | (XGoal_ShootBase*, int goal_child, bool calShootFirst) -> void |

The script.json decimal addresses are 24013440, 24020132, 24033376,
24034008, and 21779784 respectively. They are recorded to make accidental
address drift detectable.

## Struct and config evidence

The generated IL2CPP type dump confirms Shoot.SpmoveInUse is a seven-byte
boolean value in this field order:

~~~text
0x0 shootPush
0x1 CalmShoot
0x2 SAngleShoot
0x3 ShootFirst
0x4 Head
0x5 ShootLongKick
0x6 SwantonBomb
~~~

The canonical serialized spmoveactiondata and spmoveconfig blobs decode as
raw LZ4 blocks. Their byte-exact normalized schemas are recorded in
Recovery/Normalized/spmove_normalized.json:

- spmoveactiondata: 2163 compressed bytes -> 4332 decoded bytes -> 48 records.
- spmoveconfig: 3587 compressed bytes -> 11880 decoded bytes -> 292 records.
- The separate football-dream build is retained as a different provenance
  line; its config decodes to 312 records and is not merged.

The ShootSpeedConfigItem dump exposes the recovered curve/list fields used by
the velocity code, including Flist_vHor, vHorList, Flist_vVer,
vVerList, energyMapNew, vHorMapNew, shootStrongMapNew, vHorRateNew,
shootDisAndTime, ySpeedMin, and ySpeedMax. Field presence does not by
itself identify the exact branch, index, or interpolation semantics.

## Disassembly observations

The Capstone listing shows these control-flow facts:

1. GetKickVelocity obtains a ShootSpeedModule.GetConfigByType result,
   masks the seven-byte spmoveInUseData, calls GetVHor, then calls
   GetVVer with the saved spmove value and position arguments.
2. The final method combines packed vector components after the horizontal and
   vertical calls. The exact fixed-point operations and any player/state
   adjustment between calls remain unresolved.
3. GetVHor has old/new method branches. The packed spmove value is tested for
   byte 3 (ShootFirst) and byte 5 (ShootLongKick) in those branches.
4. GetVVer tests byte 0 (shootPush), byte 5 (ShootLongKick), and byte 4
   (Head) in separate branches.
5. calSpmoveInUse is a distinct producer of the seven flags. Its presence and
   address are confirmed, but its native body has not been translated into a
   reviewed, executable reference implementation.

These observations narrow the search and explain why a record-only table
normalizer cannot produce a trustworthy velocity. They do not prove the
VHor/VVer equations, config selection, interpolation, coordinate basis,
clamping, or final GetKickVelocity composition.

## Gate decision

The v0.3 gate remains BLOCKED. Do not emit BALL_CONTACT.velocity, remove
the ball_impulse placeholder, or package FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3
until the seven-byte producer, both modifiers, final methods, and complete
regression are source-backed. Keep the runtime field at +0x1C0 named
vertical_accel_raw.

The next bounded investigation is to translate the relevant ARM64 basic blocks
and call sites into a reviewed intermediate trace, then seek an independent
behavior oracle (original runtime or a matching 92/92 workspace). Static
translation may update this record, but it must not silently change the gate.

## Scratch artifact hashes

These hashes bind the static notes to the extracted canonical files used for
the analysis:

- libil2cpp.so: 70602416 bytes,
  SHA-256 2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496
- global-metadata.dat: 12210028 bytes,
  SHA-256 92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e
- disassembly_shoot.txt: 141824 bytes,
  SHA-256 ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58

## Producer trace: calSpmoveInUse

A second Capstone listing was generated for the producer at
RVA 0x14C5548 and checked by Tools/analyze_cal_spmove.py. The durable
intermediate report is Recovery/Normalized/cal_spmove_static_trace.json.

The following byte writes are anchored to the seven-byte struct and are
source-backed at the instruction level:

- reset() is called at 0x014C55A0, then ShootFirst (byte 3) is written from
  the low bit of the calShootFirst argument at 0x014C55AC.
- CalmShoot (byte 1) is set at 0x014C5630 after InCollection type 0x0F and
  PlayerProperty.GetSpmoveData id 0x417 produce a non-null result.
- shootPush (byte 0) is set at 0x014C566C after InCollection type 0x20 and
  GetSpmoveData id 0x41A produce a non-null result.
- SAngleShoot (byte 2) is set at 0x014C58F8 after a distance/config branch and
  GetSpmoveData id 0x418.
- ShootLongKick (byte 5) is set at 0x014C5A08 after an interpolated distance
  branch, InCollection type 0x0F, and GetSpmoveData id 0x3FC.
- Head (byte 4) is set at 0x014C5A44 after an interpolated distance branch,
  InCollection type 0x10, and GetSpmoveData id 0x3FB.
- SwantonBomb (byte 6) is set at 0x014C5A84 when goal_child equals 0x16B6 or
  0x16B3 and GetSpmoveData id 0x40B produces a non-null result.

The trace also anchors calls to CheckBallPos, GoalDoor position/center
accessors, XIntMath.Sqrt_Long, and InterpolationArray.GetInterpolation.
The semantic names of the collection IDs, the threshold fields at offsets
0x170/0x174/0x178, the contents of the returned property lists, and the
runtime result of each branch remain unresolved. This closes the field-write
layout at the instruction level, not the velocity gate.

## Manager selection trace and runtime-derived properties

A bounded manager disassembly was generated from the canonical
`libil2cpp.so` with `Tools/disassemble_spmove_manager.py`; the analyzer wrote
`Recovery/Normalized/spmove_manager_static_trace.json`. The listing is
non-executable Android ARM64 evidence, not behavior validation.

The following flows are anchored by instruction addresses:

- `GetSpmoveData` (`0x1B72758`) calls `GetSpmoveConfigByLogicId` (`0x1B72794`)
  and returns `[selected_config + 0x10]` after its non-empty check.
- `GetSpmoveDataNoRatio` (`0x1B72814`) uses the same selector and returns
  `[selected_config + 0x10]` only when the `noRatio` flag is set.
- `GetSpmoveConfigByLogicId` calls private `GetSpmoveIds` (`0x1B72DA8`) and
  branches to `GetMaxSpmoveConfigByIds` (`0x1B7264C`).
- `GetSpmoveIds` accesses the manager dictionary and performs a logic-ID list
  lookup; null remains a valid result.
- `GetMaxSpmoveConfigByIds` delegates to `GetMaxSpmoveIdByIds` and a config
  lookup. `GetSpmovesConfigByLogicId` reaches a level/odds path.

`SpmoveConfigConfigItem.param_Xnumber` is at IL2CPP offset `0x10`, but the
canonical serialized `spmoveconfig` schema has no serialized value at that
offset. This proves a runtime derivation boundary: record normalization alone
cannot supply the `GetSpmoveData` values used by the kick modifiers. Exact
selection, odds/level semantics, and the units/equations of the returned
XNumber values remain unknown. The physics gate therefore stays BLOCKED.

Manager listing scratch hash:

- `spmove_manager_disassembly.txt`: generated from the canonical library;
  source binary SHA-256 remains
  `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`.

## Buffer deserializer trace

The native buffer-reader listing is saved in ignored scratch as
`.local/il2cpp/spmove_deserialize_disassembly.txt`; its durable analysis is
`Recovery/Normalized/spmove_deserialize_static_trace.json`. The config reader
writes all ten serialized config fields and does not write
`SpmoveConfigConfigItem.param_Xnumber` at offset `0x10`. The action reader
writes the seven fields represented in the normalized action schema. This is
stronger schema evidence, while constructor/manager post-processing and
runtime property units are still unresolved. It does not close v0.3.

## Runtime construction and property forwarding trace

`Tools/disassemble_spmove_runtime.py` and
`Tools/analyze_spmove_runtime.py` produce
`Recovery/Normalized/spmove_runtime_static_trace.json` from the same
canonical Android ARM64 library. The report is deliberately marked
`behavior_validated=false`.

Anchored facts:

- `SpmoveModule.OnGameStart` skips disabled records, allocates an empty
  `List<XNumber>` for enabled records, stores it at
  `SpmoveConfigConfigItem +0x10` (`param_Xnumber`), then copies each value
  from the serialized `param` list at `+0x38` through `List<XNumber>.Add`.
- The canonical normalized archive has 292 config records, of which 183 have
  an empty `param_raw` list. This is a property of the captured archive and
  does not exclude later runtime mutation.
- `getSuccessByOdds` loads `odds` at `+0x34`, performs `odds << 10`, and
  branches to helper `0x192A1E0`; the helper's RNG/threshold behavior is
  unknown.
- `Player.GetSpmoveData` forwards the player's manager (`Player +0x28`) to
  `XSpmoveManager.GetSpmoveData`; `Player.GetSpmoveDataRatio` masks the
  noRatio argument and forwards to `GetSpmoveDataNoRatio`.
- Seven ShootUtility call sites are recorded with property IDs `0x3FE`,
  `0x3FC`, `0x3FE`, `0x3FC`, `0x3FC`, `0x41A`, and `0x3FB`, each with the
  packed flag test in its nearby control flow.

These are static data-flow facts. They do not establish property units,
selection winner, modifier equations, or executable behavior on Windows x64.
The v0.3 gate stays BLOCKED.

## Modifier list-index evidence

The durable report `Recovery/Normalized/spmove_modifier_access_static_trace.json`
anchors list accesses in `GetVHor` and `GetVVer`:

- ShootFirst property `0x3FE` reads `param_Xnumber[0]` at list-data offset
  `+0x20`, then adds the raw value to a sqrt-derived value.
- ShootLongKick property `0x3FC` reads `param_Xnumber[1]` at `+0x24` in
  `GetVHor`, and `param_Xnumber[2]` at `+0x28` in `GetVVer`.
- shootPush `0x41A` and Head `0x3FB` read `param_Xnumber[2]` at `+0x28` in
  `GetVVer`, followed by fixed-point multiply-shaped instructions.

The canonical level-wise raw values are included in the report. They are not
converted to metric units, and no level winner or equation is asserted.
