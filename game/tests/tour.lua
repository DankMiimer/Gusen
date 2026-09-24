-- Plays through everything M0 has: title + calibration + language, the village,
-- talking, the inn (room), the cave rooms (slide), the pause menu, the forest.
-- Run: GUSEN_AUTOTEST=tour love game
local function tp(x, y, dir)
    return { call = function(s)
        s.player.x, s.player.y = x, y
        if dir then s.player.dir = dir end
        s:updateCamera()
    end }
end
local function where(label)
    return { log = function(s) return string.format("%s: map=%s x=%.1f y=%.1f", label, s.map.name, s.player.x, s.player.y) end }
end

return {
    { wait = 20 }, { shot = "01_title" },
    { raw = "a" }, { wait = 10 },                           -- "press A": calibrates the pad
    { shot = "02_language" },
    { press = "down" }, { press = "a" }, { wait = 10 },     -- English
    { press = "a" }, { wait = 40 },
    { shot = "03_village" }, where("start"),
    { hold = "right", frames = 60 }, where("after walking right"),
    { expect = function(s) return s.player.x > 250, "walked right" end },
    { shot = "04_walk" },

    -- collision: walk into the pond from the east
    tp(104, 190, "left"), { hold = "left", frames = 40 }, where("pond"),
    { expect = function(s) return s.player.x >= 96, "stopped by the pond edge" end },

    -- talk to Lanterne-Gusen (standing at tile 11,9)
    tp(184, 166, "up"), { press = "a" }, { wait = 70 }, { shot = "05_dialog" },
    { expect = function(s) return s.dialog ~= nil, "dialog opened" end },
    { press = "a" }, { wait = 90 }, { press = "a" }, { wait = 5 },
    { expect = function(s) return s.dialog == nil, "dialog closed" end },

    -- into the inn through the door in the cliff
    tp(352, 100, "up"), { hold = "up", frames = 30 }, { wait = 40 },
    { expect = function(s) return s.map.name == "kro", "entered the inn" end },
    { shot = "06_kro" },
    { hold = "left", frames = 30 }, { shot = "07_kro_walk" },
    tp(120, 140, "down"), { hold = "down", frames = 30 }, { wait = 40 },
    { expect = function(s) return s.map.name == "gusenby", "back in the village" end },
    where("left the inn"),

    -- the cave: two single-screen rooms that slide
    tp(112, 100, "up"), { hold = "up", frames = 20 }, { wait = 40 },
    { expect = function(s) return s.map.name == "hule1", "entered the cave" end },
    { shot = "08_hule1" },
    tp(226, 88, "right"), { hold = "right", frames = 24 }, { shot = "09_slide" },
    { wait = 40 }, { expect = function(s) return s.map.name == "hule2", "slid into room 2" end },
    { shot = "10_hule2" },

    -- pause menu: switch to Norwegian
    { press = "start" }, { wait = 2 }, { shot = "11_pause" },
    { press = "down" }, { press = "a" }, { wait = 2 }, { shot = "12_pause_norsk" },
    { press = "start" }, { wait = 5 },

    -- the forest
    { call = function(s) s:startFade("skogen", "west") end }, { wait = 40 },
    { shot = "13_skogen" },
    { hold = "right", frames = 50 }, { hold = "up", frames = 40 }, where("forest"),
    tp(368, 64, "up"), { wait = 2 }, { shot = "14_shrine" },
    { press = "a" }, { wait = 60 }, { shot = "15_candle_out_norsk" },
    { press = "a" }, { wait = 5 },
    { quit = true },
}
