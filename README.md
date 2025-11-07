# Gusen Platformer Game 🎮

A fun 2D sidescrolling platformer with sprite-based characters and 2-frame directional animations!

## Features

- **Platformer Physics**: Full gravity, jumping, and collision detection
- **Animated Characters**: All characters use 2-frame directional sprite animations (frames split horizontally)
- **Player Control**: Run and jump through multiple platforms
- **AI NPCs**: Characters that walk, jump, and explore the platforms autonomously
- **Score System**: Earn points by meeting other characters
- **Beautiful Graphics**: Pixel-art style characters with smooth animations
- **Multi-level Platforming**: Jump across various platforms at different heights

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

**Movement:**
- **Left Arrow** or **A** - Move left
- **Right Arrow** or **D** - Move right

**Jumping:**
- **Up Arrow**, **W**, or **Space** - Jump (only works when on ground or platform)

**Gameplay:**
1. Jump across platforms to explore the level
2. Meet NPCs to earn points
3. Use momentum to reach higher platforms
4. Watch the NPCs as they autonomously explore and jump around!

## Character Sprites

The game includes various character sprites:
- Player character
- NPCs (npc1, npc2)
- Special characters: Ding Gusen, Gress Gusen, Lanterne Gusen, Luna Gusen, Spaghetti Gusen, Wireless Gusen, Generator Gusen
- Additional sprites (sprite1-5)

All sprites use a 2-frame directional animation system where the image is split horizontally:
- **Top half** = Left movement animation
- **Bottom half** = Right movement animation

The game automatically switches between frames based on the character's horizontal movement direction.

## Technical Details

- Built with HTML5 Canvas
- Vanilla JavaScript (no external libraries)
- Platformer physics with gravity and jumping
- Directional sprite animation system with frame splitting
- Platform collision detection (top, bottom, and side collisions)
- AI pathfinding for NPCs
- Responsive controls with multiple input options
