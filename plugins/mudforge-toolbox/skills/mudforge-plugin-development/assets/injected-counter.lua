local M = {}
local api = nil
local count = 0

function M.init(injected)
  assert(type(injected) == "table" and type(injected.echo) == "function",
    "injected-counter requires echo")
  api = injected
end

function M.tick()
  assert(api, "call injected-counter.init first")
  count = count + 1
  api.echo("Library count: " .. tostring(count))
  return count
end

return M
