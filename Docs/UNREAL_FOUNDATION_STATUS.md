# Unreal foundation status

The project descriptor and C++ module scaffold now exist at the repository root.

## Implemented in this checkpoint

- Football.uproject with Windows target and Enhanced Input, Pose
  Search, IKRig, Control Rig and CommonUI plugin declarations.
- Football runtime module with Game, Client and Dedicated Server target files.
- UFootballSimulationSubsystem fixed-step adapter at 120 Hz by default. It
  accepts a ball contact only when the normalized record is authoritative,
  semantic-complete and velocity-resolved; there is no ball_impulse fallback.
- Normalized FFootballBallContact/FFootballBallState contracts and an initial
  GameMode entry point.
- Read-only Unreal and Blender automation preflight scripts.

## Validation boundary

The C++ reference tests compile and pass with the installed MSVC toolchain.
The Unreal Editor, UnrealBuildTool, and project-generation command were not
found on this machine during this checkpoint, so no Unreal compile or package
claim is made. Re-run after installing/associating a UE 5.x installation.

## Engine-independent playable contract

`Reference/FootballSimulation/MatchSimulation.*` now provides a deterministic
server-side shell for input, player movement, resolved ball contact, goal, and
restart. It is deliberately a contract fixture: its provisional movement
numbers are new-game tuning, while mobile kick semantics remain behind the
recovery gate. The five-case MSVC suite is the current executable evidence.

- Added Primary Data Asset contracts for player definitions, actions and
  competitions. They carry provenance and unresolved/Provisional flags so data
  import cannot silently become gameplay authority.
- Added Enhanced Input intent and server command structures. The command has
  owner and sequence/tick metadata and contains no client-supplied BallState or
  velocity.

## Primeira partida headless

`Reference/FootballGameplay/PlayableMatch.*` acrescenta uma implementação
engine-independent para validar a cadeia jogável antes de o Unreal Editor ser
instalado. Ela monta elencos 3v3, 5v5 e 11v11, aplica ownership de comandos,
movimento com aceleração/frenagem, posse, passe, chute, drible, desarme,
salvamento de goleiro, gol e reinício em tick fixo.

As velocidades dessa classe são `NewGameAuthored` e servem apenas como tuning
provisório do novo jogo. Não são uma reconstrução de `GetVHor`/`GetVVer` e não
alteram o gate do recovery mobile. O teste executável cobre a interação real
entre esses estados; a integração posterior no Unreal deve substituir o
fixture pelo adapter C++/Subsystem mantendo a mesma autoridade do servidor.
