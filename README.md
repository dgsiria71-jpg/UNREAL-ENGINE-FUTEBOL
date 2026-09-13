# UNREAL ENGINE FUTEBOL

Repositório oficial: [dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL](https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL), branch `main`. O desenvolvimento usa Git local, branches de trabalho, testes e publicação dos incrementos validados neste repositório. Os históricos local e GitHub foram unidos sem reescrever commits anteriores.

O produto é um novo jogo de futebol para Windows em Unreal Engine 5.x e C++ modular. Blender é a fonte 3D; Blueprint é complementar. Unity/IL2CPP descreve somente a fonte mobile e a conversão offline.

## Continuidade

Leia [a Bíblia v3 completa, Quickstart e política de fontes](Docs/Bible_v3/README.md), [_CHECKPOINTS/CURRENT.md](_CHECKPOINTS/CURRENT.md), [_CHECKPOINTS/EVIDENCE.md](_CHECKPOINTS/EVIDENCE.md) e [a política de autoridade](Docs/PROJECT_SOURCE_OF_TRUTH.md). Não recomece o projeto. Neymar v1.9 permanece pausado. Novas fontes locais: Downloads e Videos; build 1-221-5. Não consumir 1-226-19.

## Estado verificável

- Núcleo C++ independente do editor, testes e fixtures de domínio de partida.
- Referência de matemática e spmove validada contra instruções ARM64; relatórios delimitam dependências externas ainda não recuperadas.
- Scaffold Unreal com targets Game/Client/Server, contratos de input/replication e dados. Ainda sem build/runtime Unreal validado.
- Physics v0.2 estável: 67/67 testes; SHA-256 `7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac`.
- 92/92 é histórico. O master remontado em seis partes preserva fontes, mas explicitamente não contém esse workspace. [Auditoria](Docs/MOBILE_1_221_5_SOURCE_MAP.md).
- Physics v0.3, jogo final e 120 FPS em partida real ainda não demonstrados.

## Estrutura

- `Reference/`: núcleo e recuperação em C++ independente da engine.
- `Source/`, `Config/`, `Football.uproject`: adaptação Unreal.
- `Tools/`, `Tests/`: automação, recuperação e validação.
- `Recovery/Normalized/`: contratos, proveniência e resultados delimitados por evidência.
- `Docs/`: arquitetura v1.2, Bíblia v3 e documentação histórica preservada.
- `manifests/`, `history/`: inventários e histórico da linha GitHub inicial.

## Testes reproduzíveis a partir do código publicado

```text
cmake -S Tests -B .local/build/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build .local/build/cmake --config Release
ctest --test-dir .local/build/cmake -C Release --output-on-failure
python -m unittest discover -s Tests -p "test_*.py"
python Tools/check_native_evidence.py
python Tools/Unreal/validate_content.py
```

No Windows com MSVC, `Tools/build_reference.cmd` também compila os probes. Reexecutar comparação nativa exige os binários locais com hashes canônicos e as dependências de `Tools/requirements-recovery.txt`; os testes públicos não fabricam esses inputs. O checkpoint registra os comandos de recuperação completos.

## Próximo gate

Inventário/elegibilidade spmove -> VHor/VVer finais -> GetKickVelocity -> BALL_CONTACT.velocity -> regressão -> Physics v0.3 -> integração em partida Unreal. O domínio utiliza tuning `NewGameAuthored` onde explicitado; isso não equivale a física mobile recuperada.

## Pacotes brutos

Os originais são preservados localmente e não entram nesta publicação de código. O master de SHA-256 `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2` foi remontado/validado localmente; não foi publicado como objeto LFS. A preparação LFS do histórico GitHub não equivale a upload realizado.
