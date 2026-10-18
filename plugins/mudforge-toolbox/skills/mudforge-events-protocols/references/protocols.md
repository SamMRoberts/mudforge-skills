# Protocol and event contracts

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 11–14;
reviewed 2026-10-18. The [published guide](https://mudforge.org/docs/ai-plugin-guide.md)
is a locator. These are documented contracts, not native transport observations.

## Protocol data

| API | Meaning |
|---|---|
| `getGMCPData(packageName?)` | This session's cached package, possibly nil; omit package for all. |
| `onGMCPUpdate(packageName, fn)` | Session-scoped `fn(data)`. |
| `onGMCPUpdateGlobal(packageName, fn)` | All sessions, `fn(data, sessionId)`; note reversed order relative to global MSDP. |
| `sendGMCP(package, data?)` | Returns whether handed to connected transport; table data JSON-encodes, string appends verbatim, one argument may be a full message. |
| `getMSDPVariable(name)` / `getAllMSDPVariables()` | This session's cached MSDP values. |
| `onMSDPChange(name, fn)` | Session-scoped `fn(newValue, oldValue)`. |
| `onMSDPChangeGlobal(name, fn)` | All sessions, `fn(sessionId,newValue,oldValue)`. |
| `getSessionId()` / `getSession()` | Plugin's session ID or session record, possibly nil; record includes connected/active. |
| `getSessionGMCP(nameOrId, package?)` / `getSessionMSDP(nameOrId, variable?)` | Explicit cross-session caches. |

Subscribe at init, optionally seed from current caches, then handle updates.
Schema comes from the actual server, not the package's standard-looking name.
For a partial scalar update retain that session's omitted fields; mark explicit
invalid values unknown. Validate numbers before arithmetic, including blank or
whitespace strings: the transpiler can convert blank to zero. Do not invent
zero health, zero maximum, or a connection from a foreground flag.

Reset transient state on disconnect. Cached values can be stale on reconnect;
track freshness if the feature requires it. On iOS, `on("reattached", fn)` fires
instead of connected/onConnect when the screen reloads around an existing
connection. Latest GMCP/MSDP caches are restored, but protocol callbacks are not
replayed. Seed appropriate state from those caches and resume needed observers
without login commands. The bundled session-vitals example demonstrates partial
update logic; add cache seeding/reattachment for a feature that needs it.

`sendGMCP` success means transport handoff, not server acceptance. Failure warns
for disconnected transport, missing package, or a space in a two-argument package
name. Inspect actual server replies before claiming negotiation. Callback errors
surface as terminal GMCP/MSDP errors with repeated-message suppression.

Server GMCP `Client.Package` advertisements require an HTTPS `url` and `version`;
accepted shapes are one object, an array, or an object keyed by client name.
The client advertises `Client.Package 1` support and owns installation consent,
including when the server marks an offer required. Keep advertised and bundle
versions equal and packageId stable. An advertisement is not permission for a
plugin to fetch or install content silently. For bundle contents, hashes,
authoring/import, and uninstall behavior, read
[package contracts](../../mudforge-worlds-migration/references/formats.md).

## Events and session boundaries

`on(event, fn)` / `emit(event, data?)` delivers synchronously within one session,
in registration order, including the emitter. A throwing handler does not block
others; handlers registered during an emit start on the next emit. Use namespaced
custom names, distinct source/derived events, and guards against recursive emits.
Use `off(event, callback)` for early removal; runtime handlers end on unload.

Built-in `connected`, `disconnected`, and `reattached` events have a sessionId
field. `line` has text (raw ANSI), clean, sessionId, and optional provisional.
It does not fire for a line discarded by onLine. A provisional prompt is not a
second completed server event. `windowResize` carries width/height. For raw DOM
window events, `addEventHandler(name, fn)` passes the DOM Event with payload in
`event.detail`, not the custom-event Lua table; unload removes it automatically.
Do not invent a GMCP unsubscribe API; verify cleanup natively when required.

`onGlobal(event, fn)` subscribes across sessions and returns an unsubscribe
function. `broadcast(event, data?)` reaches your own session too; origin is in
`data.__sessionId`. `emitToSession(nameOrId, event, data?)` targets one session.
These differ from the world-local plugin-ID channels `broadcastPlugin` and
`broadcastToPlugin`; the former excludes the sender, the latter can target self.

Use `getAllSessions()` or `getSessionById` / `getSessionByName` to resolve targets;
tab names are case-sensitive. `isActiveSession()` reports foreground status.
`sendToSession` / `sendToSessionId` send directly to the target MUD without
aliases or command stacking. `sendToAll` / `sendToOthers` process as typed in
each target world, so aliases apply. Targeted sends return false and warn when
missing/disconnected; do not retry blindly or accidentally broadcast fallback
commands. Cross-session actions need an actual requested use case.

`getAllSessionGMCP(package)` returns session-ID keys containing name/data;
`getAllSessionMSDP(variable?)` includes only sessions reporting CHARACTER_NAME.
Global observers have different argument orders; keep IDs explicit in per-session
state and test two sessions with conflicting values. `getSessionVariable` /
`setSessionVariable` optionally address a plugin's own variable using pluginId;
world variables and default plugin variables have distinct ownership. For
persisted cross-plugin access use
[storage contracts](../../mudforge-plugin-development/references/storage.md).

## Verification

Exercise partial/missing/blank/malformed fields, independent sessions,
reconnect/reattachment, and duplicate registration. Callback fixtures prove
payload logic only. Transport acceptance needs a real connection, even when
its peer is local. Keep private raw logs out of source control and redact
authentication, private messages, and history.
