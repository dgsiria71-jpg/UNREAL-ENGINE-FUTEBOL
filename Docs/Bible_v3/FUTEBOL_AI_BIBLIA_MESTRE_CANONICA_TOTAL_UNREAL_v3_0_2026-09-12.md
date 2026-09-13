# FUTEBOL AI — BÍBLIA MESTRE CANÔNICA TOTAL DO PROJETO

## Conversão, recovery e novo jogo de futebol para Windows PC em Unreal Engine 5.x

**Versão:** 3.0 — revisão total pós-recuperação das fontes e do checkpoint 92/92  
**Data de consolidação:** 12 de setembro de 2026  
**Finalidade:** fonte-mestra humana, especificação do produto, mapa técnico do recovery e handoff operacional para Codex/IA  
**Status:** documento canônico de continuidade do projeto. Consolida decisões, visão, mecânicas, arquitetura, recovery, fontes, estado atual e protocolo de execução. Não substitui evidência binária, hashes, testes nem checkpoints de código.  

---

# 0. COMO USAR ESTE DOCUMENTO

Esta Bíblia reúne, em uma única fonte, a visão do produto, as decisões já fechadas, a arquitetura vigente, o recovery do jogo mobile, os sistemas de gameplay, carreira, IA, multiplayer, cartas/mercado, pipeline visual, estado técnico do workspace e o modo de trabalho esperado da IA.

Ela existe para impedir quatro problemas recorrentes: recomeçar trabalho já concluído; misturar versões do mobile; deixar documentação histórica obsoleta voltar a mandar na arquitetura; e declarar como “pronto” algo que ainda não foi validado em runtime, build, testes ou profiling.

## 0.1 Legenda de autoridade

| Rótulo | Significado |
|---|---|
| **CANÔNICO** | decisão de produto/arquitetura fechada e vigente |
| **CONFIRMADO** | comportamento, arquivo, hash ou resultado sustentado por evidência já registrada |
| **CHECKPOINT HISTÓRICO** | resultado obtido em workspace anterior; deve ser reproduzido antes de ser tratado como resultado atual |
| **IMPLEMENTADO ATUAL** | existe no workspace moderno/Codex e possui evidência atual |
| **ALVO DE DESIGN** | requisito do produto ainda não necessariamente implementado |
| **INFERIDO** | hipótese forte, ainda sem prova suficiente para virar contrato definitivo |
| **UNKNOWN** | desconhecido; não preencher por imaginação |
| **PAUSADO** | preservado, porém fora da prioridade imediata |

## 0.2 Regra de precedência

Quando duas fontes entrarem em conflito, use esta ordem:

1. correções mais recentes do proprietário;
2. esta Bíblia Mestre Canônica;
3. ADR/Documentação Unreal v1.2 e `_CHECKPOINTS` do workspace corrente;
4. comportamento mobile realmente comprovado por recovery/testes;
5. decisões funcionais consolidadas de Career Universe, Competition Engine, Player Ecosystem, IA e multiplayer;
6. Master Archive v1.1 / Mega Prompt V4 apenas nas partes que não contradizem a arquitetura atual;
7. documentos históricos mais antigos.

**Unity 6 como engine final, C# como runtime principal, MonoBehaviour como arquitetura do novo jogo, Unity Animator/Netcode/UI como destino final são decisões obsoletas.** Unity permanece relevante como tecnologia da fonte mobile original e em artefatos históricos de extração/conversão.

---

# 1. SNAPSHOT CANÔNICO EM UMA PÁGINA

```text
PRODUTO
Novo jogo de futebol realista para Windows PC

ENGINE FINAL
Unreal Engine 5.x

CORE
C++ modular

BLUEPRINT
Complementar: Animation Blueprint, Motion Matching, IK, Control Rig,
UMG/CommonUI, Niagara, materiais, composição e configuração visual

3D SOURCE OF TRUTH
Blender

DESENVOLVIMENTO
AI-first: Codex/GPT executa a maior parte da engenharia
Usuário = proprietário / diretor / aprovador / testador

BUILD MOBILE CANÔNICA AGORA
football-dream-be-a-pro-1-221-5

CÓPIAS/FONTES LOCAIS DA BUILD 1-221-5
Existem múltiplas cópias da MESMA build espalhadas em Downloads/Videos.
Nenhum caminho isolado é "a única fonte" antes da deduplicação por SHA-256.

ESCOPO LOCAL DE DESCOBERTA PARA CODEX NESTA FASE
C:\Users\dg71\Downloads
C:\Users\dg71\Videos

ÁRVORE ESPECIALMENTE IMPORTANTE AINDA NÃO AUDITADA PELO CODEX
C:\Users\dg71\Videos\football-dream-be-a-pro-1-221-5

CHECKPOINT HISTÓRICO 92/92
Recuperado pelo proprietário em Downloads, dividido em partes,
com arquivo/script de montagem também solto em Downloads.
Ainda deve ser montado e revalidado no ambiente atual.

BUILD MOBILE MAIS NOVA
football-dream-be-a-pro-1-226-19
STATUS: FUTURA / SEPARADA / NÃO USAR NESTA FASE
Uso futuro: diff seletivo depois que 1-221-5 estiver fechada e integrada

BASE TÉCNICA
Unity/IL2CPP mobile -> recovery -> normalização engine-independent -> Unreal

GAMEPLAY
Simulação realista controlável, responsiva, bola independente,
movimento com peso/inércia, animação convincente e IA tática

MODOS
3v3, 5v5, 11v11, Player Career, Career 5v5/11v11,
Career co-op 5v5/11v11, online server-authoritative

CARREIRA
Career Universe persistente + Competition Engine + Manager/Club AI

MULTIPLAYER
Unreal Dedicated Server, autoridade no servidor,
prediction/reconciliation e snapshots/replication

META DE PERFORMANCE
120 FPS estáveis em partida real no hardware de referência
(~8,33 ms/frame), medidos e não presumidos

NEYMAR
v1.9 preservado; produção v2 PAUSADA

PRIORIDADE IMEDIATA
1) em Downloads: localizar TODAS as partes do workspace histórico 92/92 + montador
2) montar em diretório separado, preservar originais, validar integridade e rodar suíte original
3) em Downloads + Videos: organizar/deduplicar as cópias da build 1-221-5 por SHA-256
4) auditar a árvore Videos\football-dream-be-a-pro-1-221-5 e os ZIPs/APKs/pastas extraídas
5) se 92/92 voltar GREEN, continuar desse workspace original recuperado
6) fechar spmoveInUseData VHor/VVer
7) final GetVHor/GetVVer/GetKickVelocity -> BALL_CONTACT.velocity
8) regressão e somente então Physics Recovery v0.3
9) integrar rapidamente a física/animação comprovadas na Unreal real
```

---

# 2. VISÃO DO JOGO

O objetivo não é “rodar o APK no PC” e nem reproduzir literalmente todas as limitações do jogo mobile. O objetivo é usar a engenharia recuperada do mobile como **base técnica comprovável** para criar um novo jogo de futebol para PC, mais profundo, mais bonito, mais escalável, mais testável e preparado para carreira, online e evolução de longo prazo.

A filosofia do produto é:

> **Recuperar o que já é bom e comprovável, preservar o comportamento como referência dourada e então melhorar conscientemente quando a versão de PC puder oferecer algo superior.**

O jogo precisa transmitir **realismo controlável**. Realismo não significa controles pesados, atraso artificial ou um atleta que “briga” contra o jogador. A sensação alvo combina física convincente, animação natural, input responsivo, previsibilidade suficiente para habilidade competitiva e profundidade técnica.

## 2.1 Pilares de experiência

- **Bola independente:** a bola não é “colada” ao pé; contatos são eventos da simulação.
- **Corpo com peso:** aceleração, frenagem, giro, proteção, equilíbrio e colisão precisam ter consequência.
- **Animação como apresentação, não como autoridade da física:** Motion Matching seleciona pose/movimento; a simulação decide bola, contato, posse, falta e gol.
- **IA de futebol de verdade:** jogadores ocupam espaços, apoiam, pressionam, cobrem, fazem corridas e reagem sem onisciência.
- **Carreira viva:** temporadas, calendários, contratos, transferências, competições, desenvolvimento e decisões de clubes continuam mesmo fora das partidas do usuário.
- **Co-op de carreira real:** amigos são jogadores humanos distintos dentro do mesmo universo, não avatares temporários teletransportados para um time.
- **Performance como requisito arquitetural:** 120 FPS deve ser considerado desde cedo.
- **Automação:** tarefas repetitivas de conteúdo, import, validação, LOD, rig, material, build e teste devem virar ferramentas.

## 2.2 O que o jogo não deve ser

- um arcade de bola magnética;
- uma coleção de animações sem simulação coerente;
- um menu bonito sobre gameplay rasa;
- um “modo carreira” que é somente uma sequência fixa de partidas;
- uma IA que aumenta dificuldade trapaceando, lendo o futuro ou teleportando;
- um projeto dominado por centenas de Blueprints difíceis de manter;
- um protótipo 3v3/5v5 tratado como produto final;
- um port Unity disfarçado de jogo Unreal.

---


# 2A. APRESENTAÇÃO DO PRODUTO — O JOGO QUE ESTAMOS CONSTRUINDO

**FUTEBOL AI** (nome de trabalho) é um jogo de futebol para PC orientado a simulação, com foco em sensação de controle, inteligência coletiva, carreira persistente e capacidade de jogar sozinho ou com amigos controlando jogadores individuais dentro do mesmo universo.

A proposta não é competir por quantidade de efeitos ou por assistência invisível. A proposta é que o jogador reconheça causalidade: recebeu mal porque o corpo estava desequilibrado; chutou diferente porque ângulo, perna, contato, atributo e pressão mudaram; perdeu a bola porque o defensor leu o espaço; abriu uma linha de passe porque o time se reorganizou. O futebol deve parecer vivo sem deixar de ser jogável.

## 2A.1 Fantasia central

- **Ser um jogador:** criar/evoluir um CareerPlayer, conquistar espaço, ficar no banco, entrar durante a partida, mudar de clube, jogar 5v5 ou 11v11, construir reputação e carreira.
- **Ser o time:** quando a política permitir, controlar a equipe ao redor do CareerPlayer sem apagar a identidade do atleta próprio.
- **Jogar com amigos dentro da carreira:** cada pessoa possui um atleta real do universo persistente. Para atuarem juntas, precisam compartilhar clube/registro válidos; o restante do elenco é IA.
- **Jogar futebol de alto nível fora da carreira:** treino, 3v3, 5v5, 11v11, online e partidas rápidas usando a mesma simulação central.

## 2A.2 Sensação de campo

A experiência alvo combina:

```text
responsividade
+ peso corporal
+ bola independente
+ contato confiável
+ animação contextual
+ leitura tática
+ IA sem trapaça
+ câmeras profissionais/imersivas
```

O jogo deve ficar bonito **em movimento**, não apenas em screenshots: acelerar, frear, virar, receber, dominar, proteger, chutar, colidir, cair, levantar, marcar, pressionar, fechar linhas e transitar entre ataque/defesa.

## 2A.3 Diferencial estrutural

O projeto une duas linhas que originalmente estavam separadas:

1. **recovery técnico do mobile**, que fornece comportamento e dados reais de física/animação/gameplay;
2. **novo jogo PC**, que fornece arquitetura moderna, Career Universe, Competition Engine, multiplayer, apresentação e escalabilidade.

O resultado esperado não é um “remaster” automático e nem uma cópia literal do mobile. É um novo produto cuja base de futebol é informada por comportamento recuperado e validado.

# 3. FONTE MOBILE, CÓPIAS LOCAIS E POLÍTICA DE PROVENIÊNCIA

Esta seção é deliberadamente rígida porque vários problemas de continuidade nasceram de confundir **build**, **cópia**, **pacote derivado** e **workspace de recovery**.

## 3.1 Build canônica atual — decisão fechada

A build mobile canônica desta fase é:

`football-dream-be-a-pro-1-221-5`

O fato de existirem várias cópias no PC não cria várias versões do jogo. Até prova em contrário por hash/build metadata, são **cópias da mesma build**.

