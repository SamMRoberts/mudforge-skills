# Acceptance layers

## Offline

1. Check manifest/frontmatter/TOML, internal links, archive paths and contents.
2. Parse examples as Lua 5.1; run meaningful logic tests using injected APIs.
3. Test trigger versus alias capture indexes, timer cancellation, repeated init,
   string-coerced storage, partial updates, session isolation, markup safety, and
   refused map conflicts. Do not call a mock persistence dictionary a disk test.
4. Build twice and compare bytes, then extract the plugin and run its own helpers
   from an unrelated working directory. Confirm agents survive relocation.

## Native macOS

Use the [macOS isolation procedure](../../mudforge-macos/references/native-operations.md).
Record app version, architecture, exact fixture, original selected world, and
backup location privately before writes.

| Scenario | Acceptance |
|---|---|
| Load/reload/disable | One instance and one registration per resource; no stale widget or callback after unload. |
| Trigger/alias | Feed exact test lines via a local fixture and type aliases; captures have the documented indexes. |
| Disconnected timer | Explicit refusal/empty ID; no claim that timer fired. |
| Connected timer | Use loopback only; one callback, replace pending timer, cancel on disconnect/unload. |
| HTML/canvas | Actual render, click and keyboard action, text escaping, resize, stable focus during partial updates. |
| GMCP/MSDP | Loopback negotiation and payload delivery, partial/invalid updates, two isolated sessions. |
| Persistence | Save, disable/reload, close/reopen the disposable world, compare values. |
| Map | Wait for readiness, read known fixtures, refuse conflicts, export/reimport into disposable target. |
| Package/world | Native preview, selected conflict mode, install/uninstall, restored layout/settings and existing map content. |
| Cleanup | Remove only test resources; restore selected world and compare existing worlds/maps to baseline. |

Never fabricate UI evidence. Synthetic commands directly invoking a handler
prove only that path; they do not prove the server matcher or protocol parser.
If a capability is inaccessible, document it as pending with a concrete blocker.
