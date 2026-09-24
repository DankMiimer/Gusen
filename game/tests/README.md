# Scripted tests

Each file returns a list of steps. `tools/run_tests.py` runs them all (or
`GUSEN_AUTOTEST=<name> love game` for one). Tests always start from a fresh
first boot: they use their own settings file, never the player's.

| Step | Does |
|---|---|
| `{ wait = n }` | wait n frames (1/60 s each) |
| `{ press = "a" }` | tap a virtual button: up down left right a b l r start select |
| `{ hold = "right", frames = n }` | hold a button for n frames |
| `{ raw = "a" }` | pretend a gamepad button was pressed (for the title's A calibration) |
| `{ shot = "name" }` | screenshot → `test-output/<test>/name.png` |
| `{ call = function(scene) ... end }` | do anything (e.g. teleport the player) |
| `{ log = "text" or function(scene) }` | write to the report |
| `{ expect = function(scene) return ok, "what" end }` | PASS/FAIL check |
| `{ quit = true }` | end (exit code 1 if anything failed) |

`scene` is the top scene (usually `src/scenes/play.lua`: `scene.player`,
`scene.map`, `scene.dialog`, `scene.state`, `scene:startFade(map, spawn)`).
