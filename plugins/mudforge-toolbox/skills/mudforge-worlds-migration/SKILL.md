---
name: mudforge-worlds-migration
description: Inspect MudForge world and package exports, plan safe imports and backups, and assist Mudlet or MUSHclient migration with explicit feature-level outcomes.
---

# Worlds and assisted migration

Use [formats and migration](references/formats.md). Start with read-only
inspection: `python3 <plugin-root>/scripts/inspect_artifact.py <artifact>`.
The report deliberately contains counts and structural diagnostics, not saved
values or archive filenames that might contain private information. It never
loads Lua. Unsupported schema means inspection is incomplete, not a valid file.

For backup/import, identify source and target worlds, preview selected content,
and preserve a verified export including maps/plugins. World import defaults
to Replace in the documentation; choose the user's intended conflict mode
explicitly. Do not infer merge behavior from the extension alone.

For migration, inventory triggers, aliases, timers, macros, scripts, widgets,
libraries, maps, and external dependencies. Use supported native imports where
available, then port behavior through explicit adapters. Retain each feature's
outcome: imported, manually ported, unsupported, or requiring native verification.
Preserve source originals and report partial failures; never discard a timer or
UI feature merely to make conversion appear complete.

For distributing `.mfp`, prefer Settings → Packages → Create Package in the
target client. Inspect the resulting bundle, then test install/update/uninstall
in a disposable world. Do not hand-build undocumented container structures.
