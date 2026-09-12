# PROJECT SOURCE OF TRUTH

## Decisão oficial

A partir de 2026-09-12, o repositório GitHub `dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL` é a **fonte oficial, canônica e sempre atualizada** do projeto de futebol para PC/Windows.

O projeto final é:

- **Windows PC**
- **Unreal Engine 5.x**
- **C++ como núcleo principal**
- **Blender como source of truth 3D**
- Python para automação Blender/Unreal quando útil
- Blueprint como camada complementar, não como arquitetura principal
- o jogo mobile Unity/IL2CPP é fonte de recovery/migração, não o runtime final

## Regra de autoridade

Quando houver divergência entre:

1. arquivos locais;
2. ZIPs históricos;
3. conversas do ChatGPT;
4. documentação antiga;
5. cópias intermediárias;
6. arquivos no GitHub;

a versão rastreada em `main` neste repositório, acompanhada do checkpoint e dos manifests atuais, é a autoridade do projeto.

Exceção: artefatos binários grandes ainda não publicados via Git LFS devem ser considerados `pending upload` até aparecerem fisicamente no repositório e terem o hash validado.

## Política de trabalho

Toda mudança real deve terminar no GitHub. O fluxo padrão é:

`pesquisar/implementar → testar → registrar evidência → atualizar checkpoint → commit → push → main oficial`

Para mudanças maiores, pode-se trabalhar em branch temporária e integrar somente após validação. Nunca manter uma evolução válida apenas em um chat ou workspace efêmero.

## Checkpoint obrigatório

`_CHECKPOINTS/CURRENT.md` deve refletir o último estado técnico aprovado. Ao fechar um incremento importante, registrar no mínimo:

- o que foi concluído;
- testes executados e resultado;
- hashes/SHAs relevantes;
- limitações ainda abertas;
- próximo passo exato;
- itens que não devem ser refeitos.

## Artefatos grandes

Artefatos binários grandes devem usar **Git LFS** em `artifacts/` ou, quando apropriado, GitHub Releases. Documentação, manifests, código-fonte e scripts permanecem em Git normal.

O master recovery esperado atualmente é:

`FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

SHA-256 esperado:

`4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`

Ele só passa a ser considerado publicado quando existir fisicamente no GitHub/LFS e o hash for validado.

## Estrutura de autoridade

- `README.md` — visão canônica curta
- `_CHECKPOINTS/CURRENT.md` — estado técnico atual
- `docs/` — arquitetura, recovery, migração e decisões
- `manifests/` — provenance, hashes, inventários e lineage
- `tools/` — scripts reprodutíveis
- `Source/`, `Config/`, `Content/` — futuro projeto Unreal oficial
- `artifacts/` — pacotes binários via LFS

## Regra para agentes/IA

Qualquer agente que continuar este projeto deve primeiro ler:

1. `README.md`
2. `_CHECKPOINTS/CURRENT.md`
3. `docs/PROJECT_SOURCE_OF_TRUTH.md`
4. `docs/UNREAL_CANONICAL_ARCHITECTURE.md`
5. os manifests relevantes ao trabalho

Não reiniciar arquitetura já fechada e não substituir Unreal Engine por Unity.
