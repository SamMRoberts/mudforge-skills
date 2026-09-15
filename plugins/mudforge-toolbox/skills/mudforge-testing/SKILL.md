---
name: mudforge-testing
description: Validate MudForge artifacts and Lua examples, reproduce client integration failures, and run disposable macOS acceptance with separate offline and native evidence.
---

# Testing and acceptance

Define the changed observable behavior and its acceptance boundary. Read
[acceptance](references/acceptance.md), then run the narrowest relevant checks.
Use `python3 <plugin-root>/scripts/inspect_artifact.py <artifact>` for safe
container inspection and `python3 <plugin-root>/scripts/validate_plugin.py
<plugin-root>` for this Codex bundle (requires the declared PyYAML dependency).

When testing a Lua feature, preserve the failing input and reproduce the bug
before changing it where practical. Inject the documented API boundary to test
logic. Separate that result from the JavaScript matcher/transpiler and native
rendering/transport/persistence. Do not weaken assertions to accommodate a bug.

Use native fixtures only in an identified disposable world. A public MUD or
existing user world is not a substitute when isolation is unavailable. If native
access is blocked, finish unaffected checks and record the tool denial and exact
untested behaviors.

Report test command, version, fixture, outcome, and evidence. For failures give
reproduction steps and expected/actual behavior. Mark native acceptance complete
only after cleanup and preservation checks pass. No automatic installation,
publishing, or gameplay follows from validation.
