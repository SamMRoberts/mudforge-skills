---
name: mudforge-plugin-development
description: Author and repair MudForge Lua plugins and shared libraries, including lifecycle, reload, persistence, dependencies, and plugin communication.
---

# Plugin development

Start with [lifecycle and libraries](references/lifecycle.md) and the
[compatibility notes](../../references/compatibility.md). Confirm the expected
world/session, commands, widgets, persistence, and permissions. A Codex plugin
manifest and a MudForge Lua plugin are different artifacts.

Use a global `plugin` metadata table and bare `init`/`cleanup` functions. Register
resources during initialization; avoid side effects during top-level evaluation.
Keep initialization idempotent within one runtime. Let the runtime remove its
tracked subscriptions on unload; explicitly release owned resources and cancel
pending work where the workflow needs earlier teardown.

Use [lifecycle.lua](assets/lifecycle.lua) as the scalar persistence starter.
Use [injected-counter.lua](assets/injected-counter.lua) and
[library-consumer.lua](assets/library-consumer.lua) together for a flat-name
library with injected APIs. Inspect the consuming plugin and dependency chain
when diagnosing a library failure; do not add globals to make it work.

For widgets or protocol consumers, load their focused skills. For distribution,
use the client's documented plugin import/editor or package creation UI, then
test load, reload, disable, re-enable, and world save/reopen. No package format
is assumed from a filename alone.
