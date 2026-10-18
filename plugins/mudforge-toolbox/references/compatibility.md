# Compatibility and evidence

Authoring-guide review: 2026-10-18, using the user-supplied official guide.
Initial installed application observed on 2026-09-14: MudForge 1.2.2394,
macOS Apple Silicon. This is a historical target, not a native acceptance pass.
The supplied guide identifies no supporting client build.
Intel macOS is a documented distribution target, not locally tested.

## Sources

- [Client documentation](https://mudforge.org/#/docs): client operation and topic routing.
- [Authoring guide](https://mudforge.org/docs/ai-plugin-guide.md): Lua runtime,
  lifecycle, callbacks, storage, libraries, protocols, and mapper contracts.
- [Widgets and reactive binding](https://mudforge.org/#/docs/plugins): supplemental
  documentation consulted during the initial review; the supplied guide now
  documents HTML events and `data-mud-bind` contracts directly.
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

Distinguish documentation, structural inspection, injected fixture execution,
native matcher replay, and native observations. Parsing Lua or running it in a
VM does not test MudForge's JavaScript transpiler, transport, UI, or persistence.
`feedTriggers` in MudForge exercises its matcher; it does not prove transport.

## Corrected contracts

- Trigger raw `captures` starts at zero; prefer the third argument's
  `wildcards[1]` for the first group. Aliases retain full match at `[1]` and
  first group at `[2]`.
- Default variables, tables, and pseudo-files belong to the installed plugin
  and world. Only explicit `"global"` scope shares an app-wide namespace.
  Use `getPluginTable` to read another plugin's table explicitly.
- Library `math`, `string`, and `table` implementations match plugin scope;
  host APIs still require explicit injection. Global `unpack` also works in
  plugin scope.
- `importMapJson` defaults to destructive full replacement, but its third
  argument supports additive `{ merge = true }` and room replacement with
  `{ keepSettings = true }`. Do not confuse these with world-import modes.

## Known documentation ambiguities

- The skeleton and error table say top-level widget `x/y` do not position it;
  section 4's config table and examples explicitly support them when
  `position` is omitted. Prefer nested `position`/`size` for new code.
- Section 10 retains older claims about library pattern differences; section
  16 explicitly describes restored standard-library parity. Use section 16's
  contract and verify pattern-heavy ports in the target runtime.
- The warning inventory says startup global writes are lost; section 9 says
  `storageStatus("global") == "starting"` writes are buffered. For
  durability-critical global writes, wait for `"ready"` and handle `"failed"`;
  neither disputed behavior has been natively verified here.

`isActiveSession()` means foreground, not connectivity. Use connection hooks
and handle empty timer IDs. Current-style active-widget drawing is preferred;
the guide also says older widget-id forms remain callable in the shared API.

## Boundaries

This is a Codex plugin that helps develop MudForge plugins. Its ZIP is not an
`.mfp` or `.mfw` and must not be imported into MudForge. No MCP server, gameplay
agent, auto-converter, or client-source build workflow is included. Native work
uses an available authorized computer-use tool; these skills do not supply one.
