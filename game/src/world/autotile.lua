-- Picks edge/corner variants for regions (path, water) exactly like
-- tools/previews.py, so the game and the mockups agree.
local autotile = {}

-- inside(x, y) -> bool; out-of-map cells count as "same as nearest cell".
function autotile.key(inside, x, y)
    local n, s, w, e = inside(x, y - 1), inside(x, y + 1), inside(x - 1, y), inside(x + 1, y)
    if not n and not w then return "nw" end
    if not n and not e then return "ne" end
    if not s and not w then return "sw" end
    if not s and not e then return "se" end
    if not n then return "n" end
    if not s then return "s" end
    if not w then return "w" end
    if not e then return "e" end
    if not inside(x - 1, y - 1) then return "inw" end
    if not inside(x + 1, y - 1) then return "ine" end
    if not inside(x - 1, y + 1) then return "isw" end
    if not inside(x + 1, y + 1) then return "ise" end
    return "c"
end

return autotile
