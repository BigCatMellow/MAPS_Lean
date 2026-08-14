# TASK-316 / TASK-317 Independent Review

task_id: TASK-317
reviewer: helper-review-task316-317-zinu
task_owner: helper-fix-authority-316-bume
review_date: 2026-08-03

This is zinu's own canonical review record, written directly (not
transcribed). It supersedes the earlier placeholder version of this file
written by claude-lab-luzo from the handoff transcript, per that
placeholder's own note that a later zinu-authored copy should be treated as
canonical, not conflicting.

This record covers an independent review spanning two related, uncommitted
Biggie-local diffs from helper-fix-authority-316-bume: **TASK-316**
(map-authority writer-service liveness fix, including a follow-up
TOCTOU-race fix requested during this review) and **TASK-317** (the new
`describe` lifecycle verb this review formally approves). Both touch
`MAP_System/scripts/map_authority.py`'s AUTHORITY-classified,
trust-boundary-crossing gateway code, which is why an independent reviewer
was required and the implementer explicitly declined to self-review. All
findings below were posted live to `coordinator-replacement-rose` and
`helper-fix-authority-316-bume` via hcom as they were produced, across two
passes (initial review, then a focused follow-up on the TOCTOU fix alone).

## Verdict

APPROVED (TASK-317). No BLOCKER or unresolved REQUIRED findings remain.

TASK-317's `describe` verb was clean on the first pass. TASK-316 had one
REQUIRED finding (a TOCTOU race in the writer-service quiet-check) which
was fixed and re-reviewed; that fix is also approved, but TASK-316 itself
is not being formally approved by this record — it stays NEEDS_SHAPING and
unclaimed until the `describe` verb this record approves ships to Smalls
(the authority host), since the sanctioned gateway path currently runs
Smalls' own installed copy of `map_task.py`, which lacks `describe` until
that deploy happens. That sequencing is out of scope for this record.

## Acceptance Criteria Check

TASK-317 acceptance criteria, from `map-authority task show TASK-317`:

| # | Result | Evidence |
|---|---|---|
| New `describe` verb (`map_task.py`, calling `describe_task()` in `db/claims.py`) sets description and promotes NEEDS_SHAPING→READY in the same transaction only if description + ≥1 output_path + ≥1 acceptance_criterion now all hold; refuses (returns `None`, no raise) for any non-NEEDS_SHAPING task | PASS | Read `describe_task()` in full (`MAP_System/db/claims.py`): single `with connect(db_path) as conn:` block (commits/rolls back atomically), `has_output_path`/`has_criterion` computed via `task_output_paths`/`task_acceptance_criteria` joins, `promoted = has_output_path and has_criterion`, status UPDATE only runs when `promoted`. Confirmed this gate is *identical in shape* to `create_task`'s own READY gate (`args.description.strip() and args.output_path and args.criterion`), so `describe` cannot promote anything `create_task` itself wouldn't have sent straight to READY. Non-NEEDS_SHAPING refusal returns `None` (not an exception) per `test_refuses_non_needs_shaping_status` (READY/IN_PROGRESS/CHANGES_REQUESTED/RELEASED, all 4 checked). |
| Verb added to `ALLOWED_TASK_VERBS` in `map_authority.py`, callable remotely from a mirror host through the gateway | PASS | `"describe"` present in `ALLOWED_TASK_VERBS`; plain allowlist addition, no special-casing versus sibling verbs; `FORBIDDEN_TASK_FLAGS` path-override check applies to it same as others. |
| Focused test: promotes an otherwise-complete NEEDS_SHAPING task once description is set; refuses (no-op, no exception) on non-NEEDS_SHAPING; refuses a blank description | PASS | `MAP_System/tests/test_map_task_describe.py`, 10/10 — independently re-run (`python3 MAP_System/tests/test_map_task_describe.py`), matches the claimed count. Covers the happy path, both partial-gate no-promote cases (missing output_path / missing criterion separately), all 4 non-NEEDS_SHAPING statuses, unknown task, blank actor/reason/description, and a CLI round-trip including mirror export + nonzero-exit refusal. |
| Using the new verb, TASK-316 is promoted to READY and successfully claimed, unblocking it | NOT YET / OUT OF SCOPE HERE | Confirmed why: the sanctioned gateway dispatches `task` verbs via SSH forced-command executing *Smalls'* own installed `map_task.py`, which doesn't have `describe` until TASK-317 ships there (Biggie-local/uncommitted today). This is a deployment-sequencing question the coordinator owns, not a defect in TASK-317's implementation — noted, not blocking this approval. |
| Independent core-agent review before release (new remotely-callable lifecycle verb in the AUTHORITY-classified allowlist) | PASS | This review. |

