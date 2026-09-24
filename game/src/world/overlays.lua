-- Wall caps around interior rooms (drawn over the floor) + their collision.
local assets = require("src.core.assets")

local overlays = {}
local T = 16

function overlays.build(map, frame)
    local inter = assets.sheet("interior")
    local tiles = inter.tiles
    local batch = love.graphics.newSpriteBatch(inter.image, 64, "static")
    local solids = {}
    local gaps = {}
    for _, gx in ipairs(frame.gaps or {}) do gaps[gx] = true end
    -- the wall tiles already exist in the ground; add side caps over the whole height
    for y = 0, map.th - 1 do
        if frame.left then batch:add(inter.quads[tiles.cap_side_l + 1], 0, y * T) end
        if frame.right then batch:add(inter.quads[tiles.cap_side_r + 1], (map.tw - 1) * T, y * T) end
    end
    if frame.left then solids[#solids + 1] = { x = -8, y = 0, w = 12, h = map.h } end
    if frame.right then solids[#solids + 1] = { x = map.w - 4, y = 0, w = 12, h = map.h } end
    if frame.bottom then
        for x = 0, map.tw - 1 do
            if not gaps[x] then
                batch:add(inter.quads[tiles.cap_front + 1], x * T, (map.th - 1) * T)
                solids[#solids + 1] = { x = x * T, y = map.h - 5, w = T, h = 12 }
            end
        end
    end
    -- the back wall is solid down to its skirting board
    if frame.back then solids[#solids + 1] = { x = 0, y = -8, w = map.w, h = frame.back * T + 8 - 2 } end
    local o = { batch = batch, solids = solids }
    function o:draw() love.graphics.draw(self.batch) end
    return o
end

return overlays
