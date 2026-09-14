plugin = {
  id = "mudforge-toolbox-vitals", name = "Toolbox Vitals",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "A partial-update HUD with explicit synthetic input.",
  settings = { saveState = false }
}

local initialized = false
local widget = nil
local hp = nil
local maximum = nil
local label = "Vitals"

local function number(value)
  local n = tonumber(value)
  if not n or n ~= n or n == math.huge or n == -math.huge or n < 0 then return nil end
  return n
end

local function render()
  if not widget then return end
  local pct = 0
  if hp and maximum and maximum > 0 then
    pct = math.floor(math.max(0, math.min(100, hp / maximum * 100)))
  end
  setBoundValues(widget, {
    hp = hp and tostring(hp) or "?",
    maximum = maximum and tostring(maximum) or "?",
    label = label, percent = tostring(pct) .. "%",
    status = hp and maximum and "Ready" or "Waiting for valid vitals"
  })
end

local function update(data)
  if type(data) ~= "table" then return end
  if data.hp ~= nil then hp = number(data.hp) end
  if data.maxhp ~= nil then
    maximum = number(data.maxhp)
    if maximum and maximum <= 0 then maximum = nil end
  end
  if data.label ~= nil then label = tostring(data.label) end
  render()
end

local function reset()
  hp = nil
  maximum = nil
  label = "Vitals"
  render()
end

function init()
  if initialized then return end
  initialized = true
  widget = createWidget({ type = "html", name = "toolbox-vitals", title = "Toolbox Vitals",
    position = { x = 80, y = 90 }, size = { width = 280, height = 180 } })
  setWidgetProperty(widget, "content", [[
    <style>
      body{font:16px system-ui;background:#17212b;color:#f4f7fa;padding:10px}
      .bar{height:14px;background:#394553;margin:8px 0}
      .fill{height:100%;background:#75d6a5;width:0}
      button{font:inherit;padding:4px 10px}button:focus-visible{outline:3px solid #f8d66d}
    </style>
    <div data-mud-bind="label">Vitals</div>
    <div data-mud-bind="status" role="status">Waiting for valid vitals</div>
    <div aria-live="polite">HP <span data-mud-bind="hp">?</span> /
      <span data-mud-bind="maximum">?</span></div>
    <div class="bar" aria-hidden="true"><div class="fill" data-mud-bind-style="width:percent"></div></div>
    <button type="button" data-mud-action="reset">Reset display</button>
  ]])
  -- This fixture has exactly one action, so no undocumented payload field is needed.
  registerWidgetEvent(widget, "action", reset)
  onGMCPUpdate("Char.Vitals", update)
  registerCommand("toolbox-vitals-demo", function()
    update({ hp = "25", maxhp = "100", label = "Synthetic <vitals> & data" })
  end, "Show synthetic values without a server connection")
  render()
end

function onDisconnect(sessionId)
  if sessionId == getSessionId() then reset() end
end

function cleanup()
  if widget then destroyWidget(widget) end
  widget = nil
  -- GMCP subscription is owned by this runtime and removed at unload.
end
