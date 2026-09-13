@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0AUDITAR_ACERVO_LOCAL.ps1"
exit /b %errorlevel%
