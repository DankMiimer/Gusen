-- Plays a manifest animation: {frames = {...}, ms = number | {per frame}, loop = bool}.
local Anim = {}
Anim.__index = Anim

function Anim.new(sheet, name)
    local a = setmetatable({ sheet = sheet, t = 0, i = 1, done = false }, Anim)
    if name then a:play(name) end
    return a
end

function Anim:play(name, restart)
    if self.name == name and not restart then return end
    local def = self.sheet.anims[name]
    assert(def, "unknown animation " .. tostring(name))
    self.name, self.def, self.t, self.i, self.done = name, def, 0, 1, false
end

local function duration(def, i)
    if type(def.ms) == "table" then return def.ms[i] or 100 end
    return def.ms or 100
end

-- advance by one fixed step (1/60 s)
function Anim:update()
    local def = self.def
    if not def or #def.frames < 2 or self.done then return end
    local ms = duration(def, self.i)
    if ms <= 0 then return end
    self.t = self.t + 1000 / 60
    while self.t >= ms do
        self.t = self.t - ms
        if self.i < #def.frames then
            self.i = self.i + 1
        elseif def.loop == false then
            self.done = true
            return
        else
            self.i = 1
        end
        ms = duration(def, self.i)
    end
end

function Anim:frame() return self.def.frames[self.i] end

function Anim:draw(x, y, flip)
    require("src.core.assets").drawFrame(self.sheet, self:frame(), x, y, flip)
end

return Anim
