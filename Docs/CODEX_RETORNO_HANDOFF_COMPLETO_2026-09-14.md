# HANDOFF COMPLETO PARA RETORNO DO CODEX — 2026-09-14

> Projeto: **converter meu jogo mobile para PC / UNREAL-ENGINE-FUTEBOL**  
> Repositório oficial: `dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL`  
> Branch oficial: `main`  
> Engine-alvo: **Unreal Engine 5.x**  
> Gameplay/simulação: **C++ primário; Blueprint complementar**  
> Fonte 3D: **Blender**  
> Build mobile canônica: **Football Dream: Be a Pro 1-221-5**  
> Build **1-226-19 permanece isolada / não consumida**.  
> Neymar v1.9 permanece **PAUSED**.

Este documento existe para o Codex retomar exatamente do ponto atual. **Não reiniciar arquitetura, não refazer decisões fechadas e não produzir Physics v0.3 antes dos gates descritos abaixo.**

---

## 1. Estado oficial agora

O estado de engenharia integrado no `main` antes deste documento é:

```text
478bc02c00fa470f1cbca5af366c81a3680695fe
```

PR #13 — `Recover source-bound GetVVer player property selector` — foi integrado como:

```text
c12e61cf21b070f15860346e283c2cb92a9d5bd6
```

Validação:

```text
run #183 / 34802035409 — SUCCESS
checkpoint ed2776863d71da7442502eebb0a91d9cdb3d0d1d
run #184 / 34802089841 — SUCCESS
```

PR #14 — `Extend GetVVer property lookup evidence recovery` — foi integrado no head:

```text
478bc02c00fa470f1cbca5af366c81a3680695fe
```

O head foi provado como fast-forward limpo sobre o `main` anterior (`ahead_by=5`, `behind_by=0`), validado no run #195 / `34802465358` — **SUCCESS**, e depois integrado sem force. O GitHub registrou o PR #14 como `merged=true`, com merge SHA igual a `478bc02...`. O `main` pós-integração passou novamente no run #197 / `34802769409` — **SUCCESS**.

GitHub `main` continua sendo a fonte oficial de verdade.

---

## 2. Regras que continuam valendo

- Build canônica: `1-221-5`.
- `1-226-19` não entra automaticamente.
- C++ continua sendo o core primário no Unreal.
- Blender continua sendo source-of-truth 3D.
- `.local/` contém fontes/evidências de regeneração e deve ser preservado.
- Trabalho relevante segue RED -> GREEN -> CI -> evidência -> integração.
- Não inventar nomes/semântica para offsets ou funções sem metadata/instruções.
- O histórico original `92/92` não está provado byte-for-byte; não afirmar que foi recuperado.
- Não declarar runtime Unreal completo, package Windows, rendered match ou FPS validados: isso ainda não aconteceu.
- Physics v0.3 permanece **BLOCKED**.

---

## 3. Baseline de física preservada

```text
FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip
SHA-256:
7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac
```

Estado:

```text
67/67 testes originais v0.2 GREEN
83/83 tabelas-fonte byte-exact
spmove selection 4672/4672
spmove producer 2640/2640
```

Collector:

```text
292 configs
290 enabled
2 disabled
56 child refs
68 logic buckets
346 inventory entries
```

Semântica spmove já fechada:

- maior child ID assinado vence;
- desempate favorece father positivo;
- `noRatio` usa low bit;
- ausência do config vencedor não faz fallback;
- disabled é filtrado por `enable +0x1C`;
- `SpmoveIDCombine.childId = +0x10`;
- `SpmoveIDCombine.fatherId = +0x14`.

Gate estrutural continua:

```text
spmove
 -> GetVHor / GetVVer
 -> GetKickVelocity
 -> BALL_CONTACT.velocity
 -> regressão completa
 -> Physics v0.3
```

---

## 4. Master recovery e fontes

Master consolidado:

```text
FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip
794,639,566 bytes
SHA-256:
4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2
62 entradas / CRC pass
```

Publicado por Git LFS em:

```text
artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip
```

Commit de publicação conhecido: `c58cd352fa79bb791a9b8d4d6bff88a098cdbc20`.

A auditoria também confirmou que vários pacotes históricos são complementares, não simplesmente “versão nova substitui antiga”. PC3D v0.2 é superset de v0.1 normalizado; Migration v1.1 adiciona conteúdo; Player Systems Reference e Player Ecosystem são complementares; Ecosystem v0.2 não subsume totalmente v0.1.

