---
name: mudforge-macos
description: Configure and diagnose the MudForge desktop client on macOS, including installation discovery, connections, sessions, storage, and backups.
---

# MudForge on macOS

Start with [compatibility](../../references/compatibility.md), then run
`python3 <plugin-root>/scripts/diagnose_macos.py` for a read-only installation
summary. Accept an explicit `--app` path for a nonstandard installation. This
helper reads bundle metadata and checks storage locations; it does not read
worlds, credentials, logs, or database contents.

Identify the selected world/session and exact symptom before changing settings.
For setup, use the client's connection dialog and the user's host, port, and TLS
choice. Do not infer credentials or connect to a sample public MUD. For display
issues, check terminal/theme settings and widget layout separately from transport.
For connectivity, distinguish DNS/TLS failures, disconnects, and missing protocol
data using the actual error and a minimal redacted log excerpt.

Use [native operations](references/native-operations.md) for backup, test-world
isolation, and troubleshooting. Prefer existing authorized UI tools and native
menus; web documentation's Ctrl shortcuts may not match every macOS binding.
Do not claim that a browser smoke test validates the installed native client.

Report version/architecture, affected world, observed failure, change, and what
was verified. If UI access is denied, complete read-only diagnostics and report
the missing native check without trying an alternate UI-control mechanism.
