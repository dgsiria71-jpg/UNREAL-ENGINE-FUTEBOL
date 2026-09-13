# MEGA PROMPT CODEX GPT6 ASTRA — FOOTBALL UNREAL v5.0

Status: canonical execution prompt for the new Windows PC football game.
Date: 2026-09-12.
Authority: current owner correction and priority amendment.

============================================================
0. DECISION LOCKED
============================================================

The final engine is Unreal Engine 5.x. The primary runtime is modular C++. Blueprint is complementary and may be used where it is the correct tool: Animation Blueprint, Pose Search, Motion Matching, IK Rig, IK Retargeter, Control Rig, UMG/CommonUI, Niagara, materials, visual composition, level composition and configuration.

Blender is the 3D source of truth. Python automates Blender and Unreal. The network uses Unreal Dedicated Server and server-authoritative replication. Do not reopen Unity versus Unreal during implementation unless new, strong, reproducible technical evidence invalidates this decision.

Unity, IL2CPP, StreamingAssets, AssetBundles, controller.ctrl, COFMotion, XNumber, config/match, nova_player, xplayable and prefabs describe the mobile source and the recovery boundary only. The new PC runtime is Unreal. Do not infer the final engine from the format of the recovered source.

============================================================
1. PRECEDENCE AND EVIDENCE
============================================================

Apply this precedence:

1. This prompt and the owner's current instructions.
2. ADR-ENGINE-001-UNREAL-ENGINE-CANONICAL.md.
3. Functional Career Universe, Competition, AI, rules and multiplayer decisions.
4. Proven mobile recovery.
5. V4/v1.1 where corrected by this prompt.
6. Older historical documents.

Do a real architectural conversion, not a text replacement. Mark each claim CONFIRMED, INFERRED or UNKNOWN. Attach source archive, version, SHA-256, entry, offset, unit and scale when applicable. A historical green report is not a current green run until its exact command is executed against the current checkout.

Preserve original archives and checkpoints as read-only sources. Keep credentials, tokens, local databases, sessions, cookies, logs, raw backups and unlicensed state outside Git and deliverables.

============================================================
2. RECOVERY TO ENGINE-INDEPENDENT DATA
============================================================

The pipeline is:

MOBILE UNITY/IL2CPP
  -> recovery and reverse engineering
  -> useful assets, data, animation, physics and gameplay
  -> engine-independent normalization
  -> Unreal 5.x C++ runtime and editor assets

Do not load IL2CPP or AssetBundles during ordinary gameplay. Normalize before import. Preserve raw integer values beside normalized values. Unknown semantic fields remain null/UNKNOWN; do not invent a default impulse, gravity or action meaning.

Keep and use the recovered:
XNumber; ONE=1024; controller.ctrl; 20,213 COFBlendStates; 50,127 motion leaves; 30,648 Blend Tree Nodes; 13,722/13,722 COFMotions; 30 FPS; XQuat40U; kickOutFrame; kickPoint; MotionExpand; Animation Recovery; Physics Recovery; ActionSpeed; ActionFit; ShootSpeed; PassSpeed; Dribble; Tackle; Intercept; Goalkeeper; Collision; player ecosystem; Visual Registry; PC 3D Ready; assets; configs; formations and gameplay tuning.

Every normalized record includes schema version, source identity, source hash, units, fixed scale, raw value, normalized value, references, confidence and validation.

============================================================
3. PHYSICS GATE
============================================================

The stable release remains FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip with SHA-256:
7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac

Do not restart the physics work. The documented later workspace reached 92/92 historically, but reproduce it before claiming it. Do not produce v0.3 before the following gate:

spmoveInUseData
  -> VHor modifier
  -> VVer modifier
  -> GetVHor FINAL + GetVVer FINAL
  -> GetKickVelocity FINAL
  -> BALL_CONTACT.velocity
  -> remove ball_impulse=None
  -> complete regression
  -> FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip

Keep runtime +0x1C0 named vertical_accel_raw until its original semantic name is proved. Preserve ARM64 int32 wrap. After the gate, normalize the contract and integrate Ball Simulation, Pass, Shot, Dribble Contacts, Deflections, Goalkeeper Contacts and Player Contacts.

The ball is independent. Physics contacts are real simulation events, never a glued visual or animation impulse. Animation presents the action; simulation is authoritative.

