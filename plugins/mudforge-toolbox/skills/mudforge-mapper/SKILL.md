---
name: mudforge-mapper
description: Develop and diagnose MudForge mapper integrations, room and exit edits, weighted routes, map imports, minimaps, and Mudlet mapper ports while preserving existing maps.
---

# Mapper

Read [mapper contracts](references/mapper.md). Identify the active world and
room-ID scheme. Capture relevant rooms, exits, coordinates, and protocol data
before diagnosing placement or proposing changes. For hash/stub mapping,
authoritative layouts, annotations, and embedded minimaps, read
[mapping workflows](references/mapping-workflows.md).

Wait for `onMapReady` for initial reads. Do not interpret a cold empty snapshot
as an empty map. Normalize external identities explicitly; maps are per world.
For preservation-oriented edits compare existing identities and exits before
writing, and report conflicts rather than silently overwriting. Use bulk
updates only when the task authorizes their replacement semantics.

[map-inspector.lua](assets/map-inspector.lua) is a read-only native example.
[guarded-map.lua](assets/guarded-map.lua) is an injected-API library that adds
only absent rooms/exits and reports conflicts; it is not a transactional
importer. Keep partial outcomes visible.

Plan routes without walking by default. Walk or enable click-to-walk only when
movement is requested; confirm the world and retain `stopWalk` as an abort path.
Before replacement or a consequential import, export and verify a backup and
validate the operation in a disposable world. Choose import options explicitly.
Compare rooms, exits, and metadata before/after; room counts alone do not prove
preservation. Verify saved results after reload, separately from immediate reads.
