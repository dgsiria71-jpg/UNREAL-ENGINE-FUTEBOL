# MEGA PROMPT — FOOTBALL UNREAL v5.0 — RECOVERED/UPDATED 2026-09-12

You are continuing an existing football game conversion/reconstruction project. DO NOT restart it.

Canonical stack: Windows PC, Unreal Engine 5.x, C++ core, Blender source of truth. The source mobile game is Unity/IL2CPP only as recovery input.

Read `README.md`, `_CHECKPOINTS/CURRENT.md`, all `docs/*`, and `manifests/*` before changing anything. Treat recovered source archives as read-only.

Preserve proven baselines: controller/COFMotion recovery, XNumber ONE=1024, 30 FPS COFMotion, Animation Recovery historical 19/19, Physics v0.2 stable 67/67 + 83/83 byte-exact, and the later documented 92/92 research checkpoint. Never name unknown native fields semantically without evidence; keep +0x1C0 as `vertical_accel_raw`.

First engineering target: recover/rebuild the most advanced physics workspace, validate baseline, then implement/prove `spmoveInUseData` VHor modifier and VVer modifier, close GetVHor/GetVVer/GetKickVelocity, connect BALL_CONTACT.velocity, eliminate `ball_impulse=None`, run full regression, and ONLY THEN promote Physics Recovery v0.3.

After that normalize recovered data for Unreal. Final runtime must not parse IL2CPP/AssetBundles during normal gameplay. Implement modules for core simulation, ball, player, animation, match/rules/referee/GK/tactics/AI, career/competition/co-op, multiplayer/networking, persistence/UI/audio/tools/tests.

Animation architecture: recovered controller+COFMotion+contact metadata → normalized animation DB → Unreal assets → Pose Search/Motion Matching → Anim Blueprint → IK Rig/Retargeter → Control Rig. Motion Matching does not own ball physics; simulation is authority.

Build a real playable vertical slice early (field+goal+ball+player+GK+camera+control), then pass/shot/dribble/tackle/GK/goal/restarts, then 3v3→5v5→11v11. Preserve Career Universe, Competition Engine, co-op career and Player Ecosystem. Target 120 FPS by profiling real matches, not menus.

Use TDD, evidence before assertion, hashes/provenance, clean builds and `_CHECKPOINTS/CURRENT.md`. If blocked by missing bytes, record the gap rather than inventing data. Do not ask the user to choose routine technical alternatives when evidence can decide; investigate, document, continue.
