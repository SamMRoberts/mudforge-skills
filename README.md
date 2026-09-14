# MudForge Toolbox

A macOS-first Codex plugin for developing and diagnosing the MudForge MUD
client. Version **0.1.0** includes eight skills, three separately activated
specialist agents, nine Lua examples, and five Python helpers.

The distributable source is in [plugins/mudforge-toolbox](plugins/mudforge-toolbox/README.md).
See that guide for plugin installation, explicit project-agent activation, and
example usage. Building this repository does not install or register anything
in your personal Codex environment.

| Skill | Coverage |
|---|---|
| `mudforge-macos` | Native setup, sessions, storage discovery, backups, and diagnosis |
| `mudforge-lua-scripting` | Triggers, aliases, timers, macros, variables, and runtime differences |
| `mudforge-plugin-development` | Lifecycle, reload, persistence, libraries, and communication |
| `mudforge-widgets` | HTML, canvas, text widgets, bindings, interaction, and layout |
| `mudforge-events-protocols` | GMCP, MSDP, partial updates, and session isolation |
| `mudforge-mapper` | Map readiness, room/exit identity, route queries, and safe edits |
| `mudforge-worlds-migration` | World/package inspection and assisted Mudlet/MUSHclient migration |
| `mudforge-testing` | Artifact validation, fixtures, and disposable native acceptance |

Agents: `mudforge-developer`, `mudforge-diagnostics` (read-only), and
`mudforge-qa`. Their TOML definitions are distinct from skills' UI metadata.

## Develop, test, and package

Python 3.11+ is required. The pinned development dependencies are PyYAML and
Lupa; tests deliberately select Lupa's Lua **5.1** module.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python plugins/mudforge-toolbox/scripts/validate_plugin.py
.venv/bin/python plugins/mudforge-toolbox/scripts/build_plugin.py --output dist/mudforge-toolbox.zip
```

The build emits `dist/mudforge-toolbox.zip` and `.zip.sha256`. It normalizes
timestamps, permissions, and ordering and uses stored ZIP members for
byte-for-byte reproducibility independent of compression-library versions.
Tests/research, caches, private exports, and Finder metadata are excluded.
Unexpected distributable files and symlinks fail the build.

## Native acceptance

Initial target: installed MudForge **1.2.2394**, macOS **arm64**. Native UI
access was denied, so native acceptance is **pending**, not passed. Offline
fixtures cannot prove MudForge's Lua-to-JavaScript transpiler, rendering,
transport, storage, or import/export behavior. Intel macOS is not locally tested.
See [verification](research/verification.md) and [source ledger](research/sources.md).

When native access is available, follow the bundled
[acceptance procedure](plugins/mudforge-toolbox/skills/mudforge-testing/references/acceptance.md).
Back up and inventory existing worlds/maps before creating a disposable test
world. A loopback-only Telnet fixture is provided for connected timer, trigger,
GMCP, and MSDP tests:

```sh
.venv/bin/python tests/serve_fixture.py
```

It prints a `127.0.0.1` address and ephemeral port. Connect only the disposable
world to that local address with TLS off. Import the relevant Lua examples and
type `fixture`, `partial`, or `invalid` to send synthetic payloads. Type
`toolbox-delay` then `toolbox-cancel` to test cancellation. Stop the local fixture
with Ctrl-C. It never connects outward and logs no client commands. Its own
socket test proves the fixture's wire output, not MudForge's response to it.

Application-source development, automatic cross-client converters, gameplay
agents, live public-MUD tests, and MCP bridges are outside this release.
