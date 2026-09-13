# PHYSICS RECOVERY STATUS

## Stable release
`FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`  
SHA256: `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`

67/67 tests; 83/83 byte-exact tables; 12,920,443 bytes consumed; trailing 0; 375 entries.

## Research after stable release
A later workspace reached 92/92 GREEN. It was not promoted to v0.3. This bundle does NOT counterfeit that workspace; it preserves its exact known checkpoint and reconstructs all currently available source inputs.

## Next gate
`spmoveInUseData` VHor → VVer → GetVHor/GetVVer final → GetKickVelocity → BALL_CONTACT.velocity → remove `ball_impulse=None` → regression → v0.3.

## Naming discipline
`runtime +0x1C0` = `vertical_accel_raw` until proven otherwise.
