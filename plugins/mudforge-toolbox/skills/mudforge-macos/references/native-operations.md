# Native operations

## Storage and backup

Observed application identifier: `com.mudforge.app`. Candidate locations include
`~/Library/Application Support/com.mudforge.app`,
`~/Library/WebKit/com.mudforge.app`, and `~/MudForge`. These are discovery hints,
not a universal schema; use the diagnosed bundle ID and inspect existence first.
WebKit/IndexedDB state can coexist with desktop files. Backing up only a plugins
folder does not preserve worlds and maps.

Use Export World from the session-tab menu and include maps and plugins before
an authorized import or upgrade. Keep exports private: they can contain saved
variables, connection data, and optional command history. Verify the export can
be inspected and retain its checksum. For a whole-profile filesystem snapshot,
close the app after saving and copy discovered storage roots to a private backup;
do not copy only SQLite main files while WAL writers are active. Do not edit live
SQLite/IndexedDB records as an installation shortcut.

Default plugin variables, tables and pseudo-files travel with their world and
belong to the installed plugin ID. App-wide `"global"` storage uses the client's
storage engine rather than a desktop folder; include it in a full backup.
File Manager on the session-tab menu exposes stored data: a plugin's
`worlds/<world>/plugins/<id>.state.json` can be edited there, causing a reload.
The adjacent Lua file is a read-only browsing copy; edit code in Plugin Editor.

## Plugin files and permissions

Without File System Access, `io.open` addresses portable pseudo-files rather
than Mac paths; a path that looks absolute is still only a storage key.
`loadPluginFile`/`savePluginFile` always address this storage, including when
real-file access is enabled. A missing read returns nil, write mode truncates
at open, and repeated writes accumulate.

Desktop File System Access is opt-in per plugin. With it enabled, `io.*` uses
real UTF-8 text files inside the user's home directory; relative names resolve
under `~/MudForge/plugin-files/<plugin>/`. Traversal or symlinks escaping home
are refused; `os.remove`/`os.rename` use the same permission and path boundary.
This does not supply shell execution. Reads/writes have a 16 MiB per-call limit,
directory listings a 20,000-entry limit, and calls a 5-second timeout. A nil open can mean missing or
refused access. The switch does not migrate earlier pseudo-files; use the
plugin-file functions to read those. The toggle is absent on web/iOS.
Enable it only for a feature that needs real files, such as explicit export.

For a user-selected import, `pickFile` works across platforms without granting
general file access. It completes by callback; cancellation is expected. The
built-in SQLite library takes its binary byte-string input and is read-only,
with no SQL and no WAL visibility; close the source program before exporting
a database. It is separate from MudForge's own native storage implementation.

## Disposable acceptance

Create a clearly named test world, with auto-connect off and no real credentials.
Capture the original selected world and inventory/export existing worlds first.
Keep app-wide settings and global plugin storage out of test fixtures. Install
fixtures only into the test world. Export and reimport into a second disposable
world to test persistence and conflict handling. Remove only identified test
resources, restore the original selected world, and compare existing world/map
content with the baseline (not volatile timestamps).

Disconnected `addTimer` is expected to refuse creation. To validate timer and
transport behavior use an explicitly local loopback fixture, bound to 127.0.0.1,
never a public MUD. Keep disconnected UI/lifecycle tests separate from transport
acceptance. If safe isolation or UI control is unavailable, stop that portion and
record the concrete blocker.

## Troubleshooting

- Startup/update: check app version, architecture, and the official release asset.
  Do not remove quarantine, disable Gatekeeper, or assume a reinstall fixes data.
- UI: record scale/window size, active world, widget type, and actual error.
- Script: capture a minimal failing line and invoke the Lua/plugin skills.
  Read Plugin Editor Problems/Console and `[Plugin Warning]` output. Warnings
  identify refused/no-op calls and may appear only once per target; absence on
  a repeated call is not evidence of success. Plugin Manager → Settings → Enable
  plugin debugging controls verbose console output; `settings.debugMode` does not.
- Connection: preserve TLS verification; distinguish transport from GMCP content.
- Persistence: check active world, plugin ID, scope, save settings, and a real
  save/reopen cycle. A successful `setVariable` call alone proves no disk write.
  `saveState = false` still writes individual variables. `storageStatus(scope?)`
  distinguishes ready, starting, and failed storage; capture the reason if given.
  A world switch restarts plugins. External saved-data replacement also restarts
  affected plugins and suppresses their stale writes, including cleanup saves;
  inspect the terminal's reload reason before diagnosing missing progress.

Sources: [connections](https://mudforge.org/#/docs/connections),
[worlds](https://mudforge.org/#/docs/world-files), and
[downloads](https://github.com/Coffee-Nerd/MudForge). Plugin file/persistence and
debugging guidance: supplied official [authoring guide](https://mudforge.org/docs/ai-plugin-guide.md),
reviewed 2026-10-18, §§2–3, 9, 16, 19.5, 22.