---

## 5. Evidência canônica de chute

Listing principal:

```text
artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt
```

Hashes:

```text
Windows original:
ef1b41f609e49f2d831a16f69b82e227a967c914a4ee3748cfbfbdccd161ba58

Git LF:
c695472c6bb7820f71c334407c4998149d8f3646bc5f0614d30f3adf80f670c4

libil2cpp.so:
2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496
```

Foram adicionados `Tools/analyze_shoot_velocity_dataflow.py`, `Recovery/Normalized/shoot_velocity_dataflow_static_trace.json` e `Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md`. PR #2 fechou esse incremento; merge conhecido `7c3d89fc50cb0b1f53169549362f16dac23dc2a4`, CI `34780143404` SUCCESS.

---

## 6. GetVHor recuperado até o boundary atual

Range:

```text
0x016E6A80..0x016E84A4
```

Split old/new por `ShootSpeedConfigItem.useNewMethod +0x90`.

Novo caminho usa `energyMapNew +0xB8`, `vHorMapNew +0xC0`, `shootStrongMapNew +0xC8`, `vHorRateNew +0xD0`; remap helper em `0x016E6DE0 -> 0x126BF1C`.

Legacy usa `Flist_vHor +0x18`, `vHorList +0x20`, `speed_vHor +0x74`, clamp `+0x78`.

O construtor final normal usa fixed-point com bias `512`, shift `>>10` e forma:

```text
XVector3(x=dir0*speed, y=0, z=dir1*speed)
```

Correção importante: rewrites pré-base `0x3FE/0x3FC` são sobrescritos pelo construtor compartilhado no retorno normal de GetVHor. Eles não sobrevivem como valor final normal, embora as chamadas ainda possam ter side effects/exceptions e não devem ser removidas apenas por isso.

---

## 7. Helpers de chute

Foi criado o extractor one-click:

```text
Tools/disassemble_shoot_helpers.py
tools/EXTRAIR_HELPERS_SHOOT.bat
```

PR #3 integrado em `857398d928c044c796f673a9ed86aad5cd1a8188`, run `34781624031` SUCCESS.

O output foi depois desacoplado da árvore de input e movido para `.local/recovery-output/shoot_helper_disassembly.txt`. PR #4: `9f0c15f70e902df824a0122747a27b70a79d6fad`, run `34782155349` SUCCESS.

Publicação canônica dos helpers:

```text
Upload ID: 20260913-175551-3fafba6a
artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt
184617 bytes
SHA-256:
284964d94f4544b37612f87e79b5daec41b064d5802be1a4c8a767f37e166d58
```

---

## 8. Remap/lerp fixed-point

`0x126BF1C` tem janela de extração bounded (`exact=false`), mas normal-return arithmetic instruction-bound:

```text
if in_min == in_max: return out_min
bounded = clamp(input, in_min, in_max)
numerator = bounded - in_min
n = numerator * 1024
d = in_max - in_min
q = trunc(n/d)
r = n - q*d
ratio = q + trunc(2*r/d)
```

Depois chama `0x126C3FC`.

`0x126C3FC` faz:

```text
out_min + fixed_mul(out_max-out_min, clamp(t,0,1024))
```

fraction bits `10`, multiply bias `512`.

Para não quebrar hashes de evidência que bindavam `Reference/FootballCore/FixedPoint.h`, a recuperação específica ficou em:

```text
Reference/FootballPhysics/ShootRemap.h
```

GREEN relevante: `e49a16a4b0e561c60977952bd7e0ed7e2099bba0`, run `34784291595` SUCCESS.

---

## 9. GetShootSpeedVRate

Trace:

```text
Recovery/Normalized/shoot_speed_v_rate_static_trace.json
```

Função exata:

```text
0x01968E24..0x0196916C
PlayerProperty$$GetShootSpeedVRate
```

Metadata `AIParameterConfig +0x80 = int disArea`.

Assinatura caller-visible recuperada:

```text
GetShootSpeedVRate(goal_child, F, c) -> XNumber
```

`force_ratio = F / 100` usando XNumber/int e é aplicado duas vezes.

```text
base = one
     + fixed_mul(
         fixed_mul(
           fixed_mul(GetShootVerRate(goal_child), c),
           force_ratio),
         force_ratio)
```

