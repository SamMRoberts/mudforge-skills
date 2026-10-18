# Runtime contracts

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 1, 3,
7–10, 12, and 17; reviewed 2026-10-18. The
[published guide](https://mudforge.org/docs/ai-plugin-guide.md) is a locator;
these are documented contracts, not native observations.

## Lua and transpilation

MudForge parses Lua 5.1 and transpiles it to JavaScript; no Lua VM runs plugins.
Avoid `goto`, integer division, bitwise operators, `_ENV`, dynamic loaders,
`debug`, metatables, and coroutines. Use plain tables and callback-based work.
Both global `unpack` and `table.unpack` are available in plugin scope.

Plugin and library scopes share `math`, `string`, and `table` implementations.
`string.*` patterns use Lua patterns, not trigger regex. The guide's §10 retains
an older statement about library pattern differences; §16 explicitly documents
restored stdlib parity. Follow §16 and verify an older installed build when
compatibility matters; do not recreate the obsolete split in new code.

Important differences from a real Lua VM:

- Multiple assignment receives multiple results, but most nested calls and
  table constructors keep only the first result. Destructure before forwarding.
  `unpack`/`select` can yield a table in a single-value context; do not assume
  `string.format("%d %d", unpack(t))` expands arguments.
- Nil arithmetic/concatenation can silently produce values instead of errors;
  validate inputs. `tonumber("")` is `0`, so reject blank strings explicitly
  when blank means unknown. Indexing a nil intermediate still raises.
- Strings normally count characters, not UTF-8 bytes. Binary `pickFile` data is
  the documented byte-string exception. `string.gsub` does not return a count;
  `%f` frontier patterns are unsupported. `math.randomseed` is a no-op.
- `string.format` does not implement `%u`, `%q`, `%b`, or `%n`. Prefer supported
  specifiers and explicit conversions. `tostring(table)` is not a unique ID.

## Triggers and aliases

| Interface | Contract |
|---|---|
| `addTrigger(pattern, fn, options)` | Default substring auto-upgrades for `*`/`?`; `{type="regex"}` selects JS regex. Invalid type/oversize pattern returns `""` with a warning. |
| Trigger callback | `(captures, line, wildcards, rawLine)`; first group is `wildcards[1]` or raw `captures[0]`. `wildcards[0]` is the matched text. |
| Trigger result | String replaces line, `false` gags, nil preserves it. |
| `oneShot=true` | Disables after matching; it does not delete the trigger. |
| `addAlias(pattern, "", fn, options)` | JS regex; callback suppresses replacement; `matches[1]` full match, `[2]` first group. |
| Removal | Use owned IDs with `removeTrigger(id)` / `removeAlias(id)`. Settings aliases are addressed by name through the documented `…ByName` APIs. |

Use `[0-9]` when it avoids double escaping; a regex `\d` in a Lua string must
be written `\\d`. Preserve `rawLine` for ANSI-dependent logic. The Fast & safe
engine normally preserves matches; backreferences still use native regex and
do not get its freeze protection. Do not change the player's engine setting
to repair a pattern.

Choose multiline behavior deliberately: `fireLength=N` keeps invoking the
callback on N following lines, whether they match or not;
`setTriggerStayOpen(nameOrId, n)` adjusts that gate. A continuation's whole line
appears in `line` and `wildcards[1]`. By contrast, `type="multiline"` with
`multilineCount` matches one regex across a joined window of lines.
Provisional prompt callbacks can precede line completion; do not count each as
a distinct server event or assume provisional rewrites are applied.

Use `feedTriggers(lines, onDone)` for client-side fixture replay and
`feedTriggersFromUrl(url, onDone)` for a log URL. Completion receives
`(elapsedMs, lineCount)` asynchronously. Replay runs real trigger callbacks:
use a disposable setup whose callbacks cannot send unintended game commands.
It tests matching in the client, not a live server's output or negotiation.

## Timers and script bodies

`addTimer(ms, fn, repeating?)` uses milliseconds and defaults to one-shot;
`setTimeout(fn, ms?)` reverses argument order. Both return `""` when refused,
including disconnected creation. Track IDs, cancel/reuse work, and prevent
duplicate loops on reconnect. Limits are 100 burst creations, 30/sec refill,
and 500 live timers per plugin. `isActiveSession()` means foreground; inspect
`getSession().connected` or use connection hooks for connection state, guarding
against a nil session.

Settings timers use names with `enableTimer` / `EnableTimer`, rather than plugin
timer IDs. These match exact name first, then an unambiguous case-insensitive
name; `findTimerByName` / `toggleTimerByName` are exact-name only. Imported
Settings timers can have different disconnected and one-shot behavior; do not
apply plugin-timer rules to them.

A Settings **Send To: Script** trigger/alias runs the whole body on every match.
Globals persist in a namespace shared with Script timers and Ctrl+I; locals are
rebuilt each execution. Guard timer creation and retain the ID. Disabling its
parent trigger does not cancel a created timer. World/session switching clears
those runtime resources. Script variable APIs address world variables; plugin
variable APIs address the plugin's own variables.

For captured command text prefer a Settings World Send box, which keeps captures
as text rather than command syntax. Concatenating captures into `Send` in native
script mode can process semicolons or client commands. MUSHclient placeholder
mode has its own Send rules; preserve the imported mode rather than assuming
native rules. Use `wildcards` instead of inserting captures into Lua source.

## Macros and quick actions

Create runtime bindings with `addMacro(key, action, options?)`; text actions
default to command processing, `sendTo="world"` sends directly, and a function
action receives the key. Register in `init()`; runtime bindings end on unload.
Use `removeMacro(id)` / `enableMacro(id)` / `disableMacro(id)` for your bindings,
and `findMacroByName` / `toggleMacroByName` for Settings bindings.

Only F1–F24 and numpad keys can be unmodified. Letters, arrows, Enter, and other
plain navigation/typing keys are refused (`nil` plus a warning). User Settings
macros win conflicting keys; between plugins the latest binding wins. Verify
focus and macOS/browser shortcuts when diagnosing a missing action.

For a saved user binding, Settings → Automation → Macros records a combination
and commands. Quick Actions provides visible command buttons. Reuse tested
commands and preserve unrelated bindings. Use
[storage contracts](../../mudforge-plugin-development/references/storage.md)
for strings, tables, pseudo-files, and real-file permissions.
