plugin = {
  id = "mudforge-toolbox-lifecycle", name = "Toolbox Lifecycle",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "An explicitly invoked, persistent local counter.",
  settings = { saveState = true }
}

local initialized = false
local count = 0

function init()
  if initialized then return end
  initialized = true
  count = tonumber(getVariable("count")) or 0
  registerCommand("toolbox-count", function()
    count = count + 1
    setVariable("count", count)
    echo("Toolbox count: " .. tostring(count))
  end, "Increment the counter in this plugin and world")
  registerCommand("toolbox-count-show", function()
    echo("Toolbox count: " .. tostring(count))
  end, "Read the current counter")
end

function onSaveState(sessionId)
  if sessionId == getSessionId() then setVariable("count", count) end
end

function cleanup()
  -- No external resources; the host owns command registration and variables.
end