============================================================
4. UNREAL MODULE ARCHITECTURE
============================================================

Use modules conceptually organized as:

Source/FootballCore
Source/FootballSimulation
Source/FootballBall
Source/FootballPlayer
Source/FootballAnimation
Source/FootballGameplay
Source/FootballMatch
Source/FootballRules
Source/FootballReferee
Source/FootballGoalkeeper
Source/FootballTactics
Source/FootballAI/PlayerAI
Source/FootballAI/TeamAI
Source/FootballAI/ManagerAI
Source/FootballAI/ClubAI
Source/FootballCareer
Source/FootballCompetition
Source/FootballCareerCoop
Source/FootballMultiplayer
Source/FootballNetworking
Source/FootballPersistence
Source/FootballUI
Source/FootballAudio
Source/FootballTools
Source/FootballTests

Use Actor for world entities, ActorComponent for capabilities, UObject for data/services and Subsystems for game/world/engine services. FootballCore and FootballSimulation compile and test without the renderer/editor. FootballCareer and FootballCompetition compile headless. No career, rule or simulation module reaches into a Skeletal Mesh.

Maintain explicit Build.cs files and:
Football.Target.cs
FootballClient.Target.cs
FootballServer.Target.cs
FootballToolsEditor.Build.cs
FootballTests.Build.cs

Use UnrealBuildTool. Server targets exclude editor-only dependencies and visual-only code. Do not hide central architecture in Blueprint.

============================================================
5. GAMEPLAY FRAMEWORK AND COMMAND FLOW
============================================================

Use:
AFootballGameMode: server-only match authority.
AFootballGameState: replicated match snapshot and public clock.
AFootballPlayerState: player/team/CareerPlayer identity and public owner.
AFootballPlayerController: local Enhanced Input to Input Intent only.
AFootballCharacter: capsule, visual and capability components.
AFootballBallActor: visual/collision proxy fed by authoritative BallState.
UFootballSimulationSubsystem: fixed-step command buffer and deterministic simulation.
UFootballMatchSubsystem: lifecycle, restart and event orchestration.
UFootballRulesSubsystem: rules and restarts.
UFootballCareerSubsystem: engine-independent career aggregate adapter.
UFootballAnimationAdapter: normalized action/contact data to presentation.

Flow:
Enhanced Input
  -> Input Intent
  -> validated Gameplay Command with owner and simulation tick
  -> server queue
  -> fixed simulation
  -> action/contact/rule events
  -> authoritative snapshot
  -> prediction/reconciliation and replication
  -> Animation Blueprint, cameras, UI, audio and VFX

A client cannot set BallState, score, foul, possession, another owner's identity or a result of a tackle.

============================================================
6. BALL, PLAYER, ACTION AND RULE SEMANTICS
============================================================

BallState supports free, controlled, kicked, deflected, goalkeeper-controlled and dead/restart. Contacts are ordered by simulation tick and contain source action, player, contact frame/time, kick point, selected tuning provenance and calculated result. Unreal collision supplies geometry/overlap data; FootballSimulation decides possession, velocity, goal and rule.

Player locomotion separates intent, desired velocity, acceleration, braking, turn rate, body orientation and pose. The same contract serves human input and PlayerAI. Preserve weight, inertia, acceleration, deceleration, first touch, protection, dribble, pass, through pass, cross, placed/strong shot, volley, header, tackle, slide, interception, collision, goalkeeper actions, off-ball movement, transitions and positioning. Avoid sliding bodies, instant direction changes, magnetic balls, action teleportation and robotic AI.

FootballRules owns kickoff, goal, goal kick, corner, throw-in, free kick, penalty, offside policy, advantage, foul, cards, substitutions, injury, suspension and reset. The renderer never invents a restart.

============================================================
7. ANIMATION
============================================================

Use:
controller.ctrl + COFMotion + recovered clips + root movement + ball marker + kickOutFrame + kickPoint
  -> normalized animation database
  -> Unreal animation assets
  -> Pose Search Database
  -> Motion Matching
  -> Animation Blueprint
  -> IK Rig / IK Retargeter
  -> Control Rig
  -> final pose

Motion Matching selects presentation. It does not determine ball velocity, possession, score, foul or tackle result. The contact chain is:
Action -> kickOutFrame/kickPoint -> BALL_CONTACT -> recovered GetKickVelocity -> authoritative Ball Simulation.

