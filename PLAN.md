# Gusen – Rebuild Plan

Status: **draft for approval**. Nothing has been rebuilt yet.

---

## 1. What's in the repo now (art analysis)

The art is in two styles. Both need to fit in one game.

### A. The Gusen creatures (`*.png`, 12×30 = two stacked 12×15 frames)
`player, npc1, npc2, sprite–sprite5, dinggusen, gressgusen, lanternegusen, lunagusen, spaghettigusen, wirelessgusen, generatorgusen`

- Solid **black silhouettes** (`#000000`) with **two 1-px white eyes** (`#ffffff`) and **red glow accents** (`#ff0000`, dark reds `#930000 #460000 #2b0000 #170000`).
- The two frames are an **idle/step animation**, not left/right facing (for example the antenna dot moves, or `sprite2` changes leg pose). Most are symmetric, so facing can be done by mirroring.
- **Not pixel-clean:** `generatorgusen.png` has 22 semi-transparent pixels (alpha 3–247). These will be snapped to fully on or off.

### B. World & items (`*.ase`, Aseprite, animated)
| File | Size | Frames (ms) | Palette notes |
|---|---|---|---|
| Terreng Gress og sorpe | 32×32 | 1 | 10 colors, greens `#14a02e #1a7a3e #24523b` + dirt `#5b3138 #422433 #242234`. **Tiles seamlessly.** Identical to `Terreng_Gress.png`. |
| Penge (coin) | 12×15 | 3 × 200, tag `Loop` | `#fffc40 #ffd541 #f9a31b`. No outline |
| Bouncy Ball Frog | 12×15 | 300/150/300, tag `Loop` | Black outline, saturated greens `#51ff00 #7bff30 #008300` |
| Blåse ut lys (candle) | 12×15 | 4 × 500 | DB32 palette, outline `#222034` |
| Fluesopp med sporer | 12×15 | 2 × 500 | DB32 reds + spores `#9badb7` |
| Eksploderende Mikrobølgeovn | 12×15 | 500/100/300 | Black / yellow / red |
| Glødende Sverd | 16×16 | 2 × 100 | Black blade, greys, red glow |
| Vind i gress | 12×15 | 2 × 500 | 2 colors `#4b692f #323c39` |
| Voksende rød blomst | 32×32 | 7 × 1000 | Terrain greens + reds `#df3e23 #b4202a #73172d` |

### Excluded
- **All `.jpg` files**: excluded, as you asked.
- **`Left/Middle/Right_Grass_Platform.png`**: 117–134 colors of blurry noise per 12×15 tile. They look resampled and don't match the rest. I'll replace them with new platform art made from the terrain palette.
- **`sword.png`**: replaced by `Glødende Sverd.ase`, which is the same sword drawn more cleanly.