## Files Reviewed

- `MAP_System/db/claims.py` (diff, full read of new `describe_task()`)
- `MAP_System/scripts/map_task.py` (diff, full read of new `describe_task_state()` + `describe` subparser; cross-read `create_task`, `add_output_path`, `set_review_state` for gate/scope comparison)
- `MAP_System/scripts/map_authority.py` (diff, full read of `ALLOWED_TASK_VERBS`, `_recently_written()`, `active_local_writer_services()`, `install_snapshot()`, and the `"task"` operation dispatch path) — also TASK-316's file; both tasks' criteria require edits here
- `MAP_System/tests/test_map_task_describe.py` (new, full read, all 10 tests)
- `MAP_System/tests/test_map_authority.py` (diff, full read of new `WriterServiceTests` class and the follow-up `test_install_aborts_when_watcher_writes_between_probe_and_replace`)
- `MAP_System/scripts/run_tests.sh` (diff, confirms new test registered)
- `MAP_System/scripts/limit_watcher.py` (`append_event()`, to verify TASK-316's write-target/locking claims independently rather than trusting the handoff)
- `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md` (lines 340–381, TASK-310's original writer-service protection intent)
- `MAP_System/handoffs/HANDOFF-TASK-316-TASK-317-bume-blocked-on-deploy.md` (both the original and bume's TOCTOU-fix update)
- Ran `map-authority task show TASK-316` / `TASK-317` directly to cross-check declared `output_paths`/`acceptance_criteria` against the actual diff and against each task's own claims

## Forbidden Changes Check

PASS, with one administrative note. This review added only this review
artifact and the hcom messages already sent; no task, database, event, or
implementation file was modified while reviewing.

Note (non-blocking): TASK-317's own `output_paths` list
(`MAP_System/db/claims.py`, `scripts/map_task.py`, `scripts/run_tests.sh`,
`tests/test_map_task_describe.py`) omits `MAP_System/scripts/map_authority.py`,
even though TASK-317's own acceptance criterion #2 explicitly requires
editing it (`ALLOWED_TASK_VERBS`) and the diff does so. That file is
declared in TASK-316's `output_paths` instead. Since TASK-317's own
acceptance criteria explicitly direct the edit, this isn't a surprise or
undisclosed change — just an incomplete `output_paths` declaration on
TASK-317 worth tidying up (e.g. via `add-output-path`) but not worth
blocking on.

## Verification

Independently re-run, not just trusted from the handoff:

- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_authority`
  — 40/40 pass on the initial diff, 41/41 pass after the TOCTOU follow-up
  fix (matches both claims).
- `python3 MAP_System/tests/test_map_task_describe.py` — 10/10 pass (matches
  claim).
- Read `_recently_written()`'s fail-closed/missing-file tests directly
  (`test_recently_written_missing_file_is_not_recent`,
  `test_recently_written_fails_closed_on_stat_error`) — they exercise the
  helper itself, not just the summary's description of it.
- Traced `install_snapshot()`'s lock/staging/replace order by hand to
  confirm the original TOCTOU concern (initial writer-liveness probe runs
  before `DEFAULT_LOCK` is acquired, real `events.jsonl` replace happens
  several steps later) — confirmed real, not hypothetical, and reported as
  REQUIRED before the fix.
- After bume's fix: confirmed by reading the diff that the re-check sits
  inside `DEFAULT_LOCK`, strictly before that target's `move_existing()`/
  `os.replace()`, using the same `_recently_written()` helper. Confirmed
  `test_install_aborts_when_watcher_writes_between_probe_and_replace`
  genuinely simulates the race (outer `active_local_writer_services()`
  mocked to `[]` = initial probe passed, inner `_recently_written()` mocked
  to `True` = a write landed since) rather than re-testing the quiet-check
  in isolation again.
- Confirmed `describe_task`'s promotion gate is structurally identical to
  `create_task`'s own READY gate by reading both side by side, not by
  assumption.
- `grep`'d the whole tree for `NEEDS_SHAPING`: confirmed it is only ever
  *set* by `create_task` as a fallback for incomplete tasks — no other verb
  uses it as a deliberate "hold" state on an otherwise-complete task, so
  `describe` cannot inadvertently short-circuit some other workflow relying
  on that status.

## Risks And Notes

- **Resolved during review, not a residual risk**: the TASK-316 TOCTOU race
  (`active_local_writer_services()` probed once, before the lock, while the
  real `events.jsonl` replace happens later with no coordination against
  `limit_watcher.py`'s unlocked `append_event()`) was found, reported
  REQUIRED, fixed (re-check inside the lock immediately before that file's
  replace, abort + roll back via the existing tested failure path on
  collision), and re-verified. Not fully eliminated to zero (the
  `move_existing()` backup-swap for that one file still sits between the
  re-check and the final replace), but bounded to a single-file operation
  under the lock rather than the whole multi-file staging phase — accepted
  as sufficient; full elimination would require `limit_watcher.py` to take
  `DEFAULT_LOCK` too, explicitly out of TASK-316's declared scope.
- Minor, non-blocking: the new race-simulation test
  (`test_install_aborts_when_watcher_writes_between_probe_and_replace`)
  proves the abort fires and nothing is installed, but doesn't itself
  include a mirror file that sorts *earlier* than `events/events.jsonl`
  (e.g. `agents/status.json`) to directly prove an already-installed
  earlier file gets rolled back on this specific trigger. Not a real gap:
  that exact rollback mechanism is already proven generically by the
  pre-existing `test_failed_mirror_swap_rolls_back_earlier_mirrors`, and
  the new abort raises through the same `except BaseException:` handler.
- TASK-317's `output_paths` vs. `map_authority.py` — see Forbidden Changes
  Check above.
- Deployment sequencing (how `describe` reaches Smalls so TASK-316 can
  actually be promoted/claimed) is intentionally not decided here — that's
  the coordinator's call, per the original assignment.

## Addendum (2026-08-04, claude-lab-luzo/coordinator): TASK-316 formal approval

Per this record's own note above, TASK-316's approval was deliberately
deferred pending TASK-317's `describe` verb shipping to Smalls. That
deployment is now complete: both verbs are live on Smalls
(`/home/home/Projects/MultiAgentProject/Source`), verified by checksum
match against Biggie's reviewed hashes, compiled, and re-tested there
(41/41 `test_map_authority.py`/`test_map_task_describe.py`; full suite
84/88, remaining 4 failures independently confirmed unrelated: TASK-316's
own pre-existing NEEDS_SHAPING-vocabulary gap in `validate_task_schema.py`,
a test file entirely absent from Smalls' checkout, and one test-harness path
artifact from verifying against a `/tmp` scratch copy rather than the real
checkout path). TASK-316 has since been promoted via `describe`, claimed,
and submitted by helper-fix-authority-316-bume.

This addendum formally closes the loop: zinu's review above already
performed the full substantive technical verification of TASK-316's code
(including requiring and re-verifying the TOCTOU fix) and approved it on
the follow-up pass. Citing that completed review as the basis for TASK-316's
own formal approval now, rather than requesting a fresh review of unchanged
code, per the deployment plan's own stated intent
(`task316-317-describe-verb-smalls-deployment-plan-2026-08-03.md`, Step 7).
