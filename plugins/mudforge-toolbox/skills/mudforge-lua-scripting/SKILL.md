---
name: mudforge-lua-scripting
description: Write and debug MudForge Lua triggers, aliases, timers, macros, and variables using its capture conventions and transpiled runtime.
---

# Lua automation

Read [runtime contracts](references/runtime.md) before authoring code. Obtain a
real input line/command and expected output; preserve ANSI/raw text when it
affects matching. Choose substring, wildcard, or explicit JavaScript regex for
triggers. Alias patterns are JavaScript regex. Lua string patterns belong to a
different interface.

Trigger callbacks receive first capture at `c[1]`; alias callbacks receive the
full match at `m[1]` and first capture at `m[2]`. Test both using the original
input, including no-match and missing-data cases. Return a replacement string or
`false` only when the task requests rewriting or gagging a line. Preserve prompts
and unrelated output.

Track timer IDs, handle the empty disconnected result, and cancel/reuse pending
work instead of allocating on every line. Use connection hooks for connection
state. Treat variables as strings and explicitly convert numeric reads.

Adapt [automation.lua](assets/automation.lua) for a complete plugin example with
different trigger/alias captures, a replaceable delayed action, and cleanup.
Its commands print local status and do not send game commands. It registers a
timer only when the user invokes the delayed command.

Validate syntax, exercise callbacks with fixtures, then use
[native testing](../mudforge-testing/SKILL.md). VM fixtures do not establish
transpiler or trigger-engine compatibility.
