# Mapper contracts

Source: [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), section
11.5. Reviewed 2026-09-14.

`onMapReady(fn)` gates initial reads; `isMapReady()` can guard later commands.
`getPlayerRoom()` returns a number or nil, not a room. Pass it to `getMapRoom`
for a detached room record. Mutating that returned record does not edit storage.

Mapper lists such as `getAreaRooms`, search results, and path directions are
zero-indexed JavaScript arrays. Use `ipairs` in MudForge or explicit indices
`0..#list-1`. Ordinary Lua tables remain a different case; VM fixtures cannot
prove the array bridge. `findRoomsWithin` is a map keyed by vnum, iterated with
`pairs`, not a list.

| Canonical call | Contract |
|---|---|
| `addMapRoom(vnum, fields)` | False if room exists. |
| `updateMapRoom(vnum, patch)` | Changes supplied fields of an existing room. |
| `setMapExit(from, dir, to)` | Sets an exit; nil destination deletes it. |
| `addSpecialExit(from, command, to)` | Custom-command exit. |
| `findPath(from, to, opts)` | Record containing found, distance, directions, vnums, error. |
| `walkTo(vnum, callback)` | Movement; requires open map widget. |
| `stopWalk(callback)` | Stops movement. |
| `auditMap()` | Reports dangling/one-way exits and coordinate collisions; does not repair. |
| `exportMapJson(callback)` | Async full-map JSON export, including settings and visual metadata. |
| `importMapJson(json, callback)` | Full-map replacement, not a merge. |

Path distance is weighted cost, not necessarily hop count. Respect room/exit
locks and weights; do not default to `ignoreLocks`. Data reads work without a
map widget after readiness, but walking and view controls require one.
Writes update the snapshot immediately and are batched to storage; reopen to
verify persistence.

Mudlet port traps: `setExit(from,to,dir)` becomes `setMapExit(from,dir,to)`;
areas are strings; `getPath` does not establish Mudlet speedwalk globals.
Do not copy Mudlet room-ID assumptions or Geyser APIs into MudForge.
