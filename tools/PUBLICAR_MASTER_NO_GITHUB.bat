@echo off
setlocal
cd /d "%~dp0"
set "GIT_CONFIG_COUNT=1"
set "GIT_CONFIG_KEY_0=credential.username"
set "GIT_CONFIG_VALUE_0=dgsiria71-jpg"
echo GitHub account requested: dgsiria71-jpg
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0PUBLICAR_MASTER_NO_GITHUB.ps1"
exit /b %errorlevel%
