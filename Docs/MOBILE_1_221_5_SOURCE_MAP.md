# Source audit 1-221-5

Executed 2026-09-12/13. User explicitly adopted the Bible v3 scope. Sources scanned: the named Videos tree and its eight ZIPs, Videos 1-221-5 ZIP, Downloads 1-221-5 XAPK, Migration Master v1.1, and the separately assembled Master Recovery copy. No 1-226-19 contents consumed.

`Tools/audit_mobile_sources.py` records 122 critical-file/archive observations, archive/directory counts and 22 identical groups in `Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json`. Duplicate grouping is by kind and exact SHA-256; originals remain untouched. This is a bounded critical-artifact matrix, not a claim that every file in Downloads/Videos was inspected.

- ARM64 libil2cpp: seven identical observations, 2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496.
- ARMv7 libil2cpp: separate ABI, five identical observations; not a competing ARM64 baseline.
- global-metadata: five identical observations, 92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e.
- controller.ctrl: eight identical observations, 21ab2bcb48ac64f62533a75860bcc4155b214ceb97145912dc0c739876d6b514.
- spmoveconfig, spmoveactiondata and shootspeed: ten identical observations each.

The named Videos inputs corroborate the exact binary/metadata already used by native differential recovery. Archive-level differences alone do not prove different builds because containers can differ while critical payloads match. Package version metadata is still a separate identification task; path names alone are not proof.

## Critical correction to the Bible 92/92 claim

Six Downloads parts concatenate to the exact expected SHA-256 4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2. CRC passes; 62 entries. However this is a source consolidation, not the original advanced Physics workspace. Its own README, physics status, provenance and checkpoint explicitly state that the original 92/92 bytes are missing. There is no original 92-test suite to run from these six parts. See `Recovery/Normalized/original_reassembly.json`.

Continue the verified existing recovery instead of adopting this package as a fictitious 92/92 implementation. Original v0.2 rerun remains 67/67 GREEN. Never sum newer suites to manufacture 92/92.

## Unreal availability

Current host scan: Epic Games install folder contains launcher/redist folders, launcher InstallationList is empty, no custom build registered in HKCU Unreal Engine Builds. No usable UE installation has been located. There is only C: and approximately 23 GB free at observation time. These are current host observations, not evidence that UE can never be installed. No Game/Client/Server build or FPS measurement was possible.