Se `c < 0`:

```text
bound = max(one, base - disArea_raw)
```

Se `c >= 0`:

```text
bound = min(one, base + disArea_raw)
```

Return:

```text
XRandom.Range(bound, c)
```

`XRandom.Range` também foi fechado caller-visible:

```text
sample = XRandom.NextInt(1001)  // 0..1000
result = from + divide_by_int((to-from)*sample, 1000)
```

O estado/sequence original do RNG continua não recuperado. `behavior_validated=false` permanece correto.

---

## 10. shootDisAndTime e solver vertical

Trace:

```text
Recovery/Normalized/shoot_dis_and_time_static_trace.json
```

Campo:

```text
ShootSpeedConfigItem.shootDisAndTime +0x108
List<List<int>>
```

A tabela é 2D: eixo externo por magnitude de vHor, eixo interno por distância horizontal. Valores são milissegundos e são convertidos por divisão por `XNumber.thousand`; interpolação usa o remap fixed-point recuperado.

Vertical solver:

```text
solved_y_speed =
  (vertical_delta
   - fixed_mul(fixed_mul(flight_time, vertical_accel_raw), flight_time)/2)
  / flight_time
```

Depois clamp em `ySpeedMin` / resolved `ySpeedMax`.

`AIParameterConfig +0x1C0` continua chamado conservadoramente de `vertical_accel_raw`; não renomear para gravity sem prova.

---

## 11. GetVVer new path

Range:

```text
0x016E84A4..0x016EA55C
```

Trace atual:

```text
Recovery/Normalized/getvver_new_path_composition_static_trace.json
schema football.recovery.getvver_new_path_composition.v3
```

Produtores source-bound:

```text
horizontal_distance + shootDisMap(+0xE8)
 -> outEnergyMaxMap(+0x100) => out_energy

current_energy + energyMapNew(+0xB8)
 -> ySpeedMax(+0xA0) => y_speed_max

horizontal_distance + shootDisMap(+0xE8)
 -> shootPointHUpMap(+0xF8) => point_up_rate

horizontal_distance + shootDisMap(+0xE8)
 -> shootPointHDownMap(+0xF0) => point_down_rate

PlayerProperty.GetShootProperty result + shootPropertyMapNew(+0xD8)
 -> energyToleranceMap(+0xE0) => energy_tolerance
```

Energy protection:

```text
protected_floor = out_energy - energyNeedProtect
if protected_floor >= current_energy:
    selected_energy = current_energy
else if current_energy >= out_energy + energy_tolerance:
    selected_energy = current_energy
else:
    selected_energy = max(current_energy-energy_tolerance, protected_floor)
```

Target-height adjustment:

```text
delta > 0:
  fixed_mul(delta, point_up_rate)

else:
  -(fixed_mul(abs(delta), point_down_rate) + XNumber.create(0,100))
```

A chamada observada `XNumber.create(0,100)` retorna raw `102`, não random.

`0x14DEFDC..0x14DEFE8 = GoalDoor$$get_Height`.

```text
vertical_delta =
 native_clamp(
   GoalDoor.get_Height + adjustment,
   shootPointH.min,
   shootPointH.max)
 - reference_y
```

Base vector em `0x016E9D08..0x016E9D48`:

```text
vertical_direction * solved_y_speed
```

Modifiers que sobrevivem no new path:

```text
0x3FC parameter[2]
0x41A parameter[2]
```

na ordem `0x3FC -> 0x41A`, escalando os três componentes vivos via fixed multiply.

---

## 12. GetKickVelocity

Range:

```text
0x016EBAD8..0x016EBF14
```

Calls:

```text
GetVHor: 0x016EBBA8
GetVVer: 0x016EBEAC
```

Join final `0x016EBED8..0x016EBF04` combina componente a componente adjusted GetVHor + GetVVer e repacka `XVector3`.

Isso fecha a forma estática do join; não é ainda runtime complete equivalence.

---

## 13. Publicação upstream de 59.637 bytes

O usuário publicou:

```text
Upload ID: 20260913-234939-ff28866f
artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt
59637 bytes
SHA-256:
4a71aa5b3e6fa94414e789f5c779d710f94d9ca082d14b746b9979b3bc679ec3
```

Hashes internos confirmados:

