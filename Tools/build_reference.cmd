@echo off
setlocal
set "FOOTBALL_ROOT=%~dp0.."
set "FOOTBALL_VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%FOOTBALL_VSWHERE%" exit /b 2
for /f "usebackq tokens=*" %%i in (`"%FOOTBALL_VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "FOOTBALL_VS=%%i"
if not defined FOOTBALL_VS exit /b 3
call "%FOOTBALL_VS%\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b %errorlevel%
if not exist "%FOOTBALL_ROOT%\.local\build\reference" mkdir "%FOOTBALL_ROOT%\.local\build\reference"
pushd "%FOOTBALL_ROOT%\.local\build\reference"
cl /nologo /std:c++17 /EHsc /W4 /WX /permissive- /Fe:FootballReferenceTests.exe "%FOOTBALL_ROOT%\Tests\physics_reference_tests.cpp" "%FOOTBALL_ROOT%\Reference\FootballCore\FixedPoint.cpp" "%FOOTBALL_ROOT%\Reference\FootballSimulation\BallContact.cpp" "%FOOTBALL_ROOT%\Reference\FootballSimulation\MatchSimulation.cpp" "%FOOTBALL_ROOT%\Reference\FootballGameplay\PlayableMatch.cpp"
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /permissive- /Fe:RecoveredKernelProbe.exe "%FOOTBALL_ROOT%\Tests\recovered_kernel_probe.cpp"
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /permissive- /Fe:SpmoveBranchesProbe.exe "%FOOTBALL_ROOT%\Tests\spmove_branches_probe.cpp"
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /permissive- /Fe:SpmoveSelectionProbe.exe "%FOOTBALL_ROOT%\Tests\spmove_selection_probe.cpp"
if errorlevel 1 exit /b %errorlevel%
cl /nologo /std:c++17 /EHsc /W4 /WX /permissive- /Fe:SpmoveProducerProbe.exe "%FOOTBALL_ROOT%\Tests\spmove_producer_probe.cpp"
if errorlevel 1 exit /b %errorlevel%
FootballReferenceTests.exe
set "FOOTBALL_RESULT=%errorlevel%"
popd
exit /b %FOOTBALL_RESULT%
