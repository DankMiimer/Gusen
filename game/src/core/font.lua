-- The Gusen pixel font: 8x10 cells, variable width, white glyphs tinted when drawn.
local utf8 = require("utf8")
local meta = require("assets.ui.font")
local assets = require("src.core.assets")

local font = { lineHeight = meta.line_height, spacing = meta.letter_spacing }
local image, quads

local function load()
    if image then return end
    image = assets.image("ui/font.png")
    quads = {}
    local iw, ih = image:getDimensions()
    local cw, ch = meta.cell[1], meta.cell[2]
    for c, g in pairs(meta.glyphs) do
        local col, row = g.index % meta.columns, math.floor(g.index / meta.columns)
        quads[c] = { q = love.graphics.newQuad(col * cw, row * ch, cw, ch, iw, ih), w = g.width }
    end
end

local function glyph(c)
    load()
    return quads[c] or quads["?"]
end

local function chars(text)
    local out = {}
    for _, code in utf8.codes(text) do out[#out + 1] = utf8.char(code) end
    return out
end
font.chars = chars

function font.width(text)
    local w = 0
    for _, c in ipairs(chars(text)) do w = w + glyph(c).w + font.spacing end
    return math.max(0, w - font.spacing)
end

local function hex(c)
    return tonumber(c:sub(1, 2), 16) / 255, tonumber(c:sub(3, 4), 16) / 255, tonumber(c:sub(5, 6), 16) / 255
end

-- print a single line (no wrapping). `limit` = max characters to show (typewriter).
function font.print(text, x, y, color, shadow, limit)
    load()
    local cs = chars(text)
    local n = limit and math.min(limit, #cs) or #cs
    local function pass(dx, dy, col)
        love.graphics.setColor(hex(col))
        local cx = x
        for i = 1, n do
            local g = glyph(cs[i])
            if cs[i] ~= " " then love.graphics.draw(image, g.q, math.floor(cx + dx), math.floor(y + dy)) end
            cx = cx + g.w + font.spacing
        end
    end
    if shadow then pass(1, 1, shadow) end
    pass(0, 0, color or "ffffff")
    love.graphics.setColor(1, 1, 1, 1)
end

-- word-wrap into lines no wider than maxw; honours explicit "\n"
function font.wrap(text, maxw)
    local lines = {}
    for para in (text .. "\n"):gmatch("(.-)\n") do
        local line = ""
        for word in para:gmatch("%S+") do
            local try = line == "" and word or (line .. " " .. word)
            if font.width(try) <= maxw or line == "" then
                line = try
            else
                lines[#lines + 1] = line
                line = word
            end
        end
        lines[#lines + 1] = line
    end
    return lines
end

return font
