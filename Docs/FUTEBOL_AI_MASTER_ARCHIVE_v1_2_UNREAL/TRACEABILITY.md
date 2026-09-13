# Traceability e correção do V4/v1.1

Current executable recovery: [native differential checkpoint](../../Recovery/Physics/EXECUTABLE_RECOVERY.md).
Selected-property spmove branches, native sqrt and 3D normalization are now
implemented in engine-independent C++. Whole velocity and selection remain
pending; the static-only observations below describe earlier checkpoints.

## Correção arquitetural

V4/v1.1 são fontes importantes de recovery e domínio, mas seus trechos que definem Unity 6, C# como runtime, MonoBehaviour, Unity Input System, Unity Netcode, Unity Animator e PlayMode/EditMode como destino final foram sobrescritos pela decisão atual e pelo ADR-ENGINE-001. O jogo mobile continua Unity/IL2CPP; o novo jogo é Unreal 5.x/C++.

A interpretação correta não é substituir palavras. Cada responsabilidade foi remapeada para Gameplay Framework, Actor/Component/UObject/Subsystem, Enhanced Input, Animation Blueprint, Pose Search/Motion Matching, IK Rig/Retargeter, Control Rig, Unreal Networking, replication, Dedicated Server, UMG/CommonUI, Data Assets/Data Tables, Asset Manager, Unreal Python, commandlets, Automation/Functional/Gauntlet e UBT targets.

## Recovery preservado

Ficam válidos: XNumber, controller.ctrl, 20.213 COFBlendStates, 50.127 motion leaves, 30.648 Blend Tree Nodes, 13.722/13.722 COFMotions, 30 FPS, XQuat40U, kickOutFrame, kickPoint, MotionExpand, ActionSpeed, ActionFit, Animation Recovery, Physics Recovery, Player Ecosystem, Visual Registry, PC 3D Ready, assets, configs, formations e tuning. Esses dados são normalizados antes de Unreal.

A sequência de física continua exatamente spmoveInUseData VHor -> VVer -> GetVHor/GetVVer finais -> GetKickVelocity -> BALL_CONTACT.velocity -> remoção de ball_impulse=None -> regressão -> v0.3. O nome vertical_accel_raw permanece no campo +0x1C0.

## Prioridade atual

Neymar fica pausado e preservado. O produto deve sair de arquivos/parsers/GLBs para campo, jogadores, bola, animação, input, física, IA, regras, partida, modos, carreira e multiplayer. Use generic players e assets temporários para gameplay. Não aguarde um personagem perfeito para testar o sistema.

A ordem prática é:

    recuperar e validar baselines
      -> fechar física e normalizar
      -> Unreal foundation C++
      -> campo/bola/jogador/goleiro/câmera/controle
      -> movement/first touch/pass/shot/dribble/tackle/save/goal/restart
      -> 3v3 -> 5v5 -> 11v11
      -> Career/Competition/persistence
      -> Dedicated Server/online/co-op
      -> UI/audio/VFX/content/polish
      -> profiling and Windows release

Vertical slice é checkpoint. Feature complete não é release quality.

## Critérios de afirmação

- Recovery fechado: parser/bytes/testes e fonte identificados.
- Gameplay: partida real executada com input, bola, regras e reset.
- Multiplayer: server/client e ownership/reconciliation testados.
- Carreira: mesma Football Simulation alimenta o Match Setup e o resultado atualiza o aggregate.
- 120 FPS: captura de uma partida real no hardware e build declarados.
- Final: todos os gates de gameplay, carreira, multiplayer, persistência, qualidade, performance, acessibilidade e empacotamento aprovados.

Ausência de erro em uma busca, existência de uma classe ou uma renderização estática não comprova nenhum desses critérios.
## Derivação runtime recém-ancorada

`Recovery/Normalized/spmove_runtime_static_trace.json` conecta o schema
serializado à fronteira de execução: `OnGameStart` inicializa
`param_Xnumber`, `getSuccessByOdds` mostra a escala `odds << 10`, e os pontos
de chamada de `Player.GetSpmoveDataRatio` enumeram os IDs de propriedade
consumidos por `ShootUtility`. A conexão é estática e permanece
`behavior_validated=false`; portanto não substitui o gate de comportamento.

O trace de acesso de modificadores preserva o próximo nível de evidência:
`GetVHor` lê `param_Xnumber[0]` para `0x3FE` e `[1]` para `0x3FC`;
`GetVVer` lê `[2]` para `0x3FC`, `0x41A` e `0x3FB`. Os valores crus por nível
continuam normalizados e a seleção/equação ainda é UNKNOWN.