O recovery histórico, a extração de XAPK/APKs, o Migration Master, Animation Recovery, Physics Recovery, PC 3D Ready e os demais pacotes foram construídos a partir da linha `1-221-5`. Portanto, toda continuação deve permanecer ancorada nela até o jogo PC possuir essa base integrada e estável.

## 3.2 Regra local nova: Codex deve descobrir fontes somente em Downloads e Videos

Para a fase atual, as duas únicas áreas permitidas para **descoberta/leitura de novas fontes locais** são:

```text
C:\Users\dg71\Downloads
C:\Users\dg71\Videos
```

Essa regra não impede o Codex de continuar trabalhando no repositório/workspace Git existente onde ele estiver. Ela impede apenas que o agente escolha `Documents`, `Desktop`, `Temp`, `OneDrive` ou outra pasta como nova raiz de fonte e volte a fragmentar a proveniência.

### Downloads

`C:\Users\dg71\Downloads` contém os recovery packs/pacotes de migração usados pelo Codex, novos arquivos adicionados pelo proprietário e, agora, **o workspace histórico Physics 92/92 recuperado em partes**, além do arquivo/script/instrução para **montar as partes**.

### Videos

`C:\Users\dg71\Videos` contém a árvore importante da build `1-221-5`, especialmente:

`C:\Users\dg71\Videos\football-dream-be-a-pro-1-221-5`

O proprietário informa que ali existem APKs já descompactados em pastas normais, conteúdo do `UnityStreamingAssetsPack`, outros ZIPs importantes e material organizado que o Codex ainda não havia auditado na rodada anterior.

## 3.3 Múltiplas cópias 1-221-5: não escolher uma por nome; deduplicar por conteúdo

Nenhum caminho deve ser chamado de “a única fonte canônica”. O canônico é a **build 1-221-5**. As cópias concretas precisam ser organizadas.

Para cada cópia/pacote/pasta 1-221-5 encontrada em Downloads ou Videos, registrar:

- path;
- tipo: APK, ZIP, diretório extraído, recovery pack, migration pack;
- `versionName`/`versionCode` quando recuperável;
- tamanho e quantidade de arquivos;
- SHA-256 de APK/base e artefatos críticos;
- relação de proveniência com os recovery packs existentes.

Artefatos de comparação prioritários:

```text
com.estar.bap.apk
config.arm64_v8a.apk
config.armeabi_v7a.apk
UnityDataAssetPack.apk
UnityStreamingAssetsPack.apk
libil2cpp.so
global-metadata.dat
data.unity3d
datapack.unity3d
controller.ctrl
spmoveconfig
spmoveactiondata
shootspeed
```

Se os hashes forem iguais: `DUPLICATE_IDENTICAL_COPY`. Se forem diferentes dentro da mesma build declarada: investigar antes de escolher.

Saídas recomendadas para o workspace:

```text
Recovery/Normalized/MOBILE_1_221_5_SOURCE_MATRIX.json
Docs/MOBILE_1_221_5_SOURCE_MAP.md
```

Não apagar nenhuma cópia durante a auditoria.

## 3.4 O que o Codex realmente usou antes desta correção

Os logs mostram que a investigação moderna do Codex utilizou principalmente material de `Downloads`, em especial:

`FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip`

Dali ele consultou `global-metadata.dat`, `libil2cpp`, `spmoveconfig`, `spmoveactiondata`, `shootspeed`, metadata e documentação de physics/shoot/ball. Também chegou a pesquisar uma árvore `Documents\\football-dream-be-a-pro-1-221-5`, mas isso **não deve governar a próxima rodada**; a descoberta de fontes foi agora limitada a Downloads + Videos.

A árvore em `Videos\\football-dream-be-a-pro-1-221-5` ainda precisa ser auditada diretamente e comparada por hash com os derivados já utilizados.

## 3.5 Versão 1-226-19 — futura, separada e não-baseline

`football-dream-be-a-pro-1-226-19` é a versão mobile mais recente do proprietário. O plano de produto é **não usá-la agora**. Primeiro terminar a extração/reconstrução/integração da `1-221-5`; somente depois abrir uma fase comparativa dedicada.

Uma sessão anterior do Codex chegou a catalogar brevemente um arquivo `football-dream-be-a-pro-1-226-19.zip` em Downloads e observou um `spmoveactiondata` idêntico em um recorte e um `spmoveconfig` de tamanho diferente. Isso deve ser tratado apenas como **inspeção incidental histórica**, não como início oficial da análise 1-226-19 e não como fonte de valores para a linha atual.

Regra vigente:

```text
1-221-5 = CURRENT_CANONICAL_BUILD
1-226-19 = FUTURE_REFERENCE_SOURCE_UNANALYZED_FOR_PRODUCT_WORK
```

Não misturar configs, IL2CPP, metadata, assets ou tuning da 1-226-19 nesta fase.

## 3.6 Arquitetura técnica da fonte mobile original

O jogo mobile original é distribuído como XAPK/APKs e usa Unity + IL2CPP. A arquitetura recuperada é aproximadamente:

```text
Football Dream: Be a Pro
├── Android / Java
│   └── Activity + integração Android <-> Unity
├── Unity Runtime
│   ├── libunity.so
│   ├── libmain.so
│   └── UnityPlayer
├── Código principal
│   └── IL2CPP
│       ├── libil2cpp.so
│       └── global-metadata.dat
├── Gameplay data-driven
│   ├── assets/config/match/
│   ├── assets/LocalSettings/
│   └── assets/ai_configs/running/
├── Animação / Playables
│   ├── assets/xplayable/
│   ├── controller.ctrl
│   └── COFMotion / animation configs
├── Jogadores / modelos / rigs
│   ├── assets/nova_player/
│   ├── assets/fbxs/
│   └── assets/prefabs/
├── Lua
│   ├── LuaScripts/data/
│   ├── LuaScripts/service/
│   └── LuaScripts/ui2/
└── Conteúdo Unity
    ├── data.unity3d
    ├── datapack.unity3d
    ├── textures/
    ├── materials/
    └── cenas/estádios
```

APKs históricos principais: `com.estar.bap.apk`, `config.arm64_v8a.apk`, `config.armeabi_v7a.apk`, `UnityDataAssetPack.apk`, `UnityStreamingAssetsPack.apk`.

## 3.7 Política de normalização

O runtime final Unreal nunca deve depender de parser IL2CPP/AssetBundle durante gameplay normal.

```text
MOBILE UNITY / IL2CPP
        ↓
EXTRAÇÃO / RECOVERY
        ↓
EVIDÊNCIA CRUA + PARSERS + TESTES
        ↓
DADOS NORMALIZADOS ENGINE-INDEPENDENT
        ↓
IMPLEMENTAÇÃO C++ DE REFERÊNCIA
        ↓
ADAPTADOR UNREAL
        ↓
GAMEPLAY REAL
```

Cada registro normalizado deve carregar, quando aplicável: schema version, source/build, archive/hash, source entry, offset/length, unidade, escala fixed-point, valor raw, valor normalizado, confidence (`CONFIRMED/INFERRED/UNKNOWN`) e validação.


# 4. EVOLUÇÃO HISTÓRICA DOS ENTREGÁVEIS

A linha de trabalho não foi um único ZIP. Houve uma sequência cumulativa de migração, 3D, player systems, apresentação visual, animação e física.

## 4.1 Pacotes confirmados historicamente

1. `FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1.zip`
2. `FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip`
3. `FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_STAGE1_XPLAYA...` — nome histórico preservado parcialmente; não inventar o sufixo ausente se não houver o arquivo real.
4. `FOOTBALL_PC_3D_READY_PACK_v0_1.zip`
5. `FOOTBALL_PC_3D_READY_PACK_v0_2.zip`
6. `FOOTBALL_PLAYER_SYSTEMS_REFERENCE_PACK_v0_1.zip`
7. `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip`
8. `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip`
9. `FOOTBALL_VISUAL_PRESENTATION_ARCHITECTURE_v1.zip`
10. `FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip`
11. `FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip`
12. `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`

`UnityStreamingAssetsPack`, `GAMEPLAY_MODELS_CORE`, `GAMEPLAY_DATA_CORE`, `config.arm64_v8a` e `XPLAYABLE_GAMEPLAY` são nomes de fontes/inputs ou conjuntos de análise e não devem ser tratados automaticamente como releases do projeto novo.

## 4.2 Linha conceitual

```text
MOBILE / XPLAYABLE
  ↓
Migration Master v1 → v1.1 → Stage1 Xplayable
  ↓
PC 3D Ready v0.1 → v0.2
  ↓
Player Systems Reference
  ↓
Player Ecosystem Core v0.1
  ↓
Visual Registry v0.2
  +->
   Visual Presentation Architecture
   Visual Production Asset Pack
  ↓
Animation Recovery v1.0
  ↓
Physics Recovery v0.2
  ↓
workspace avançado histórico 92/92
  ↓
reconstrução/continuação Codex moderna
  ↓
Unreal Foundation + gameplay headless
  ↓
[Physics v0.3 ainda NÃO existe]
```

---

# 5. INVENTÁRIO DE BASELINES E HASHES

| Artefato | Estado | SHA-256 / evidência principal |
|---|---|---|
| `FOOTBALL_MOBILE_TO_PC_MIGRATION_MASTER_v1_1.zip` | CONFIRMADO | `c1c7d5352f94241c5aed771666ad5f723b24593ac7cf8c3bc9bfb0e7d175e1eb` |
| `UnityStreamingAssetsPack.zip` | CONFIRMADO | `8253956de06aad31220672ccb5ace8f556975119d92a366570d81495113ed36f` |
| `FOOTBALL_PC_3D_READY_PACK_v0_1.zip` | CONFIRMADO | `5b22f66a75e694405273cdb8647084076f621b7d6cc29fc99045a018423e2ef7` |
| `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_1.zip` | CONFIRMADO | `74d6e29c0d68ceb59912e7049f85f1d57f16f225cd6905dd03f28d3756383822` |
| `FOOTBALL_PLAYER_ECOSYSTEM_CORE_v0_2_VISUAL_REGISTRY.zip` | CONFIRMADO | `cea86e1e18f7aa58f924302bae542ebf2782217b32594d315aff3ff423efe813` |
| `FOOTBALL_VISUAL_PRESENTATION_ARCHITECTURE_v1.zip` | CONFIRMADO | `a823b6d83637dc6899041348649f1b9650c060c9407786bcf9cc3e7366838645` |
| `FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip` | CONFIRMADO | `b0e1336e576c0b9dae8d04d424e706f16b18c18a28ed94b13da129a052d322b1` |
| `FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip` | CONFIRMADO | `91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64` |
| `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip` | release estável | `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac` |
| Physics workspace 92/92 | CHECKPOINT HISTÓRICO | existiu em workspace anterior; não foi entregue byte-a-byte |
| Reconstruction 92 checkpoint 2026-09-12 | reconstrução auxiliar | `c387050b23abd66726bbe31c0147e1a857a911f2942e61bd6c0c40c95ca3a9f8` |
| Master Archive v1.1 histórico | auditado | `816a7100f7652f65cf42f069bb29b4ed441e28707cf541e4f806957758ebee41` |
| Master Context 2026-09-11 | histórico/handoff | `9bab94e8cd58924b86b22c2735f6b0766f359bc587d1a9c4650e93537ef68331` |
| Mega Prompt V4 histórico | superseded | `b645981aeebe99aa9c3899cc80f783918e0ee496ce43b9fa20ebebf7b6bbbfc4` |

**Importante:** o hash antigo `f44f...` de Physics v0.2 não deve ser usado. O hash canônico é o `7d5c...` acima.

---

# 6. MIGRATION MASTER E STREAMING ASSETS

O Migration Master v1.1 é a consolidação histórica mais forte da linha de migração anterior ao Unreal. Foi validado com 4.931 entradas, sem corrupção e sem caminhos duplicados.

O `UnityStreamingAssetsPack.zip` continha aproximadamente 16.551 arquivos reais (16.788 entries no ZIP), com inventário por caminho, tamanho, CRC32, SHA-256, categoria, decode state e candidate visual ID. O trabalho histórico registrou, entre outros:

