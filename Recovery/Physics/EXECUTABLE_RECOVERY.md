# Executable physics recovery checkpoint — 2026-09-12

The recovered C++ implementation now reproduces the spmove modifier regions
when supplied with the selected parameter records. Full GetVHor/GetVVer and
GetKickVelocity are still pending; the Physics Recovery v0.3 gate remains closed.

## Implemented and differentially tested

- `Reference/FootballCore/FixedPoint.h`: corrected native multiply rounding and
  the nonzero divisor arithmetic. Former tests used exact products/quotients;
  fractional cases exposed the old truncation error. Multiply adds raw 512
  before extracting the 32-bit result after ten fractional bits. Divide uses
  quotient plus a signed doubled-remainder correction. Their tie rules differ.
- `Reference/FootballPhysics/NativeSqrtTable.h`: generated from the canonical
  metadata initializer `5F4A8854DFF73E49FE6168022DA8913860542337`, field index
  56186, payload offset `0x50376D`, 256 integers. Payload SHA-1 matches its
  compiler field name; payload SHA-256 is
  `3874d640b10c011383ae39af98a0700a1e20266404218ad973caa918f9d0ee4a`.
- `NativeVectorMath.h`: original Sqrt_Long lookup/iteration algorithm and
  XVector3.get_normalized, including near-unit band and small-vector precision.
  This is deliberately not ordinary floor sqrt: native sqrt(256) returns 17.
- `SpmoveBranches.h`: VHor ShootFirst then LongKick, VVer ballistic LongKick
  then Push, and the separate VVer Head branch. Optional selected property lists
  preserve native null-skip behavior. Bounds-checked access rejects malformed
  lists. The ballistic magnitude guard is reevaluated after the first modifier.
- Head subtracts param[2] from magnitude; a negative result is preserved in the
  recovered baseline. Any future gameplay clamp needs an explicit deviation.

## Evidence and its scope

| Differential run | Cases matching canonical ARM64 | Validated boundary |
| --- | ---: | --- |
| `Tools/verify_native_kernels.py` | 13,685 | Multiply, nonzero divide, five packed-vector arithmetic kernels |
| `Tools/verify_native_vector_math.py` | 15,956 | Full native sqrt/normalization bodies and composed modifiers |
| `Tools/verify_spmove_branches.py` | 7,776 | Flags, null lists, indices, guards and sequence in four native regions |

These are comparison cases, not 37,417 independent product tests. Random
corpora use fixed seeds and include negative values, ties, integer limits,
zero vectors, all property-presence combinations, and native non-1 flag bytes.
The C++ regression executable separately passes 16 named tests.

The oracle runs unmodified ARM64 instructions taken from canonical
`libil2cpp.so`, SHA-256
`2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`.
Its initialized IL2CPP class memory is synthetic. The branch harness hooks only
`Player.GetSpmoveDataRatio` at `0x196807C`, supplies selected lists/null and
asserts the original `noRatio=1` call ABI. Sqrt/normalization/arithmetic are not
stubbed. Unexpected instruction addresses and instruction-budget overruns fail.
The tests do not run Android gameplay or validate property-level selection.

Machine-readable reports carry source, binary, executable and corpus hashes:
`Recovery/Normalized/native_kernel_validation.json`,
`native_vector_validation.json`, `native_spmove_branch_validation.json`.
`Tools/check_native_evidence.py` rejects stale C++ and verifier source hashes.
Text hashes normalize UTF-8 BOM and CRLF/LF so Git checkout conversion does not
create false staleness; binary/executable hashes are byte-exact.

## Remaining work in order

1. Recover `XSpmoveManager.GetSpmoveDataNoRatio`/selection and eligibility from
   the existing canonical manager/producer disassembly. Keep selected fixtures
   as the explicit boundary until source-backed tests replace them.
2. Recover/reconstruct the missing GetVHor/GetVVer old/new base implementations
   and their config bindings. The historical 92/92 workspace has not been found;
   this checkpoint does not relabel current tests as 92/92.
3. Differentially validate complete GetVHor/GetVVer and GetKickVelocity using
   representative canonical configurations and edge cases.
4. Feed resolved velocity into BALL_CONTACT, eliminate pending impulse only for
   the fully proven path, rerun v0.2 plus end-to-end regression, then package v0.3.
