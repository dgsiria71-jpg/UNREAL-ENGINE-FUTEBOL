# CURRENT CHECKPOINT — 2026-09-12

## Autoridade
- **GitHub oficial/source of truth:** `dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL` branch `main`.
- Engine final: Unreal Engine 5.x (travada).
- Windows PC.
- C++ modular.
- Blender source of truth 3D.
- Mobile Unity/IL2CPP = fonte/recovery, não runtime final.
- Toda evolução válida deve terminar no GitHub; chats/workspaces/ZIPs intermediários são auxiliares.

## Estado do repositório oficial
- README canônico publicado.
- Arquitetura Unreal, recovery, migração, manifests, tools e histórico publicados.
- `docs/PROJECT_SOURCE_OF_TRUTH.md` publicado e define a política oficial de continuidade.
- `.gitattributes` preparado para Git LFS.
- workflow de verificação do master preparado.
- **Pendente:** o objeto binário grande `artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip` ainda não está fisicamente presente no GitHub/LFS; não considerar o master publicado até o upload e validação do hash.

## Master recovery esperado
`FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

- tamanho: 794.639.566 bytes (~757,83 MiB)
- SHA-256: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`

## Último release físico estável conhecido
`FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip` — SHA256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`.

## Último checkpoint de pesquisa conhecido
92/92 testes GREEN (histórico), posterior ao v0.2; workspace byte-a-byte ainda não recuperado nesta consolidação.

## Próxima tarefa técnica real
1. publicar/validar o master recovery no Git LFS quando possível;
2. recuperar/reconstruir workspace 92/92 a partir dos releases/fontes;
3. `spmoveInUseData` VHor modifier;
4. `spmoveInUseData` VVer modifier;
5. GetVHor/GetVVer final;
6. GetKickVelocity final;
7. BALL_CONTACT.velocity;
8. eliminar `ball_impulse=None`;
9. regressão completa;
10. somente então Physics Recovery v0.3;
11. normalização engine-independent;
12. Unreal runtime integration.

## Não refazer
controller.ctrl; XNumber; Animation Recovery; Player Ecosystem; Visual Registry; trabalho de parsing já comprovado.

## Gaps físicos desta consolidação
Os bytes dos releases históricos Animation/Physics/Player/Visual não estavam presentes no runtime atual. Seus nomes, hashes e estados foram preservados por históricos/transcrições. O `com.estar.bap.zip` também foi upload anterior, mas não está fisicamente montado agora; por isso `global-metadata.dat` e `data.unity3d` não foram inventados nem incluídos.
