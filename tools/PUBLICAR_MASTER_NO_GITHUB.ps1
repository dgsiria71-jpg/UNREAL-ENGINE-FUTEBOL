param(
    [string]$MasterPath = ""
)

$ErrorActionPreference = 'Stop'

$RepoUrl = 'https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL.git'
$RepoName = 'UNREAL-ENGINE-FUTEBOL'
$MasterName = 'FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip'
$MasterSha = '4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2'
$MasterBytes = 794639566
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $Here
$CanonicalLocalMaster = Join-Path $RepoRoot ".local\recovered-original\$MasterName"

function Fail($msg) {
    Write-Host "ERRO: $msg" -ForegroundColor Red
    exit 1
}

function Resolve-Master {
    param([string]$Requested)

    if ($Requested) {
        if (-not (Test-Path -LiteralPath $Requested -PathType Leaf)) {
            Fail "MasterPath nao existe: $Requested"
        }
        return (Resolve-Path -LiteralPath $Requested).Path
    }

    if (Test-Path -LiteralPath $CanonicalLocalMaster -PathType Leaf) {
        return (Resolve-Path -LiteralPath $CanonicalLocalMaster).Path
    }

    $BesideScript = Join-Path $Here $MasterName
    if (Test-Path -LiteralPath $BesideScript -PathType Leaf) {
        return (Resolve-Path -LiteralPath $BesideScript).Path
    }

    $Parts = Get-ChildItem -LiteralPath $Here -Filter "$MasterName.part*" -ErrorAction SilentlyContinue | Sort-Object Name
    if ($Parts.Count -gt 0) {
        Write-Host "Reconstruindo $MasterName a partir de $($Parts.Count) partes ao lado do script..."
        $Dest = [System.IO.File]::Open($BesideScript, [System.IO.FileMode]::Create)
        try {
            foreach ($Part in $Parts) {
                Write-Host "  + $($Part.Name)"
                $Src = [System.IO.File]::OpenRead($Part.FullName)
                try { $Src.CopyTo($Dest) } finally { $Src.Dispose() }
            }
        } finally { $Dest.Dispose() }
        return (Resolve-Path -LiteralPath $BesideScript).Path
    }

    Fail "Nao encontrei o master. Esperado em '$CanonicalLocalMaster', ao lado do script, ou via -MasterPath."
}

Write-Host ''
Write-Host '======================================================================='
Write-Host ' FOOTBALL MOBILE -> PC | PUBLICAR MASTER COMPLETO NO GITHUB VIA LFS'
Write-Host '======================================================================='
Write-Host ''

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail 'Git nao foi encontrado. Instale Git for Windows e tente novamente.'
}

& git lfs version *> $null
if ($LASTEXITCODE -ne 0) {
    Fail 'Git LFS nao foi encontrado. Instale Git LFS e execute: git lfs install'
}

$Master = Resolve-Master -Requested $MasterPath
Write-Host "Master encontrado: $Master"

$Length = (Get-Item -LiteralPath $Master).Length
if ($Length -ne $MasterBytes) {
    Fail "Tamanho incorreto. Esperado $MasterBytes bytes, obtido $Length bytes."
}

Write-Host 'Validando SHA-256 do master (pode levar alguns segundos)...'
$Got = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLower()
if ($Got -ne $MasterSha) {
    Fail "SHA incorreto. Esperado $MasterSha, obtido $Got"
}
Write-Host 'SHA-256 OK.' -ForegroundColor Green

