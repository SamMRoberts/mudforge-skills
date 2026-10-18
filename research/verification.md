# Verification history

## 0.1.2 minimap starter — 2026-10-18

Added the supplied example as an adapted native minimap/custom canvas radar
starter, with a focused authoring reference. Source provenance and hash are
recorded in the source ledger. No native application actions were performed.

Commands used the existing development environment at
`/Users/samroberts/Repo/SamMRoberts/mudforge-skills/.venv/bin/python`.

- `python -m unittest discover -s tests -p test_examples.py -v`: **23 passed**,
  including nine new minimap tests and Lua 5.1 parsing of all ten examples.
  New fixtures cover cold/duplicate readiness and setup, native embedding
  refusal with radar fallback, missing/unmapped locations, malformed numeric
  records, string-key neighborhoods, same-floor filtering, south-positive
  projection, clipping, player-last drawing, map-update/resize redraws,
  inherited fonts, live forced visibility, timer/highlight refusal,
  disconnected clicks, replacement/expiry, and disconnect/cleanup behavior.
  Captured callbacks after cleanup remain inert. These are injected logic
  checks, not a native renderer or transpiler emulator.
- `python -m unittest discover -s tests -v`: **44 passed**, retaining the
  existing helper, artifact safety, reproducible build, and extracted-bundle
  relocation coverage.
- Bundle validation accepted the manifest, eight skills, three agent TOMLs,
  and local links. The installed skill-creator validator accepted all eight
  skills. `git diff --check` passed.
- Independent read-only review compared the starter, notes, and tests against
  both supplied sources; no actionable findings were reported. The reviewer
  also ran the 23 example tests successfully.

Fetched `origin` and verified its primary branch at `5668767`. The previous
worktree base already had identical files. Created the fresh branch
`codex/add-native-minimap-starter` from `origin/main`; before/after hashes
confirmed preservation of tracked edits and both new files. No existing branch
was deleted or rewritten, and no commits or pushes were made for this update.

`python plugins/mudforge-toolbox/scripts/build_plugin.py --output dist/mudforge-toolbox.zip`
built version **0.1.2** with **52 files**, including the new starter and notes.
The archive names/bytes matched source, ZIP integrity passed, its checksum
matched, and a second temporary build produced identical ZIP bytes.

SHA-256: `51bc143e36d373444e9469922e74b052605c5621c035e9f125896bdb748d2ca3`.

Native first-frame rendering, mapper/transpiler behavior, docking/resize,
font changes, embedded room clicks, saved visibility/reopen, reload cleanup,
and two-world isolation remain **pending**. No installation or publication
occurred. The example notes describe the disposable native acceptance checks.

## 0.1.1 regression reproduction — 2026-10-18

Before the example fixes, the corrected Lua fixtures reproduced four failures:
the existing single-group trigger test no longer saved its first capture, an
unequal-group callback saved the second raw capture instead of the first
wildcard, missing/unrelated widget actions cleared the HUD, and the canvas
overrode the widget font. The unchanged baseline had passed all 32 tests and
bundle validation; its old trigger fixture supplied an incorrect one-based raw
capture array.

The previous report below remains historical. Its independent forward-check
item 1 endorsed raw capture `[1]`; the supplied guide and corrected regression
supersede that conclusion. Current guidance uses the third callback argument's
`wildcards[1]`. No native matcher or application acceptance was run for this
update.

An additional regression injected the documented blank-string-to-zero numeric
conversion at the API boundary. Both vitals examples initially treated blank
health as zero; explicit blank/whitespace rejection now keeps it unknown. This
is a narrow injected behavior check, not an emulation of the transpiler.

## 0.1.1 offline verification — 2026-10-18

Commands used Python 3.14.8 from the existing development environment at
`/Users/samroberts/Repo/SamMRoberts/mudforge-skills/.venv/bin/python`, with
PyYAML 6.0.3 and Lupa 2.6's Lua 5.1 module. No dependencies were changed.

- `python -m unittest discover -s tests -p test_examples.py -v`: **14 passed**.
  Covers corrected zero-based raw captures versus one-based wildcards,
  unequal-group regression, unchanged alias indexing, validated reset actions,
  inherited canvas fonts across redraw, blank numeric rejection, and the
  existing lifecycle, partial-data, isolation, and map-preservation checks.
- `python -m unittest discover -s tests -v`: **35 passed**. This includes
  deterministic build bytes, extracted-bundle relocation, and helper behavior.
- `python plugins/mudforge-toolbox/scripts/validate_plugin.py`: accepted
  manifest, all eight skills, three agent TOMLs, and local reference links.
- The installed skill-creator `scripts/quick_validate.py` accepted all eight
  skill folders. `git diff --check` passed.

Independent agents received realistic authoring/migration requests and the
revised skills without the intended answers. Their read-only outputs correctly
distinguished imported Settings timers from plugin timers, preserved package
identity and consent, used widget ready handshakes and inherited canvas fonts,
and chose explicit map merge behavior. Follow-up clarified the acceptance
table's timer wording and linked map backup preparation to native export.
The runtime scenario identified missing explicit JSON encode/decode call
guidance; that gap is addressed in the focused HTTP reference. Character IDs
and trigger-only recovery remain server-specific inputs, not invented APIs.

Native transpilation/matching, UI, persistence, HTTP permission handling,
imports/exports, and iOS reattachment remain **pending**. No native app actions,
installation, publication, commits, or pushes were performed for this update.

## 0.1.1 built artifact — 2026-10-18

`python plugins/mudforge-toolbox/scripts/build_plugin.py --output dist/mudforge-toolbox.zip`
built the final bundle. A second temporary build produced identical ZIP bytes.
Archive integrity passed, and all **50 files** matched the distributable source
names and bytes. The ZIP contains version 0.1.1, eight skills, and three agent
definitions; research and tests are excluded. The adjacent checksum matched.

SHA-256: `7707c40da16f6fc4aa06ee7715c79c038de5dcfb8c2054bb3ccbd788bbdd7f35`.

## Initial verification — 2026-09-14

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
