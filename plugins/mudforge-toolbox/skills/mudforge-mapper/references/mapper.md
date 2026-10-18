# Mapper contracts

Source: [official authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
section 11.5; reconciled with the user-supplied guide on 2026-10-18. Documented
behavior does not establish acceptance in an installed build.

## Readiness and data shapes

`onMapReady(fn)` gates initial reads; `isMapReady()` guards later commands.
Before readiness, reads can return nil/empty and paths not-found. An unopened
world has no map yet. The map snapshot and writes belong to the plugin's world.
`getPlayerRoom()` returns a number or nil; pass it to `getMapRoom` to obtain a
detached room record. Changing that copy does not edit storage. Room `area`
and `zone` are equivalent zone strings, not numeric area IDs.

Mapper lists (`getAreaRooms`, `searchRooms`, path directions/vnums, flag results,
stubs) are zero-indexed JavaScript arrays: iterate with MudForge `ipairs` or
`0..#list-1`. `findRoomsWithin` instead returns a vnum-to-distance table,
excluding the start; use `pairs` and convert keys with `tonumber` before reuse.
Ordinary Lua arrays remain different; native array bridging needs native tests.

## Writes and failures

| Call | Contract |
|---|---|
| `addMapRoom(vnum, fields?)` | Creates a room; false if already present, with a warning when supplied fields were discarded |
| `updateMapRoom(vnum, patch)` | Changes supplied fields; can wait for a room the open map is about to create |
| `setMapExit(from, dir, to?)` | Adds/changes an exit; nil removes; long compass names normalize |
| `addSpecialExit(from, command, to)` | Adds a custom-command exit; commands can stack with `;;` |
| `setPlayerRoom(vnum)` | Sets the player to an existing room; does not change its coordinates |
| `auditMap()` | Reports dangling/one-way exits and coordinate collisions; never repairs |

Writes are visible to this plugin's reads immediately and batch to storage in
about 250 ms. Reopen to verify persistence. A write returning true can also mean
it was held for automatic room creation: with the map open, enrichment from a
GMCP handler may run before the mapper adds that room. Only changed fields are
applied when it appears; if it never appears the write is dropped with a warning
8–16 seconds later. Without an open map, absent-room writes fail immediately.

`setPlayerRoom`, deletion, stub connection, and clearing/removal operations
require the real room; perform them after it exists, such as in `onRoomChange`.
Do not infer that a queued create overwrote the auto-mapper's fields. A partial
patch may accept valid fields and warn about invalid ones. Inspect relevant
records and warnings rather than equating one return value with atomic success.

Most failed writes warn once per distinct problem; reads usually return their
empty/false result silently. Readiness-dependent stats/audit/free-ID calls warn.
Result callbacks receive `{success=false,error=...}` instead of a printed
failure; immediately invalid arguments can both warn and call back. Map-load
and storage failures also warn: visible changes may be lost on reload.

## Routes and walking

`findPath(from,to,opts?)` returns `{found,distance,directions,vnums,error}`.
Distance is weighted cost, not necessarily hops; vnums omit the start. Room/exit
locks and weights apply to routes and walking. Step cost is an exit weight,
otherwise destination room weight, otherwise 1. A locked/avoided destination
has no path; a locked start can be left. Use `opts.avoid` for excluded room IDs;
do not default to `ignoreLocks=true` (weights still apply when it is set).
`getDistance` returns -1 if unreachable.

`walkTo(vnum,callback?)` completes its callback when the walk ends, returning
`{success,error,steps}`. `stopWalk(callback?)` aborts. Walking uses the real
map's walker settings, custom-exit pauses, and walk-command template. A special
exit wins a tie to the same neighbor when costs match; it does not lengthen the
route. Walking, `refreshMap`, and view controls need an open map widget; missing
widgets fail after roughly 2 seconds. Data APIs work headless after readiness.
Closing the map during a walk reports failure.

`setMapZoom`, `getMapView`, `setAreaView`, `setWalkDelay`, and `setFastWalk` use
callbacks and the open view; they are not substitutes for saved map edits.

## Import, export, and preservation

`exportMapJson(callback)` calls `callback(json,error)` asynchronously; JSON is
nil on failure. It exports the full map, including settings/state, labels, flag
definitions, custom environment colors, and area/map user data. Large maps can
produce tens of MB; validate a backup rather than logging its contents.
The callback's JSON is not itself a saved backup. Before an API import, use
Export World with maps included and verify that export through the
[native backup procedure](../../mudforge-macos/references/native-operations.md).

`importMapJson(json,callback?,options?)` has three distinct modes:

- Omitted options: destructive full replacement, including settings.
- `{merge=true}`: keeps existing positions, exits, notes, settings, labels, and
  visit counts; adds absent rooms/exits/notes and fills empty fields.
- `{keepSettings=true}`: replaces rooms while retaining settings/labels/extras.

Specify one intended mode rather than guessing precedence for combined flags.
The callback reports success/error, rooms, merged/layout information and, for
merge, `roomsAdded`, `roomsUpdated`, `exitsAdded`, `exitConflicts`, `notesAdded`.
Read those outcomes and inspect conflicts; a merge is not an atomic dry run.
Import rebuilds connections and emits update events. Rooms without positions
are laid out from exits; custom-exit islands are packed separately. During
merge, new-room coordinates are placed relative to existing connections rather
than copied from a different map's coordinate frame.

## Mudlet port traps

`setExit(from,to,dir)` uses a different argument order from
`setMapExit(from,dir,to)`; nil destination is refused by the alias, so use the
canonical removal call. `getAreaTable()` is `{[name]=name}`.
Destructure `getPath` into `found,distance` and `getRoomCoordinates` into
`x,y,z`: a single receiver can get a zero-indexed result list, making
`if getPath(a,b)` always truthy. Prefer `findPath(a,b).found`.
`speedWalkDir`/`speedWalkPath` are not populated. `centerview` aliases
`setPlayerRoom`, not coordinate changes. Label/color APIs use CSS strings,
not Mudlet RGB triplets, and `createMapLabel` has a different argument order.
Do not copy Geyser APIs or Mudlet numeric area assumptions into MudForge.
