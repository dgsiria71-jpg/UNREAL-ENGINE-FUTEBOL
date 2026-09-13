# Current checkpoint

Updated: 2026-09-13. Project NOT COMPLETE.
Branch: codex/unreal-football-foundation.
HEAD before this increment: 62aaa05428b217b60926663f18b2641e5b15f074 (run `git rev-parse HEAD` for the current checkpoint commit).
Continuation base: 4d672ab5dccbe7ba9b238de9b8202086e759931e.

## GitHub publication

Official remote: https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL.git, main.
Reconciled remote history from 6760d3d with local c0d761c; no history rewritten.
Bible text and its policies are preserved in Docs/Bible_v3. Raw master LFS upload
remains unperformed; code publication does not claim binary publication.
Remote publication before this increment: main -> 1044d0285aee91a324df47ebb529956142d4e59d.

## Authority

User explicitly adopted Bible v3, its Quickstart and Source Policy after full
reading. Latest direct user corrections remain highest authority; current binary,
hash and test evidence overrides stale technical claims. Windows UE5.x/C++ final,
Blueprint complementary, Blender source of truth, Neymar v1.9 PAUSED. New source
discovery only Downloads/Videos. 1-221-5 current; do not consume 1-226-19.

## Current task and discovery

Continue recovered physics from current code, not from an assumed 92/92 archive.
The six found parts were assembled and verified, but the result is Master Recovery
source consolidation and explicitly lists original 92/92 bytes as missing.
Evidence: Recovery/Normalized/original_reassembly.json and
Docs/MOBILE_1_221_5_SOURCE_MAP.md.

The native `getSpmoveIdDict` collection shape is now normalized and implemented
headlessly. The open-all canonical dataset is complete at that boundary: 292
serialized configs, 290 enabled, 2 disabled, 56 child references, 68 logic
buckets, 346 entries and zero missing children. Real-player `spmoveIds`, later
eligibility/ownership, odds and RNG remain explicit unresolved inputs.

## Latest executed GREEN

- Tools/build_reference.cmd: five executables compiled, C++17 /W4 /WX, 21/21 GREEN.
- python Tools/verify_spmove_selection.py: 4,672/4,672 native comparisons match.
- python Tools/verify_spmove_producer.py: preserved 2,640/2,640 native report remains source-current.
- python Tools/analyze_spmove_inventory_collector.py: GREEN, 23 ARM64 anchors plus IL2CPP layouts.
- python Tools/collect_spmove_inventory.py: GREEN, 290 enabled configs -> 346 entries / 68 buckets.
- python Tools/audit_feature_coverage.py: GREEN, 9 systems and 5 SHA/CRC-verified source archives.
- python Tools/check_native_evidence.py: CURRENT source bindings.
- python -m unittest discover -s Tests -p "test_*.py": 58/58 OK.
- python Tools/Unreal/validate_content.py: GREEN (provenance only).
- Original v0.2 07_TESTS: 67/67 OK in 6.600s.
- Earlier preserved native evidence: kernels 13,685, vectors 15,956, branches 7,776.
  These older suites were not rerun in this increment; their bound sources remain current.

## CONFIRMED

- Source matrix: 122 critical/archive observations and 22 identical groups.
  Videos ARM64 and metadata hashes match the current recovery binary/metadata.
- Selection: highest signed child ID wins, not level/order/odds; positive father
  tie rule; noRatio low bit; missing highest config has no fallback.
- Collector: `SpmoveIDCombine` is childId +0x10/fatherId +0x14. Each enabled root
  adds `(root.id, 0)` to its logicId bucket; every child adds `(childId, root.id)`
  to the child config logicId bucket. Missing player roots are skipped.
- Runtime config dictionary excludes disabled records through enable +0x1C.
- Producer: original reset/seven flags/strict comparisons/native distance math
  match C++ with explicit external geometry/curve/membership/property outcomes.
- Stable v0.2 SHA: 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac.
- Runtime +0x1C0 remains vertical_accel_raw.
- Feature audit separates recovered source, normalization, executable reference,
  Unreal integration and runtime validation.

## INFERRED / UNKNOWN

Managed allocation/exception details, real-player spmoveIds source/lifetime,
complete eligibility/ownership and odds/RNG remain open. The open-all artifact
uses decoded config-record order; original managed Dictionary.Values order is
not claimed. Complete GetVHor/GetVVer bases, GetKickVelocity and BALL_CONTACT
velocity still need native-backed integration. Original 92/92 source was not
found in the reconstructed six-part bundle; other copies remain unproven.

Unreal installation not located: Epic launcher InstallationList empty and no
custom registry builds. No UE compile/package/rendered match or FPS result.
Current C++ headless gameplay uses explicit NewGameAuthored tuning where marked.

## Local game-development tooling

`game-dev` CLI 1.0.2 is globally installed from the official tagged source and
its basic version/capabilities/doctor commands run; doctor reports healthy with
Windows warning and without Blender/provider credentials. The permanent skill
`C:\Users\dg71\.codex\skills\game-development-studio` was installed with content
SHA-256 e11d373f4aef10e10b13f1aa2a1d00e2a467373951ecfe839ccc6208be464409.
The upstream full CLI suite is not GREEN on this Windows host (78 failures from
POSIX process fixtures, directory fsync and missing openssl); do not cite it as
validated for mutating asset/package workflows.

## Files changed in this increment

SpmoveSelection/SpmoveInventoryCache C++ collector metadata and implementation;
collector analyzer/test; canonical open-all inventory generator/artifact/test;
recovery manifest, Unreal import plan/validator; coverage report; physics docs;
this checkpoint and evidence log. No raw archives/binaries/assets or Neymar edits.

## Exact resume commands

```powershell
git status --short
git rev-parse HEAD
Get-Content _CHECKPOINTS/CURRENT.md
Get-Content Recovery/Physics/EXECUTABLE_RECOVERY.md
Tools/build_reference.cmd
python Tools/verify_spmove_selection.py
python Tools/verify_spmove_producer.py
python Tools/analyze_spmove_inventory_collector.py
python Tools/collect_spmove_inventory.py
python Tools/audit_feature_coverage.py
python Tools/check_native_evidence.py
python -m unittest discover -s Tests -p "test_*.py"
python Tools/Unreal/validate_content.py
```

## Next exact step

Use `.local/il2cpp/disassembly_shoot.txt` and the existing static/native harnesses
to split and recover the old/new base regions inside GetVHor
(0x016E6A80..0x016E84A4) and GetVVer (0x016E84A4..0x016EA55C), starting with
config bindings and branch inputs before the already validated spmove modifiers.
Use `spmove_collected_open_all.json` as a complete open-all fixture while keeping
real-player inventory/eligibility explicit. Then join final GetVHor/GetVVer,
GetKickVelocity and BALL_CONTACT. Do not create Physics v0.3 until the full gate
and regression pass. Do not treat the scaffold/headless fixture as the game.
