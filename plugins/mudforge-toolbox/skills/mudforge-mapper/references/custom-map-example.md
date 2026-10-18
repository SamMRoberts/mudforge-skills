# Native minimap and custom radar example

[mapper-minimap.lua](../assets/mapper-minimap.lua) is a maintained starter adapted
from the user-supplied **Mapper Minimap 1.0.1**, attributed to MudForge and
reviewed 2026-10-18. It demonstrates the client-native mapper API, not an
independent map store. The supplied source's claims about inspecting private
client source are not verification evidence for this toolbox.

## Two views of the same map

- `createMapperWidget("minimap", options)` embeds the real map engine and
  follows the player without plugin drawing code. `interactive=false` keeps
  click-to-walk disabled; room-click callbacks still work.
- The `radar` canvas reads `getPlayerRoom()`, `getMapRoom(vnum)`, and
  `findRoomsWithin(vnum, 4)`. It draws rings, room dots, and the player marker
  using active-widget drawing calls. It never creates or updates map rooms.

`findRoomsWithin` returns a keyed room-ID-to-distance table, excluding the
start room. Iterate with `pairs`, normalize keys with `tonumber`, and validate
finite IDs, distances, and coordinates before plotting. These records are not
the zero-indexed arrays returned by other mapper queries.

The radar preserves the supplied example's south-positive Y projection:
`screenX = centerX + (room.x - player.x) * cell`, and likewise for Y without
a sign flip. It plots only the player's floor. Graph distance chooses dot
color, while coordinate distance chooses position; a room reached by a short
custom exit may be offscreen and is clipped. The player is drawn last.
For a different projection, adapt those calculations explicitly and verify
orientation against known rooms in the target client.

## Lifecycle, drawing, and interaction

Initialization registers once; widget construction waits for `onMapReady`.
Readiness can be asynchronous even for a warm map. Guards prevent duplicate
construction and keep callbacks inert after cleanup. If native embedding fails,
the custom radar can still display mapped data.

The radar draws initially, then on room changes, map updates, resize/font
changes, and explicit show. Each pass selects its canvas and reads current
dimensions. Waiting/unmapped states remain explicit, malformed neighbors are
skipped, and omitted font arguments inherit the user's widget font. Docking
owns geometry, so reflow rather than repeatedly calling `resizeWidget`.

There is no startup delay that guarantees mounting. Drawing is batched by the
runtime; `clear(color)` discards pending draws and fills the background, rather
than flushing queued commands. Actual first-frame rendering still needs native
acceptance. See [canvas contracts](../../mudforge-widgets/references/canvas.md).

`toolbox-radar` replaces the supplied generic `radar` alias. It checks live
visibility and uses forced show/hide because the command is an explicit user
choice, including reopening a widget closed with its X button. It repaints on
show without overriding saved placement or dock-owned size.

Room clicks report a name without sending a command to the MUD. A connected
session can flash the latest clicked room for three seconds. One timer and one
owned highlight replace the previous flash; timer refusal leaves no highlight.
Disconnected clicks only report the room. Matching-session disconnect and
cleanup cancel the timer and clear the owned flash. Cleanup destroys both
widgets; the host removes runtime-owned aliases and event subscriptions on
unload. No persistent colors, topology, or other plugins' highlights are cleared.

## Adapting and verifying

Change widget names when adding more views, and change the alias prefix when
copying this starter into a different plugin. Customize range, colors, filters,
and projection through the existing draw function. Keep location identity in
the mapper rather than deriving another map from terminal text for this view.
See [mapper contracts](mapper.md) for reads and failure behavior.

Offline Lua 5.1 fixtures exercise readiness, lifecycle, projection, malformed
records, visibility, fonts, and timer decisions. They do not prove the native
mapper, JavaScript transpiler, rendering, event delivery, or layout persistence.
In a disposable native world, check first frame, floating/docked resizing,
font changes, mapped-room clicks with and without a connection, saved closure
and explicit reopen, reload cleanup, and two-world isolation. Keep native
acceptance pending until those observations exist; use the
[acceptance procedure](../../mudforge-testing/references/acceptance.md).
