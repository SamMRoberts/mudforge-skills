# Formats and migration

Sources: [world files](https://mudforge.org/#/docs/world-files),
[packages](https://mudforge.org/#/docs/packages),
[import/export](https://mudforge.org/#/docs/import-export), and
[authoring guide](https://mudforge.org/docs/ai-plugin-guide.md).
World-file documentation reviewed 2026-09-14; supplied official authoring guide
reviewed 2026-10-18 (§§7–9, 11.5, 15.5, 16.5).

`.mfw` is a ZIP world snapshot. `.mfw.json` is a supported legacy JSON import.
`.mfp` is a ZIP content package with `package.json` and no `world.json`.
The public overview does not specify a complete legacy JSON schema.
The inspector checks the documented container envelope and
flags legacy/unknown schema as unsupported; it is not MudForge's import validator.

Worlds can include connection details, automation, variables, plugins and saved
state, layout, maps, sounds, and optional command history. Keep originals and
backups private. Use redacted, synthetic fixtures for shared tests.

World import previews contents and offers Replace, Merge, and Skip-if-existing
modes. Verify map import backup behavior in the installed version. Mapper API
import is a separate interface: `importMapJson(json, callback?, options?)`
defaults to replacing the whole map including settings. `{ merge = true }`
preserves existing positions, exits, notes, settings, labels and visit counts,
adding absent rooms/exits/notes and filling empty fields. New rooms are laid
out relative to the existing map, ignoring their imported coordinates.
`{ keepSettings = true }` replaces rooms while preserving settings/labels/extras.
Choose one intended mode explicitly and inspect callback results/conflicts;
never describe the default call as a merge. Export/reimport should preserve
labels, flag definitions, environment colors, and area/map user data as well
as rooms. Highlights are ephemeral and need reapplying after reload.

Packages target the active world. The docs describe ownership tagging, preserved
user items on ID collision, additive map rooms, settings rollback, and layout
replacement with restore on uninstall. A package cannot contain connection
settings. Verify checksum, content preview, minimum-client requirements, and
Lua/network permissions using the client. The inspector cannot prove all of
these semantics. Do not bypass the package consent flow.

## Server package authoring

`package.json` has `formatVersion: 1`, `packageId`, `name`, `version`, and
`contents[]`; optional fields include `plugins[]`, `libs[]`, `applyTheme`, and
`minClientVersion`. This is a documented authoring contract, not a full schema
validator implemented by the inspector. Use the client's Create Package UI to
produce the bundle, hash, and GMCP `Client.Package` advertisement.

- The advertisement needs an HTTPS `url` and `version`; keep that version equal
  to the manifest version. Keep `packageId` stable for updates. Recognition uses
  advertised name, URL and manifest ID; changing identity can orphan installs.
- The bundle may include automation, plugin source/manifests, `libs/<name>.lua`,
  maps, themes, layout, whitelisted settings and images. It cannot contain
  `world.json` or connection data. Create Package excludes content already
  owned by another package.
- User item collisions are renamed rather than overwritten; package items carry
  `__pkg` ownership. Maps add rooms without modifying existing ones. Uninstall
  removes tagged items and restores recorded settings/layout state; verify the
  relevant user content survives install, update and uninstall.
- Libraries installed as files take precedence over package copies. Identical
  libraries from multiple packages share an entry until the last owner leaves;
  different sources under the same name are refused. Package libraries persist
  per world and re-register when it opens.
- Settings → Packages → Import Package runs local `.mfp` files through the normal
  consent and lifecycle path without hosting. With no advertised checksum, local
  files are unverified and Lua needs the extra opt-in. A server's `required` hint
  does not bypass consent, and package installation never grants HTTP permission.

For distribution of individual plugins or libraries rather than a server bundle,
use the plugin-development skill's repository publishing guidance. A Codex
toolbox ZIP, `.mfp`, world snapshot, and plugin repository are different artifacts.

## Assisted migration record

For each source feature record source identifier, observable behavior, target
implementation/import path, dependencies, outcome, and evidence or blocking gap.
Use stable source references; avoid embedding private capture text in reports.
Separate planned work (manual port required) from completed outcomes (manually
ported). Never use a completed outcome merely because a target approach exists.

- MUSHclient compatibility covers selected calls; inspect the documented function
  before relying on parity. Settings Script items and Ctrl+I share a world script
  context and world variables; a plugin has its own variables and globals.
  Imported `script="Func"` callbacks must be defined in the world script context,
  not in a plugin. Miniwindows, filesystem operations, and regex capture
  conventions need explicit review.
- Compare regex dialect, flags, anchoring, Unicode/case behavior, capture numbering,
  and unsupported constructs against representative source inputs. A regex-mode
  toggle alone cannot preserve source semantics.
  Imported PCRE-compatible patterns get selected translations (including scoped
  flags); unsupported forms such as atomic groups, possessive quantifiers and
  extended mode are diagnosed rather than silently converted. Keep exact fixture
  inputs. Raw plugin trigger captures count from zero; prefer `wildcards[1]` for
  the first group. Alias callbacks instead put the full match at `matches[1]`.
- Record whether each timer must run while disconnected. MudForge `addTimer`
  refuses creation in that state, but imported Settings timers can retain
  `active when closed`. Preserve fractional intervals, time-of-day, offsets,
  destinations and one-shot semantics where supported. Imported Script timers
  use the world script context; imported `script="Func"` calls `Func(name)`.
  Do not label an offline timer unsupported before checking that native path.
- Mudlet automation/map compatibility aliases are partial. Geyser widgets need a
  MudForge widget implementation; Lua modules may need injected APIs and flat
  names. Mapper calls have argument-order, area, and array differences.
- Supported import formats in a given build should be confirmed in the visible
  import dialog. Do not promise a general XML or mpackage importer from API aliases.
- Count accepted, blocked, and unverified features independently. A successfully
  opened file is not evidence that its behavior was preserved.
