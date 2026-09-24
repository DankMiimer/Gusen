-- Virtual GBA buttons from keyboard and gamepad.
--
-- PortMaster devices differ in whether SDL's "a" is the button labelled A or the
-- button in the Xbox A position. Instead of guessing, the title screen asks the
-- player to press A once and remembers which button that was (settings.pad).
local settings = require("src.core.settings")

local input = { down = {}, pressed = {}, released = {}, forced = {}, joystick = nil, lastRaw = nil,
                usingPad = false }

local BUTTONS = { "up", "down", "left", "right", "a", "b", "l", "r", "start", "select" }
local KEYS = {
    up = { "up", "w" }, down = { "down", "s" }, left = { "left", "a" }, right = { "right", "d" },
    a = { "z", "j", "space" }, b = { "x", "k" }, l = { "q" }, r = { "e", "lshift" },
    start = { "return", "escape" }, select = { "tab", "backspace" },
}
local PARTNER = { a = "b", b = "a", x = "y", y = "x" }
local DEADZONE = 0.5

function input.init()
    for _, j in ipairs(love.joystick.getJoysticks()) do input.joystickadded(j) end
end

function input.joystickadded(j)
    if not input.joystick and j:isGamepad() then input.joystick = j end
end

function input.joystickremoved(j)
    if input.joystick == j then
        input.joystick = nil
        input.init()
    end
end

-- raw face button -> which virtual button it is, using the calibrated layout
local function padButton(raw)
    local pad = settings.data.pad
    if raw == pad.a then return "a" end
    if raw == pad.b then return "b" end
    return nil
end

function input.gamepadpressed(joystick, raw)
    input.usingPad = true
    input.lastRaw = raw
end

function input.keypressed(key)
    input.usingPad = false
    input.lastRaw = "key:" .. key
    if key == "f11" then love.window.setFullscreen(not love.window.getFullscreen(), "desktop") end
end

-- Remember `raw` as A; its neighbour (a<->b, x<->y) becomes B.
function input.calibrate(raw)
    if raw and not raw:find("^key:") then
        settings.data.pad = { a = raw, b = PARTNER[raw] or "b" }
        settings.data.calibrated = true
        settings.save()
    end
end

local function rawDown(name)
    for _, k in ipairs(KEYS[name]) do
        if love.keyboard.isDown(k) then return true end
    end
    local j = input.joystick
    if not j then return false end
    if name == "up" then
        return j:isGamepadDown("dpup") or j:getGamepadAxis("lefty") < -DEADZONE
    elseif name == "down" then
        return j:isGamepadDown("dpdown") or j:getGamepadAxis("lefty") > DEADZONE
    elseif name == "left" then
        return j:isGamepadDown("dpleft") or j:getGamepadAxis("leftx") < -DEADZONE
    elseif name == "right" then
        return j:isGamepadDown("dpright") or j:getGamepadAxis("leftx") > DEADZONE
    elseif name == "a" or name == "b" then
        return j:isGamepadDown(settings.data.pad[name])
    elseif name == "l" then
        return j:isGamepadDown("leftshoulder")
    elseif name == "r" then
        return j:isGamepadDown("rightshoulder")
    elseif name == "start" then
        return j:isGamepadDown("start")
    elseif name == "select" then
        return j:isGamepadDown("back")
    end
    return false
end

function input.update()
    for _, b in ipairs(BUTTONS) do
        local now
        if input.forced[b] ~= nil then now = input.forced[b] else now = rawDown(b) end
        local was = input.down[b] or false
        input.down[b] = now
        input.pressed[b] = now and not was
        input.released[b] = was and not now
    end
end

-- Direction as a unit-ish vector from the d-pad / stick.
function input.axis()
    local x, y = 0, 0
    if input.down.left then x = x - 1 end
    if input.down.right then x = x + 1 end
    if input.down.up then y = y - 1 end
    if input.down.down then y = y + 1 end
    return x, y
end

-- Used by the title screen: which raw button was just pressed (and clear it).
function input.takeRaw()
    local r = input.lastRaw
    input.lastRaw = nil
    return r
end

input.padButton = padButton
return input
