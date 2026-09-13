# C++ module boundary and extraction plan

The first checked-in foundation uses one Football runtime module so the
project can be associated with any installed Unreal 5.x without prematurely
coupling unvalidated recovery code to many build targets. The domain boundary
is still explicit in namespaces, headers, and the engine-independent reference.

## Logical runtime modules

The intended extraction order is:

1. FootballCore: fixed-point math, IDs, units, time, deterministic RNG and
   serialization contracts.
2. FootballSimulation: fixed-step state, player/ball movement and snapshots.
3. FootballBall and FootballPlayer: authority-owned entity components.
4. FootballGameplay, FootballMatch, FootballRules, FootballReferee and
   FootballGoalkeeper.
5. FootballTactics and FootballAI (PlayerAI, TeamAI, ManagerAI, ClubAI and
   background simulation).
6. FootballCareer, FootballCompetition, FootballCareerCoop and
   FootballPersistence.
7. FootballNetworking, FootballUI, FootballAudio and FootballTools.
8. FootballTests plus FootballToolsEditor for automation and import commandlets.

Source/Football/Football.Build.cs is the current UE module boundary. Splitting
a logical module is allowed only when its public contract and dependencies are
covered by headless tests; this avoids a cosmetic module split that hides
cross-domain ownership.

## Target rules

Football.Target.cs, FootballClient.Target.cs, and FootballServer.Target.cs are
separate UBT targets. The server target is the authority for simulation, rules,
persistence contracts and replication. Editor and presentation dependencies
remain outside the server path as modules are extracted.

## Recovery boundary

The engine-independent code under Reference/ is the first contract fixture.
Unresolved mobile selection semantics stay outside the UE module until the
spmove gate is closed with native evidence. This keeps the Unreal runtime from
opening IL2CPP metadata or AssetBundles during gameplay.
