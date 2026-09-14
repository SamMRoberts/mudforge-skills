# Source ledger — 2026-09-14

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

Documented ambiguities are captured in the distributed compatibility reference:
per-world table sharing, foreground versus connected state, HTML event coverage,
and map replacement versus world-import merging.