- 1.582 COFMotions;
- 305 timelines;
- dezenas de prefabs adicionais;
- referências de estádio, material, efeitos, lightmaps e cenas;
- `config/match`, `LocalSettings`, `ai_configs`, `groundData`, `xplayable`, `nova_player`, FBX, prefabs e Lua.

A política visual correta foi preservada: formatos ainda UnityFS/ASTC/custom não são “convertidos” apenas renomeando extensão. O registry registra o estado real (`unity_bundle`, `custom_player_container`, `custom_material_record`, `encoded_lua`) até existir decoder/procedimento válido.

---

# 7. RECOVERY DE ANIMAÇÃO — BASE FECHADA

## 7.1 Release

`FOOTBALL_ANIMATION_RECOVERY_PACK_v1_0.zip`  
SHA-256 `91a2a6bffeb9739807ab2ae432ed1ee79232db0b4ec4c2862cb0241027273f64`  
Status histórico: **19/19 GREEN**.

## 7.2 Controller e grafos

`controller.ctrl` foi estruturalmente fechado:

- 2.956.942 bytes;
- 20.213 `COFBlendState`;
- 50.127 clip/motion leaves;
- 30.648 Blend Tree Nodes;
- 13.722 motion hashes únicos;
- 13.722/13.722 resolvidos;
- 100% bytes consumidos;
- trailing bytes = 0.

Inventários históricos incluíram:

- `CONTROLLER_STATE_INDEX.csv`: 20.213;
- `CONTROLLER_MOTION_MAP.csv`: 50.127;
- `BLEND_TREE_EDGES.csv`: 60.562;
- `COFMOTION_INDEX.csv`: 13.722;
- `BLEND_PARAMETER_USAGE.csv`: 25 parâmetros;
- `CONTACT_EVENT_CANDIDATES.csv`: 18.101;
- animation catalog: 3.651 nomes;
- 461 correlações diretas COFMotion;
- 421 mirror aliases;
- 2.769 nomes lógicos/hierárquicos.

## 7.3 Fixed-point e timing

`XNumber`:

```text
FRACTION_BITS = 10
ONE = 1024
```

COFMotion usa **30 FPS exatos**. Conversões fixed-point e int32/wrap devem preservar comportamento nativo quando o objetivo for reproduzir o mobile.

## 7.4 Export COFMotion

O export normalizado histórico possuía aproximadamente 56 canais:

- root X/Z + yaw;
- Hips Y;
- 22 rotações de corpo;
- 30 rotações de mãos/dedos;
- COF_BallMarker XYZ.

O formato original de rotação `XQuat40U` foi preservado em sidecars onde necessário.

## 7.5 Integração Unreal

```text
controller.ctrl + COFMotion + clips recuperados
+ root movement + ball marker + kickOutFrame + kickPoint
        ↓
NORMALIZED ANIMATION DATABASE
        ↓
Unreal Animation Assets
        ↓
Pose Search Database
        ↓
Motion Matching
        ↓
Animation Blueprint
        ↓
IK Rig / IK Retargeter
        ↓
Control Rig
        ↓
Final Pose
```

**Regra crítica:** Motion Matching escolhe apresentação/movimento, não decide velocidade da bola, posse, gol, falta ou resultado do tackle.

Cadeia de contato:

```text
Action
 → kickOutFrame / kickPoint
 → BALL_CONTACT
 → GetKickVelocity recuperado
 → Ball Simulation autoritativa
```

---

# 8. PHYSICS RECOVERY — RELEASE ESTÁVEL E ESTADO ATUAL

## 8.1 Release estável v0.2

`FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`  
SHA-256: `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`

Validação histórica e posteriormente reexecutada pelo Codex com a fixture de animação correta:

- 67/67 testes GREEN;
- 83/83 tabelas byte-exact;
- 12.920.443 / 12.920.443 bytes consumidos;
- trailing = 0;
- 375 entries;
- nenhuma corrupção no ZIP.

## 8.2 Dados recuperados relevantes

### ActionSpeed
- 979 registros;
- 24.392 bytes;
- 854/979 ligados a controller states.

### ActionFit
- 15.945 registros;
- 1.084.264 bytes;
- todos mapeiam estados do controller.

### ActionFit Fixed
- 284 registros;
- 19.316 bytes.

### Collision
O metadata runtime listava `breakTime`, mas o arquivo serializado não contém esse campo. O formato recuperado contém:

`animationHash`, `collisionRegion`, `forceSize`, `forceFrom`, `stringLength`, `animationName`.

São 104 regras e 6.226/6.226 bytes. Não criar `breakTime` fictício.

### ShootSpeed
- 28 registros;
- 133.872 bytes;
- curvas/listas, fixed-point, flag de método novo, `xSpeed`, `shootPointH`, mapas de energia/distância e `shootDisAndTime`.

### Pass
Velocidade inicial recuperada usa direção XZ normalizada do alvo em relação à bola e compõe `v_x` horizontal + `v_y` vertical em fixed-point.

### Dribble
Família de velocidade de kick recuperada com interpolação bilinear e variantes LOW / NORMAL / SPEED-UP.

### Goalkeeper
Hand throw: escolha por bucket de altura e depois interpolação por distância; não existe interpolação contínua entre alturas no caminho recuperado.

## 8.3 Fixed point / ARM64

- escala 1/1024;
- 1000 ms -> 1024 raw;
- 2000 ms -> 2048;
- 999 ms -> 1023;
- preservar wrap signed int32/ARM64 onde comprovado;
- helper nativo de remap fixed-point clamped já recuperado;
- campo runtime `+0x1C0` permanece **`vertical_accel_raw`** até existir prova semântica para outro nome.

## 8.4 GetVVer — base nova recuperada

A cadeia comprovada inclui:

- distância horizontal shootPoint <-> ballPos;
- milissegundos -> XNumber segundos;
- `shootDisAndTime`;
- interpolação distância x VHor;
- `outEnergyMax`;
- `shootPointHDown` / `shootPointHUp`;
- `energyTolerance`;
- `energyNeedProtect`;
- playerHeight -> targetHeight;
- clamp de shootPointH;
- targetHeight - ballPos.y;
- solver vertical balístico;
- `ySpeedMin` / `ySpeedMax`.

Vetor de referência conhecido para config 5800:

```text
vHor=20
Distância=25m
shootDisAndTime[20][25]=1327ms
flightTime raw=1359
energy=92160
shootProperty=92160
playerHeight=1843
ballY=112
outEnergyMax=92160
energyTolerance=2560
HDown=31
HUp=394
vertical delta=1551
vertical_accel_raw=-10035
ySpeedMax=9216
vY=7828
VVer=(0,7828,0)
```

## 8.5 GetVHor — base e shootStrong

Cadeia de método novo recuperada:

```text
energyMapNew -> vHorMapNew -> baseVHor
shoot property -> shootStrongMapNew -> vHorRateNew -> baseVHor + rate
```

Exemplo config 5800:

```text
energy=38400
baseVHor=20480
shootStrong ~60 -> rate 0
~80 -> 138
~90 -> 276
~100 -> 369
exemplo: 20480 + 276 = 20756
```

## 8.6 GetKickVelocity

A composição base foi provada como soma dos componentes de VHor + VVer preservando semântica int32/wrap. Porém isso não significa que todos os modificadores contextuais anteriores estejam encerrados.

## 8.7 SPMOVE — evidência moderna do Codex

O dump IL2CPP confirma `Shoot.SpmoveInUse` como sete bool bytes:

```text
0 shootPush
1 CalmShoot
2 SAngleShoot
3 ShootFirst
4 Head
5 ShootLongKick
6 SwantonBomb
```

Métodos/RVAs recuperados na linha canônica de análise:

| Método | RVA |
|---|---:|
| `ShootUtility.GetVHor` | `0x16E6A80` |
| `ShootUtility.GetVVer` | `0x16E84A4` |
| `ShootUtility.GetKickHorSpd` | `0x16EB860` |
| `ShootUtility.GetKickVelocity` | `0x16EBAD8` |
| `XGoal_ShootBase.calSpmoveInUse` | `0x14C5548` |

Controle estático comprovado:

- `GetKickVelocity` busca config, mascara os sete bytes, chama GetVHor e depois GetVVer;
- GetVHor testa `ShootFirst` (byte 3) e `ShootLongKick` (byte 5);
- GetVVer testa `shootPush` (byte 0), `ShootLongKick` (byte 5) e `Head` (byte 4);
- `calSpmoveInUse` é um produtor dos flags, mas sua semântica completa ainda precisa de implementação de referência revisada.

Evidência de acesso de parâmetros mais recente:

- property `0x3FE` / ShootFirst: `param_Xnumber[0]` em `+0x20` no VHor, somado a termo derivado de sqrt;
- `0x3FC` / ShootLongKick: `param_Xnumber[1]` em `+0x24` no VHor e `[2]` em `+0x28` no VVer;
- `0x41A` / shootPush: `[2]` em `+0x28` no VVer, em sequência de multiplicação fixed-point;
- `0x3FB` / Head: `[2]` em `+0x28` no VVer, em sequência de multiplicação fixed-point.

Valores crus canônicos preservados por níveis:

```text
0x3FE VHor: [1500, 2000, 2500, 3000, 3500]
0x3FC VHor: [4000, 4500, 5000, 5500, 6000]
0x3FC/0x41A VVer: [900, 800, 700, 600, 500]
0x3FB VVer: [300, 600, 900, 1200, 1500]
```

**Isso ainda não prova** level selection, unidade métrica, coordinate basis, equação final completa ou comportamento executável. O gate continua bloqueado.

## 8.8 Gate obrigatório para Physics v0.3

`FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip` **NÃO existe como release válido ainda**.

Somente criar depois de:

1. recuperar/validar `calSpmoveInUse` suficiente para o fluxo necessário;
2. fechar modificador VHor de `spmoveInUseData`;
3. fechar modificador VVer;
4. finalizar GetVHor;
5. finalizar GetVVer;
6. finalizar GetKickVelocity;
7. ligar resultado a `BALL_CONTACT.velocity`;
8. remover `ball_impulse=None` apenas quando o valor estiver comprovado;
9. executar regressão completa;
10. registrar evidência e então empacotar v0.3.

---

# 9. CHECKPOINT HISTÓRICO 92/92 — AGORA RECUPERADO EM PARTES

A história deste checkpoint precisa ser tratada com precisão porque ele foi o maior ponto de perda de continuidade do projeto.

## 9.1 O que aconteceu originalmente

Depois do release estável `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip` (67/67), o trabalho continuou em um workspace temporário e chegou ao checkpoint histórico **92/92 GREEN** sem que um `v0.3` fosse empacotado. O trabalho já havia avançado por XNumber, GetVHor/GetVVer, shootStrong, shootDisAndTime, solver vertical e composição GetKickVelocity. O próximo bloco exato era `spmoveInUseData`.

Esse workspace não havia sido entregue ao proprietário antes da sessão terminar. Por isso o Codex moderno inicialmente não conseguiu encontrá-lo e começou a reconstruir parte do avanço a partir do v0.2 + documentação + ARM64.

## 9.2 Reconstrução de emergência baseada em evidência

Enquanto o original parecia perdido, foi criado:

`FOOTBALL_PHYSICS_92_CHECKPOINT_RECONSTRUCTION_2026-09-12.zip`

Essa reconstrução materializa novamente semânticas preservadas e possui uma suíte nova de reconstrução. Ela **não é byte-identical** ao workspace histórico e seus testes não são “os mesmos 92”. Serve como fallback, comparação e evidência auxiliar.

## 9.3 Atualização crítica: o proprietário recuperou o workspace original 92/92

**NOVO ESTADO:** o proprietário informa que recuperou o workspace histórico 92/92 e colocou o material em:

`C:\Users\dg71\Downloads`

Ele está **dividido em partes**, e há também, solto em Downloads, o arquivo/script/instrução usado para **montar as partes**.

Como o Codex atingiu limite antes de inspecionar esse material novo, o estado correto é:

- `92/92 histórico`: CONFIRMADO pela continuidade anterior;
- `partes originais recuperadas em Downloads`: CONFIRMADO pelo proprietário;
- `pacote original remontado`: PENDENTE;
- `integridade/hash do remontado`: PENDENTE;
- `92/92 reproduzido no PC atual`: PENDENTE até o Codex rodar a suíte original.

## 9.4 Procedimento obrigatório de recuperação

