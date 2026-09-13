# FUTEBOL AI MASTER ARCHIVE v1.2 — Unreal

Status: arquitetura canônica para execução progressiva; o produto ainda não é declarado concluído.

Esta revisão é separada do arquivo mestre v1.1. O v1.1 fica preservado como histórico e como fonte de recovery. A documentação antiga pode mencionar Unity 6, C# e MonoBehaviour porque descreve o jogo mobile de origem ou uma arquitetura intermediária; essas escolhas não governam o novo runtime.

## Decisão vigente

O novo jogo é Windows PC + Unreal Engine 5.x + C++ modular. Blueprint é complementar. Blender é o source of truth 3D. O runtime usa Gameplay Framework, Enhanced Input, Animation Blueprint, Pose Search/Motion Matching, IK Rig, IK Retargeter, Control Rig, Unreal Networking, servidor dedicado, UMG/CommonUI, Data Assets/Data Tables, Asset Manager, Unreal Python, Editor Utility, commandlets, Unreal Automation Tests, Functional Tests, Gauntlet quando útil e UnrealBuildTool.

O jogo mobile original é Unity/IL2CPP. StreamingAssets, AssetBundles, global-metadata.dat, libil2cpp, controller.ctrl, COFMotion, XNumber, prefabs, config/match, nova_player e xplayable são fontes de extração. O pipeline remove essa dependência do runtime: arquivos nativos são decodificados e normalizados antes de serem importados para Unreal.

## Precedência

1. A correção arquitetural atual e a mudança de prioridade do proprietário.
2. A decisão original do novo jogo em Unreal.
3. Career Universe, Competition, AI, regras e contrato multiplayer.
4. Recovery comprovado do mobile.
5. V4/v1.1, exceto as partes que prescrevem Unity como engine final.
6. Documentos históricos.

Toda conclusão é marcada CONFIRMED, INFERRED ou UNKNOWN e carrega source_id, versão, hash, unidade e escala. Resultados históricos GREEN não são considerados reexecutados no checkout atual sem comando e saída atuais.

## Escopo do produto

O mesmo Football Simulation alimenta partida normal, carreira e online. Permanecem no escopo 3v3, 5v5, 11v11, Player Career, Career 5v5/11v11, OWN_PLAYER_ONLY, PLAYER_CAREER_TEAM_CONTROL, Career co-op, calendário, temporadas, clubes, jogadores, CareerPlayers, contratos, registrations, transfers, competitions, fixtures, standings, brackets, treino, desenvolvimento, forma, moral, fadiga, lesões, suspensões, ManagerTrust, Manager AI, Club AI, background simulation e histórico.

5v5 e 11v11 compartilham o Competition Engine parametrizado por dados. O servidor decide posse, contato, bola, gols, faltas, regras, estado de partida e ownership de cada CareerPlayer. Nenhum cliente controla o CareerPlayer de outro humano.

## Neymar congelado

Neymar v1.9, arquivos, checkpoints e proveniência permanecem intactos. Neymar Blender Master v2, sculpt, cabelo, rosto, roupa, materiais, botas e LODs específicos ficam pausados. O v1.9 pode ser fixture de importação ou teste; jogadores genéricos e meshes já convertidos devem permitir que gameplay avance sem esperar o personagem hero.

## Física e animação

Mantemos XNumber, ONE=1024, 30 FPS, XQuat40U, ActionFit, ActionSpeed, ShootSpeed, PassSpeed, Dribble, Tackle, Intercept, goalkeeper, Collision, kickOutFrame e kickPoint. A simulação da bola é autoritativa e independente; a animação apresenta a ação.

Gate obrigatório: spmoveInUseData VHor -> VVer -> GetVHor FINAL + GetVVer FINAL -> GetKickVelocity FINAL -> BALL_CONTACT.velocity -> eliminar ball_impulse=None -> regressão completa -> promover v0.3. O campo do runtime em +0x1C0 permanece vertical_accel_raw até prova de sua semântica original.

Fluxo de animação: recovery -> dados normalizados -> clips/curvas com root movement e contato -> Pose Search Database -> Motion Matching -> Animation Blueprint -> IK Rig/Retargeter -> Control Rig -> pose. Motion Matching não calcula a velocidade da bola; kickOutFrame/kickPoint emitem um evento de contato para a simulação.

## Qualidade e performance

120 FPS é uma meta medida em partida real, aproximadamente 8,33 ms por frame, e não uma afirmação antecipada. Game Thread, Render Thread, GPU, physics, ball simulation, animation, Player AI, Team AI, networking, crowd, UI, memória e VRAM devem ter métricas e orçamento em broadcast e Player Career. Simulation Quality é independente de Rendering Quality; fixed/sub-stepped simulation e interpolação impedem que o resultado lógico dependa de 60/90/120/144/240 FPS.

Definition of Done exige produto jogável com partida, regras, modos, carreira, persistência, multiplayer autoritativo, co-op, testes e pacotes Windows/Dedicated Server. Scaffold, menu, 3v3, 5v5, 11v11 isolado ou vertical slice são checkpoints, não a entrega final.

## Documentos

- ADR-ENGINE-001-UNREAL-ENGINE-CANONICAL.md
- ARCHITECTURE.md
- MODULE_BOUNDARIES.md
- DATA_AND_RECOVERY.md
- PHYSICS_HANDOFF.md
- ANIMATION_PIPELINE.md
- GAMEPLAY_FRAMEWORK.md
- CAREER_COMPETITION_NETWORK.md
- TOOLS_TESTING_PERFORMANCE.md
- TRACEABILITY.md

Referências oficiais: https://dev.epicgames.com/documentation/en-us/unreal-engine/compiling-game-projects-in-unreal-engine-using-cplusplus, https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-dedicated-servers-in-unreal-engine, https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine e https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api.
