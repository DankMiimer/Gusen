# Gusen

A small top-down adventure in the style of a GBA game, made with **LÖVE 11.5**
for **PortMaster on the Anbernic RG34XXSP**. The game renders at 240×160, and
the RG34XXSP's 720×480 screen shows it at exactly ×3.

![Gusenby](docs/img/mockup_gameplay_x4.png)

* **[PLAN.md](PLAN.md)**: analysis of the old game, the design, tech,
  milestones and status
* **[docs/ART_GUIDE.md](docs/ART_GUIDE.md)**: pixel-art rules, the asset
  catalogue, what's used from `Mega_Spritesheet.ase`

Status: **M0 (foundation) is playable**: title, village, forest, the inn,
two cave rooms, talking, Norwegian/English. Combat comes in M1.

## Play it on your PC first

1. Install **LÖVE 11.5** for Windows from <https://love2d.org> (the same
   version PortMaster uses on the handheld).
2. Get this repo into your game folder, e.g. `C:\Programmering\Spill\Gusen v1.0`
   (clone it, or *Code → Download ZIP* on GitHub and unzip).
3. Double-click **`Test on PC.bat`**.

Keyboard: arrows/WASD move, **Z** = A, **X** = B, **Enter** = Start,
**F11** = fullscreen. Any window size works; the game always scales by whole
numbers.

(Linux/macOS: `love game`.)

## Put it on the RG34XXSP

**Over the network (Windows):** with the handheld on Wi-Fi and network sharing
on, double-click **`Install to RG34XXSP.bat`**. It copies to
`\\GAMEBOY\share\roms\ports` (give it another path as an argument if yours
differs). Then open *Ports* on the handheld and start **Gusen**. Update the
game list if it doesn't show up yet.

**By hand / SD card:** put these in `roms/ports/`:

```
roms/ports/Gusen.sh        ← port/Gusen.sh
roms/ports/gusen/          ← everything in port/gusen/
roms/ports/gusen/gamedata/ ← everything in game/ (except game/tests/)
```

or run `python3 tools/package_port.py` and copy the contents of `dist/ports/`.

Needs PortMaster with its `love_11.5` runtime (current PortMaster has it). The
first start asks you to **press A**: that teaches the game which button is A
on your firmware. Settings and saves go in `roms/ports/gusen/saves/`. If it
doesn't start, `roms/ports/gusen/log.txt` says why.

## For development

| Task | Command |
|---|---|
| Rebuild all art (1x PNGs, `.ase` copies, manifest, previews) | `python3 tools/make_assets.py` (needs Pillow) |
| Scripted play-through with checks + screenshots | `GUSEN_AUTOTEST=tour love game` |
| Same, the way the handheld's GPU renders (OpenGL ES) | `LOVE_GRAPHICS_USE_OPENGLES=1 GUSEN_AUTOTEST=tour love game` |
| Build the PortMaster package | `python3 tools/package_port.py` → `dist/` |

Screenshots from tests land in LÖVE's save folder (`%APPDATA%\LOVE\gusen` on
Windows, `~/.local/share/love/gusen` on Linux).

`Gusen.sh` must keep LF line endings. `.gitattributes` takes care of that, even
on Windows.

## Folders

```
game/      the LÖVE game (becomes roms/ports/gusen/gamedata on the handheld)
port/      PortMaster launcher + port files
tools/     art generator, packaging
art/ase/   editable Aseprite copies of the generated sprites
docs/      art guide, mockups, screenshots
*.ase *.png (top level)   your original art: the generator reads these
```
