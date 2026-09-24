"""Tiny pixel-art toolkit used by make_assets.py.

Every sprite is authored at 1x as ASCII art against a fixed palette, so the
output is pixel perfect: no anti-aliasing, no stray colours. Scaling happens
only in previews / at runtime with nearest-neighbour and integer factors.
"""
from PIL import Image

# ---------------------------------------------------------------------------
# Master palette: AAP-64 (already used by Penge, Terreng and Voksende blomst)
# plus the "Gusen ink" used by every Gusen character sprite.
# ---------------------------------------------------------------------------
AAP64 = [
    "060608", "141013", "3b1725", "73172d", "b4202a", "df3e23", "fa6a0a", "f9a31b",
    "ffd541", "fffc40", "d6f264", "9cdb43", "59c135", "14a02e", "1a7a3e", "24523b",
    "122020", "143464", "285cc4", "249fde", "20d6c7", "a6fcdb", "ffffff", "fef3c0",
    "fad6b8", "f5a097", "e86a73", "bc4a9b", "793a80", "403353", "242234", "221c1a",
    "322b28", "71413b", "bb7547", "dba463", "f4d29c", "dae0ea", "b3b9d1", "8b93af",
    "6d758d", "4a5462", "333941", "422433", "5b3138", "8e5252", "ba756a", "e9b5a3",
    "e3e6ff", "b9bffb", "849be4", "588dbe", "477d85", "23674e", "328464", "5daf8d",
    "92dcba", "cdf7e2", "e4d2aa", "c7b08b", "a08662", "796755", "5a4e44", "423934",
]
GUSEN_INK = ["000000", "090000", "170000", "2b0000", "460000", "930000", "c50000", "ff0000", "ff1c1c", "ffe3e3"]
MASTER = AAP64 + GUSEN_INK
MASTER_SET = set(MASTER)


def rgba(hexstr, a=255):
    return (int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16), a)


def art(rows, key, w=None, h=None):
    """ASCII -> RGBA image. '.' and ' ' are transparent."""
    rows = [r for r in rows]
    h = h or len(rows)
    w = w or max(len(r) for r in rows)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows[:h]):
        for x, ch in enumerate(row[:w]):
            if ch in ". ":
                continue
            if ch not in key:
                raise KeyError(f"char {ch!r} not in key (row {y}: {row!r})")
            c = key[ch]
            px[x, y] = rgba(c) if isinstance(c, str) else c
    return im


def parse_block(text):
    """Split a triple-quoted block into rows, dropping the first/last blank lines."""
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    indent = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    return [l[indent:] for l in lines]


def frames(text, key, w, h, gap=1):
    """Several frames written side by side in one ASCII block, separated by `gap` columns."""
    rows = parse_block(text)
    n = (max(len(r) for r in rows) + gap) // (w + gap)
    out = []
    for i in range(n):
        x0 = i * (w + gap)
        out.append(art([r[x0:x0 + w].ljust(w, ".") for r in rows], key, w, h))
    return out


def blank(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def over(dst, src, x=0, y=0):
    dst.alpha_composite(src, (x, y))
    return dst


def flip_h(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def flip_v(im):
    return im.transpose(Image.FLIP_TOP_BOTTOM)


def rot90(im, k=1):
    """Rotate counter-clockwise by k*90 degrees (lossless)."""
    for _ in range(k % 4):
        im = im.transpose(Image.ROTATE_90)
    return im


def recolor(im, mapping):
    """Swap exact colours: {"from_hex": "to_hex"}."""
    im = im.copy()
    px = im.load()
    m = {rgba(k)[:3]: rgba(v) for k, v in mapping.items()}
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] and p[:3] in m:
                px[x, y] = m[p[:3]][:3] + (p[3],)
    return im


def outline(im, color, diagonal=False):
    """Add a 1px outline around opaque pixels (inside the canvas)."""
    out = im.copy()
    src = im.load()
    px = out.load()
    c = rgba(color)
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        nb += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for y in range(im.height):
        for x in range(im.width):
            if src[x, y][3]:
                continue
            for dx, dy in nb:
                xx, yy = x + dx, y + dy
                if 0 <= xx < im.width and 0 <= yy < im.height and src[xx, yy][3]:
                    px[x, y] = c
                    break
    return out


def sheet(images, cols, cell=None, pad=0):
    """Pack equally-sized frames left-to-right, top-to-bottom."""
    cw, ch = cell or images[0].size
    rows = (len(images) + cols - 1) // cols
    out = blank(cols * (cw + pad) - pad, rows * (ch + pad) - pad)
    for i, im in enumerate(images):
        out.alpha_composite(im, ((i % cols) * (cw + pad), (i // cols) * (ch + pad)))
    return out


def _pixels(im):
    get = getattr(im, "get_flattened_data", None)
    return get() if get else im.getdata()


def colors_used(im):
    return {"%02x%02x%02x" % p[:3] for p in _pixels(im) if p[3]}


def check_palette(name, im, max_colors=15, master=True):
    """GBA rule of thumb: one 4bpp palette = 15 colours + transparent."""
    used = colors_used(im)
    stray = used - MASTER_SET
    if master and stray:
        raise ValueError(f"{name}: colours outside master palette: {sorted(stray)}")
    if len(used) > max_colors:
        raise ValueError(f"{name}: {len(used)} colours > {max_colors} (GBA 4bpp limit)")
    alphas = {p[3] for p in _pixels(im)} - {0, 255}
    return len(used), alphas


def scale(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)
