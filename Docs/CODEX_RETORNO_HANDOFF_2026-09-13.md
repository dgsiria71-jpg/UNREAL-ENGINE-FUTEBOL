# HANDOFF COMPLETO PARA RETORNO DO CODEX — 2026-09-13

> Projeto: **converter meu jogo mobile para PC / UNREAL-ENGINE-FUTEBOL**  
> Repositório oficial: `dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL`  
> Branch oficial: `main`  
> Engine-alvo: **Unreal Engine 5.x**  
> Gameplay/simulação: **C++ primário; Blueprint complementar**  
> Fonte 3D: **Blender**  
> Build mobile canônica de recuperação: **football-dream-be-a-pro 1-221-5**  
> Build **1-226-19 permanece isolada e NÃO deve ser consumida** sem comparação/aprovação explícita.

Este documento existe para o Codex retomar exatamente do ponto atual depois do período em que ficou fora do fluxo. **Não reiniciar arquitetura, não refazer decisões fechadas e não substituir evidência atual por documentação histórica.**

---

## 1. Regra de fonte da verdade

Durante este período consolidamos a política do projeto:

- GitHub `main` é a fonte oficial de verdade do projeto.
- Mudança relevante deve seguir o fluxo: implementação → testes/evidência → checkpoint → commit/push → `main`.
- Binários e arquivos grandes de recuperação são preservados via **Git LFS**.
- Código, JSON, traces, disassembly e documentação textual ficam em Git normal para poderem ser lidos/analisados diretamente.
- Arquivos locais dentro de `.local/` são fonte/regeneração local e **não devem ser apagados, resetados ou publicados em massa**.
- O histórico “92/92 GREEN” permanece apenas como histórico documentado; os bytes do workspace histórico 92/92 **não foram provados como recuperados byte-for-byte**. Não fabricar esse estado a partir dos testes atuais.

---

## 2. Estado herdado do Codex antes desse período

A base de física estável continua sendo:

- `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip`
- SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`
- suíte original v0.2: **67/67 GREEN**
- tabelas-fonte: **83/83 byte-exact**

O trabalho nativo já havia confirmado:

- seleção `spmove`: **4.672/4.672** comparações nativas ARM64 sem divergência;
- produtor `spmove`: **2.640/2.640** comparações nativas sem divergência;
- collector open-all: **292 configs serializadas**, **290 enabled**, **2 disabled**, **56 child refs**, **68 logic buckets**, **346 entradas**, zero child-config ausente;
- prioridade de seleção: maior child ID assinado, não `level/order/odds`;
- desempate com father positivo;
- `noRatio` usa apenas o low bit;
- ausência do config vencedor não faz fallback;
- dicionário de runtime filtra configs disabled por `enable +0x1C`;
- `SpmoveIDCombine`: childId `+0x10`, fatherId `+0x14`.

Também já estava estabelecido que a física v0.3 **não poderia ser criada** antes de fechar a cadeia real:

`spmove → GetVHor/GetVVer → GetKickVelocity → BALL_CONTACT.velocity → regressão completa`.

---

## 3. Portabilidade do repositório foi reparada

O primeiro problema importante encontrado foi que o `main` não validava corretamente em checkout novo do GitHub Actions porque parte dos testes dependia de artefatos gerados apenas localmente.

Foi criado o reparo de portabilidade para separar:

- evidência persistida/commitada que precisa existir em checkout limpo;
- artefatos completos que podem continuar sendo regenerados a partir dos arquivos locais preservados.

O PR de reparo foi integrado e o CI confirmou fresh checkout funcional.

Resultado importante: o repositório pode ser validado em runner limpo sem fingir que arquivos locais ausentes estão commitados.

---

## 4. Master Recovery foi consolidado e publicado via Git LFS

O grande master consolidado continua identificado como:

`FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

- tamanho: **794.639.566 bytes**
- SHA-256: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`
- 62 entradas
- CRC validado

Ele foi publicado no GitHub via LFS em:

`artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

Commit de publicação registrado no checkpoint:

`c58cd352fa79bb791a9b8d4d6bff88a098cdbc20`

Importante: esse master é uma **consolidação de fontes recuperadas**. Ele **não** contém/prova o workspace histórico original 92/92.

---

## 5. Infraestrutura de upload para GitHub foi criada e endurecida

