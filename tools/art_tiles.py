"""Overworld tiles (16x16) and big props, AAP-64 only.

Style rules (derived from Terreng Gress og sorpe / Voksende rod blomst):
  * nature uses dark same-hue outlines (dark green, dark maroon), never black
  * light comes from the top-left
  * 3-5 flat shades per material, no dithering, no anti-aliasing
"""
import math
from pixel import *

T = 16

# --- material ramps ------------------------------------------------------
G = dict(o="122020", D="24523b", d="1a7a3e", g="14a02e", l="59c135", h="9cdb43", y="d6f264")
DIRT = dict(k="242234", s="422433", a="5b3138", m="8e5252", p="ba756a")          # Terreng dirt
SAND = dict(e="796755", q="a08662", c="c7b08b", w="e4d2aa")                      # paths
WATER = dict(W="143464", b="285cc4", B="249fde", f="a6fcdb", F="ffffff", t="20d6c7")
STONE = dict(S="333941", n="4a5462", N="6d758d", v="8b93af", V="b3b9d1", X="dae0ea")
WOOD = dict(K="221c1a", r="322b28", R="71413b", u="bb7547", U="dba463", Y="f4d29c")
GOLD = dict(j="f9a31b", J="ffd541", Z="fffc40")
RED = dict(x="73172d", i="b4202a", I="df3e23", Q="3b1725")


def key(*ramps, **extra):
    k = {}
    for r in ramps:
        k.update(r)
    k.update(extra)
    return k


# --- grass --------------------------------------------------------------
GRASS_KEY = key(G)
GRASS = [
    art(parse_block('''
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gglggggggggggggg
        gdlgdggggggggggg
        ggddgggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggglggggg
        gggggggggdlgdggg
        ggggggggggddgggg
        gggggggggggggggg
        gggglggggggggggg
        gggdlgdggggggggg
        ggggddgggggggggg
        gggggggggggggggg
    '''), GRASS_KEY),
    art(parse_block('''
        gggggggggggggggg
        ggggggggggglgggg
        ggggggggggdlgdgg
        gggggggggggddggg
        gggggggggggggggg
        ggggglgggggggggg
        gggggdgggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gglggggggggggggg
        gdlgdgggggglgggg
        ggddgggggggdgggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
    '''), GRASS_KEY),
    art(parse_block('''
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggglggggggg
        gggggggdlgdggggg
        ggggggggddgggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggglg
        ggggggggggggggdg
        gggggggggggggggg
    '''), GRASS_KEY),
]
# grass with tiny flowers (petals from the red flower sprite)
GRASS_FLOWERS = [
    art(parse_block('''
        gggggggggggggggg
        ggggggggggggIggg
        gggggggggggIjIgg
        ggggggggggggIggg
        gggIggggggggdggg
        ggIjIggggggggggg
        gggIgggggggggggg
        gggdgggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        ggggggggIggggggg
        gggggggIjIgggggg
        ggggggggIggggggg
        ggggggggdggggggg
        gggggggggggggggg
        gggggggggggggggg
    '''), key(G, I="df3e23", j="ffd541")),
    art(parse_block('''
        gggggggggggggggg
        gggggggggggggggg
        gggJgggggggggggg
        ggJjJggggggJgggg
        gggJgggggggJjJgg
        gggdgggggggJgggg
        gggggggggggggggg
        gggggggggggggggg
        gggggggggggggggg
        ggggggggggggggJg
        gggggJgggggggJjJ
        ggggJjJgggggggJg
        gggggJgggggggggg
        gggggdgggggggggg
        gggggggggggggggg
        gggggggggggggggg
    '''), key(G, J="fffc40", j="fa6a0a")),
]

# --- autotile machinery ---------------------------------------------------
# A wobble that repeats every 16px so edge tiles line up seamlessly.
WOB = [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0, 1, 0, 0]
EDGE = 4  # grass border thickness at the edge of a path / pond


