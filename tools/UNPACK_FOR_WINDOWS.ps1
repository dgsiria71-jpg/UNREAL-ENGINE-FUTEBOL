param([string]$Destination = ".\FOOTBALL_RECOVERED_UNPACK")
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Write-Host "Use the normalized/reference packages in 01_RECOVERED_CORE and original archives in 00_SOURCE_ARCHIVES."
Write-Host "Do not edit 00_SOURCE_ARCHIVES in place. Copy/extract into your working tree."