```text
dump.cs:
4ba445977f2b0854b19375d69c5b30275fe36d06518efe2c5028097868579fbe

script.json:
d15222efc79ebfe50074f385c0f5e5af4960fb43c5cf55a383ea32cba34ae799

global-metadata.dat:
92fae52ec4dc570929eb7b99d2083fd6ab6016cbbaa30f87e87ac6732bb1e42e

libil2cpp.so:
2a3ffe74b6c2d195b54db5b1c2616d289ab19d27426a4c4de041a916c214d496
```

Essa publicação fechou o antigo target anônimo:

```text
0x01968398..0x019687C8
PlayerProperty$$GetShootProperty
exact=true
boundary=script.json:next-method
```

GetVVer preserva original `w1`, recarrega em `0x016E8DC4` e chama em `0x016E8DCC`; o return alimenta `shootPropertyMapNew -> energyToleranceMap`.

---

## 14. PlayerProperty.GetShootProperty selector

Foi criado:

```text
Reference/FootballPhysics/PlayerPropertySelector.h
```

Entry:

```text
ResolvePlayerProperty
```

Integração:

```text
ComposeNewGetVVerFromPlayerProperty
```

Branches recuperados:

```text
action 0x16B3 -> property 0x15
action 0x22C5 -> property 0x16
```

Collection:

```text
InCollection(action, 0x13)
 -> base property 0x14
 -> optional PropertySingle.calMain(0x30, runtime value)
```

Normal path mede distância 2D entre `Football.position2D` e `GoalDoor.center` via `XIntMath.Sqrt_Long`.

```text
distance > AI +0x148 -> property 0x10
AI +0x24 >= positionY -> near property 0x0F
AI +0x24 <  positionY -> near property 0x11
distance < AI +0x14C -> near property
```

Middle interval:

```text
ratio = (upper-distance)/(upper-lower)
result = fixed_mul(near, ratio) + fixed_mul(far, 1024-ratio)
```

com a divisão fixed-point nativa `q + trunc(2*r/d)`.

Primeiros callees exatos no body incluem:

```text
Football$$get_position2D
GoalDoor$$getCenter
XIntMath$$Sqrt_Long
XGoalExtension$$InCollection
PropertySingle$$calMain
PlayerProperty$$getShootPropertyWithSpmove
XBaseLocalSetting<AIParameterConfig>$$get_Singleton
```

`whole_function_equivalent=false` continua obrigatório.

---

## 15. PR #13 TDD

```text
RED selector:
93cf1edd5408c54b6528d374bc731d6398311efa
run 34801287309

GREEN selector:
29ac8e76373fc07df9765963c99e0775715eecd4
run 34801381432 SUCCESS

RED integration:
df459ab5b7afe7bb216b187069e97f8f2426a14d
run 34801475096

GREEN integration:
28251f4cb56602ed64ec14542ba6b21606d66da7
run 34801518576 SUCCESS

RED evidence rebinding:
ed4d797dcebeb4248419389b8f5757ff9ade5b35
run 34801599176
C++ 6/6 GREEN; analyzer rejeitou apenas SHA antigo

Analyzer candidate:
0ff9a744831c637bcdd158ec555ef5cb80ea923e
run 34801770214
âncoras/C++ GREEN; trace v2 stale era a única falha

Merge:
c12e61cf21b070f15860346e283c2cb92a9d5bd6
run #183 / 34802035409 SUCCESS
```

---

## 16. PR #14 — extractor profundo

Remaining internals do selector exigiam nova evidência:

```text
0x1967D38
0x1B718D8
AIParameterConfig +0x24/+0x148/+0x14C
PlayerProperty +0x98
nested +0x40/+0x44
```

O read-only extractor agora pede explicitamente:

```text
0x14DEFDC goal_door_height_14DEFDC
0x1B60CC8 xnumber_create_1B60CC8
0x1968398 shoot_property_1968398
0x1967D38 property_lookup_1967D38
0x1B718D8 property_fallback_1B718D8
```

Os dois últimos labels continuam neutros até `ScriptMethod` provar identidade.

O extractor também copia do `dump.cs`:

```text
AIParameterConfig 0x20..0x160
PlayerProperty 0x90..0xA0
```

incluindo os offsets de interesse e, quando a classe declarada estiver disponível, os nested fields `+0x40/+0x44` do tipo em `PlayerProperty +0x98`.

Schema do report:

```text
football.recovery.getvver_upstream_evidence.v2
```

