local M = {}
local api = nil
local directions = { n = true, s = true, e = true, w = true, ne = true, nw = true,
  se = true, sw = true, u = true, d = true }

local function validId(id)
  return type(id) == "number" and id > 0 and id < math.huge and id == math.floor(id)
end

function M.init(injected)
  assert(type(injected) == "table", "guarded-map requires injected mapper APIs")
  for _, key in ipairs({ "isMapReady", "getMapRoom", "addMapRoom", "setMapExit" }) do
    assert(type(injected[key]) == "function", "missing mapper API: " .. key)
  end
  api = injected
end

function M.ensureRoom(id, fields)
  assert(api, "call guarded-map.init first")
  if not api.isMapReady() then return "not-ready" end
  if not validId(id) or type(fields) ~= "table" or type(fields.name) ~= "string"
      or type(fields.area) ~= "string" then return "invalid-room" end
  local current = api.getMapRoom(id)
  if current then
    for key, value in pairs(fields) do
      if current[key] ~= value then return "room-conflict" end
    end
    return "unchanged"
  end
  if api.addMapRoom(id, fields) then return "created" end
  return "write-failed"
end

function M.ensureExit(from, direction, to)
  assert(api, "call guarded-map.init first")
  if not api.isMapReady() then return "not-ready" end
  if not validId(from) or not validId(to) or not directions[direction] then return "invalid-exit" end
  local source = api.getMapRoom(from)
  if not source or not api.getMapRoom(to) then return "missing-room" end
  local existing = source.exits and source.exits[direction]
  if existing ~= nil then
    if tonumber(existing) == to then return "unchanged" end
    return "exit-conflict"
  end
  if api.setMapExit(from, direction, to) then return "created" end
  return "write-failed"
end

return M
