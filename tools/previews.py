"""Preview sheets and 240x160 GBA mockups built only from real 1x assets."""
import os

from PIL import Image

import aseprite
import art_chars
import art_items
import art_tiles
import art_ui
from pixel import blank, flip_h, over, rgba, scale

SCREEN = (240, 160)
BG = "242234"


def _ase(root, name, frame=0):
    return aseprite.read(os.path.join(root, name))["frames"][frame][0]


def _png(root, name, box=None):
    im = Image.open(os.path.join(root, name)).convert("RGBA")
    return im.crop(box) if box else im


def _save(im, docs, name, k=4):
    os.makedirs(docs, exist_ok=True)
    scale(im, k).save(os.path.join(docs, name))


def _fill(w, h, c):
    return Image.new("RGBA", (w, h), rgba(c))


def _label(dst, x, y, text, color="ffffff"):
    art_ui.draw_text(dst, x, y, text, color=color, shadow="000000")


# --- tile map composition ------------------------------------------------
def _autotile_key(region, x, y):
    H, W = len(region), len(region[0])

    def r(xx, yy):
        xx, yy = min(max(xx, 0), W - 1), min(max(yy, 0), H - 1)
        return region[yy][xx]

    n, s, w, e = r(x, y - 1), r(x, y + 1), r(x - 1, y), r(x + 1, y)
    if not n and not w:
        return "nw"
    if not n and not e:
        return "ne"
    if not s and not w:
        return "sw"
    if not s and not e:
        return "se"
    if not n:
        return "n"
    if not s:
        return "s"
    if not w:
        return "w"
    if not e:
        return "e"
    if not r(x - 1, y - 1):
        return "inw"
    if not r(x + 1, y - 1):
        return "ine"
    if not r(x - 1, y + 1):
        return "isw"
    if not r(x + 1, y + 1):
        return "ise"
    return "c"


def compose_map(rows, water_frame=0):
    """rows: strings with '.' grass, 'H' plateau, 'C' cliff, 'P' path, 'W' water,
    'r'/'y' flower grass, 'K' cave (treated as cliff+path). One tile of margin all round."""
    H, W = len(rows), len(rows[0])
    t = art_tiles.all_tiles()
    path = dict(zip(art_tiles.AUTOTILE_ORDER, t["path"]))
    water = dict(zip(art_tiles.AUTOTILE_ORDER, t[f"water{water_frame}"]))
    cliff = art_tiles.cliff_tiles()
    pe = art_tiles.plateau_edges()
    im = blank(W * 16, H * 16)
    in_path = [[c in "PK" for c in row] for row in rows]
    in_water = [[c == "W" for c in row] for row in rows]
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            px, py = x * 16, y * 16
            g = art_tiles.GRASS[(x * 7 + y * 3 + (x * y) % 4) % 3]
            if c == ".":
                over(im, g, px, py)
            elif c == "r":
                over(im, art_tiles.GRASS_FLOWERS[0], px, py)
            elif c == "y":
                over(im, art_tiles.GRASS_FLOWERS[1], px, py)
            elif c == "P":
                over(im, path[_autotile_key(in_path, x, y)], px, py)
            elif c == "W":
                over(im, water[_autotile_key(in_water, x, y)], px, py)
            elif c == "H":
                east = x + 1 < W and rows[y][x + 1] != "H"
                west = x > 0 and rows[y][x - 1] != "H"
                over(im, pe[4] if east else pe[3] if west else g, px, py)
            elif c in "CK":
                top = y > 0 and rows[y - 1][x] == "H"
                r0 = 0 if top else 2
                left = x > 0 and rows[y][x - 1] not in "CK"
                right = x + 1 < W and rows[y][x + 1] not in "CK"
                col = 0 if left else 3 if right else 1 + (x % 2)
                over(im, cliff[r0 * 4 + col], px, py)
    return im


