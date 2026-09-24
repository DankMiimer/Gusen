# Gusen: guide for coding agents

Gusen is a top-down, GBA-style action-adventure written in **LÖVE 11.5 (Lua)**
for **PortMaster on the Anbernic RG34XXSP**. The owner (GitHub: DankMiimer)
draws the pixel art in Aseprite and tests on the handheld. Read this file
first, then `docs/HANDOFF.md` (where things stand, what's next), then
`PLAN.md` (design + milestones) as needed.

## Hard rules

1. **Only target: PortMaster's `love_11.5` runtime on the RG34XXSP**
   (720×480 = exactly 3 × 240×160, Allwinner H700, Mali-G31 → OpenGL ES).
   * Lua 5.1 / LuaJIT syntax only: no `goto`, no `//`, no bitwise operators,
     no Lua 5.3 `utf8` functions beyond LÖVE's `require("utf8")`.
   * No shaders unless verified under `--gles`. Keep draw calls low
     (sprite batches for ground tiles; cull off-screen objects).
2. **Pixel perfect, GBA look.** Everything renders to the 240×160 canvas; the
   canvas is scaled by a whole number. Never rotate or non-integer-scale a
   sprite, never smooth-filter. Positions are floored when drawn. The only
   partial alpha allowed: the drop shadow and full-screen fades.
3. **Art rules** (details: `docs/ART_GUIDE.md`):
   * New art is authored **at 1x** in `tools/art_*.py` as ASCII against the
     master palette (`tools/pixel.py`: AAP-64 + "Gusen ink" = 74 colours),
     with **≤ 15 colours per sprite/tile** (GBA 4bpp). The build fails
     otherwise.
   * Gusens: pure `#000000` silhouettes, 1-px white eyes (facing shown only by
     eye position), red glow ramp. Nature: dark same-hue outlines. Creatures
     and items: black outlines. Props: `#221c1a`. Light from the top-left.
   * **Never edit the owner's originals** (the `.ase`/`.png` files in the repo
     root). The generator reads them.
   * **Never use the `.jpg` files** (owner's request; they're lossy anyway).
   * `Mega_Spritesheet.ase`: only the curated picks in `tools/art_mega.py`
     (`PICKS`). The owner said "don't use everything, choose wisely", then
     asked to include the **cobblestone and the tables**. `SKIPPED` lists the
     rest and why. Pixels are copied exactly, never recoloured.
4. **All player-facing text goes in both `game/lang/no.lua` (Norwegian bokmål)
   and `game/lang/en.lua`, with the same keys.** The font has ASCII + ÆØÅæøå♥
   only (no curly quotes, no `·`, no arrows).
5. **Test every change:** `python tools/run_tests.py` and
   `python tools/run_tests.py --gles` must pass. New features get a scripted
   test in `game/tests/`. Look at the screenshots in `test-output/`: a passing
   test can still look wrong.
6. `port/Gusen.sh` must keep **LF** line endings (`.gitattributes` enforces
   it; `tools/deploy.py` refuses CRLF).
7. Don't commit `dist/` or `test-output/`. Regenerate assets with
   `tools/make_assets.py` instead of hand-editing files in `game/assets/`
   (they get overwritten).

## Commands

