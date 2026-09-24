@echo off
rem Runs Gusen on this PC with LOVE 11.5 for Windows (https://love2d.org).
rem Same game code as on the RG34XXSP. Keyboard: arrows, Z = A, X = B, Enter = Start, F11 = fullscreen.
set "LOVE=C:\Program Files\LOVE\love.exe"
if not exist "%LOVE%" set "LOVE=C:\Program Files (x86)\LOVE\love.exe"
if not exist "%LOVE%" (
  echo Could not find love.exe. Install LOVE 11.5 from https://love2d.org and run this again.
  pause
  exit /b 1
)
start "" "%LOVE%" "%~dp0game"
