-- Walking around the world: maps, camera, doors, room slides, talking.
local Map = require("src.world.map")
local Player = require("src.world.player")
local Dialog = require("src.ui.dialog")
local hud = require("src.ui.hud")
local input = require("src.core.input")
local screen = require("src.core.screen")
local scenes = require("src.core.scenes")

local Play = {}
Play.__index = Play

local FADE = 16      -- frames to fade out (and again to fade in)
local SLIDE = 40     -- frames for a room-to-room slide

function Play.new(mapName, spawn)
    local p = setmetatable({ frame = 0, cam = { x = 0, y = 0 } }, Play)
    p.state = { hp = 6, maxHp = 6, coins = 0, hasSword = true, bItem = nil }
    p:enter(Map.load(mapName), spawn)
    screen.fade = 1
    p.transition = { kind = "fadein", t = 0 }
    return p
end

function Play:enter(map, spawn, keepPlayer)
    self.map = map
    if not keepPlayer then
        local x, y, dir = map:spawn(spawn)
        if self.player then
            self.player.x, self.player.y, self.player.dir = x, y, dir
        else
            self.player = Player.new(x, y, dir)
        end
    end
    for _, d in ipairs(map.doors) do d.armed = not Map.overlap(self.player:box(), d) end
    self:updateCamera()
end

function Play:updateCamera()
    local m, pl = self.map, self.player
    if m.kind == "room" then
        self.cam.x, self.cam.y = 0, 0
        return
    end
    local cx, cy = pl.x - 120, pl.y - 88
    if m.w <= 240 then cx = (m.w - 240) / 2 else cx = math.min(math.max(cx, 0), m.w - 240) end
    if m.h <= 160 then cy = (m.h - 160) / 2 else cy = math.min(math.max(cy, 0), m.h - 160) end
    self.cam.x, self.cam.y = math.floor(cx + 0.5), math.floor(cy + 0.5)
end

function Play:startFade(to, spawn)
    self.transition = { kind = "fade", t = 0, to = to, spawn = spawn }
end

function Play:startSlide(dir, to)
    local nextMap = Map.load(to)
    local pl = self.player
    local dx = (dir == "east" and 1) or (dir == "west" and -1) or 0
    local dy = (dir == "south" and 1) or (dir == "north" and -1) or 0
    -- player keeps walking in; express its position in the new room's coordinates
    pl.x, pl.y = pl.x - dx * self.map.w, pl.y - dy * self.map.h
    self.transition = { kind = "slide", t = 0, dx = dx, dy = dy, old = self.map, new = nextMap }
end

function Play:checkExits()
    local pl, m = self.player, self.map
    local exits = m.def.exits or {}
    local dir
    if pl.x < 2 then dir = "west" elseif pl.x > m.w - 2 then dir = "east"
    elseif pl.y < 6 then dir = "north" elseif pl.y > m.h + 2 then dir = "south" end
    local e = dir and exits[dir]
    if not e then return end
    if e.slide then self:startSlide(dir, e.to) else self:startFade(e.to, e.spawn) end
end

function Play:interact()
    local probe = self.player:probe()
    for _, n in ipairs(self.map.npcs) do
        if n.talk and Map.overlap(probe, n.box) then
            n:face(self.player.x, self.player.y)
            self:say(n.talk, n.name)
            return true
        end
    end
    for _, o in ipairs(self.map.objects) do
        if o.talk and o.box and Map.overlap(probe, o.box) then
            self:say(o.talk)
            return true
        end
    end
    return false
end

function Play:say(key, nameKey)
    local sy = self.player.y - self.cam.y
    self.dialog = Dialog.new(key, nameKey, sy > 100)
end

function Play:updateTransition()
    local tr = self.transition
    tr.t = tr.t + 1
    if tr.kind == "fadein" then
        screen.fade = 1 - tr.t / FADE
        if tr.t >= FADE then screen.fade, self.transition = 0, nil end
    elseif tr.kind == "fade" then
        if tr.t <= FADE then
            screen.fade = tr.t / FADE
        end
        if tr.t == FADE then
            self:enter(Map.load(tr.to), tr.spawn)
            self.player.anim:play("idle_" .. self.player.dir)
        elseif tr.t > FADE then
            screen.fade = 1 - (tr.t - FADE) / FADE
            if tr.t >= 2 * FADE then screen.fade, self.transition = 0, nil end
        end
    elseif tr.kind == "slide" then
        local pl = self.player
        -- walk a few pixels into the new room while the screen scrolls
        pl.x, pl.y = pl.x + tr.dx * 12 / SLIDE, pl.y + tr.dy * 14 / SLIDE
        pl.anim:play("walk_" .. pl.dir)
        pl.anim:update()
        if tr.t >= SLIDE then
            self:enter(tr.new, nil, true)
            self.transition = nil
        end
    end
end

function Play:update()
    self.frame = self.frame + 1
    self.map:update(self.frame)
    if self.transition then
        self:updateTransition()
        return
    end
    if self.dialog then
        self.dialog:update()
        if self.dialog.done then self.dialog = nil end
        self.player:update(self.map, true)
        return
    end
    if input.pressed.start then
        scenes.push(require("src.scenes.pause").new(self))
        return
    end
    if input.pressed.a and self:interact() then
        self.player:update(self.map, true)
        return
    end
    self.player:update(self.map)
    local box = self.player:box()
    for _, d in ipairs(self.map.doors) do
        if Map.overlap(box, d) then
            if d.armed then self:startFade(d.to, d.spawn) return end
        else
            d.armed = true
        end
    end
    self:checkExits()
    self:updateCamera()
end

local function drawMap(map, pl, frame, ox, oy)
    love.graphics.push()
    love.graphics.translate(-ox, -oy)
    map:drawGround(frame)
    map:drawSorted(pl and { pl } or {}, ox, oy)
    love.graphics.pop()
end

function Play:draw()
    local tr = self.transition
    if tr and tr.kind == "slide" then
        local k = tr.t / SLIDE
        local ox, oy = math.floor(tr.dx * 240 * k), math.floor(tr.dy * 160 * k)
        drawMap(tr.old, nil, self.frame, ox, oy)
        drawMap(tr.new, self.player, self.frame, ox - tr.dx * 240, oy - tr.dy * 160)
    else
        drawMap(self.map, self.player, self.frame, self.cam.x, self.cam.y)
    end
    hud.draw(self.state)
    if self.dialog then self.dialog:draw() end
end

return Play