Use `python` on Windows and `python3` on Linux/macOS. Tools need Python 3.8+
and Pillow (`pip install -r requirements.txt`). The game needs LÖVE 11.5
(Windows: installs to `C:\Program Files\LOVE\`; `lovec.exe` is the console
build).

| What | Command |
|---|---|
| Run the game (PC) | `love game` · Windows: `"Test on PC.bat"` |
| All scripted tests (+ screenshots in `test-output/`) | `python tools/run_tests.py` (`-v` prints full reports) |
| One test | `python tools/run_tests.py smoke` |
| Tests the way the handheld renders | `python tools/run_tests.py --gles` |
| Rebuild all art, manifest, previews | `python tools/make_assets.py` |
| Build the PortMaster package → `dist/` | `python tools/package_port.py` |
| Copy to the RG34XXSP (`\\GAMEBOY\share\roms\ports`) | `python tools/deploy.py` (or `--ports <path>`) |
| Read the handheld's last run log | `python tools/deploy.py --log` |

Keyboard in the game: arrows/WASD, Z = A, X = B, Enter = Start, Tab = Select,
F11 = fullscreen.

## Repository map

```
game/                 LÖVE project = roms/ports/gusen/gamedata on the device
  main.lua conf.lua   fixed 60 Hz loop; conf picks fullscreen when GUSEN_DEVICE=1
  src/core/           screen (240x160 canvas, integer scale, fades), input (virtual
                      buttons + A/B calibration), settings, i18n, assets (manifest
                      sheets), anim, font, scenes (stack), autotest
  src/world/          map (load, autotile, collision, draw), autotile, props, npc,
                      player, overlays (interior wall caps)
  src/ui/             hud, dialog (9-slice, typewriter, pages)
  src/scenes/         boot (title/calibration/language), play, pause
  maps/               gusenby, skogen (areas) · kro, hule1, hule2 (rooms)
  lang/               no.lua, en.lua
  tests/              scripted tests (not shipped): smoke, tour; README
  assets/             GENERATED: PNGs + manifest.lua + ui/font.lua
port/                 Gusen.sh (PortMaster launcher), gusen/ (port.json, README, licences)
tools/                make_assets.py (+ art_tiles/chars/items/ui/mega.py, pixel.py,
                      aseprite.py, previews.py), run_tests.py, deploy.py, package_port.py
art/ase/              generated .ase copies with animation tags (for Aseprite)
docs/                 ART_GUIDE.md, HANDOFF.md, img/ (mockups, previews, screenshots)
*.ase *.png (root)    the owner's original art (read-only for us)
```

## How the game works

* **Loop:** `main.lua` accumulates `dt`, runs `tick()` at 60 Hz (max 4 catch-up
  steps): `autotest.step() → input.update() → scenes.update()`. Draw:
  `screen.begin() → scenes.draw() → screen.finish()`.
* **Scenes:** a stack (`src/core/scenes.lua`). The top updates, all draw.
  `boot` → `play` (+ `pause` pushed on top).
* **Input:** virtual buttons `up down left right a b l r start select`;
  `input.down/pressed/released[btn]`, `input.axis()`. The gamepad A/B come from
  `settings.data.pad` (learned on the title screen by "press A"). The left stick
  works as the d-pad.
* **Assets:** `assets.sheet(name)` uses the keys of `game/assets/manifest.lua`
  (e.g. `gusen_player`, `overworld`, `interior`, `candle`, `frog`,
  `gusen_npcs`). It returns `{image, quads, fw, fh, anims, tiles, ox, oy}`.
  `assets.drawFrame(sheet, frameIndex0, x, y, flip)` draws with the origin at
  (x, y). `Anim.new(sheet, "walk_down")` plays manifest animations (`ms` is a
  number or per-frame list; `loop = false` stops at the end).
* **Maps** (`game/maps/*.lua`) return:
  * `kind`: `"area"` (any size, camera follows, clamped) or `"room"` (exactly
    15×10, fixed camera)
  * `theme`: `"overworld"` | `"interior"` | `"cave"`
  * `rows`: ASCII ground
    * overworld: `.` grass, `,` red-flower grass, `;` yellow, `P` path
      (autotiled), `W` water (autotiled, animated, solid), `H` plateau
      (solid), `C` cliff face (solid; top/mid/base + ends automatic), `K` cave
      top (solid), `k` cave floor, `D` cliff with a door (walkable), `T` pine
      forest (solid + pine sprite)
    * interior/cave: `w` back wall (solid), `f`/`F` light/dark planks, `o`
      cobblestone, `X` void (solid)
  * `frame = {left, right, bottom, gaps = {tile columns}}`: interior wall caps
    + collision
  * `spawns = { name = {tx, ty, dx=, dy=, dir=} }`: feet at the bottom centre
    of that tile, plus the nudge
  * `exits = { east = {to=, spawn=, span={first, last tile}}, ... }`:
    `slide = true` for room→room slides, otherwise a fade
  * `objects`, positioned by tile (feet at the bottom centre) or `{"at", x, y, ...}` (top-left in pixels):
    * `{"npc", tx, ty, who=, dir=, talk=, name=}`
    * `{"door", tx, ty, w=, h=, to=, spawn=}`: trigger, and makes those tiles walkable
    * `{"cave", tx, ty}`
    * `{"tree", ...}`
    * `{"candle", ..., lit=false, talk=}`
    * `{"candle_dish", ...}`
    * `{"mega", ..., name=}`: any `game/assets/mega/*.png`
    * `{"legacy", ..., name=}`: an animated original sprite (frog, fluesopp, coin, …)
    * `{"sheet", ..., sheet=, anim=}`
    * a 16×16 atlas tile by name (`"bush"`, `"rock_big"`, `"sign"`, `"chest_closed"`, `"tallgrass_0"`, `"flowers_sway_0"`, `"pot"`, `"stump"`, `"fence"`)
    * common options: `talk` (text key), `solid` (`{w,h}` or `false`),
      `layer` (`"floor"`, `"wall"` or `"top"` for things lying on furniture), `flip`
* **Collision:** 8×5 foot box vs solid tiles, object `box`es and `rects`.
  `Player:slide` moves in ¼-px steps, and `Player:nudge` rounds corners. Map
  edges are solid except exits (within `span`).
* **Drawing order:** ground batches → water frame → wall caps → `floor`/`wall`
  layer objects → everything else sorted by feet `y` (`sorty` for things on
  furniture). HUD and dialog go on top.
* **Play scene** (`src/scenes/play.lua`):
  * `state = {hp, maxHp, coins, hasSword, bItem}`
  * `:startFade(map, spawn)`, `:startSlide(dir, map)`, `:say(textKey, nameKey)`
  * doors re-arm only after you step off them
* **Text:** `i18n.t(key)` returns a string or a list of pages. `font.print(text,
  x, y, "rrggbb", shadowHex, maxChars)`, `font.wrap(text, width)`.
* **Settings/saves:** `love.filesystem`, identity `gusen`. On the device that's
  `roms/ports/gusen/saves/love/gusen/`, because the launcher sets
  `XDG_DATA_HOME`.

## Recipes

* **New map:** add `game/maps/<name>.lua` (rooms are 15×10). Connect it with
  an `exit` or a `door` from an existing map. Add a step to `tests/tour.lua`
  that walks in and screenshots it.
* **New NPC / text:** an `{"npc", ...}` object plus `talk_<x>` and `name_<x>`
  keys in both lang files. NPCs from `sprites/gusen_npcs.png` have 4
  directions; others use `legacy/<who>.png` (left/right only).
* **New sprite / tile:** write it as ASCII in the right `tools/art_*.py`,
  register it in `tools/make_assets.py` (`save(...)` with frame size, origin,
  animations), run `python tools/make_assets.py`, then look at
  `docs/img/new_assets_x3.png`. The manifest updates by itself.
* **New test:** copy `game/tests/smoke.lua`. Steps are documented in
  `game/tests/README.md`.

## Device testing

You can't press the handheld's buttons. Deploy with `python tools/deploy.py`,
ask the owner to play, then read `python tools/deploy.py --log`. Things only
the device can confirm are listed in `docs/HANDOFF.md`. The handheld's share
is `\\GAMEBOY\share` (probably Knulli); it's reachable only from the owner's
network.

## Working with the owner

* Writes in English and gives short, direct instructions, sometimes mid-task.
  Follow them literally (examples: "dont use any of the .JPGs", "Dont use
  everything, choose wisely", "also use the cobblestone and the tables").
* Cares most about: pixel-perfect GBA look, using their own art, the game
  running well on the RG34XXSP.
* Game text: Norwegian and English. Names stay Norwegian (Gusenby, Skogen,
  Mørk hule, Lanterne-Gusen, Skyggegusen).
* Show results as screenshots (from `test-output/` or `docs/img/`), not just
  descriptions.
