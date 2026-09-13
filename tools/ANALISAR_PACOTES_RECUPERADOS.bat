@echo off
setlocal
cd /d "%~dp0\.."
python "%~dp0ANALISAR_PACOTES_RECUPERADOS.py"
exit /b %errorlevel%
