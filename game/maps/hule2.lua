-- Mørk hule, room 2: a blown-out candle and something guarding it.
return {
    kind = "room",
    theme = "cave",
    rows = {
        "CCCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCCC",
        "XoooooooooooooX",
        "XoooooooooooooX",
        "ooooooooooooooX",
        "ooooooooooooooX",
        "ooooooooooooooX",
        "XoooooooooooooX",
        "XoooooooooooooX",
        "XXXXXXXXXXXXXXX",
    },
    spawns = {
        start = { 1, 5, dir = "right" },
    },
    exits = {
        west = { to = "hule1", slide = true, span = { 4, 6 } },
    },
    objects = {
        { "candle", 9, 3, lit = false, talk = "candle_out" },
        { "sheet", 11, 4, sheet = "gusen_shadow", anim = "walk_left", talk = "shadow_hiss" },
        { "chest_closed", 12, 2, talk = "chest_locked" },
        { "rock_big", 2, 2 }, { "rock_small", 5, 8 }, { "rock_big", 12, 8 },
    },
}
