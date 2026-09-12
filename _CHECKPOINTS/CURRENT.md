# CURRENT CHECKPOINT — 2026-09-12

## Autoridade
- Engine final: Unreal Engine 5.x (travada).
- Windows PC.
- C++ modular.
- Blender source of truth 3D.
- Mobile Unity/IL2CPP = fonte/recovery, não runtime final.

## Último release físico estável conhecido
`FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip` — SHA256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`.

## Último checkpoint de pesquisa conhecido
92/92 testes GREEN (histórico), posterior ao v0.2; workspace byte-a-byte ainda não recuperado nesta consolidação.

## Próxima tarefa técnica real
1. recuperar/reconstruir workspace 92/92 a partir dos releases/fontes;
2. `spmoveInUseData` VHor modifier;
3. `spmoveInUseData` VVer modifier;
4. GetVHor/GetVVer final;
5. GetKickVelocity final;
6. BALL_CONTACT.velocity;
7. eliminar `ball_impulse=None`;
8. regressão completa;
9. somente então Physics Recovery v0.3;
10. normalização engine-independent;
11. Unreal runtime integration.

## Não refazer
controller.ctrl; XNumber; Animation Recovery; Player Ecosystem; Visual Registry; trabalho de parsing já comprovado.

## Gaps físicos desta consolidação
Os bytes dos releases históricos Animation/Physics/Player/Visual não estavam presentes no runtime atual. Seus nomes, hashes e estados foram preservados por históricos/transcrições. O `com.estar.bap.zip` também foi upload anterior, mas não está fisicamente montado agora; por isso `global-metadata.dat` e `data.unity3d` não foram inventados nem incluídos.
