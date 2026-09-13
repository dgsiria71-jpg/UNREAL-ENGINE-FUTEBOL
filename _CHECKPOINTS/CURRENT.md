# Current checkpoint

Updated: 2026-09-13. Project NOT COMPLETE.
Official branch: `main`.
GitHub is the canonical source of truth.

## Repository publication

The recovered master archive is now published through Git LFS:

- path: `artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`
- bytes: `794639566`
- SHA-256 / LFS OID: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`
- publication commit: `c58cd352fa79bb791a9b8d4d6bff88a098cdbc20`
- durable publication note: `Docs/LFS_MASTER_PUBLICATION_2026-09-13.md`

The Git repository stores the LFS pointer; the large object is handled by Git LFS. `artifacts/SHA256.txt` records the same SHA-256.

## Canonical architecture

- Windows PC
- Unreal Engine 5.x
- C++ as the primary gameplay/simulation core
- Blueprint complementary
- Blender as 3D source of truth
- mobile build `1-221-5` remains the current recovery baseline
- build `1-226-19` must remain isolated until explicitly compared and approved
- Neymar v1.9 remains PAUSED

## Recovered physics state

Confirmed/preserved evidence includes:

- stable Physics v0.2 SHA `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- original v0.2 tests: 67/67 GREEN
- spmove selection: 4,672/4,672 native comparisons match
- spmove producer: preserved 2,640/2,640 native comparisons match
- open-all spmove collector boundary: 292 serialized configs, 290 enabled, 2 disabled, 56 child references, 68 logic buckets, 346 entries
- GetVHor/GetVVer old/new config-family split confirmed and bound to 26 ARM64/layout anchors
- original historical 92/92 workspace bytes are still not proven recovered; do not manufacture that status from newer suites

## Current recovery boundary

The next native physics task remains:

1. recover interpolation/clamp/arithmetic inside GetVHor (`0x016E6A80..0x016E84A4`)
2. recover interpolation/clamp/arithmetic inside GetVVer (`0x016E84A4..0x016EA55C`)
3. preserve already validated spmove modifiers
4. finish GetKickVelocity composition
5. bind final result to `BALL_CONTACT.velocity`
6. run complete regression gate
7. only then consider Physics Recovery v0.3

The local ignored `.local/il2cpp/disassembly_shoot.txt` was the Codex resume source for this work and is not yet canonical Git content.

## Immediate preservation task before repeating recovery work

A wider local archive audit is now required because additional historical ZIPs shown on the workstation may contain physically recoverable project deliveries that the earlier bounded audit did not fully consume.

Repository tools:

- `tools/AUDITAR_ACERVO_LOCAL.ps1`
- `tools/AUDITAR_ACERVO_LOCAL.bat`
- `tools/PUBLICAR_INBOX_NO_GITHUB.ps1`
- `tools/PUBLICAR_INBOX_NO_GITHUB.bat`

The audit is read-only. It must inventory/hash/classify archives first, identify duplicates and potentially newer recoveries, and keep `1-226-19` isolated from the canonical `1-221-5` baseline until comparison is explicit.

## GitHub validation status

Fresh-checkout portability was repaired and validated earlier on GitHub Actions. The source tree now separates persisted evidence from local regeneration artifacts instead of pretending missing local source bytes are committed.

## Resume rule

Do not restart architecture. Do not silently substitute historical documentation for current binary evidence. Preserve provenance, hashes and test evidence. Any newly recovered archive must be catalogued and compared before becoming canonical input.
