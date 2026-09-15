plugin = {
  id = "mudforge-toolbox-automation", name = "Toolbox Automation",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "Local capture and replaceable timer demonstration.",
  settings = { saveState = false }
}

local initialized = false
local triggerId = nil
local aliasId = nil
local timerId = nil

local function cancel()
  if timerId and timerId ~= "" then removeTimer(timerId) end
  timerId = nil
end

function init()
  if initialized then return end
  initialized = true
  triggerId = addTrigger("^Toolbox score: ([0-9]+)$", function(c)
    local score = tonumber(c[1])
    if score then setVariable("score", score) end
  end, { type = "regex" })
  aliasId = addAlias("^toolbox-score ([0-9]+)$", "", function(m)
    local score = tonumber(m[2])
    if score then
      setVariable("score", score)
      echo("Toolbox score stored: " .. tostring(score))
    end
  end, { name = "toolbox-score" })
  registerCommand("toolbox-delay", function()
    cancel()
    timerId = addTimer(1000, function()
      timerId = nil
      echo("Toolbox delayed callback")
    end, false)
    if not timerId or timerId == "" then
      timerId = nil
      echo("Timer unavailable; a connected test session is required.")
    end
  end, "Replace the pending local one-second callback")
  registerCommand("toolbox-cancel", cancel, "Cancel the pending callback")
end

function onDisconnect(sessionId)
  if sessionId == getSessionId() then cancel() end
end

function cleanup()
  cancel()
  if triggerId then removeTrigger(triggerId) end
  if aliasId then removeAlias(aliasId) end
  triggerId = nil
  aliasId = nil
  -- A fresh runtime handles re-enable; init's guard lasts for this runtime.
end
