# Gameplay Framework e runtime

## Fronteira engine-independent

FootballCore e FootballSimulation devem compilar e testar sem renderer/editor. Unreal fornece o adapter de mundo, input, replication e apresentação. O domínio não depende de UMG, Skeletal Mesh, Animation Blueprint ou callbacks de frame.

## Entidades e responsabilidades

- AFootballGameMode: servidor; cria o match e rejeita configuração inválida.
- AFootballGameState: snapshot replicado, relógio e estado público.
- AFootballPlayerState: team, PlayerDefinition/CareerPlayer ID e ownership público.
- AFootballPlayerController: Enhanced Input local para Input Intent; nunca decide resultado.
- AFootballCharacter: cápsula, visual e componentes; não é autoridade da bola.
- AFootballBallActor: proxy de apresentação/colisão; recebe BallState autoritativo.
- UFootballSimulationSubsystem: fixed tick, command buffer, state transitions e deterministic RNG.
- UFootballMatchSubsystem: lifecycle, restart, score e eventos.
- UFootballActionResolver: combina intent, contexto, tuning normalizado e elegibilidade.
- UFootballAnimationAdapter: converte action/contact metadata em query/Animation Blueprint inputs.
- UFootballRulesSubsystem: regras e reinícios.
- UFootballCareerSubsystem: aggregate de carreira headless e integração com match setup.

## Input e ações

    Enhanced Input
      -> Input Intent (move, facing, pass, shoot, sprint, tackle, skill)
      -> Gameplay Command com sequence/tick/owner
      -> validação no servidor
      -> action resolver
      -> fixed simulation
      -> event/snapshot

Um input não escolhe diretamente a velocidade. A decisão passa por elegibilidade, contexto, player attributes, tuning e recuperação. Um cliente não pode enviar owner de outro jogador, BallState, score, card ou resultado de tackle.

## Bola e contatos

BallState possui estados free, controlled, kicked, deflected, goalkeeper-controlled e dead/restart. Player contact, pass, shot, dribble, first touch, deflection e goalkeeper contact entram em uma fila ordenada por simulation tick. Cada contato contém source action, player ID, frame/time, kick point, selected tuning provenance e resultado calculado.

A consulta de colisão Unreal pode fornecer geometria, normal e overlap, mas o FootballSimulation decide posse, lançamento e regra. Eventos de Animation Blueprint são observações e marcadores, nunca comandos para alterar a bola.

## Jogador e goleiro

Locomotion separa intent, desired velocity, acceleration, braking, turn rate, body orientation e presentation pose. Player AI e input humano usam o mesmo contrato. Goalkeeper usa uma camada própria para posicionamento, catch, parry, throw e save, com BallState como autoridade.

## Regras e restart

Kickoff, throw-in, goal kick, corner, free kick, penalty, offside policy, advantage, foul, cards, substitutions, injury e goal confirmation são estados de FootballRules/FootballMatch. O renderer mostra a decisão; não inventa restart por overlap.

## IA

PlayerAI reage em alta frequência; decision frequency é intermediária; TeamAI e tática rodam em frequência menor; ManagerAI e ClubAI rodam por evento/calendário; background match AI usa o mesmo contrato de regras em modo headless. Relevance/AI LOD reduz custo sem remover a estrutura tática. Não existe uma classe gigante de IA.

## Fixed simulation

A lógica usa um timestep fixo/substeps selecionado por profiling. Render frames interpolam estados. Replays e testes executam uma sequência de Gameplay Commands e comparam snapshots/hash. Taxa de render não pode mudar ball trajectory, possession, foul, goal ou career result.
## Estado executável atual

`Reference/FootballGameplay/PlayableMatch.*` fornece uma primeira partida
headless determinística independente do renderer. O fixture monta 3v3, 5v5 e
11v11, impõe ownership, executa movimento com aceleração/frenagem e cobre
posse, passe, chute, drible, desarme, defesa do goleiro, gol e reinício. Seu
lançamento de bola é marcado como tuning `NewGameAuthored`, separado do
recovery mobile; ele não fecha nem contorna o gate de `GetVHor`/`GetVVer`.

A suíte MSVC atual combina o contrato de recovery e essa fatia jogável:
`FOOTBALL_REFERENCE_TESTS: 16/16 GREEN`. Quando o Unreal Editor estiver
instalado, o mesmo contrato será adaptado para GameMode/Subsystem/Actors e
Functional Tests em mapa carregado.
