param(
    [string[]]$Roots = @(),
    [switch]$IncludeAllProjectFiles
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DefaultRoots = @(
    (Join-Path $env:USERPROFILE 'Downloads'),
    (Join-Path $env:USERPROFILE 'Videos\football-dream-be-a-pro-1-221-5'),
    $ProjectRoot
)
if ($Roots.Count -eq 0) { $Roots = $DefaultRoots }

$OutDir = Join-Path $ProjectRoot '.local\full-pc-audit'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$JsonOut = Join-Path $OutDir 'FULL_PC_PROJECT_ARCHIVE_AUDIT.json'
$CsvOut = Join-Path $OutDir 'FULL_PC_PROJECT_ARCHIVE_AUDIT.csv'
$TxtOut = Join-Path $OutDir 'FULL_PC_PROJECT_ARCHIVE_AUDIT_SUMMARY.txt'

$InterestingExt = @('.zip','.7z','.rar','.xapk','.apk','.md','.txt','.json','.csv','.ps1','.bat','.bin','.data','.ctrl','.so','.pdb','.unity3d')
$NameRegex = '(?i)(football|futebol|football-dream|gameplay|xplayable|unreal|biblia|codex|converter_meu_jogo|physics|animation|player|visual|migration|recovery|spmove|goalconfig|controller)'
$ArchiveExt = @('.zip','.xapk')
$ImportantEntryRegex = '(?i)(spmove|shootspeed|getvhor|getvver|getkickvelocity|ball_contact|libil2cpp|global-metadata|controller\.ctrl|xplayable|localsettings|config/match|nova_player|fbxs|prefabs|cofmotion|checkpoint|workspace|test)'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Classify([string]$Name,[string]$Path) {
    $s = ($Name + ' ' + $Path).ToLowerInvariant()
    if ($s -match '1-226-19') { return 'isolated_mobile_1_226_19_do_not_merge' }
    if ($s -match '1-221-5') { return 'canonical_mobile_1_221_5' }
    if ($s -match 'physics_recovery') { return 'physics_recovery_delivery' }
    if ($s -match 'animation_recovery') { return 'animation_recovery_delivery' }
    if ($s -match 'player_ecosystem|player_systems') { return 'player_systems_delivery' }
    if ($s -match 'pc_3d_ready') { return 'pc_3d_delivery' }
    if ($s -match 'visual_') { return 'visual_delivery' }
    if ($s -match 'migration_master') { return 'migration_delivery' }
    if ($s -match 'master_recovery') { return 'master_recovery_or_part' }
    if ($s -match 'master_archive') { return 'project_master_archive' }
    if ($s -match 'biblia') { return 'project_bible' }
    if ($s -match 'gameplay_(data|models|core)|xplayable') { return 'gameplay_source_delivery' }
    return 'supporting_project_material'
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$records = New-Object System.Collections.Generic.List[object]
$errors = New-Object System.Collections.Generic.List[object]

foreach ($root in $Roots) {
    if (-not (Test-Path -LiteralPath $root)) {
        $errors.Add([pscustomobject]@{ path=$root; error='root_not_found' })
        continue
    }
    Write-Host "Varrendo: $root" -ForegroundColor Cyan
    try {
        $files = Get-ChildItem -LiteralPath $root -File -Recurse -Force -ErrorAction SilentlyContinue
    } catch {
        $errors.Add([pscustomobject]@{ path=$root; error=$_.Exception.Message })
        continue
    }
    foreach ($file in $files) {
        $ext = $file.Extension.ToLowerInvariant()
        if (-not ($InterestingExt -contains $ext)) { continue }
        $insideProject = $file.FullName.StartsWith($ProjectRoot,[System.StringComparison]::OrdinalIgnoreCase)
        if (-not $IncludeAllProjectFiles -and -not $insideProject -and $file.Name -notmatch $NameRegex) { continue }
        # Skip generated caches/build products; preserve .local recovery/source material.
        if ($file.FullName -match '(?i)\\(Binaries|DerivedDataCache|Intermediate|Saved|__pycache__|\.pytest_cache)\\') { continue }

        Write-Host "  hash $($file.Name)" -ForegroundColor DarkGray
        try { $sha = Get-Sha256 $file.FullName } catch {
            $errors.Add([pscustomobject]@{ path=$file.FullName; error=$_.Exception.Message })
            continue
        }

        $archiveStatus = $null
        $zipEntries = $null
        $selectedEntries = @()
        if ($ArchiveExt -contains $ext) {
            try {
                $z = [System.IO.Compression.ZipFile]::OpenRead($file.FullName)
                try {
                    $zipEntries = $z.Entries.Count
                    $selectedEntries = @($z.Entries | Where-Object { $_.FullName -match $ImportantEntryRegex } | Select-Object -First 200 | ForEach-Object { $_.FullName })
                    $archiveStatus = 'readable_zip'
                } finally { $z.Dispose() }
            } catch {
                $archiveStatus = 'not_zip_or_unreadable'
            }
        }

        $records.Add([pscustomobject]@{
            name = $file.Name
            full_path = $file.FullName
            extension = $ext
            bytes = [int64]$file.Length
            modified_local = $file.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss')
            sha256 = $sha
            classification = Classify $file.Name $file.FullName
            archive_status = $archiveStatus
            zip_entries = $zipEntries
            selected_entries = $selectedEntries
        })
    }
}

$duplicateGroups = @($records | Group-Object sha256 | Where-Object Count -gt 1 | ForEach-Object {
    [pscustomobject]@{
        sha256 = $_.Name
        count = $_.Count
        files = @($_.Group | ForEach-Object full_path)
    }
})

$result = [ordered]@{
    schema_version = 'football.full_pc_project_archive_audit.v1'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    project_root = $ProjectRoot
    roots = $Roots
    policy = [ordered]@{
        mutation = 'read_only'
        canonical_mobile = '1-221-5'
        isolated_candidate = '1-226-19'
        note = 'Presence does not imply semantic integration. Hash and classify first; compare before merge.'
    }
    record_count = $records.Count
    duplicate_group_count = $duplicateGroups.Count
    records = $records
    duplicate_groups = $duplicateGroups
    errors = $errors
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonOut -Encoding UTF8

$records | Select-Object name,full_path,extension,bytes,modified_local,sha256,classification,archive_status,zip_entries |
    Export-Csv -LiteralPath $CsvOut -NoTypeInformation -Encoding UTF8

$byClass = $records | Group-Object classification | Sort-Object Name
$summary = New-Object System.Collections.Generic.List[string]
$summary.Add('FULL PC PROJECT ARCHIVE AUDIT')
$summary.Add('Generated UTC: ' + [DateTime]::UtcNow.ToString('o'))
$summary.Add('Records: ' + $records.Count)
$summary.Add('Duplicate SHA groups: ' + $duplicateGroups.Count)
$summary.Add('')
$summary.Add('BY CLASSIFICATION')
foreach ($g in $byClass) { $summary.Add(('  {0}: {1}' -f $g.Name,$g.Count)) }
$summary.Add('')
$summary.Add('OUTPUTS')
$summary.Add('  ' + $JsonOut)
$summary.Add('  ' + $CsvOut)
$summary.Add('  ' + $TxtOut)
$summary.Add('')
$summary.Add('IMPORTANT: 1-226-19 is catalogued but remains isolated from canonical 1-221-5 until explicitly compared and approved.')
$summary | Set-Content -LiteralPath $TxtOut -Encoding UTF8

Write-Host ''
Write-Host 'AUDITORIA CONCLUIDA (READ-ONLY).' -ForegroundColor Green
Write-Host "JSON: $JsonOut"
Write-Host "CSV : $CsvOut"
Write-Host "TXT : $TxtOut"
Write-Host "Registros: $($records.Count) | grupos duplicados: $($duplicateGroups.Count)"
