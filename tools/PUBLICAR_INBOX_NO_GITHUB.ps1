param(
    [string[]]$SourcePath = @(),
    [string]$DestinationRoot = 'artifacts/incoming',
    [string]$CommitMessage = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoUrl = 'https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL.git'
$RepoName = 'UNREAL-ENGINE-FUTEBOL'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $Here
$DefaultInbox = Join-Path $RepoRoot '.local\github-inbox'
$LargeFileThreshold = 50MB

function Fail([string]$Message) {
    Write-Host ''
    Write-Host "ERRO: $Message" -ForegroundColor Red
    exit 1
}

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Fail "Comando obrigatorio nao encontrado: $Name"
    }
}

function Get-SafeFileName([string]$Name) {
    $invalid = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Name
    foreach ($char in $invalid) { $safe = $safe.Replace([string]$char, '_') }
    return $safe
}

function Assert-NoObviousSecret([System.IO.FileSystemInfo]$Item) {
    $name = $Item.Name.ToLowerInvariant()
    $blockedNames = @('.env', 'id_rsa', 'id_ed25519', 'credentials.json', 'credentials.yml')
    if ($blockedNames -contains $name -or
        $name -match '(^|[._-])(token|secret|password|passwd|private[-_]?key)([._-]|$)' -or
        $name.EndsWith('.pem') -or $name.EndsWith('.pfx') -or $name.EndsWith('.p12')) {
        Fail "Possivel segredo/credencial detectado: $($Item.FullName). Remova-o da selecao antes de publicar."
    }
}

function Resolve-SourceItems {
    $items = New-Object System.Collections.Generic.List[System.IO.FileSystemInfo]

    if ($SourcePath.Count -gt 0) {
        foreach ($requested in $SourcePath) {
            if (-not (Test-Path -LiteralPath $requested)) {
                Fail "SourcePath nao existe: $requested"
            }
            $resolved = Get-Item -LiteralPath (Resolve-Path -LiteralPath $requested).Path
            $items.Add($resolved)
        }
    } else {
        if (-not (Test-Path -LiteralPath $DefaultInbox)) {
            New-Item -ItemType Directory -Force -Path $DefaultInbox | Out-Null
            Write-Host "Inbox criada: $DefaultInbox" -ForegroundColor Yellow
            Write-Host 'Coloque nela os arquivos/pastas que deseja publicar e rode este script novamente.'
            exit 2
        }
        foreach ($item in Get-ChildItem -LiteralPath $DefaultInbox -Force) {
            $items.Add($item)
        }
    }

    if ($items.Count -eq 0) {
        Fail "Nenhum arquivo encontrado. Use -SourcePath ou coloque arquivos em $DefaultInbox"
    }

    foreach ($item in $items) {
        if ($item.Name -eq '.git') { Fail 'Nunca publique uma pasta .git como artefato.' }
        Assert-NoObviousSecret $item
    }
    return $items
}

Require-Command 'git'
& git lfs version *> $null
if ($LASTEXITCODE -ne 0) {
    Fail 'Git LFS nao foi encontrado. Instale Git LFS e execute: git lfs install'
}

$SourceItems = Resolve-SourceItems
$UploadId = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + ([guid]::NewGuid().ToString('N').Substring(0,8))
$TempBase = Join-Path ([System.IO.Path]::GetTempPath()) ("football-github-upload-$UploadId")
$Prepared = Join-Path $TempBase 'prepared'
$CloneRoot = Join-Path $TempBase $RepoName
New-Item -ItemType Directory -Force -Path $Prepared | Out-Null

