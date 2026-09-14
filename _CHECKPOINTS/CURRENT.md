# Current checkpoint

Updated: 2026-09-14. Project **NOT COMPLETE**. GitHub `main` is the canonical source of truth.

## Current engineering baseline

The latest engineering head completed before the documentation-only handoff commits is:

`478bc02c00fa470f1cbca5af366c81a3680695fe`

PR #13 (`Recover source-bound GetVVer player property selector`) merged as `c12e61cf21b070f15860346e283c2cb92a9d5bd6` and passed post-merge run #183 / `34802035409` **SUCCESS**. Checkpoint `ed2776863d71da7442502eebb0a91d9cdb3d0d1d` passed run #184 / `34802089841` **SUCCESS**.

PR #14 (`Extend GetVVer property lookup evidence recovery`) is integrated at `478bc02c00fa470f1cbca5af366c81a3680695fe`. Its exact head passed run #195 / `34802465358` **SUCCESS** and the `main` integration passed run #197 / `34802769409` **SUCCESS**. GitHub records PR #14 as merged with merge SHA equal to `478bc02...`.

Documentation-only commits may appear after that SHA. Codex should require that `478bc02...` is contained in current `main`, not necessarily that it is the literal tip.

Physics v0.3 remains **BLOCKED**. Build `1-226-19` remains isolated. Neymar v1.9 remains paused.

## Canonical upstream evidence already consumed

- upload ID `20260913-234939-ff28866f`
- `artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt`
- 59,637 bytes
- SHA-256 `4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3`
- source `libil2cpp.so` SHA-256 `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

This publication proved exact `PlayerProperty$$GetShootProperty` at `0x01968398..0x019687C8` and allowed `ComposeNewGetVVerFromPlayerProperty` to feed the recovered branch-level selector into `shootPropertyMapNew -> energyToleranceMap` and the existing new-path GetVVer composition.

## Current executable boundary

`Reference/FootballPhysics/PlayerPropertySelector.h` source-binds the branch/value selector for `PlayerProperty.GetShootProperty`:

- action `0x16B3 -> property 0x15`
- action `0x22C5 -> property 0x16`
- collection id `0x13`, base property `0x14`, optional `PropertySingle.calMain(0x30, runtime value)` bonus
- far property `0x10`
- near properties `0x0F` / `0x11`
- fixed-point middle-distance blend

`ComposeNewGetVVerFromPlayerProperty` then feeds:

```text
PlayerProperty selector
 -> shootPropertyMapNew / energyToleranceMap
 -> protected-energy selection
 -> target-height adjustment
 -> GoalDoor.get_Height
 -> shootPointH clamp
 -> shootDisAndTime lookup
 -> vertical solver
 -> base vertical vector
 -> surviving 0x3FC parameter[2]
 -> surviving 0x41A parameter[2]
 -> shared GetVVer return
```

This is not yet whole-function native differential equivalence.

## PR #14 changes now on main

`Tools/extract_getvver_upstream_evidence.py` now directly requests:

```text
0x14DEFDC
0x1B60CC8
0x1968398
0x1967D38
0x1B718D8
```

The last two remain address-labelled until ScriptMethod metadata proves identity.

The extractor also copies exact `dump.cs` field windows for `AIParameterConfig 0x20..0x160`, `PlayerProperty 0x90..0xA0`, and attempts nested `+0x40/+0x44` fields of the type declared at `PlayerProperty +0x98`.

`tools/EXTRAIR_GETVVER_UPSTREAM.bat` now preserves any existing fixed-name report as `getvver_upstream_evidence_previous_<timestamp>.txt` before creating a new report.

TDD trail:

- deeper evidence RED `4a8f961376228938a5f547cb482942a973f6ca30`, run #187 / `34802181960`
- deeper evidence GREEN `b7f5693614d8b188fe38e272fd613cc5bcaea165`, run #189 / `34802255444` SUCCESS
- Windows preservation RED `5d118acf2e616994b619c6be001fb0215078ffc4`, run #191 / `34802298175`
- Windows preservation GREEN `6b9bb80361d4541fe4a2be66e83947497e6ea4d5`, run #193 / `34802399858` SUCCESS
- final head `478bc02c00fa470f1cbca5af366c81a3680695fe`, run #195 / `34802465358` SUCCESS
- main run #197 / `34802769409` SUCCESS

## Immediate next action

On the canonical Windows checkout, first inspect local status and preserve user changes, then synchronize `main` with `--ff-only`. Run:

```powershell
.\tools\EXTRAIR_GETVVER_UPSTREAM.bat
```

The new report should publish under `artifacts/native-recovery/getvver-upstream/<NEW_UPLOAD_ID>/` with a new manifest. Consume that exact upload before assigning identities or semantics to `0x1967D38`, `0x1B718D8`, `AIParameterConfig +0x24/+0x148/+0x14C`, or the collection-bonus fields.

## Remaining gates

Before complete GetVVer equivalence:

- recover `0x1967D38` and `0x1B718D8` from the new publication;
- bind exact AI threshold field names/units;
- bind `PlayerProperty +0x98` and nested bonus fields where metadata permits;
- bind runtime Football/GoalDoor object wiring;
- bind real runtime activation and ratios for `0x3FC` / `0x41A`;
- produce native/original differential vectors;
- preserve old-path GetVVer separately;
- complete GetKickVelocity;
- bind `BALL_CONTACT.velocity`;
- run final regression;
- only then create Physics v0.3.

## Stable baseline

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 `67/67 GREEN`
- source tables `83/83` byte-exact
- spmove selection `4672/4672`
- spmove producer `2640/2640`

Historical original 92/92 advanced workspace remains **not proven recovered**.

## Handoff document

Read next:

`Docs/CODEX_RETORNO_HANDOFF_COMPLETO_2026-09-14.md`

It contains the full chronology, formulas, hashes, CI trail, safety constraints and exact continuation plan for Codex.
