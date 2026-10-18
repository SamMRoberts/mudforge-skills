# Lifecycle and communication

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 2, 9,
14–16; reviewed 2026-10-18. The
[published guide](https://mudforge.org/docs/ai-plugin-guide.md) is a locator.
Contracts below are documented, not native-tested here.

## Metadata and hooks

Use a global `plugin` table with name, version, author, and description. Its
optional `id` is cosmetic: installed identity comes from the repository listing
or a generated file-import ID. `getPluginId()` returns that installed ID; find
another loaded plugin with `findPluginByName(name).id`. Keep repository listing
IDs stable across updates so users receive an update instead of a duplicate.
Omit ignored `engineType`. A plugin needs no `return plugin`; a library returns
its exported table. Settings must be plain literals readable before execution;
computed settings fall back to defaults with a warning.

Bare hooks and `plugin.<hook>` methods are accepted. Prefer native names:
`init`, `onEnable`, `onConnect`, `onDisconnect`, `onLine`, `onCommand`, `onSend`,
`onSaveState`, `onBroadcast`, `onDisable`, and `cleanup`. The documented
MUSHclient `OnPlugin*` aliases support ports; do not invent a camelCase alias
for every hook. `init` runs on load/enable, then `onEnable`; widget creation
at top level can defer init until the first canvas-ready event or a 2s timeout.
Register resources in init where possible, and redraw when widgets are ready.

Connection/line/command/send/save hooks receive session ID first:
`onLine(sessionId, rawLine, cleanLine)` and `onCommand(sessionId, command)`, for
example. Boolean false from line/command/send hooks blocks processing; nil
preserves it. `onBroadcast(senderId, message, data)` has a different signature.
On iOS reattachment, `onConnect` does not run; see
[protocol recovery](../../mudforge-events-protocols/references/protocols.md).

## Restart and ownership

Disabling runs `onDisable`, then `cleanup`. Runtime-owned triggers, aliases,
timers, widget handlers, and custom events end on unload; use explicit removal
for earlier teardown and clean up resources you allocated outside those APIs.
Do not invent `offGMCPUpdate`. Keep initialization idempotent within one runtime;
a full reload constructs a new runtime.

A world switch fully unloads plugins before loading them against the new world;
last old-instance writes still belong to the old world. Load world state in
`init()`, rather than expecting module locals to survive. Replaced saved data
also restarts the affected plugin: sync, restore, import, File Manager edits,
and another saving window can trigger this. Old-instance saves in the replaced
scope, including cleanup saves, are suppressed so they cannot overwrite the
replacement. Save on changes, not only at cleanup. Shared-name changes restart
plugins that used those changed global names; unaffected scopes stay writable.
See [storage](storage.md) for copy ownership, readiness, and multi-window saves.

## Commands and messages

`registerCommand(name, handler, description?)` registers a world-local terminal
command that works disconnected. The handler receives one argument string;
return a string for immediate terminal output, with `\r\n` between lines.
Use echo for later timer/HTTP output. Names are case-insensitive, share a
namespace with other plugins, and can collide with built-in commands; choose
a distinctive prefix. `addPaletteCommand(config)` adds a discoverable titled
action or toggle; palette registrations also end on unload.

Use namespaced `on`/`emit` for synchronous messages within one session, including
the sender; use `off(event, callback)` for early removal. Prevent recursive
re-emission. Cross-session `broadcast`/`onGlobal` also reaches the sender;
`onGlobal` returns a function to unsubscribe. MUSHclient-style `broadcastPlugin`
is world-local and excludes the sender, while `broadcastToPlugin` targets an
installed ID and can reach yourself. They are not cross-session substitutes.

For utility dependencies read [libraries](libraries.md); for integrations and
repository releases read [HTTP and publishing](http-publishing.md).
