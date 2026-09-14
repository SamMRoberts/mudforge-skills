# Verification — 2026-09-14

## Executed offline checks

- `.venv/bin/python -m unittest discover -s tests -v`: **32 tests passed**.
  Covers artifact envelopes, malformed JSON/ZIP, duplicate/traversal/colliding
  paths, CRC failures, size/ratio limits, symlinks, redacted reports, source
  preservation, activation dry-run/conflicts/rollback, bundle reproducibility,
  extracted-bundle relocation, and bundle metadata/reference validation.
- Nine Lua files parse as Lua 5.1 through `lupa.lua51`; behavioral fixtures check
  trigger/alias capture differences, repeated init/cleanup, timer refusal and
  cancellation, serialized counter reload, injected library isolation, partial
  GMCP/MSDP and session isolation, widget binding boundaries, canvas reflow,
  unknown/zero maxima, and map-conflict refusal.
- Loopback test opens a real local TCP peer, negotiates GMCP/MSDP, and checks
  partial payload output. This verifies the fixture server, not native MudForge.
- The installed plugin-creator validator accepted the manifest. The installed
  skill-creator quick validator accepted all eight skills.
- Read-only macOS diagnostic confirmed installed MudForge 1.2.2394, arm64, and
  presence of the candidate storage locations without reading saved values.
- Codex CLI help confirmed the documented user-run installation command shapes.

## Independent forward checks

A separate evaluator received realistic requests and only the skills/raw
artifacts, without the expected answer or test conclusions:

1. Corrected a `%d`/capture-index trigger to explicit JS regex, capture `[1]`,
   and an implicit nil return preserving output. Native matching was not claimed.
2. Assessed a MUSHclient trigger, repeating timer, Miniwindow HUD, shell
   dependency, and map. Retained every feature and identified unsupported shell
   behavior and unverified import paths instead of dropping them.
3. Reviewed the counter plugin against persistent state and duplicate-init
   requirements. No defect found for the documented full-runtime reload model.
4. Traced partial HP updates and hostile labels. Found that zero maximum retained
   a misleading valid label; implementation now rejects nonpositive maxima and
   binds readiness separately. A focused regression checks recovery to valid data.
5. Created a synthetic traversal `.mfp` in a private temporary directory and ran
   the inspector: exit 1, `unsafe archive member path`, unchanged source checksum,
   and no extraction. This also exposed rejection of macOS `/var` parent aliases;
   the inspector now resolves parent aliases while refusing a symlinked source file.

The evaluator suggested explicit source-regex parity and disconnected-timer
criteria for migration. Both were added to the migration reference.
The focused follow-up confirmed the HUD sequence now ends at `10 / ?`, 0%,
Waiting for valid vitals, and repeated the `/var/folders` traversal fixture
successfully. No native rendering claim was made.

## Release artifact

`dist/mudforge-toolbox.zip`: 44 files. The final archive member names and bytes
were compared against the distributable source; all matched. ZIP integrity and
text-whitespace checks passed. The checksum is also written alongside the ZIP.

SHA-256: `a80606c23b3e86273ce2b123e56f71120006268034d4dad56b2f30fdc10f28ca`.

## Native acceptance: blocked

The native Computer Use request for `com.mudforge.app` returned:
**“Computer Use was not approved to use MudForge.”** No alternate UI-control
mechanism was used to bypass the denial.

No test content was imported and no world/map mutations were performed. Since
native writes did not proceed, no backup/import/cleanup sequence or before/after
world-map preservation comparison was performed. File presence and application
metadata checks are not substitutes for those observations.

Pending: actual transpilation/load, trigger and alias dispatch, connected timers,
GMCP/MSDP delivery, HTML/canvas rendering and keyboard interaction, widget array
bridging, runtime cleanup, save/reopen persistence, world/package import/export
round trips, uninstall restoration, and existing-world/map preservation checks.
Intel macOS is untested. Codex installation/agent discovery in a fresh task was
not performed; activation was verified only in disposable filesystem projects.

To resume, enable authorized native Computer Use access, back up relevant state,
create the disposable world, and follow the bundled native acceptance procedure
with the repository's loopback fixture. No public MUD connection is needed.
