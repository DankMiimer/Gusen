-- Friendly Gusens. Standard-body Gusens have 4 directions (sprites/gusen_npcs.png);
-- the others use their original left/right sprite from legacy/.
local assets = require("src.core.assets")

local NPC = {}
NPC.__index = NPC

local FOUR_DIR = { npc1 = 0, npc2 = 1, dinggusen = 2, gressgusen = 3, lanternegusen = 4, lunagusen = 5,
                   wirelessgusen = 6, sprite = 7 }
local DIRS = { down = 0, up = 1, left = 2, right = 3 }

function NPC.new(o)
    local n = setmetatable({ who = o.who, x = o.x, y = o.y, dir = o.dir or "down", home = o.dir or "down",
                             talk = o.talk, name = o.name, bob = 0, t = 0 }, NPC)
    if FOUR_DIR[o.who] then
        n.sheet, n.row = assets.sheet("gusen_npcs"), FOUR_DIR[o.who]
    else
        n.sheet = assets.sheet(o.who)   -- legacy/<who>.png, frames: 0 = left, 1 = right
        if n.dir ~= "left" and n.dir ~= "right" then n.dir = "right" end
    end
    n.box = { x = n.x - 5, y = n.y - 4, w = 10, h = 5 }
    return n
end

function NPC:face(px, py)
    local dx, dy = px - self.x, py - self.y
    local d
    if math.abs(dx) > math.abs(dy) then d = dx < 0 and "left" or "right" else d = dy < 0 and "up" or "down" end
    if not self.row and (d == "up" or d == "down") then d = dx < 0 and "left" or "right" end
    self.dir = d
    self.t = 180 -- look back home after 3 s
end

function NPC:update()
    if self.t > 0 then
        self.t = self.t - 1
        if self.t == 0 then self.dir = self.row and self.home or self.dir end
    end
end

function NPC:draw()
    local frame
    if self.row then frame = self.row * 4 + DIRS[self.dir] else frame = self.dir == "left" and 0 or 1 end
    love.graphics.draw(assets.image("fx/shadow.png"), math.floor(self.x) - 5, math.floor(self.y) - 2)
    assets.drawFrame(self.sheet, frame, self.x, self.y)
end

function NPC:bounds() return self.x - 6, self.y - 14, 12, 15 end

return NPC