def _mask_nw(x, y):
    """True where the *inner* material is, for the outer NW corner tile."""
    if y < EDGE + WOB[x]:
        return False
    if x < EDGE + WOB[y]:
        return False
    cx = cy = EDGE + 5
    if x < cx and y < cy and (x - cx) ** 2 + (y - cy) ** 2 > 5.2 ** 2:
        return False
    return True


def _mask_n(x, y):
    return y >= EDGE + WOB[x]


def _mask_inner_nw(x, y):
    """Inner corner: material everywhere except a notch of grass in the NW."""
    return not (y < EDGE + WOB[x] and x < EDGE + WOB[y])


def _mk(fn):
    return [[fn(x, y) for x in range(T)] for y in range(T)]


def _fl(m, h=False, v=False):
    return [[m[T - 1 - y if v else y][T - 1 - x if h else x] for x in range(T)] for y in range(T)]


def _tr(m):
    return [[m[x][y] for x in range(T)] for y in range(T)]


def autotile_masks():
    nw, n, inw = _mk(_mask_nw), _mk(_mask_n), _mk(_mask_inner_nw)
    w = _tr(n)
    full = [[True] * T for _ in range(T)]
    # layout (5 cols x 3 rows):  NW N NE | iNW iNE
    #                            W  C  E | iSW iSE
    #                            SW S SE | C2  (spare)
    return {
        "nw": nw, "n": n, "ne": _fl(nw, h=True),
        "w": w, "c": full, "e": _fl(w, h=True),
        "sw": _fl(nw, v=True), "s": _fl(n, v=True), "se": _fl(nw, h=True, v=True),
        "inw": inw, "ine": _fl(inw, h=True), "isw": _fl(inw, v=True), "ise": _fl(inw, h=True, v=True),
    }


AUTOTILE_ORDER = ["nw", "n", "ne", "inw", "ine",
                  "w", "c", "e", "isw", "ise",
                  "sw", "s", "se", "c2", "c3"]


def _render_autotile(mask, inner_px, edge_px, grass_src):
    im = blank(T, T)
    px = im.load()
    gs = grass_src.load()

    def m(x, y):
        if 0 <= x < T and 0 <= y < T:
            return mask[y][x]
        return mask[min(max(y, 0), T - 1)][min(max(x, 0), T - 1)]

    for y in range(T):
        for x in range(T):
            if m(x, y):
                nb = dict(up=not m(x, y - 1), down=not m(x, y + 1),
                          left=not m(x - 1, y), right=not m(x + 1, y))
                c = edge_px(x, y, nb) if any(nb.values()) else None
                px[x, y] = rgba(c or inner_px(x, y))
            else:
                near = [m(x, y + 1), m(x, y - 1), m(x + 1, y), m(x - 1, y)]
                if near[0]:
                    px[x, y] = rgba(G["l"])          # lit grass lip above the dip
                elif any(near):
                    px[x, y] = rgba(G["g"])          # keep tufts off the border
                else:
                    px[x, y] = gs[x, y]
    return im


# path: packed light sand, darker rim where the grass overhangs it
def _path_inner(x, y):
    h = (x * 7 + y * 13 + (x * y) % 5) % 23
    if h == 0:
        return SAND["q"]
    if h == 11 and y % 2 == 0:
        return SAND["w"]
    return SAND["c"]


def _path_edge(x, y, nb):
    if nb["up"]:
        return SAND["e"]
    if nb["left"] or nb["right"]:
        return SAND["q"]
    if nb["down"]:
        return SAND["w"]
    return None


def path_tiles():
    masks = autotile_masks()
    out = []
    for name in AUTOTILE_ORDER:
        if name in ("c2", "c3"):
            im = blank(T, T)
            px = im.load()
            for y in range(T):
                for x in range(T):
                    c = _path_inner(x, y)
                    if name == "c2" and (x, y) in [(4, 5), (5, 5), (11, 11), (3, 12), (12, 3)]:
                        c = SAND["q"]
                    if name == "c3" and (x, y) in [(6, 9), (7, 9), (6, 10), (10, 3), (2, 2)]:
                        c = SAND["e"] if (x, y) == (6, 10) else SAND["q"]
                    px[x, y] = rgba(c)
            out.append(im)
        else:
            out.append(_render_autotile(masks[name], _path_inner, _path_edge, GRASS[2]))
    return out


