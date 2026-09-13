# Physics Recovery: handoff e gate v0.3

Current executable recovery: [native differential checkpoint](../../Recovery/Physics/EXECUTABLE_RECOVERY.md).
Selected-property spmove branches, native sqrt and 3D normalization are now
implemented in engine-independent C++. Whole velocity and selection remain
pending; the static-only observations below describe earlier checkpoints.

## Estado de partida

O release estável é FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip, SHA256 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac. Ele fecha 83/83 tabelas e 67 testes, mas declara a seleção de impulso como unresolved by design. O bridge atual agenda contato em kickOutFrame/30 e mantém ball_impulse=None.

O arquivo de migração v1.1 possui spmoveconfig, spmoveactiondata, IL2CPP e metadata. A metadata confirma os métodos ShootUtility.GetVHor, GetVVer, GetKickVelocity e o campo spmoveInUseData em XGoal_ShootBase e GoalStateData.Shoot. Isso localiza o trabalho, mas não prova ainda o corpo nativo dos modificadores.

## Gate obrigatório

A sequência não pode ser encurtada:

    spmoveInUseData
      -> VHor modifier
      -> VVer modifier
      -> GetVHor FINAL + GetVVer FINAL
      -> GetKickVelocity FINAL
      -> BALL_CONTACT.velocity
      -> remover ball_impulse=None
      -> regressão completa
      -> empacotar v0.3

Até o fechamento desse gate não se publica v0.3 e não se declara paridade final. A função normalizada deve expor velocity_raw/velocity_normalized, origem e operação de wrap; não aceitar uma velocidade calculada por animação.

## Invariantes comprovados

- XNumber signed int32 e escala 1/1024.
- Interpolação ActionFit é bilinear somente sobre coordenadas normalizadas fornecidas pela camada superior.
- kickOutFrame usa COFMotion 30 FPS.
- O campo +0x1C0 continua vertical_accel_raw.
- collisiondata tem 104 regras e não serializa breakTime, apesar de metadata sugerir campo runtime.
- Os valores de ShootSpeed e mapas new method permanecem raw e decodificados; semântica de input não deve ser inventada.
- Um contato sem tuning selecionado mantém ausência explícita em vez de receber impulso padrão.

## Implementação de referência

A primeira implementação de C++ deve ser engine-independent e reproduzir os inteiros/wrap do recovery antes de um adapter Unreal. Estruturas sugeridas:

    FFixedXNumber { int32 Raw; }
    FRecoveredShootInput
    FSpmoveContext
    FHorizontalVelocityResult
    FVerticalVelocityResult
    FKickVelocityResult
    FBallContact

FSpmoveContext recebe apenas campos cuja origem foi confirmada. Qualquer campo sem semântica comprovada permanece Optional/Unknown. O método ResolveKickVelocity deve falhar explicitamente se o seletor necessário estiver ausente; não deve retornar uma bola parada como se fosse sucesso.

## Regressão mínima antes do release

Reexecutar os 67 testes do v0.2 e acrescentar casos golden para:

- old/new GetVHor;
- old/new GetVVer;
- remap clampado e normalização XVector2;
- ShootSpeed 5800 e seus mapas;
- distância, vHor, energia, playerHeight, ballPos.y delta, flightTime e ySpeedMin/ySpeedMax;
- int32 wrap ARM64;
- spmove VHor/VVer;
- soma final GetKickVelocity;
- emissão de BALL_CONTACT.velocity somente quando a seleção for resolvida;
- ausência de ball_impulse=None;
- ground pass, lofted pass, shot, deflection, first touch e GK contact;
- determinismo entre múltiplas execuções e entre taxas de render diferentes.

Um teste só pode ser chamado GREEN quando executado com o mesmo comando e a saída estiver registrada no checkpoint. O pacote v0.2 original não é substituído por uma cópia parcial.

## Integração Unreal posterior

Após o gate, FootballSimulation recebe FBallContact. AFootballBallActor apresenta estado e usa colisão para consulta, enquanto a regra de contato e velocidade vem da simulação. O evento de animação pode carregar contact frame/marker, mas não substitui o resultado. Pass, shot, dribble contacts, deflections, goalkeeper contacts e player contacts compartilham o mesmo contrato.
## Manager-derived spmove properties

`param_Xnumber` is not part of the normalized `spmoveconfig` stream. Static
ARM64 manager evidence shows `GetSpmoveData` selecting a logic-ID config and
returning the selected record's field at `config + 0x10`; the no-ratio variant
uses the same boundary. The selector chain and unresolved level/odds behavior
are recorded in `Recovery/Normalized/spmove_manager_static_trace.json`. This
is an integration constraint for Unreal: import the schema and provenance,
but do not emit velocity until the runtime property derivation is proved.

## Buffer deserializer trace

The native buffer-reader listing is saved in ignored scratch as
`.local/il2cpp/spmove_deserialize_disassembly.txt`; its durable analysis is
`Recovery/Normalized/spmove_deserialize_static_trace.json`. The config reader
writes all ten serialized config fields and does not write
`SpmoveConfigConfigItem.param_Xnumber` at offset `0x10`. The action reader
writes the seven fields represented in the normalized action schema. This is
stronger schema evidence, while constructor/manager post-processing and
runtime property units are still unresolved. It does not close v0.3.

## Novo rastreio de derivação runtime

O artefato `Recovery/Normalized/spmove_runtime_static_trace.json` registra,
sem executar o binário Android, três fatos adicionais:

1. `SpmoveModule.OnGameStart` cria `List<XNumber>` para itens habilitados,
   armazena a lista em `param_Xnumber` (`+0x10`) e copia cada inteiro bruto da
   lista serializada `param` (`+0x38`) via `List<XNumber>.Add`.
2. `getSuccessByOdds` carrega `odds` (`+0x34`), aplica `odds << 10` e chama o
   helper opaco `0x192A1E0`; a escala é confirmada, mas o sorteio não.
3. Os métodos de `Player` encaminham o manager em `Player+0x28`, e sete pontos
   em `ShootUtility` pedem propriedades `0x3FE`, `0x3FC`, `0x3FE`, `0x3FC`,
   `0x3FC`, `0x41A` e `0x3FB` através de `GetSpmoveDataRatio`.

No arquivo canônico normalizado, 183 de 292 configs têm `param_raw` vazio. A
contagem descreve o arquivo capturado; não elimina mutação posterior. O
resultado ainda é estático, `behavior_validated=false`, e não fecha o gate de
VHor/VVer/GetKickVelocity.

## Acesso aos parâmetros dos modificadores

O trace `Recovery/Normalized/spmove_modifier_access_static_trace.json`
confirma os índices lidos no código nativo: `0x3FE` usa `param[0]` no VHor,
`0x3FC` usa `param[1]` no VHor e `param[2]` no VVer, enquanto `0x41A` e
`0x3FB` usam `param[2]` no VVer. O primeiro grupo soma o valor a um termo
derivado de raiz quadrada; os demais entram em sequências de multiplicação
fixed-point. Isso ainda não é a equação final nem fecha a seleção de nível,
unidades ou comportamento; `behavior_validated=false` e o gate v0.3 continua
bloqueado.
