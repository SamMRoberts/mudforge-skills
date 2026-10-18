-- Adapted from MudForge's Mapper Minimap tutorial. The native minimap and
-- hand-drawn radar are retained; toolbox adaptations add guarded lifecycle,
-- map-update redraws, inherited fonts, input checks, and one replaceable flash.
-- This example reads map data and uses temporary highlights; it never walks
-- or changes saved rooms, exits, annotations, settings, or the player cursor.
plugin = {
  id = "mudforge-toolbox-mapper-minimap", name = "Toolbox Mapper Minimap",
  version = "0.1.2", author = "MudForge",
  description = "A native minimap and resize-aware canvas radar with a bounded click flash."
}

local initialized = false
local alive = false
local built = false
local minimap = nil
local radar = nil
local aliasId = nil
local flashTimer = nil
local flashRoom = nil
local flashGeneration = 0
local RADAR_RANGE = 4
local DIST_COLOR = {
  [1] = "#7CFFB2", [2] = "#4FD1C5", [3] = "#3B82C4", [4] = "#5A5F8A"
}

local function finiteNumber(value)
  if type(value) ~= "number" and type(value) ~= "string" then return nil end
  -- The host can coerce a blank string to zero; reject it before tonumber.
  if type(value) == "string" and value:match("^%s*$") then return nil end
  local number = tonumber(value)
  if not number or number ~= number or number <= -math.huge or number >= math.huge then return nil end
  return number
end

local function roomId(value)
  local number = finiteNumber(value)
  if number and number > 0 and number == math.floor(number) then return number end
  return nil
end

local function coordinates(room)
  if type(room) ~= "table" then return nil end
  local x, y, z = finiteNumber(room.x), finiteNumber(room.y), finiteNumber(room.z)
  if not x or not y or not z then return nil end
  return { x = x, y = y, z = z }
end

local function clearFlash()
  flashGeneration = flashGeneration + 1
  if flashTimer and flashTimer ~= "" then removeTimer(flashTimer) end
  flashTimer = nil
  if flashRoom then unhighlightRoom(flashRoom) end
  flashRoom = nil
end

local function drawRadar()
  if not alive or not radar then return end
  -- Other widgets and callbacks can change the active drawing target.
  setActiveWidget(radar)
  local width, height = finiteNumber(getCanvasWidth()), finiteNumber(getCanvasHeight())
  if not width or not height or width <= 0 or height <= 0 then return end
  local cx, cy = width / 2, height / 2
  clear("#0B0F17")
  if not isMapReady() then
    drawText("Waiting for the map...", 14, cy, "#6B7280")
    return
  end
  local meId = roomId(getPlayerRoom())
  if not meId then
    drawText("Waiting for your location...", 14, cy, "#6B7280")
    return
  end
  local me = coordinates(getMapRoom(meId))
  if not me then
    drawText("This room isn't mapped yet", 14, cy, "#6B7280")
    drawCircle(cx, cy, 4, "#FFD166", "#000000")
    return
  end

  local cell = (math.min(width, height) / 2) / (RADAR_RANGE + 1)
  for range = 1, RADAR_RANGE do
    drawCircle(cx, cy, range * cell, nil, "#1B2536")
  end
  drawLine(cx, 6, cx, height - 6, "#151D2B", 1)
  drawLine(6, cy, width - 6, cy, "#151D2B", 1)
  local font = getWidgetFont(radar)
  local northWidth = measureText("N", font.css).width
  drawText("N", cx - northWidth / 2, font.size + 4, "#3B4763")

  -- This result is keyed by vnum, not a zero-indexed mapper list. Its keys
  -- can be strings. Graph distance chooses colour; coordinates choose pixels.
  local nearby = findRoomsWithin(meId, RADAR_RANGE)
  if type(nearby) == "table" then
    for key, distance in pairs(nearby) do
      local id, dist = roomId(key), finiteNumber(distance)
      if id and dist and dist >= 1 and dist <= RADAR_RANGE and dist == math.floor(dist) then
        local room = coordinates(getMapRoom(id))
        if room and room.z == me.z then
          -- Map Y and canvas Y both increase southward; no axis flip.
          local px, py = cx + (room.x - me.x) * cell, cy + (room.y - me.y) * cell
          if px >= 4 and px <= width - 4 and py >= 4 and py <= height - 4 then
            drawCircle(px, py, 3, DIST_COLOR[dist])
          end
        end
      end
    end
  end
  -- Draw the player last so nearby rooms cannot obscure it.
  drawCircle(cx, cy, 4, "#FFD166", "#000000")
