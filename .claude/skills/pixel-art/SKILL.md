---
name: pixel-art
description: Create or change Gusen's sprites, tiles, UI or effects in the owner's GBA pixel-art style. Use for any new or edited art asset, or when choosing art from the owner's files.
---

# Pixel art for Gusen

Read `docs/ART_GUIDE.md` first. The short version:

* Author at **1x** as ASCII in `tools/art_tiles.py`, `art_chars.py`,
  `art_items.py` or `art_ui.py`. `pixel.art(rows, key)` maps characters to
  hex colours, `pixel.frames(...)` handles side-by-side animation frames.
  Helpers in `tools/pixel.py`: `outline`, `flip_h/flip_v/rot90` (lossless),
  `recolor`, `sheet`; `art_tiles.shaded_blob` makes clumped foliage/rocks lit
  from the top-left.
* Colours: only the master palette (`tools/pixel.py` `MASTER`: AAP-64 +
  Gusen ink), **≤ 15 per sprite / per 16×16 tile**. `save()` in
  `tools/make_assets.py` enforces both.
* Style: Gusens are pure black silhouettes with 1-px white eyes and red glow
  accents; outlines are black for creatures/items, the darkest own shade for
  nature, `#221c1a` for props; light from the top-left; 3–5 flat shades, no
  dithering, no anti-aliasing. Sizes: tiles 16×16, characters 12×15, items
  12×15 or 8×8, screen 240×160.
* Register new art in `tools/make_assets.py` with frame size, origin (the pixel
  on the ground) and animations (ms per frame; follow the originals' timings).
  Then `python tools/make_assets.py` and look at `docs/img/new_assets_x3.png` /
  the mockups. Check it in the game via `/playtest`.
* The owner's files in the repo root are read-only sources. **Never use the
  .jpg files.** From `Mega_Spritesheet.ase` use `tools/art_mega.py` picks;
  adding a piece means adding it to `PICKS` with its job (pixels are copied,
  never recoloured).
* The owner draws in Aseprite: editable copies go to `art/ase/`. If the owner
  hand-edits a sprite, remove it from the generator so it isn't overwritten.