### Takeaways that drive the style guide
1. The canonical sizes are yours: **12×15** for characters and items, **16×16** for weapons, **32×32** for terrain and large props.
2. Nearly every color comes from **DB32** (Aseprite's default palette) plus the green/dirt/gold set in the terrain, flower and coin files. I'll build **one master palette** from these colors, and every new asset must use only colors from it.
3. Outlines are black or `#222034`. There's no anti-aliasing, and everything is readable at 1×.

## 2. Pixel-perfect rules (the core of the rebuild)
- **Render at 320×180 logical pixels**, then scale the whole canvas up by a **whole-number factor** (×4 = 1280×720, or the largest factor that fits the window). Smoothing stays off.
- **All draw positions are rounded to whole pixels**, camera included. Nothing lands on a half-pixel.
- **No rotation or fractional scaling at runtime.** The old game rotated the sword with `ctx.rotate`, which smears pixels. Swings will be hand-drawn frames instead.
- **Text uses a pixel font** (a bitmap font I'll draw, with Æ Ø Å) instead of browser fonts, which blur at low resolution.
- **A validator script** (`tools/check_art.py`) fails if any sprite has partial alpha, an off-palette color, or a non-standard size.

## 3. Architecture (from scratch, no build step)
You'll still run it with `python3 -m http.server`.
```
index.html
src/
  main.js       fixed-timestep loop (60 updates/s regardless of monitor Hz; the old game ran 2× speed on 120 Hz screens)
  screen.js     320×180 canvas, integer scaling, camera snapping
  aseprite.js   loads .ase files directly in the browser: frames, durations, tags
  assets.js     asset manifest
  input.js      keyboard (+ gamepad later)
  physics.js    tile-grid collision, one-way platforms, coyote time, jump buffering
  entities/     player, gusen enemies, frog, mushroom, microwave, pickups, checkpoint, goal
  levels/       levels as ASCII text maps (easy for you to edit by hand)
  ui.js font.js hearts, coin counter, pause/title/game-over screens
art/            your source files (.ase/.png), unchanged, plus my new .ase files
tools/          art validator and generator scripts
```
**Loading `.ase` directly:** save in Aseprite, refresh the browser, and the new art is in the game. Frame timings and tags (for example your `Loop` tags) come straight from the file.

**My new assets will also be `.ase` files**, so you can open and edit them in Aseprite like your own.

## 4. How your art becomes gameplay
| Asset | Role |
|---|---|
| `player.png` | Player. Idle uses its 2 frames. I'll add run/jump/fall/land frames |
| Other 13 Gusen | Enemies with different behaviors (walker, hopper, flyer, patroller), assigned per sprite |
| Terreng Gress og sorpe | Main ground tile, textured by world position so any ground width tiles cleanly |
| Penge | Coins (spinning loop) |
| Glødende Sverd | Sword attack. The glow frame shows while the attack is ready |
| Bouncy Ball Frog | Hopping enemy. Stomp it, or bounce off it for a high jump |
| Fluesopp med sporer | Hazard that puffs damaging spores every few seconds |
| Eksploderende Mikrobølgeovn | Trap that explodes when you come close. Run away! |
| Blåse ut lys | Checkpoint. Its frames play in reverse when lit (smoke → flame) |
| Voksende rød blomst | Level goal. It grows and blooms when you reach it |
| Vind i gress | Animated grass tufts scattered on the ground as decoration |

Decoration (grass, flowers, bushes) is scattered with a **fixed random seed**. That gives the "random placement" you asked for earlier, but the level looks the same on every load and nothing lands inside a wall.

## 5. New assets I'll draw (same palette, same sizes)
**Needed for the first playable version**
1. Terrain: dirt-only fill tile, left and right grass edge caps, a 3-piece one-way ledge (to replace the blurry Left/Middle/Right tiles).
2. Player frames: run (2), jump, fall, land squash. All black silhouette with 2-px eyes.
3. Sword slash: 3–4 frame arc in the sword's black/grey/red palette.
4. UI: heart full/empty, pixel font, coin icon (from Penge frame 1).
5. Effects: dust puff, coin sparkle, spore cloud, hit flash, enemy "poof".
6. Background: sky in DB32 blue bands, 2 parallax tree-line layers in dark terrain greens, 2 clouds.

**Nice-to-have**
Forest props (bush, dark tree, stones, mushrooms) drawn from scratch to replace the excluded JPGs, a squashed-frog frame, and a title-screen logo "GUSEN".

## 6. Build order (each step ends with a screenshot check)
1. **Foundation**: canvas, scaling, loop, `.ase` loader, validator. Check that all your assets render 1:1 on a test screen.
2. **Movement**: player physics, tile collision, camera, ground/ledge tiles. Tune jump feel.
3. **Art pass 1**: terrain pieces, player frames, UI and font.
4. **Gameplay**: enemies, sword, coins, hazards, checkpoints, goal flower, health, death/respawn.
5. **Level**: one full forest level (sized to about the old 6400 px world, adjusted for the new scale), plus decoration scatter.
6. **Polish**: parallax, effects, title/pause/win screens, simple sound, updated README.

Old `game.html` gets removed once the new version plays better. It stays in git history either way.

**Verification:** I'll try to install headless Chromium (Playwright) so I can screenshot the game at each step. If this environment blocks that, I'll tell you and verify with rendered asset sheets plus logic tests instead.

## 7. Questions for you
1. **Gusen = enemies?** In the current game they're enemies you slash. Or are they friends you rescue or collect? This changes the whole feel.
2. **Frame layout:** is my reading right that the 2 frames in each Gusen PNG are an animation, not left-facing/right-facing?
3. **Palette:** should new art use the full DB32 + terrain colors, or stay tighter (say, terrain + black/red only)?
4. **Can I move your files into `art/`?** Names stay unchanged.
5. **Norwegian or English** for in-game text?
