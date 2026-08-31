# PR #206 — SEC/6.24 test-hardening + docstring drift follow-up to #204 — independent review evidence

reviewer: maps-lean-rev-fone
head_sha: 228da0aa5c654f923e072a63835e77eef2051142
independent: true
verdict: APPROVE
summary: TEST + PROSE only. `git diff origin/main...HEAD -- runtime/` touches exactly one file (`runtime/recovery/production.py`) and every changed line is inside a docstring — the module docstring (L76-92) and the `RunBoundValidator` class docstring (L200-210). Zero executable-line change confirmed. The L79 change is a minimal factual correction: it deletes the now-false "zero production writers" bullet, notes `flow_start` step 4 is a writer as of #204, restates the pre-existing `validation_repo_root` gate, and points to project memory `env-evidence-writer-authority-redecision` for the re-decision — explicitly "no gate here changes until it lands." It does NOT make the authority decision or move any gate. GAP 1 (`allow_older_task_revision` uncovered) and GAP 2 (negative-age / `produced_at_in_future` uncovered) both closed with tests on the correct paths; GAP 2 covered on BOTH the recorded and caller-supplied-JSON paths. Full targeted glob green (131 tests), `runtime.smoke` exit 0. 6 mutants run: gina's 3 surviving mutants (M4/M5/M6) now KILLED, plus 3 more against the new assertions KILLED. No checklist change (no status move — matches dispatch). Not the author (author = maps-lean-laze).

## Method

Reviewer's own detached worktree at PR #206 head `c9eb7b43d117c08149e3e3e91312c591df13af30`; `git fetch origin main` first. `git merge-base HEAD origin/main` = `e7d93ca` = `origin/main` tip → no rebase needed. `git status` clean, no staged reverts. A second detached worktree (`MAPS_Lean_mut206`) at the same head was used for mutation testing so it could not disturb the glob run.

