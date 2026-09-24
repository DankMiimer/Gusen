#!/usr/bin/env python3
"""Build the PortMaster package.

    python3 tools/package_port.py

dist/ports/ is laid out exactly like the handheld's roms/ports folder
(Gusen.sh + gusen/), and dist/gusen.zip is the same thing zipped the way
PortMaster expects. On Windows, "Install to RG34XXSP.bat" does the same copy
straight onto the device instead.
"""
import os
import shutil
import zipfile

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST = os.path.join(ROOT, "dist")
PORTS = os.path.join(DIST, "ports")
SKIP_DIRS = {"tests", "__pycache__"}


def screenshot(dst):
    """PortMaster wants 4:3, at least 640x480, showing letterboxing: game at 2x, centred."""
    shot = Image.open(os.path.join(ROOT, "docs", "img", "mockup_gameplay_1x.png")).convert("RGB")
    canvas = Image.new("RGB", (640, 480), (0, 0, 0))
    big = shot.resize((480, 320), Image.NEAREST)
    canvas.paste(big, (80, 80))
    canvas.save(dst)


def main():
    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(PORTS)
    shutil.copy2(os.path.join(ROOT, "port", "Gusen.sh"), os.path.join(PORTS, "Gusen.sh"))
    shutil.copytree(os.path.join(ROOT, "port", "gusen"), os.path.join(PORTS, "gusen"))
    shutil.copytree(os.path.join(ROOT, "game"), os.path.join(PORTS, "gusen", "gamedata"),
                    ignore=lambda d, names: [n for n in names if n in SKIP_DIRS])
    screenshot(os.path.join(PORTS, "gusen", "screenshot.png"))
    with open(os.path.join(PORTS, "Gusen.sh"), "rb") as f:
        assert b"\r\n" not in f.read(), "Gusen.sh must use LF line endings"
    zpath = os.path.join(DIST, "gusen.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(PORTS):
            for fn in files:
                full = os.path.join(base, fn)
                rel = os.path.relpath(full, PORTS)
                info = zipfile.ZipInfo.from_file(full, rel)
                if fn.endswith(".sh"):
                    info.external_attr = (0o755 << 16)
                with open(full, "rb") as f:
                    z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)
    n = sum(len(f) for _, _, f in os.walk(PORTS))
    size = os.path.getsize(zpath) / 1024
    print(f"dist/ports: {n} files   dist/gusen.zip: {size:.0f} KiB")


if __name__ == "__main__":
    main()
