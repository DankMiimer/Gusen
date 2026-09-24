#!/usr/bin/env python3
"""Copy Gusen onto the RG34XXSP (or any PortMaster ports folder).

    python tools/deploy.py                 # copy to the handheld
    python tools/deploy.py --log           # show the handheld's gusen/log.txt
    python tools/deploy.py --ports D:\\roms\\ports   # e.g. the SD card in a reader

The ports folder defaults to $GUSEN_PORTS, else \\\\GAMEBOY\\share\\roms\\ports
(the handheld's network share). Saves on the device (gusen/saves/) are never
touched. gusen/gamedata/ is replaced so no stale files stay behind.
"""
import argparse
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_PORTS = os.environ.get("GUSEN_PORTS", r"\\GAMEBOY\share\roms\ports")
SKIP = {"tests", "__pycache__"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ports", default=DEFAULT_PORTS, help="the device's roms/ports folder")
    ap.add_argument("--log", action="store_true", help="print gusen/log.txt from the device and exit")
    args = ap.parse_args()
    ports = args.ports
    if not os.path.isdir(ports):
        sys.exit(f"Can't reach {ports}. Is the handheld on, on Wi-Fi, with network sharing on? "
                 f"(or pass --ports)")
    gdir = os.path.join(ports, "gusen")
    if args.log:
        p = os.path.join(gdir, "log.txt")
        if not os.path.exists(p):
            sys.exit(f"No log yet at {p}: start Gusen on the handheld first.")
        with open(p, encoding="utf8", errors="replace") as f:
            print(f.read())
        return

    with open(os.path.join(ROOT, "port", "Gusen.sh"), "rb") as f:
        if b"\r\n" in f.read():
            sys.exit("port/Gusen.sh has CRLF line endings: it won't run on the handheld. "
                     "Fix with: git add --renormalize . (see .gitattributes)")
    shutil.copyfile(os.path.join(ROOT, "port", "Gusen.sh"), os.path.join(ports, "Gusen.sh"))
    shutil.copytree(os.path.join(ROOT, "port", "gusen"), gdir, dirs_exist_ok=True)
    gamedata = os.path.join(gdir, "gamedata")
    shutil.rmtree(gamedata, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "game"), gamedata,
                    ignore=lambda d, names: [n for n in names if n in SKIP])
    n = sum(len(files) for _, _, files in os.walk(gamedata))
    print(f"Copied Gusen to {ports} ({n} game files). Start it from Ports on the handheld;")
    print("afterwards `python tools/deploy.py --log` shows what happened.")


if __name__ == "__main__":
    main()