$TempBase = Join-Path ([System.IO.Path]::GetTempPath()) ("football-lfs-upload-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $TempBase | Out-Null
$Work = Join-Path $TempBase $RepoName

try {
    Write-Host 'Clonando o GitHub oficial em workspace temporario limpo...'
    & git clone $RepoUrl $Work
    if ($LASTEXITCODE -ne 0) { Fail 'Falha ao clonar o repositorio.' }

    Push-Location $Work
    try {
        & git lfs install --local
        if ($LASTEXITCODE -ne 0) { Fail 'Falha ao inicializar Git LFS.' }

        & git lfs track 'artifacts/*.zip'
        if ($LASTEXITCODE -ne 0) { Fail 'git lfs track falhou.' }

        New-Item -ItemType Directory -Force -Path 'artifacts' | Out-Null
        $DestMaster = Join-Path $Work "artifacts/$MasterName"
        Copy-Item -LiteralPath $Master -Destination $DestMaster -Force

        @"
$MasterSha  $MasterName
"@ | Set-Content -LiteralPath 'artifacts/SHA256.txt' -Encoding ASCII

        @"
# Canonical recovered master artifact

This directory contains the complete recovered mobile-to-PC master archive through Git LFS.

- File: `$MasterName`
- Bytes: `$MasterBytes`
- SHA-256: `$MasterSha`
- Source workstation path at publication time: `.local/recovered-original/$MasterName`
- Publication rule: the ZIP is authoritative only when the LFS object is uploaded and the pointer is present in GitHub `main`.
"@ | Set-Content -LiteralPath 'artifacts/README.md' -Encoding UTF8

        & git add .gitattributes artifacts/
        if ($LASTEXITCODE -ne 0) { Fail 'git add falhou.' }

        $LfsFiles = & git lfs ls-files
        if ($LASTEXITCODE -ne 0) { Fail 'git lfs ls-files falhou.' }
        if (-not ($LfsFiles -match [regex]::Escape($MasterName))) {
            Fail 'O master nao apareceu como objeto Git LFS. Abortando antes do commit.'
        }

        Write-Host ''
        Write-Host 'Objeto confirmado no Git LFS:' -ForegroundColor Cyan
        $LfsFiles | ForEach-Object { Write-Host "  $_" }

        $Pending = & git status --porcelain
        if (-not $Pending) {
            Write-Host 'Nenhuma alteracao nova para publicar. O artefato pode ja estar no repositorio.'
        } else {
            & git commit -m 'Publish complete recovered mobile-to-PC master via Git LFS'
            if ($LASTEXITCODE -ne 0) { Fail 'git commit falhou. Confirme nome/email do Git.' }

            Write-Host ''
            Write-Host 'Enviando commit e objeto LFS para o GitHub...'
            Write-Host 'Nao feche esta janela durante o upload de ~758 MiB.' -ForegroundColor Yellow
            & git push origin main
            if ($LASTEXITCODE -ne 0) {
                Fail 'git push falhou. Confirme autenticacao, quota Git LFS e conexao; nenhum sucesso sera declarado.'
            }
        }

        Write-Host ''
        Write-Host 'Verificando ponteiro remoto apos o push...'
        & git fetch origin main
        if ($LASTEXITCODE -ne 0) { Fail 'Nao foi possivel atualizar origin/main para verificacao.' }
        $RemotePointer = & git show "origin/main:artifacts/$MasterName" 2>$null
        if ($LASTEXITCODE -ne 0) { Fail 'O ponteiro LFS nao apareceu em origin/main.' }
        $PointerText = ($RemotePointer -join "`n")
        if ($PointerText -notmatch 'version https://git-lfs.github.com/spec/v1' -or
            $PointerText -notmatch [regex]::Escape("oid sha256:$MasterSha") -or
            $PointerText -notmatch [regex]::Escape("size $MasterBytes")) {
            Fail 'O ponteiro remoto existe, mas nao corresponde ao SHA/tamanho esperado.'
        }

        Write-Host ''
        Write-Host 'PUBLICACAO LFS CONCLUIDA E PONTEIRO REMOTO VALIDADO.' -ForegroundColor Green
        Write-Host "Repositorio : https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL"
        Write-Host "Artefato    : artifacts/$MasterName"
        Write-Host "Bytes       : $MasterBytes"
        Write-Host "SHA-256     : $MasterSha"
        Write-Host ''
        Write-Host 'OBS: a existencia do ponteiro remoto confirma o commit; o proprio git push acima e responsavel pelo envio do objeto LFS.'
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
