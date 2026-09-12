# CONVERTER MEU JOGO MOBILE PARA PC — MASTER CONTEXT RECUPERADO

**Data da consolidação:** 2026-09-12  
**Plataforma final:** Windows PC  
**Engine final canônica:** Unreal Engine 5.x  
**Fonte mobile:** Unity + IL2CPP  
**3D source of truth:** Blender  

## Regra principal
Este projeto NÃO deve ser recomeçado. A linha anterior de Migration Master, PC 3D Ready, Player Ecosystem, Visual Registry, Animation Recovery e Physics Recovery é cumulativa. O mobile é fonte técnica/asset/gameplay; o runtime final do novo jogo é Unreal Engine.

## Arquitetura canônica

```text
JOGO MOBILE ORIGINAL (Unity / IL2CPP)
        ↓
RECOVERY / ENGENHARIA REVERSA
        ↓
ASSETS + DADOS + ANIMAÇÃO + FÍSICA + GAMEPLAY
        ↓
NORMALIZAÇÃO ENGINE-INDEPENDENT
        ↓
C++ REFERENCE IMPLEMENTATION
        ↓
UNREAL ENGINE 5.x RUNTIME
        ↓
WINDOWS PC GAME
```

O runtime final não deve depender de parsers IL2CPP ou AssetBundle durante a partida normal.

## Animation Recovery — baseline fechada
- `FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip`
- SHA-256: `91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64`
- 19/19 testes GREEN
- controller descompactado: 2,956,942 bytes
- 20,213 COFBlendState
- 50,127 Clip Nodes
- 30,648 Blend Tree Nodes
- 13,722 / 13,722 COFMotions resolvidos
- 100% bytes consumidos; trailing = 0
- XNumber: FRACTION_BITS=10, ONE=1024
- COFMotion: 30 FPS exatos
- MotionExpand, kickOutFrame, kickPoint, mirror aliases e blend trees preservados
- export histórico COFMotion→GLB: 56 canais (root X/Z, root yaw, Hips Y, 22 body rotations, 30 hand/finger rotations, COF_BallMarker XYZ)

Não refazer `controller.ctrl` do zero.

## Physics Recovery — estado real
Último RELEASE estável: `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`  
SHA-256 correto: `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`  
O hash antigo iniciado por `f44f` está invalidado.

Baseline do release:
- 67/67 testes
- 83/83 tabelas byte-exact
- 12,920,443 / 12,920,443 bytes
- trailing = 0
- 375 entradas

O workspace de pesquisa avançou DEPOIS do v0.2 e chegou historicamente a **92/92 GREEN**, mas o workspace posterior não foi recuperado byte a byte nesta sessão e `v0.3` NÃO foi legitimamente promovido.

Confirmado na cadeia nativa:
- XNumber primitives; Lerp; InverseLerp; Multiply; Divide; Create; fixed-point Remap
- XVector2 normalization
- GetVHor old/new base
- energyMapNew / vHorMapNew
- shootStrongMapNew / vHorRateNew
- GetVVer old/new base
- shootDisAndTime
- ms → XNumber seconds
- distance × horizontal velocity interpolation
- outEnergyMax, energyTolerance, energyNeedProtect
- shootPointHDown / shootPointHUp
- targetHeight / playerHeight / ballPos.y delta
- ballistic vertical solver
- ySpeedMin / ySpeedMax / clamp
- GetKickVelocity = VHor + VVer
- ARM64 int32 wrapping

Campo runtime `+0x1C0`: manter nome neutro **`vertical_accel_raw`**; não chamar de gravity sem prova.

### Próximo ponto exato
```text
spmoveInUseData
  ↓
VHor modifier
  ↓
VVer modifier
  ↓
GetVHor FINAL + GetVVer FINAL
  ↓
GetKickVelocity FINAL
  ↓
BALL_CONTACT.velocity
  ↓
eliminar ball_impulse=None
  ↓
regressão completa
  ↓
FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip
```
NÃO gerar v0.3 antes desse gate.

## Descobertas físicas adicionais preservadas
- Dribble kick-speed `getKickSpeed`, `_SpeedUp`, `_Normal`, `_Low`: interpolação bilinear original via Lerp, seguida por interpolação DirectionMin/DirectionMax.
- Seletores de `dribblespeeddata`: `speed`, `speed_fast`, `speed_0`, `speed_11`, `speed_12`, `speed_21`, `speed_22`.
- `GKDataModule.GetGKHandThrowSpeedData` (histórico RVA 0x1520878): bucket de altura, sem interpolação entre alturas; interpolação entre vizinhos por distância para vx/vy/time; modo `secondDistance`.
- Exemplo raw GK: height=2048, distance=15872, vx=14779, vy=3955, time=1170.
- `InverseLerp(0,3,1)=341`; `InverseLerp(0,3,2)=683`.
- `XNumber.create(0,900)=922` (~0.9); `create(0,100)=102` (~0.1).
- `collisiondata`: 104 regras; 6226/6226 bytes; arquivo serializado NÃO contém `breakTime`, apesar do metadata runtime mencionar o campo.
- ShootSpeed: 28 registros, 133872/133872 bytes; inclui curvas/listas, fixed-point, flag de método novo, xSpeed, shootPointH, energy/distance maps e shootDisAndTime.

## Unreal final
Arquitetura principal em C++. Blueprint para Animation Blueprint, Motion Matching/Pose Search, Control Rig/IK, UMG/CommonUI, Niagara, materiais e composição visual.

Módulos conceituais: FootballCore, FootballSimulation, FootballBall, FootballPlayer, FootballAnimation, FootballGameplay, FootballMatch, FootballRules, FootballReferee, FootballGoalkeeper, FootballTactics, FootballAI, FootballCareer, FootballCompetition, FootballCareerCoop, FootballMultiplayer, FootballNetworking, FootballPersistence, FootballUI, FootballAudio, FootballTools, FootballTests.

Contato físico canônico:
```text
Action → kickOutFrame / kickPoint → BALL_CONTACT → recovered GetKickVelocity → authoritative Ball Simulation
```
Motion Matching apresenta a ação; a simulação é autoridade sobre a bola.

## Produto final
Modos: 3v3, 5v5, 11v11; Player Career; Career 11v11/5v5; co-op; OWN_PLAYER_ONLY; PLAYER_CAREER_TEAM_CONTROL; server-authoritative online.
Career Universe e Competition Engine são independentes do renderer e devem ser testáveis sem abrir o Unreal Editor.

## Performance
Meta arquitetural: 120 FPS (~8.33 ms/frame) no hardware de referência, medido em partida real. Separar Simulation Quality de Rendering Quality. Gameplay não pode depender do FPS de render; usar timestep/substep e interpolation quando necessário.
