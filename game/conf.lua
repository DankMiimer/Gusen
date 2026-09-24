-- Gusen runs on a 240x160 canvas (GBA resolution). The RG34XXSP screen is
-- 720x480, exactly 3x, so the game fills it with no scaling artefacts.
function love.conf(t)
    t.identity = "gusen"
    t.version = "11.5"
    t.console = false
    t.accelerometerjoystick = false
    t.gammacorrect = false

    t.window.title = "Gusen"
    t.window.width = 720
    t.window.height = 480
    t.window.minwidth = 240
    t.window.minheight = 160
    t.window.resizable = true
    t.window.vsync = 1
    t.window.msaa = 0

    -- Set by the PortMaster launcher: take over the whole screen.
    if os.getenv("GUSEN_DEVICE") then
        t.window.fullscreen = true
        t.window.fullscreentype = "desktop"
        t.window.resizable = false
    end

    t.modules.physics = false
    t.modules.video = false
    t.modules.touch = false
end
