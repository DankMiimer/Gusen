-- The player Gusen: 8-way movement, collision with a small box at the feet,
-- corner sliding so doorways and gaps feel forgiving.
local assets = require("src.core.assets")
local Anim = require("src.core.anim")
local input = require("src.core.input")

local Player = {}
Player.__index = Player

local SPEED = 1.25          -- px per 1/60 s step (75 px/s), GBA-Zelda-ish
local DIAG = SPEED * 0.7071
local NUDGE = 5             -- how far round a corner we slide the player

function Player.new(x, y, dir)
    local p = setmetatable({ x = x, y = y, dir = dir or "down", moving = false }, Player)
    p.sheet = assets.sheet("gusen_player")
    p.anim = Anim.new(p.sheet, "idle_" .. p.dir)
    p.dust = 0
    return p
end

function Player:box(x, y)
    return { x = (x or self.x) - 4, y = (y or self.y) - 4, w = 8, h = 5 }
end

-- move along one axis in small steps; returns true if the whole move happened
function Player:slide(map, dx, dy)
    local n = math.max(1, math.ceil(math.max(math.abs(dx), math.abs(dy)) * 4))
    for _ = 1, n do
        local nx, ny = self.x + dx / n, self.y + dy / n
        if map:blocked(self:box(nx, ny)) then return false end
        self.x, self.y = nx, ny
    end
    return true
end

-- blocked going straight? try shifting sideways a little to round the corner
function Player:nudge(map, dx, dy)
    for off = 1, NUDGE do
        for _, s in ipairs({ -1, 1 }) do
            local ox, oy = (dx == 0) and s * off or 0, (dy == 0) and s * off or 0
            if not map:blocked(self:box(self.x + ox, self.y + oy))
                and not map:blocked(self:box(self.x + ox + dx, self.y + oy + dy)) then
                self:slide(map, (dx == 0) and s * 0.5 or 0, (dy == 0) and s * 0.5 or 0)
                return
            end
        end
    end
end

function Player:update(map, frozen)
    local ax, ay = 0, 0
    if not frozen then ax, ay = input.axis() end
    self.moving = ax ~= 0 or ay ~= 0
    if self.moving then
        -- facing: keep the current facing if it's one of the pressed directions
        local keep = (self.dir == "left" and ax < 0) or (self.dir == "right" and ax > 0)
            or (self.dir == "up" and ay < 0) or (self.dir == "down" and ay > 0)
        if not keep then
            if ax ~= 0 then self.dir = ax < 0 and "left" or "right" else self.dir = ay < 0 and "up" or "down" end
        end
        local sp = (ax ~= 0 and ay ~= 0) and DIAG or SPEED
        local okx = ax == 0 or self:slide(map, ax * sp, 0)
        local oky = ay == 0 or self:slide(map, 0, ay * sp)
        if not okx and ay == 0 then self:nudge(map, ax * sp, 0) end
        if not oky and ax == 0 then self:nudge(map, 0, ay * sp) end
        self.anim:play("walk_" .. self.dir)
        self.dust = self.dust + 1
    else
        self.anim:play("idle_" .. self.dir)
        self.dust = 0
    end
    self.anim:update()
end

-- the point just in front of the player (for talking / reading)
function Player:probe()
    local dx = (self.dir == "left" and -1) or (self.dir == "right" and 1) or 0
    local dy = (self.dir == "up" and -1) or (self.dir == "down" and 1) or 0
    return { x = self.x + dx * 9 - 4, y = self.y - 2 + dy * 9 - 4, w = 8, h = 8 }
end

function Player:draw()
    love.graphics.draw(assets.image("fx/shadow.png"), math.floor(self.x) - 5, math.floor(self.y) - 2)
    self.anim:draw(self.x, self.y)
end

function Player:bounds() return self.x - 6, self.y - 14, 12, 15 end

return Player
