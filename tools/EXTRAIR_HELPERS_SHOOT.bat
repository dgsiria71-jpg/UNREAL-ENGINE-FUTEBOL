@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set "ROOT=%CD%"
set "OUT=%ROOT%\.local\il2cpp\shoot_helper_disassembly.txt"
set "RC=1"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >nul 2>&1
    if not errorlevel 1 (
        echo [1/2] Extraindo helpers ARM64 com py -3...
        py -3 "%ROOT%\Tools\disassemble_shoot_helpers.py"
        set "RC=%ERRORLEVEL%"
        goto :after_extract
    )
)

where python >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python 3 nao foi encontrado. Instale Python 3 ou habilite o launcher py.
    exit /b 1
)
echo [1/2] Extraindo helpers ARM64 com python...
python "%ROOT%\Tools\disassemble_shoot_helpers.py"
set "RC=%ERRORLEVEL%"

:after_extract
if not "%RC%"=="0" exit /b %RC%
if not exist "%OUT%" (
    echo ERRO: o extrator terminou sem criar "%OUT%".
    exit /b 1
)

echo [2/2] Publicando o TXT no GitHub oficial...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\tools\PUBLICAR_INBOX_NO_GITHUB.ps1" -SourcePath "%OUT%" -DestinationRoot "artifacts/native-recovery/shoot-helpers" -CommitMessage "Publish native shoot helper disassembly"
exit /b %errorlevel%
