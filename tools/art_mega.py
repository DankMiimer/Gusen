"""Curated picks from Mega_Spritesheet.ase.

Only pieces with a clear job in the top-down game are extracted. The pixels are
copied exactly (no recolouring). Everything else is listed in SKIPPED with the
reason, so the choice is documented and easy to revisit.
"""
import os

import aseprite

# name: (box x0, y0, x1, y1), trim to content?, category, role in the game
PICKS = {
    # interiors ---------------------------------------------------------------
    "floor_planks":      ((128, 64, 144, 80), False, "interior", "house floor; tiles seamlessly"),
    "floor_planks_dark": ((128, 48, 144, 64), False, "interior", "cellar / Lanterne-Gusen's dark house"),
    "stool":             ((48, 92, 64, 112), True, "interior", "seating around tables"),
    "chair":             ((64, 90, 80, 112), True, "interior", "seating"),
    "armchair":          ((80, 90, 96, 112), True, "interior", "living corner (mirror in engine for the other side)"),
    "sofa":              ((128, 94, 176, 112), True, "interior", "living corner"),
    "nightstand":        ((48, 112, 64, 144), True, "interior", "against walls; can hide a key"),
    "dresser":           ((80, 112, 112, 144), True, "interior", "shop counter / bedroom"),
    "cabinet":           ((112, 112, 144, 144), True, "interior", "shop counter / kitchen"),
    "bookshelf":         ((144, 112, 176, 144), True, "interior", "Luna-Gusen's house; readable books = hints"),
    "table_big":         ((0, 96, 48, 144), True, "interior", "restaurant's shared dining table, food on top"),
    "table_big_wood":    ((0, 144, 48, 192), True, "interior", "kitchen worktable / village market stall top"),
    "table_pedestal":    ((96, 214, 129, 240), True, "interior", "Luna-Gusen's house / castle"),
    "table_small":       ((48, 144, 64, 160), True, "interior", "small table"),
    "table_red":         ((48, 160, 64, 176), True, "interior", "Spaghetti-Gusen's restaurant"),
    "table_red2":        ((64, 160, 80, 176), True, "interior", "Spaghetti-Gusen's restaurant"),
    "table_green":       ((48, 176, 64, 192), True, "interior", "Spaghetti-Gusen's restaurant"),
    "table_square":      ((64, 176, 80, 192), True, "interior", "Spaghetti-Gusen's restaurant"),
    "side_table":        ((80, 160, 96, 176), True, "interior", "shop display / next to armchair"),
    "side_table2":       ((80, 176, 96, 192), True, "interior", "shop display"),
    # stone ---------------------------------------------------------------------
    "cobble":            ((81, 59, 97, 75), False, "stone", "16x16 cobblestone tile (the texture repeats every 16px, so it tiles seamlessly): plazas, castle, cave floors"),
    "cobble_patch":      ((80, 48, 128, 80), True, "stone", "soft-edged cobble patch to drop on grass (shrine clearings, ruins)"),
    "stand_tall":        ((96, 168, 112, 192), True, "interior", "indoor candle stand, unlit"),
    "stand_candle":      ((112, 160, 128, 192), True, "interior", "indoor candle stand, lit = checkpoint"),
    "window_view":       ((68, 260, 92, 283), True, "interior", "back-wall window"),
    "door":              ((46, 260, 66, 289), True, "house", "house door (exterior and interior)"),
    "window_small":      ((144, 56, 160, 72), False, "house", "house exterior window"),
    "rug":               ((46, 289, 98, 304), True, "interior", "doormat / under tables"),
    "potted_plant":      ((144, 217, 156, 241), True, "interior", "decor"),
    "basket":            ((101, 272, 124, 304), True, "village", "breakable container (like pots)"),
    # items ---------------------------------------------------------------------
    "lantern":           ((129, 254, 142, 268), True, "item", "Lanterne-Gusen's lantern (key item; replaces the generated one)"),
    "wallet":            ((129, 242, 143, 252), True, "item", "wallet upgrade: carry more Penge"),
    "cupcakes":          ((97, 242, 111, 253), True, "food", "shop: heals 1/2 heart"),
    "salad":             ((100, 258, 128, 271), True, "food", "shop: heals 1 heart"),
    "roast":             ((111, 242, 128, 253), True, "food", "shop: heals 2 hearts"),
    "fruit_bowl":        ((128, 222, 145, 236), True, "food", "table decor / free snack"),
    # outdoors ---------------------------------------------------------------------
    "pine":              ((0, 240, 16, 256), False, "forest", "Skogen's tree; overlap in rows for dense forest walls"),
    "pine_trio":         ((6, 262, 42, 290), True, "forest", "ready-made cluster"),
    "log":               ((270, 64, 290, 91), True, "forest", "hollow log: something can hide inside"),
    "sunflower":         ((132, 32, 145, 48), True, "garden", "Gress-Gusen's garden"),
    "white_flower":      ((180, 20, 191, 37), True, "garden", "Gress-Gusen's garden"),
    # boss room ------------------------------------------------------------------
    "throne":            ((145, 252, 176, 289), True, "castle", "Skyggekongen's throne"),
}
# 4-frame "table candle blown out" animation (fixed 16x16 cells)
CANDLE_DISH = [(48 + i * 16, 192, 64 + i * 16, 208) for i in range(4)]

SKIPPED = [
    ("grass tiles, dirt decals, dirt-ring autotile, grass islands, hedge",
     "a second, more olive grass family: mixing it with the AAP-64 overworld grass on one screen clashes"),
    ("dirt patch with hole, dirt 32x32", "duplicates the new path autotile"),
    ("cave hole", "duplicates tiles/cave_mouth.png, which also fits into the cliff face"),
    ("TVs and TV desk", "low contrast at 1x; 44 colours for the desk"),
    ("aquarium", "37 colours (GBA limit is 15) and very busy; maybe later as a one-off after a colour pass"),
    ("pink loveseat", "20 colours and louder than the rest of the maroon furniture set"),
    ("narrow cabinet, round stool, sofa with plants",
     "near-duplicates of picked pieces; one of each is enough"),
    ("table candle, candle strip", "same animation as Blåse ut lys / the candle-dish pick"),
    ("cupcake plate, low bookshelf, second potted plant, 5 more sunflowers, second cobble patch (same texture)",
     "fine art, but no job in the first areas; easy to add later"),
    ("black 16x16 square, grass mat", "placeholders"),
]


def load(root):
    sheet = aseprite.read(os.path.join(root, "Mega_Spritesheet.ase"))["frames"][0][0]
    out = {}
    for name, (box, trim, _, _) in PICKS.items():
        im = sheet.crop(box)
        if trim:
            bb = im.getbbox()
            im = im.crop(bb)
        out[name] = im
    out["candle_dish"] = [sheet.crop(b) for b in CANDLE_DISH]
    return out
