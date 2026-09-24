"""Gusen characters, 12x15 cells, in the style of player.png / npc*.png.

Style rules (from the existing Gusen sprites):
  * pure #000000 silhouette, no outline, no shading
  * eyes are single #ffffff pixels; facing is shown only by where they sit
  * red "glow" details use the Gusen ink ramp (#170000 .. #ff0000, #ffe3e3)
"""
import os
from PIL import Image
from pixel import *

INK = {"#": "000000", "o": "ffffff", "e": "170000", "d": "2b0000", "n": "460000",
       "r": "c50000", "R": "ff0000", "p": "ffe3e3"}
W, H = 12, 15
DIRS = ["down", "up", "left", "right"]

BODY = [
    "....####....",
    "..########..",
    ".##########.",
    "############",
    "############",
    "############",
    ".##########.",
]
EYES = {"down": (3, 8), "up": None, "left": (3, 7), "right": (4, 8)}

# legs, bottom-aligned to row 14. Walk frames have 3 rows because the body bobs up 1px.
LEGS_RIGHT = {
    "idle": ["..##...##...",
             "..###..###.."],
    "A":    [".##.....##..",
             ".###....##..",
             "........###."],
    "B":    ["...##..##...",
             "...##..###..",
             "...###......"],
    "atk":  [".##.....##..",
             ".###.....###"],
}
LEGS_FRONT = {
    "idle": ["...##..##...",
             "..###..###.."],
    "A":    ["...##..##...",
             "..###..##...",
             ".......###.."],
    "B":    ["...##..##...",
             "...##..###..",
             "..###......."],
    "atk":  [".###....###."],
}


def _mirror_rows(rows):
    return [r[::-1] for r in rows]


def legs_for(direction, pose):
    if direction == "right":
        return LEGS_RIGHT[pose]
    if direction == "left":
        return _mirror_rows(LEGS_RIGHT[pose])
    return LEGS_FRONT[pose]


def gusen(direction, pose="idle", eyes="white", head=None, face=None):
    """Build one 12x15 frame.

    head: rows drawn directly above the body (bottom-aligned to the body top).
    face: {(x, y_in_body): char} extra pixels on the body (y 0..6)."""
    grid = [["."] * W for _ in range(H)]
    legs = legs_for(direction, pose)
    body_bottom = H - 1 - len(legs)          # last body row
    top = body_bottom - (len(BODY) - 1)
    body = list(BODY)
    shift = 0
    if pose == "atk":
        shift = {"right": 1, "left": -1}.get(direction, 0)
    for i, row in enumerate(body):
        s = shift if i < 3 else 0             # lean: only the dome moves forward
        for x, ch in enumerate(row):
            xx = x + s
            if ch != "." and 0 <= xx < W:
                grid[top + i][xx] = ch
    for i, row in enumerate(legs):
        for x, ch in enumerate(row):
            if ch != ".":
                grid[body_bottom + 1 + i][x] = ch
    if head:
        for i, row in enumerate(head):
            y = top - len(head) + i
            for x, ch in enumerate(row):
                if ch != "." and 0 <= y:
                    grid[y][x] = ch
    ep = EYES[direction]
    if ep and eyes:
        ey = top + 3
        for ex in ep:
            if eyes == "white":
                grid[ey][ex] = "o"
            elif eyes == "red":
                grid[ey][ex] = "R"
                grid[ey - 1][ex] = "d"
                grid[ey + 1][ex] = "d"
                if ex - 1 >= 0 and grid[ey][ex - 1] == "#":
                    grid[ey][ex - 1] = "d"
                if ex + 1 < W and grid[ey][ex + 1] == "#":
                    grid[ey][ex + 1] = "d"
    if face:
        for (x, y), ch in face.items():
            grid[top + y][x] = ch
    return art(["".join(r) for r in grid], INK, W, H)


def player_sheet():
    """4 rows (down, up, left, right) x 4 cols (idle, walkA, walkB, attack)."""
    out = []
    for d in DIRS:
        for pose in ("idle", "A", "B", "atk"):
            out.append(gusen(d, pose))
    return sheet(out, 4)


SHADOW_HEAD = {
    "down":  ["..#.....#...", "..##.#.##...", "...#####...."],
    "up":    ["..#.....#...", "..##.#.##...", "...#####...."],
    "left":  [".#.....#....", ".##.#.##....", "..#####....."],
    "right": ["....#.....#.", "....##.#.##.", ".....#####.."],
}


def shadow_sheet():
    """Red-eyed Skyggegusen enemy: 4 dirs x (walkA, walkB, attack)."""
    out = []
    for d in DIRS:
        mouth = {"down": {(4, 5): "p", (6, 5): "p"}, "up": None,
                 "left": {(3, 5): "p", (5, 5): "p"}, "right": {(6, 5): "p", (8, 5): "p"}}[d]
        for pose in ("A", "B", "atk"):
            head = [r.replace("#", "#") for r in SHADOW_HEAD[d]]
            out.append(gusen(d, pose, eyes="red", head=head[1:] if pose != "atk" else head, face=mouth))
    return sheet(out, 3)