Foi criado um fluxo genérico para mandar arquivos do PC ao repositório sem depender do chat:

- `tools/PUBLICAR_INBOX_NO_GITHUB.ps1`
- `tools/PUBLICAR_INBOX_NO_GITHUB.bat`
- uploader específico do master também permanece disponível.

O uploader genérico:

- preserva o arquivo original local;
- calcula SHA-256 e tamanho;
- cria upload ID;
- publica artefato em árvore canônica;
- escreve manifesto em `manifests/uploads/<upload-id>.json`;
- usa Git LFS para extensões binárias conhecidas;
- aborta arquivo grande sem atributo LFS;
- bloqueia nomes óbvios de segredo/credential/private key;
- faz clone limpo, commit, rebase/fetch se necessário e push sem force;
- verifica commit remoto;
- para LFS, verifica pointer remoto/oid/tamanho.

Também corrigimos um problema real de autenticação local: o Git Credential Manager estava usando a conta `dgrich33`, causando `403` no repositório. Os wrappers passaram a solicitar `credential.username=dgsiria71-jpg` no processo. Isso não altera permanentemente todas as credenciais do PC.

---

## 6. Auditoria das fontes e ZIPs locais

Foi investigada a suspeita de que o Codex não estava aproveitando todos os ZIPs disponíveis. A suspeita tinha fundamento parcial.

O script antigo de catálogo de arquivos era **deliberadamente limitado**: ele olhava principalmente arquivos de topo em `Downloads` cujo nome casava com padrões `FOOTBALL/FUTEBOL/football-dream` e ZIP/XAPK. Portanto:

- catalogar não significava consumir;
- subpastas podiam ficar fora;
- nomes genéricos podiam ficar fora;
- `.7z/.rar` e outras árvores podiam ficar fora;
- uma cópia nova de um arquivo histórico podia existir em outro ponto do PC sem ser reconhecida por aquele catálogo.

A auditoria da build 1-221-5 registrou **122 observações críticas/de arquivo** e **22 grupos de cópias idênticas**, mas explicitamente não declarou ter inspecionado todo arquivo existente em todo o PC.

Também foram publicados materiais de auditoria/delta em `artifacts/audits/` e `artifacts/package-deltas/`, mostrando que vários pacotes históricos são complementares em vez de simplesmente “versão nova substitui versão antiga”. As duas cópias de `FUTEBOL_AI_MASTER_ARCHIVE_v1_1_2026-09-11` encontradas na auditoria são duplicatas exatas de arquivo.

A regra continua: **não misturar automaticamente builds**. A build 1-221-5 segue canônica; 1-226-19 continua excluída.

---

## 7. Mapa de origem mobile 1-221-5 consolidado

A build canônica continua confirmada como Unity + IL2CPP e inclui, entre outros:

- `libil2cpp.so`, `libunity.so`, `libmain.so` ARM64/ARM32;
- `global-metadata.dat`;
- `data.unity3d` / datapack;
- PDBs de `Assembly-CSharp`, `Assembly-CSharp-firstpass`, `MagicaCloth` e Unity;
- `assets/config/match/` com tabelas de movimento, chute, passe, colisão, drible, tackle, interceptação, goleiro etc.;
- `assets/LocalSettings/*.json` com configurações como `AIParameterConfig`, `FootballConfig`, `ShootConfig`, `PassBallConfig`, `GoalKeeperConfig`, `CollisionConfig`, `DribbleConfig`, `PhysicalPowerConfig` etc.;
- `assets/xplayable/`, `nova_player`, `fbxs`, `prefabs` e Lua services.

A cadeia conceitual de gameplay preservada continua:

`input → estado do jogador → movimento/rotação/aceleração → controller/AI → seleção de ação → passe/chute/drible/tackle → animação → skeleton/IK → contato/colisão → física da bola → resultado`.

---

## 8. Disassembly canônico de chute foi levado ao GitHub

O antigo `disassembly_shoot.txt`, que antes existia apenas em `.local`, foi publicado como evidência textual normal Git:

`artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`

- SHA Windows original: `ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58`
- SHA após normalização LF no Git: `c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4`

Com isso, a investigação de GetVHor/GetVVer deixou de depender apenas do workspace local do Codex.

Foram adicionados:

