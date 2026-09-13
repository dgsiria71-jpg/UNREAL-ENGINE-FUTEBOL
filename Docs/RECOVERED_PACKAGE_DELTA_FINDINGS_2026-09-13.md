# Recovered package delta findings — 2026-09-13

Source: `artifacts/package-deltas/20260913-161656-9fc85b00/`.

This document records what was proven by hashing and comparing the physically recovered local football packages. It does not treat package presence as runtime equivalence and it does not merge the isolated mobile 1-226-19 build into the canonical 1-221-5 line.

## Audit result

- 14 target packages analyzed.
- 0 targets missing.
- `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip` and `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11 (1).zip` are exact byte-identical duplicates with SHA-256 `816a7100f7652f65cf42f069bb29b4ed441e28707cf541e4f806957758ebee41`.

## Migration master lineage

### v1 -> v1.1

- 1,926 same-path/same-content entries.
- 8 same-path entries changed.
- 7 entries only in v1.
- 2,933 entries only in v1.1.

`FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip` is therefore a major expansion, not a repack. Among the additions are streaming assets, `goalconfig.data`, `controller.ctrl`, COFMotion curves, mobile IL2CPP sources, LocalSettings and additional animation/gameplay material.

### Stage1 XPlayable -> v1.1

- 41 same-path/same-content entries.
- 0 changed shared paths.
- 8 entries only in Stage1.
- 4,826 entries only in v1.1.

The Stage1 package remains useful as a focused handoff, but v1.1 contains the broader canonical migration source set.

## 3D lineage

### PC 3D Ready v0.1 -> v0.2

- 258 same-path/same-content entries.
- 0 changed shared paths.
- 0 entries only in v0.1.
- 19 entries only in v0.2.

v0.2 is a strict additive superset of v0.1 at the compared path/content level. Important v0.2 additions include:

- `player_cristiano_rigged_named.glb`;
- `ANIMATION_STRING_CATALOG.txt`;
- `BONE_INDEX_MAP.csv`;
- `SKELETON_HIERARCHY.json`;
- stadium instance map;
- placed day/night stadium GLBs;
- rig/stadium recovery documentation;
- texture staging links;
- validation/manifest files.

For future 3D recovery work, v0.2 should be preferred while v0.1 is retained as provenance.

## Player-system lineage

`FOOTBALL_PLAYER_SYSTEMS_REFERENCE_PACK_v0_1.zip` and `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip` are complementary, not superseding copies: the comparison found no same-path files between the two package roots.

The reference pack contains mobile/reference player-system material such as Lua player progression/card/team management sources. The ecosystem core adds the reconstructed PC-side data/system line, including card sources, reference 3D assets, registries and player data.

`FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip` -> `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip`:

- 117 same-path/same-content entries;
- 1 changed shared path (`RELEASE_MANIFEST.json`);
- 23 entries only in v0.1;
- 21 entries only in v0.2.

v0.2 is therefore not a byte-for-byte superset of v0.1. Preserve both until the 23 v0.1-only paths are semantically reconciled. v0.2 adds the visual registry layer, schemas, inventory/recovery tools and visual tests.

## Animation and physics

The recovered physical Animation v1.0 and Physics v0.2 releases match their historical SHA-256 identities:

- Animation v1.0: `91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64`, 1,963 entries.
- Physics v0.2: `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`, 375 entries.

Animation v1.0 physically contains the controller, COFMotion index/data and representative GLB exports.

Physics v0.2 physically contains metadata mentioning `GetVHor`, `GetVVer` and `GetKickVelocity`, plus decoded gameplay tables and the stable recovery tests. The package-delta scan did not prove the later historical 92/92 workspace exists inside these compared ZIPs. Continue to treat 92/92 as a historical workspace state whose exact bytes remain unproven.

## Canonical use policy after this audit

1. Preserve all physical packages and hashes.
2. Prefer Migration Master v1.1 over v1 for source coverage, while keeping the 7 v1-only paths until reconciled.
3. Prefer PC 3D Ready v0.2 for 3D work; retain v0.1 as provenance.
4. Treat Player Systems Reference + Player Ecosystem as complementary lines.
5. Preserve Player Ecosystem v0.1 and v0.2 until v0.1-only content is reconciled.
6. Keep Animation v1.0 and Physics v0.2 as verified stable recovery baselines.
7. Keep mobile 1-226-19 isolated and compare-only; do not merge it into canonical 1-221-5 without explicit approval and evidence.
8. Do not recreate work already present in these packages before checking the package contents and local extracted workspaces.