Support natural idle, walk, jog, run, sprint, acceleration, deceleration, turning, first touch, carrying, pass, shoot, cross, dribble, skill, tackle, collision, fall, recovery and goalkeeper transitions. Validate foot sliding, popping, pose snapping, root drift and contact timing in movement, broadcast camera and Player Career camera.

============================================================
8. BLENDER AND ASSET POLICY
============================================================

Blender remains source of truth. Automated tools validate scale, axes, bind pose, skeleton mapping, weights, morph topology, UVs, tangents, material slots, LODs, provenance and export hash. Exports are derived FBX/glTF/other approved intermediates into Unreal Skeletal Mesh, Skeleton, Physics Asset, IK Rig, IK Retargeter, Control Rig, Morph Targets, Materials and LODs.

Neymar v1.9 is frozen and preserved. Do not start Neymar Blender Master v2, sculpt, hair, face, cosmetics, specific clothing, boots or LOD work now. It can be a fixture. Use generic players, recovered players, converted meshes and temporary assets to build gameplay. Player gameplay must not depend on the hero asset.

============================================================
9. CAREER AND COMPETITION
============================================================

Career Universe is engine-independent and contains Calendar, Seasons, Clubs, Players, CareerPlayers, Contracts, Registrations, Transfers, Competitions, Fixtures, Standings, Brackets, Training, Development, Form, Morale, Fatigue, Injuries, Suspensions, ManagerTrust, ManagerAI, ClubAI, background simulation and History.

Keep PlayerDefinition, PlayerCardDefinition, CardInstance, Roster, Squad, Formation and Tactics distinct. Card progression is not career development. A career match uses:
Career Universe -> Match Setup -> same Football Simulation -> match events/result -> Career Universe.

Competition Engine parameterizes League, Group Stage, Knockout, Playoff, Final, Cup, Qualification, Promotion, Relegation, fixtures, standings, brackets and deterministic draws. 5v5 and 11v11 share the engine. 3v3 is first-class where its ruleset requires it.

Co-op uses stable human ownership. Human A controls CareerPlayer A, Human B controls B, and remaining players are server AI. Transfers/contracts are real universe events. Disconnect uses temporary AI takeover and same-owner reclaim. No client controls another human's CareerPlayer. Unanimous decisions remain unanimous.

============================================================
10. AI
============================================================

Keep PlayerAI, TeamAI, TacticalAI, GoalkeeperAI, ManagerAI, ClubAI and Background Match AI separate. Use reaction, decision, tactical and strategic frequencies with relevance/LOD. Players near the ball receive higher update priority, but distant AI does not lose all tactical structure. Do not run a heavyweight 22-agent decision loop every render frame.

============================================================
11. NETWORK
============================================================

The final model is:
CLIENT
  -> Enhanced Input
  -> Input Intent
  -> Gameplay Command
  -> Unreal Dedicated Server
       ownership, CareerPlayer ownership, Football Simulation,
       Ball Authority, tackles, fouls, goals, rules and Match State
  -> replication
  -> clients

Server validates owner, tick, sequence and bounds. Use prediction/reconciliation where it improves responsiveness. Choose snapshot/command rates by profiling. Evaluate Replication Graph or Iris only after measuring actor count, relevance, bandwidth, CPU and memory. Test latency 0/30/80/150 ms, loss 1/2/3%, reorder/duplicate, reconnect, ownership and replay.

============================================================
12. INPUT, DATA, UI AND TOOLS
============================================================

Use Enhanced Input, not Unity Input System. Use Primary Data Assets for immutable content references, Data Tables for dense validated rows and Asset Manager for stable asset discovery. Use UMG/CommonUI for view-only presentation.

Automate repetitive work:
Tools/Blender/player_import.py
Tools/Blender/player_validate.py
Tools/Blender/player_lod.py
Tools/Blender/player_export.py
Tools/Blender/rig_validate.py
Tools/Blender/stadium_export.py
Tools/Unreal/import_players.py
Tools/Unreal/import_stadiums.py
Tools/Unreal/setup_skeleton.py
Tools/Unreal/create_ik_rig.py
Tools/Unreal/create_ik_retargeter.py
Tools/Unreal/create_control_rig.py
Tools/Unreal/setup_materials.py
Tools/Unreal/setup_physics_asset.py
Tools/Unreal/setup_lods.py
Tools/Unreal/import_animations.py
Tools/Unreal/validate_content.py

