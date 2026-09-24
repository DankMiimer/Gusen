---
name: playtest
description: Run Gusen's scripted play-tests with LÖVE and inspect the screenshots. Use after any change under game/ or tools/, and whenever asked to run, test, start or screenshot the game.
---

# Play-test Gusen

1. If art or tools changed: `python tools/make_assets.py` (fails loudly on
   palette / 15-colour violations; fix the art, don't loosen the check).
2. Run the tests, in both render modes:
   ```
   python tools/run_tests.py
   python tools/run_tests.py --gles
   ```
   On Windows the runner prefers `lovec.exe` from `C:\Program Files\LOVE\`;
   set `LOVE=<path>` if it's elsewhere. A failing run prints the report and a
   Lua stack trace if there was an error.
3. **Look at the screenshots** in `test-output/<test>/*.png` (720×480, what the
   RG34XXSP shows). Check: nothing blurry or misaligned, sprites sorted
   correctly (feet lower = in front), text fits its box in **both** languages,
   HUD not covering important things.
4. New feature? Add steps to an existing test or a new `game/tests/<name>.lua`
   (step reference: `game/tests/README.md`), and make it `expect` the new
   behaviour, not just screenshot it.
5. To play by hand: `love game` (Windows: `"Test on PC.bat"`). Keyboard:
   arrows, Z = A, X = B, Enter = Start.

Report results with the pass counts and the relevant screenshots.
