-- A map is either an "area" (any size, the camera scrolls) or a "room"
-- (exactly one 15x10 screen; neighbouring rooms slide like on the GBA).
--
-- Maps are Lua files in maps/: ASCII rows for the ground plus a list of
-- objects. Paths, water and cliffs are autotiled when the map loads.
local assets = require("src.core.assets")
local autotile = require("src.world.autotile")
local props = require("src.world.props")
local NPC = require("src.world.npc")

local T = 16
local Map = {}
Map.__index = Map

-- ground characters -------------------------------------------------------------
-- overworld: . grass  , red flowers  ; yellow flowers  P path  W water
--            H plateau (high ground)  C cliff face  K cave (top, solid)
--            k cave floor (walkable)  D cliff with a door (walkable)  T pine forest
-- interior:  w back wall  f planks  F dark planks  o cobblestone  X void
-- cave:      C cliff wall  o cobblestone  X void
local SOLID = { W = true, H = true, C = true, K = true, T = true, X = true, w = true }

local function hash(x, y) return (x * 73856093 + y * 19349663) % 1000 end

function Map.load(name)
    local def = require("maps." .. name)
    local m = setmetatable({ name = name, def = def, kind = def.kind or "area", theme = def.theme or "overworld",
                             rows = def.rows, objects = {}, npcs = {}, doors = {}, rects = {} }, Map)
    m.tw, m.th = #def.rows[1], #def.rows
    m.w, m.h = m.tw * T, m.th * T
    for y, row in ipairs(def.rows) do
        assert(#row == m.tw, name .. ": row " .. y .. " has " .. #row .. " chars, expected " .. m.tw)
    end
    if m.kind == "room" then assert(m.tw == 15 and m.th == 10, name .. ": rooms are 15x10 tiles") end
    m:buildGround()
    m:buildObjects()
    return m
end

function Map:char(x, y)
    x = math.min(math.max(x, 0), self.tw - 1)
    y = math.min(math.max(y, 0), self.th - 1)
    local row = self.rows[y + 1]
    return row:sub(x + 1, x + 1)
end

function Map:solidAt(tx, ty)
    if self.open and self.open[ty * self.tw + tx] then return false end
    return SOLID[self:char(tx, ty)] or false
end

-- ground tiles ------------------------------------------------------------------
function Map:buildGround()
    local ow = assets.sheet("overworld")
    local tiles = ow.tiles
    self.batch = love.graphics.newSpriteBatch(ow.image, self.tw * self.th * 2, "static")
    self.water = {}
    for f = 0, 2 do self.water[f] = love.graphics.newSpriteBatch(ow.image, 256, "static") end
    local inter = self.theme ~= "overworld" and assets.sheet("interior") or nil
    if inter then self.ibatch = love.graphics.newSpriteBatch(inter.image, self.tw * self.th * 2, "static") end

    local rows = self.rows
    local function isChar(set)
        return function(x, y) return set:find(self:char(x, y), 1, true) ~= nil end
    end
    local inPath, inWater = isChar("PkD"), isChar("W")
    local cliffy = isChar("CKkD")

    local function put(batch, sheet, index, x, y)
        batch:add(sheet.quads[index + 1], x * T, y * T)
    end
    local function grass(x, y)
        local h = hash(x, y) % 10
        return tiles[h < 6 and "grass_c" or (h < 8 and "grass_a" or "grass_b")]
    end

    for y = 0, self.th - 1 do
        for x = 0, self.tw - 1 do
            local c = rows[y + 1]:sub(x + 1, x + 1)
            if c == "." or c == "T" then
                put(self.batch, ow, grass(x, y), x, y)
            elseif c == "," then
                put(self.batch, ow, tiles.grass_redflowers, x, y)
            elseif c == ";" then
                put(self.batch, ow, tiles.grass_yellowflowers, x, y)
            elseif c == "P" then
                put(self.batch, ow, tiles["path_" .. autotile.key(inPath, x, y)], x, y)
            elseif c == "W" then
                local k = autotile.key(inWater, x, y)
                for f = 0, 2 do put(self.water[f], ow, tiles["water" .. f .. "_" .. k], x, y) end
            elseif c == "H" then
                local east, west = not isChar("H")(x + 1, y), not isChar("H")(x - 1, y)
                local name = east and "plateau_e" or (west and "plateau_w" or nil)
                put(self.batch, ow, name and tiles[name] or grass(x, y), x, y)
            elseif cliffy(x, y) then
                local top = not cliffy(x, y - 1) or y == 0
                local base = not cliffy(x, y + 1) or y == self.th - 1
                local r = top and "top" or (base and "base" or "mid")
                if top and base then r = "base" end
                local left, right = not cliffy(x - 1, y), not cliffy(x + 1, y)
                local col = left and "l" or (right and "r" or (x % 2 == 0 and "m1" or "m2"))
                put(self.batch, ow, tiles["cliff_" .. r .. "_" .. col], x, y)
            elseif inter and (c == "f" or c == "F" or c == "o") then
                local n = c == "f" and "floor_planks" or (c == "F" and "floor_planks_dark" or "cobble")
                put(self.ibatch, inter, inter.tiles[n], x, y)
            elseif inter and c == "w" then
                local top = self:char(x, y - 1) ~= "w" or y == 0
                put(self.ibatch, inter, inter.tiles[top and "wall_top" or "wall_bottom"], x, y)
            elseif inter and c == "X" then
                put(self.ibatch, inter, inter.tiles.void, x, y)
            end
        end
    end
    -- room frame: side caps, front cap with a doorway gap (interior rooms)
    local frame = self.def.frame
    if frame and inter then
        local names = { left = "side_l", right = "side_r" }
        local ov = require("src.world.overlays")
        self.overlays = ov.build(self, frame)
    end
end

-- objects -----------------------------------------------------------------------
-- positions: {tx, ty} = the tile the thing stands on (feet at its bottom centre),
-- plus optional dx/dy pixel nudges; or at = {x, y} for the sprite's top-left.
local function feet(o)
    if o.at then return o.at[1], o.at[2] end
    return o[2] * T + 8 + (o.dx or 0), o[3] * T + 15 + (o.dy or 0)
end

function Map:buildObjects()
    -- pines for every forest cell, jittered so the forest doesn't look like a grid
    for y = 0, self.th - 1 do
        for x = 0, self.tw - 1 do
            if self.rows[y + 1]:sub(x + 1, x + 1) == "T" then
                local h = hash(x, y)
                local p = props.new({ kind = "mega", name = "pine",
                                      x = x * T + 8 + (h % 7) - 3, y = y * T + 13 + (h % 5), solid = false })
                self.objects[#self.objects + 1] = p
            end
        end
    end
    self.open = {}
    for _, o in ipairs(self.def.objects or {}) do
        local kind = o[1]
        local x, y = feet(o)
        if kind == "npc" then
            local n = NPC.new({ who = o.who, x = x, y = y, dir = o.dir, talk = o.talk, name = o.name })
            self.npcs[#self.npcs + 1] = n
            self.objects[#self.objects + 1] = n
        elseif kind == "door" then
            -- a trigger area; `open` makes the tiles under it walkable
            local w, h = o.w or 1, o.h or 1
            local d = { x = o[2] * T, y = o[3] * T, w = w * T, h = h * T, to = o.to, spawn = o.spawn }
            self.doors[#self.doors + 1] = d
            for yy = o[3], o[3] + h - 1 do
                for xx = o[2], o[2] + w - 1 do self.open[yy * self.tw + xx] = true end
            end
        elseif kind == "at" then
            -- top-left placement for furniture (matches the mockups)
            local p = props.new({ kind = o.kind or "mega", name = o.name, x = 0, y = 0, talk = o.talk,
                                  solid = o.solid, layer = o.layer, flip = o.flip, lit = o.lit })
            local ox, oy = p.ox or p.sheet.ox, p.oy or p.sheet.oy
            p.x, p.y = o[2] + ox, o[3] + oy
            if p.box then
                local bw, bh = p.box.w, p.box.h
                p.box = { x = p.x - bw / 2, y = p.y - bh + 1, w = bw, h = bh }
            end
            self.objects[#self.objects + 1] = p
        else
            local def = { kind = kind, name = o.name, x = x, y = y, talk = o.talk, solid = o.solid,
                          layer = o.layer, lit = o.lit, anim = o.anim, sheet = o.sheet, frame = o.frame,
                          flip = o.flip }
            if kind == "atlas" or kind == "mega" or kind == "legacy" or kind == "sheet" then
                -- shorthand: {"mega", tx, ty, name = "..."}
            elseif kind ~= "candle" and kind ~= "candle_dish" and kind ~= "tree" and kind ~= "cave" then
                def.kind, def.name = "atlas", kind   -- {"bush", tx, ty} -> atlas tile
            end
            if kind == "cave" then def.x, def.y = o[2] * T, o[3] * T end
            self.objects[#self.objects + 1] = props.new(def)
        end
    end
    -- things lying on furniture (food on a table) sort together with that furniture
    for _, o in ipairs(self.objects) do
        if o.layer == "top" then
            for _, f in ipairs(self.objects) do
                if f ~= o and f.box and not f.layer then
                    local x, y, w, h = f:bounds()
                    if o.x >= x and o.x <= x + w and o.y >= y and o.y <= f.y then
                        o.sorty = f.y + 0.5
                        break
                    end
                end
            end
            o.layer = nil
        end
    end
    for _, r in ipairs(self.def.solids or {}) do self.rects[#self.rects + 1] = r end
    if self.overlays then
        for _, r in ipairs(self.overlays.solids) do self.rects[#self.rects + 1] = r end
    end
end

function Map:spawn(name)
    local s = (self.def.spawns or {})[name or "start"] or self.def.spawns.start
    return s[1] * T + 8 + (s.dx or 0), s[2] * T + 15 + (s.dy or 0), s.dir or "down"
end

-- collision -----------------------------------------------------------------------
local function overlap(a, b)
    return a.x < b.x + b.w and b.x < a.x + a.w and a.y < b.y + b.h and b.y < a.y + a.h
end
Map.overlap = overlap

-- Is the box blocked? `exits` lets the player leave the map on sides that have one.
function Map:blocked(box, ignore)
    local x0, y0 = math.floor(box.x / T), math.floor(box.y / T)
    local x1, y1 = math.floor((box.x + box.w - 0.001) / T), math.floor((box.y + box.h - 0.001) / T)
    local exits = self.def.exits or {}
    -- an exit may be limited to a span of tiles along its edge
    local function open(e, lo, hi)
        return e and (not e.span or (lo >= e.span[1] and hi <= e.span[2]))
    end
    if box.x < 0 and not open(exits.west, y0, y1) then return true end
    if box.y < 0 and not open(exits.north, x0, x1) then return true end
    if box.x + box.w > self.w and not open(exits.east, y0, y1) then return true end
    if box.y + box.h > self.h and not open(exits.south, x0, x1) then return true end
    for ty = y0, y1 do
        for tx = x0, x1 do
            if tx >= 0 and ty >= 0 and tx < self.tw and ty < self.th and self:solidAt(tx, ty) then
                return true
            end
        end
    end
    for _, r in ipairs(self.rects) do
        if overlap(box, r) then return true end
    end
    for _, o in ipairs(self.objects) do
        if o ~= ignore and o.box and overlap(box, o.box) then return true end
    end
    return false
end

-- drawing ----------------------------------------------------------------------------
function Map:update(frame)
    for _, o in ipairs(self.objects) do o:update() end
end

function Map:drawGround(frame)
    love.graphics.draw(self.batch)
    if self.ibatch then love.graphics.draw(self.ibatch) end
    love.graphics.draw(self.water[math.floor(frame / 15) % 3])
    if self.overlays then self.overlays:draw() end
    for _, o in ipairs(self.objects) do
        if o.layer == "ground" or o.layer == "floor" or o.layer == "wall" then o:draw() end
    end
end

-- everything that stands on the ground, sorted by feet y (things lower down are in front)
function Map:drawSorted(extra, cx, cy)
    local list = {}
    for _, o in ipairs(self.objects) do
        if not o.layer then
            local x, y, w, h = o:bounds()
            if x + w >= cx - 8 and x <= cx + 248 and y + h >= cy - 8 and y <= cy + 168 then
                list[#list + 1] = o
            end
        end
    end
    for _, e in ipairs(extra) do list[#list + 1] = e end
    table.sort(list, function(a, b)
        local ay, by = a.sorty or a.y, b.sorty or b.y
        if ay == by then return a.x < b.x end
        return ay < by
    end)
    for _, o in ipairs(list) do o:draw() end
end

return Map