Scripts are idempotent, hash outputs, fail early and never mutate frozen sources.

============================================================
13. TESTING, BUILD AND CI
============================================================

Use Unreal Automation Tests, Functional Tests, integration tests and Gauntlet when useful. Keep headless reference tests for fixed math, recovery, physics, career, competition and persistence. Test real field interactions: movement, first touch, pass, shot, dribble, tackle, interception, collision, goalkeeper save, goal and restart. Test server ownership, prediction/reconciliation, disconnect/reclaim and replays.

Build with UnrealBuildTool and explicit Client/Game/Server targets. CI runs format/static checks, C++ compile, headless automation, content validation, cooked Windows client, cooked Dedicated Server, smoke launches and artifact manifest. Each artifact records commit, engine version, target, platform, config, source hashes and receipts.

============================================================
14. FIRST PLAYABLE AND EXECUTION ORDER
============================================================

Do not wait for menus, career or perfect characters.

1. Recover and validate baselines.
2. Complete spmove VHor/VVer, final velocity, BALL_CONTACT and v0.3 gate.
3. Normalize the physics and animation contracts.
4. Establish Unreal C++ foundation and targets.
5. Create field, goals, ball, generic player, goalkeeper, camera and controls.
6. Implement movement, first touch, pass, shot, dribble, tackle, goalkeeper save, goal and restart.
7. Validate a real 3v3.
8. Expand the same gameplay to 5v5 and 11v11.
9. Integrate rules, AI, competition, career and persistence.
10. Add Dedicated Server, online replication and co-op.
11. Add UI, audio, VFX, content, accessibility and polish.
12. Profile and optimize.
13. Package and validate Windows client/server release.

A vertical slice, isolated 3v3, 5v5 or 11v11 is a checkpoint, not the final product.

============================================================
15. PERFORMANCE AND QUALITY
============================================================

Target 120 stable FPS on defined reference hardware in a real match, about 8.33 ms per frame. Measure Game Thread, Render Thread, GPU, Physics, Ball Simulation, Animation, Player AI, Team AI, Networking, Crowd, UI, Memory and VRAM separately. Test 3v3, 5v5, 11v11, broadcast camera, Player Career camera, loaded stadium, complete AI, ball and HUD.

Do not claim 120 FPS from menus, empty fields, one player or screenshots. Report hardware, driver, build, map, player count, mode, preset, resolution, frame cap, capture duration, tool, p50/p95/p99 and bottleneck. If target misses, report the measured result and blocker.

Provide Low/Medium/High/Ultra and independent render options. Separate Simulation Quality from Rendering Quality. Use Nanite, Lumen, Virtual Shadow Maps, TSR, Niagara, modern materials, grass, stadium light, crowd LOD, character LOD, culling and animation budget only when profiling supports them. Fixed/sub-stepped simulation plus render interpolation must keep logic identical at 60, 90, 120, 144 and 240 FPS.

============================================================
16. PRIORITY AMENDMENT — NEYMAR IS PAUSED
============================================================

Leave Neymar aside. Preserve every existing Neymar v1.9 file and checkpoint. Do not delete, rebuild or cosmetically modify it now. Use it only as a test fixture when useful.

The priority is:
CONVERT + INTEGRATE + MODIFY + IMPROVE + EXPAND + FINISH THE GAME.

Do not remain indefinitely in reverse engineering. When a subsystem has enough evidence for a safe adapter, integrate it. Do not invent behavior while relevant original semantics remain recoverable. Preserve golden behavior and document deliberate improvements.

============================================================
17. ASSERTION AND CHECKPOINT RULE
============================================================

Maintain _CHECKPOINTS/CURRENT.md with branch, HEAD, last green tests, current task, changed files, CONFIRMED, INFERRED, UNKNOWN, blockers, exact resume command and next step. Keep evidence append-only. Do not call a recovery, gameplay, multiplayer, career or performance gate complete without the command/artifact/runtime evidence that proves its full scope.

The final criterion is a playable Windows Unreal game with real football feel, quality animation, good AI, rules, 3v3/5v5/11v11, Career Universe, Competition Engine, persistence, online server authority, co-op, UI, content, measured performance and release packaging. Do not stop at documentation, architecture, recovery, parsers or a vertical slice.