O BAT também foi endurecido. Se `.local/recovery-output/getvver_upstream_evidence.txt` já existir, ele o preserva automaticamente em um arquivo `getvver_upstream_evidence_previous_<timestamp>.txt` antes de iniciar Python. Não é mais necessário fazer o rename manual executado na rodada anterior.

TDD/CI:

```text
RED deeper evidence:
4a8f961376228938a5f547cb482942a973f6ca30
run #187 / 34802181960

GREEN deeper evidence:
b7f5693614d8b188fe38e272fd613cc5bcaea165
run #189 / 34802255444 SUCCESS

RED Windows preservation:
5d118acf2e616994b619c6be001fb0215078ffc4
run #191 / 34802298175

GREEN Windows preservation:
6b9bb80361d4541fe4a2be66e83947497e6ea4d5
run #193 / 34802399858 SUCCESS

checkpoint head:
478bc02c00fa470f1cbca5af366c81a3680695fe
run #195 / 34802465358 SUCCESS

main after integration:
run #197 / 34802769409 SUCCESS
```

---

## 17. Current executable boundary

Maior entry host hoje:

```text
ComposeNewGetVVerFromPlayerProperty
```

Fluxo:

```text
PlayerProperty.GetShootProperty selector
 -> shootPropertyMapNew / energyToleranceMap

horizontal distance
 -> shootDisMap / outEnergyMaxMap
 -> shootPointHUpMap
 -> shootPointHDownMap

current energy
 -> energyMapNew / ySpeedMax

resolved outputs
 -> protected-energy selection
 -> target-height adjustment
 -> XNumber.create(0,100) fixed downward bias
 -> GoalDoor.get_Height
 -> shootPointH clamp - reference_y
 -> shootDisAndTime lookup
 -> ballistic vertical solve
 -> ySpeedMin / ySpeedMax clamp
 -> vertical_direction * solved_y_speed
 -> optional 0x3FC parameter[2]
 -> optional 0x41A parameter[2]
 -> shared GetVVer return
```

Esse boundary é executável dentro das precondições canônicas recuperadas, mas **não** é ainda whole-function native differential equivalence.

---

## 18. O que ainda falta antes de fechar GetVVer

1. identidade/body semantics de `0x1967D38`;
2. identidade/body semantics de `0x1B718D8`;
3. nomes/unidades exatos de `AIParameterConfig +0x24/+0x148/+0x14C`;
4. tipo/campos reais de `PlayerProperty +0x98` e nested `+0x40/+0x44`;
5. runtime Football/GoalDoor object wiring;
6. runtime activation e ratio real de `0x3FC`;
7. runtime activation e ratio real de `0x41A`;
8. native/original whole-path differential vectors;
9. old-path GetVVer preservado/validado separadamente;
10. caller-visible GetKickVelocity completo;
11. `BALL_CONTACT.velocity`;
12. regressão completa;
13. só então Physics v0.3.

`BallContact.h` continua exigindo `authoritative && semantic_complete && recovered_velocity`. Não criar fallback aproximado para ultrapassar o gate.

---

## 19. PRIMEIRA AÇÃO DO CODEX AGORA

No checkout Windows real:

```powershell
cd "C:\Users\dg71\Documents\ChatGPT\JOGO DE FUTEBOL"
git status --short
git switch main
git fetch origin
git pull --ff-only origin main
git log -1 --oneline
```

Preservar qualquer modificação local do usuário; se a troca/pull ameaçar sobrescrever arquivo local, parar e resolver sem reset destrutivo.

Depois executar:

```powershell
.\tools\EXTRAIR_GETVVER_UPSTREAM.bat
```

Fluxo esperado:

```text
preservar report anterior automaticamente
 -> validar hashes canônicos locais
 -> extrair metadata ShootSpeedConfigItem
 -> extrair AIParameterConfig
 -> extrair PlayerProperty / nested type
 -> disassemblar 5 requested targets
 -> first-level direct callees
 -> .local/recovery-output/getvver_upstream_evidence.txt
 -> publicar em artifacts/native-recovery/getvver-upstream/<NEW_UPLOAD_ID>/
 -> criar manifests/uploads/<NEW_UPLOAD_ID>.json
```

Assim que existir o novo upload, o Codex deve consumir **esse novo TXT + manifesto**, confirmar SHA/bytes e só então atribuir identidade/semântica a `0x1967D38`, `0x1B718D8` e aos campos AI/bonus.

