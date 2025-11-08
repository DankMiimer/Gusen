# Gusen Platformer - Installation Guide for Anbernic RG34XXSP with Knulli

This guide will help you install and run the native PyGame version of Gusen on your Anbernic RG34XXSP running Knulli.

## Requirements

- Anbernic RG34XXSP handheld
- Knulli (Gladiator 2 or later)
- Python 3 with PyGame support
- microSD card with your Knulli installation

## Installation Methods

### Method 1: Direct Installation (Recommended)

1. **Copy game files to your device:**
   - Connect your Anbernic RG34XXSP to your computer via USB or remove the SD card
   - Navigate to `/roms/ports/` directory on your SD card
   - Create a new folder called `Gusen`
   - Copy all game files to `/roms/ports/Gusen/`:
     - `gusen_game.py` (main game file)
     - `launch.sh` (launcher script)
     - All PNG image files (player.png, npc1.png, sword.png, etc.)
     - Platform images (Left_Grass_Platform.png, etc.)

2. **Make the launcher executable:**
   ```bash
   chmod +x /roms/ports/Gusen/launch.sh
   ```

3. **Install dependencies (if needed):**
   - SSH into your device or use the terminal
   ```bash
   pip3 install pygame
   ```

4. **Launch from EmulationStation:**
   - Navigate to "Ports" in EmulationStation
   - Select "Gusen" and press A to launch

### Method 2: Via PortMaster (If Available)

If your Knulli installation has PortMaster installed:

1. Copy the entire `Gusen` folder to `/roms/ports/`
2. PortMaster should automatically detect it
3. Launch via PortMaster menu

## Controls for Anbernic RG34XXSP

The game is optimized for the Anbernic gamepad:

| Control | Action |
|---------|--------|
| **D-Pad Left** | Move Left |
| **D-Pad Right** | Move Right |
| **D-Pad Down** | Stomp Attack (while jumping) |
| **A Button** | Jump (press twice for double jump) |
| **B Button** | Sword Attack |
| **Start Button** | Quit Game |

Keyboard controls (if using USB keyboard):
- Arrow Keys or WASD: Movement
- Space/W/Up Arrow: Jump
- X: Sword Attack
- Down Arrow/S: Stomp
- ESC: Quit

## Display Settings

The game is configured for the RG34XXSP's 3:2 aspect ratio (640x480 resolution):
- Native 640x480 rendering
- Optimized sprite scaling for smaller screen
- Viewport culling for better performance

## Troubleshooting

### Game won't start
- Ensure Python 3 is installed on your Knulli system
- Check that pygame is installed: `python3 -c "import pygame"`
- Verify all PNG files are in the same directory as the game

### Performance issues
- The game is capped at 60 FPS
- If experiencing lag, close other applications
- Ensure your Knulli installation is up to date

### Graphics not loading
- Verify all .png image files are in the game directory
- Check file permissions (should be readable)

### Gamepad not working
- The game auto-detects the first connected gamepad
- Check that your gamepad is properly connected
- Try restarting the game

## Files Required

Make sure these files are in your Gusen directory:

**Required:**
- `gusen_game.py` - Main game executable
- `launch.sh` - Launcher script
- `player.png` - Player sprite

**Optional (for full experience):**
- `sword.png` - Sword weapon sprite
- `npc1.png`, `npc2.png` - Enemy sprites
- `sprite.png`, `sprite2.png`, `sprite3.png`, `sprite4.png`, `sprite5.png` - Character sprites
- `dinggusen.png`, `gressgusen.png`, `lanternegusen.png` - Special character sprites
- `lunagusen.png`, `spaghettigusen.png`, `wirelessgusen.png`, `generatorgusen.png`
- Platform graphics (optional - game will use colored rectangles if missing)

## Running from Command Line

If you want to run the game directly from SSH or terminal:

```bash
cd /roms/ports/Gusen
python3 gusen_game.py
```

Or use the launcher:

```bash
cd /roms/ports/Gusen
./launch.sh
```

## Features

This native PyGame version includes:
- ✅ Full gamepad support for Anbernic RG34XXSP
- ✅ Optimized for 3:2 aspect ratio (640x480)
- ✅ 60 FPS gameplay
- ✅ All original game mechanics (sword combat, double jump, stomp attack)
- ✅ Multiple enemy types (walking, flying, patrolling)
- ✅ Collectibles (coins and gems)
- ✅ Particle effects
- ✅ Multiple platform types (wood, crystal, metal, cloud)
- ✅ Lives system with invincibility frames
- ✅ Score tracking

## Credits

Original HTML5 game converted to native PyGame for handheld devices.
Optimized for Anbernic RG34XXSP running Knulli.

## Support

For issues or questions:
- Check the main README.md
- Report bugs on GitHub

Enjoy playing Gusen on your Anbernic handheld!
