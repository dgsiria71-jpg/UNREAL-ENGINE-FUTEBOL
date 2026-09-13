# Ferramentas, testes, builds e performance

## Automação

A intervenção manual do proprietário deve ser mínima. Tools/Blender inclui player_import.py, player_validate.py, player_lod.py, player_export.py, rig_validate.py e stadium_export.py. Tools/Unreal inclui import_players.py, import_stadiums.py, setup_skeleton.py, create_ik_rig.py, create_ik_retargeter.py, create_control_rig.py, setup_materials.py, setup_physics_asset.py, setup_lods.py, import_animations.py e validate_content.py.

Scripts repetitivos precisam ser idempotentes, receber input/output explícitos, registrar hashes e falhar cedo. Unreal Python e Editor Utility operam no editor; commandlets e módulos C++ de editor devem permitir validação headless quando possível. Nenhum script deve modificar Neymar v1.9 sem uma tarefa específica posterior.

## C++ build

UnrealBuildTool é a autoridade. O projeto mantém Football.Target.cs, FootballClient.Target.cs, FootballServer.Target.cs e Build.cs por módulo. O Client/Game não incorpora código exclusivo do servidor sem necessidade; Server não depende de editor, UMG, Niagara ou assets visuais. CI gera compile checks, Automation tests, cooked client e dedicated server package para Windows quando o engine source/installation estiver disponível.

O pipeline esperado é:

    GenerateProjectFiles
      -> Build Development Editor / Client
      -> Build Development Server
      -> Automation tests
      -> cook/package Windows client
      -> cook/package Windows dedicated server
      -> smoke launch and artifact manifest

Cada artefato tem commit, engine version, target, platform, config, source hashes e test receipt.

## Testes

- Core unit tests: fixed math, XNumber, int32 wrap, deterministic RNG, units and serialization.
- Recovery golden tests: parser byte consumption, controller/COFMotion counts, ShootSpeed maps, spmove and GetKickVelocity once semantics are recovered.
- Simulation integration: movement, first touch, pass, shot, dribble, tackle, intercept, collision, goalkeeper, goal and restart.
- Unreal Automation Tests: module behavior and command contracts.
- Functional Tests: field, goal, ball, player, goalkeeper, camera, input and reset in a loaded map.
- Network/Gauntlet: client/server launch, replication, disconnect/reclaim, latency/loss matrix and replay.
- Career headless tests: seasons, contracts, transfers, competitions, persistence and deterministic background matches.

A green test deve ter um comando exato e saída no checkpoint. Um teste de arquivo permanece histórico até ser repetido contra a fonte atual.

## Performance budget

Meta principal: 120 FPS em partida real no hardware de referência documentado. 8,33 ms é o orçamento total aproximado; ele deve ser dividido após medir, sem inventar valores. Capture Game Thread, Render Thread, GPU, Physics, Ball Simulation, Animation, Player AI, Team AI, Networking, Crowd, UI, Memory e VRAM.

Capture cenários 3v3, 5v5 e 11v11, broadcast e Player Career camera, estádio carregado, IA completa, bola e HUD. Relate p50/p95/p99, frame time, stalls e memória. Menu, campo vazio ou um jogador isolado não contam como validação da meta.

Presets Low/Medium/High/Ultra afetam renderização e LOD. Simulation Quality fica separada. Nanite, Lumen, Virtual Shadow Maps, TSR, Niagara, materiais modernos, grass, iluminação, crowd LOD, character LOD, culling e animation budget só são habilitados se a captura mostrar benefício sustentável. AI LOD e animation LOD reduzem custo sem retirar decisões centrais.

## Evidência de performance

Nenhum documento ou screenshot autoriza afirmar “120 FPS”. O relatório deve conter hardware, driver, build, mapa, número de jogadores, modo de câmera, preset, resolução, VSync/frame cap, duração da captura, ferramenta, p50/p95/p99 e gargalo. Se a meta não for atingida, o resultado é medido e registrado como blocker ou trabalho pendente.
## Headless gameplay gate

Antes da disponibilidade do Unreal Editor, a validação do domínio usa
`Reference/FootballGameplay/PlayableMatch.*`. O teste exercita elencos de
3v3/5v5/11v11, ownership server-authoritative, aceleração/frenagem, posse,
passe, chute, drible, tackle, save do goleiro, gol e restart. O fixture usa
velocidade `NewGameAuthored` explicitamente; a cadeia de recovery continua
exigindo `BALL_CONTACT.velocity` comprovado antes de aceitar dados mobile.
