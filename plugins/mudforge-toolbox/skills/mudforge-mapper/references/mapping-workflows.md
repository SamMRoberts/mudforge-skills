# Mapping workflows and visual layers

Source: [official authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
section 11.5; user-supplied guide reviewed 2026-10-18.

## Identities, text mapping, and layout updates

For a text-only MUD, parse a stable room identity, create rooms and both intended
exit directions, then call `setPlayerRoom(id)`. It sets the route origin and map
cursor without moving the room; subsequent MUD room protocol updates can
replace this position. It works without an open map widget once data is ready.

For string identities, use `getRoomIDbyHash(hash)`; unknown returns **-1**, not
nil. Allocate a local ID with `nextFreeRoomId(hint?)` only when necessary and
bind with `setRoomIDbyHash(id,hash)`. The built-in mapper already assigns stable
synthetic numeric IDs and hash bindings for MUD string UIDs; look them up before
creating a parallel identity. `getRoomHashByID` performs reverse lookup; an
empty hash clears a binding.

Record unknown compass destinations with `setExitStub(vnum,dir,true)` rather
than fake room IDs. Stubs accept compass directions only.
`connectExitStub(vnum,dir)` looks one grid step away; the destination-ID variant
infers direction from coordinates or a sole stub. It creates the forward exit
and clears that stub; a matching reverse stub also creates the return exit.
Compare existing topology first when preservation is required.

`mergeMapRooms(rooms)` is for authoritative MUD-supplied layout windows. It
creates missing rooms, changes supplied existing fields, adds/replaces supplied
exits, preserves unspecified exits, and removes exits explicitly set to false.
It returns changed-room count; unchanged rooms are not rewritten. This differs
from preservation-oriented `importMapJson(...,{merge=true})`: do not substitute
it when existing exits must win conflicts. Supply validated IDs and only fields
the source actually owns.

Door status is per direction: 0 removes, 1 open, 2 closed, 3 locked. Routing
locks are controlled separately with `lockRoom`/`lockExit`; use explicit states
for repeatable updates. Room weights must be finite and at least 1.

## Persistent annotations and transient overlays

Saved annotations render immediately and travel with full-map exports; do not
reapply them on every `onMapReady` as though they were temporary highlights.

- `setRoomColor` overrides terrain color/texture. `setCustomEnvColor` registers
  a CSS color for a terrain/environment ID. Nil clears either override.
- `setRoomSymbol` sets a 1–2-character glyph and optional CSS color.
  `setRoomHidden` omits rendering while retaining the room in reads and routes.
- `addMapLabel(area,x,y,z,text,opts?)` returns a label ID; empty area displays in
  every area. Text labels persist unless `temporary=true`; image labels are
  unsupported. `getMapLabels` includes global labels in area-filtered results.
- Flags are lowercase semantic tags with optional color/icon/symbol definitions.
  `defineMapFlag` replaces a definition; deleting it keeps tags on rooms.
  `setRoomFlag(id,name,true/false)` is idempotent; omitting state toggles and
  returns the new state, so false is not necessarily a failed call.
- Room/area/map user data are string-valued bags; nil deletes a key. Whole-map
  searches such as `getRoomsWithFlag` and `searchRoomUserData` are O(V), so avoid
  invoking them inside a hot rendering loop.

Visual precedence is room color over flag color over terrain; a room's symbol
over flag symbol over vnum. Avoid redefining player-owned flag definitions or
clearing shared annotation bags without task authorization.

`highlightRoom` and `highlightPath` are plugin-owned ephemeral overlays, cleared
on unload/reload. Reapply desired highlights after map readiness/world changes.
Path highlighting needs at least two room IDs; prepend the start to
`findPath(...).vnums`. No-argument `unhighlightRoom`/`unhighlightPath` clears
this plugin's overlays, not saved room colors or another plugin's highlights.
`setMapLight` is also transient and plugin-owned; radius is 0–50 and ambient
0–1, with optional source-room lights. The user's dimming/line-of-sight settings
still govern display. `setMapLight()` clears this plugin's light.

Area names are strings. `addAreaName` can register an empty area;
`deleteArea` removes the registry entry **and its rooms**. `resetRoomArea` instead
moves one room to the empty zone. Do not confuse registry cleanup with a safe
room-preserving operation.

## Minimap and events

For a complete native minimap plus hand-drawn radar starter, see
[mapper-minimap.lua](../assets/mapper-minimap.lua) and its
[custom-map example notes](custom-map-example.md). It uses map data without
editing rooms or walking; adapt its display rather than copying a map database.

`createMapperWidget(name,opts?)` returns an embedded real-map widget ID or nil.
Options include title/geometry, `lockedArea`, `fixedZoom` (0.1–2), and
`interactive` (false by default). It does not own map data, settings, or the
player cursor. Use the default read-only behavior for inspection; setting
interactive true enables click-to-walk and requires intended movement scope.

`onRoomChange(fn)` receives `(newVnum,oldVnum,room)` for MUD updates and
`setPlayerRoom`; room can be nil. `onMapUpdate(fn)` receives `{kind}` for
rooms-saved, room-deleted, cleared, and imported changes. Use it to invalidate
cached reads. `onMapRoomClick(fn)` receives `(vnum,{button})` for primary and
embedded maps, regardless of whether the minimap walks on clicks.

## Acceptance deltas

In a disposable native world, check warm/cold reads and real zero-indexed arrays;
hash/stub round trips; protocol enrichment arriving before room creation;
locked/weighted routes without movement; and callback failure when the map is
closed. For imports compare conflict outcomes, exit topology, placement, and
full visual/user metadata before and after reload. Verify transient overlays
clear independently from persistent annotations. Exercise embedded-map clicks
and two-world event isolation; walk only if requested and test abort behavior.
