@echo off
setlocal
cd /d "%~dp0.."
py -3 "%CD%\Tools\disassemble_shoot_helpers.py"
if errorlevel 1 exit /b %errorlevel%
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%CD%\tools\PUBLICAR_INBOX_NO_GITHUB.ps1" -SourcePath "%CD%\.local\il2cpp\shoot_helper_disassembly.txt" -DestinationRoot "artifacts/native-recovery/shoot-helpers" -CommitMessage "Publish native shoot helper disassembly"
exit /b %errorlevel%
