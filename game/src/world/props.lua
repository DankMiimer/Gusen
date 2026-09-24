-- Static things in the world: trees, furniture, signs, candles, NPC-less decor.
-- Each prop: position = the point on the ground (feet), a sprite, an optional
-- solid box around the feet, and an optional `talk` text key.
local assets = require("src.core.assets")
local Anim = require("src.core.anim")

local props = {}

local ATLAS = { bush = { 12, 8 }, bush_cut = false, rock_small = { 10, 6 }, rock_big = { 14, 9 },
                sign = { 12, 5 }, chest_closed = { 14, 8 }, chest_open = { 14, 8 }, pot = { 10, 6 },
                fence = { 16, 4 }, fence_post = { 16, 4 }, stump = { 12, 6 },
                grass_redflowers = false, tallgrass_cut = false }

-- solid box sizes (w, h) at the feet for single images
local IMAGE = {
    tree = { file = "tiles/tree.png", ox = 16, oy = 38, solid = { 10, 6 } },
    cave = { file = "tiles/cave_mouth.png", ox = 0, oy = 0, solid = false, layer = "ground" },
}
local MEGA_SOLID = {
    rug = false, cobble_patch = false, window_view = false, window_small = false, door = false,
    potted_plant = { 8, 4 }, pine = { 8, 5 }, pine_trio = { 30, 6 }, log = { 14, 6 },
    table_big = { 44, 30 }, table_big_wood = { 44, 30 }, table_pedestal = { 8, 6 },
    sunflower = false, white_flower = false, cupcakes = false, salad = false, roast = false,
    fruit_bowl = false, lantern = false, wallet = false,
}
local MEGA_LAYER = { rug = "floor", cobble_patch = "floor", window_view = "wall", window_small = "wall",
                     door = "wall" }

local Prop = {}
Prop.__index = Prop

-- def: {kind, x=, y=} in pixels (feet) plus options from the map file
function props.new(def)
    local p = setmetatable({ x = def.x, y = def.y, talk = def.talk, name = def.name,
                             layer = def.layer, flip = def.flip }, Prop)
    local kind = def.kind
    local solid
    if kind == "atlas" then
        -- a 16x16 tile from the overworld atlas, drawn as an object
        p.sheet = assets.sheet("overworld")
        p.frame = p.sheet.tiles[def.name]
        assert(p.frame, "no atlas tile " .. def.name)
        solid = ATLAS[def.name]
        if def.name == "tallgrass_0" then
            p.anim = Anim.new(p.sheet, "tallgrass")
            solid = false
        elseif def.name == "flowers_sway_0" then
            p.anim = Anim.new(p.sheet, "flowers")
            solid = false
        end
        p.ox, p.oy = 8, 15
    elseif kind == "mega" then
        p.image = assets.image("mega/" .. def.name .. ".png")
        local w, h = p.image:getDimensions()
        p.ox, p.oy = math.floor(w / 2), h - 1
        solid = MEGA_SOLID[def.name]
        if solid == nil then solid = { w - 2, math.min(8, math.floor(h / 3)) } end
        p.layer = p.layer or MEGA_LAYER[def.name]
    elseif kind == "candle" then
        p.sheet = assets.sheet("candle")
        p.frame = def.lit == false and 3 or 0
        solid = { 8, 4 }
    elseif kind == "candle_dish" then
        p.sheet = assets.sheet("candle_dish")
        p.frame = def.lit == false and 3 or 0
        solid = false
    elseif IMAGE[kind] then
        local d = IMAGE[kind]
        p.image = assets.image(d.file)
        p.ox, p.oy = d.ox, d.oy
        solid = d.solid
        p.layer = p.layer or d.layer
    elseif kind == "legacy" then
        -- one of your existing animated sprites (frog, fluesopp, coin, ...)
        p.sheet = assets.sheet(def.name)
        local first = next(p.sheet.anims)
        p.anim = Anim.new(p.sheet, def.anim or first)
        solid = def.solid or { 10, 5 }
    elseif kind == "sheet" then
        -- a frame or animation from a generated sheet (e.g. a Skyggegusen standing guard)
        p.sheet = assets.sheet(def.sheet)
        if def.anim then p.anim = Anim.new(p.sheet, def.anim) else p.frame = def.frame or 0 end
        solid = def.solid or { 10, 5 }
    else
        error("unknown prop kind " .. tostring(kind))
    end
    if def.solid ~= nil then solid = def.solid end
    if solid then
        p.box = { x = p.x - solid[1] / 2, y = p.y - solid[2] + 1, w = solid[1], h = solid[2] }
    end
    return p
end

function Prop:update()
    if self.anim then self.anim:update() end
end

function Prop:draw()
    if self.anim then
        self.anim:draw(self.x, self.y, self.flip)
    elseif self.sheet then
        assets.drawFrame(self.sheet, self.frame, self.x, self.y, self.flip)
    else
        love.graphics.draw(self.image, math.floor(self.x) - self.ox, math.floor(self.y) - self.oy)
    end
end

-- screen-space bounds for culling
function Prop:bounds()
    local w, h
    if self.image then w, h = self.image:getDimensions() else w, h = self.sheet.fw, self.sheet.fh end
    return self.x - (self.ox or self.sheet.ox), self.y - (self.oy or self.sheet.oy), w, h
end

return props
