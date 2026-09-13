# Cobertura real de recovery e implementação

Gerado por Tools/audit_feature_coverage.py. Fonte recuperada, normalização, referência executável, integração Unreal e validação runtime são estados separados.

**Conclusão:** a build mobile 1-221-5 preserva muito material, mas o jogo completo ainda não foi recuperado nem integrado. O runtime Unreal ainda não foi compilado ou jogado nesta máquina.

| Sistema | Fonte | Normalizado | Executável | Unreal | Validação |
|---|---|---|---|---|---|
| Fixed-point physics and vectors | confirmed | confirmed | native differential green | contracts scaffolded | headless only |
| Final kick velocity and ball contact | partial | inventory shape confirmed velocity partial | collection shape tested plus partial native differential | guarded contract scaffolded | blocked |
| Animation controller and COFMotion | confirmed data format | catalogued not runtime database | exporter and previews only | planned | not validated |
| Collision, tackle, interception and goalkeeper | confirmed tables | archive schema only | simple authored headless behaviour | contracts scaffolded | not mobile equivalent |
| Pass, shot, dribble and defense | confirmed source tables | partial | simple authored headless behaviour | input and simulation scaffolded | not mobile equivalent |
| 3D players, ball and stadium | confirmed partial pc exports | asset packages only | not executed | not imported | not validated |
| Game AI | config sources present | not normalized as complete ai | not implemented | module architecture only | not validated |
| Cameras and field views | mobile camera sources present | not normalized | not implemented | planned | not validated |
| Match modes | design and mobile sources present | mode roster contract | 3v3 5v5 11v11 headless fixture | gameplay scaffold only | headless only |

## Lacunas por sistema

### Fixed-point physics and vectors

- not compiled or played in Unreal Editor on this machine
- native divide-by-zero fallback

### Final kick velocity and ball contact

- real-player inventory source/eligibility/RNG
- GetVHor/GetVVer base equations after confirmed old/new path split
- GetKickVelocity composition
- BALL_CONTACT.velocity regression

### Animation controller and COFMotion

- 2,769 logical action mappings
- bulk animation database
- retarget validation
- Pose Search/Motion Matching
- Animation Blueprint/IK/Control Rig
- not compiled or played in Unreal Editor on this machine

### Collision, tackle, interception and goalkeeper

- recovered collision resolution
- contact windows
- fouls/cards/advantage
- goalkeeper recovered equations

### Pass, shot, dribble and defense

- mobile action selection/tuning
- first touch/through pass/cross/volley/header
- placed/curved/chipped/lob shots
- complete dribbles and defense

### 3D players, ball and stadium

- ASTC texture transcode
- PBR materials
- deformable cloth
- complete crowd/flags/railings
- LODs/physics assets
- Unreal import/review

### Game AI

- Player/Team/Tactical/GK AI
- Manager/Club/Background AI
- difficulty and performance tests

### Cameras and field views

- Broadcast camera
- Player Career camera
- ball awareness/occlusion/comfort/transitions
- in-motion review

### Match modes

- complete rules/restarts
- rendered field/cameras
- AI rosters
- real 5v5/11v11
- Career/co-op/Dedicated Server

## Regra de evidência

Um ZIP presente prova preservação de fonte. Parser e catálogo provam leitura estrutural. Teste headless prova apenas o contrato exercitado. Integração Unreal exige importação, compilação e execução no engine; animação em movimento, câmeras, multiplayer e 120 FPS exigem validações próprias.