def _actor(dst, sprite, x, y, shadow=True):
    """Draw with the sprite's feet at (x, y)."""
    if shadow:
        over(dst, art_items.shadow(), x - 5, y - 2)
    over(dst, sprite, x - sprite.width // 2, y - sprite.height + 1)


# --- mockups -----------------------------------------------------------
GAME_MAP = [
    "HHHHHHHHHHH......",
    "HHHHHHHHHHH......",
    "HHHHHHHHHHH......",
    "CCCCCKKCCCC......",
    "CCCCCKKCCCC......",
    ".r...PP..........",
    "....rPP.....y....",
    ".....PPPPPPPPPPPP",
    "WWWW.PPPPPPPPPPPP",
    "WWWW.PP...y......",
    "WWWW.PP..........",
    "WWWW.PP..........",
]


def scene(root, made, variant="gameplay"):
    world = compose_map(GAME_MAP)
    player = made["player"]
    frame = lambda sh, i, w, h, cols: sh.crop(((i % cols) * w, (i // cols) * h, (i % cols) * w + w, (i // cols) * h + h))
    tile = lambda name: frame(made["atlas"], made["tile_names"][name], 16, 16, 16)

    over(world, made["cave"], 5 * 16, 3 * 16)
    # plateau trees + lower-ground tree
    over(world, made["tree"], 30, 6)
    over(world, made["tree"], 124, 2)
    over(world, made["tree"], 220, 30)
    # props and foliage
    over(world, tile("sign"), 8 * 16, 5 * 16)
    over(world, tile("chest_closed"), 12 * 16 + 4, 4 * 16 - 2)
    for cx in (11, 12, 13):
        over(world, tile("tallgrass_0"), cx * 16, 5 * 16)
    over(world, tile("tallgrass_0"), 11 * 16, 6 * 16)
    over(world, tile("tallgrass_cut"), 12 * 16, 6 * 16)
    over(world, tile("tallgrass_0"), 13 * 16, 6 * 16)
    over(world, tile("bush"), 15 * 16, 5 * 16)
    over(world, tile("rock_big"), 9 * 16, 9 * 16 + 2)
    over(world, tile("rock_small"), 10 * 16, 10 * 16)
    over(world, tile("flowers_sway_0"), 2 * 16, 6 * 16)
    over(world, tile("stump"), 15 * 16, 9 * 16)
    for fx in (12, 13, 14):
        over(world, tile("fence" if fx != 13 else "fence_post"), fx * 16, 10 * 16 + 6)
    # existing art straight from the user's .ase files
    candle = _ase(root, "Blåse ut lys_12x15.ase", 0)
    frog = _ase(root, "Bouncy Ball Frog_12x15.ase", 0)
    shroom = _ase(root, "Fluesopp med sporer_12x15.ase", 0)
    coins = [_ase(root, "Penge_12x15.ase", i) for i in range(3)]
    _actor(world, candle, 4 * 16 + 6, 5 * 16 + 12, shadow=False)
    _actor(world, candle, 7 * 16 + 10, 5 * 16 + 12, shadow=False)
    _actor(world, frog, 3 * 16 + 4, 7 * 16 + 10)
    _actor(world, shroom, 13 * 16 + 8, 9 * 16 + 14)
    over(world, made["spores"].crop((8, 0, 16, 8)), 13 * 16 + 12, 9 * 16)
    over(world, made["spores"].crop((0, 0, 8, 8)), 14 * 16 + 2, 9 * 16 + 4)
    over(world, coins[0], 12 * 16 + 1, 6 * 16 + 1)
    over(world, coins[1], 12 * 16 + 9, 6 * 16 + 3)
    over(world, made["leaves"].crop((16, 0, 32, 16)), 12 * 16, 5 * 16 + 8)
    over(world, frame(made["heart"], 0, 12, 15, 2), 15 * 16 + 2, 6 * 16 + 1)

    npc_row = art_chars.STANDARD_NPCS.index("lanternegusen")
    lantern_npc = frame(made["npcs"], npc_row * 4 + 0, 12, 15, 4)
    bat = frame(made["bat"], 1, 16, 16, 3)
    shadow_left = frame(made["shadow"], 2 * 3 + 0, 12, 15, 3)
    shadow_hit = frame(made["shadow"], 2 * 3 + 2, 12, 15, 3)

    if variant == "gameplay":
        _actor(world, lantern_npc, 9 * 16 + 8, 6 * 16 + 4)
        _actor(world, frame(player, 3 * 4 + 3, 12, 15, 4), 9 * 16 + 4, 8 * 16 + 8)       # attack right
        sword = frame(made["sword"], 5, 16, 16, 8)                                       # down-right, glowing
        over(world, sword, 9 * 16 + 6, 8 * 16 - 5)
        over(world, frame(made["slash"], 3 * 3 + 1, 24, 24, 3), 9 * 16 + 0, 7 * 16 + 8)
        over(world, made["dust"].crop((8, 0, 16, 8)), 8 * 16 + 8, 8 * 16 + 2)
        _actor(world, flip_h(shadow_hit), 10 * 16 + 14, 8 * 16 + 8)
        over(world, frame(made["hit"], 0, 12, 12, 2), 10 * 16 + 4, 7 * 16 + 12)
        _actor(world, shadow_left, 14 * 16 + 6, 7 * 16 + 14)
        over(world, art_items.shadow(), 12 * 16 + 3, 3 * 16 + 2)
        over(world, bat, 12 * 16, 1 * 16 + 12)
    else:
        _actor(world, lantern_npc, 7 * 16 + 12, 5 * 16 + 12)
        _actor(world, frame(player, 0, 12, 15, 4), 7 * 16 + 12, 7 * 16 + 6)              # "item get" pose
        lan = made["mega_lantern"]
        over(world, lan, 7 * 16 + 12 - lan.width // 2, 6 * 16 + 2)
        _actor(world, shadow_left, 14 * 16 + 6, 7 * 16 + 14)

    view = world.crop((16, 16, 16 + SCREEN[0], 16 + SCREEN[1]))
    hud(view, made, dialog=(variant == "dialog"))
    return view


def hud(v, made, dialog=False):
    hearts = [made_frame(made, "hearts", i) for i in range(3)]
    for i, k in enumerate([0, 0, 0, 1, 2]):
        over(v, hearts[k], 3 + i * 9, 3)
    a = art_ui.item_slot("A")
    b = art_ui.item_slot("B")
    over(a, made["sword"].crop((0, 0, 16, 16)), 2, 2)
    lan = made["mega_lantern"]
    over(b, lan, 2 + (16 - lan.width) // 2, 2 + (16 - lan.height) // 2)
    over(v, b, 194, 2)
    over(v, a, 216, 2)
    if not dialog:
        icon = made_frame(made, "icons", 0)
        over(v, icon, 4, 149)
        art_ui.draw_text(v, 14, 148, "042", shadow="000000")
    else:
        box = art_ui.nine_slice(art_ui.dialog_box_9slice(), 232, 50)
        over(v, box, 4, 106)
        art_ui.draw_text(v, 13, 111, "Lanterne-Gusen", color="ffd541")
        art_ui.draw_text(v, 13, 123, "The candles in the village are going\nout, one by one. Take my lantern!")
        _, arrows = art_ui.cursors()
        over(v, arrows[0], 222, 146)


def made_frame(made, key, i):
    if key == "hearts":
        return art_items.hud_hearts()[i]
    return art_items.hud_icons()[i]


def title(root, made):
    v = _fill(*SCREEN, "060608")
    # night sky bands + stars
    for y0, c in ((0, "060608"), (40, "141013"), (70, "242234"), (96, "403353")):
        over(v, _fill(240, 160 - y0, c), 0, y0)
    for (x, y) in [(12, 8), (40, 22), (77, 6), (130, 14), (170, 30), (205, 9), (228, 24), (98, 34),
                   (60, 50), (190, 58), (20, 62), (150, 52)]:
        v.putpixel((x, y), rgba("dae0ea" if (x + y) % 3 else "8b93af"))
    # rolling hills of plateau grass + ground strip
    for x in range(240):
        h = 112 + int(6 * __import__("math").sin(x / 23.0)) + int(3 * __import__("math").sin(x / 7.0))
        for y in range(h, 160):
            v.putpixel((x, y), rgba("122020" if y < h + 2 else "24523b"))
    for x in range(0, 240, 16):
        over(v, art_tiles.GRASS[(x // 16) % 3], x, 136)
        over(v, art_tiles.GRASS[(x // 16 + 1) % 3], x, 152)
    logo = scale(made["logo"], 2)
    over(v, logo, (240 - logo.width) // 2, 26)
    art_ui.draw_text(v, 90, 90, "PRESS START", color="ffffff", shadow="c50000")
    # the cast
    xs = [28, 52, 76, 100, 140, 164, 188, 212]
    for i, x in enumerate(xs):
        f = made["npcs"].crop((0, i * 15, 12, i * 15 + 15))
        _actor(v, f, x, 150)
    _actor(v, made["player"].crop((0, 0, 12, 15)), 120, 150)
    candle = _ase(root, "Blåse ut lys_12x15.ase", 0)
    _actor(v, candle, 120, 134, shadow=False)
    return v


# --- reference / catalogue sheets --------------------------------------------
def existing_reference(root):
    """What the game already has (JPGs deliberately excluded)."""
    v = _fill(276, 132, BG)
    y = 2
    _label(v, 2, y, "Gusen sprites 12x15 (L / R frames)")
    names = ["player", "npc1", "npc2", "dinggusen", "gressgusen", "lanternegusen", "lunagusen",
             "spaghettigusen", "wirelessgusen", "generatorgusen", "sprite", "sprite2", "sprite3", "sprite4"]
    for i, n in enumerate(names):
        im = _png(root, n + ".png")
        over(v, im, 2 + i * 14, y + 11)
    y = 46
    _label(v, 2, y, "Aseprite art")
    x = 2
    for name, nfr in [("Penge_12x15.ase", 3), ("Blåse ut lys_12x15.ase", 4), ("Bouncy Ball Frog_12x15.ase", 3),
                      ("Fluesopp med sporer_12x15.ase", 2), ("Eksploderende Mikrobølgeovn_12x15.ase", 3),
                      ("Vind i gress_12x15.ase", 2), ("Glødende Sverd_16x16.ase", 2)]:
        for i in range(nfr):
            f = _ase(root, name, i)
            over(v, f, x, y + 11)
            x += f.width + 1
        x += 4
    y = 76
    over(v, _ase(root, "Terreng Gress og sorpe.ase"), 2, y + 11)
    for i in range(7):
        over(v, _ase(root, "Voksende rød blomst_32x32.ase", i), 38 + i * 30, y + 11)
    _label(v, 2, y, "Terreng 32x32 + Voksende rød blomst 32x32")
    return v


def catalogue(made):
    v = _fill(256, 446, BG)
    _label(v, 2, 2, "Overworld tiles 16x16 (tiles/overworld.png)")
    over(v, made["atlas"], 0, 13)
    y = 13 + made["atlas"].height + 3
    _label(v, 2, y, "Objects")
    over(v, made["tree"], 2, y + 10)
    over(v, made["cave"], 38, y + 18)
    x = 74
    for key in ("heart", "key", "shard", "spaghetti"):
        over(v, made[key], x, y + 12)
        x += made[key].width + 4
    over(v, made["logo"], 74, y + 30)
    y += 54
    _label(v, 2, y, "Gusen player  /  Skyggegusen  /  NPC front+back")
    over(v, made["player"], 2, y + 10)
    over(v, made["shadow"], 56, y + 10)
    over(v, made["npcs"].crop((0, 0, 48, 60)), 96, y + 10)
    over(v, made["npcs"].crop((0, 60, 48, 120)), 146, y + 10)
    over(v, made["bat"], 198, y + 10)
    y += 74
    _label(v, 2, y, "Boss  /  sword  /  slash  /  fx")
    over(v, made["boss"], 2, y + 10)
    over(v, made["sword"], 2, y + 44)
    over(v, made["slash"].crop((0, 0, 72, 48)), 104, y + 10)
    over(v, made["slash"].crop((0, 48, 72, 96)), 178, y + 10)
    over(v, made["poof"], 104, y + 60)
    over(v, made["hit"], 170, y + 62)
    over(v, made["dust"], 196, y + 62)
    over(v, made["spores"], 222, y + 62)
    over(v, made["leaves"], 136, y + 44 + 34)
    y += 98
    _label(v, 2, y, "UI: font, dialog 9-slice, hearts, icons, slots")
    over(v, made["font"], 0, y + 10)
    return v


def labeled_atlas(made, k=4):
    """Atlas at 4x with every tile index printed on it (for Tiled / level data)."""
    big = scale(made["atlas"], k)
    for i in range(16 * (made["atlas"].height // 16)):
        x, y = (i % 16) * 16 * k, (i // 16) * 16 * k
        lab = blank(16, 8)
        art_ui.draw_text(lab, 0, -1, str(i), color="ffffff", shadow="000000")
        over(big, scale(lab, 2), x + 1, y + 1)
    return big


# --- interior: Spaghetti-Gusen's restaurant -------------------------------------
def interior_scene(root, made):
    m = made["mega"]
    ov = made["interior_overlays"]
    v = blank(*SCREEN)
    for ty in range(10):
        for tx in range(15):
            floor = m["cobble"] if (tx <= 3 and 2 <= ty <= 5) else m["floor_planks"]
            over(v, floor, tx * 16, ty * 16)
    for tx in range(15):
        over(v, ov["wall_top"], tx * 16, 0)
        over(v, ov["wall_bottom"], tx * 16, 16)
        if tx != 7:
            over(v, ov["front"], tx * 16, 9 * 16)
    for ty in range(10):
        over(v, ov["side_l"], 0, ty * 16)
        over(v, ov["side_r"], 14 * 16, ty * 16)
    # back wall
    over(v, m["window_view"], 150, 5)
    over(v, m["door"], 66, 3)
    # kitchen corner on cobblestone: worktable + counter
    over(v, m["cabinet"], 90, 13)
    over(v, m["table_big_wood"], 6, 30)
    over(v, m["roast"], 12, 36)
    over(v, m["salad"], 18, 52)
    over(v, art_items.spaghetti_pickup(), 34, 32)
    over(v, m["stand_candle"], 124, 14)
    over(v, m["bookshelf"], 170, 13)
    over(v, m["nightstand"], 218, 13)
    over(v, m["potted_plant"], 156, 22)
    # dining room: the big table + stools, small cloth tables on the right
    over(v, m["table_big"], 97, 64)
    for (x, y) in [(84, 72), (84, 92), (144, 72), (144, 92)]:
        over(v, m["stool"], x, y)
    over(v, m["chair"], 113, 50)
    over(v, m["cupcakes"], 104, 72)
    over(v, m["fruit_bowl"], 121, 80)
    over(v, m["candle_dish"][0], 108, 88)
    over(v, m["table_red"], 186, 64)
    over(v, m["table_green"], 186, 100)
    over(v, m["table_square"], 212, 82)
    for (x, y) in [(172, 66), (202, 66), (172, 102), (202, 102)]:
        over(v, m["stool"], x, y)
    over(v, m["candle_dish"][0], 187, 60)
    # shop display in front of the kitchen, prices underneath
    for i, (item, price) in enumerate([("roast", "20"), ("salad", "10"), ("cupcakes", "5")]):
        x = 10 + i * 22
        over(v, m["side_table2"], x + 2, 110)
        it = m[item]
        over(v, it, x + 8 - it.width // 2, 106)
        art_ui.draw_text(v, x + 3, 127, price, color="ffd541", shadow="000000")
    over(v, m["rug"], 94, 144)
    over(v, m["basket"], 214, 124)
    # people
    spag = _png(root, "spaghettigusen.png", (0, 15, 12, 30))
    _actor(v, spag, 58, 78)
    luna = made["npcs"].crop((0, 5 * 15, 12, 6 * 15))
    _actor(v, luna, 219, 96)
    _actor(v, made["player"].crop((0, 15, 12, 30)), 36, 146)
    hud(v, made)
    return v


# --- Skogen: pines, logs, a cobblestone shrine with a blown-out candle ---------
FOREST_MAP = [
    ".................",
    ".................",
    ".................",
    "PPPPPP...........",
    "PPPPPP...........",
    "....PPPPPPPPP....",
    "....PPPPPPPPP....",
    "..........PP.....",
    "..........PP.....",
    "..........PPPPPPP",
    "..........PPPPPPP",
    ".................",
]


def forest_scene(root, made):
    m = made["mega"]
    world = compose_map(FOREST_MAP)
    tile = lambda name: made["atlas"].crop(((made["tile_names"][name] % 16) * 16, (made["tile_names"][name] // 16) * 16,
                                            (made["tile_names"][name] % 16) * 16 + 16,
                                            (made["tile_names"][name] // 16) * 16 + 16))
    # shrine clearing: cobblestone patch + the candle that was blown out
    over(world, m["cobble_patch"], 13 * 16 - 8, 3 * 16 + 6)
    _actor(world, _ase(root, "Blåse ut lys_12x15.ase", 3), 13 * 16 + 16, 4 * 16 + 20, shadow=False)
    # forest walls: pines overlapped back to front
    pines = []
    for row, y in enumerate(range(2, 70, 8)):
        for x in range(-8, 272, 12):
            x2 = x + (6 if row % 2 else 0)
            bottom = y + 16
            if x2 < 104 and bottom > 46:
                continue                   # path entrance on the left
            if x2 >= 104 and bottom > 78:
                continue                   # the path through the middle
            if 176 < x2 < 256 and bottom > 38:
                continue                   # the shrine clearing
            pines.append((x2, y))
    for (x, y) in [(16, 150), (28, 158), (40, 150), (4, 142), (52, 160), (64, 152), (76, 162), (88, 156),
                   (116, 150), (120, 168), (208, 110), (220, 118), (232, 108), (244, 116)]:
        pines.append((x, y))
    for (x, y) in sorted(pines, key=lambda p: p[1]):
        over(world, m["pine"], x, y)
    over(world, m["log"], 7 * 16 + 4, 7 * 16 + 4)
    for cx, cy in ((2, 7), (3, 7), (2, 8)):
        over(world, tile("tallgrass_0"), cx * 16, cy * 16)
    over(world, tile("tallgrass_cut"), 3 * 16, 8 * 16)
    over(world, m["white_flower"], 6 * 16 + 2, 9 * 16)
    over(world, m["white_flower"], 9 * 16 + 4, 4 * 16 + 4)
    shroom = _ase(root, "Fluesopp med sporer_12x15.ase", 1)
    _actor(world, shroom, 8 * 16 + 4, 9 * 16 + 12)
    over(world, made["spores"].crop((8, 0, 16, 8)), 8 * 16 + 8, 9 * 16 - 2)
    _actor(world, _ase(root, "Bouncy Ball Frog_12x15.ase", 2), 5 * 16 + 4, 8 * 16 + 10)
    coins = [_ase(root, "Penge_12x15.ase", i) for i in range(3)]
    over(world, coins[0], 10 * 16 + 2, 5 * 16 + 2)
    over(world, coins[2], 11 * 16 + 2, 5 * 16 + 2)
    # actors
    _actor(world, made["player"].crop((12, 45, 24, 60)), 7 * 16 + 4, 6 * 16 + 6)      # walking right
    over(world, made["dust"].crop((0, 0, 8, 8)), 6 * 16 + 8, 6 * 16)
    sh = made["shadow"]
    _actor(world, sh.crop((0, 30, 12, 45)), 12 * 16 + 8, 6 * 16 + 4)                    # facing left
    _actor(world, sh.crop((0, 45, 12, 60)), 12 * 16 + 2, 4 * 16 + 14)                    # guarding the shrine
    over(world, art_items.shadow(), 5 * 16 + 3, 6 * 16 + 14)
    over(world, made["bat"].crop((32, 0, 48, 16)), 5 * 16, 5 * 16 + 4)
    v = world.crop((16, 16, 16 + SCREEN[0], 16 + SCREEN[1]))
    hud(v, made)
    return v


def mega_sheet(made):
    """The curated picks, labelled, so the choice is visible at a glance."""
    import art_mega
    m = made["mega"]
    cards = []
    for name in list(art_mega.PICKS) + ["candle_dish"]:
        frs = m[name] if isinstance(m[name], list) else [m[name]]
        w = sum(f.width + 1 for f in frs) + 1
        lw = art_ui.text_width(name)
        c = _fill(max(w, lw + 2), max(f.height for f in frs) + 12, "14a02e")
        x = 1
        for f in frs:
            over(c, f, x, 11)
            x += f.width + 1
        _label(c, 1, 0, name)
        cards.append(c)
    W = 300
    x = y = rh = 0
    pos = []
    for c in cards:
        if x + c.width > W:
            x, y, rh = 0, y + rh + 2, 0
        pos.append((x, y))
        x += c.width + 2
        rh = max(rh, c.height)
    v = _fill(W, y + rh, BG)
    for c, p in zip(cards, pos):
        over(v, c, *p)
    return v


def build_all(made, root, docs):
    _save(scene(root, made, "gameplay"), docs, "mockup_gameplay_x4.png")
    scene(root, made, "gameplay").save(os.path.join(docs, "mockup_gameplay_1x.png"))
    _save(scene(root, made, "dialog"), docs, "mockup_dialog_x4.png")
    _save(title(root, made), docs, "mockup_title_x4.png")
    _save(existing_reference(root), docs, "existing_art_x4.png")
    _save(catalogue(made), docs, "new_assets_x3.png", k=3)
    labeled_atlas(made).save(os.path.join(docs, "tiles_labeled_x4.png"))
    _save(made["palette"], docs, "palette_x4.png")
    _save(interior_scene(root, made), docs, "mockup_interior_x4.png")
    _save(forest_scene(root, made), docs, "mockup_forest_x4.png")
    _save(mega_sheet(made), docs, "mega_picks_x3.png", k=3)
    labeled = scale(made["interior"], 4)
    labeled.save(os.path.join(docs, "tiles_interior_x4.png"))
