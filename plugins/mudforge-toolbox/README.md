# MudForge Toolbox 0.1.0

Eight Codex skills and three specialist agents for macOS MudForge. The skills
cover native operations, Lua, plugins/libraries, widgets, protocols, mapping,
worlds/migration, and testing. Start with the relevant skill in `skills/`.
Read [compatibility and sources](references/compatibility.md) for version and
evidence boundaries. This bundle does not include an MCP server or a UI driver.

## Install and activate

This is a **Codex plugin**, not a MudForge content package. The source repository
ships the `mudforge-skills` marketplace. From its repository root, run:

```sh
codex plugin marketplace add .
codex plugin add mudforge-toolbox@mudforge-skills
```

Once the catalog is published to GitHub, replace `.` in the first command with
`SamMRoberts/mudforge-skills` to install without a local checkout. Start a new
Codex task after installation so the skills are discovered. Nothing in these
helpers modifies a marketplace or installs into your personal environment
automatically.

For a standalone ZIP, extract it into a directory named `mudforge-toolbox`.
For a private local marketplace, place the extracted folder at
`<marketplace-root>/plugins/mudforge-toolbox` and create
`<marketplace-root>/.agents/plugins/marketplace.json` with this entry:

```json
{
  "name": "mudforge-local",
  "interface": {"displayName": "MudForge Local"},
  "plugins": [{
    "name": "mudforge-toolbox",
    "source": {"source": "local", "path": "./plugins/mudforge-toolbox"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Developer Tools"
  }]
}
```

Then run `codex plugin marketplace add <marketplace-root>` and
`codex plugin add mudforge-toolbox@mudforge-local`. This is a user-run example,
separate from the repository's `mudforge-skills` marketplace. Check your installed
CLI's `codex plugin --help` if its install interface differs.

Custom agents are separate from skills' `agents/openai.yaml` display metadata.
After installing the skills, activate the TOML definitions for an explicit
project (Python 3.11+; commands run from the extracted plugin):

```sh
python3 scripts/activate_agents.py --project /absolute/path/to/project --dry-run
python3 scripts/activate_agents.py --project /absolute/path/to/project
```

The helper writes only the three `.codex/agents/*.toml` files. Identical files
are accepted; conflicts are refused before writes. It does not alter global
configuration or model settings. Start a new task in that project and ask Codex
to use `mudforge-developer`, `mudforge-diagnostics`, or `mudforge-qa`. Agents find
skills through installed plugin discovery or a bundle path supplied in the task.
Remove only those three files to undo activation; preserve unrelated agents.

## Helpers

```sh
python3 scripts/diagnose_macos.py
python3 scripts/diagnose_macos.py --app /Applications/MudForge.app
python3 scripts/inspect_artifact.py /absolute/path/to/world.mfw
python3 scripts/validate_plugin.py .
python3 scripts/build_plugin.py --output /absolute/path/to/mudforge-toolbox.zip
```

Diagnostics, inspection, and activation use only Python's standard library.
Validation/build require PyYAML 6.0.3. Install it in a virtual environment.
Inspection exit codes: 0 = documented envelope checked, 1 = rejected/unreadable,
2 = unsupported schema/format. None is a native import acceptance claim. Limits:
64 MiB artifact, 32 MiB per member, 256 MiB expanded, 4096 members, ratio 200.
Inspection does not extract files, execute Lua, or print embedded values/names.

## Examples

Import the `.lua` plugin examples through MudForge's plugin UI in a disposable
world. Install `injected-counter.lua` as a library before its consumer;
`guarded-map.lua` is also a library, not a standalone plugin. Commands include
`toolbox-count`, `toolbox-score 42`, `toolbox-vitals-demo`,
`toolbox-protocol-demo`, and `toolbox-map-inspect`. `toolbox-delay` requires a
connected test session; `toolbox-cancel` cancels it. Examples never send game
commands or walk automatically.

`Char.Vitals` and `HEALTH`/`HEALTH_MAX` are demonstration schemas, not promises
about any particular MUD. The synthetic commands bypass transport and matching.
Use the [acceptance procedure](skills/mudforge-testing/references/acceptance.md)
for native verification and preserve existing worlds/maps before native writes.

## Current acceptance

The initial target is installed MudForge 1.2.2394 on Apple Silicon. Native UI
access was denied during this release's implementation; renderer, transpiler,
transport, persistence, import/export, and cleanup acceptance remain pending.
Source-repository tests exercise logic with Lua 5.1 and injected API boundaries;
they do not emulate MudForge's entire runtime. See the repository verification
report for executed commands and results. Intel macOS remains untested.
