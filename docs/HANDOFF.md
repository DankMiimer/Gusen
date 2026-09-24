# Handoff: where Gusen stands

Written at the end of the first (cloud) session, for the next session, which
has local access to the owner's PC and the handheld. Rules and commands:
`AGENTS.md`. Design and milestones: `PLAN.md`.

## Where the code is

* GitHub `DankMiimer/Gusen`, branch **`claude/happy-thompson-fy2wde`**. No
  pull request yet; `main` still has the old platformer. Ask the owner
  whether to merge.
* The owner's local folder: `C:\Programmering\Spill\Gusen v1.0`. It may not
  be a git clone yet; if not, clone the repo there (or into it) and check out
  the branch.
* Handheld: Anbernic **RG34XXSP**, reachable as `\\GAMEBOY\share\roms\ports`.
  The owner had an older copy of the game in `roms\ports\Top down game` (the
  web version). It's unused by the new port and safe to ignore.

## What's done

1. **Analysis + plan** (`PLAN.md`): why the old `game.html` platformer was
   rebuilt, the design (top-down GBA adventure, candles as checkpoints,
   Skyggegusen enemies), milestones M0–M6.
2. **Art pipeline + assets** (`tools/`, `game/assets/`, `docs/ART_GUIDE.md`):
   * 1x pixel-perfect tiles, characters, items, effects and UI in the owner's
     style
   * 43 curated `Mega_Spritesheet.ase` pieces
   * the owner's originals exported unchanged to `game/assets/legacy/`
   * `.ase` copies with animation tags in `art/ase/`
   * mockups in `docs/img/`
3. **M0, the foundation** (`game/`): everything listed under *Status* in
   `PLAN.md`.
   * Maps: Gusenby and Skogen (scrolling areas), the inn and two cave rooms
     (single screens, sliding)
   * Movement and collision, talking, both languages, pause menu
4. **PortMaster port** (`port/`), Windows helpers (`Test on PC.bat`,
   `Install to RG34XXSP.bat`), and tools: `run_tests.py`, `deploy.py`,
   `package_port.py`.

### Verified (in the cloud, Linux + Xvfb + LÖVE 11.5)

* `smoke` and `tour` tests pass: 10 checks, in desktop GL and OpenGL ES mode,
  with pixel-identical output
* `port/Gusen.sh` ran end to end against a stand-in PortMaster: runtime found,
  device fullscreen mode, saves written to `gusen/saves/`, clean exit
* `deploy.py`: keeps device saves, clears stale files, never ships tests
* `make_assets.py` is deterministic (a rebuild changes no files) and every
  sprite passes the palette and 15-colour checks

### Not verified yet (needs the real RG34XXSP)

* [ ] It starts from *Ports*. PortMaster on the device has `runtimes/love_11.5`.
* [ ] "Press A" on the title picks the button labelled A (the calibration is
      there because firmwares disagree), and B works in menus.
* [ ] D-pad and left stick both move. The deadzone (0.5) feels right.
* [ ] Fullscreen is 720×480 with no borders: the game should fill the screen
      at ×3.
* [ ] 60 fps in Skogen, the map with the most objects (~300 pines).
* [ ] Start → *Quit* returns to the menu. Select + Start (gptokeyb hotkey)
      also exits.
* [ ] Settings survive a restart (`roms/ports/gusen/saves/love/gusen/settings.lua`).

If it doesn't start, read `python tools/deploy.py --log` (the handheld's
`gusen/log.txt`).

## Decisions (with the owner's words where it matters)

| When | Decision |
|---|---|
| Start | Rebuild into a real game; plan first. Keep the art pixel perfect at 1x and scale by whole numbers to look like a GBA game |
| Art | "dont use any of the .JPGs": the .jpg files are never used |
| Art | Mega sheet: "Dont use everything, choose wisely", then "also use the cobblestone and the tables". Curated list in `tools/art_mega.py` |
| Tech | **LÖVE**, text in **both** Norwegian and English, **both** single-screen rooms and big scrolling areas, retire the old version |
| Target | "only develop the game specifically to be runnable on PortMaster ARM devices (… rg34xxsp … the only device we test on)", and "you can test the game first before running it on the rg34xxsp" → PC tests first, then the device |

