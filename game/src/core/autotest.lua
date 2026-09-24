-- Scripted play-testing: GUSEN_AUTOTEST=<name> runs tests/<name>.lua, a list of
-- steps that press buttons, move the player, take screenshots and check state.
-- Used to test every build on a PC before it goes to the handheld.
local input = require("src.core.input")

local autotest = { active = false, frame = 0 }
local steps, idx, wait, holding, pendingShot
local REPORT = "autotest_report.txt"
local MAX_FRAMES = 60 * 60 * 5 -- a test that runs longer than 5 minutes has hung

-- print and also append to autotest_report.txt in the save folder (love.exe on
-- Windows has no console, so tools/run_tests.py reads the file instead)
local function say(line)
    print(line)
    love.filesystem.append(REPORT, line .. "\n")
end
autotest.say = say

function autotest.init(name)
    if not name or name == "" then return end
    autotest.active = true
    io.stdout:setvbuf("line") -- so logs show up live even when piped (e.g. through tee)
    love.filesystem.write(REPORT, "")
    -- a Lua error must end the run (with the message in the report), not sit on the error screen
    love.errorhandler = function(msg)
        say("[autotest] ERROR " .. tostring(msg))
        say(debug.traceback("", 2))
        say("[autotest] done WITH FAILURES")
        return function() return 2 end
    end
    steps = require("tests." .. name)
    idx, wait, holding = 1, 0, {}
    say("[autotest] running " .. name .. " (" .. #steps .. " steps)")
end

local function scene() return require("src.core.scenes").top() end

function autotest.step()
    if not autotest.active then return end
    autotest.frame = autotest.frame + 1
    if autotest.frame > MAX_FRAMES then
        say("[autotest] FAIL timed out after " .. MAX_FRAMES .. " frames")
        say("[autotest] done WITH FAILURES")
        love.event.quit(1)
        return
    end
    for b, n in pairs(holding) do
        if n <= 0 then
            input.forced[b] = false
            holding[b] = nil
        else
            holding[b] = n - 1
        end
    end
    if wait > 0 then
        wait = wait - 1
        return
    end
    while idx <= #steps do
        local s = steps[idx]
        idx = idx + 1
        if s.wait then
            wait = s.wait
            return
        elseif s.press then
            input.forced[s.press] = true
            holding[s.press] = 1
            wait = 2
            return
        elseif s.hold then
            input.forced[s.hold] = true
            holding[s.hold] = s.frames or 30
            wait = s.frames or 30
            return
        elseif s.raw then
            input.lastRaw = s.raw           -- pretend a gamepad button was pressed
        elseif s.shot then
            pendingShot = s.shot
            return
        elseif s.call then
            s.call(scene())
        elseif s.log then
            say("[autotest] " .. (type(s.log) == "function" and s.log(scene()) or s.log))
        elseif s.expect then
            local ok, msg = s.expect(scene())
            say(string.format("[autotest] %s %s", ok and "PASS" or "FAIL", msg or ""))
            if not ok then autotest.failed = true end
        elseif s.quit then
            say("[autotest] done" .. (autotest.failed and " WITH FAILURES" or ""))
            love.event.quit(autotest.failed and 1 or 0)
            return
        end
    end
end

function autotest.afterDraw()
    if pendingShot then
        love.graphics.captureScreenshot("autotest_" .. pendingShot .. ".png")
        say("[autotest] screenshot " .. pendingShot)
        pendingShot = nil
    end
end

return autotest
