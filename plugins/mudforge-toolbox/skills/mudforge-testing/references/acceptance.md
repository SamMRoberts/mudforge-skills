# Acceptance layers

## Offline

1. Check manifest/frontmatter/TOML, internal links, archive paths and contents.
2. Parse examples as Lua 5.1; run meaningful logic tests using injected APIs.
3. Test raw trigger `captures[0]` versus `wildcards[1]`, alias `matches[2]`,
   timer cancellation, repeated init,
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
| Trigger/alias | Run exact lines through `feedTriggers`, then type aliases; first group is raw `captures[0]`, trigger `wildcards[1]`, alias `matches[2]`. Use two distinct groups to expose off-by-one errors. |
| Disconnected plugin timer | `addTimer` refuses with an empty ID; imported Settings timers with active-when-closed behavior need separate migration checks. |
| Connected timer | Use loopback only; one callback, replace pending timer, cancel on disconnect/unload. |
| HTML/canvas | Actual render, click and keyboard action, text escaping, resize, stable focus during partial updates. |
| GMCP/MSDP | Loopback negotiation and payload delivery, partial/invalid updates, two isolated sessions. |
| Persistence | Save, disable/reload, close/reopen the disposable world, compare values. |
| State replacement | Switch disposable worlds and verify fresh `init()` reads. Replace plugin data through a supported import/File Manager edit; new data wins, stale cleanup writes are skipped, identical replacements do not restart. |
| Map | Wait for readiness, refuse conflicts, export/reimport visual extras; separately verify default replacement, `{ merge = true }` preservation, and `{ keepSettings = true }`. |
| Package/world | Native preview, selected conflict mode, local Import Package consent, install/update/uninstall, restored layout/settings and existing map content. |
| Cleanup | Remove only test resources; restore selected world and compare existing worlds/maps to baseline. |

## Focused runtime checks

Select only scenarios relevant to the change; these are native checks unless
explicitly described as injected logic fixtures.

- `feedTriggers(lineOrLines, onDone)` exercises the plugin's real matcher and
  per-line pipeline without connecting. Wait for `onDone(elapsedMs, lineCount)`;
  check rewrites, gags and colorization as well as callback state. A log replay
  through `feedTriggersFromUrl` also needs an accessible source and does not
  prove live transport. Avoid replaying triggers with unintended game actions.
- For saved tables, mutate a loaded copy without saving and verify the stored
  value is unchanged; save explicitly and check reload. Verify plugin/world
  isolation separately from namespaced `"global"` sharing. Ordinary `init()`
  reads need no delay once a world is open. Save changes as they happen.
- For replacement of global data, use separately authorized namespaced fixtures
  whose global names are otherwise unused: only users of changed names restart,
  and stale writes are suppressed only for the replaced scope. Same-world
  multi-window takeover needs its own preservation check; never simulate it by
  editing live storage files outside the client.
- Exercise `storageStatus`/save failure handling through injected boundaries
  when appropriate. This proves the plugin's response, not a disk failure.
  `saveState = false` does not make `setVariable` temporary.
- For file import, check `pickFile` callback success, cancellation and error;
  binary SQLite input must preserve byte values. The built-in `sqlite` reader
  is read-only, has no SQL, and does not include WAL changes. Test small row
  reads and bounded cursor batches with synthetic UTF-8 database fixtures.
- If real-file access is required, test both permission states and restoration
  in isolation, home-folder confinement, and separation from pseudo-files.
  Do not enable it merely to test ordinary plugin persistence.
- For UI changes, verify saved placement/visibility and dock-owned size as well
  as first load, resize, escaping and keyboard interaction. Check the HTML bridge
  ready handshake: custom messages sent before its receiver exists are lost;
  send initial custom data after the widget reports ready. Change a canvas's
  per-widget font and verify resize redraw, `getWidgetFont` metrics, and matching
  drawing/measurement fonts. For library changes,
  test dependency injection and Editor Save & Reload users, then check package
  library precedence/uninstall only when distribution changes.

Record `[Plugin Warning]` output alongside returned failures. Repeated calls may
be suppressed after the first warning for a target; disconnected-send warnings
reset after reconnect. Plugin Editor Problems/Console can report parse/load
errors at the Lua line. `plugin.settings.debugMode` has no effect; the client
debugging setting controls verbose console logs.

Never fabricate UI evidence. Synthetic commands directly invoking a handler
prove only that path; `feedTriggers` proves matching but not the protocol parser.
Lupa's Lua 5.1 behavior does not establish the transpiler's return expansion,
nil arithmetic, string/byte handling, or restricted standard-library behavior.
If a capability is inaccessible, document it as pending with a concrete blocker.

## Cross-platform acceptance

iOS `reattached` is a separate native acceptance scenario: a restored connection
does not call `onConnect` or replay protocol handlers. Verify the plugin reseeds
GMCP/MSDP state from the restored caches and rebuilds UI without repeating login
steps. Injected events can test that plugin logic; macOS acceptance cannot prove
iOS screen reload/reattachment. Keep that check pending until tested on iOS.

Source: [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md), supplied
official guide reviewed 2026-10-18, §§1–4, 7, 9, 11.5, 14, 16–17, 19.5, 22.