Sources of truth:
- gina's second-pass GAP 1 / GAP 2 definitions (relayed via niko dispatch #75617).
- `work/notes/2026-08-31-environment-report-production-source-cache-design.md` (#204 design note) — freshness semantics: "environment_spec_hash == spec.sha256, age <= max_age_seconds, task-revision match unless allow_older_task_revision, project boundary".
- `reference_committee_review`.

Files read at HEAD: `runtime/recovery/production.py` (full docstrings L45-92, L190-219), `runtime/routing/environment_reports.py` (`_freshness_diagnostic` L85-113, both callers L150-170 and L225-273), `tests/test_routing_environment_reports.py` (full diff + helpers).

## CORE CHECK — "zero runtime logic change" claim is TRUE

`git diff origin/main...HEAD --stat`:
```
 runtime/recovery/production.py            |  29 +++++---
 tests/test_routing_environment_reports.py | 118 +++++++++++++++++++++++++++++-
 2 files changed, 135 insertions(+), 12 deletions(-)
```

`git diff origin/main...HEAD -- runtime/` — every hunk is inside a triple-quoted docstring:
- **Module docstring (L76-92)**: deletes the bullet "the table has zero production writers today, so nothing executes at all" and the paragraph that rested on it; replaces with (a) a restatement of the existing "`validation_repo_root` must still be explicitly passed" gate, and (b) a new paragraph noting `flow_start` step 4 (#204) is now a production writer, that this fires the re-decision the note itself calls for, that the re-decision is a separate open design task tracked in project memory `env-evidence-writer-authority-redecision`, and "**no gate here changes until it lands.**"
- **`RunBoundValidator` class docstring (L200-210)**: replaces "Since `record_run_environment_evidence` currently has zero production writers, that is the answer every real incident gets today; this wiring is deliberately inert…" with an accurate description — `flow_start` step 4 writes a row for any task carrying an environment contract, so incidents on such runs can now get a bound spec; an incident on a run whose task had no environment contract still gets `no_spec_bound`.

The first hunk's context line immediately after the changed block is the closing `"""` followed by `from __future__ import annotations` — i.e. the change is entirely within the docstring string literal. No `def`, no branch, no assignment, no import touched. **The claim holds.**

### L79 change is a minimal factual correction, not an authority decision — PASS

The new paragraph does not answer "who may write those rows" or "whether their `validation.quick` should run unattended" — it explicitly defers both to the separate design task and states no gate changes until that lands. It is consistent with open PR #207 (the design note that resolves the re-decision, concluding "security posture did NOT regress, no runtime change required"). No `PolicyDecision`, no gate constant, no executable guard is touched anywhere in the diff.

Non-blocking observation: once PR #207 merges, the phrase "a separate open design task" in this docstring will be stale (the task will be resolved, not open). A one-line follow-up, not a defect in #206.

## GAP closure

### GAP 1 — `allow_older_task_revision` was a wired operator knob with zero coverage — CLOSED

`runtime/routing/environment_reports.py:249` `allow_older = bool(contract.get("allow_older_task_revision"))` → passed to `_freshness_diagnostic(..., allow_older_task_revision=allow_older)` at L266 (recorded path only; the caller-supplied path L170 hardcodes `False`, matching the design — GAP 1 is a recorded-path gap). `_freshness_diagnostic` L106: `if recorded_task_revision != current_task_revision and not allow_older_task_revision: return "task_revision_mismatch"`.

New tests (recorded path):
- `test_recorded_report_at_older_revision_dropped_when_flag_absent` — `_contracted_task()` (flag defaults False), record, `_bump_task_revision` (mutates `tasks.outcome` so `compute_task_revision()` advances while the recorded evidence keeps the older revision), assert `reports == {}` and diagnostic `task_revision_mismatch`.
- `test_recorded_report_at_older_revision_accepted_when_flag_set` — `_contracted_task(allow_older_task_revision=True)`, same bump, assert diagnostic `fresh` and the report projected (`state.value == "COMPATIBLE"`).

Mirror pair present (absent/False → dropped; True → accepted). `_bump_task_revision` asserts the revision actually changed, so the test cannot silently no-op.

### GAP 2 — future-dated report (negative age) never asserted-dropped — CLOSED

`_freshness_diagnostic` L108-110: `age = (now - produced_at).total_seconds(); if age < 0: return "produced_at_in_future"`. Shared by both selectors.

New tests:
- Caller-supplied path: `test_future_dated_report_is_omitted_not_read_as_fresh` — envelope `produced_at = now + 60s`, assert `reports == {}`, diagnostic `produced_at_in_future`.
- Recorded path: `test_recorded_report_dated_in_the_future_is_dropped` — record "now", evaluate freshness at `now=datetime(2000,1,1)` (strictly before the write), assert `reports == {}`, diagnostic `produced_at_in_future`.

Both paths, exact-string assertions, `reports == {}` (never read as fresh). Prior "future" coverage advanced `now` forward (positive age → `report_stale`) and never exercised the negative branch — confirmed against `test_stale_recorded_report_is_dropped_not_converted` / `test_stale_report_is_omitted_not_converted_to_incompatible`.

### kimi's optional finding — direct recorded-path `spec_hash_mismatch` — ADDED

`test_recorded_report_spec_hash_mismatch_is_dropped` — inserts a `run_environment_evidence` row directly (bypassing the recorder's own fail-close) whose `environment_spec_hash` disagrees with the contract's spec, asserts `reports == {}`, diagnostic `spec_hash_mismatch`.

## Mutation testing

Run against `tests.test_routing_environment_reports` (16 tests) in the isolated `MAPS_Lean_mut206` worktree; each mutant applied to `runtime/routing/environment_reports.py`, module restored between runs.

| # | Mutation | Target | Result |
|---|----------|--------|--------|
| M6 | drop `and not allow_older_task_revision` from the revision guard (gina's M6 — force revision check to always fire) | GAP 1 | **KILLED** |
| M9 | `and not allow_older_task_revision` → `and allow_older_task_revision` (invert the knob) | GAP 1 new assertions | **KILLED** |
| M4 | `if age < 0:` → `if age < -1e9:` (negative-age check never fires; gina's M4) | GAP 2 | **KILLED** |
| M5 | `return "produced_at_in_future"` → `return "fresh"` (gina's M5) | GAP 2 | **KILLED** |
| M7 | `return "task_revision_mismatch"` → `return "spec_hash_mismatch"` | GAP 1 new assertions (exact token) | **KILLED** |
| M8 | `return "produced_at_in_future"` → `return "report_stale"` | GAP 2 new assertions (exact token) | **KILLED** |

6/6 killed. gina's 3 survivors behind #204 (M4/M5/M6) are now killed by the new tests; the 3 additional mutants confirm the new assertions pin the exact diagnostic tokens, not just "some drop happened." Module restored + `git diff --stat` empty after the run.

## Verification commands

```
git fetch origin main && git merge-base HEAD origin/main   # = e7d93ca (origin/main tip), no rebase
git diff origin/main...HEAD -- runtime/                     # docstring-only, 1 file
python3 -m unittest tests.test_routing_environment_reports tests.test_routing_policy \
  tests.test_routing_cli tests.test_task_environment_contract tests.test_flow_start \
  tests.test_run_environment_evidence tests.test_recovery_production_trigger
#   -> Ran 131 tests ... OK   (GLOB_EXIT=0)
python3 -m runtime.smoke                                    # {"ok": true}  (SMOKE_EXIT=0)
python3 scripts/check_review_evidence.py 206
```

## Diff-in-bounds

New/changed: `tests/test_routing_environment_reports.py` (+118, 5 new tests + 1 helper + `allow_older_task_revision` kwarg on `_contracted_task`), `runtime/recovery/production.py` (2 docstrings). No checklist change (no status move — dispatch expected none). No new runtime behavior. In bounds.

## Verdict

**APPROVE.** The "zero runtime logic change" claim is true (docstring-only in `runtime/`). GAP 1 and GAP 2 are closed with correctly-targeted tests on the right paths; gina's 3 survivors are killed. L79 prose is a factual correction that neither makes nor changes any authority gate. Full targeted glob + smoke green. One non-blocking doc-drift note (the "separate open design task" phrasing goes stale when #207 merges).
