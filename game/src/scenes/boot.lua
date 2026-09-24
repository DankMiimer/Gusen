-- Title screen. First run: press A once (this also learns which pad button is
-- A on this device), then pick Norsk / English. After that: press A to start.
local assets = require("src.core.assets")
local font = require("src.core.font")
local i18n = require("src.core.i18n")
local input = require("src.core.input")
local settings = require("src.core.settings")
local scenes = require("src.core.scenes")

local Boot = {}
Boot.__index = Boot

local VERSION = "v0.1 (M0)"
local FACE = { a = true, b = true, x = true, y = true }

function Boot.new(opts)
    local b = setmetatable({ t = 0, choice = 1, opts = opts or {} }, Boot)
    b.step = not settings.data.calibrated and "press" or (settings.data.lang and "start" or "lang")
    if b.opts.recalibrate then b.step = "press" end
    input.takeRaw()
    return b
end

function Boot:update()
    self.t = self.t + 1
    if self.step == "press" then
        local raw = input.takeRaw()
        if raw and FACE[raw] then
            input.calibrate(raw)
            self:next()
        elseif raw then
            -- any other key/button still gets you in; the layout just isn't learned
            self:next()
        end
    elseif self.step == "lang" then
        if input.pressed.up or input.pressed.down then self.choice = 3 - self.choice end
        if input.pressed.a then
            settings.data.lang = self.choice == 1 and "no" or "en"
            settings.save()
            i18n.set(settings.data.lang)
            self.step = "start"
            self.t = 0
        end
    elseif self.step == "start" then
        if (input.pressed.a or input.pressed.start) and self.t > 10 then
            if self.opts.recalibrate then
                scenes.pop()
            else
                scenes.replace(require("src.scenes.play").new("gusenby", "start"))
            end
        end
    end
end

function Boot:next()
    input.update() -- swallow this press
    self.t = 0
    if self.opts.recalibrate then
        scenes.pop()
        return
    end
    self.step = settings.data.lang and "start" or "lang"
end

local SKY = { { 0, "060608" }, { 40, "141013" }, { 70, "242234" }, { 96, "403353" } }
local STARS = { { 12, 8 }, { 40, 22 }, { 77, 6 }, { 130, 14 }, { 170, 30 }, { 205, 9 }, { 228, 24 },
                { 98, 34 }, { 60, 50 }, { 190, 58 }, { 20, 62 }, { 150, 52 } }

local function rgb(h) return tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255,
    tonumber(h:sub(5, 6), 16) / 255 end

local function centered(text, y, color, shadow)
    font.print(text, math.floor((240 - font.width(text)) / 2), y, color, shadow)
end

function Boot:draw()
    for _, band in ipairs(SKY) do
        love.graphics.setColor(rgb(band[2]))
        love.graphics.rectangle("fill", 0, band[1], 240, 160 - band[1])
    end
    for i, s in ipairs(STARS) do
        local twinkle = math.floor((self.t + i * 13) / 40) % 5 ~= 0
        love.graphics.setColor(rgb(twinkle and "dae0ea" or "8b93af"))
        love.graphics.points(s[1] + 0.5, s[2] + 0.5)
    end
    -- hills and ground
    for x = 0, 239 do
        local h = 112 + math.floor(6 * math.sin(x / 23)) + math.floor(3 * math.sin(x / 7))
        love.graphics.setColor(rgb("122020"))
        love.graphics.rectangle("fill", x, h, 1, 2)
        love.graphics.setColor(rgb("24523b"))
        love.graphics.rectangle("fill", x, h + 2, 1, 160 - h)
    end
    love.graphics.setColor(1, 1, 1, 1)
    local ow = assets.sheet("overworld")
    for x = 0, 224, 16 do
        assets.drawFrame(ow, ow.tiles[({ "grass_a", "grass_b", "grass_c" })[x / 16 % 3 + 1]], x + 8, 136 + 15)
        assets.drawFrame(ow, ow.tiles.grass_c, x + 8, 152 + 15)
    end
    local logo = assets.image("ui/logo.png")
    love.graphics.draw(logo, math.floor((240 - logo:getWidth() * 2) / 2), 26, 0, 2, 2)
    -- the cast
    local npcs = assets.sheet("gusen_npcs")
    local shadow = assets.image("fx/shadow.png")
    for i, x in ipairs({ 28, 52, 76, 100, 140, 164, 188, 212 }) do
        love.graphics.draw(shadow, x - 5, 148)
        assets.drawFrame(npcs, (i - 1) * 4, x, 150)
    end
    love.graphics.draw(shadow, 115, 148)
    assets.drawFrame(assets.sheet("gusen_player"), 0, 120, 150)
    assets.drawFrame(assets.sheet("candle"), 0, 120, 134)

    local blink = math.floor(self.t / 30) % 2 == 0
    if self.step == "press" then
        if blink then centered("Trykk A  /  Press A", 88, "ffffff", "c50000") end
    elseif self.step == "lang" then
        centered("Velg språk  /  Choose language", 80, "ffd541", "000000")
        local opts = { "Norsk", "English" }
        for i, o in ipairs(opts) do
            local y = 92 + (i - 1) * 11
            local x = 104
            font.print(o, x, y, "ffffff", "000000")
            if self.choice == i then love.graphics.draw(assets.image("ui/cursor.png"), x - 10, y + 1) end
        end
    else
        if blink then centered(i18n.t("title_start"), 88, "ffffff", "c50000") end
    end
    font.print(VERSION, 240 - font.width(VERSION) - 2, 2, "4a5462")
    if not input.usingPad and not input.joystick and self.step ~= "lang" then
        centered(i18n.t("keys_hint"), 104, "b3b9d1", "000000")
    end
end

return Boot
