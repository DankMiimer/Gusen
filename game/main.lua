-- Gusen: a top-down adventure in the style of a GBA game.
-- Fixed 60 Hz simulation, 240x160 canvas, integer scaling only.
love.graphics.setDefaultFilter("nearest", "nearest")
love.graphics.setLineStyle("rough")

local screen = require("src.core.screen")
local input = require("src.core.input")
local settings = require("src.core.settings")
local i18n = require("src.core.i18n")
local scenes = require("src.core.scenes")
local autotest = require("src.core.autotest")

local STEP = 1 / 60
local accumulator = 0

function love.load()
    love.mouse.setVisible(false)
    settings.load()
    i18n.set(settings.data.lang or "no")
    screen.init()
    input.init()
    autotest.init(os.getenv("GUSEN_AUTOTEST"))
    scenes.push(require("src.scenes.boot").new())
end

local function tick()
    autotest.step()
    input.update()
    scenes.update()
end

function love.update(dt)
    if autotest.active then
        tick() -- tests run one fixed step per frame so they are deterministic
        return
    end
    accumulator = accumulator + math.min(dt, 0.25)
    local steps = 0
    while accumulator >= STEP and steps < 4 do
        tick()
        accumulator = accumulator - STEP
        steps = steps + 1
    end
    if steps == 4 then accumulator = 0 end -- a long hitch: don't try to catch up
end

function love.draw()
    screen.begin()
    scenes.draw()
    screen.finish()
    autotest.afterDraw()
end

function love.resize(w, h) screen.resize(w, h) end
function love.keypressed(key) input.keypressed(key) end
function love.gamepadpressed(joystick, button) input.gamepadpressed(joystick, button) end
function love.joystickpressed(joystick, button)
    if not joystick:isGamepad() then input.lastRaw = "joy:" .. tostring(button) end
end
function love.joystickadded(joystick) input.joystickadded(joystick) end
function love.joystickremoved(joystick) input.joystickremoved(joystick) end
