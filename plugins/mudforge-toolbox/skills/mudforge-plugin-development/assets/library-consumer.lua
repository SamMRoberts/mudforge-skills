plugin = {
  id = "mudforge-toolbox-library", name = "Toolbox Library Consumer",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "Install injected-counter as a shared library first."
}

local initialized = false
function init()
  if initialized then return end
  local counter = require("injected-counter")
  counter.init({ echo = echo })
  registerCommand("toolbox-library-count", function() counter.tick() end,
    "Increment this plugin's independent library counter")
  initialized = true
end

function cleanup() end
