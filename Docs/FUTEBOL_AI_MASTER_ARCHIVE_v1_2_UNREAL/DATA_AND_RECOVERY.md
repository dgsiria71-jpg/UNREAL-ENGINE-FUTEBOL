# Data, recovery e normalização

## Fronteira

O pacote mobile é uma fonte, não o runtime. O processo tem quatro estágios:

1. Extract: ler bytes, descompactar LZ4/Unity containers necessários e registrar origem.
2. Decode: aplicar parser source-faithful com consumo de bytes e trailing bytes explícitos.
3. Normalize: emitir JSON/CSV/binário versionado engine-independent, com unidades, escala, IDs, hash e confiança.
4. Import: criar Data Assets, Data Tables, Animation Sequences/Pose Search inputs e assets visuais Unreal por commandlet/editor tools.

Uma partida nunca resolve um arquivo IL2CPP, AssetBundle ou formato mobile ad hoc. O Server recebe só contratos normalizados e dados já validados.

## Contrato normalizado

Cada registro tem, conforme aplicável:

    schema_version
    source_id
    source_archive_sha256
    source_entry
    source_offset / source_length
    semantic_status
    unit
    fixed_scale
    value_raw
    value_normalized
    references
    validation

Inteiros recuperados permanecem disponíveis ao lado da conversão métrica. Valores desconhecidos ficam null/UNKNOWN; não se preenche com zero, gravidade presumida ou impulso sintético. Mudanças de schema exigem migração e teste golden.

## Recovery preservado

A camada mantém XNumber signed int32 com ONE 1024; XQuat40U de 5 bytes; 30 FPS; controller.ctrl; 20.213 COFBlendStates; 50.127 clip leaves; 30.648 blend-tree nodes; 13.722 COFMotions; kickOutFrame; kickPoint; MotionExpand; ActionSpeed; ActionFit; ShootSpeed; PassSpeed; Dribble; Tackle; Intercept; goalkeeper; Collision; formations; Visual Registry; PC 3D Ready; assets e configs.

Recovery de animação é separado do cálculo de resultado. Cada clip normalizado inclui bone mapping, root movement, ball marker se existir, contacto e estado original. Ações lógicas que não correspondem a um COFMotion ficam registradas como unresolved semantic action, não como arquivo ausente.

## Proveniência atual

Confirmado nesta execução:

- FOOTBALL_PHYSICS_RECOVERY_PACK_v0_2.zip existe em Downloads e seu SHA256 é 7d5cabe5d974f7282ca7126d5c36c7bc71a448275cf144b73625be9fccf415ac.
- O pacote v0.2 contém 83 tabelas byte-exact, 12.920.443 bytes decodificados, ponte com 18.101 candidatos e 67 testes.
- A execução local corrigida com a fixture do pacote de animação passou 67/67 testes.
- O arquivo de migração v1.1 contém global-metadata.dat, libil2cpp, spmoveconfig, spmoveactiondata e documentação de origem.
- A documentação registra um workspace posterior em 92/92, mas nenhuma cópia desse workspace foi localizada nesta busca; 92/92 ainda não é uma afirmação reproduzida.

## Asset pipeline

Blender é source of truth. O importador Unreal não edita o blend canônico. Um asset é admitido somente com hash, escala, orientação, skeleton mapping, material slots, LOD policy e validation report. Neymar v1.9 é preservado como fixture congelada. Generic Player pipeline deve aceitar jogadores temporários e trocar o asset sem tocar em FootballSimulation.

## Dados de carreira e competição

PlayerDefinition, PlayerCardDefinition, CardInstance, Roster, Squad, Formation, Tactics e MatchSnapshot têm IDs e schemas distintos. Card progression não altera diretamente Career development. Career state é engine-independent e pode ser testado em processo headless sem Unreal Editor, renderer ou assets.
