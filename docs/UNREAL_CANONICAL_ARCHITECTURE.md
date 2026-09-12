# UNREAL ENGINE — ARQUITETURA CANÔNICA

## Decisão
Unreal Engine 5.x é o engine final do novo jogo para Windows PC. Documentos antigos que colocaram Unity 6/C# como runtime final estão obsoletos; Unity permanece apenas como tecnologia da fonte mobile e das ferramentas de conversão.

## Mapeamento correto
| Fonte/ideia Unity | Destino Unreal |
|---|---|
| C# runtime | C++ modules |
| MonoBehaviour | Actor / ActorComponent / UObject / Subsystem |
| Unity Input System | Enhanced Input |
| Animator | Animation Blueprint + Pose Search + Motion Matching |
| Animation Rigging | IK Rig + IK Retargeter + Control Rig |
| Unity Netcode | Unreal networking / replication / Dedicated Server |
| Unity UI | UMG / CommonUI |
| ScriptableObject | Data Assets / Primary Data Assets / Data Tables |
| Editor scripts | Unreal Python / Editor Utility / commandlets / C++ editor modules |
| PlayMode/EditMode tests | Automation + Functional + Integration + Gauntlet quando útil |

## Runtime principle
RECOVERED DATA → NORMALIZED DATA → C++ REFERENCE → UNREAL ADAPTER → GAMEPLAY. Parsers de IL2CPP/AssetBundle não ficam no hot path da partida final.

## Multiplayer
Servidor é autoridade sobre bola, regras, tackles, faltas, gols e match state. Cada humano controla exclusivamente seu CareerPlayer nos modos OWN_PLAYER_ONLY/co-op; demais atletas são server AI.
