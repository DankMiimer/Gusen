-- Hearts top-left, A/B item slots top-right, coins bottom-left (GBA Zelda layout).
local assets = require("src.core.assets")
local font = require("src.core.font")

local hud = {}

function hud.draw(state)
    local hearts = assets.sheet("hearts")
    local hp, max = state.hp, state.maxHp
    for i = 0, max / 2 - 1 do
        local left = hp - i * 2
        local f = left >= 2 and 0 or (left == 1 and 1 or 2)
        assets.drawFrame(hearts, f, 3 + i * 9 + hearts.ox, 3 + hearts.oy)
    end
    love.graphics.draw(assets.image("ui/slot_b.png"), 194, 2)
    love.graphics.draw(assets.image("ui/slot_a.png"), 216, 2)
    if state.hasSword then
        assets.drawFrame(assets.sheet("sword"), 0, 218 + 8, 4 + 15)
    end
    if state.bItem then
        local im = assets.image("mega/" .. state.bItem .. ".png")
        local w, h = im:getDimensions()
        love.graphics.draw(im, 196 + math.floor((16 - w) / 2), 4 + math.floor((16 - h) / 2))
    end
    local icons = assets.sheet("icons")
    assets.drawFrame(icons, 0, 4 + icons.ox, 149 + icons.oy)
    font.print(string.format("%03d", state.coins), 14, 148, "ffffff", "000000")
end

return hud
