-- Mørk hule, room 1. One screen; the room to the east slides in.
return {
    kind = "room",
    theme = "cave",
    rows = {
        "CCCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCCC",
        "XoooooooooooooX",
        "XoooooooooooooX",
        "Xoooooooooooooo",
        "Xoooooooooooooo",
        "Xoooooooooooooo",
        "XoooooooooooooX",
        "XoooooooooooooX",
        "XXXXXXoooXXXXXX",
    },
    spawns = {
        start = { 7, 8, dir = "up" },
        south = { 7, 8, dir = "up" },
    },
    exits = {
        east = { to = "hule2", slide = true, span = { 4, 6 } },
        south = { to = "gusenby", spawn = "from_cave", span = { 6, 8 } },
    },
    objects = {
        { "candle", 7, 2, talk = "candle_lit" },
        { "rock_big", 2, 3 }, { "rock_small", 3, 7 }, { "rock_small", 12, 8 },
        { "rock_big", 11, 2 }, { "pot", 4, 2 }, { "pot", 5, 2 },
    },
}
