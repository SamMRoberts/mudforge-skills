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
- Connection: preserve TLS verification; distinguish transport from GMCP content.
- Persistence: check active world, plugin ID, scope, save settings, and a real
  save/reopen cycle. A successful `setVariable` call alone proves no disk write.

Sources: [connections](https://mudforge.org/#/docs/connections),
[worlds](https://mudforge.org/#/docs/world-files), and
[downloads](https://github.com/Coffee-Nerd/MudForge).
