# GITHUB UPLOAD STATUS — 2026-09-12

## Já publicado diretamente neste repositório

- README canônico do projeto
- checkpoint atual
- arquitetura Unreal canônica
- master context recuperado
- status Animation Recovery
- status Physics Recovery
- Asset Migration Map
- Important Files Index
- Player Ecosystem / Career / AI scope
- Performance Targets
- Recovery Gaps
- Archive Lineage + hashes
- source archive index + checksums
- asset subtree counts
- project provenance
- ferramentas de recovery/verification
- publicador Git LFS para o pacote mestre

## Artefato binário mestre

Arquivo validado no workspace de recovery:

`FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

- tamanho: `794639566` bytes (~757.83 MiB)
- SHA-256: `4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2`
- validação ZIP: OK

Ele contém os arquivos físicos recuperados, focused archives, documentação, manifests, ferramentas, inventário, transcripts e evidências.

## Por que o binário ainda não aparece em `artifacts/`

O conector GitHub disponível nesta sessão consegue criar/editar arquivos de repositório e commits, mas não expõe upload de Git LFS/Release a partir de um arquivo local grande. O arquivo mestre também excede o limite de um blob Git normal. Portanto ele não foi falsamente marcado como publicado.

O repositório já possui `.gitattributes` preparado para Git LFS e `tools/PUBLICAR_MASTER_NO_GITHUB.ps1`, que valida/reconstrói o master e faz o push LFS para `artifacts/`.

Quando o LFS push for concluído, o artefato esperado é:

`artifacts/FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip`

A integridade deve continuar exatamente no SHA-256 registrado acima.
