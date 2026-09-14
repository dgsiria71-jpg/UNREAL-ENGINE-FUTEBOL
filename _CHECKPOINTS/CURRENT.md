# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**. Physics v0.3 is **BLOCKED**. GitHub main is canonical.

## Branch and HEAD

- working branch: codex/getvver-modifier-vectors
- canonical merged baseline: ce8d9c2415fc37f68ed227c34b1a164cc1a91de2 (PR #16)
- branch base: GitHub main commit ce8d9c2415fc37f68ed227c34b1a164cc1a91de2
- canonical build: football-dream-be-a-pro-1-221-5
- build 1-226-19: isolated and not consumed
- Neymar v1.9: preserved and paused

The canonical root checkout contains exactly four protected user modifications; they were not staged or rewritten:

- Tools/PUBLICAR_MASTER_NO_GITHUB.bat
- Tools/PUBLICAR_MASTER_NO_GITHUB.ps1
- docs/ARCHIVE_LINEAGE_AND_HASHES.md
- docs/PROJECT_SOURCE_OF_TRUTH.md

## Last GREEN tests

- focused Python modifier-vector test: 1/1 GREEN
- complete Python discovery: 117 run, 112 GREEN, 5 optional skips, zero failures
- C++ CTest Release/MSVC: 8/8 GREEN
- direct MSVC C++17 /W4 /WX modifier-vector executable: GREEN
- native evidence bindings: CURRENT
- Unreal persisted content validation: GREEN
- PR #16 run #216 / 34806239926: SUCCESS
- post-merge main run #217 / 34806276146: SUCCESS

## Current task

Connect the recovered GetVVer XNumber result to explicit runtime spmove inventories and produce deterministic representative vectors for no modifier, 0x3FC, 0x41A, and both in native order.

## Files changed by the current increment

- Reference/FootballPhysics/GetVVerSpmoveRuntime.h
- Tests/getvver_spmove_modifier_vectors_test.cpp
- Tests/test_getvver_spmove_modifier_vectors.py
- Tests/CMakeLists.txt
- Tools/build_getvver_modifier_vectors.py
- Tools/analyze_getvver_spmove_runtime_ratios.py
- Tools/analyze_getvver_new_path_composition.py
- Recovery/Normalized/getvver_spmove_modifier_vectors.json
- Recovery/Normalized/getvver_spmove_runtime_ratios.json
- Recovery/Normalized/getvver_new_path_composition_static_trace.json
- Recovery/Normalized/recovery_manifest.json
- Recovery/Physics/GETVVER_SPMOVE_MODIFIER_VECTORS.md
- _CHECKPOINTS/EVIDENCE.md
- _CHECKPOINTS/CURRENT.md

## CONFIRMED

- PR #16 merged the source-bound runtime ratio matrix into GitHub main at ce8d9c2415fc37f68ed227c34b1a164cc1a91de2.
- 0x3FC is gated by ShootLongKick / flag byte 5 and 0x41A by shootPush / flag byte 0.
- both modifiers use recovered param[2] matrices 900, 800, 700, 600, 500 across levels 1..5.
- highest signed eligible child_id selects the runtime record; level, order and odds do not select it.
- the new adapter passes the recovered GetVVer vector through the validated flag, magnitude, inventory, maximum-child and non-null parameter-list guards.
- representative explicit inventory selects child 102003 / level 3 / ratio 700 for 0x3FC and child 105002 / level 2 / ratio 800 for 0x41A.
- base raw vector [-3000,1537,777] produces:
  - none: [-3000,1537,777]
  - 0x3FC: [-2051,1051,531]
  - 0x41A: [-2344,1201,607]
  - both, in native order: [-1602,821,415]
- precombining ratios would produce x=-1603. The native two-step fixed-point chain produces x=-1602, proving that intermediate rounding must be preserved.
- absent selected config/list and a zero vector preserve the input under the recovered guards.

## INFERRED

- The representative inventories are plausible post-eligibility fixtures built only from canonical recovered records. They are suitable for deterministic host validation but do not assert ownership for a specific real player/action.

## UNKNOWN

- actual eligible spmove inventory for each runtime player/action;
- matching canonical ARM64 outputs for the four representative cases;
- whole-function native differential equivalence for the complete new-path GetVVer composition;
- final caller-visible GetKickVelocity behavior beyond the static vector join;
- final BALL_CONTACT.velocity binding.

## Blockers

Physics v0.3 remains blocked until the full gate is satisfied:

explicit eligible inventories and host vectors
 -> matching native ARM64 GetVVer execution/capture
 -> whole GetVVer differential validation
 -> complete GetKickVelocity
 -> BALL_CONTACT.velocity
 -> no unresolved/pending impulse
 -> full regression
 -> Physics Recovery v0.3

Do not rename vertical_accel_raw without proof. Do not fabricate the historical 92/92 workspace.

## Exact resume command

cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL\.local\worktrees\getvver-modifier-vectors"
git status --short
python -m unittest discover -s Tests -p "test_*.py"
& "C:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\ctest.exe" --test-dir .local/build/cmake -C Release --output-on-failure

## Next exact step

Commit and publish this bounded modifier-vector increment. Then build the canonical ARM64 differential harness or capture path for matching none/0x3FC/0x41A/both cases. Do not label the host vectors as native outputs.
