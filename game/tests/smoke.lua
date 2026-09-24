-- Quick check: boots, gets through the first-run title (calibrate + language),
-- walks for a second and quits. Use this after every small change; tour.lua for the full route.
return {
    { wait = 10 },
    { raw = "a" }, { wait = 5 },
    { press = "a" }, { wait = 15 },                     -- Norsk (the title ignores A for 10 frames)
    { press = "a" }, { wait = 30 },
    { expect = function(s) return s.map and s.map.name == "gusenby", "in Gusenby" end },
    { hold = "down", frames = 30 },
    { expect = function(s) return s.player.y > 170, "the player moves" end },
    { shot = "smoke" },
    { quit = true },
}