5. Integrate the engine-independent recovered core into the Unreal adapter and
   test the playable field/player/ball slice with an installed UE build toolchain.

C++ `Divide` still uses a host exception for zero divisor; the original reads a
static fallback field. The older headless XVector2 Normalize function still
uses floats and is not advertised as recovered normalization. Neither limitation
is hidden by the green differential results above. `vertical_accel_raw` remains
unchanged. No full match, Unreal build, packaging or 120 FPS result is claimed.

## Reproduce

From the repository root, with canonical sources already extracted under `.local`:

```powershell
python -m pip install --target .local/pydeps unicorn==2.1.4 capstone==5.0.9
python Tools/recover_native_sqrt_table.py
Tools/build_reference.cmd
python Tools/verify_native_kernels.py
python Tools/verify_native_vector_math.py
python Tools/verify_spmove_branches.py
python Tools/check_native_evidence.py
```

The build script locates MSVC via vswhere and builds with C++17, `/W4 /WX` and
assertions enabled. The original Downloads archives and Neymar assets remain
preserved. The new vector/branch headers have no Unreal, IL2CPP or parser runtime
dependency. Unicorn and metadata parsing are offline verification tools only.

Tool API references used for this work:
[Unicorn API tutorial](https://www.unicorn-engine.org/docs/tutorial.html) and
[Il2CppDumper v6.7.46 metadata layout](https://github.com/Perfare/Il2CppDumper/blob/v6.7.46/Il2CppDumper/Il2Cpp/MetadataClass.cs).


## 2026-09-13 selection and producer increment

SpmoveSelection.h recovers max signed child ID, positive father tie handling,
config lookup and noRatio low-bit behavior. Level/order/odds fields do not pick
the winner. A missing maximum config does not fall back. Null and empty parameter
lists remain distinct. Inventory collection remains an explicit external snapshot.
Original manager functions plus native modifiers match C++ across 4,672 cases.

SpmoveProducer.h recovers calSpmoveInUse control flow with explicit context-query
inputs. Original reset, seven flag writes, strict thresholds, wrapping coordinate
differences, squared distance and native sqrt match C++ across 2,640 cases.
Original method range: 0x14C5548..0x14C5AA4. Geometry/angle, InCollection, curve
interpolation and Player.GetSpmoveData outcomes including odds remain supplied
boundaries; this is not an assertion that full eligibility is recovered.

Run Tools/build_reference.cmd then python Tools/verify_spmove_selection.py and
python Tools/verify_spmove_producer.py. Both reports are included in the central
source-binding validator and normalized manifest/import plan. Complete VHor/VVer
bases and BALL_CONTACT velocity remain pending. v0.3 stays blocked.

## 2026-09-13 inventory/cache collector increment

`Tools/analyze_spmove_inventory_collector.py` records 15 instruction anchors from
`XSpmoveManager::getSpmoveIdDict` (RVA 0x1B71AAC). Static evidence confirms the
cache guard (`+0x29` initialized, `+0x28` open-all), dictionary reset at `+0x10`,
the open-all/config-list path, and the player inventory list at `+0x30` selected
when `matchrule_skill == -1`. Both paths construct entries with native stores at
`+0x10` and `+0x14` before returning the dictionary. This is control-flow evidence
only: helper types, inventory source, eligibility/RNG and the meaning of `+0x14`
remain unresolved. The physics v0.3 gate stays blocked.

The same trace cross-checks generic helper names in the local Il2CppDumper
`script.json`: `List<int>::GetEnumerator`, `List<SpmoveIDCombine>::.ctor/Add`,
`Dictionary<int,List<SpmoveIDCombine>>::ContainsKey/get_Item/Add`,
`ModuleSingleton<SpmoveModule>::get_Instance` and `SpmoveModule::GetConfig`.
This identifies call targets at the metadata layer only; it is not proof of
managed object layout or eligibility behavior.

## 2026-09-13 engine-independent cache adapter

`Reference/FootballPhysics/SpmoveInventoryCache.h` now provides a small C++
adapter for the proven collector boundary. It models the native initialized/open-all
cache key, explicit invalidation, and source snapshots without pretending to
recover the upstream inventory provider or eligibility/RNG. Same-state calls are
cache hits; changing open-all rebuilds the normalized dictionary. This adapter is
safe to consume later from Unreal C++ and is covered by the reference regression.
