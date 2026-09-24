@echo off
rem Copies Gusen to the RG34XXSP over the network.
rem Default target is your handheld's share; pass another ports folder as the first argument if needed.
set "PORTS=\\GAMEBOY\share\roms\ports"
if not "%~1"=="" set "PORTS=%~1"
if not exist "%PORTS%\" (
  echo Can not reach %PORTS%
  echo Is the handheld on, on Wi-Fi, with network sharing enabled?
  pause
  exit /b 1
)
echo Copying Gusen to %PORTS% ...
copy /Y "%~dp0port\Gusen.sh" "%PORTS%\Gusen.sh" >nul
if errorlevel 1 goto fail
robocopy "%~dp0port\gusen" "%PORTS%\gusen" /E /NFL /NDL /NJH /NJS >nul
if errorlevel 8 goto fail
robocopy "%~dp0game" "%PORTS%\gusen\gamedata" /MIR /XD tests /NFL /NDL /NJH /NJS >nul
if errorlevel 8 goto fail
echo Done. On the RG34XXSP open Ports and start Gusen (update the game list if it is not there yet).
pause
exit /b 0
:fail
echo Copying failed. Nothing on the handheld was deleted except old game files inside gusen\gamedata.
pause
exit /b 1
