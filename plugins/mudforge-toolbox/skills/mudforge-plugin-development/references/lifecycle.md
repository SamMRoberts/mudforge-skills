# Lifecycle, libraries, and communication

Source: [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), sections
2, 9, 14–16. Reviewed 2026-09-14.

New plugin metadata contains `id`, `name`, `version`, `author`, and `description`.
Use a stable unique ID; changing it can detach saved state and widget identity.
`settings.saveState` defaults true. Omit ignored `engineType`. A plugin does not
need `return plugin`; a library returns its exported table.

Initialization runs on load/enable, followed by `onEnable`. Disabling runs
`onDisable`, then `cleanup`. Connection/line/command hooks receive session ID
first: `onConnect(sessionId)`, `onDisconnect(sessionId)`,
`onLine(sessionId, rawLine, cleanLine)`. Returning false from line/command/send
hooks suppresses processing; use it only for the requested behavior.

Runtime-owned triggers, aliases, timers, custom events, and widget event
subscriptions are documented as cleaned on unload. Do not invent
`offGMCPUpdate`. An init guard prevents duplicate subscriptions if a helper
accidentally calls init twice; a full reload constructs a new runtime. For
manual teardown/restart within one runtime, use documented removal APIs and
retain subscription ownership instead of re-registering callbacks blindly.

Library names are flat alphanumeric/underscore/hyphen names (max 64 chars for
top-level require). No `.lua` extension, path, or dots. Each consuming plugin
gets a separate library instance; repeat require in that plugin is cached.
Libraries lack plugin APIs. Accept a narrow table of injected functions in
`init`, not an entire ambient environment. Diagnose missing libraries and
circular imports from the actual loader error.

Use `on`/`emit` for events shared within one session, and `off` for explicit
early removal. Emission also reaches the sender; avoid recursive re-emission.
Use namespaced event names. Cross-session `broadcast`/`onGlobal` also reaches
the sender; use it only when cross-session behavior is requested.

Prefer no network or filesystem permission for local automation. HTTP calls
are HTTPS-only and have per-domain permission handling; never hard-code tokens
or ask for broad permission merely to make a sample run.
