plugin = {
  id = "mudforge-toolbox-map", name = "Toolbox Map Inspector",
  version = "0.1.0", author = "MudForge Toolbox",
  description = "Read-only map readiness and current-room inspection."
}

local initialized = false
local function inspect()
  if not isMapReady() then echo("Map is not ready.") return end
  local id = getPlayerRoom()
  if not id then echo("No current room reported.") return end
  local room = getMapRoom(id)
  if not room then echo("Current room is not mapped.") return end
  echo("Mapped room " .. tostring(id) .. ": " .. tostring(room.name))
  local rooms = getAreaRooms(room.area)
  for i = 0, #rooms - 1 do
    echo("Area room: " .. tostring(rooms[i]))
  end
end

function init()
  if initialized then return end
  initialized = true
  registerCommand("toolbox-map-inspect", inspect, "Inspect the current map without editing")
  onMapReady(function() echo("Map snapshot ready; use toolbox-map-inspect.") end)
end

function cleanup() end
