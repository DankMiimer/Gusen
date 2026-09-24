-- Spaghetti-Gusen's inn: one screen. Mega furniture on planks, a cobblestone kitchen.
local function at(name, x, y, extra)
    local o = { "at", x, y, name = name }
    for k, v in pairs(extra or {}) do o[k] = v end
    return o
end

return {
    kind = "room",
    theme = "interior",
    rows = {
        "wwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwww",
        "oooofffffffffff",
        "oooofffffffffff",
        "oooofffffffffff",
        "oooofffffffffff",
        "fffffffffffffff",
        "fffffffffffffff",
        "fffffffffffffff",
        "fffffffffffffff",
    },
    frame = { left = true, right = true, bottom = true, gaps = { 7 } },
    spawns = {
        start = { 7, 8, dir = "up" },
        door = { 7, 8, dir = "up" },
    },
    exits = {
        south = { to = "gusenby", spawn = "from_kro", span = { 7, 7 } },
    },
    objects = {
        at("window_view", 150, 5), at("door", 66, 3),
        at("cabinet", 90, 13), at("bookshelf", 170, 13), at("nightstand", 218, 13),
        at("potted_plant", 156, 22),
        at("stand_candle", 124, 14, { talk = "candle_lit" }),
        at("table_big_wood", 6, 30),
        at("roast", 12, 36, { solid = false, layer = "top" }), at("salad", 18, 52, { solid = false, layer = "top" }),
        at("table_big", 97, 64),
        at("chair", 113, 50), at("stool", 84, 72), at("stool", 84, 92), at("stool", 144, 72), at("stool", 144, 92),
        at("cupcakes", 104, 72, { solid = false, layer = "top" }),
        at("fruit_bowl", 121, 80, { solid = false, layer = "top" }),
        { "at", 108, 88, kind = "candle_dish", layer = "top" },
        at("table_red", 186, 64), at("table_green", 186, 100), at("table_square", 212, 82),
        at("stool", 172, 66), at("stool", 202, 66), at("stool", 172, 102), at("stool", 202, 102),
        { "at", 187, 60, kind = "candle_dish", layer = "top" },
        at("side_table2", 12, 110, { talk = "menu_food" }), at("side_table2", 34, 110, { talk = "menu_food" }),
        at("side_table2", 56, 110, { talk = "menu_food" }),
        at("roast", 10, 106, { solid = false, layer = "top" }), at("salad", 26, 106, { solid = false, layer = "top" }),
        at("cupcakes", 57, 106, { solid = false, layer = "top" }),
        at("rug", 94, 144), at("basket", 214, 124),
        { "npc", 3, 4, dx = -6, dy = 1, who = "spaghettigusen", dir = "right", talk = "talk_spaghetti",
          name = "name_spaghetti" },
        { "npc", 13, 5, dx = 3, dy = 1, who = "lunagusen", dir = "left", talk = "talk_luna", name = "name_luna" },
    },
}