- `Tools/analyze_shoot_velocity_dataflow.py`
- `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
- `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`

---

## 9. Avanço real em GetVHor

Função recuperada/analisada:

`0x016E6A80 .. 0x016E84A4`

Foi confirmado o split old/new pelo `ShootSpeedConfigItem.useNewMethod` em `+0x90`:

- zero → caminho legacy;
- não-zero → caminho novo map-driven.

Famílias antigas:

- `Flist_vHor`
- `vHorList`
- `speed_vHor`

Famílias novas:

- `energyMapNew`
- `vHorMapNew`
- `shootStrongMapNew`
- `vHorRateNew`

Correção importante descoberta enquanto o Codex estava fora:

Os rewrites vetoriais pré-base de `spmove` `0x3FE/0x3FC`, antes considerados parte do resultado horizontal, **são sobrescritos pelo construtor normal compartilhado em `0x016E79D4/0x016E79D8`**. Portanto, no caminho normal de retorno de GetVHor, eles **não sobrevivem como contribuição de valor ao vetor final**.

Isso não significa que as chamadas possam ser removidas: ainda podem ter exceções/efeitos colaterais. A conclusão é apenas sobre o valor final normal.

O vetor-base sobrevivente usa fixed-point com bias `+512`, shift `>>10` e forma:

`XVector3(x = dir0 * speed, y = 0, z = dir1 * speed)`.

---

## 10. Avanço real em GetVVer

Função:

`0x016E84A4 .. 0x016EA55C`

O caminho novo agora está estruturalmente ligado por:

`shootDisMap → outEnergyMaxMap → energyMapNew/ySpeedMax → shootPointHUpMap → shootPointHDownMap → shootPropertyMapNew/energyToleranceMap → energyNeedProtect → clamp shootPointH → shootDisAndTime → ySpeedMin → vetor-base`.

Callsites de interpolação/remap importantes foram ligados em:

- `0x016E8804`
- `0x016E89F4`
- `0x016E8BC8`
- `0x016E8DA4`
- `0x016E8FA8`

Os modifiers pós-vetor do caminho novo `0x3FC` e `0x41A` **sobrevivem** até o retorno normal.

No caminho antigo foram ligados:

- `Flist_vVer`
- `vVerList`
- interpolação-base em `0x016EA188`
- `speed_vVer +0x80`
- chamada externa `0x1968E24`
- modifier pós-vetor `0x3FB`, que também sobrevive.

O retorno compartilhado de GetVVer está em:

`0x016EA52C .. 0x016EA554`

ABI do `XVector3`:

- `x0`: low32 = x, high32 = y
- `w1`: z

A equação completa de GetVVer **ainda não está fechada**.

---

## 11. GetKickVelocity: composição final estática fechada

Função:

`0x016EBAD8 .. 0x016EBF14`

Foi confirmado que:

- chama GetVHor em `0x016EBBA8`;
- pós-processa o horizontal;
- chama GetVVer em `0x016EBEAC`;
- `0x016EBED8 .. 0x016EBF04` faz a soma/composição componente a componente de **GetVHor ajustado + GetVVer** e repack do `XVector3`.

Isso fecha a **forma estática do join final**, não o comportamento runtime completo de GetKickVelocity.

---

## 12. Ferramenta one-click para extrair os helpers de chute

Como faltavam corpos auxiliares importantes, foi criada uma ferramenta segura de extração local:

- `Tools/disassemble_shoot_helpers.py`
- `tools/EXTRAIR_HELPERS_SHOOT.bat`

Ela:

- lê `.local/il2cpp/libil2cpp.so` em modo de análise;
- valida ELF 64-bit little-endian AArch64;
- usa `script.json` do Il2CppDumper quando disponível;
- usa apenas `ScriptMethod` para afirmar boundary exata;
- para endereço sem boundary confiável usa janela limitada e marca `exact=false`;
- também coleta first-level `bl` targets dentro dos blocos primários;
- não executa nem modifica o binário mobile;
- grava o resultado em área local separada de output;
- publica pelo uploader genérico.

Alvos primários:

- `0x126BF1C`
- `0x1968E24`
- `0x196807C`

Esse pipeline passou por várias etapas RED → GREEN, incluindo correção de `%ERRORLEVEL%` no BAT e correção de falsa boundary causada por metadata genérica que não era `ScriptMethod`.

---

## 13. Helper disassembly foi finalmente publicado pelo usuário

Upload:

- Upload ID: `20260913-175551-3fafba6a`
- destino: `artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a`
- manifesto: `manifests/uploads/20260913-175551-3fafba6a.json`
- arquivo: `01_shoot_helper_disassembly.txt`
- tamanho: **184.617 bytes**
- SHA-256: `284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58`
- `libil2cpp.so` ARM64 de origem registrado pelo extractor: `2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496`

Essa foi a evidência que desbloqueou o próximo incremento sem precisar pedir novo ZIP grande.

---

## 14. Semântica do helper `0x126BF1C` recuperada

Foi criado:

- `Tools/analyze_shoot_helper_semantics.py`
- `Recovery/Normalized/shoot_helper_semantics_static_trace.json`
- `Recovery/Physics/SHOOT_HELPER_SEMANTICS.md`

A janela de `0x126BF1C` permanece corretamente marcada `exact=false` porque não há boundary `ScriptMethod` confiável para o endereço, mas o caminho normal termina em `0x0126C074` e uma nova prologue independente começa em `0x0126C078`.

Semântica normal recuperada:

- argumentos `x0..x4` correspondem a `(input, in_min, in_max, out_min, out_max)`;
- se `in_min == in_max`, retorna `out_min` diretamente;
- input é clamped na ordem de comparação nativa;
- ratio é fixed-point 10-bit;
- `n = (bounded - in_min) * 1024`;
- `d = in_max - in_min`;
- `q = trunc(n/d)`;
- `r = n - q*d`;
- `ratio = q + trunc(2*r/d)`;
- numerador zero usa ratio raw zero sem divisão;
- saída segue para `0x126C3FC`.

---

## 15. Semântica do helper `0x126C3FC` recuperada

A janela também é bounded/`exact=false`, mas o retorno normal fecha em `0x0126C534`, seguido de nova prologue em `0x0126C538`.

Forma recuperada:

`out_min + fixed_mul(out_max - out_min, clamp(t, 0, 1024))`

O multiply é o fixed-point já recuperado:

`(a*b + 512) >> 10`

Foi criado o helper executável específico:

`Reference/FootballPhysics/ShootRemap.h`

Decisão importante: **não modificar `Reference/FootballCore/FixedPoint.h`** para encaixar esse comportamento específico.

Quando foi tentada uma alteração exploratória no helper genérico, o novo CTest passou, mas cinco evidências diferenciais antigas corretamente ficaram stale porque estavam vinculadas ao SHA inteiro de `FixedPoint.h`. A mudança foi descartada e `FixedPoint.h` foi restaurado. O comportamento de chute ficou isolado em `ShootRemap.h`.

Isso preserva a proveniência do kernel fixo já validado.

---

## 16. `0x1968E24` foi identificado exatamente

Il2CppDumper fornece boundary exata:

- start `0x01968E24`
- end `0x0196916C`
- nome: `PlayerProperty$$GetShootSpeedVRate`

Cadeia direta de valores identificada:

- `0x01968C34` → `PlayerProperty$$GetShootVerRate`
- `0x01FF58AC` → `XBaseLocalSetting<AIParameterConfig>$$get_Singleton`
- campo observado do singleton `AIParameterConfig` em `+0x80`
- `0x0192A0C4` → `XRandom$$Range`

Caller antigo em GetVVer também foi ligado:

- `0x016EA318`: `ShootSpeedConfigItem +0x80` → `w3`
- `0x016EA31C`: argumento da stack → `w1`
- `0x016EA320`: GetVVer `x20` → `x2`
- `0x016EA324`: `x4 = null`
- `0x016EA330`: call `0x1968E24`

O que **ainda não** foi fechado:

- unidades/semântica de todos os inputs;
- significado e unidade do campo `AIParameterConfig +0x80`;
- equação completa branch-by-branch;
- todos os limites/efeitos de randomização.

Portanto `full_equation_recovered = false` continua correto.

---

## 17. `0x196807C` foi identificado e fechado

Boundary exata:

- `0x0196807C .. 0x0196808C`
- nome: `PlayerProperty$$GetSpmoveDataRatio`

O corpo de quatro instruções:

- carrega manager em `PlayerProperty +0x28`;
- mascara low bit do argumento no-ratio;
- zera `x3`;
- tail-call para `0x01B72814`, o caminho já recuperado `SpmoveManager.GetSpmoveDataNoRatio`.

Esse helper deixou de ser uma incógnita do pipeline.

---

## 18. TDD/CI do incremento de helpers

A recuperação de helpers seguiu RED → GREEN de verdade.

Pontos principais:

- `a0693931147de82a4f5d452d4bf9bc49c5ba4621`: RED — analyzer/persisted evidence ainda ausentes;
- `c0211fb9df40e605d358b473f7bd2bfe37d0f65f`: trace persistido GREEN, Actions `34784114057`;
- `bd9bab264b8fbca8202c9f9e1e742f0d065a98a1`: CTest RED mostrando que o `RemapClamped` genérico não tem o comportamento equal-bound nativo do shoot helper;
- `c3d022de7c2fd728a1fe3b88f7875bceabc44cbb`: alteração exploratória genérica fez o teste passar, mas invalidou corretamente cinco bindings de evidência do `FixedPoint.h`; não foi aceita como arquitetura final;
- `e1f3280a923e9633f61e949c5dc07c25f0f02a85`: restauração do `FixedPoint.h` validado;
- `800b3a69a9dd7331c8b5ca8ec5b89370fcaf8d63`: RED isolado porque `ShootRemap.h` ainda não existia;
- `e49a16a4b0e561c60977952bd7e0ed7e2099bba0`: helper específico GREEN, Actions `34784291595`;
- `2be52efc63182592db3f048725ff53d55ea949a9`: trace registrado no recovery manifest, Actions `34784415498` GREEN;
- head da branch de trabalho antes do merge: `68c9e69453f4793f614f05342b9ebf8eb48b1019`, Actions `34784499829` GREEN;
- PR #5 passou CI de pull request, Actions `34784529181` GREEN.

PR integrado:

**#5 — Recover native shoot helper semantics from published ARM64 evidence**

Merge oficial em `main`:

`4a6add06b03306f3fe362437095d12af443fa568`

CI pós-merge do `main`:

- workflow run `34784551208`
- **SUCCESS**

Esse é o estado oficial a partir do qual o Codex deve continuar.

---

## 19. Arquivos canônicos novos/atualizados que o Codex deve ler

Começar por estes, nesta ordem:

1. `_CHECKPOINTS/CURRENT.md`
2. `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`
3. `Recovery/Physics/SHOOT_HELPER_SEMANTICS.md`
4. `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json`
5. `Recovery/Normalized/shoot_helper_semantics_static_trace.json`
6. `Recovery/Normalized/recovery_manifest.json`
7. `Reference/FootballPhysics/ShootRemap.h`
8. `Tools/analyze_shoot_velocity_dataflow.py`
9. `Tools/analyze_shoot_helper_semantics.py`
10. `artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt`
11. `artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt`

Não voltar para versões antigas desses documentos se a evidência binária/trace atual discordar.

---

## 20. Gate atual da Physics v0.3

**Physics v0.3 continua BLOQUEADA.**

Não criar `FOOTBALL_PHYSICS_RECOVERY_PACK_v0_3.zip` ainda.

Falta fechar, em ordem prática:

1. `shootDisAndTime` — aritmética/tempo aninhada do caminho novo de GetVVer;
2. `GetShootSpeedVRate` — completar a equação/unidades ou provar exatamente o resultado caller-visible de que GetVVer precisa;
3. transformar GetVHor/GetVVer em comportamento executável source-bound completo e validar contra evidência original/nativa;
4. fechar o comportamento final de GetKickVelocity além do join estático já recuperado;
5. ligar o resultado resolvido a `BALL_CONTACT.velocity`;
6. remover placeholder/fallback unresolved (`ball_impulse=None` ou equivalente ainda bloqueado pelo contrato);
7. rodar regressão completa;
8. somente depois empacotar Physics v0.3.

O contrato de `BallContact` deve continuar conservador: sem velocidade recuperada e sem semântica completa, não mover a bola como se o comportamento original estivesse fechado.

---

## 21. Unreal / jogo jogável: estado real

Ainda não houve nesta linha de recuperação:

- build completa do projeto no Unreal no ambiente do Codex;
- execução/render de partida real no Unreal;
- medição de FPS/performance em jogo Unreal;
- validação visual final dos assets importados.

Portanto não declarar que o jogo/physics já está “pronto no Unreal”.

A base C++ headless e os artefatos recuperados estão avançados, mas a integração Unreal completa continua etapa posterior.

---

## 22. Cobertura funcional ainda parcial

Estado conservador atual:

- fixed-point math / vector native differential: forte/validado nos kernels já cobertos;
- seleção/producer `spmove`: validado nos casos preservados;
- chute / velocidade final: parcial, ainda bloqueado;
- animações: grande volume recuperado/catalogado, runtime completo ainda não reconstruído;
- colisão/tackle/interceptação/GK: fontes/tabelas existem, comportamento original completo ainda não fechado;
- passe/chute/drible/defesa: comportamento headless parcial;
- assets 3D: recuperação/export parcial, sem validação final de import Unreal;
- AI: configs/fontes existentes, comportamento completo ainda não reconstruído;
- câmeras: incompleto;
- modos de partida: existe estrutura/headless, não equivale a produto final UE validado.

ZIP presente prova preservação, não integração. Parser/catalog prova leitura estrutural, não execução original reproduzida.

---

## 23. Cuidados de continuidade

O Codex NÃO deve:

- reiniciar o projeto;
- escolher outra engine;
- trocar `main` como fonte oficial;
- consumir build `1-226-19` silenciosamente;
- alterar `FixedPoint.h` sem regenerar os relatórios nativos SHA-bound que dependem dele;
- apagar `.local`;
- descartar arquivos só porque parecem duplicados sem comparar hash;
- considerar master recovery equivalente ao histórico 92/92;
- declarar GetVVer/GetKickVelocity/BALL_CONTACT completos antes da validação;
- criar Physics v0.3 antecipadamente;
- apagar/normalizar cegamente as colisões de caixa `Docs/docs` ou `Tools/tools` no Windows.

Existem avisos de case-collision no checkout Windows para algumas árvores com nomes que diferem apenas por caixa. Isso é um problema de portabilidade separado e deve ser normalizado com plano próprio, nunca por deleção automática.

---

## 24. Comandos seguros de retorno do Codex

Antes de trabalhar:

```powershell
git status --short
git switch main
git fetch origin
git pull --ff-only origin main
git log -1 --oneline
```

O Codex deve confirmar que está em/contém o merge:

`4a6add06b03306f3fe362437095d12af443fa568`

Se houver modificações locais, **não usar `reset --hard` nem stash automático** sem entender o que são.

Depois ler os arquivos do item 19 e continuar diretamente pelo item 20.

---

## 25. Próximo incremento recomendado

O próximo incremento técnico deve continuar a engenharia reversa, sem desviar para Unreal/UI/asset import ainda:

**Track imediato: fechar `shootDisAndTime` e aprofundar `PlayerProperty.GetShootSpeedVRate`.**

Objetivo da próxima rodada:

- descobrir os value-producing callees e campos ainda opacos;
- fechar unidades/branch equations suficientes para o resultado de GetVVer;
- persistir trace source-bound;
- criar testes RED antes da implementação;
- validar GREEN em GitHub Actions;
- só então incorporar ao comportamento executável de GetVVer.

Se o disassembly atual não contiver algum helper de primeiro nível necessário, expandir o extractor de forma bounded e pedir/publicar somente a evidência textual adicional necessária, em vez de mover novamente grandes APKs/ZIPs.

---

## 26. Estado oficial de retorno

**Fonte oficial:** GitHub `main`  
**Merge atual deste ciclo:** `4a6add06b03306f3fe362437095d12af443fa568`  
**CI pós-merge:** Actions `34784551208` — **SUCCESS**  
**Build mobile canônica:** `1-221-5`  
**Build 1-226-19:** isolada/excluída  
**Physics v0.2:** baseline estável preservada  
**Physics v0.3:** **BLOQUEADA — não empacotar ainda**  
**Próximo alvo:** `shootDisAndTime` + `GetShootSpeedVRate` → GetVVer executável/validado → GetKickVelocity → BALL_CONTACT.velocity.

Este documento é um handoff de continuidade. O Codex deve **continuar deste estado**, não reconstruir o raciocínio do zero.