$preparedFiles = New-Object System.Collections.Generic.List[object]

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $index = 0
    foreach ($item in $SourceItems) {
        $index++
        Assert-NoObviousSecret $item
        if ($item.PSIsContainer) {
            # Avoid accidentally shipping gigantic generated caches when somebody points at the project root.
            if (Test-Path -LiteralPath (Join-Path $item.FullName '.git')) {
                Fail "A pasta '$($item.FullName)' parece ser um repositorio. Selecione apenas a subpasta/arquivo que deseja compartilhar."
            }
            $safe = Get-SafeFileName $item.Name
            $outName = ('{0:D2}_{1}.zip' -f $index, $safe)
            $outPath = Join-Path $Prepared $outName
            Write-Host "Compactando pasta: $($item.FullName) -> $outName"
            [System.IO.Compression.ZipFile]::CreateFromDirectory(
                $item.FullName,
                $outPath,
                [System.IO.Compression.CompressionLevel]::Optimal,
                $true
            )
            $kind = 'directory_zip'
            $sourceDisplay = $item.FullName
        } else {
            $safe = Get-SafeFileName $item.Name
            $outName = ('{0:D2}_{1}' -f $index, $safe)
            $outPath = Join-Path $Prepared $outName
            Write-Host "Preparando arquivo: $($item.FullName) -> $outName"
            Copy-Item -LiteralPath $item.FullName -Destination $outPath -Force
            $kind = 'file'
            $sourceDisplay = $item.FullName
        }

        $file = Get-Item -LiteralPath $outPath
        $sha = (Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $preparedFiles.Add([pscustomobject]@{
            source = $sourceDisplay
            kind = $kind
            stored_name = $outName
            bytes = [int64]$file.Length
            sha256 = $sha
        })
    }

    Write-Host ''
    Write-Host 'Clonando o GitHub oficial em workspace temporario limpo...'
    & git clone --branch main --single-branch $RepoUrl $CloneRoot
    if ($LASTEXITCODE -ne 0) { Fail 'Falha ao clonar o repositorio.' }

    Push-Location $CloneRoot
    try {
        & git lfs install --local
        if ($LASTEXITCODE -ne 0) { Fail 'Falha ao inicializar Git LFS.' }

        $destDir = "$DestinationRoot/$UploadId" -replace '\\','/'
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        New-Item -ItemType Directory -Force -Path 'manifests/uploads' | Out-Null

        $manifestFiles = @()
        foreach ($entry in $preparedFiles) {
            $dest = Join-Path $destDir $entry.stored_name
            Copy-Item -LiteralPath (Join-Path $Prepared $entry.stored_name) -Destination $dest -Force
            $relative = ($dest -replace '\\','/')
            $attr = (& git check-attr filter -- $relative) -join "`n"
            $usesLfs = $attr -match 'filter: lfs'
            if ($entry.bytes -ge $LargeFileThreshold -and -not $usesLfs) {
                Fail "Arquivo grande nao esta coberto por Git LFS: $relative"
            }
            $manifestFiles += [ordered]@{
                source_name = [System.IO.Path]::GetFileName($entry.source)
                source_kind = $entry.kind
                repository_path = $relative
                bytes = $entry.bytes
                sha256 = $entry.sha256
                git_lfs = $usesLfs
            }
        }

        $manifest = [ordered]@{
            schema_version = 'football.github_handoff.v1'
            upload_id = $UploadId
            created_utc = [DateTime]::UtcNow.ToString('o')
            repository = 'dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL'
            destination_root = $DestinationRoot
            preservation_rule = 'Source files are copied/zipped; originals are not modified or deleted.'
            files = $manifestFiles
        }
        $manifestPath = "manifests/uploads/$UploadId.json"
        $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

        # Binary extensions are intentionally ignored outside artifacts/. Force only the canonical handoff tree.
        & git add .gitattributes .gitignore $manifestPath
        & git add -f -- $destDir
        if ($LASTEXITCODE -ne 0) { Fail 'git add falhou.' }

        foreach ($entry in $manifestFiles) {
            if ($entry.git_lfs) {
                $listed = (& git lfs ls-files -- $entry.repository_path) -join "`n"
                if ($LASTEXITCODE -ne 0 -or $listed -notmatch [regex]::Escape($entry.repository_path)) {
                    Fail "Arquivo deveria estar no LFS, mas nao apareceu em git lfs ls-files: $($entry.repository_path)"
                }
            }
        }

        $Pending = & git status --porcelain
        if (-not $Pending) { Fail 'Nenhuma alteracao foi preparada para commit.' }

        if (-not $CommitMessage) {
            $CommitMessage = "Publish project source handoff $UploadId via Git LFS"
        }
        & git commit -m $CommitMessage
        if ($LASTEXITCODE -ne 0) { Fail 'git commit falhou. Confirme git user.name/user.email.' }

        # Main may move while large files are hashed/zipped. Reconcile without rewriting remote history.
        & git fetch origin main
        if ($LASTEXITCODE -ne 0) { Fail 'git fetch origin main falhou.' }
        $behind = (& git rev-list --count HEAD..origin/main).Trim()
        if ([int]$behind -gt 0) {
            Write-Host "main avancou $behind commit(s); reaplicando o upload sobre origin/main..." -ForegroundColor Yellow
            & git rebase origin/main
            if ($LASTEXITCODE -ne 0) { Fail 'Rebase automatico falhou. Nenhum push foi feito.' }
        }

        Write-Host ''
        Write-Host 'Enviando commit e objetos LFS para o GitHub...' -ForegroundColor Cyan
        & git push origin HEAD:main
        if ($LASTEXITCODE -ne 0) {
            Fail 'git push falhou. Verifique autenticacao, quota Git LFS e conexao. Nenhum sucesso sera declarado.'
        }

        & git fetch origin main
        if ($LASTEXITCODE -ne 0) { Fail 'Falha ao atualizar origin/main para verificacao.' }
        & git merge-base --is-ancestor HEAD origin/main
        if ($LASTEXITCODE -ne 0) { Fail 'O commit publicado nao foi encontrado em origin/main.' }

        foreach ($entry in $manifestFiles) {
            if ($entry.git_lfs) {
                $pointer = (& git show "origin/main:$($entry.repository_path)" 2>$null) -join "`n"
                if ($LASTEXITCODE -ne 0 -or
                    $pointer -notmatch 'version https://git-lfs.github.com/spec/v1' -or
                    $pointer -notmatch [regex]::Escape("oid sha256:$($entry.sha256)") -or
                    $pointer -notmatch [regex]::Escape("size $($entry.bytes)")) {
                    Fail "Ponteiro LFS remoto invalido: $($entry.repository_path)"
                }
            } else {
                & git cat-file -e "origin/main:$($entry.repository_path)"
                if ($LASTEXITCODE -ne 0) { Fail "Arquivo remoto ausente: $($entry.repository_path)" }
            }
        }

        Write-Host ''
        Write-Host 'PUBLICACAO CONCLUIDA E VALIDADA.' -ForegroundColor Green
        Write-Host "Upload ID : $UploadId"
        Write-Host "Destino   : $destDir"
        Write-Host "Manifesto : $manifestPath"
        Write-Host "Arquivos  : $($manifestFiles.Count)"
        Write-Host ''
        foreach ($entry in $manifestFiles) {
            $mode = if ($entry.git_lfs) { 'LFS' } else { 'Git' }
            Write-Host ("[{0}] {1} | {2} bytes | SHA256 {3}" -f $mode, $entry.repository_path, $entry.bytes, $entry.sha256)
        }
        Write-Host ''
        Write-Host 'Os arquivos originais locais foram preservados.'
    } finally {
        Pop-Location
    }
} finally {
    if (Test-Path -LiteralPath $TempBase) {
        Remove-Item -LiteralPath $TempBase -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ''
Pause
