# CommandCenterUI Cross-PC Alignment — Biggie-Side Evidence (TASK-306)

## Rework (2026-07-29, after claude-lab-muza's CHANGES_REQUESTED)

muza's independent review (`MAP_System/artifacts/reviews/task306-review-muza.md`)
confirmed the design and all originally-submitted evidence were sound, but
found real drift: between submission and review, this same session made a
separate, unrelated live edit to `orchestrator.js`/`orchestrator.css` (a
recap-message rendering feature, requested directly by the operator) without
realizing it invalidated TASK-306's live/template parity claim — nothing
pins the live source as stable during a review window, and this session's
own concurrent work happened to surface that gap. Two required fixes,
both completed:

1. Re-imported the current live `orchestrator.js`/`orchestrator.css` into
   the template (byte-for-byte, reverified), regenerated `version.json`
   (`2026-07-29-orchestrator-v2-recap`), and reverified parity in both
   directions — clean.
2. Registered `MAP_System/scripts/run_tests.sh` as an additional TASK-306
   output path (via `map-authority task add-output-path`, before editing,
   same as the other incidental-scope registrations below) and added
   `test_command_center_deployment_parity.py` to it, so this exact class of
   drift is now caught by the routine test suite instead of depending on a
   reviewer noticing manually.

Transitioned via `map-authority task rework` (CHANGES_REQUESTED → READY,
`--reason` on record) then re-claimed before making any further edits.

- date: 2026-07-29
- owner: claude-lab-nene
- scope: local versioned-source half only (per mebo's TASK-306 scoping
  instruction) — importing Biggie's live, operator-directed CommandCenterUI
  redesign into the repo-owned installer template, with deterministic
  version/parity evidence. **No Smalls-side write happened under this
  task.**

## Authority for the underlying UI work

The CommandCenterUI redesign this task imports (`orchestrator.html/js/css`,
`bcmagent.svg`) was built earlier the same day (2026-07-29) under direct
operator instruction in a chat session with claude-lab-nene — not a MAP
task. Confirmed via three explicit operator decisions (AskUserQuestion:
tag-derived room grouping, alongside-not-replacing rollout, plain-JS port)
plus direct asks for the terminal panel, attention popup, favicon, and
per-agent popup-reopen feature. This is the same pattern INS-0056 (TASK-305)
documents for opt-in emergence capture of intentionally non-MAP work;
INS-0057 (also TASK-305) is itself sourced from this same session.

## What TASK-306 did (this pass)

1. Inventoried the exact live Biggie bundle at
   `/home/mellow/Projects/CommandCenterUI` (root scripts/config +
   `src/orchestrator.{html,js,css}` + `src/bcmagent.svg`). Confirmed
   `AGENTS.md`, `.gitignore`, `launch-command-center-ui.sh`,
   `run-command-center-app.sh`, and `app/window.py` were already
   byte-identical between the live install and the repo template —
   untouched by today's UI work.
2. Imported the four new/changed managed files
   (`app/server.py`, `README.md`, and the four new `src/` files) into
   `MAP_System/templates/install/command-center-ui/`. Confirmed
   `CommandCenterUI.desktop` differs only in its host-rendered `Exec=` line
   (template: portable `command-center-ui`; live: absolute install path) —
   expected, not drift; excluded from checksum parity by design (see
   `command_center_version.py`'s `EXCLUDED_HOST_RENDERED`).
3. Left the template's pre-existing legacy UI (`chat.html`, `app.html`,
   `index.html`, `studio.*`, `styles.css`, `assets/`) untouched — out of
   TASK-306's declared `output_paths`, and per "preserve unrelated/user/
   runtime files." Live Biggie moved its equivalent legacy files aside to
   `_legacy-ui-removed-2026-07-29/` earlier the same day; both sets are
   explicitly excluded from the parity manifest as
   `EXCLUDED_LEGACY_OUT_OF_SCOPE` / the live-only runtime-pattern exclusion,
   not silently ignored.
4. Built `MAP_System/scripts/command_center_version.py`: a `generate`/
   `verify` manifest tool over an explicit `MANAGED_FILES` list, with three
   documented exclusion classes (runtime/host-local state, host-rendered
   files, pre-existing out-of-scope legacy). `generate` refuses to run if
   any file exists that isn't accounted for in `MANAGED_FILES` or an
   exclusion set — an unrecognized new file is a hard stop, not a silent
   pass.