## Next: M1, combat feel

Goal: fighting 3 Skyggegusens in one room is fun for 2 minutes. Suggested
order, each with a test:

1. **Sword.** A swings when there's nothing to talk to (`Play:interact()`
   returns false).
   * **Timing:** 12 frames: 3 wind-up (player `attack_<dir>` frame), 6 active,
     3 recovery. No other cooldown.
   * **Visuals:** smear from `fx/slash.png` (`slash_<dir>`, 3 frames × 2
     steps). The sword from `fx/sword.png` uses diagonals only (flipped,
     never rotated).
   * **Hitbox:** ~16×14 in front of the player during the active frames.
   * **Cutting:** tall grass and bushes turn into their `_cut` tile and play
     `fx/leaves.png`. Drops: coin ~30%, heart ~10%.
2. **Pickups:** coin (`legacy/coin.png`, `spin`) +1 coin; heart
   (`items/heart.png`) +2 hp; shown in the HUD.
3. **Skyggegusen AI** (new `src/world/enemy.lua` + `skyggegusen.lua`):
   * **States:** wander → chase (sees you within ~64 px) → telegraph 0.4 s
     (`attack_<dir>` frame, horns) → lunge → rest.
   * **Stats:** 2 HP, speed 0.75 px/step, collides like the player.
   * **On hit:** 3-frame global hit-stop, 24 px knockback over 8 frames,
     white flash (swap to a flat-white copy of the frame; no shaders needed).
   * **Death:** `fx/poof.png`, drops a coin.
4. **Player damage:** touching an enemy costs ½ heart, knocks you back, and
   gives 60 i-frames of flicker (skip drawing every 4 frames).
5. **Death and candles:** at 0 hp, fade out and respawn at the last **lit
   candle** touched (candles become checkpoints; store map + spawn in
   `state`). Save progress to a file then (settings already do this).
6. **Content:** replace the static Skyggegusen props in `maps/skogen.lua` and
   `maps/hule2.lua` with live enemies; add 2–3 more in Skogen.
7. **Tests:** `tests/combat.lua`:
   * teleport next to an enemy, attack, expect its hp to drop and then death
   * walk into one, expect player hp down and i-frames set
   * cut grass, expect the tile to change

Then M2 (world systems: chests/keys/locked doors, pots, save/continue), then
M3 (vertical slice).

## Known issues / tech debt

* The cave rooms use the overworld cliff (with its grass lip) as walls. They
  need a proper cave tileset (M3 art backlog in `PLAN.md`).
* Legacy NPC sprites (e.g. Spaghetti-Gusen) only face left or right.
* Dialog quads are cached, but `font.print` splits UTF-8 every call. That's
  fine now; cache per string if profiling on the device says so.
* `Map:buildObjects` has grown a few shorthand branches. Tidy it when adding
  enemies.
* Art debt (M6): the owner's DB32 and free-picked-colour sprites and the Mega
  pieces aren't on the master palette. The Mega bookshelf has 30 colours.
  `generatorgusen.png` has ~20 half-transparent pixels. `player.png` is
  identical to `sprite5.png`.
* No audio yet (plan: jsfxr SFX, BeepBox/Furnace music).
* Rebuilding art with a different Pillow version can change PNG bytes but not
  pixels. Don't be alarmed by binary diffs in `game/assets/` after
  `make_assets.py`.

## Questions to ask the owner when relevant

* Merge the branch into `main`?
* After the device test: does the scale/feel look right? Is the text readable
  at 3.4"?
* House exteriors for Gusenby (roofs/walls): draw them yourself, or should the
  agent generate them in the same style?
