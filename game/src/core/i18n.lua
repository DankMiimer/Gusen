-- Norwegian (no) and English (en). Strings live in lang/*.lua. A value can be
-- a string or a list of pages (for dialog).
local i18n = { lang = "no", strings = {} }

function i18n.set(lang)
    i18n.lang = lang
    i18n.strings = require("lang." .. lang)
end

function i18n.t(key)
    local s = i18n.strings[key]
    if s == nil then return key end
    return s
end

return i18n
