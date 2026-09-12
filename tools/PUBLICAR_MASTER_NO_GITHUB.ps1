$ErrorActionPreference = 'Stop'

$RepoUrl = 'https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL.git'
$RepoName = 'UNREAL-ENGINE-FUTEBOL'
$MasterName = 'FOOTBALL_MOBILE_TO_PC_UNREAL_MASTER_RECOVERY_2026-09-12.zip'
$MasterSha = '4240ae8ff93abcd582b88b65b0e58de0909a9e95ca5197931e6df656b3d3a3e2'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Master = Join-Path $Here $MasterName

function Fail($msg) {
    Write-Host "ERRO: $msg" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '=============================================================='
Write-Host ' FOOTBALL MOBILE -> PC | PUBLICAR MASTER NO GITHUB (Git LFS)'
Write-Host '=============================================================='
Write-Host ''

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail 'Git nao foi encontrado. Instale Git for Windows e tente novamente.'
}

if (-not (Test-Path -LiteralPath $Master)) {
    $Parts = Get-ChildItem -LiteralPath $Here -Filter "$MasterName.part*" | Sort-Object Name
    if ($Parts.Count -eq 0) {
        Fail "Nao encontrei $MasterName nem as partes $MasterName.part*."
    }

    Write-Host "Reconstruindo $MasterName a partir de $($Parts.Count) partes..."
    $Dest = [System.IO.File]::Open($Master, [System.IO.FileMode]::Create)
    try {
        foreach ($Part in $Parts) {
            Write-Host "  + $($Part.Name)"
            $Src = [System.IO.File]::OpenRead($Part.FullName)
            try { $Src.CopyTo($Dest) } finally { $Src.Dispose() }
        }
    } finally { $Dest.Dispose() }
}

Write-Host 'Validando SHA-256 do master...'
$Got = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLower()
if ($Got -ne $MasterSha) {
    Fail "SHA incorreto. Esperado $MasterSha, obtido $Got"
}
Write-Host 'SHA-256 OK.' -ForegroundColor Green

& git lfs version *> $null
if ($LASTEXITCODE -ne 0) {
    Fail 'Git LFS nao foi encontrado. Instale Git LFS e execute: git lfs install'
}

$Work = Join-Path $Here '_github_upload_work'
if (Test-Path -LiteralPath $Work) {
    Remove-Item -LiteralPath $Work -Recurse -Force
}

Write-Host 'Clonando repositorio...'
& git clone $RepoUrl $Work
if ($LASTEXITCODE -ne 0) { Fail 'Falha ao clonar o repositorio.' }

Push-Location $Work
try {
    & git lfs install --local
    if ($LASTEXITCODE -ne 0) { Fail 'Falha ao inicializar Git LFS.' }

    & git lfs track 'artifacts/*.zip'
    New-Item -ItemType Directory -Force -Path 'artifacts' | Out-Null
    Copy-Item -LiteralPath $Master -Destination (Join-Path $Work "artifacts/$MasterName") -Force

    @"
$MasterSha  $MasterName
"@ | Set-Content -LiteralPath 'artifacts/SHA256.txt' -Encoding ASCII

    & git add .gitattributes artifacts/
    if ($LASTEXITCODE -ne 0) { Fail 'git add falhou.' }

    $Pending = & git status --porcelain
    if (-not $Pending) {
        Write-Host 'Nenhuma alteracao nova para publicar.'
    } else {
        & git commit -m 'Add complete recovered mobile-to-PC master artifact via Git LFS'
        if ($LASTEXITCODE -ne 0) { Fail 'git commit falhou.' }
        & git push origin main
        if ($LASTEXITCODE -ne 0) {
            Fail 'git push falhou. Confirme que voce esta autenticado no GitHub no Git for Windows.'
        }
    }

    Write-Host ''
    Write-Host 'PUBLICACAO CONCLUIDA.' -ForegroundColor Green
    Write-Host "Repositorio: https://github.com/dgsiria71-jpg/UNREAL-ENGINE-FUTEBOL"
    Write-Host "Artefato: artifacts/$MasterName"
    Write-Host "SHA-256: $MasterSha"
} finally {
    Pop-Location
}

Write-Host ''
Pause
