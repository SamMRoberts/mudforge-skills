# Formats and migration

Sources: [world files](https://mudforge.org/#/docs/world-files),
[packages](https://mudforge.org/#/docs/packages),
[import/export](https://mudforge.org/#/docs/import-export), and
[authoring guide](https://mudforge.org/docs/ai-plugin-guide.md).
Reviewed 2026-09-14.

`.mfw` is a ZIP world snapshot. `.mfw.json` is a supported legacy JSON import.
`.mfp` is a ZIP content package with `package.json` and no `world.json`.
The public overview does not specify a complete legacy JSON schema or all
manifest fields. The inspector checks the documented container envelope and
flags legacy/unknown schema as unsupported; it is not MudForge's import validator.

Worlds can include connection details, automation, variables, plugins and saved
state, layout, maps, sounds, and optional command history. Keep originals and
backups private. Use redacted, synthetic fixtures for shared tests.

World import previews contents and offers Replace, Merge, and Skip-if-existing
modes. Map import backup behavior documented for that UI must be verified for
the installed version. It does not make `importMapJson` a merge operation.

Packages target the active world. The docs describe ownership tagging, preserved
user items on ID collision, additive map rooms, settings rollback, and layout
replacement with restore on uninstall. A package cannot contain connection
settings. Verify checksum, content preview, minimum-client requirements, and
Lua/network permissions using the client. The inspector cannot prove all of
these semantics. Do not bypass the package consent flow.

## Assisted migration record

For each source feature record source identifier, observable behavior, target
implementation/import path, dependencies, outcome, and evidence or blocking gap.
Use stable source references; avoid embedding private capture text in reports.
Separate planned work (manual port required) from completed outcomes (manually
ported). Never use a completed outcome merely because a target approach exists.

- MUSHclient compatibility covers selected calls; inspect the documented function
  before relying on parity. Miniwindows, filesystem operations, and regex capture
  conventions need explicit review.
- Compare regex dialect, flags, anchoring, Unicode/case behavior, capture numbering,
  and unsupported constructs against representative source inputs. A regex-mode
  toggle alone cannot preserve source semantics.
- Record whether each timer must run while disconnected. MudForge `addTimer`
  refuses creation in that state; an offline source timer remains a gap until a
  documented equivalent is implemented and tested.
- Mudlet automation/map compatibility aliases are partial. Geyser widgets need a
  MudForge widget implementation; Lua modules may need injected APIs and flat
  names. Mapper calls have argument-order, area, and array differences.
- Supported import formats in a given build should be confirmed in the visible
  import dialog. Do not promise a general XML or mpackage importer from API aliases.
- Count accepted, blocked, and unverified features independently. A successfully
  opened file is not evidence that its behavior was preserved.
