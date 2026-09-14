plugin = {
  id = "mudforge-toolbox-canvas", name = "Toolbox Canvas",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "A resize-aware canvas with explicit active-widget selection."
}

local widget = nil
local initialized = false
local width = 240
local height = 100

local function draw()
  if not widget then return end
  setActiveWidget(widget)
  clear("#17212b")
  drawRect(8, 8, math.max(1, width - 16), math.max(1, height - 16), "#294455", "#75d6a5")
  drawText("Local canvas ready", 18, 40, "#f4f7fa", "16px monospace")
end

function init()
  if initialized then return end
  initialized = true
  widget = createWidget({ type = "canvas", name = "toolbox-canvas", title = "Toolbox Canvas",
    position = { x = 380, y = 90 }, size = { width = width, height = height } })
  registerWidgetEvent(widget, "resize", function(event)
    width = tonumber(event.width) or width
    height = tonumber(event.height) or height
    draw()
  end)
  draw()
end

function cleanup()
  if widget then destroyWidget(widget) end
  widget = nil
end
