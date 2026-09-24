-- Loads images and sprite sheets described by assets/manifest.lua.
local manifest = require("assets.manifest")

local assets = { images = {}, sheets = {}, manifest = manifest }

function assets.image(path)
    local im = assets.images[path]
    if not im then
        im = love.graphics.newImage("assets/" .. path)
        im:setFilter("nearest", "nearest")
        assets.images[path] = im
    end
    return im
end

-- A sheet: image + one quad per frame + animations + origin.
-- `name` is the manifest key (e.g. "gusen_player", "overworld", "candle").
function assets.sheet(name)
    local s = assets.sheets[name]
    if s then return s end
    local def = manifest.assets[name]
    assert(def, "unknown asset " .. tostring(name))
    local image = assets.image(def.file)
    local iw, ih = image:getDimensions()
    local fw, fh = iw, ih
    if def.frame then fw, fh = def.frame[1], def.frame[2] end
    local quads = {}
    local cols = math.floor(iw / fw)
    for y = 0, math.floor(ih / fh) - 1 do
        for x = 0, cols - 1 do
            quads[#quads + 1] = love.graphics.newQuad(x * fw, y * fh, fw, fh, iw, ih)
        end
    end
    s = {
        image = image, quads = quads, fw = fw, fh = fh, cols = cols,
        anims = def.animations or {}, tiles = def.tiles,
        ox = def.origin and def.origin[1] or math.floor(fw / 2),
        oy = def.origin and def.origin[2] or fh - 1,
    }
    assets.sheets[name] = s
    return s
end

-- Draw frame `i` (0-based, like the manifest) with its origin at (x, y).
function assets.drawFrame(sheet, i, x, y, flip)
    local q = sheet.quads[i + 1]
    if flip then
        love.graphics.draw(sheet.image, q, math.floor(x) + sheet.ox + 1, math.floor(y) - sheet.oy, 0, -1, 1)
    else
        love.graphics.draw(sheet.image, q, math.floor(x) - sheet.ox, math.floor(y) - sheet.oy)
    end
end

return assets
