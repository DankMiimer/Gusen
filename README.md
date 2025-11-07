# Gusen Platformer Game 🎮

A fun 2D sidescrolling platformer with sprite-based characters, smooth camera following, forest environment, and 2-frame directional animations!

## Features

- **Extended Sidescrolling World**: Massive 6400px world to explore with smooth camera following
- **Forest Environment**: Beautiful parallax forest background with trees, bushes, grass, and flowers
- **One-Way Platforms**: Jump through platforms from below for better movement flow
- **Platformer Physics**: Full gravity, jumping, and collision detection with balanced movement speed
- **Epic Level Design**: 70+ platforms across 9 distinct sections creating challenging jumps, tall towers, and precision platforming
- **Animated Characters**: All characters use 2-frame directional sprite animations (frames split horizontally)
- **Player Control**: Precise run and jump mechanics through multiple platform sections
- **AI NPCs**: 27 unique characters that walk, jump, and explore platforms autonomously throughout the level
- **Score System**: Earn points by meeting other characters scattered across the world
- **Beautiful Graphics**: Pixel-art style characters with smooth animations in a lush forest setting
- **Parallax Scrolling**: Multi-layer parallax for clouds, trees, and foliage creating depth
- **9 Epic Sections**: Tutorial, stepping stones, maze, tower climb, long jumps, high peaks, caves, multi-layer, and final descent

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
1. Navigate through a massive sidescrolling forest world with the camera following you
2. Jump through platforms from below - all platforms are one-way!
3. Explore 9 distinct sections across the 6400px world:
   - **Section 1**: Tutorial area with easy jumps (0-800px)
   - **Section 2**: Stepping stones over pits (800-1500px)
   - **Section 3**: Mid-level maze with multiple paths (1500-2200px)
   - **Section 4**: Tall tower climb requiring precise jumping (2200-2800px)
   - **Section 5**: Long jump challenge testing your timing (2800-3500px)
   - **Section 6**: High peaks with vertical exploration (3500-4200px)
   - **Section 7**: Cave-like platforming section (4200-4900px)
   - **Section 8**: Multi-layer platforming puzzles (4900-5600px)
   - **Section 9**: Final descent to the end (5600-6400px)
4. Meet 27 NPCs scattered throughout the forest to earn points
5. Use momentum and timing to reach difficult platforms
6. Enjoy the parallax forest background with trees, bushes, and flowers
7. Watch the NPCs as they autonomously explore and jump around!

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
- Multi-layer parallax scrolling:
  - Background trees (0.5x camera speed)
  - Foreground trees (0.8x camera speed)
  - Clouds (0.3x camera speed)
  - Bushes, grass, and flowers (1.0x camera speed)
- Massive 6400x600 pixel world with 70+ platforms across 9 sections
- One-way platform collision (can jump through from below)
- Platformer physics with gravity (0.4), balanced jump power (-9), and slower movement speed (3px/frame)
- Directional sprite animation system with frame splitting
- AI-controlled NPCs with autonomous movement and jumping
- 27 NPCs distributed across the entire world
- Responsive controls with multiple input options (arrows/WASD/Space)
- World position tracking in UI
- Forest environment rendering with trees, bushes, grass tufts, and colorful flowers
