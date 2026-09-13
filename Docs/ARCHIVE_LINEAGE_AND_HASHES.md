# HISTORICAL RELEASE LINEAGE AND HASHES

Updated from the sanitized full local archive audit published on 2026-09-13. `PHYSICAL_LOCAL_CONFIRMED` means the exact ZIP is physically present in the audited local source set and has an observed SHA-256. Historical transcript evidence remains useful, but current observed hashes take precedence for identity.

## FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `50073adf3b26be9e448ca7f6faa063d7ecd070a1fc3bfbb7cdc2b3d1969b0434`
- Bytes: `208900550`
- ZIP entries: `1941`
- Notes: Early migration master; previously marked not physically recovered.

## FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `c1c7d5352f94241c5aed771666ad5f723b24593ac7cf8c3bc9bfb0e7d175e1eb`
- Bytes: `157288676`
- ZIP entries: `4931`
- Notes: Hash matches the previously transcript-verified identity.

## FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_STAGE1_XPLAYABLE.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `516a81372616663b6e0ef0ea290d2cea08314f3ff5186679cb0f60e6adaa8757`
- Bytes: `20509708`
- ZIP entries: `49`
- Notes: Stage-1 XPlayable package is physically present; previously only its name had been recovered.

## FOOTBALL_PC_3D_READY_PACK_v0_1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `5b22f66a75e694405273cdb8647084076f621b7d6cc29fc99045a018423e2ef7`
- Bytes: `7220246`
- ZIP entries: `273`
- Notes: Hash matches the previously transcript-verified identity. Historical notes: 123/123 FBXS + 93/93 nova_player meshes; ball.glb/obj/collision sphere; ball radius ~0.1107703m.

## FOOTBALL_PC_3D_READY_PACK_v0_2.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `e287e1140dd704479292e5516996484641ed326a027f5c8302577eadd3393226`
- Bytes: `15126093`
- ZIP entries: `277`
- Notes: Later PC 3D ready evolution is physically present; previously marked not physically recovered. Must be diffed against v0.1 before choosing canonical 3D inputs.

## FOOTBALL_PLAYER_SYSTEMS_REFERENCE_PACK_v0_1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `46d0d4bf90f3d37bef137cb9be223d66db7b9ea4c03cb13bbaa9f7debf1aad50`
- Bytes: `3409699`
- ZIP entries: `214`
- Notes: Player systems reference package is physically present; previously marked not physically recovered.

## FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `74d6e29c0d68ceb59912e7049f85f1d57f16f225cd6905dd03f28d3756383822`
- Bytes: `1469457`
- ZIP entries: `141`
- Notes: Hash matches historical transcript evidence; 21/21 tests were historically recorded.

## FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `cea86e1e18f7aa58f924302bae542ebf2782217b32594d315aff3ff423efe813`
- Bytes: `2591557`
- ZIP entries: `139`
- Notes: Hash matches historical transcript evidence; 31/31 tests were historically recorded.

## FOOTBALL_VISUAL_PRESENTATION_ARCHITECTURE_v1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `a823b6d83637dc6899041348649f1b9650c060c9407786bcf9cc3e7366838645`
- Bytes: `17019`
- ZIP entries: `10`
- Notes: Hash matches historical transcript evidence.

## FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `b0e1336e576c0b9dae8d04d424e706f16b18c18a28ed94b13da129a052d322b1`
- Bytes: `73269452`
- ZIP entries: `1119`
- Notes: Hash matches historical transcript evidence; historical note: 1106 real recovered visual assets.

## FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64`
- Bytes: `104588601`
- ZIP entries: `1963`
- Notes: Hash matches historical transcript evidence; local extracted recovery tree also exists. Historical validation: 19/19 GREEN; controller structurally closed.

## FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- Bytes: `14956086`
- ZIP entries: `375`
- Notes: Hash matches historical transcript evidence. Local extracted v0.2 recovery tree also exists. Historical validation: 67/67 tests; 83/83 tables byte-exact; stable release. Later workspace reached 92/92 without v0.3 release, but that later exact workspace remains separately unproven.

## FUTEBOL_AI_MASTER_ARCHIVE_v1_0_2026-09-11.zip
- Status: `HISTORICAL_ARTIFACT_NOT_OBSERVED_IN_SANITIZED_AUDIT`
- SHA256: `UNKNOWN / not recovered`
- Notes: Global project architecture line. Do not infer identity from v1.1.

## FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip
- Status: `PHYSICAL_LOCAL_CONFIRMED`
- SHA256: `816a7100f7652f65cf42f069bb29b4ed441e28707cf541e4f806957758ebee41`
- Bytes: `256072964`
- ZIP entries: `56`
- Notes: Two local filenames were observed: the plain name and `(1)` copy. They are byte-identical: same size and SHA-256. Preserve one canonical copy plus duplicate provenance; do not waste LFS storage on both.

## FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11 (1).zip
- Status: `PHYSICAL_LOCAL_DUPLICATE_CONFIRMED`
- SHA256: `816a7100f7652f65cf42f069bb29b4ed441e28707cf541e4f806957758ebee41`
- Bytes: `256072964`
- ZIP entries: `56`
- Notes: Exact duplicate of `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11.zip`.

## Mobile source packages

### football-dream-be-a-pro-1-221-5.xapk
- Status: `CANONICAL_MOBILE_SOURCE_CONFIRMED`
- SHA256: `630a6f1b203bdce7ef2f8053801ee2afe0c77ffceef6bb3e3a23a9d196da3d56`
- Bytes: `509799714`
- ZIP entries: `5`
- Rule: current canonical mobile source.

### football-dream-be-a-pro-1-226-19.zip
- Status: `PHYSICAL_LOCAL_ISOLATED_CANDIDATE`
- SHA256: `2cddc1a4da4a4cddf28c41a846834252650ac49a2377f9146bca22786579d5c5`
- Bytes: `166757441`
- ZIP entries: `7363`
- Rule: catalog/compare only; do not merge into canonical 1-221-5 without an explicit version-delta decision.

## Master recovery consolidation

### FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip
- Status: `PUBLISHED_GIT_LFS_CONFIRMED`
- SHA256: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`
- Bytes: `794639566`
- ZIP entries: `62`
- GitHub path: `artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`
- Notes: source consolidation, not the lost advanced 92/92 Physics workspace.

## Audit provenance

Sanitized audit publication:
- upload id: `20260913-142305-d8fa2f3f`
- JSON: `artifacts/audits/20260913-142305-d8fa2f3f/01_FOOTBALL_PROJECT_AUDIT.json`
- CSV: `artifacts/audits/20260913-142305-d8fa2f3f/02_FOOTBALL_PROJECT_AUDIT.csv`
- summary: `artifacts/audits/20260913-142305-d8fa2f3f/03_FOOTBALL_PROJECT_AUDIT_SUMMARY.txt`
- records: `523`
- duplicate SHA groups: `101`

Presence proves preservation/identity, not semantic integration. Each recovered delivery must still be diffed and classified before being promoted into the canonical implementation.
