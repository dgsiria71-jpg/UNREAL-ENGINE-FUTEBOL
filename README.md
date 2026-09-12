# UNREAL ENGINE FUTEBOL — Mobile → PC Recovery / Migration

Repositório canônico do projeto de conversão/reconstrução do jogo de futebol mobile (Unity/IL2CPP) para **Windows PC + Unreal Engine 5.x + C++**, com Blender como source of truth 3D.

> **Não recomeçar o projeto.** A linha de Migration Master, PC 3D Ready, Player Ecosystem, Visual Registry, Animation Recovery e Physics Recovery é cumulativa.

## Estado atual

- Engine final: **Unreal Engine 5.x**
- Plataforma: **Windows PC**
- Core: **C++ modular**
- Fonte mobile: **Unity + IL2CPP** apenas como recovery input
- 3D source of truth: **Blender**
- Animation Recovery histórico: **19/19 GREEN**, 20.213 states, 50.127 motion leaves, 30.648 blend-tree nodes, 13.722/13.722 COFMotions
- Physics Recovery v0.2 estável: **67/67 testes**, **83/83 tabelas byte-exact**, SHA256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- Workspace posterior documentado: **92/92 GREEN**, sem promoção legítima para v0.3

## Próximo gate técnico

`spmoveInUseData` VHor → VVer → GetVHor/GetVVer final → GetKickVelocity → `BALL_CONTACT.velocity` → eliminar `ball_impulse=None` → regressão completa → somente então Physics Recovery v0.3.

## Estrutura

- `docs/` — documentação recuperada e arquitetura canônica
- `manifests/` — provenance, hashes e inventários
- `tools/` — validação, unpack e publicação dos artefatos
- `artifacts/` — pacote mestre binário via Git LFS

## Pacote mestre recuperado

Arquivo local validado:

`FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

- tamanho: 794.639.566 bytes (~757,83 MiB)
- SHA-256: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`

O ZIP contém os arquivos físicos recuperados, documentação, manifests, ferramentas, inventário, transcripts e evidências. O artefato grande deve ser armazenado no repositório usando **Git LFS**; os arquivos de documentação permanecem Git normal para serem navegáveis no GitHub.

## Autoridade de arquitetura

`RECOVERED DATA → NORMALIZED DATA → C++ REFERENCE → UNREAL ADAPTER → GAMEPLAY`

Parsers IL2CPP/AssetBundle não devem ficar no hot path da partida final.
