-- Player settings (language, button layout), stored as a Lua table in the save dir.
local settings = { file = "settings.lua" }

local DEFAULTS = { lang = nil, pad = { a = "a", b = "b" }, calibrated = false }

local function copy(t)
    local o = {}
    for k, v in pairs(t) do o[k] = type(v) == "table" and copy(v) or v end
    return o
end

local function serialize(v)
    if type(v) == "table" then
        local parts = {}
        for k, x in pairs(v) do
            parts[#parts + 1] = string.format("[%q]=%s", tostring(k), serialize(x))
        end
        return "{" .. table.concat(parts, ",") .. "}"
    elseif type(v) == "string" then
        return string.format("%q", v)
    end
    return tostring(v)
end

function settings.load()
    settings.data = copy(DEFAULTS)
    if os.getenv("GUSEN_AUTOTEST") then
        -- tests always start from a fresh first boot and never touch the player's settings
        settings.file = "autotest_settings.lua"
        love.filesystem.remove(settings.file)
    end
    if love.filesystem.getInfo(settings.file) then
        local ok, chunk = pcall(love.filesystem.load, settings.file)
        if ok and chunk then
            local ok2, t = pcall(chunk)
            if ok2 and type(t) == "table" then
                for k, v in pairs(t) do settings.data[k] = v end
            end
        end
    end
end

function settings.save()
    love.filesystem.write(settings.file, "return " .. serialize(settings.data) .. "\n")
end

return settings