---

## 20. Ordem recomendada de leitura

```text
_CHECKPOINTS/CURRENT.md
Docs/CODEX_RETORNO_HANDOFF_2026-09-13.md
Docs/CODEX_RETORNO_HANDOFF_COMPLETO_2026-09-14.md
Recovery/Normalized/recovery_manifest.json
Recovery/Normalized/shoot_velocity_dataflow_static_trace.json
Recovery/Normalized/shoot_helper_semantics_static_trace.json
Recovery/Normalized/shoot_speed_v_rate_static_trace.json
Recovery/Normalized/shoot_dis_and_time_static_trace.json
Recovery/Normalized/getvver_new_path_composition_static_trace.json
Recovery/Physics/SHOOT_VELOCITY_STATIC_RECOVERY.md
Recovery/Physics/SHOOT_HELPER_SEMANTICS.md
Recovery/Physics/GETVVER_NEW_PATH_COMPOSITION.md
Reference/FootballPhysics/ShootRemap.h
Reference/FootballPhysics/ShootSpeedVRate.h
Reference/FootballPhysics/ShootDisAndTime.h
Reference/FootballPhysics/GetVVerNewPath.h
Reference/FootballPhysics/GetVVerNewPathConfig.h
Reference/FootballPhysics/PlayerPropertySelector.h
Tools/analyze_getvver_new_path_composition.py
Tools/extract_getvver_upstream_evidence.py
tools/EXTRAIR_GETVVER_UPSTREAM.bat
```

Evidence principal:

```text
artifacts/native-recovery/20260913-163217-9cdb54d0/01_disassembly_shoot.txt
artifacts/native-recovery/shoot-helpers/20260913-175551-3fafba6a/01_shoot_helper_disassembly.txt
artifacts/native-recovery/getvver-upstream/20260913-234939-ff28866f/01_getvver_upstream_evidence.txt
```

Depois da primeira ação, acrescentar o novo `getvver-upstream/<NEW_UPLOAD_ID>`.

---

## 21. Segurança do workspace

Existem modificações locais do usuário que não devem ser descartadas:

```text
Tools/PUBLICAR_MASTER_NO_GITHUB.bat
Tools/PUBLICAR_MASTER_NO_GITHUB.ps1
docs/ARCHIVE_LINEAGE_AND_HASHES.md
docs/PROJECT_SOURCE_OF_TRUTH.md
```

Também existem warnings de case collision no Windows entre alguns caminhos `Docs/`/`docs/` e `Tools/`/`tools/`. Não transformar isso em uma limpeza ampla durante a recuperação de física.

---

## 22. Claims proibidos

Não afirmar que:

- o workspace histórico 92/92 foi recuperado;
- Physics v0.3 está pronto;
- GetVHor inteiro é whole-function native equivalent;
- GetVVer inteiro é whole-function native equivalent;
- GetKickVelocity runtime completo está fechado;
- BALL_CONTACT.velocity está fechado;
- RNG state do original foi recuperado;
- `vertical_accel_raw` é definitivamente gravity;
- 1-226-19 foi integrada;
- Unreal runtime/package/rendered match/FPS foi validado;
- `0x1967D38` ou `0x1B718D8` têm nome conhecido antes da nova publicação;
- pre-base GetVHor `0x3FE/0x3FC` sobrevive ao retorno normal.

---

## 23. Estado final em uma linha

```text
main 478bc02...
 -> v0.2 preservado
 -> evidência ARM64 canônica publicada
 -> remap/lerp fixed-point recuperados
 -> GetShootSpeedVRate normal-return recuperado; RNG state externo
 -> shootDisAndTime + solver vertical recuperados
 -> GetVVer new-path maps e target-height recuperados
 -> PlayerProperty.GetShootProperty identificado e branch selector implementado
 -> selector já alimenta shootPropertyMapNew/energyToleranceMap
 -> 0x3FC/0x41A pós-vetor preservados
 -> extractor profundo para 0x1967D38/0x1B718D8 já está em main
 -> report anterior agora é preservado automaticamente no Windows
 -> PR #14 merged
 -> main CI #197 SUCCESS
 -> próximo passo: executar EXTRAIR_GETVVER_UPSTREAM.bat e consumir o novo upload
 -> Physics v0.3 continua BLOCKED
```

**Codex: continue exatamente daqui. Não recomece.**