def bat_frames():
    """Flaggermusgusen: 16x16, wings up / mid / down."""
    return frames('''
        ................ ................ ................
        #..............# ................ ................
        ##............## ................ ................
        .##..........##. ................ ................
        .###..####..###. ......####...... ......####......
        ..############.. .###.######.###. .....######.....
        ...##dR##Rd##... #####dR##Rd##### ....#dR##Rd#....
        ....##d##d##.... #.#.##d##d##.#.# ...###d##d###...
        .....#p##p#..... .....#p##p#..... ..####p##p####..
        ......####...... ......####...... .###.######.###.
        ......#..#...... ......#..#...... .##...#..#...##.
        ................ ................ .#............#.
        ................ ................ #..............#
        ................ ................ ................
        ................ ................ ................
        ................ ................ ................
    ''', INK, 16, 16)


def boss_frames():
    """Skyggekongen: 32x32 boss. idle A, idle B (squash), attack telegraph."""
    def build(squash=0, open_mouth=False):
        g = [["."] * 32 for _ in range(32)]
        cx, cy, rx, ry = 15.5, 19 + squash, 14, 9 - squash
        for y in range(32):
            for x in range(32):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    g[y][x] = "#"
        # legs
        for x in list(range(7, 11)) + list(range(21, 25)):
            for y in range(int(cy + ry) - 1, 31):
                g[y][x] = "#"
        for x in list(range(5, 11)) + list(range(21, 27)):
            g[30][x] = "#"
        # crown: three antennae with glowing orbs
        top = int(cy - ry)
        for ax, h in ((9, 6), (15, 8), (22, 6)):
            for y in range(top - h + 2, top + 1):
                g[y][ax] = "#"
                g[y][ax + 1] = "#" if ax == 15 else g[y][ax + 1]
            oy = top - h
            for (dx, dy, c) in [(0, 0, "R"), (-1, 0, "d"), (1, 0, "d"), (0, -1, "d"), (0, 1, "d")]:
                if ax == 15:
                    for k in (0, 1):
                        g[oy + dy][ax + k + dx] = c if g[oy + dy][ax + k + dx] != "R" else "R"
                else:
                    g[oy + dy][ax + dx] = c
        # eyes: 2x2 red with dark-red halo; white core when about to strike
        ey = int(cy) - 3
        for ex in (9, 20):
            for dx in (-1, 2):
                for dy in (0, 1):
                    g[ey + dy][ex + dx] = "d"
            for dy in (-1, 2):
                for dx in (0, 1):
                    g[ey + dy][ex + dx] = "d"
            for dx in (0, 1):
                for dy in (0, 1):
                    g[ey + dy][ex + dx] = "R"
            if open_mouth:
                g[ey][ex] = "p"
        # jagged mouth
        my = ey + 5
        teeth = "p.p.p.p.p.p" if not open_mouth else "p.p.p.p.p.p"
        for i, ch in enumerate(teeth):
            if ch == "p":
                g[my][10 + i] = "p"
        if open_mouth:
            for y in range(my + 1, my + 4):
                for x in range(11, 21):
                    g[y][x] = "n" if y < my + 3 else "d"
            for i in range(11):
                if i % 2 == 0:
                    g[my + 4][10 + i] = "p"
        return art(["".join(r) for r in g], INK, 32, 32)
    return [build(0), build(1), build(1, open_mouth=True)]


# NPC Gusens that share the standard body get front/back frames derived from
# their existing left frame (head decoration kept, eyes and feet re-posed).
STANDARD_NPCS = ["npc1", "npc2", "dinggusen", "gressgusen", "lanternegusen",
                 "lunagusen", "wirelessgusen", "sprite"]


def npc_sheet(src_dir):
    rows = []
    for name in STANDARD_NPCS:
        im = Image.open(os.path.join(src_dir, name + ".png")).convert("RGBA")
        left = im.crop((0, 0, 12, 15))
        right = im.crop((0, 15, 12, 30))
        front = left.copy()
        px = front.load()
        white, black = (255, 255, 255, 255), (0, 0, 0, 255)
        assert px[3, 9] == white and px[7, 9] == white, name
        px[7, 9] = black
        px[8, 9] = white
        for y, row in zip((13, 14), LEGS_FRONT["idle"]):
            for x, ch in enumerate(row):
                px[x, y] = black if ch == "#" else (0, 0, 0, 0)
        back = front.copy()
        bp = back.load()
        bp[3, 9] = black
        bp[8, 9] = black
        rows += [front, back, left, right]
    return sheet(rows, 4), STANDARD_NPCS