Antes de continuar reconstrução manual de GetVHor/GetVVer/spmove:

1. listar Downloads sem alterar arquivos;
2. identificar todas as partes do 92/92 e o montador correspondente;
3. registrar nome, tamanho e hash de cada parte;
4. montar em **diretório de trabalho separado**;
5. nunca sobrescrever as partes originais;
6. validar integridade do ZIP/workspace final;
7. abrir manifests/README/status/tests/tools/dumps;
8. identificar o comando original de testes;
9. executar a suíte;
10. registrar a saída completa;
11. comparar o workspace remontado com Physics v0.2 e com a reconstrução baseada em evidência;
12. se 92/92 voltar GREEN, usar esse workspace original recuperado como principal linha de continuação da física.

## 9.5 Precedência da física após a remontagem

Se a integridade e a suíte confirmarem o checkpoint:

```text
WORKSPACE ORIGINAL RECUPERADO 92/92
        >
RECONSTRUÇÃO BASEADA EM EVIDÊNCIA 2026-09-12
        >
RELEASE ESTÁVEL PHYSICS v0.2
```

Isso não significa apagar o v0.2: ele continua o último **release** estável. O 92/92 é o workspace de pesquisa mais avançado para continuação.

## 9.6 Delta esperado vs v0.2

A auditoria deve produzir uma lista exata de arquivos/testes/helpers adicionados depois do v0.2 e confirmar, entre outros:

- XNumber/Remap helpers posteriores;
- XVector2 normalization;
- GetVHor old/new base;
- `energyMapNew` / `vHorMapNew`;
- `shootStrongMapNew` / `vHorRateNew`;
- GetVVer old/new;
- `shootDisAndTime`;
- ms -> XNumber seconds;
- target-height/energy protection;
- solver balístico;
- ySpeed clamp;
- GetKickVelocity composition;
- quaisquer avanços em `BALL_CONTACT`;
- estado exato de `spmoveInUseData`.

Somente após essa auditoria a Bíblia deve receber o hash do pacote remontado e o novo comando de reprodução 92/92.


# 10. PC 3D READY — BOLA, JOGADOR E ESTÁDIO

## 10.1 Ball

O pacote PC 3D Ready v0.1 contém `ball.glb`, `ball.obj` e `collision_sphere.json`.

Métricas validadas:

- 338 vértices;
- 360 triângulos;
- raio aproximado 0,1107703 m;
- diâmetro aproximado 0,2215406 m.

Vínculos originais identificados incluíam mesh, material, albedo, normal e mask do asset de bola. Bundles originais permanecem como proveniência.

## 10.2 Cristiano — recuperação do formato proprietário

O formato de mesh foi desmontado até:

- positions;
- normals;
- UVs;
- triangles;
- bind poses;
- bone weights;
- bone indices.

Skinning identificado: 4 pesos half-float + 4 índices uint8 por vértice, com soma dos pesos próxima de 1.

Foram extraídos head, eyes, teeth, hair e componentes de corpo/roupa. O jogador montado possui aproximadamente:

- 11 geometrias;
- 14.511 vértices;
- 21.986 triângulos;
- altura aproximada 1,765 m.

O pipeline produziu assets como `player_cristiano_rigged_named.glb`, componentes rigged/bind pose e hierarquia de skeleton.

## 10.3 Campo/estádio

O campo recuperado mede aproximadamente 108,64 m x 67,35 m. Há componentes para field base, goal frame/net, advertising, grass e stadium components.

A versão final do jogo deve reconstruir conteúdo de estádio como produção Unreal/Blender moderna, sem perder escala, colisão, material provenance e possibilidade de LOD/culling.

---

# 11. NEYMAR — CHECKPOINT PRESERVADO E PRIORIDADE PAUSADA

## 11.1 Asset atual

`player_neymar_psg_2017_v1_9_UNITY_READY.glb`

- 48.263.832 bytes;
- SHA-256 `fba8dca5bd4fa0f28f4ac05d2f32ddc035907d0c154167ab84e8f99bd70e4f48`;
- 60 joints;
- 13 skinned meshes;
- 221.449 vertices;
- 85.507 triangles;
- 9 materials;
- 65 head blendshapes;
- tangents presentes;
- erro máximo de soma de skin weights ~4,47e-08;
- boot/sock PBR;
- clipes `RigExercise_v19` e `FaceExercise_v19`;
- structural validation `failureCount=0`.

Pacotes:

- checkpoint v1.9 SHA `872041cd84a226b645946803033649a9459f8ba4e777562ce2ae07080bc59000`;
- runtime v1.9 SHA `b653e65b9598b784353e3b424d1ba87e1e88a4254a6bd45dfb430f0e72a20f3`.

## 11.2 Regra vigente

**PAUSADO:** não iniciar agora Neymar Master v2, sculpt facial, cabelo, roupa específica, materiais, chuteiras, LODs hero ou polimento cosmético.

Preservar v1.9 e usar apenas como fixture quando útil. Gameplay deve avançar com jogadores recuperados, genéricos, Cristiano e meshes já convertidos.

A regra arquitetural é:

```text
PLAYER GAMEPLAY
NÃO DEPENDE DE
PERSONAGEM HERO FINAL
```

Quando o projeto voltar ao Neymar, continuar do v1.9; não reconstruir do zero.

---

# 12. FOOTBALL SIMULATION — CONTRATO CENTRAL

Football Simulation deve ser independente de Career e de apresentação. Partida normal, carreira e online consomem o mesmo núcleo.

## 12.1 Estado da bola

Estados conceituais:

- Free;
- Controlled;
- Kicked;
- Deflected;
- GoalkeeperControlled;
- Dead/Restart.

Campos/efeitos alvo:

- position;
- velocity;
- angular velocity / spin;
- drag;
- Magnus/curve quando sustentado;
- grass friction;
- bounce/restitution;
- wetness/surface interaction;
- frame/post/net collision;
- player/keeper contact.

## 12.2 Contatos

Contatos são ordenados pelo tick de simulação e registram, quando aplicável:

- action source;
- player/entity;
- contact frame/time;
- kickPoint;
- tuning/provenance selecionada;
- resultado calculado.

Unreal Collision/Chaos pode fornecer geometria/overlap/collision data, mas Football Simulation decide semanticamente posse, velocidade, gol e regras.

## 12.3 Primeiro toque

`FirstTouchSystem` deve distinguir pelo menos:

- Controlled;
- Heavy;
- Deflection;
- Failed.

A decisão considera velocidade/ângulo da bola, pressão, equilíbrio, atributos e input.

## 12.4 Passing

- ground pass;
- driven pass;
- through pass;
- lob/high pass;
- cross;
- cutback.

A assistência não pode virar teleporte. Targeting e direção precisam respeitar espaço, atributos, corpo, timing e pressão.

## 12.5 Shooting

- normal shot;
- finesse/placed;
- power;
- chip;
- volley;
- header;
- aerial variants;
- set pieces.

Força, direção e curva devem respeitar física/contato recuperado, atributos e contexto.

## 12.6 Dribble / carry / protection

- carrying;
- close control;
- acceleration out of touch;
- body protection/shield;
- direction changes com inércia;
- skill moves data-driven.

## 12.7 Defense

- contain;
- jockey;
- sprint jockey;
- standing tackle;
- slide tackle;
- shoulder challenge;
- interception;
- block;
- clearance;
- second-man press.

Evitar magnetismo e “roubo garantido” apenas por apertar botão.

## 12.8 Goalkeeper

- positioning;
- set stance;
- catch;
- parry;
- dive;
- smother;
- rush;
- 1v1;
- cross claim;
- punch;
- distribution / hand throw / kick.

BallState permanece autoridade.

---

# 13. LOCOMOÇÃO E CONTROLE DO JOGADOR

A locomotion separa:

```text
Input Intent
 → desired velocity
 → acceleration / braking
 → turn rate
 → body orientation
 → simulation state
 → presentation pose
```

Player AI e input humano usam o mesmo contrato de intenção/comando, evitando duas físicas diferentes para humanos e bots.

Objetivos de sensação:

- resposta rápida sem ignorar inércia;
- sprint com custo/compromisso;
- frenagem visível;
- curvas realistas;
- sem rotação instantânea a 180 graus;
- sem foot sliding como solução permanente;
- nenhum “action teleport”.

Gamepad é a referência primária de feel, mas teclado/mouse precisa funcionar desde o primeiro produto jogável. Rebinding, deadzone, sensitivity e hold/toggle pertencem às configurações.

---

# 14. SKILL MOVES

Skill moves são sistemas de gameplay, não invulnerabilidade cosmética.

Lista consolidada:

- Body Feint;
- Step Over;
- Double Step Over;
- Ball Roll;
- Drag Back;
- Fake Shot;
- Heel-to-Heel;
- Roulette;
- Elastico;
- Reverse Elastico;
- Heel Chop;
- Stop Turn;
- Flick;
- Directional Nutmeg.

Resultado depende de timing, espaço, velocidade, atributos técnicos, equilíbrio e leitura do defensor. A bola continua sob simulação.

---

# 15. REGRAS E REFEREE

`FootballRules` / `FootballMatch` são autoridade de regras. Renderer/UI não inventam restart por overlap.

Cobertura alvo:

- kickoff;
- goal / goal confirmation;
- out of bounds;
- throw-in ou perfil configurável de restart;
- goal kick;
- corner;
- direct/indirect free kick;
- penalty;
- offside;
- advantage;
- fouls;
- yellow/red cards;
- substitutions;
- injury hooks;
- match clock;
- stoppage time;
- halftime/full time;
- extra time;
- penalty shootout.

Offside deve considerar momento do passe, posição do atacante, segundo último defensor e envolvimento na jogada. Falta deve derivar de contato/timing/força/ângulo e regras, não de aleatoriedade arbitrária.

---

# 16. IA DE FUTEBOL — CAMADAS

Não existe uma “classe gigante de AI”.

## 16.1 Player AI

```text
Perception
 → Decision
 → MovementIntent / Planner
 → ActionSelector
 → Execution
```

Responsabilidades: reação local, opções de passe, condução, chute, tackle, posicionamento imediato e comportamento sem bola.

## 16.2 Team AI

`TeamBrain + TacticalState + RolePlanner`.

Responsabilidades:

- compactação;
- largura/profundidade;
- pressing;
- cover;
- marking;
- passing lanes;
- runs;
- support;
- transitions;
- counters;
- set pieces;
- adaptação ao placar/tempo.

## 16.3 Goalkeeper AI

Camada própria por especificidade de posicionamento, ângulo, catch/parry, saída e tomada de decisão.

## 16.4 Manager AI

- lineup XI;
- bench;
- substitutions;
- formation;
- tactical plan;
- rotation;
- squad role / minutes;
- resposta a condição física, forma e adversário.

## 16.5 Club AI

- squad planning;
- budgets;
- contracts;
- transfers;
- loans;
- renewals;
- releases;
- balanceamento de posições e idade.

## 16.6 Background Match AI

Partidas não jogadas usam simulação coerente e determinística com lineup, tactics, attributes, form, fatigue, home context e seed explícita.

## 16.7 Dificuldade

Não trapacear. Variar principalmente:

- perception quality;
- reaction delay;
- decision quality;
- positioning;
- risk tolerance;
- technical execution variance;
- team coordination.

## 16.8 Frequências e performance

- reaction: alta frequência;
- decision: intermediária;
- team tactics: menor;
- manager/club: evento/calendário;
- relevance/AI LOD para custo.

Jogadores longe da bola não podem simplesmente “desligar o cérebro” e destruir a estrutura tática.

---

# 17. MODOS DE JOGO

Escopo final consolidado:

- Training/Practice;
- 3v3;
- 5v5;
- 11v11;
- Player Career;
- Career 11v11;
- Career 5v5;
- Career co-op 11v11;
- Career co-op 5v5;
- partidas online server-authoritative;
- modos de controle `OWN_PLAYER_ONLY` e `PLAYER_CAREER_TEAM_CONTROL`.

Um 3v3, 5v5 ou 11v11 funcionando isoladamente é checkpoint, não Definition of Done.

---

# 18. CAREER UNIVERSE

Career Universe deve ser engine-independent e testável sem Unreal Editor/rendering.