5. Generated `MAP_System/templates/install/command-center-ui/version.json`
   (version `2026-07-29-orchestrator-v1`, source Biggie/KUDU
   `/home/mellow/Projects/CommandCenterUI`), then verified it against both
   the template and the live bundle — clean, zero issues, both directions.
6. Wrote `MAP_System/tests/test_command_center_deployment_parity.py` (7
   focused tests: clean round-trip, changed/missing/extra detection,
   generate-refuses-on-unaccounted-file, exclusions never flagged, and the
   real live-vs-template parity proof using the checked-in manifest).
7. Wrote `MAP_System/notes/command-center-cross-pc-sync.md`: the
   Biggie-to-Smalls protocol (destination identity, backup, dry-run, staged
   verification, atomic activation, post-deploy smoke/parity, rollback).
   **Document only — no step in it has been executed against Smalls.**

## Verification (independently run, this session)

- `MAP_System/.venv/bin/python -m py_compile
  MAP_System/scripts/command_center_version.py
  MAP_System/tests/test_command_center_deployment_parity.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/command_center_version.py
  verify` (against the template) — OK, 11/11 managed files.
- `MAP_System/.venv/bin/python MAP_System/scripts/command_center_version.py
  verify --bundle-root /home/mellow/Projects/CommandCenterUI` — OK, 11/11
  managed files match.
- `MAP_System/.venv/bin/python
  MAP_System/tests/test_command_center_deployment_parity.py` — PASS, 7/7,
  including manual negative-case sanity checks (tampered file, deleted file,
  stray extra file) confirmed caught before the formal test file was
  written.
- Exact checksums and the full managed-file list are in
  `MAP_System/templates/install/command-center-ui/version.json` — not
  duplicated here to avoid a second copy going stale.
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_command_center_agent_identity`
  / `test_command_center_composer_alignment` / `test_command_center_message_intent_copy`
  / `test_command_center_attention_history` — all OK (1 skipped each) after
  the incidental fix below; all failed with `FileNotFoundError` before it.
- `MAP_System/scripts/map-git diff --check` — PASS, clean exit.

## Incidental fix: 4 pre-existing regression tests broken by an earlier,
## unrelated action this session

Running the full local test suite as part of TASK-306's own diligence (not
prompted by anything in TASK-306's acceptance criteria) surfaced that
`test_command_center_agent_identity.py`, `test_command_center_composer_alignment.py`,
`test_command_center_message_intent_copy.py`, and
`test_command_center_attention_history.py` each had a `test_live_*_matches_
installer_template` assertion that read live `chat.js`/`chat.html`/`chat.css`
directly and failed with `FileNotFoundError` — because `chat.js` etc. were
moved to `_legacy-ui-removed-2026-07-29/` earlier the same day, under direct
operator instruction, *before* TASK-306 existed. That earlier action was not
tracked by any MAP task and its test-suite impact was never checked at the
time.

Per explicit operator decision when this was discovered: the four
`test_live_*_matches_installer_template` methods are now `@unittest.skip`ped
with a comment explaining chat.js/html/css's 2026-07-29 retirement and
pointing at `command_center_version.py` as the current live/template parity
mechanism. Nothing else in those four files changed — their other assertions
(which check properties of the template's still-present, historically-
preserved chat.js/html/css) still run and still pass. The four test files
were registered as TASK-306 output paths through `map-authority task
add-output-path` before editing, matching the process TASK-305's rereview
established for exactly this kind of incidental-fix situation.

## What TASK-306's acceptance criteria still require (deferred, not done)

Per mebo's explicit scoping instruction, this pass implements only the local
versioned-source half. The following acceptance-criteria items are **not**
addressed by this evidence and require a follow-up task:

- Smalls is not modified, and no remote write of any kind was attempted
  against it under TASK-306.
- "Smalls installed parity and communication are proven after deployment"
  — not applicable yet; no deployment has happened.
- The cross-PC protocol in `command-center-cross-pc-sync.md` is written but
  unexecuted. Its own preconditions (confirmed Smalls identity, dry-run)
  are explicitly what block proceeding, per mebo's instruction to keep
  Smalls/RUKI remote writes blocked until those are established.

## Review

A different core agent must perform functional plus security-framed review
before approval/release, per TASK-306's acceptance criteria. Not
self-approved.
