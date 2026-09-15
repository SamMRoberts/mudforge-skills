plugin = {
  id = "mudforge-toolbox-protocols", name = "Toolbox Protocols",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "Session-local partial vitals, with synthetic demo input.",
  settings = { saveState = false }
}

local initialized = false
local hp = nil
local maximum = nil

local function numeric(value)
  local n = tonumber(value)
  if not n or n ~= n or n == math.huge or n == -math.huge or n < 0 then return nil end
  return n
end

local function update(data)
  if type(data) ~= "table" then return end
  if data.hp ~= nil then hp = numeric(data.hp) end
  if data.maxhp ~= nil then
    maximum = numeric(data.maxhp)
    if maximum and maximum <= 0 then maximum = nil end
  end
  emit("mudforge-toolbox.vitals", { sessionId = getSessionId(), hp = hp, maxhp = maximum })
end

function init()
  if initialized then return end
  initialized = true
  onGMCPUpdate("Char.Vitals", update)
  onMSDPChange("HEALTH", function(value) update({ hp = value }) end)
  onMSDPChange("HEALTH_MAX", function(value) update({ maxhp = value }) end)
  registerCommand("toolbox-protocol-demo", function()
    update({ hp = "25", maxhp = "100" })
  end, "Emit synthetic session-local vitals")
end

function onDisconnect(sessionId)
  if sessionId ~= getSessionId() then return end
  hp = nil
  maximum = nil
  emit("mudforge-toolbox.vitals", { sessionId = sessionId })
end

function cleanup() end
