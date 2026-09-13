# ADR-ENGINE-001 — Unreal Engine canônico

Status: ACCEPTED / LOCKED
Data: 2026-09-12
Decisor: proprietário do projeto

## DECISION

Unreal Engine 5.x é o engine final do novo jogo de futebol para Windows PC. C++ é o núcleo principal, separado em módulos por responsabilidade. Blueprint é uma camada complementar para Animation Blueprint, Pose Search/Motion Matching, Control Rig, IK, UMG/CommonUI, Niagara, materiais, composição de níveis e configuração visual.

Blender é o source of truth 3D. A automação de Blender e Unreal usa Python, Editor Utility, commandlets e módulos de editor em C++. A rede final usa Unreal Networking, replicação e Unreal Dedicated Server. Replication Graph ou Iris só entram após análise e profiling que demonstrem necessidade.

## CONTEXT

O jogo mobile de origem usa Unity/IL2CPP. Por isso o recovery contém UnityStreamingAssets, AssetBundles, global-metadata.dat, libil2cpp, controller.ctrl, COFMotion, XNumber, prefabs, config/match, nova_player e xplayable. Documentos V4/v1.1 misturaram essa origem com uma recomendação temporária de Unity 6 para o produto PC. Essa recomendação é histórica e está obsoleta.

O fluxo canônico é:

    mobile Unity/IL2CPP
      -> recovery e engenharia reversa
      -> assets, dados, animação, física e gameplay
      -> normalização engine-independent
      -> Unreal Engine 5.x / C++

## RATIONALE

- Personagens realistas e câmera próxima precisam de pipeline PC para rig, materiais, LOD e iluminação.
- Motion Matching e Pose Search permitem locomoção e transições naturais usando clips recuperados.
- IK Rig, IK Retargeter e Control Rig resolvem contato visual com campo, corpo e bola sem assumir autoridade da física.
- Dedicated Server e replicação encaixam no modelo server-authoritative desejado.
- Estádios, crowd, iluminação, Nanite/Lumen/TSR quando medidos e perfil de 120 FPS exigem o ecossistema Unreal para PC.
- C++ deixa a simulação, contratos e ownership testáveis fora do renderer e fora do Blueprint.
- Python e módulos de editor permitem pipeline AI-first e automação com intervenção manual mínima.
- O comportamento recuperado continua sendo baseline/golden behavior; melhorias para o produto novo devem ser documentadas como divergências intencionais.

## CONSEQUENCE

A migração é por responsabilidade:

| Histórico mobile/intermediário | Destino canônico |
|---|---|
| Unity 6 | Unreal Engine 5.x |
| C# runtime / MonoBehaviour | C++ com Actor, ActorComponent, UObject, Subsystem e Gameplay Framework |
| Unity Input System | Enhanced Input -> Input Intent -> Gameplay Command |
| Unity Animator | Animation Blueprint + Pose Search/Motion Matching |
| Animation Rigging | IK Rig + IK Retargeter + Control Rig |
| Unity Netcode | Unreal Networking + replication + Dedicated Server |
| Unity UI | UMG/CommonUI |
| ScriptableObject | Primary Data Asset, Data Asset ou Data Table |
| Unity Editor scripting | Unreal Python, Editor Utility, commandlets e módulos de editor C++ |
| Unity tests | Automation Tests, Functional Tests, integração e Gauntlet |
| Unity build | UnrealBuildTool, .Build.cs, .Target.cs, Client/Server targets e packaging Windows |

O recovery não é carregado durante gameplay. Normalizadores geram contratos versionados com hashes e unidades. Neymar v1.9 permanece preservado e congelado; assets genéricos podem validar a gameplay primeiro.

## REJECTED

- Unity 6 como engine final.
- C# ou MonoBehaviour como runtime principal.
- Blueprint como local da arquitetura central.
- Parsers IL2CPP/AssetBundle durante uma partida normal.
- Motion Matching como autoridade da bola.
- Reiniciar ou polir Neymar como pré-requisito de gameplay.
- Alegar 120 FPS sem captura de partida real.

## REVISION RULE

A decisão não deve ser reaberta durante a implementação sem evidência técnica nova, forte, reproduzível e relevante para os requisitos. Preferência de ferramenta, familiaridade ou conveniência não constitui essa evidência.