Agregados/entidades principais:

- CareerUniverse;
- Season;
- Club;
- Player;
- CareerPlayerState;
- Contract;
- Registration;
- TransferCase;
- CompetitionInstance;
- CalendarEvent;
- Fixture;
- Standings;
- Brackets;
- Training;
- Development;
- Form;
- Morale;
- Fatigue;
- Injury;
- Suspension;
- ManagerTrust;
- History / event stream.

## 18.1 Dois modos de controle do Player Career

### OWN_PLAYER_ONLY
O usuário controla apenas seu CareerPlayer. O restante do time é IA.

### PLAYER_CAREER_TEAM_CONTROL
Existe um CareerPlayer próprio persistente, porém o usuário pode controlar o time quando o modo permitir.

Não confundir esses modos com Manager Career.

## 18.2 Seleção do atleta

O CareerPlayer humano não deve ser titular automaticamente.

Estados:

- NotSelected;
- Bench;
- Starter.

Fatores:

- overall;
- form;
- fitness;
- injury;
- suspension;
- tactical fit;
- ManagerTrust;
- squad role.

No banco, pode existir spectate / `SIM_UNTIL_SUBSTITUTED`. Ao entrar, o servidor transfere controle ao owner legítimo. Não selecionado nunca “teleporta” para o campo.

## 18.3 Co-op Career

Cada humano possui stable owner + CareerPlayer próprio:

```text
Human A -> CareerPlayer A
Human B -> CareerPlayer B
Human C -> CareerPlayer C
restante -> SERVER_AI
```

Nenhum cliente controla o CareerPlayer de outro humano.

Para jogarem juntos no mesmo clube, precisam chegar legitimamente ao mesmo time por contratos/transferências. O mundo da carreira não é ignorado para facilitar lobby.

Opções históricas de proposta entre amigos:

- `REJECT`;
- `ACCEPT_STANDARD_TRANSFER`;
- `ACCEPT_IMMEDIATE_TERMINATION` com consequência contratual/econômica;
- `ACCEPT_PRE_CONTRACT`.

Respeitar janelas, inscrições, orçamento, squad limits e invariant de um contrato/registro ativo válido.

Quando uma mudança de política de controle afeta humanos, a decisão definida historicamente exige unanimidade dos participantes afetados.

## 18.4 Desconexão

Default: AI takeover temporário preservando ownership humano. Em reconnect, o mesmo owner recupera seu CareerPlayer após rehidratar snapshot, clock, score, ownership e bola.

---

# 19. PROGRESSÃO DO JOGADOR DE CARREIRA

Atributos 1–99 organizados em grupos:

- Physical;
- Technical;
- Mental;
- Defensive;
- Goalkeeper.

OVR por posição utiliza `AttributeWeightProfile`.

Desenvolvimento considera:

- age;
- potential;
- training;
- minutes;
- match performance;
- facilities;
- form/morale/fitness;
- injuries e disponibilidade.

Humano pode usar `DevelopmentXP` + `SkillPoints`.

Árvores:

- PACE;
- TECHNIQUE;
- PASSING;
- SHOOTING;
- PHYSICAL;
- DEFENDING;
- MENTAL.

Archetypes:

- Playmaker;
- Dribbler;
- Finisher;
- Speedster;
- TargetForward;
- BoxToBox;
- BallWinner;
- DeepPlaymaker;
- WingBack;
- Stopper;
- SweeperKeeper.

ManagerTrust: 0–100.  
SquadRole: Prospect / Rotation / Important / Star.  
PlayerForm: Poor / Average / Good / Excellent.

---

# 20. COMPETITION ENGINE

O mesmo motor de competição atende 5v5 e 11v11 por configuração, não por duplicação de código.

Primitivos:

- CompetitionDefinition;
- CompetitionInstance;
- StageDefinition;
- LeagueStage;
- GroupStage;
- KnockoutStage;
- PlayoffStage;
- Fixture;
- StandingsRow;
- BracketRound / Tie / Slot;
- CompetitionQualificationRule;
- CompetitionDrawEngine.

Capacidades:

- single/double round robin;
- standings/tiebreakers configuráveis;
- fixtures determinísticos por seed persistente;
- home/away balance;
- calendar/rest constraints;
- groups;
- single/two-leg knockout;
- extra time / penalties;
- away goals opcional e desligado por default;
- seeded/random draws;
- pots/restrictions;
- qualifications;
- promotion/relegation;
- season rollover;
- projeção read-only de bracket para UI.

QA de referência:

- 8 clubes double round-robin: 14 jogos por clube, 56 total;
- knockout de 8: 4 QF + 2 SF + 1 final;
- 4 grupos x 4 clubes em turno/return: 6 jogos por clube;
- nenhum clube duas vezes na mesma rodada;
- winner propagation independe da UI;
- `MatchResult` idempotente não duplica standings;
- simular 1.000 seasons para estados impossíveis/duplicações.

---

# 21. PLAYER ECOSYSTEM — IDENTIDADE, CARTAS, ELENCO E MERCADO

## 21.1 Identidades separadas

Não colapsar:

- `PlayerDefinition`;
- `PlayerCardDefinition`;
- `PlayerCardInstance`;
- `PlayerId`;
- `CardDefinitionId`;
- `CardInstanceId`;
- `CareerPlayer`.

Carta/progressão de carta não é desenvolvimento de carreira.

Fluxo:

```text
PlayerDefinition
 → PlayerAssetRegistry / PlayerCardDefinition
 → PlayerCardInstance
 → Roster
 → Squad
 → Formation
 → Tactics
 → MatchSquadSnapshot
 → Gameplay Runtime
```

## 21.2 Cartas

Campos típicos:

- player_id;
- card_definition_id;
- instance_id;
- owner_id;
- edition;
- rarity;
- season;
- quality;
- visual_theme_id;
- level;
- exp;
- upgrade_tier;
- training_points;
- locked;
- trade_state;
- tradable.

`CardPresentationService` pode projetar nome, posição, OVR, level, EXP, upgrade, edition, rarity, season, theme e estado de mercado.

Temas visuais recuperados incluem famílias normal, special, legend, future_star, ucl_2025, fcwc_2025, laliga, european, black, red e outras.

## 21.3 Progressão de carta

```text
match/training -> EXP -> Level -> Training Points -> Upgrade Tier
```

Inclui evolução, materials, refund e upgrade transfer.

**Separação obrigatória:**

```text
CARD DEVELOPMENT
level / exp / upgrade / training

!=

CAREER DEVELOPMENT
age / potential / form / fitness / morale / fatigue /
minutes / long-term attributes / injuries / contracts
```

## 21.4 Roster / Squad

`RosterService` distingue Owned Cards de Squad Eligible. Item listed/consumed/inválido não entra silenciosamente em escalação.

### 11v11
Formação demo/referência: 3-4-1-2 (`t_formation_config.lua`, id 34120):

GK / LCB / CB / RCB / LM / LCM / RCM / RM / CAM / LST / RST, bench/reserves e set pieces.

### 5v5
1-2-1:

GK / L / R / AM / ST.

Táticas incluem TeamTactics, PlayerInstructions, PositionCompatibility e SetPieceRoles.

## 21.5 MatchPlayerSnapshot

Gameplay recebe snapshot imutável em vez de conhecer mercado/inventory/UI:

- PlayerId;
- CardInstanceId;
- name;
- position;
- OVR;
- resolved attributes;
- position fit;
- form;
- fitness;
- fatigue;
- tactical instruction;
- model/skeleton/animation references.

---

# 22. MERCADO, AQUISIÇÃO E ECONOMIA

Serviços historicamente estruturados:

- CreateListing;
- BuyListing;
- CancelListing;
- CreatePurchaseOrder;
- CancelPurchaseOrder;
- MatchPurchaseOrders;
- Favorites;
- SearchListings;
- PriceHistory;
- AveragePrice;
- MarketTax;
- EconomyLedger;
- QuickSell;
- Scout;
- Recruitment;
- Packs;
- Draws;
- Exchange;
- Rewards;
- Save/Load.

Exemplo de teste/demo histórico:

```text
Preço: 25.000
Taxa 5%: 1.250
Vendedor recebe: 23.750
Comprador: 100.000 -> 75.000
Nova propriedade da carta: club.demo
```

A UI envia comandos; não altera diretamente owner, wallet ou trade state.

---

# 23. VISUAL REGISTRY E PRODUÇÃO VISUAL

Decisão fechada:

> **Reaproveitar a produção visual do mobile, mas não transformar a UI/UX mobile na arquitetura definitiva de PC.**

## 23.1 Visual Production Asset Pack

`FOOTBALL_VISUAL_PRODUCTION_ASSET_PACK_v0_1.zip`:

- 1.119 entries ZIP;
- 0 corrompidas;
- 1.106/1.106 assets validados por SHA;
- 268 assets de cartas;
- 165 heads (55 identidades x high/low/ultralow);
- 292 texturas head/hair;
- 96 uniform/material cloth;
- 144 emblems;
- 44 sponsors;
- 39 shoes;
- 38 GK gloves;
- 20 grupos/configs de clube.

## 23.2 Player Visual Registry

Um PlayerId estável resolve modelo, head LODs, texturas, cabelo, kit/club visual, portrait/fallback e demais variantes.

Exemplo conceitual:

```text
player.cristiano_ronaldo
  -> player visual registry
  -> head_high / head_low / head_ultralow
  -> textures
  -> player_cristiano_rigged_named.glb
```

## 23.3 Portrait fallback

Não foi encontrada uma biblioteca separada confiável de portraits PNG de todos os atletas. Portanto:

```text
portrait específico recuperado
 -> senão render do head/model
 -> senão silhueta/fallback genérico
```

## 23.4 Fallbacks não podem quebrar gameplay

Carta: tema específico -> família edition -> família rarity -> normal.  
Jogador: portrait -> rendered head -> silhouette.  
Clube: específico -> competition default -> neutral/default.

---

# 24. MATCH EVENT STREAM

Eventos de partida formam uma linguagem comum entre simulação e sistemas externos:

- Pass;
- Shot;
- Goal;
- Assist;
- Save;
- Tackle;
- Interception;
- Foul;
- Card;
- Offside;
- Substitution;
- Injury.

Consumidores:

- statistics;
- career history;
- commentary hooks;
- news/feed;
- replay;
- achievements;
- backend persistence/telemetry.

---

# 25. CÂMERAS

Câmeras previstas:

- BroadcastCamera;
- PlayerCareerCamera;
- TrainingCamera;
- SetPieceCamera;
- ReplayCamera;
- GoalkeeperCamera.

## 25.1 Broadcast

Leitura profissional, visão de linhas, antecipação da jogada, enquadramento suave e útil para 5v5/11v11.

## 25.2 Player Career

Atrás e ligeiramente acima do atleta, com:

- dynamic distance/FOV;
- awareness da bola;
- off-ball framing;
- lookahead;
- recenter;
- collision avoidance;
- tratamento de sprint e espaços pequenos;
- set piece handling;
- câmera local por client.

Objetivo: imersão sem enjoo e sem perder contexto tático.

---

# 26. MUNDO, ESTÁDIOS E PITCH

O escopo inicial do “mundo” não é um open world gigante. Prioridades:

- stadiums;
- training grounds;
- locker room;
- tunnel;
- club facilities;
- 5v5 arena.

Blender modular pode produzir:

- GenericSmallStadium;
- GenericMediumStadium;
- GenericLargeStadium;
- TrainingGround;
- 5v5Arena.

`PitchSystem` deve parametrizar dimensões, markings, grass, friction, wetness e wear. Goals possuem collision, net interaction e goal detection semanticamente robusta.

---

# 27. ÁUDIO, VFX E REPLAY

Arquitetura de áudio:

- crowd;
- ball impacts;
- kicks/passes;
- post/net;
- whistle;
- player impacts;
- stadium ambience;
- UI;
- music;
- commentary hooks.

Conteúdo definitivo não precisa bloquear gameplay: usar fallback claramente marcado quando necessário.

Niagara, materiais e iluminação devem enriquecer movimento e leitura, não apenas screenshot.

Replay deve ser dirigido por estados/eventos determinísticos e snapshots, não gravação improvisada de transforms sem semântica.

---

# 28. UI/UX PC

