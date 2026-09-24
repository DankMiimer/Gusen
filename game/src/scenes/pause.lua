-- Start menu: resume, language, set up A/B, quit.
local assets = require("src.core.assets")
local font = require("src.core.font")
local i18n = require("src.core.i18n")
local input = require("src.core.input")
local settings = require("src.core.settings")
local scenes = require("src.core.scenes")
local Dialog = require("src.ui.dialog")

local Pause = {}
Pause.__index = Pause

function Pause.new(play)
    return setmetatable({ play = play, sel = 1, t = 0 }, Pause)
end

local ITEMS = { "menu_resume", "menu_language", "menu_buttons", "menu_quit" }

function Pause:update()
    self.t = self.t + 1
    if input.pressed.up then self.sel = (self.sel - 2) % #ITEMS + 1 end
    if input.pressed.down then self.sel = self.sel % #ITEMS + 1 end
    if input.pressed.start or input.pressed.b then
        scenes.pop()
        return
    end
    if input.pressed.a then
        local item = ITEMS[self.sel]
        if item == "menu_resume" then
            scenes.pop()
        elseif item == "menu_language" then
            settings.data.lang = settings.data.lang == "no" and "en" or "no"
            settings.save()
            i18n.set(settings.data.lang)
        elseif item == "menu_buttons" then
            scenes.push(require("src.scenes.boot").new({ recalibrate = true }))
        elseif item == "menu_quit" then
            love.event.quit()
        end
    end
end

function Pause:draw()
    local w, h = 132, 72
    local x, y = math.floor((240 - w) / 2), 40
    Dialog.nine(assets.image("ui/dialog_box.png"), x, y, w, h)
    font.print(i18n.t("menu_title"), x + 10, y + 6, "ffd541")
    for i, key in ipairs(ITEMS) do
        local ty = y + 20 + (i - 1) * 12
        font.print(i18n.t(key), x + 20, ty, i == self.sel and "ffffff" or "b3b9d1")
        if i == self.sel then love.graphics.draw(assets.image("ui/cursor.png"), x + 9, ty + 1) end
    end
end

return Pause
