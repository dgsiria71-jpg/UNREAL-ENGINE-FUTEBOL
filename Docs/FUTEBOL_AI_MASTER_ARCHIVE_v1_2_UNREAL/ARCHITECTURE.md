# Arquitetura Unreal

## Princípios

O runtime é modular, C++ first, data-driven e testável sem renderização. Cada módulo tem uma única autoridade para seu domínio. Actors representam entidades no mundo; ActorComponents carregam capacidades; UObjects representam dados e serviços puros; Subsystems representam serviços por engine, mundo ou jogo. Blueprints expõem composição e apresentação, mas não escondem regras centrais, simulação ou ownership.

O grafo de dependências aponta para baixo: tipos e math em FootballCore; simulação em FootballSimulation; gameplay e regras em FootballGameplay/FootballMatch; Career/Competition/Network dependem de contratos, não do renderer. UI, áudio, Niagara e câmeras consomem snapshots e eventos. Nenhum módulo de carreira ou regra acessa um Skeletal Mesh diretamente.

## Módulos de runtime

| Módulo | Responsabilidade | Depende de |
|---|---|---|
| FootballCore | fixed-point/reference math, IDs, units, time, deterministic RNG, errors, serialization contracts | Core, CoreUObject |
| FootballSimulation | fixed timestep, state transitions, players, ball, contacts, movement and deterministic snapshots | FootballCore |
| FootballBall | authority, free/controlled/kicked/deflected/GK/dead states, contact queue and trajectory | Core, Simulation |
| FootballPlayer | locomotion intent, acceleration, deceleration, body orientation, action state and ownership-independent player model | Core, Simulation |
| FootballAnimation | normalized action/clip metadata, contact windows, pose query inputs and presentation bridge | Core, AnimationCore; never owns ball result |
| FootballGameplay | gameplay commands, possession, actions, first touch, pass, shot, dribble, tackle and interaction orchestration | Core, Simulation, Ball, Player |
| FootballMatch | match lifecycle, clock, restart states, score and authoritative match snapshot | Core, Simulation, Gameplay |
| FootballRules | foul, advantage, cards, offside policy, goals, restarts and format parameters | Core, Match |
| FootballReferee | deterministic rule evaluation and referee event stream | Core, Rules, Match |
| FootballGoalkeeper | goalkeeper intent/contact classification and action bridge | Core, Ball, Player, Animation |
| FootballTactics | formations, role constraints, team shape and tactical intents | Core, Player, AI |
| FootballAI | PlayerAI, TeamAI, ManagerAI, ClubAI and background simulation schedulers | Core, Simulation, Tactics, Career contracts |
| FootballCareer | players, CareerPlayers, clubs, seasons, training, development, form, morale, fatigue, injuries and history | Core, Competition contracts |
| FootballCompetition | leagues, groups, knockout, playoff, final, qualification, promotion, relegation, fixtures, tables and deterministic draws | Core |
| FootballCareerCoop | human stable owners, contract/transfer flow, unanimous decisions, disconnect/reclaim | Core, Career, Network contracts |
| FootballNetworking | command validation, ownership, replication snapshots, prediction/reconciliation adapter | Core, Simulation, Match |
| FootballPersistence | versioned career/save schemas, migrations, idempotent match save and atomic writes | Core, Career, Competition |
| FootballTools | import schemas, asset IDs, source provenance and validation helpers shared by commandlets | Core |
| FootballUI | UMG/CommonUI presentation of view models only | Core, Match snapshots |
| FootballAudio | event-driven sound and mix state | Core, Match events |
| FootballTests | automation, deterministic, integration and replay tests | all testable runtime modules |

## Módulos de editor e targets

FootballToolsEditor contém importers, Asset Manager rules, Editor Utility integration, Python bridge and validation commands. O projeto deve ter Client, Game and Server targets; Server inclui apenas código necessário à simulação, regras, persistence contracts and network authority. Editor-only dependencies não entram no Server.

Exemplo conceitual de arquivos:

    Source/Football/Football.Build.cs
    Source/Football/Football.Target.cs
    Source/Football/FootballClient.Target.cs
    Source/Football/FootballServer.Target.cs
    Source/FootballToolsEditor/FootballToolsEditor.Build.cs
    Source/FootballTests/FootballTests.Build.cs

Cada Build.cs declara dependências explicitamente. O Target.cs define build environment, include order, type, configuration and platform. Server target deve ser descoberto pelo UnrealBuildTool como FootballServer.Target.cs; o packaging Windows gera client e server a partir de targets distintos.

## Gameplay Framework

- AFootballGameMode: somente no servidor; cria e valida o match.
- AFootballGameState: estado replicado da partida e relógio de apresentação.
- AFootballPlayerState: identidade, team, CareerPlayer ID e ownership público.
- AFootballPlayerController: recebe Enhanced Input local e produz intents; nunca decide resultado.
- AFootballCharacter: representação visual/colisão do jogador e componentes.
- UFootballSimulationSubsystem: clock fixed-step, command buffer and deterministic simulation.
- UFootballMatchSubsystem: lifecycle, restarts and rules orchestration.
- UFootballCareerSubsystem: loads a career aggregate outside the renderer.
- AFootballBallActor: visual/physical proxy fed by authoritative BallState; collision callbacks become input to simulation, not direct score/velocity truth.
- UFootballMatchHUD: view only through snapshots/events.

## Command flow

    Enhanced Input
      -> Input Intent (analog intent and buttons)
      -> validated Gameplay Command
      -> server command queue
      -> fixed simulation step
      -> action/contact/rule events
      -> authoritative snapshot
      -> replication/prediction reconciliation
      -> Animation Blueprint, camera, UI, audio and VFX

The same command and simulation contracts run in headless tests. A client cannot submit another human's ownership ID, set ball velocity, mark a goal or bypass a rule.

## Tick and authority

Simulation time is independent of render frame. Choose server tick, substeps and snapshot rate through profiling; record them in a versioned performance profile. The ball and player contacts are resolved in the fixed simulation. Rendering interpolates snapshots. Physics engine queries may provide collision geometry, but gameplay authority stays in FootballSimulation.

## Data ownership

Primary Data Assets describe immutable content references and tuning; Data Tables suit dense rows with stable schemas and validation. Runtime mutable state is plain C++/serialized domain data. Asset Manager resolves visual assets by stable VisualRegistry IDs. No UI, Blueprint or asset import path becomes a second authority for gameplay values.
