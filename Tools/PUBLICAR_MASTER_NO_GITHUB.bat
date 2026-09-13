@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0PUBLICAR_MASTER_NO_GITHUB.ps1"
exit /b %errorlevel%
