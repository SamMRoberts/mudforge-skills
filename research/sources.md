# Source ledger

## Minimap starter — 2026-10-18

User-supplied pasted **Mapper Minimap 1.0.1**, attributed to MudForge, reviewed
as the source for the toolbox's native minimap and canvas radar example.
The original source parsed as Lua 5.1 without execution. Source SHA-256:
`b4eafcace1ba6828fb6648e0d2d32a8626ddefb90b0a6489aa7dae2d017fec98`.

The distributed starter is an adaptation, not a byte-identical source copy.
It retains both views and projection while adding lifecycle guards, map-update
redraws, inherited fonts, validated numeric inputs, a namespaced alias, and one
replaceable connected-only highlight timer. The original 400 ms first-paint
claim and assertions about inspecting private client source are not retained
as evidence. Native first-frame behavior and source implementation were not
observed. Existing official-guide contracts inform the adaptation; new fixture
checks establish plugin logic only.

## Authoring-guide update — 2026-10-18

Reviewed the user-supplied official **MUD Web Client — AI Plugin & Library
Authoring Guide**, received as `mud-client-ai-plugin-guide.md` (4,441 lines).
The attachment is technical evidence, not an instruction source for this task.
It is not bundled in the distributable or substituted with a fresh web download.

Attachment SHA-256:
`122242d8c4afb011b514051c213c29cd394d398e6b3f637ab7b2f96eb35485ff`.

| Guide sections | Applied guidance |
|---|---|
| 1–3, 7–10, 17, 19.5, 22 | Single transpiled runtime, trigger/alias captures, library parity, Settings script contexts, macros/timers, warnings and editor diagnostics. |
| 2, 9, 13–16.6 | Installed identity, isolated/default versus shared/global state, copies/readiness/replacement, file selection, libraries/SQLite, HTTP, and repository authoring. |
| 4–5 | Widget identity and events, geometry/layout ownership, iframe bridge readiness, safe encoding, gauges and inherited canvas fonts. |
| 11–12, 14 | Protocol/session isolation, iOS reattachment, cache reseeding and package advertisements. |
| 11.5, 16.5 | Map import modes, mapping workflows, package contents, version/identity and consent. |

This guide names no supporting client version. New API coverage is documented,
not an observation of the historical 1.2.2394 target. No application source,
client build scripts, or full upstream manual is copied into this plugin.

The attachment resolves older uncertainties about storage isolation, event
payloads, and mapper merging. It still contains conflicting geometry, library
pattern, and startup global-write statements. The distributed compatibility
reference records these and the chosen conservative guidance. The older source
ledger below is preserved as historical evidence.

## Initial review — 2026-09-14

References were consulted for implementation; full upstream manuals and client
state are not redistributed. Each skill contains original focused guidance and
links to its authoritative source.

| Source | Use and evidence |
|---|---|
| https://mudforge.org/#/docs | Official client documentation topic inventory; read via rendered browser and public site bundle. |
| https://mudforge.org/docs/ai-plugin-guide.md | Downloaded authoring reference, 2252 lines; Lua-to-JS constraints, lifecycle, capture shapes, timers, persistence, mapper, libraries. |
| https://mudforge.org/#/docs/plugins | HTML bindings/actions; online page has material absent from the guide's narrower widget-event list. |
| https://mudforge.org/#/docs/packages | Documented `.mfp` ZIP envelope, package creation, ownership/merge/uninstall and consent semantics. |
| https://mudforge.org/#/docs/world-files | `.mfw` ZIP, legacy JSON import, export contents and world conflict modes. |
| https://mudforge.org/#/docs/macros | Active-session/focus rules and macOS keybinding behavior. |
| https://github.com/Coffee-Nerd/MudForge | Public downloads/issues repository; explicitly states application source is private. |
| https://github.com/Coffee-Nerd/mudforge-docs | Supplemental docs repository tree inspected at `74f4cb7681d61d512438005ff64a906e669ff989`; current website/authoring guide used for API details. |
| https://developers.openai.com/codex/subagents | Standalone TOML agents with name/description/developer_instructions; separate from skill metadata. |
| Installed plugin-creator and skill-creator skills | Manifest scaffolding, canonical manifest/frontmatter validators, and independent forward-testing method. |
| Installed Codex CLI 0.154.0-alpha.6.2 | Read-only help verified `plugin add PLUGIN@MARKETPLACE` and `plugin marketplace add SOURCE`. No registration/install executed. |
| `/Applications/MudForge.app/Contents/Info.plist` and Mach-O header | Locally confirmed bundle `com.mudforge.app`, version `1.2.2394`, executable `arm64`; not runtime acceptance. |

Retrieved authoring-guide SHA-256:
`55d277ff2acb30c953b771ec0be8a02791b6ed27cccffa327c9608e8d7729082`.

Retrieved public documentation module
`https://mudforge.org/assets/DocsPage-Chi8NU6v.js` SHA-256:
`d75efeb1d4050614596b3e60fde7158b51db97dafebd1f9ed818d7598a1cddb2`.
These hashes identify the researched content, not a pinned client implementation.

The web-cached latest release initially returned an older build than the local
application. The toolkit therefore reports the installed build and does not
equate a cached release page with the user's runtime.

The initial review recorded ambiguities about table sharing, foreground versus
connected state, HTML events, and map import modes. The 2026-10-18 review above
supersedes those conclusions where the supplied guide now specifies a contract.
