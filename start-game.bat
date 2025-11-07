@echo off
REM Simple script to start the game with a local web server (Windows)

echo Starting Gusen Character Game...
echo ================================
echo.
echo The game will open at: http://localhost:8000/game.html
echo.
echo Press Ctrl+C to stop the server
echo.

REM Try to start Python server
python -m http.server 8000 2>nul || py -m http.server 8000 2>nul || (
    echo Error: Python is not installed. Please install Python to run the game.
    pause
    exit /b 1
)