## 28.1 Menu principal

- PLAY;
- CAREER;
- ONLINE;
- TRAINING;
- CUSTOMIZE;
- SETTINGS;
- EXIT.

## 28.2 Career entry

- CONTINUE;
- NEW 11V11 PLAYER CAREER;
- NEW 5V5 PLAYER CAREER;
- JOIN CO-OP CAREER;
- LOAD CO-OP CAREER.

Wizard:

- format;
- solo/co-op;
- player creation;
- starting club;
- difficulty;
- control mode;
- settings.

## 28.3 Career Hub

- NEXT MATCH;
- CALENDAR;
- STANDINGS;
- COMPETITIONS;
- MY PLAYER;
- DEVELOPMENT;
- TRAINING;
- CLUB;
- CONTRACT;
- TRANSFERS;
- STATISTICS;
- CAREER HISTORY;
- FRIENDS/CO-OP.

## 28.4 Settings

- Gameplay;
- Controls;
- Camera;
- Graphics;
- Audio;
- Accessibility;
- Online.

Acessibilidade:

- remapping;
- deadzones;
- sensitivity;
- vibration;
- camera shake;
- UI scale;
- text size;
- colorblind/high contrast;
- reduced motion;
- hold/toggle.

Localização inicialmente pt-BR + en-US.

---

# 29. ARQUITETURA UNREAL CANÔNICA

## 29.1 Stack

```text
Windows PC
Unreal Engine 5.x
C++ modular core
Blueprint complementar
Blender 3D source of truth
Python + C++ + Editor tools para automação
Dedicated Server server-authoritative
```

## 29.2 Módulos conceituais

```text
Source/
├── FootballCore/
├── FootballSimulation/
├── FootballBall/
├── FootballPlayer/
├── FootballAnimation/
├── FootballGameplay/
├── FootballMatch/
├── FootballRules/
├── FootballReferee/
├── FootballGoalkeeper/
├── FootballTactics/
├── FootballAI/
│   ├── PlayerAI/
│   ├── TeamAI/
│   ├── ManagerAI/
│   └── ClubAI/
├── FootballCareer/
│   ├── CareerUniverse/
│   ├── PlayerCareer/
│   ├── Progression/
│   ├── Training/
│   ├── Contracts/
│   └── Transfers/
├── FootballCompetition/
│   ├── League/
│   ├── Groups/
│   ├── Knockout/
│   ├── Brackets/
│   └── Qualification/
├── FootballCareerCoop/
├── FootballMultiplayer/
├── FootballNetworking/
├── FootballPersistence/
├── FootballUI/
├── FootballAudio/
├── FootballTools/
└── FootballTests/
```

Os nomes exatos podem ser refinados por dependência/compile profiling; a separação de responsabilidade é o contrato importante.

## 29.3 Gameplay Framework

Direção:

- GameMode: regras/autorização server-only;
- GameState: estado replicado de partida;
- PlayerState: identidade/ownership;
- PlayerController: Enhanced Input -> intent/commands;
- Character/Pawn: representação e collision do player;
- BallActor: proxy/representação da bola;
- Simulation Subsystem: fixed-step sim;
- Match Subsystem: lifecycle;
- Career adapter/subsystem: ponte engine-independent;
- UI layer: UMG/CommonUI;
- Animation layer: ABP/Pose Search/IK/Control Rig.

## 29.4 Fluxo do input

```text
Enhanced Input
 -> Input Intent
 -> Gameplay Command
 -> validação de sequence/tick/owner/limits
 -> Server Command Queue
 -> Fixed Simulation
 -> events + snapshots
 -> replication/reconciliation
 -> presentation (animation/camera/UI/audio/VFX)
```

---

# 30. BLUEPRINT — ONDE USAR E ONDE NÃO USAR

Blueprint é recomendado para:

- Animation Blueprint;
- Motion Matching setup;
- Control Rig;
- IK Rig / IK Retargeter;
- UMG / CommonUI;
- Niagara;
- materials;
- visual composition;
- level composition;
- editor-facing configuration.

Não colocar a arquitetura de Football Simulation, Career Universe, Competition Engine, persistence ou autoridade de rede em Blueprints gigantes.

---

# 31. MULTIPLAYER E REDE

## 31.1 Autoridade

```text
CLIENT
 -> Enhanced Input
 -> Input Intent / Gameplay Command
 -> UNREAL DEDICATED SERVER
    - ownership
    - simulation
    - ball authority
    - tackle/foul/goal
    - match rules/state
 -> snapshots/replication
 -> CLIENTS
```

Cliente não define BallState, score, foul, possession, identidade de outro owner ou resultado de tackle.

## 31.2 Prediction / reconciliation

- prediction local apenas dentro do contrato;
- servidor valida sequence/tick/owner/limits;
- reconcile contra snapshots;
- remote interpolation;
- rates por perfil e profiling.

Faixas exploratórias, não dogmas:

- simulation ~60 Hz;
- ball substep até ~120 Hz se necessário;
- snapshots ~20–30 Hz.

## 31.3 Testes de rede

- 0/30/80/150 ms;
- jitter;
- 1/2/3% loss;
- duplicate/reorder;
- disconnect/reconnect;
- 2+ owners;
- server headless.

## 31.4 Party / Lobby

PartySystem é separado de MatchLobby. Lobby valida universe/club, eligibility, ownership, votes e readiness.

---

# 32. BACKEND E PERSISTÊNCIA

Uma linha de documentação posterior propôs backend **ASP.NET Core modular monolith + PostgreSQL**. Tratar isso como baseline de serviços/persistência, não como requisito de runtime do Unreal.

Regras importantes:

- cliente Unreal nunca acessa banco diretamente;
- saves/economia/match results críticos não dependem de autoridade do cliente;
- contratos de API e domínio permanecem engine-independent;
- storage pode evoluir sem contaminar Football Simulation.

Save local/offline precisa de:

- schema version;
- migration support;
- atomic writes;
- backup;
- corruption detection/recovery;
- round-trip tests.

Persistir conforme modo: career, player development, cards/inventory, squad, formations, tactics, economy, world state, fixtures, standings, statistics e settings.

---

# 33. AUTOMAÇÃO — REGRA OBRIGATÓRIA

O proprietário não deve ter de aprender/realizar manualmente tarefas repetitivas de Unreal/Blender/C++.

Direção de tooling:

```text
Tools/Blender/
├── player_import.py
├── player_validate.py
├── player_lod.py
├── player_export.py
├── rig_validate.py
└── stadium_export.py

Tools/Unreal/
├── import_players.py
├── import_stadiums.py
├── setup_skeleton.py
├── create_ik_rig.py
├── create_ik_retargeter.py
├── create_control_rig.py
├── setup_materials.py
├── setup_physics_asset.py
├── setup_lods.py
├── import_animations.py
└── validate_content.py
```

Scripts devem ser idempotentes, receber inputs/outputs explícitos, registrar hashes, falhar cedo e nunca mutar frozen sources.

Unreal Python/Editor Utility serve editor automation. Commandlets e módulos C++ Editor devem permitir validação headless quando possível.

---

# 34. TESTING, TDD E EVIDENCE-BEFORE-ASSERTION

Fluxo obrigatório por subsistema:

1. entender comportamento;
2. localizar/escrever teste;
3. RED quando aplicável;
4. implementar;
5. GREEN;
6. regressão;
7. commit/checkpoint;
8. registrar evidência.

Suites:

- fixed math / XNumber / int32 wrap / RNG / units / serialization;
- parser byte consumption / trailing / hashes;
- recovery golden tests;
- simulation integration: movement, first touch, pass, shot, dribble, tackle, intercept, collision, GK, goal, restart;
- Unreal Automation Tests;
- Functional Tests em mapa;
- network/Gauntlet;
- Career/Competition headless;
- save/load/migration/corruption;
- performance captures.

Um relatório histórico GREEN não é current GREEN até o comando atual ser executado sobre checkout atual.

---

# 35. BUILD, CI E RELEASE PIPELINE

UnrealBuildTool é autoridade para build.

Targets esperados:

- Football/Game Target;
- FootballClient Target;
- FootballServer Target;
- Editor Target quando necessário;
- Build.cs por módulo.

Pipeline conceitual:

```text
Generate project / validate engine
 -> compile Development Editor/Client
 -> compile Development Server
 -> Automation Tests
 -> content validation
 -> cook/package Windows client
 -> cook/package Dedicated Server
 -> smoke launch
 -> artifact manifest
```

Cada artefato registra commit, engine version, target, platform, config, source hashes, test receipts e provenance.

---

# 36. PERFORMANCE — META 120 FPS

Meta principal: **120 FPS estáveis em partida real** no hardware de referência, ~8,33 ms/frame.

Medições separadas:

- Game Thread;
- Render Thread;
- GPU;
- Physics;
- Ball Simulation;
- Animation;
- Player AI;
- Team AI;
- Networking;
- Crowd;
- UI;
- Memory;
- VRAM;
- Streaming.

Não vale medir somente menu, campo vazio ou um jogador.

Matriz real inclui:

- 5v5;
- 11v11;
- Broadcast Camera;
- Player Career Camera;
- stadium;
- crowd;
- AI completa;
- ball;
- animation;
- HUD.

Relatório deve registrar hardware, driver, build, map, player count, mode, preset, resolution, cap, capture duration, tool, p50/p95/p99 e bottleneck.

## 36.1 Escalabilidade

LOW / MEDIUM / HIGH / ULTRA e opções independentes.

Separar **Simulation Quality** de **Rendering Quality**. Reduzir crowd/animation/render LOD não deve destruir lógica da partida.

## 36.2 Frame-rate independence

Lógica idêntica em 60/90/120/144/240 FPS. Usar fixed/sub-stepped simulation e render interpolation conforme profiling.

## 36.3 Recursos Unreal

Nanite, Lumen, Virtual Shadow Maps, TSR, Niagara, modern materials, grass, stadium lighting, crowd/character LOD e culling são ferramentas, não checkboxes obrigatórios. Usar quando o profiling justificar.

---

# 37. ESTADO ATUAL DO WORKSPACE MODERNO/CODEX

## 37.1 Branch e commits conhecidos

Branch registrado nos logs: `codex/unreal-football-foundation`.

Commits duráveis citados:

- `5242e31ebc7ec30af4e5b58a5600f3bd52786c2a` — foundation Unreal + playable reference;
- `107e6b2` — checkpoint posterior registrado em log.

O workspace moderno já criou documentação Unreal v1.2, ADR de engine, Mega Prompt Unreal v5, contratos normalizados, recovery evidence, ferramentas, scaffold C++ e test harnesses.

## 37.2 Headless playable fixture

Existe implementação C++ de referência/headless capaz de exercitar:

- rosters 3v3/5v5/11v11;
- server ownership;
- acceleration/braking;
- possession;
- pass;
- shot;
- dribble;
- tackle;
- goalkeeper save;
- goal;
- restart.

Essa fixture usa tuning explicitamente marcado `NewGameAuthored` onde a semântica mobile ainda não está fechada. Ela é uma ponte de arquitetura, não uma desculpa para substituir recovery por aproximação silenciosa.

Resultado C++ registrado: `FOOTBALL_REFERENCE_TESTS: 13/13 GREEN`.

Uma suíte Python chegou a checkpoint durável reportado em **40/40**; sessões posteriores alteraram/incrementaram ferramentas específicas. Sempre usar a saída atual do workspace para números novos, nunca somar contagens de suites diferentes.

## 37.3 Unreal real

Na rodada anterior do Codex, `UnrealEditor`, `UnrealEditor-Cmd` e UnrealBuildTool não foram encontrados. O proprietário informou que iniciou o download/instalação do Unreal Engine. A versão menor exata 5.x não deve ser considerada travada apenas por um `.uproject` provisório.

Assim que o engine estiver disponível:

1. localizar a instalação real;
2. associar/ajustar `EngineAssociation` se necessário;
3. gerar project files;
4. compilar Game/Client/Server;
5. corrigir Build.cs/Target.cs/API reais;
6. executar Automation Tests/commandlets;
7. importar mapa/campo/bola/player genérico;
8. ligar Enhanced Input e simulação;
9. validar uma partida Unreal real.

Até isso acontecer, o headless C++ é checkpoint de domínio, **não** uma partida Unreal renderizada.

