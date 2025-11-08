#!/bin/bash

# Gusen Platformer - Launcher for Anbernic RG34XXSP with Knulli
# This script launches the PyGame version of Gusen

GAME_DIR="$(dirname "$0")"
cd "$GAME_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found! Please install Python 3."
    exit 1
fi

# Check if pygame is installed
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing pygame..."
    pip3 install pygame
fi

# Launch the game
python3 gusen_game.py

exit 0
