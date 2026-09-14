---
name: mudforge-mapper
description: Develop and diagnose MudForge mapper integrations, room and exit edits, pathfinding, map imports, and Mudlet mapper ports while preserving existing maps.
---

# Mapper

Read [mapper contracts](references/mapper.md). Identify the active world and
room-ID scheme. Capture relevant room records, exits, coordinates, and current
protocol data before diagnosing placement or proposing a mutation.

Wait for `onMapReady` for initial reads. Do not interpret a cold empty snapshot
as an empty map. Normalize external identities explicitly; maps are per world.
Compare an existing room/exit before writing: block conflicting identities or
destinations and report the conflict instead of silently overwriting it.

[map-inspector.lua](assets/map-inspector.lua) is a read-only native example.
[guarded-map.lua](assets/guarded-map.lua) is an injected-API library that adds
only absent rooms and exits and reports conflicts. It is not a full converter
or transactional importer. Keep partial outcomes visible.

Plan routes without walking by default. Use `walkTo` only when movement is
requested, confirm the correct session, and retain an abort path. Before map
replacement, export and verify a backup, then validate in a disposable world.
Record rooms/exits and relevant metadata before/after; room counts alone do not
prove preservation.