## 37.4 Atualização de fontes após o limite do Codex

Depois que o Codex atingiu o limite, o proprietário reorganizou/recuperou novas fontes importantes. Na próxima sessão o agente deve **primeiro**:

- ler os novos arquivos em `Downloads`;
- montar e validar o 92/92 recuperado em partes;
- ler/organizar a árvore 1-221-5 em `Videos`;
- deduplicar cópias 1-221-5 por SHA-256;
- manter 1-226-19 fora da linha atual;
- só depois retomar `spmoveInUseData`.

Não iniciar nova varredura de Documents/Desktop/Temp/OneDrive.


# 38. ROADMAP CANÔNICO

0. Unified Recovery/Audit.  
1. Finish Physics Recovery (`spmoveInUseData` -> final VHor/VVer -> GetKickVelocity -> BALL_CONTACT -> v0.3).  
2. Normalize recovered football data.  
3. Unreal Engine 5.x C++ foundation.  
4. Recovered animation integration in Unreal.  
5. Football vertical slice using recovered physics/animation.  
6. Neymar Blender Master v2.0 **mais tarde; atualmente pausado**.  
7. Advanced mechanics.  
8. Football AI.  
9. Rules/referee.  
10. 3v3/5v5 standalone.  
11. 11v11 offline.  
12. Career Core.  
13. Career 11v11.  
14. Career 5v5.  
15. Club/Manager AI.  
16. Backend/identity/party.  
17. Match networking.  
18. Online friend matches.  
19. Co-op Career 11v11.  
20. Co-op Career 5v5.  
21. Friend recruitment/contracts.  
22. Player Ecosystem/cards/market.  
23. Final PC UI/UX.  
24. Stadium/content/audio/generic players.  
25. Optimization/accessibility/localization.  
26. Release candidate.

A ordem pode ser intercalada quando isso reduzir risco, mas nenhuma fase pode apagar uma baseline comprovada.

---

# 39. ORDEM TÁTICA IMEDIATA PARA CODEX

A próxima sessão do Codex deve seguir esta ordem, sem recomeçar arquitetura ou recovery já provado.

## 39.1 Recovery de fontes primeiro

1. permanecer no repositório/workspace atual para desenvolvimento;
2. para descoberta de fontes locais, usar **somente Downloads e Videos**;
3. em Downloads, localizar as partes do workspace histórico 92/92 e o montador;
4. montar em diretório separado e preservar originais;
5. rodar a suíte original e provar se 92/92 volta GREEN;
6. gerar hash/manifest do resultado remontado;
7. comparar com v0.2 e com a reconstrução baseada em evidência;
8. em Videos, auditar `football-dream-be-a-pro-1-221-5` e os ZIPs/APKs/pastas extraídas;
9. criar matriz de cópias 1-221-5 e deduplicar por SHA-256;
10. registrar apenas a localização de 1-226-19; não utilizá-la.

## 39.2 Física

Se o workspace original 92/92 validar:

```text
spmoveInUseData
 -> VHor modifier
 -> VVer modifier
 -> GetVHor FINAL + GetVVer FINAL
 -> GetKickVelocity FINAL
 -> BALL_CONTACT.velocity
 -> remover ball_impulse=None
 -> regressão completa
 -> Physics Recovery v0.3
```

Não refazer GetVHor/GetVVer base se já existirem e estiverem verdes no workspace recuperado.

## 39.3 Integração Unreal em paralelo

Quando Unreal real estiver instalado, continuar simultaneamente com a fundação e o primeiro gameplay real. Não esperar toda a engenharia reversa acabar para importar campo/bola/player genérico e validar a cadeia de input/simulação/render.

Primeiro playable Unreal real:

```text
campo + gols + bola + jogador + goleiro + câmeras + input
 -> movimento + first touch + passe + chute + drible + tackle + save
 -> goal/restart
 -> 3v3
 -> 5v5
 -> 11v11
```

O Neymar continua pausado.


# 40. DEFINITION OF DONE

Não dizer “jogo pronto” porque compila, abre menu ou inicia uma partida.

Produto final exige no mínimo:

- **Windows build real** reproduzível;
- startup sem hacking manual;
- keyboard/gamepad;
- começar, jogar e terminar partida;
- bola correta em passes, chutes, contatos, terreno e gol;
- jogadores com input + AI + animação;
- goleiro funcional;
- regras principais;
- 11v11 funcional;
- 5v5 funcional;
- Career persistente;
- Career 5v5;
- Co-op Career com ownership correto;
- AI teams;
- Competition Engine;
- player development;
- cards/roster/squad integrados;
- save/load;
- UI essencial;
- settings persistentes;
- performance aceitável sem blocker crítico;
- testes obrigatórios GREEN;
- zero blocker P0/P1 aberto;
- package final organizado;
- README de execução;
- evidência de smoke test.

**Feature complete != release quality.** Depois de fechar sistemas, fazer passes explícitos de Gameplay Feel, Animation Polish, Ball Feel, AI, Camera, Input, Audio, VFX, Lighting, UI, Performance, Networking, Accessibility e Bug Fixing.

---

# 41. CONTRATO OPERACIONAL PARA CODEX/IA

## 41.1 Não recomeçar

Nunca refazer controller, XNumber, Animation Recovery, Player Ecosystem ou Visual Registry só porque uma sessão perdeu contexto. Primeiro localizar artefatos, hashes, commits e checkpoints.

## 41.2 Fonte de verdade

- frozen sources read-only;
- manifests/provenance;
- code + tests;
- `_CHECKPOINTS/CURRENT.md`;
- evidence append-only;
- commits duráveis antes de handoff.

## 41.3 CONFIRMED / INFERRED / UNKNOWN

Cada conclusão técnica nova deve usar uma dessas classificações. Nomes semânticos definitivos só depois de prova.

## 41.4 Evidência antes de afirmação

Se 120 FPS não foi medido, não dizer 120.  
Se multiplayer está instável, não dizer final.  
Se Animation import ainda não foi testado no Unreal, não chamar “Unreal-ready” como validação runtime.  
Se um parser só foi validado estruturalmente, não chamar semântica de gameplay de fechada.

## 41.5 Autonomia

O agente deve avançar de forma profissional sem perguntar “quer que eu continue?” em cada etapa. Parar somente diante de blocker externo real ou decisão de produto irreversível que exija o proprietário.

## 41.6 Papel do proprietário

- aprovar/rejeitar visual;
- avaliar gameplay/câmera/feeling;
- fornecer asset/licença quando necessário;
- testar builds importantes;
- decidir direção de produto.

Não transformá-lo em programador principal.

---

# 42. RISCOS, DÍVIDAS E UNKNOWN ATUAIS

- workspace histórico 92/92 foi recuperado em partes em Downloads, mas ainda precisa ser remontado e revalidado;
- cópias 1-221-5 em Downloads/Videos ainda precisam de matriz/deduplicação por SHA-256;
- `spmoveInUseData` ainda não está fechado de ponta a ponta;
- `calSpmoveInUse` precisa de tradução/referência executável suficiente;
- level selection / unidades / equações finais de alguns modifiers ainda UNKNOWN;
- `BALL_CONTACT.velocity` não deve ser promovido com hipótese;
- Physics v0.3 bloqueado;
- Unreal real ainda precisa de build/import/runtime validation após engine ficar disponível;
- Motion Matching database final ainda precisa ser produzido/importado;
- 11v11 visual/performance real ainda não medido;
- networking real ainda não executado sob matriz de latência/perda;
- Career Universe e Competition Engine possuem especificação forte, mas implementação final precisa de evidência runtime/testes atuais;
- backend final pode evoluir; manter interface desacoplada;
- direitos de jogadores/clubes/marcas precisam de tratamento para distribuição pública/comercial;
- conteúdo Neymar hero está pausado e não pode bloquear o jogo.

---

# 43. FASE FUTURA: COMPARAÇÃO COM 1-226-19

A `football-dream-be-a-pro-1-226-19` é a versão mais recente do jogo mobile do proprietário, porém **não faz parte da execução atual**.

A fase oficial de 1-226-19 só começa depois de:

- recovery 1-221-5 organizado e rastreável;
- Physics v0.3 fechado;
- animação/physics normalizadas;
- base 1-221-5 integrada e jogável na Unreal;
- principais sistemas da versão de PC estabilizados o suficiente para medir diferenças.

Aí sim:

1. criar provenance/source matrix separada para 1-226-19;
2. extrair binários/configs/assets em árvore isolada;
3. comparar método por método e tabela por tabela;
4. identificar mecânicas novas ou melhoradas;
5. classificar cada mudança: feature, bugfix, tuning, content, performance ou breaking behavior;
6. criar testes diferenciais;
7. manter baseline 1-221-5 congelado para comparação;
8. portar seletivamente apenas melhorias que beneficiem o jogo PC;
9. documentar toda divergência deliberada.

Áreas de comparação futura:

- física de chute/passe/bola;
- dribble/first touch;
- goalkeeper;
- collision/contact;
- animation/controller/COFMotion;
- IA/táticas/posicionamento;
- formations;
- match rules;
- configs/tuning;
- player ecosystem/visuals;
- performance-related data.

Qualquer inspeção incidental anterior do arquivo 1-226-19 deve permanecer como provenance separada e não ser consumida no baseline atual.


# 44. DIREITOS, PROVENIÊNCIA E DISTRIBUIÇÃO

Os materiais técnicos do jogo original e assets fornecidos pelo proprietário são tratados como fonte autorizada do projeto. Ainda assim, uma distribuição pública/comercial precisa separar direitos técnicos do projeto de direitos de terceiros sobre:

- likeness de atletas;
- clubes;
- ligas/competições;
- uniformes;
- emblemas;
- sponsors;
- marcas esportivas;
- música/comentário;
- fotografias e materiais licenciados.

Neymar/PSG/Nike/UEFA e equivalentes são exemplos de conteúdo que pode exigir clearance. O checkpoint técnico pode existir sem significar licença de distribuição.

---

# 45. APÊNDICE A — AUDITORIA DO MASTER ARCHIVE v1.1

O Master Archive v1.1 histórico continha 56 entradas principais e foi aberto recursivamente junto com 6 ZIPs internos; auditoria anterior contabilizou 173 arquivos entre níveis, 3 DOCX e 18 JSON, além de C# histórico e conteúdo visual/3D.

Integridade reportada:

- 55/55 entradas principais de manifest conferidas;
- 54/54 Neymar checkpoint;
- 11/11 runtime package.

Limitações registradas:

- recovery packs mobile citados em handoffs não estavam fisicamente dentro desse archive;
- Neymar v1.1–v1.8 eram referenciados historicamente, mas o archive atual carregava v1.9;
- GLB v1.9 tem rig/face technical exercises, não set completo de animação de futebol;
- alguns OBJ LOD de chuteiras referenciavam MTL ausente;
- “Unity Ready” era convenção histórica e não equivale a validação Unreal atual.

---

# 46. APÊNDICE B — HISTÓRICO DE HASHES NEYMAR

- v1.2: `7d52f5fa14dd75d9f86e5e32b5a3aea1ad3e6cb2aeacdace2e6fa3bde0f968be`
- v1.3: `a26e83a58163cdd1f389448d8df969a148ec9a47d1fa54cd8bed82fee64f1f56`
- v1.4: `c7e7761e318e92e3d5f9f1f851ad568d6a5d401dd764e475ef4eb8f5deba7490`
- v1.6: `2eac9b84eee99746913acfc98aee1a537c6e05751f8e15a796e6e5c7fc1712cf`
- v1.7: `7754a0001058fb9d3c057f01c2cbb8a623e20676c0ee9c0df08ca0e9630baf99`
- v1.8: `0e84aeb62f0278937fef2070239d9a28c55822e6a5472e1adb2d565d6d1eda68`
- clean v1.1: `2a55940de20f5a3f4f72fe443adb35ce436ca10d4a4bc0a9c03860a1a66c3`

Esses hashes servem apenas como rastreabilidade histórica; o v1.9 é o checkpoint atual preservado.

---

# 47. APÊNDICE C — GLOSSÁRIO OPERACIONAL

