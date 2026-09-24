-- A small scene stack. Every scene has update() and draw(); the top one updates,
-- all of them draw (so the pause menu sits on top of the world).
local scenes = { stack = {} }

function scenes.push(s) scenes.stack[#scenes.stack + 1] = s end
function scenes.pop() scenes.stack[#scenes.stack] = nil end
function scenes.top() return scenes.stack[#scenes.stack] end
function scenes.replace(s)
    scenes.stack[#scenes.stack] = s
end

function scenes.update()
    local top = scenes.top()
    if top then top:update() end
end

function scenes.draw()
    for i = 1, #scenes.stack do scenes.stack[i]:draw() end
end

return scenes
