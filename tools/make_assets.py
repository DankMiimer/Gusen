#!/usr/bin/env python3
"""Build every new Gusen asset from source (ASCII art + small generators).

    python3 tools/make_assets.py

Writes 1x pixel-perfect PNGs to assets/, editable .ase files to assets/ase/,
a manifest (assets/assets.json) and 4x previews + GBA mockups to docs/img/.
Nothing is ever resampled except by integer nearest-neighbour in previews.
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, os.path.dirname(__file__))

from PIL import ImageDraw  # noqa: E402

import aseprite  # noqa: E402
import art_chars  # noqa: E402
import art_items  # noqa: E402
import art_mega  # noqa: E402
import art_tiles  # noqa: E402
import art_ui  # noqa: E402
from pixel import AAP64, MASTER, blank, check_palette, colors_used, rgba, sheet  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "assets")
DOCS = os.path.join(ROOT, "docs", "img")
MANIFEST = {"_about": "Frames are numbered left-to-right, top-to-bottom. origin = the pixel "
                      "that sits on the ground / entity position. Render at 240x160 and only "
                      "ever scale by whole numbers.",
            "screen": [240, 160], "tile": 16, "palette": "palette/gusen-master.gpl", "assets": {}}


def existing(name):
    return aseprite.read(os.path.join(ROOT, name))


def save(rel, im, frame=None, anims=None, origin=None, ase=None, max_colors=15, per_tile=None, note=None,
         master=True):
    """Save a PNG (1x), validate its palette, optionally write .ase and a manifest entry.
    master=False: art copied from the Mega sheet keeps its own colours (only the count is checked)."""
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if per_tile:
        tw, th = per_tile
        for ty in range(0, im.height, th):
            for tx in range(0, im.width, tw):
                check_palette(f"{rel}@{tx},{ty}", im.crop((tx, ty, tx + tw, ty + th)), max_colors, master)
    elif max_colors:
        check_palette(rel, im, max_colors, master)
    im.save(path)
    entry = {"file": rel, "size": list(im.size)}
    if frame:
        entry["frame"] = list(frame)
        entry["frames"] = (im.width // frame[0]) * (im.height // frame[1])
    if origin:
        entry["origin"] = list(origin)
    if anims:
        entry["animations"] = anims
    if note:
        entry["note"] = note
    MANIFEST["assets"][os.path.splitext(os.path.basename(rel))[0]] = entry
    if ase and frame:
        fw, fh = frame
        cells = [im.crop((x, y, x + fw, y + fh))
                 for y in range(0, im.height, fh) for x in range(0, im.width, fw)]
        frames, durs, tags = [], [], []
        for name, a in (anims or {"all": {"frames": list(range(len(cells))), "ms": 100}}).items():
            start = len(frames)
            for i in a["frames"]:
                frames.append(cells[i])
                durs.append(a["ms"])
            tags.append((name, start, len(frames) - 1))
        ase_path = os.path.join(OUT, "ase", os.path.splitext(os.path.basename(rel))[0] + ".ase")
        os.makedirs(os.path.dirname(ase_path), exist_ok=True)
        aseprite.write(ase_path, frames, durs, tags=tags, palette=MASTER)
    return im


def four_dir(prefix, cols, per_dir, ms):
    """Animation table for sheets with one row per direction (down, up, left, right)."""
    anims = {}
    for r, d in enumerate(art_chars.DIRS):
        for name, idx in per_dir.items():
            anims[f"{name}_{d}"] = {"frames": [r * cols + i for i in idx], "ms": ms[name]}
    return anims


# ---------------------------------------------------------------------------
def build():
    made = {}

    # palette ---------------------------------------------------------------
    os.makedirs(os.path.join(OUT, "palette"), exist_ok=True)
    with open(os.path.join(OUT, "palette", "gusen-master.gpl"), "w") as f:
        f.write("GIMP Palette\nName: Gusen master (AAP-64 + Gusen ink)\nColumns: 8\n#\n")
        for i, c in enumerate(MASTER):
            r, g, b, _ = rgba(c)
            label = f"AAP-64 {i:02d}" if i < len(AAP64) else f"Gusen ink {i - len(AAP64)}"
            f.write(f"{r:3d} {g:3d} {b:3d}\t{label} #{c}\n")
    sw = blank(8 * 8, 8 * ((len(MASTER) + 7) // 8))
    d = ImageDraw.Draw(sw)
    for i, c in enumerate(MASTER):
        x, y = (i % 8) * 8, (i // 8) * 8
        d.rectangle((x, y, x + 7, y + 7), fill=rgba(c))
    sw.save(os.path.join(OUT, "palette", "gusen-master.png"))
    made["palette"] = sw

    # tiles -----------------------------------------------------------------
    t = art_tiles.all_tiles()
    fol = t["foliage"]  # tall grass x2, stub, bush, bush cut, rock, rock big, flowers x2
    rows = [
        t["grass"] + [fol[7], fol[8]] + fol[0:3] + fol[3:7],
        t["path"],
        t["water0"], t["water1"], t["water2"],
        t["cliff"][:16],                 # 12 cliff pieces + plateau nw, n, ne, w
        [t["cliff"][16]] + t["props"],    # plateau e + props
    ]
    cells = []
    for r in rows:
        r = r + [blank(16, 16)] * (16 - len(r))
        cells += r[:16]
    atlas = sheet(cells, 16)
    tile_names = {}
    names = (["grass_a", "grass_b", "grass_c", "grass_redflowers", "grass_yellowflowers",
              "flowers_sway_0", "flowers_sway_1", "tallgrass_0", "tallgrass_1", "tallgrass_cut",
              "bush", "bush_cut", "rock_small", "rock_big", None, None]
             + [f"path_{n}" for n in art_tiles.AUTOTILE_ORDER] + [None]
             + [f"water{f}_{n}" for f in range(3) for n in art_tiles.AUTOTILE_ORDER + ["_pad"]]
             + ["cliff_top_l", "cliff_top_m1", "cliff_top_m2", "cliff_top_r",
                "cliff_mid_l", "cliff_mid_m1", "cliff_mid_m2", "cliff_mid_r",
                "cliff_base_l", "cliff_base_m1", "cliff_base_m2", "cliff_base_r",
                "plateau_nw", "plateau_n", "plateau_ne", "plateau_w"]
             + ["plateau_e", "sign", "chest_closed", "chest_open", "pot", "fence", "fence_post", "stump"])
    for i, n in enumerate(names):
        if n and not n.endswith("__pad"):
            tile_names[n] = i
    save("tiles/overworld.png", atlas, frame=(16, 16), per_tile=(16, 16),
         anims={"water": {"frames": [tile_names["water0_c"], tile_names["water1_c"], tile_names["water2_c"]],
                          "ms": 250, "note": "every water tile animates: add 16*k to the index"},
                "flowers": {"frames": [5, 6], "ms": 500}, "tallgrass": {"frames": [7, 8], "ms": 500}},
         note="Autotile order per row: nw n ne inner-nw inner-ne / w c e inner-sw inner-se / sw s se c2 c3")
    MANIFEST["assets"]["overworld"]["tiles"] = tile_names
    made["atlas"] = atlas
    made["tile_names"] = tile_names
    made["tree"] = save("tiles/tree.png", art_tiles.tree(), origin=(16, 38))
    made["cave"] = save("tiles/cave_mouth.png", art_tiles.cave_mouth(), note="replaces 2x2 cliff tiles (top+mid rows)")

    # characters --------------------------------------------------------------
    walk = {"idle": [0], "walk": [1, 0, 2, 0], "attack": [3]}
    made["player"] = save("sprites/gusen_player.png", art_chars.player_sheet(), frame=(12, 15), origin=(6, 14),
                          anims=four_dir("", 4, walk, {"idle": 400, "walk": 120, "attack": 200}), ase=True)
    made["shadow"] = save("sprites/gusen_shadow.png", art_chars.shadow_sheet(), frame=(12, 15), origin=(6, 14),
                          anims=four_dir("", 3, {"walk": [0, 1], "attack": [2]}, {"walk": 180, "attack": 250}),
                          ase=True)
    made["bat"] = save("sprites/gusen_bat.png", sheet(art_chars.bat_frames(), 3), frame=(16, 16), origin=(8, 15),
                       anims={"fly": {"frames": [0, 1, 2, 1], "ms": 90}}, ase=True)
    made["boss"] = save("sprites/gusen_boss.png", sheet(art_chars.boss_frames(), 3), frame=(32, 32),
                        origin=(16, 31), anims={"idle": {"frames": [0, 1], "ms": 350},
                                                "telegraph": {"frames": [2], "ms": 600}}, ase=True)
    npcs, npc_names = art_chars.npc_sheet(ROOT)
    made["npcs"] = save("sprites/gusen_npcs.png", npcs, frame=(12, 15), origin=(6, 14),
                        anims={f"{n}_{d}": {"frames": [r * 4 + c], "ms": 0}
                               for r, n in enumerate(npc_names) for c, d in enumerate(art_chars.DIRS)},
                        ase=True, note="rows: " + ", ".join(npc_names))

    # items -------------------------------------------------------------------
    made["heart"] = save("items/heart.png", sheet(art_items.heart_pickup(), 2), frame=(12, 15), origin=(6, 13),
                         anims={"bob": {"frames": [0, 1], "ms": 300}}, ase=True)
    made["key"] = save("items/key.png", sheet(art_items.key_pickup(), 3), frame=(12, 15), origin=(6, 13),
                       anims={"shine": {"frames": [0, 1, 2], "ms": 200}}, ase=True)
    made["shard"] = save("items/shard.png", sheet(art_items.shard_pickup(), 3), frame=(12, 15), origin=(6, 13),
                         anims={"shine": {"frames": [0, 1, 2], "ms": 200}}, ase=True)
    made["spaghetti"] = save("items/spaghetti.png", art_items.spaghetti_pickup(), frame=(12, 15), origin=(6, 13))

    # weapon + fx -------------------------------------------------------------
    sword_src = [f for f, _ in existing("Glødende Sverd_16x16.ase")["frames"]]
    made["sword"] = save("fx/sword.png", sheet(art_items.sword_orientations(sword_src), 8), frame=(16, 16),
                         anims={"up_right": {"frames": [0, 1], "ms": 100}, "up_left": {"frames": [2, 3], "ms": 100},
                                "down_right": {"frames": [4, 5], "ms": 100},
                                "down_left": {"frames": [6, 7], "ms": 100}},
                         ase=True, note="Glodende Sverd remapped to the master palette; flips only, never rotated")
    made["slash"] = save("fx/slash.png", sheet(art_items.slash_arcs(), 3), frame=(24, 24), origin=(12, 12),
                         anims={f"slash_{d}": {"frames": [r * 3, r * 3 + 1, r * 3 + 2], "ms": 50}
                                for r, d in enumerate(art_chars.DIRS)}, ase=True)
    made["poof"] = save("fx/poof.png", sheet(art_items.poof(), 4), frame=(16, 16), origin=(8, 8),
                        anims={"poof": {"frames": [0, 1, 2, 3], "ms": 70}}, ase=True)
    made["hit"] = save("fx/hit.png", sheet(art_items.hit_spark(), 2), frame=(12, 12), origin=(6, 6),
                       anims={"hit": {"frames": [0, 1], "ms": 50}}, ase=True)
    made["dust"] = save("fx/dust.png", sheet(art_items.dust(), 3), frame=(8, 8), origin=(4, 6),
                        anims={"puff": {"frames": [0, 1, 2], "ms": 80}}, ase=True)
    made["leaves"] = save("fx/leaves.png", sheet(art_items.leaves(), 3), frame=(16, 16), origin=(8, 8),
                          anims={"cut": {"frames": [0, 1, 2], "ms": 80}}, ase=True)
    made["spores"] = save("fx/spores.png", sheet(art_items.spores(), 3), frame=(8, 8), origin=(4, 4),
                          anims={"drift": {"frames": [0, 1, 2], "ms": 150}}, ase=True)
    made["shadow_blob"] = save("fx/shadow.png", art_items.shadow(), origin=(5, 2), max_colors=None,
                               note="50% black, drawn under every actor (GBA alpha-blend layer)")

    # curated Mega_Spritesheet picks (pixels copied exactly) ------------------------
    mega = art_mega.load(ROOT)
    made["mega"] = mega
    for name, (box, _, cat, role) in art_mega.PICKS.items():
        im = mega[name]
        n = len(colors_used(im))
        note = f"{cat}: {role}. From Mega_Spritesheet.ase {list(box)}; {n} colours"
        if n > 15:
            note += " (over the GBA 15-colour limit: reduce in the palette pass)"
        save(f"mega/{name}.png", im, note=note, max_colors=None)
        MANIFEST["assets"][name]["category"] = cat
    save("mega/candle_dish.png", sheet(mega["candle_dish"], 4), frame=(16, 16), origin=(8, 15), max_colors=15,
         master=False, anims={"lit": {"frames": [0], "ms": 0}, "blow_out": {"frames": [0, 1, 2, 3], "ms": 500},
                              "relight": {"frames": [3, 2, 1, 0], "ms": 150}},
         note="indoor checkpoint candle (Mega sheet), same timing as Blåse ut lys")
    made["mega_lantern"] = mega["lantern"]

    # interior tiles: Mega floors + new walls in the furniture's maroon ------------
    it = art_tiles.interior_tiles(mega["floor_planks"])
    order = ["wall_top_l", "wall_top", "wall_top_r", "wall_bottom_l", "wall_bottom", "wall_bottom_r",
             "side_l", "side_r", "front_l", "front", "front_r", "void"]
    cells = [mega["floor_planks"], mega["floor_planks_dark"], mega["cobble"]] + [it[k] for k in order]
    interior = sheet(cells + [blank(16, 16)] * (16 - len(cells)), 16)
    save("tiles/interior.png", interior, frame=(16, 16), per_tile=(16, 16), master=False,
         note="side/front pieces are drawn on floor_planks; use art_tiles.interior_tiles() overlays for other floors")
    MANIFEST["assets"]["interior"]["tiles"] = {n: i for i, n in enumerate(
        ["floor_planks", "floor_planks_dark", "cobble"] + order)}
    made["interior_overlays"] = art_tiles.interior_tiles(None)
    made["interior"] = interior

    # ui ------------------------------------------------------------------------
    font, widths = art_ui.font_sheet()
    save("ui/font.png", font, frame=(art_ui.CELL_W, art_ui.CELL_H))
    with open(os.path.join(OUT, "ui", "font.json"), "w", encoding="utf8") as f:
        json.dump({"cell": [art_ui.CELL_W, art_ui.CELL_H], "columns": 16, "baseline": 7,
                   "line_height": art_ui.CELL_H + 1, "letter_spacing": 1,
                   "glyphs": {ch: {"index": i, "width": widths[ch]} for i, ch in enumerate(art_ui.ORDER)}},
                  f, ensure_ascii=False, indent=1)
    made["font"] = font
    save("ui/dialog_box.png", art_ui.dialog_box_9slice(), note="9-slice, 8px borders")
    save("ui/hearts.png", sheet(art_items.hud_hearts(), 3), frame=(8, 8), note="full, half, empty")
    save("ui/icons.png", sheet(art_items.hud_icons(), 3), frame=(8, 8), note="coin, key, shard")
    cur, arrows = art_ui.cursors()
    save("ui/cursor.png", cur)
    save("ui/more_arrow.png", sheet(arrows, 2), frame=(7, 6), anims={"bob": {"frames": [0, 1], "ms": 300}})
    save("ui/slot_a.png", art_ui.item_slot("A"))
    save("ui/slot_b.png", art_ui.item_slot("B"))
    made["logo"] = save("ui/logo.png", art_ui.logo())

    MANIFEST["mega_skipped"] = [{"what": w, "why": y} for w, y in art_mega.SKIPPED]
    with open(os.path.join(OUT, "assets.json"), "w", encoding="utf8") as f:
        json.dump(MANIFEST, f, indent=1, ensure_ascii=False)
    return made


if __name__ == "__main__":
    made = build()
    import previews
    previews.build_all(made, ROOT, DOCS)
    print(f"wrote {len(MANIFEST['assets'])} assets to {OUT}")
