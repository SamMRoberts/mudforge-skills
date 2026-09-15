# Compatibility and evidence

Reference review: 2026-09-14. Initial installed application: MudForge 1.2.2394,
macOS Apple Silicon. This identifies a target, not a native acceptance pass.
Intel macOS is a documented distribution target, not locally tested.

## Sources

- [Client documentation](https://mudforge.org/#/docs): client operation and topic routing.
- [Authoring guide](https://mudforge.org/docs/ai-plugin-guide.md): Lua runtime,
  lifecycle, callbacks, storage, libraries, protocols, and mapper contracts.
- [Widgets and reactive binding](https://mudforge.org/#/docs/plugins): HTML events
  and `data-mud-bind` APIs absent from portions of the downloadable guide.
- [World files](https://mudforge.org/#/docs/world-files): ZIP worlds and legacy JSON imports.
- [Packages](https://mudforge.org/#/docs/packages): `.mfp` contents and merge/uninstall behavior.
- [Public project](https://github.com/Coffee-Nerd/MudForge): downloads and issues;
  the application source is private. Do not invent a source checkout or build commands.
- [Codex custom agents](https://developers.openai.com/codex/subagents): standalone
  TOML definitions with name, description, and developer_instructions.

## How to use evidence

Read the targeted reference, then verify the installed client's version and the
specific capability being changed. Documentation is mutable and may describe a
newer build. If an API is missing, report the version discrepancy and choose a
documented compatible approach; do not substitute Mudlet/Geyser calls by analogy.
The source ledger and verification report in the source repository record review
hashes and actual test results. No copied upstream manual is distributed here.

Distinguish four kinds of evidence: documentation, structural inspection,
fixture execution, and native observations. Parsing Lua or running it in a VM
does not test MudForge's JavaScript transpiler, transport, UI, or persistence.

## Known documentation ambiguities

- Guide section 9 first describes isolated default storage, then clarifies that
  saved tables are shared by plugins on the same world. Namespace saved-table
  names; use default-scope variables for plugin-local scalar state.
- `isActiveSession()` identifies the foreground session, not connectivity.
  Although the guide's error table suggests it as a connection guard, use
  connection hooks and handle an empty timer ID instead.
- The guide's widget event list is narrower than the online HTML-widget page.
  Check actual HTML action/key/submit and binding behavior in the target build.
- World import offers conflict modes; `importMapJson` replaces the entire map.
  Do not transfer the world-import merge guarantees to that mapper API.

## Boundaries

This is a Codex plugin that helps develop MudForge plugins. Its ZIP is not an
`.mfp` or `.mfw` and must not be imported into MudForge. No MCP server, gameplay
agent, auto-converter, or client-source build workflow is included. Native work
uses an available authorized computer-use tool; these skills do not supply one.