# water: deep shadow under the bank, ripples and sparkles animated over 3 frames
def _water_inner(frame):
    def f(x, y):
        # horizontal ripple dashes drifting right
        r = (x - frame * 2 + (y // 4) * 5) % 16
        if y % 4 == 1 and r < 3:
            return WATER["B"]
        if y % 8 == 5 and (x + frame * 3 + 4) % 16 == 0:
            return WATER["f"]
        return WATER["b"]
    return f


def _water_edge(x, y, nb):
    if nb["up"]:
        return WATER["W"]
    if nb["left"] or nb["right"]:
        return WATER["W"]
    if nb["down"]:
        return WATER["B"]
    return None


def water_tiles(frame):
    masks = autotile_masks()
    inner = _water_inner(frame)

    def edge(x, y, nb):
        return _water_edge(x, y, nb)

    out = []
    for name in AUTOTILE_ORDER:
        mask = masks["c"] if name in ("c2", "c3") else masks[name]
        im = _render_autotile(mask, inner, edge, GRASS[2])
        # second row of shadow under the north bank
        px = im.load()
        for y in range(1, T):
            for x in range(T):
                if mask[y][x] and y - 1 >= 0 and mask[y - 1][x] and (y - 2 < 0 or not mask[y - 2][x]) and px[x, y - 1][:3] == rgba(WATER["W"])[:3] and not (y - 2 < 0 and name in ("c", "c2", "c3", "w", "e", "s", "sw", "se", "isw", "ise")):
                    px[x, y] = rgba(WATER["b"]) if (x + frame) % 3 else rgba(WATER["W"])
        if name == "c3":  # lily pad
            over(im, art(parse_block('''
                ..DDD.
                .DlhlD
                DlglgD
                DggDgD
                .DgggD
                ..DDD.
            '''), key(G)), 5, 5)
        out.append(im)
    return out


# --- cliff (top-down version of Terreng Gress og sorpe) ---------------------
CLIFF_KEY = key(G, DIRT)
CLIFF_TOP = art(parse_block('''
    ggggggggggggggggggggggggggggggggg
    llllhlllllllllllllllhllllllllllll
    gggglggggglllllgggggggggggglgggg
    ggddgdddggggggggddddddgdggdddgdg
    dDddDDDddddgddddddDDDDdDddDDDDdd
    DDDDDDDDDDDdDDDDDDDDDDDDDDDDDDDD
    DoDDDDDoDDDDDDDDDDDDDoDDDDDDDoDD
    oooDoooooDDDDDDoDDDoooooDDoooooo
    aaoooaaaooooooooooooaaaaoooaaaaa
    aaaaaaaaaaaaaaoooooaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aapaaaaaaaaaaaaaaaaaaaaaaaaapaaa
    smsssssaaaaaaaaaaaaaaaaaaaaamssss
    kkkkkkksssaaaaaaaaaaaasssssssskkk
    aaaaaaakkksssssssssssskkkkkkkkaaa
    aaaaaaaaaakkkkkkkkkkkkaaaaaaaaaaa
'''), CLIFF_KEY, 32, 16)
CLIFF_MID = art(parse_block('''
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaapaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaamaaaaaaaaaaaaaaaaaa
    saaaaaaaaaaaaaaaaaaaaaaassssssss
    kssssssssssssaaaaaaaaaaskkkkkkkk
    akkkkkkkkkkkksssssssssskaaaaaaaa
    aaaaaaaaaaaaakkkkkkkkkkaaaaaaaaa
    aaaaaaaasaaaaaaaaaaaaaaaaaaaaaaa
    aaaapaaasaaaaaaaaaaaaaaaaaaaaaaa
    aaamaaaaskaaaaaaaaaaaaaaaaaaapaa
    aaaaaaaaakaaaaaaaaaaaaaaaaaamaaa
    sssssssaaaaaaaaaaaaaaaaaaaaaaaaa
    kkkkkkksssaaaaaaaaaaaaaaassssssss
    aaaaaaakkkssssssssssssssskkkkkkkk
    aaaaaaaaaakkkkkkkkkkkkkkkaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
'''), CLIFF_KEY, 32, 16)
CLIFF_BASE = art(parse_block('''
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaasaaaapaaaa
    aaaaapaaaaaaaaaaaaaaaasaamaaaaaa
    ssssmsaaaaaaaaaaaaaaaaskaaaasssss
    kkkkkksssssaaaaaaaaaaassssskkkkk
    aaaaaakkkkksssssssssssskkkkaaaaa
    aaaaaaaaaaakkkkkkkkkkkkaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    saaaaaaaaaaaaaaaaaaaaaaaaaaaaaas
    kssaaasaaaaaaassaaaaaaaaasaaasssk
    kkksskkssssssskkssssssssskssskkkk
    kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
    DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
    dddddDDdddddddddddDDddddddddDDddd
    ggddgggddddgggggddggggddddgggdggg
    gggggggggggggggggggggggggggggggggg
'''), CLIFF_KEY, 32, 16)


def _cliff_end(col_img, side):
    """Give a 16x48 cliff column a rim: lit on the left end, shaded on the right."""
    im = col_img.copy() if side == "left" else flip_h(col_img)
    px = im.load()
    for y in range(im.height):
        if y < 8:                     # grass lip rows continue the plateau rim
            rim, edge = G["o"], G["D"]
        elif y < 44:                  # exposed dirt
            rim, edge = DIRT["k"], (DIRT["m"] if side == "left" else DIRT["s"])
        else:                         # grass shadow at the foot of the cliff
            continue
        px[0, y] = rgba(rim)
        px[1, y] = rgba(edge)
        if side == "left" and 8 <= y < 44 and y % 7 == 3:
            px[2, y] = rgba(DIRT["p"])
    # soften the bottom corner where the rim meets the ground
    px[0, 43] = rgba(G["D"])
    return im if side == "left" else flip_h(im)


def cliff_tiles():
    """Returns a 4x3 block: [L-end, mid, mid, R-end] x [top, mid, base]."""
    rows = []
    for strip in (CLIFF_TOP, CLIFF_MID, CLIFF_BASE):
        rows.append([strip.crop((0, 0, 16, 16)), strip.crop((16, 0, 32, 16))])
    col_l, col_r = blank(16, 48), blank(16, 48)
    for i, (a, b) in enumerate(rows):
        over(col_l, a, 0, i * 16)
        over(col_r, b, 0, i * 16)
    col_l = _cliff_end(col_l, "left")
    col_r = _cliff_end(col_r, "right")
    tiles = []
    for i, (a, b) in enumerate(rows):
        tiles += [col_l.crop((0, i * 16, 16, i * 16 + 16)), a, b, col_r.crop((0, i * 16, 16, i * 16 + 16))]
    return tiles


def plateau_edges():
    """Grass-top rims for the sides of a raised plateau: W, E, and NW/NE corners."""
    w = GRASS[2].copy()
    px = w.load()
    for y in range(16):
        px[0, y] = rgba(G["o"])
        px[1, y] = rgba(G["D"])
        px[2, y] = rgba(G["l"]) if y % 5 != 2 else rgba(G["g"])
    e = flip_h(w)
    px = e.load()
    for y in range(16):  # right rim is in shadow: no highlight
        px[13, y] = rgba(G["d"])
    nw = GRASS[2].copy()
    px = nw.load()
    for y in range(16):
        for x in range(16):
            if y == 0 or x == 0:
                px[x, y] = rgba(G["o"])
            elif y == 1 or x == 1:
                px[x, y] = rgba(G["D"])
            elif y == 2 or x == 2:
                px[x, y] = rgba(G["l"])
    for (x, y) in [(0, 0), (1, 0), (0, 1)]:
        px[x, y] = rgba(G["d"])
    ne = flip_h(nw)
    px = ne.load()
    for y in range(2, 16):
        px[13, y] = rgba(G["d"])
    n = GRASS[2].copy()
    px = n.load()
    for x in range(16):
        px[x, 0] = rgba(G["o"])
        px[x, 1] = rgba(G["D"])
        px[x, 2] = rgba(G["l"])
    return [nw, n, ne, w, e]


def cave_mouth():
    """32x32 opening that replaces a 2x2 block of cliff (top row + base row)."""
    im = blank(32, 32)
    over(im, CLIFF_TOP, 0, 0)
    over(im, CLIFF_BASE, 0, 16)
    px = im.load()
    cx = 15.5
    for y in range(32):
        for x in range(32):
            dx = abs(x - cx)
            top = 12 + (dx / 9.0) ** 2 * 7 if dx < 9 else 99
            if y >= top:
                px[x, y] = rgba("000000")
            elif y >= top - 1:
                px[x, y] = rgba(DIRT["k"])
            elif y >= top - 2 and dx < 8:
                px[x, y] = rgba(DIRT["m"])
    # a lit edge on the left jamb, shadow on the right
    for y in range(22, 32):
        if px[6, y][:3] == rgba(DIRT["a"])[:3]:
            px[6, y] = rgba(DIRT["m"])
    return im


# --- foliage via shaded clumps ------------------------------------------
def shaded_blob(w, h, clumps, ramp, outline_c, light=(-0.55, -0.8), inner_line=None, flat_bottom=None):
    """Draw overlapping round clumps (back to front) with top-left lighting.

    ramp: dark->light list of hex colours (4 entries)."""
    L = math.hypot(*light)
    lx, ly = light[0] / L, light[1] / L
    owner = [[-1] * w for _ in range(h)]
    for i, (cx, cy, r) in enumerate(clumps):
        for y in range(h):
            for x in range(w):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    if flat_bottom is not None and y > flat_bottom:
                        continue
                    owner[y][x] = i
    im = blank(w, h)
    px = im.load()
    for y in range(h):
        for x in range(w):
            i = owner[y][x]
            if i < 0:
                continue
            cx, cy, r = clumps[i]
            nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            b = nx * lx + ny * ly
            if b > 0.55:
                c = ramp[3]
            elif b > 0.0:
                c = ramp[2]
            elif b > -0.55:
                c = ramp[1]
            else:
                c = ramp[0]
            # a front clump casts a sliver of shadow on the clump behind it
            if inner_line and y + 1 < h and owner[y + 1][x] > i and owner[y + 1][x] >= 0:
                c = inner_line
            if inner_line and x + 1 < w and owner[y][x + 1] > i and owner[y][x + 1] >= 0 and b < 0.3:
                c = inner_line
            px[x, y] = rgba(c)
    return outline(im, outline_c)


def tree():
    """32x40 round-canopy tree; trunk in the Terreng dirt ramp."""
    canopy = shaded_blob(32, 30, [
        (16, 9, 8.5), (8.5, 13, 7), (23.5, 13, 7), (11, 20, 7.5), (21, 20, 7.5), (16, 17, 7),
    ], [G["D"], G["d"], G["g"], G["l"]], G["o"], inner_line=G["D"])
    # sprinkle a few leaf highlights
    px = canopy.load()
    for (x, y) in [(12, 5), (13, 5), (6, 10), (19, 4), (9, 16), (17, 13), (22, 10), (14, 18)]:
        if px[x, y][:3] in (rgba(G["l"])[:3], rgba(G["g"])[:3]):
            px[x, y] = rgba(G["h"])
    trunk = art(parse_block('''
        ......oaaams......
        ......oamaas......
        ......oamaas......
        .....oaamaass.....
        ....ooamaaaasso...
        ...oaaaoasaaaaso..
        ....ooo.oo.ooo....
    '''), key(DIRT, o=DIRT["k"]))
    shadow = art(parse_block('''
        ...DDDDDDDDDDDDDDD...
        .DDDDDDDDDDDDDDDDDDD.
        ..DDDDDDDDDDDDDDDDD..
    '''), key(G))
    im = blank(32, 40)
    over(im, shadow, 6, 35)
    over(im, trunk, 7, 31)
    over(im, canopy, 0, 2)
    return im


def bush(cut=False):
    if cut:
        return art(parse_block('''
            ................
            ................
            ................
            ................
            ................
            ................
            ................
            ................
            ................
            ................
            .....o.oo.o.....
            ....olDdlDdo....
            ...oDddDddDDo...
            ...oDDDDDDDDo...
            ....oooooooo....
            ................
        '''), key(G))
    b = shaded_blob(16, 16, [(8, 7, 5.5), (4.8, 10, 4), (11.2, 10, 4), (8, 10.5, 4.5)],
                    [G["D"], G["d"], G["g"], G["l"]], G["o"], inner_line=G["D"], flat_bottom=13)
    px = b.load()
    for (x, y) in [(6, 3), (7, 3), (3, 8)]:
        if px[x, y][3]:
            px[x, y] = rgba(G["h"])
    return b


def rock(big=False):
    if big:
        return shaded_blob(16, 16, [(7, 8.5, 6), (10.5, 9.5, 5)],
                           [STONE["n"], STONE["N"], STONE["v"], STONE["V"]], STONE["S"],
                           inner_line=STONE["n"], flat_bottom=13)
    return shaded_blob(16, 16, [(8, 10, 4.5), (6, 11, 3.2)],
                       [STONE["n"], STONE["N"], STONE["v"], STONE["V"]], STONE["S"],
                       inner_line=STONE["n"], flat_bottom=13)


def tall_grass():
    """Cuttable tall grass, 2 sway frames (like Vind i gress) + stubble."""
    K = key(G)
    fs = frames('''
        ................ ................
        ................ ................
        ....l.....l..... .....l.....l....
        ...ld..l..dl.... ....ld..l..dl...
        ...dd..dl.dd..l. ...dd..ld.dd..l.
        .l.ddl.dd.ddldl. ..l.dl.dd.dd.ld.
        .dldDd.dDldDddd. .dl.Dd.dDldDldd.
        .ddlDdldDddDdDd. ..dlDdldDddDdDd.
        .dDdDddDDdDDdDd. .dDdDddDDdDDdDd.
        .DdDDdDDDdDDDDd. .DdDDdDDDdDDDDd.
        .DDDDDDDDDDDDDD. .DDDDDDDDDDDDDD.
        .oDDDDDDDDDDDDo. .oDDDDDDDDDDDDo.
        ..oooooooooooo.. ..oooooooooooo..
        ................ ................
        ................ ................
        ................ ................
    ''', K, 16, 16)
    stub = art(parse_block('''
        ................
        ................
        ................
        ................
        ................
        ................
        ................
        ................
        ................
        ..l..l..l.l..l..
        .dld.dldld.ldd..
        .DdDdDdDDdDdDDd.
        .oDDDDDDDDDDDDo.
        ..oooooooooooo..
        ................
        ................
    '''), K)
    return fs + [stub]


def flower_patch():
    """Two-frame sway, colours lifted from Voksende rod blomst."""
    K = key(G, x="73172d", i="b4202a", I="df3e23", J="ffd541")
    return frames('''
        ................ ................
        ................ ................
        ................ ................
        ........x....... .........x......
        .......xIx...... ........xIx.....
        ......xIJIx..... .......xIJIx....
        .......xix...... ........xix.....
        ...x....d....... ...x.....d......
        ..xIx...d.....x. ..xIx...d.....x.
        .xIJIx.ld....xIx .xIJIx.ld....xIx
        ..xix..dd...xIJI ..xix..dd...xIJI
        ...d...d.....xix ...d....d...xix.
        ..ld..ld......d. ...ld..ld....d..
        ..dD.dD......ld. ..dD..dD....ld..
        ...D..D......D.. ...D..D.....D...
        ................ ................
    ''', K, 16, 16)


# --- props (warm near-black outline) --------------------------------------
def sign():
    return art(parse_block('''
        ................
        ................
        .KKKKKKKKKKKKKK.
        KYUUUUUUUUUUUUuK
        KUuUUUUUUUUUUuRK
        KUrrrrurrrrrruRK
        KUuuuuuuuuuuuuRK
        KUrrrurrrrruuuRK
        KuuuuuuuuuuuuRRK
        KRRRRRRRRRRRRRRK
        .KKKKKuUKKKKKKK.
        ......uRK.......
        ......uRK.......
        ....DDuRKDD.....
        .....DKKKD......
        ................
    '''), key(WOOD, D=G["D"]))


def chest(open_=False):
    if open_:
        return art(parse_block('''
            ................
            ..KKKKKKKKKKKK..
            .KRRRRRRRRRRRRK.
            .KRuuuuuuuuuuRK.
            .KjJJJJJJJJJJjK.
            .KrKKKKKKKKKKrK.
            KKKKKKKKKKKKKKKK
            KUUUUUjJjUUUUUUK
            KuuuuujZjuuuuuRK
            KjJJJJJJJJJJJJjK
            KuuuuuuuuuuuuuRK
            KuRRRRRRRRRRRRRK
            KjjjjjjjjjjjjjjK
            .KKKKKKKKKKKKKK.
            ..DDDDDDDDDDDD..
            ................
        '''), key(WOOD, GOLD, D=G["D"]))
    return art(parse_block('''
        ................
        ................
        ................
        ..KKKKKKKKKKKK..
        .KYUUUUUUUUUUuK.
        KUUuuuuuuuuuuuRK
        KjJJJJJJJJJJJJjK
        KRRRRRjZjRRRRRRK
        KUUUUUjJjUUUUUuK
        KuuuuujjjuuuuuRK
        KjJJJJJJJJJJJJjK
        KuRRRRRRRRRRRRRK
        KjjjjjjjjjjjjjjK
        .KKKKKKKKKKKKKK.
        ..DDDDDDDDDDDD..
        ................
    '''), key(WOOD, GOLD, D=G["D"]))


def pot():
    return art(parse_block('''
        ................
        ................
        ....KKKKKKKK....
        ...KUYYUUUUuK...
        ...KrKKKKKKrK...
        ....KuUUuuRK....
        ...KUYUuuuuRK...
        ..KUYUuuuuuuRK..
        ..KUUuuuuuuuRK..
        ..KUuuuuuuuRRK..
        ..KuuuuuuuuRRK..
        ...KuuuuuuRRK...
        ...KRuRRRRRRK...
        ....KKKKKKKK....
        ....DDDDDDDD....
        ................
    '''), key(WOOD, D=G["D"]))


def fence():
    return frames('''
        ................ ................
        ................ ................
        ................ ................
        ................ ......KK........
        ................ .....KYUK.......
        KKKKKKKKKKKKKKKK KKKKKKUuKKKKKKKK
        UUUUYUUUUUUYUUUU UUUUUKUuKUUUUYUU
        uuuuuuuuuuuuuuuu uuuuuKuRKuuuuuuu
        KKKKKKKKKKKKKKKK KKKKKKuRKKKKKKKK
        ................ .....KuRK.......
        KKKKKKKKKKKKKKKK KKKKKKuRKKKKKKKK
        UUUUUUYUUUUUUUYU UUUUUKuRKUUUUUUU
        uuuuuuuuuuuuuuuu uuuuuKuRKuuuuuuu
        KKKKKKKKKKKKKKKK KKKKKKKKKKKKKKKK
        DDDDDDDDDDDDDDDD DDDDDDDDDDDDDDDD
        ................ ................
    ''', key(WOOD, D=G["D"]), 16, 16)


def stump():
    return art(parse_block('''
        ................
        ................
        ................
        ................
        ................
        ....kkkkkkkk....
        ...kppmmmmmmk...
        ..kpmmppppmmak..
        ..kpmpmmmmpmak..
        ..kmmmppppmaak..
        ..kammmmmmaaak..
        ..ksaaaaaaaask..
        .kkssasaassskk..
        ..kkkskksskkk...
        ...DDDDDDDDDD...
        ................
    '''), key(DIRT, D=G["D"]))


def all_tiles():
    """Everything in one 16x16 atlas, row by row (see assets/README.md)."""
    rows = {}
    rows["grass"] = GRASS + GRASS_FLOWERS
    rows["path"] = path_tiles()
    for f in range(3):
        rows[f"water{f}"] = water_tiles(f)
    rows["cliff"] = cliff_tiles() + plateau_edges()
    rows["foliage"] = tall_grass() + [bush(), bush(cut=True), rock(), rock(big=True)] + flower_patch()
    rows["props"] = [sign(), chest(), chest(open_=True), pot()] + fence() + [stump()]
    return rows


# --- interior walls (go with the Mega_Spritesheet furniture + floor) ----------
# Same maroon ramp as the furniture (#8e5252 / #5b3138 / #422433 are AAP-64),
# with warm sand wallpaper so furniture stands out against it.
WALL_KEY = key(DIRT, SAND)
WALL_TOP = art(parse_block('''
    kkkkkkkkkkkkkkkk
    ssssssssssssssss
    ssssssssssssssss
    aaaaaaaaaaaaaaaa
    pppppppppppppppp
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwqwwwcwwww
    wwwcwwqwqwwcwwww
    wwwcwwwqwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
    wwwcwwwwwwwcwwww
'''), WALL_KEY)
WALL_BOTTOM = art(parse_block('''
    wwwcwwwwwwwcwwww
    wwwcwwwqwwwcwwww
    wwwcwwqwqwwcwwww
    wwwcwwwqwwwcwwww
    wwwcwwwwwwwcwwww
    qqqqqqqqqqqqqqqq
    aaaaaaaaaaaaaaaa
    pppppppppppppppp
    appppppaappppppa
    apmmmmmsapmmmmms
    apmmmmmsapmmmmms
    apmmmmmsapmmmmms
    assssssaassssssa
    kkkkkkkkkkkkkkkk
    ssssssssssssssss
    kkkkkkkkkkkkkkkk
'''), WALL_KEY)


def interior_tiles(floor=None):
    """[wall_top, wall_bottom, side_l, side_r, front, front_l, front_r, void] plus the
    wall tiles with side caps (top_l, bottom_l, top_r, bottom_r). Side/front pieces are
    drawn over `floor` so every tile is complete on its own."""
    def side(im, left=True):
        im = im.copy()
        px = im.load()
        cols = [(0, "k"), (1, "s"), (2, "s"), (3, "a")]
        for x, c in cols:
            xx = x if left else 15 - x
            for y in range(16):
                px[xx, y] = rgba(DIRT[c])
        return im

    def front(im):
        im = im.copy()
        px = im.load()
        for y, c in [(11, "a"), (12, "s"), (13, "s"), (14, "s"), (15, "k")]:
            for x in range(16):
                px[x, y] = rgba(DIRT[c])
        return im

    floor = floor if floor is not None else blank(16, 16)
    void = art(["k" * 16] * 16, {"k": "000000"})
    side_l, side_r = side(floor), side(floor, left=False)
    f = front(floor)
    front_l = side(front(floor))
    front_r = side(front(floor), left=False)
    for im in (front_l, front_r):  # corner: the front cap wraps round
        px = im.load()
        for y in range(11, 16):
            for x in range(16):
                if px[x, y][:3] == rgba(DIRT["a"])[:3] and y > 11:
                    px[x, y] = rgba(DIRT["s"])
    return {
        "wall_top": WALL_TOP, "wall_bottom": WALL_BOTTOM,
        "wall_top_l": side(WALL_TOP), "wall_bottom_l": side(WALL_BOTTOM),
        "wall_top_r": side(WALL_TOP, False), "wall_bottom_r": side(WALL_BOTTOM, False),
        "side_l": side_l, "side_r": side_r, "front": f, "front_l": front_l, "front_r": front_r,
        "void": void,
    }
