# WS-1 Command Center Consumer (Local/Template Only) — TASK-314

- author: claude-lab-mimi (implementation, template + endpoint), continued
  and completed by rotation-replacement-mimi-koda (live edit, manifest,
  restart, focused tests, submission)
- date: 2026-07-30
- authorization: DEC-040 (split from retired TASK-306), DEC-041 (operator
  approval for the live CommandCenterUI edit named below)

## What this is

The 4th and final WS-1 "Required Consumer" of the authority-freshness
contract (`ws1-truthful-authority-state.md`): the Command Center UI now
displays MAP's authority freshness (fresh/stale/unavailable/invalid),
sourced from a new read-only endpoint that calls `map-authority status` and
never writes to Smalls.

## What changed

- `app/server.py`: added `authority_status_summary()` (flattens
  `map-authority status`'s `authority` object for direct UI display; never
  blends into a single ok/warn/error aggregate, freshness stays a
  first-class four-state signal per the contract) and a new
  `GET /api/map/authority` route.
- `src/orchestrator.html`: added a `#authority-status` badge element in the
  header, next to the existing simplifier-status badge.
- `src/orchestrator.css`: added `.authority-status` styling (mono text,
  ok/warn/error color variants matching the existing badge pattern).
- `src/orchestrator.js`: polls `/api/map/authority` every 15s, sets badge
  text/class/title from the response (`fresh`/`stale`/`unavailable`, plus
  host/revision/last-sync in the tooltip); falls back to an `unavailable`
  error state if the fetch itself fails.

Both the template (`MAP_System/templates/install/command-center-ui/`) and
the live Biggie-local app (`/home/mellow/Projects/CommandCenterUI/`) were
updated identically per DEC-030 (live is authoritative, merge direction
live to template) and DEC-041's explicit approval for this named exception.

## Live edit sequence (this session, koda)

1. Verified the live CCUI files still matched mimi's pre-edit backup
   (`diff -q`, no drift since backup was taken) before touching anything.
2. Diffed backup vs. new template content: all four changed files were
   pure additions (46/4/1/31 inserted lines respectively, zero deletions or
   modifications to existing lines).
3. Copied the four template files to their live counterparts, `chmod 755`
   on `server.py`.
4. Moved the pre-edit backup
   (`.map-task314-backup-20260730T222819Z/`) out of the live bundle root
   to `/home/mellow/Projects/.map-task314-backup-20260730T222819Z/` --
   `command_center_version.py generate` refuses to run while any
   unaccounted-for file sits inside the bundle root, so the backup has to
   live outside it. Not deleted, kept for rollback per the operator's
   original instruction.
5. Regenerated `version.json` (`command_center_version.py generate`,
   version id `2026-07-30-orchestrator-v5-authority-freshness`) and
   verified template/live parity (`command_center_version.py verify`) --
   `OK: matches manifest (11 managed files)`.
6. Restarted the live server process (old PID 276733 killed; new PID
   2219603 via `run-command-center-app.sh --server-only`).
7. Smoke-checked: `GET /api/map/authority` returns a real live payload
   (`{"ok": true, "freshness": "FRESH", ...}`); the main page still returns
   200; `#authority-status` badge markup is present in the served HTML;
   the served `/orchestrator.js` and `/orchestrator.css` both contain the
   new `authority-status` code (confirming the restart picked up the new
   files, not a stale cached process).
8. `test_command_center_deployment_parity.py`: all 7 checks pass,
   including `test_live_biggie_bundle_matches_template_manifest`.

## Focused tests (fresh/stale/unavailable)

New file: `MAP_System/tests/test_command_center_authority_freshness.py`,
registered in `run_tests.sh` as `command_center_authority_freshness_test`.
Mocks `subprocess.run` (same pattern as
`test_local_ollama_lane.py::test_ui_discovery_forces_loopback_despite_ambient_host`)
so no real map-authority gateway call happens:

- `test_fresh_state_reports_ok_and_fresh_label` -- FRESH in, `ok:true`/
  `freshness_label:"fresh"` out, host/revision passed through.
- `test_stale_state_reports_ok_true_but_stale_label` -- STALE in, `ok:true`/
  `freshness_label:"stale"` out (stale is a valid signal state, not an
  error -- `ok` reflects "the call succeeded," not "the data is fresh").
- `test_unavailable_when_gateway_call_fails` -- subprocess returns nonzero,
  `ok:false`/`freshness:"UNAVAILABLE"`, `error` key present.
- `test_unavailable_when_authority_object_missing_freshness` -- malformed/
  empty authority object still degrades to `UNAVAILABLE`, not a crash.
- `test_endpoint_is_wired_to_authority_status_summary` -- confirms the
  route and the summary function are actually connected in `server.py`
  source, not just independently correct in isolation.

All 5 pass standalone and via `run_tests.sh`.

## Full suite result

`run_tests.sh`: 82 pass / 1 fail / 83 total (same as before this task's
changes) -- the one remaining failure (`validate_shared_state_tasks`) is
TASK-312/WS-3's pre-existing, independently root-caused infra limitation
(Biggie's `shared/current-state.md` mirror gets overwritten by Smalls'
~60s `map-authority-mirror.timer` before a local fix can stick; needs a
Smalls-side regeneration, unrelated to this task's Command Center scope).
No regression introduced by this task's live edit or test addition.

## Out of scope (per DEC-040)

Smalls cross-PC deployment and template/live parity verification *on
Smalls* are explicitly deferred to a separate WS-6 task, gated by its own
operator/security/rollback approval. This task's live edit was Biggie-local
only, per DEC-041.

## Review

Needs independent core-agent review before approval, per this task's own
acceptance criteria and DEC-038's review-independence rule (reviewer must
be outside the claude-lab-mimi / rotation-replacement-mimi-koda lineage,
same constraint TASK-310 is under).
