#!/usr/bin/env python3
"""Run the game's scripted tests (game/tests/*.lua) and collect the results.

    python tools/run_tests.py              # every test
    python tools/run_tests.py smoke        # one test
    python tools/run_tests.py --gles       # render like the handheld (OpenGL ES)

Screenshots and reports end up in test-output/<test>/ (git-ignored). Exit code
is 0 only if every test passed. Finds LÖVE via $LOVE, then PATH, then the
default Windows install (prefers lovec.exe, the console build).
"""
import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GAME = os.path.join(ROOT, "game")
OUT = os.path.join(ROOT, "test-output")
TIMEOUT = 300


def find_love():
    if os.environ.get("LOVE"):
        return os.environ["LOVE"]
    for name in ("lovec", "love"):
        p = shutil.which(name)
        if p:
            return p
    for base in (r"C:\Program Files\LOVE", r"C:\Program Files (x86)\LOVE"):
        for exe in ("lovec.exe", "love.exe"):
            p = os.path.join(base, exe)
            if os.path.exists(p):
                return p
    sys.exit("Could not find LÖVE 11.5. Install it (https://love2d.org) or set LOVE=path/to/love.")


def save_dir(env):
    """Where LÖVE keeps files for identity 'gusen' (unfused game)."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ["APPDATA"], "LOVE", "gusen")
    if system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/LOVE/gusen")
    base = env.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, "love", "gusen")


def run(test, love, gles):
    env = dict(os.environ, GUSEN_AUTOTEST=test)
    if gles:
        env["LOVE_GRAPHICS_USE_OPENGLES"] = "1"
    tmp = None
    if platform.system() == "Linux":
        tmp = tempfile.mkdtemp(prefix="gusen-test-")
        env["XDG_DATA_HOME"] = tmp      # isolated save dir on Linux
    sdir = save_dir(env)
    for old in glob.glob(os.path.join(sdir, "autotest_*")):
        os.remove(old)
    cmd = [love, GAME]
    if platform.system() == "Linux" and not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 720x480x24"] + cmd
    try:
        proc = subprocess.run(cmd, env=env, cwd=ROOT, timeout=TIMEOUT,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        code = proc.returncode
    except subprocess.TimeoutExpired:
        code = "timeout"
    dest = os.path.join(OUT, test + ("-gles" if gles else ""))
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest)
    report = ""
    rp = os.path.join(sdir, "autotest_report.txt")
    if os.path.exists(rp):
        with open(rp, encoding="utf8") as f:
            report = f.read()
        shutil.copy2(rp, os.path.join(dest, "report.txt"))
    for png in glob.glob(os.path.join(sdir, "autotest_*.png")):
        shutil.copy2(png, os.path.join(dest, os.path.basename(png)[len("autotest_"):]))
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    passed = report.count("[autotest] PASS")
    failed = report.count("[autotest] FAIL") + report.count("[autotest] ERROR")
    finished = "[autotest] done" in report
    ok = code == 0 and finished and failed == 0
    return ok, passed, failed, code, report, dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="*", help="test names (default: all in game/tests)")
    ap.add_argument("--gles", action="store_true", help="force OpenGL ES like the RG34XXSP")
    ap.add_argument("-v", "--verbose", action="store_true", help="print full reports")
    args = ap.parse_args()
    tests = args.tests or sorted(os.path.splitext(os.path.basename(p))[0]
                                 for p in glob.glob(os.path.join(GAME, "tests", "*.lua")))
    love = find_love()
    print(f"LÖVE: {love}")
    all_ok = True
    for t in tests:
        ok, passed, failed, code, report, dest = run(t, love, args.gles)
        all_ok &= ok
        status = "OK  " if ok else "FAIL"
        print(f"{status} {t:12s} {passed} passed, {failed} failed, exit {code}  → {os.path.relpath(dest, ROOT)}")
        if args.verbose or not ok:
            for line in report.splitlines():
                if not line.startswith("[autotest] screenshot"):
                    print("     " + line)
            if not report:
                print("     (no report: LÖVE didn't get as far as starting the test)")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
