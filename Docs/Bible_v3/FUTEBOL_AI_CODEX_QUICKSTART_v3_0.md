# FUTEBOL AI — CODEX QUICKSTART v3.0

Este arquivo é um resumo operacional. A fonte completa é `FUTEBOL_AI_BIBLIA_MESTRE_CANONICA_TOTAL_UNREAL_v3_0_2026-09-12.md`.

## Estado canônico

- Produto: jogo de futebol realista para Windows PC.
- Engine final: Unreal Engine 5.x.
- Core: C++ modular.
- Blueprint: complementar.
- 3D source of truth: Blender.
- Desenvolvimento: AI-first.
- Build mobile atual: `football-dream-be-a-pro-1-221-5`.
- `football-dream-be-a-pro-1-226-19`: futura; não usar agora.
- Neymar v1.9: preservado e pausado.
- Physics v0.3: ainda não existe.
- Próximo bloco de física: `spmoveInUseData`.

## Fontes locais permitidas nesta fase

Use para descoberta/leitura de novas fontes SOMENTE:

```text
C:\Users\dg71\Downloads
C:\Users\dg71\Videos
```

O repositório/workspace de desenvolvimento pode continuar onde já está.

Em `Downloads` há novos arquivos importantes, incluindo o workspace histórico 92/92 recuperado em partes e o arquivo/script para montar as partes.

Em `Videos`, audite especialmente:

```text
C:\Users\dg71\Videos\football-dream-be-a-pro-1-221-5
```

Há múltiplas cópias da MESMA build 1-221-5; deduplicar por SHA-256. Não escolher um caminho como “única fonte” antes da matriz de hashes.

## Primeira sequência ao retomar

1. `git status`, branch, HEAD, dirty tree.
2. Ler `_CHECKPOINTS/CURRENT.md` e `EVIDENCE.md`.
3. Em Downloads, localizar partes do 92/92 + montador.
4. Montar em diretório separado sem alterar originais.
5. Validar integridade/hash e rodar suíte original.
6. Se 92/92 voltar GREEN, usar o workspace original recuperado como linha principal da física.
7. Auditar Downloads + Videos para cópias 1-221-5 e criar source matrix/dedup.
8. Retomar `spmoveInUseData`.
9. Fechar GetVHor/GetVVer/GetKickVelocity/BALL_CONTACT e regressão.
10. Só então promover Physics v0.3.
11. Em paralelo, quando Unreal estiver disponível, validar Game/Client/Server e construir o primeiro playable real.
12. Commit/checkpoint antes de limite de sessão.

## Nunca fazer

- não recomeçar baselines GREEN;
- não usar Documents/Desktop/Temp/OneDrive como novas fontes locais nesta fase;
- não misturar 1-226-19;
- não trabalhar no Neymar agora;
- não chamar tuning novo de `Recovered`;
- não gerar v0.3 antes do gate;
- não dizer 120 FPS sem medição em partida real;
- não parar no vertical slice como produto final.
