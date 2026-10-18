# Storage and user-selected files

Source: user-supplied official `mud-client-ai-plugin-guide.md`, sections 2, 3,
9, and 16; reviewed 2026-10-18. These are documented contracts, not native tests.

## Ownership and durability

Default `setVariable`/`getVariable`, `saveTable`/`loadTable`, and plugin-file
APIs are isolated to this installed plugin and world. Other plugins must use
`getPluginVariable(installedId, name)` or `getPluginTable(installedId, name)`
explicitly. Sessions on the same world see the same saved table. Settings
Script bodies and Ctrl+I instead use the world's variables, separate from
plugin variables; deleting your plugin's variable does not delete the world's.

Passing `"global"` as the optional scope selects one app-wide namespace shared
by all plugins and worlds. Prefix shared names with your plugin name; match
scope on reads, writes, deletes, and bindings. Global persistence uses the app
storage engine and is included in full backups; it is not a normal disk folder.
Default data with a world open lives in its per-plugin state file. Do not treat
a disabled writer as removing shared data.

`setVariable` coerces to string; explicitly parse reads. Prefer `saveTable` for
structured data. `settings.saveState=false` only skips bulk scalar saves at
unload/world save: individual writes still persist and stored variables still
load. Temporary data belongs in ordinary Lua locals. Scalar writes coalesce
with a 50ms debounce; `saveState()` starts an immediate save and returns nothing.
`saveTable(name, table, scope?)` returns a boolean; handle false when the caller
needs confirmation rather than promising a successful save.

Read saved values in `init()`; with a world loaded, startup waits for its file
before plugins start. `loadTable` returns a copy; modifying it never persists
until `saveTable` is called, which also stores a copy. Load large data once and
keep it in memory, save on meaningful changes, and avoid reloading per line.
Every default-scope table, variable, and plugin file shares one state file, so
frequent small writes also rewrite large tables in that plugin. Consider a
separate rarely written data owner when measured cost justifies it.

`storageStatus(scope?)` returns `status, reason`, where status is `"ready"`,
`"starting"`, or `"failed"`. Destructure to obtain the reason; nested calls keep
only the first result. Use this API when a feature must choose behavior based
on durability; ordinary failed saves already report a terminal warning.
The guide conflicts on startup global writes: §1 says they can be lost while
§9 says `starting` writes are buffered. Do not promise durability before ready;
for critical shared writes wait for ready, often at `onConnect`, and verify the
target build. A failed global store drops writes; failed per-world persistence
can leave only in-memory data until closing.

External saved-data replacement reloads affected plugins. Save changes as they
occur and reload state in init; the old runtime's writes to a replaced scope
are skipped, including cleanup. With two windows on one world, only one saves;
a held window may restart affected plugins when it takes over, dropping its
stale interim progress. Do not implement a cleanup-only backup that overwrites
newer data. Test world switching and external replacement independently from
ordinary disable/re-enable.

## Pseudo-files and real files

`savePluginFile`, `loadPluginFile`, `appendPluginFile`, and `deletePluginFile`
use storage regardless of filesystem permission and accept optional scope.
Default `io.open` accesses pseudo-files there, not arbitrary Mac paths. Missing
read files return nil; write mode truncates at open; successive writes append
to the open file. Check failures and close handles.

Desktop **File System Access** is opt-in per plugin and changes `io.open` and
`io.lines` to real files; `os.remove`/`os.rename` work only in that mode. Paths
must stay inside the user's home, including symlink/traversal checks. Relative
paths resolve under `~/MudForge/plugin-files/<plugin>/`; `~` expands. Old
pseudo-files remain in storage and can be migrated through `loadPluginFile`.
This is UTF-8 text I/O, not binary: invalid bytes are replaced. Calls have a
16 MiB limit and 5s deadline; directory listings cap at 20,000 entries. Never
assume permission exists on web/iOS, and request it only for an actual real-file
feature. Fake `os.getenv` placeholders are not machine paths; `os.execute`,
`io.popen`, and raw `io.read` cannot provide a shell or file chooser.

## File picking and SQLite

`pickFile(callback, options?)` works on web, desktop, and iOS through a user
chooser. It returns nothing; the later callback receives
`(file, message, reason)`. Success file fields are `name`, `size`, `data`, and
`binary`; failures have nil file and reason `cancelled`, `too-large`,
`read-failed`, or `unavailable`. Treat cancellation normally. Options are title,
accept filter, `maxBytes` (64 MB default, 256 MB maximum), and `binary`.
With `binary=true`, data is one character per byte, unlike ordinary UTF-8 text.
Do not try to bypass the chooser or read an arbitrary host path.

Use bundled `require("sqlite")` for a read-only UTF-8 SQLite file chosen with
`binary=true`: `sqlite.open(file.data)` returns db or nil/reason. Inspect
`db:tables()`, `db:hasTable(name)`, and `db:columns(name)` before reading.
`db:rows(name)` reads all rows for small tables; use `db:cursor(name)` and
`cur:next(n)` batches for large data, with `cur:done()` / `cur:pagesRead()` for
progress. Connected timer ticks can pace batches; handle timer refusal rather
than silently dropping work. This reader provides no SQL or writes; pending
WAL changes are invisible, so close the owning program before exporting input.
NULL fields become nil and INTEGER PRIMARY KEY fields use rowid.
