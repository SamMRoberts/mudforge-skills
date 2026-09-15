# Runtime contracts

Source: [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), sections
1, 3, 7–10, 12, and 17; reviewed 2026-09-14.

MudForge parses Lua 5.1 and transpiles it to JavaScript. Avoid `goto`, integer
division, bitwise operators, `_ENV`, dynamic loaders, and `debug`. Plugin-scope
`table.unpack` exists while global `unpack` does not; library scope differs.
Prefer explicit numeric conversion and simple tables over VM-specific tricks.

| Interface | Contract |
|---|---|
| `addTrigger(pattern, fn, options)` | Default substring can auto-upgrade to wildcard for `*`/`?`; use `{type="regex"}` for JS regex. |
| Trigger callback | `(captures, line, wildcards, rawLine)`; capture 1 is `captures[1]`. |
| Trigger result | String replaces line, `false` gags, nil preserves it. |
| `oneShot=true` | Disables after matching; it does not delete the trigger. |
| `addAlias(pattern, "", fn, options)` | Callback suppresses replacement; `matches[1]` full match, `[2]` first capture. |
| `addTimer(ms, fn, repeating)` | Milliseconds; empty ID when disconnected. Repeating defaults false. |
| Removal | `removeTrigger(id)`, `removeAlias(id)`, `removeTimer(id)`. |

Use `[0-9]` when it avoids Lua/regex double escaping; a JS `\d` in a Lua quoted
string must be written `\\d`. Plugin `string.*` uses Lua patterns; libraries
have a smaller string API with different pattern behavior. Do pattern-heavy
work in the plugin and inject that operation into a library when needed.

Timers have documented creation/rate ceilings. Use one bounded worker or a
replaceable one-shot, not one timer per entity or packet. `isActiveSession()`
means foreground, not connected. Reconnects must not duplicate periodic work.
Provisional prompt triggers can fire before a line closes; do not assume each
callback is a distinct server event or that provisional rewrites are applied.

Default `setVariable` values are plugin/world-local strings. Use namespaced
`saveTable` keys for structured data: tables may be shared within the same world.
The optional `global` scope is shared across worlds and plugins. `saveTable`
persists regardless of the plugin's scalar `saveState` setting; scalar writes
are debounced. Verify persistence after saving/reopening.

Default `io.open` accesses pseudo-files, not Mac paths. Desktop File System
Access changes its meaning and requires per-plugin permission; prefer storage
APIs unless real files are necessary. `os.getenv` returns placeholders;
`os.execute`/`io.popen` do not provide a usable shell.

## Macros and quick actions

The [macro documentation](https://mudforge.org/#/docs/macros) routes creation
through Settings → Automation → Macros: record a key combination, enter the
commands, and save. Macros act on the active session while the client is focused.
Plain keys yield to focused command-line text input; function/numpad keys and
Ctrl/Alt/Cmd combinations have different dispatch rules. Dialogs/settings suspend
macros. Verify the actual macOS shortcut and focus context before diagnosing a
missing callback; browser shortcuts may intercept Cmd-number combinations.
Use Settings → Automation → Quick Actions for a visible command button. Bind
an existing tested command and preserve unrelated keybindings.
