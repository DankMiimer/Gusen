-- Dialog box: speaker name in gold, typewriter text, 3 lines per page,
-- A finishes the page / goes on, blinking arrow when there's more.
local assets = require("src.core.assets")
local font = require("src.core.font")
local i18n = require("src.core.i18n")
local input = require("src.core.input")

local Dialog = {}
Dialog.__index = Dialog

local BOX_W, BOX_H, PAD = 232, 50, 9
local LINES = 3

local quadCache = {}

-- 9-slice with 8 px borders; quads are built once per image
local function nine(img, x, y, w, h)
    local s = 8
    local iw, ih = img:getDimensions()
    local q = quadCache[img]
    if not q then
        local function mk(sx, sy, sw, sh) return love.graphics.newQuad(sx, sy, sw, sh, iw, ih) end
        q = { mk(0, 0, s, s), mk(s, 0, iw - 2 * s, s), mk(iw - s, 0, s, s),
              mk(0, s, s, ih - 2 * s), mk(s, s, iw - 2 * s, ih - 2 * s), mk(iw - s, s, s, ih - 2 * s),
              mk(0, ih - s, s, s), mk(s, ih - s, iw - 2 * s, s), mk(iw - s, ih - s, s, s) }
        quadCache[img] = q
    end
    local mw, mh = (w - 2 * s) / (iw - 2 * s), (h - 2 * s) / (ih - 2 * s)
    love.graphics.draw(img, q[1], x, y)
    love.graphics.draw(img, q[2], x + s, y, 0, mw, 1)
    love.graphics.draw(img, q[3], x + w - s, y)
    love.graphics.draw(img, q[4], x, y + s, 0, 1, mh)
    love.graphics.draw(img, q[5], x + s, y + s, 0, mw, mh)
    love.graphics.draw(img, q[6], x + w - s, y + s, 0, 1, mh)
    love.graphics.draw(img, q[7], x, y + h - s)
    love.graphics.draw(img, q[8], x + s, y + h - s, 0, mw, 1)
    love.graphics.draw(img, q[9], x + w - s, y + h - s)
end
Dialog.nine = nine

-- key: text key in lang/*.lua (string or list of pages); name: optional speaker key
function Dialog.new(key, nameKey, atTop)
    local d = setmetatable({ pages = {}, page = 1, shown = 0, t = 0, done = false, atTop = atTop }, Dialog)
    d.name = nameKey and i18n.t(nameKey) or nil
    local text = i18n.t(key)
    if type(text) == "string" then text = { text } end
    local lines = d.name and LINES - 1 or LINES
    for _, t in ipairs(text) do
        local wrapped = font.wrap(t, BOX_W - 2 * PAD)
        for i = 1, #wrapped, lines do
            local page = {}
            for j = i, math.min(i + lines - 1, #wrapped) do page[#page + 1] = wrapped[j] end
            d.pages[#d.pages + 1] = page
        end
    end
    d.total = d:pageLength()
    return d
end

function Dialog:pageLength()
    local n = 0
    for _, l in ipairs(self.pages[self.page]) do n = n + #font.chars(l) end
    return n
end

function Dialog:update()
    self.t = self.t + 1
    if self.shown < self.total then
        self.shown = self.shown + 1           -- one character per frame
        if input.pressed.a or input.pressed.b then self.shown = self.total end
    elseif input.pressed.a or input.pressed.b then
        if self.page < #self.pages then
            self.page = self.page + 1
            self.shown, self.total = 0, self:pageLength()
        else
            self.done = true
        end
    end
end

function Dialog:draw()
    local x, y = 4, self.atTop and 4 or 106
    nine(assets.image("ui/dialog_box.png"), x, y, BOX_W, BOX_H)
    local ty = y + 5
    if self.name then
        font.print(self.name, x + PAD, ty, "ffd541")
        ty = ty + 12
    end
    local left = self.shown
    for _, line in ipairs(self.pages[self.page]) do
        local n = #font.chars(line)
        font.print(line, x + PAD, ty, "ffffff", nil, math.max(0, left))
        left = left - n
        ty = ty + 12
    end
    if self.shown >= self.total and math.floor(self.t / 20) % 2 == 0 then
        assets.drawFrame(assets.sheet("more_arrow"), 0, x + BOX_W - 14 + 3, y + BOX_H - 9 + 5)
    end
end

return Dialog
