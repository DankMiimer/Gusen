"""Minimal Aseprite (.ase/.aseprite) reader and writer (RGBA, one layer).

Reader: enough to flatten the visible layers of the Gusen .ase files.
Writer: RGBA sprite with one layer, per-frame durations, animation tags and the
master palette, so new assets open in Aseprite ready to edit.
Spec: https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
"""
import struct
import zlib
from PIL import Image


def read(path):
    d = open(path, "rb").read()
    _, magic, nframes, w, h, depth = struct.unpack_from("<IHHHHH", d, 0)
    if magic != 0xA5E0:
        raise ValueError(f"{path}: not an Aseprite file")
    transp = d[28]
    off = 128
    palette, layers, raw_frames = [], [], []
    for _ in range(nframes):
        fsize, _, oldn, dur = struct.unpack_from("<IHHH", d, off)
        n = struct.unpack_from("<I", d, off + 12)[0] or oldn
        p = off + 16
        cels = []
        for _ in range(n):
            csize, ctype = struct.unpack_from("<IH", d, p)
            body = d[p + 6:p + csize]
            if ctype == 0x2019:
                size, first, last = struct.unpack_from("<III", body, 0)
                palette += [(0, 0, 0, 0)] * max(0, size - len(palette))
                q = 20
                for i in range(first, last + 1):
                    fl, r, g, b, a = struct.unpack_from("<HBBBB", body, q)
                    q += 6
                    if fl & 1:
                        q += 2 + struct.unpack_from("<H", body, q)[0]
                    palette[i] = (r, g, b, a)
            elif ctype == 0x2004:
                flags = struct.unpack_from("<H", body, 0)[0]
                nl = struct.unpack_from("<H", body, 16)[0]
                layers.append({"visible": bool(flags & 1), "background": bool(flags & 8),
                               "name": body[18:18 + nl].decode("utf8", "replace")})
            elif ctype == 0x2005:
                li, x, y, _, ct = struct.unpack_from("<HhhBH", body, 0)
                if ct in (0, 2):
                    cw, ch = struct.unpack_from("<HH", body, 16)
                    data = body[20:]
                    if ct == 2:
                        data = zlib.decompress(data)
                    cels.append({"layer": li, "x": x, "y": y, "w": cw, "h": ch, "data": data})
                elif ct == 1:
                    cels.append({"layer": li, "link": struct.unpack_from("<H", body, 16)[0]})
            p += csize
        raw_frames.append((dur, cels))
        off += fsize
    # resolve linked cels
    for i, (_, cels) in enumerate(raw_frames):
        for j, c in enumerate(cels):
            if "link" in c:
                src = next(cc for cc in raw_frames[c["link"]][1] if cc["layer"] == c["layer"])
                cels[j] = dict(src, layer=c["layer"])
    frames = []
    for dur, cels in raw_frames:
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for c in sorted(cels, key=lambda c: c["layer"]):
            L = layers[c["layer"]]
            if not L["visible"]:
                continue
            px = []
            raw = c["data"]
            for i in range(c["w"] * c["h"]):
                if depth == 32:
                    px.append(tuple(raw[i * 4:i * 4 + 4]))
                elif depth == 16:
                    px.append((raw[i * 2],) * 3 + (raw[i * 2 + 1],))
                else:
                    ix = raw[i]
                    px.append((0, 0, 0, 0) if ix == transp and not L["background"] else palette[ix])
            cel = Image.new("RGBA", (c["w"], c["h"]))
            cel.putdata(px)
            layer_im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            layer_im.paste(cel, (c["x"], c["y"]))
            im.alpha_composite(layer_im)
        frames.append((im, dur))
    return {"width": w, "height": h, "frames": frames, "layers": layers, "palette": palette}


def _chunk(ctype, payload):
    return struct.pack("<IH", len(payload) + 6, ctype) + payload


def _string(s):
    b = s.encode("utf8")
    return struct.pack("<H", len(b)) + b


def write(path, frames, durations, tags=(), palette=(), layer_name="Layer 1"):
    """frames: list of equally sized RGBA images; durations: ms per frame (int or list);
    tags: [(name, from, to)]; palette: list of 'rrggbb' strings."""
    w, h = frames[0].size
    if isinstance(durations, int):
        durations = [durations] * len(frames)
    body = b""
    for i, (im, dur) in enumerate(zip(frames, durations)):
        chunks = []
        if i == 0:
            if palette:
                pal = struct.pack("<III", len(palette), 0, len(palette) - 1) + b"\0" * 8
                for c in palette:
                    pal += struct.pack("<HBBBB", 0, int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)
                chunks.append(_chunk(0x2019, pal))
            layer = struct.pack("<HHHHHHB", 3, 0, 0, 0, 0, 0, 255) + b"\0" * 3 + _string(layer_name)
            chunks.append(_chunk(0x2004, layer))
            if tags:
                t = struct.pack("<H", len(tags)) + b"\0" * 8
                for name, a, b_ in tags:
                    t += struct.pack("<HHBH", a, b_, 0, 0) + b"\0" * 6 + b"\0\0\0" + b"\0" + _string(name)
                chunks.append(_chunk(0x2018, t))
        pixels = im.convert("RGBA").tobytes()
        cel = struct.pack("<HhhBHh", 0, 0, 0, 255, 2, 0) + b"\0" * 5
        cel += struct.pack("<HH", w, h) + zlib.compress(pixels, 9)
        chunks.append(_chunk(0x2005, cel))
        payload = b"".join(chunks)
        fh = struct.pack("<IHHHH", 16 + len(payload), 0xF1FA, min(len(chunks), 0xFFFF), int(dur), 0)
        fh += struct.pack("<I", len(chunks))
        body += fh + payload
    header = struct.pack("<IHHHHHIHII", 128 + len(body), 0xA5E0, len(frames), w, h, 32, 1, 100, 0, 0)
    header += struct.pack("<B3sHBBhhHH", 0, b"\0\0\0", len(palette) if len(palette) < 256 else 0, 1, 1, 0, 0, 16, 16)
    header += b"\0" * (128 - len(header))
    assert len(header) == 128
    with open(path, "wb") as f:
        f.write(header + body)