**BALL_CONTACT** — evento semântico de contato que alimenta a simulação da bola.  
**CareerPlayer** — jogador persistente de carreira, distinto de card instance.  
**COFMotion** — formato/dado de movimento recuperado do mobile.  
**Competition Engine** — motor parametrizado de ligas/grupos/knockouts/qualificação.  
**CONFIRMED** — sustentado por evidência.  
**Engine-independent** — domínio testável sem depender do renderer/editor.  
**Fixed-point / XNumber** — matemática com ONE=1024 preservada como referência.  
**Golden behavior** — comportamento recuperado usado como referência diferencial.  
**MatchPlayerSnapshot** — projeção imutável da identidade/atributos de partida.  
**Motion Matching** — seleção de animação/pose; não autoridade física.  
**OWN_PLAYER_ONLY** — controle exclusivo do CareerPlayer do humano.  
**PLAYER_CAREER_TEAM_CONTROL** — carreira com CareerPlayer próprio e controle ampliado do time.  
**Provenance** — vínculo explícito de um dado com fonte/hash/build/caminho.  
**Server-authoritative** — estado crítico decidido pelo servidor.  
**SPMOVE** — flags/configs contextuais de ações especiais usadas na cadeia de chute.  
**Visual Registry** — resolução estável de IDs lógicos para assets visuais.  

---

# 48. APÊNDICE D — CHECKLIST DE RETOMADA DE UMA NOVA SESSÃO DE IA

1. Ler esta Bíblia e depois `_CHECKPOINTS/CURRENT.md` + `EVIDENCE.md` + commits recentes.
2. Confirmar branch/HEAD/dirty tree antes de editar.
3. **Não** usar Documents/Desktop/Temp/OneDrive para descobrir novas fontes nesta fase.
4. Usar fontes locais somente em `C:\Users\dg71\Downloads` e `C:\Users\dg71\Videos`.
5. Em Downloads, procurar primeiro o 92/92 recuperado em partes + montador.
6. Montar em diretório separado; preservar partes originais.
7. Rodar e registrar a suíte original 92/92 antes de continuar física.
8. Auditar `Videos\\football-dream-be-a-pro-1-221-5` e criar matriz/dedup de cópias 1-221-5.
9. Não usar 1-226-19 nesta fase.
10. Rodar testes atuais antes de qualquer edição funcional.
11. Não refazer baselines GREEN.
12. Se mexer em recovery, preservar raw + normalized + tests + provenance.
13. Se mexer em Unreal, core em C++ e Blueprint complementar.
14. Se criar tuning novo, marcar `NewGameAuthored`, nunca “Recovered”.
15. Atualizar checkpoint ao final de cada incremento.
16. Fazer commit durável antes de handoff/limite de sessão.
17. Nunca declarar release sem build/test/runtime evidence.
18. Nunca declarar 120 FPS sem captura de partida real.


# 49. APÊNDICE E — FONTES CONSOLIDADAS NESTA BÍBLIA

A consolidação combina fontes de naturezas diferentes. A IA deve sempre distinguir **documentação de produto**, **evidência de recovery**, **pacote derivado**, **log moderno** e **correção posterior do proprietário**.

Principais famílias consultadas:

- contexto/memória consolidada do projeto “converter meu jogo mobile para pc”;
- conversas/handoffs “Extrair APK com Apktool”;
- “Enviar pacote xplayable”;
- “Continuar engenharia reversa”;
- logs atuais do Codex em `Texto colado.txt`;
- `CONVERTER_MEU_JOGO_MOBILE_PARA_PC_MASTER_CONTEXT_2026-09-11.md`;
- `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11` e documentos internos;
- `MEGA_PROMPT_CODEX_GPT6_ASTRA_FOOTBALL_UNIFIED_v4_0.md` como histórico superseded na escolha de engine;
- documentação Unreal v1.2 / ADR / Mega Prompt v5 criados no workspace moderno;
- Migration Master, PC 3D Ready, Player Ecosystem, Visual Registry, Animation Recovery e Physics Recovery;
- Neymar conversion plan/checklists e v1.9;
- reconstrução baseada em evidência do checkpoint 92/92;
- correções mais recentes do proprietário sobre Downloads/Videos, cópias 1-221-5, recuperação do 92/92 em partes e adiamento da 1-226-19.

## 49.1 Regra de conflito

Se esta Bíblia divergir de documento antigo que declare Unity 6 como runtime final, a correção Unreal prevalece.

Se esta Bíblia declarar um estado técnico diferente de um teste/hash/manifest atual, a **evidência executável atual** prevalece e a Bíblia deve ser atualizada.

Se um log antigo tratar uma cópia de arquivo como “fonte canônica”, mas a matriz nova provar duplicatas/variantes, a matriz de hashes prevalece.

## 49.2 Fontes locais operacionais atuais

Para a próxima rodada do Codex:

```text
C:\Users\dg71\Downloads
C:\Users\dg71\Videos
```

Essas são as únicas áreas de descoberta de novas fontes nesta fase. O repositório de desenvolvimento pode permanecer no local atual.



# 49A. APÊNDICE F — MATRIZ DE MECÂNICAS E RESPONSABILIDADES

Esta matriz funciona como índice mental para a IA não implementar a mecânica no lugar errado.

- **Movimento** — autoridade: FootballSimulation/Player; recovery: ActionSpeed, ActionFit, tuning; apresentação: Character + Animation Blueprint.
- **First touch** — autoridade: FootballGameplay/Ball; recovery: action/contact data; apresentação: Animation + IK.
- **Pass** — autoridade: FootballGameplay/Ball; recovery: pass speed e GetKickVelocity quando aplicável; apresentação: clip + ball presentation.
- **Through pass** — autoridade: Gameplay/Tactics; recovery: pass/action/context; apresentação: animation.
- **Cross** — autoridade: Gameplay/Ball; recovery: shot/pass context; apresentação: animation.
- **Shot** — autoridade: Gameplay/Ball; recovery: ShootSpeed, GetVHor/GetVVer, spmove; apresentação: animation/contact marker.
- **Dribble** — autoridade: Gameplay/Ball; recovery: dribble speed/kick/areas; apresentação: Motion Matching.
- **Skill moves** — autoridade: Gameplay + Ball; recovery/autoria: action rules; apresentação: Animation BP/Control Rig.
- **Tackle** — autoridade: Gameplay/Rules; recovery: collision/tackle/intercept; apresentação: contact animation.
- **Foul/Card** — autoridade: Rules/Referee; dados: contact timing/force/rule state; apresentação: UI/referee.
- **Goalkeeper** — autoridade: Goalkeeper + Ball; recovery: GK tables/GetkHor/GetkVer; apresentação: GK animations.
- **Offside** — autoridade: Rules; dados: pass moment + positions; apresentação: overlay/UI.
- **Goal** — autoridade: Match/Rules; dados: ball crossing + rule validation; apresentação: net/VFX/UI.
- **Substitution** — autoridade: Match/Career; dados: lineup/fitness/manager decision; apresentação: UI/entrance.
- **Career transfer** — autoridade: Career Universe; dados: contract/registration/transfer state; apresentação: UI only.
- **Competition bracket** — autoridade: Competition Engine; dados: deterministic stage state; apresentação: UI projection.
- **Human ownership** — autoridade: Networking/CareerCoop; dado: stable HumanOwnerId; apresentação: controller mapping.

# 49B. APÊNDICE G — REGISTRO DE DECISÕES DE PRODUTO FECHADAS

- Plataforma inicial: Windows PC.
- Engine final: Unreal Engine 5.x.
- Linguagem/core: C++ modular.
- Blueprint: complementar, não arquitetura central.
- 3D source of truth: Blender.
- Desenvolvimento: AI-first; usuário não deve fazer programação repetitiva/manual.
- Referência de input: gamepad; teclado/mouse também suportados.
- Estilo: simulação realista, porém responsiva/controlável.
- Modos obrigatórios: Training, 3v3, 5v5, 11v11, Player Career, Career 5v5/11v11, co-op Career, online.
- Políticas de Player Career: `OWN_PLAYER_ONLY` e `PLAYER_CAREER_TEAM_CONTROL`.
- Co-op Career: cada humano possui seu próprio CareerPlayer; reunião no mesmo clube acontece por contratos/transferências válidos.
- Alterações de política que afetam humanos: unanimidade quando definido pelo modo.
- Career 5v5 é first-class, não minigame.
- Football Simulation deve ser compartilhada por partidas normais, carreira e online.
- Competition Engine compartilhada e parametrizada por formato.
- Multiplayer: Dedicated Server, server-authoritative.
- Ball physics: bola independente; animation não manda na física.
- Animation: Pose Search/Motion Matching + Animation BP + IK/Control Rig.
- Neymar: v1.9 preservado, trabalho específico pausado.
- Physics v0.3: proibido antes do gate spmove/velocity/BALL_CONTACT/regressão.
- Build mobile atual: 1-221-5.
- Build 1-226-19: somente fase futura de comparação/melhoria.
- Meta performance: 120 FPS medidos em partida real no hardware de referência.
- Vertical slice/3v3/5v5/11v11 isolado: checkpoints, não produto final.

# 49C. APÊNDICE H — QUICKSTART PARA CODEX/IA

Ao iniciar uma nova sessão, a IA deve assumir:

```text
PRODUTO: jogo de futebol realista para Windows PC
ENGINE: Unreal Engine 5.x
CORE: C++ modular
3D: Blender
MODELO DE TRABALHO: AI-first
BUILD MOBILE ATUAL: football-dream-be-a-pro-1-221-5
FONTES LOCAIS NOVAS: Downloads + Videos somente
92/92: recuperado em partes em Downloads; montar/validar primeiro
NEXT PHYSICS: spmoveInUseData
NEYMAR: pausado
1-226-19: futura; não usar
FINAL TARGET: jogo completo, não protótipo
```

Primeiras ações:

```text
1. git status / branch / HEAD
2. ler checkpoints
3. inspecionar Downloads: 92/92 parts + assembler
4. remontar e rodar 92/92
5. auditar Videos/1-221-5 e dedup hashes
6. retomar spmove
7. em paralelo validar Unreal real quando instalado
8. checkpoint + commit antes de qualquer limite
```

# 49D. APÊNDICE I — PROTOCOLO DE ALTERAÇÃO DA BÍBLIA

Este documento deve evoluir como um artefato versionado. Uma alteração deve indicar:

- data;
- decisão/fato alterado;
- origem da mudança;
- impacto arquitetural;
- hashes/testes se técnicos;
- itens superseded.

Nunca apagar silenciosamente uma decisão histórica importante. Marcar como superseded quando necessário. O objetivo é permitir que outra IA reconstrua a evolução do projeto sem depender de memória implícita.

# 50. DECLARAÇÃO FINAL DO PROJETO

O projeto é um **novo jogo de futebol realista para Windows PC**, construído em **Unreal Engine 5.x + C++**, com **Blender** como source of truth 3D e um modelo de desenvolvimento **AI-first**.

Ele reaproveita o que foi tecnicamente recuperado do jogo mobile — física, animação, controller, COFMotion, gameplay data, IA/configs, formações, jogadores, visuais e tuning — mas converte tudo para contratos engine-independent e então para um runtime moderno Unreal.

O produto final deve entregar excelente gameplay, carreira persistente 5v5/11v11, co-op de carreira com ownership individual, competições reais, IA em múltiplas camadas, player/card ecosystem, multiplayer server-authoritative, UI de PC, saves, conteúdo, áudio/VFX, acessibilidade e desempenho medido.

O Neymar está pausado. A prioridade é **terminar o jogo**.

A build mobile 1-221-5 é o baseline canônico atual, com múltiplas cópias a serem organizadas por hash em Downloads/Videos. O workspace histórico 92/92 recuperado em partes deve ser remontado e revalidado antes de novo retrabalho. A 1-226-19 será estudada apenas numa fase futura, separada, para encontrar melhorias seletivas.

A Physics v0.3 não deve ser fabricada antes do gate nativo fechar. A Unreal não deve receber comportamento “recuperado” que na verdade foi inventado.

E a regra final de execução é simples:

> **Preserve o que está provado. Termine o que está incompleto. Integre cedo. Teste de verdade. Meça. Melhore conscientemente. Não recomece. Não masque blockers. Não pare no protótipo. Entregue o jogo.**
