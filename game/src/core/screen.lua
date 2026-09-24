-- The 240x160 back buffer, integer scaling and GBA-style brightness fades.
local screen = { w = 240, h = 160, scale = 1, ox = 0, oy = 0, fade = 0 }

function screen.init()
    screen.canvas = love.graphics.newCanvas(screen.w, screen.h)
    screen.canvas:setFilter("nearest", "nearest")
    screen.resize(love.graphics.getDimensions())
end

function screen.resize(w, h)
    screen.scale = math.max(1, math.floor(math.min(w / screen.w, h / screen.h)))
    screen.ox = math.floor((w - screen.w * screen.scale) / 2)
    screen.oy = math.floor((h - screen.h * screen.scale) / 2)
end

function screen.begin()
    love.graphics.setCanvas(screen.canvas)
    love.graphics.clear(0, 0, 0, 1)
    love.graphics.setColor(1, 1, 1, 1)
end

function screen.finish()
    if screen.fade > 0 then
        -- the GBA fades with its brightness register in 16 steps; 8 look the same at 60 Hz
        local q = math.floor(math.min(screen.fade, 1) * 8 + 0.5) / 8
        love.graphics.setColor(0, 0, 0, q)
        love.graphics.rectangle("fill", 0, 0, screen.w, screen.h)
        love.graphics.setColor(1, 1, 1, 1)
    end
    love.graphics.setCanvas()
    love.graphics.clear(0, 0, 0, 1)
    love.graphics.draw(screen.canvas, screen.ox, screen.oy, 0, screen.scale, screen.scale)
end

return screen