end

local function flashClickedRoom(value)
  if not alive or not built then return end
  local id = roomId(value)
  if not id then return end
  clearFlash()
  local room = nil
  if isMapReady() then room = getMapRoom(id) end
  local name = "room #" .. tostring(id)
  if type(room) == "table" and type(room.name) == "string" and not room.name:match("^%s*$") then
    name = room.name
  end
  echo("[Minimap] " .. name .. " (#" .. tostring(id) .. ")", "#22D3EE")

  -- Plugin timers require a connection. Offline clicks still name the room,
  -- but cannot leave a flash whose expiry timer would never run.
  local session = getSession()
  if not isMapReady() or not session or not session.connected then return end
  local generation = flashGeneration
  flashTimer = addTimer(3000, function()
    if not alive or generation ~= flashGeneration then return end
    flashTimer = nil
    clearFlash()
  end, false)
  if not flashTimer or flashTimer == "" then
    flashTimer = nil
    return
  end
  flashRoom = id
  if highlightRoom(id, "#22D3EE", { opacity = 0.55 }) == false then clearFlash() end
end

local function buildWidgets()
  if not alive or built then return end
  built = true
  minimap = createMapperWidget("minimap", {
    title = "Minimap", x = 24, y = 90, width = 280, height = 280,
    fixedZoom = 0.8, interactive = false
  })
  radar = createWidget({
    type = "canvas", name = "radar", title = "Radar",
    position = { x = 320, y = 90 }, size = { width = 220, height = 220 }, resizable = true
  })
  if radar then
    -- Initial dimensions come from creation; resize supplies later measurement,
    -- docking, and font-load changes. No connected timer is needed to paint.
    registerWidgetEvent(radar, "resize", drawRadar)
    drawRadar()
  end
  onRoomChange(drawRadar)
  onMapUpdate(drawRadar)
  onMapRoomClick(flashClickedRoom)
  if not minimap then echo("[Minimap] Native minimap unavailable.", "#9CA3AF") end
  echo("[Minimap] Ready. Type 'toolbox-radar' to toggle the radar.", "#7CFFB2")
end

function init()
  if initialized then return end
  initialized = true
  alive = true
  aliasId = addAlias("^toolbox-radar$", "", function()
    if not alive or not radar then return end
    if getWidgetProperty(radar, "visible") then
      hideWidget(radar, true)
      echo("[Minimap] Radar hidden. Type 'toolbox-radar' to show it again.", "#9CA3AF")
    else
      showWidget(radar, true)
      drawRadar()
      echo("[Minimap] Radar shown.", "#7CFFB2")
    end
  end, { name = "toolbox-radar-toggle" })
  onMapReady(buildWidgets)
end

function onDisconnect(sessionId)
  if alive and sessionId == getSessionId() then clearFlash() end
end

function cleanup()
  alive = false
  clearFlash()
  if aliasId and aliasId ~= "" then removeAlias(aliasId) end
  aliasId = nil
  if radar then destroyWidget(radar) end
  if minimap then destroyWidget(minimap) end
  radar, minimap = nil, nil
  -- Map subscriptions are runtime-owned; alive also protects captured callbacks.
  -- Re-enable uses a fresh runtime, as with the other toolbox examples.
end
