# Gusen Character Game 🎮

A fun 2D character animation game using sprite-based characters with 2-frame animations!

## Features

- **Animated Characters**: All characters use 2-frame sprite animations (frames split horizontally)
- **Player Control**: Move your character around the map using arrow keys
- **NPCs**: Multiple AI-controlled characters roaming the world
- **Score System**: Earn points by interacting with other characters
- **Beautiful Graphics**: Pixel-art style characters with smooth animations

## How to Play

### Quick Start (Recommended)

**Option 1: Use the Start Script**

Linux/Mac:
```bash
./start-game.sh
```

Windows:
```cmd
start-game.bat
```

Then open your browser and go to: `http://localhost:8000/game.html`

**Option 2: Using Python directly**

```bash
# Python 3
python3 -m http.server 8000

# Or Python 2
python -m SimpleHTTPServer 8000
```

Then open: `http://localhost:8000/game.html`

**Option 3: Using Node.js**

```bash
npx http-server -p 8000
```

Then open: `http://localhost:8000/game.html`

> **Note:** Opening `game.html` directly (file://) won't work due to browser security restrictions (CORS). You must use a local web server.

### Game Controls

1. Use **Arrow Keys** (↑↓←→) or **WASD** to move your character
2. Explore the world and interact with NPCs to earn points
3. Try to meet all the different characters!

## Character Sprites

The game includes various character sprites:
- Player character
- NPCs (npc1, npc2)
- Special characters: Ding Gusen, Gress Gusen, Lanterne Gusen, Luna Gusen, Spaghetti Gusen, Wireless Gusen, Generator Gusen
- Additional sprites (sprite1-5)

All sprites use a 2-frame animation system where the image is split horizontally:
- Top half = Frame 1
- Bottom half = Frame 2

## Technical Details

- Built with HTML5 Canvas
- Vanilla JavaScript (no external libraries)
- Sprite animation system with frame splitting
- Simple collision detection
- Responsive controls
