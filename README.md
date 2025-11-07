# Gusen Platformer Game 🎮

A fun 2D sidescrolling platformer with sprite-based characters, smooth camera following, and 2-frame directional animations!

## Features

- **Sidescrolling Camera**: Smooth camera that follows the player through a large 3200px world
- **Platformer Physics**: Full gravity, jumping, and collision detection with balanced movement speed
- **Complex Level Design**: 40+ platforms creating challenging jumps, tall towers, and precision platforming
- **Animated Characters**: All characters use 2-frame directional sprite animations (frames split horizontally)
- **Player Control**: Precise run and jump mechanics through multiple platform sections
- **AI NPCs**: 12 unique characters that walk, jump, and explore platforms autonomously throughout the level
- **Score System**: Earn points by meeting other characters scattered across the world
- **Beautiful Graphics**: Pixel-art style characters with smooth animations
- **Parallax Clouds**: Background clouds with depth effect that move slower than the camera
- **Multi-section Platforming**: Tutorial area, stepping stones, tall tower climb, long jumps, and final descent

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
1. Navigate through a large sidescrolling world with the camera following you
2. Jump across platforms and gaps to progress through different sections:
   - Starting tutorial area with easy jumps
   - Stepping stones over pits
   - Tall tower requiring precise climbing
   - Long jump challenges
   - High platform section with multi-level design
   - Final descending platforming to the end
3. Meet NPCs scattered throughout the level to earn points
4. Use momentum and timing to reach difficult platforms
5. Watch the NPCs as they autonomously explore and jump around!
6. The camera smoothly follows you as you explore the 3200px wide world

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
- Smooth camera system that follows the player (centered, bounded to world)
- Parallax scrolling clouds for depth effect
- Large 3200x600 pixel world with 40+ platforms
- Platformer physics with gravity (0.4), balanced jump power (-9), and slower movement speed (3px/frame)
- Directional sprite animation system with frame splitting
- Platform collision detection (top, bottom, and side collisions)
- AI-controlled NPCs with autonomous movement and jumping
- Responsive controls with multiple input options (arrows/WASD/Space)
- World position tracking in UI
