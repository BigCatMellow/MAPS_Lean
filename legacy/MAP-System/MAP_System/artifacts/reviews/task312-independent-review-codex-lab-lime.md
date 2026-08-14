# Review: TASK-312 Reproducible Green MAP Baseline

task_id: TASK-312
reviewer: codex-lab-lime
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-312-codex-lab-lime-84fe0934
review_scope: Independent Biggie-local review of every declared TASK-312 output, the seven-failure recovery scope, and the unpublished candidate baseline under TASK-315's preserved cross-host convergence workflow.

## Verdict

APPROVED

The documented canonical command is independently reproducible: `bash
MAP_System/scripts/run_tests.sh` completed with 84 passes, zero failures, and
exit status zero on Biggie. Focused validators and regressions also pass. The
seven recovery failures are either repaired in the declared outputs or
truthfully attributed to separately owned, visible work, with no broad
refactor or unrelated overwrite found.

This verdict approves TASK-312's baseline verification deliverable only. It
does not approve TASK-294 or authorize publication/convergence under TASK-315.
Canonical TASK-312 approval must remain blocked until this review artifact is
transported to Smalls and its SHA-256 is independently confirmed there.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| A single documented baseline command passes, or remaining environmental limitations are isolated | PASS | `MAP_System/artifacts/recovery/ws3-green-baseline.md` names `bash MAP_System/scripts/run_tests.sh`; the independent run completed `SUMMARY pass=84 fail=0 total=84`. No environmental exclusion was required. |
| The seven captured failures are addressed | PASS | TASK-311 is canonically `APPROVED`; the Herdr summary validates; event validation reports zero new warnings; TASK-294's stale assertion no longer fails in the candidate tree; Layer-1 passes; and both copied-database fixture regressions pass after fixture-local permission normalization. |
| No unrelated changes are overwritten and each change has focused verification | PASS | Declared-output diffs are narrow: one research envelope, one reviewed warning-baseline advance, removal of retired TASK-254 from generated active state, and one fixture-local `chmod(0o644)` in each affected test. `git diff --check` passes for all seven outputs. TASK-315 records verified rollback archives for both dirty worktrees. |
| A different core agent independently reproduces the final baseline | PASS | `codex-lab-lime`, distinct from owner `zeno`, claimed the canonical review and independently ran the full command plus focused checks. |

## Seven-Failure Trace

1. **Active output collisions:** TASK-311 is canonically `APPROVED`; the task
   graph and shared-output regression checks pass.
2. **Invalid Herdr research evidence:** the existing body is preserved beneath
   a complete research-summary envelope; research validation passes.
3. **Two new event warnings:** the baseline advance is explicit and reviewed.
   The live validator reports 34 legacy warnings, zero new warnings, and only
   one warning after the old line-680 boundary: line 2145's noncanonical
   `TASK_SUBMITTED`. Line 2146 is the canonical `SUBMISSION` that explicitly
   supersedes it.
4. **TASK-294 exact-code assertion:** the candidate local-lane suite passes
   5/5. TASK-294 remains separately `SUBMITTED`; this review does not bless or
   release that task.
5. **Layer-1 derivative:** all eight Layer-1 tests pass after the event evidence
   is truthful.
6. **Liveness read-only fixture:** the production database remains read-only;
   only the copied temporary fixture is made writable. All 18 focused tests
   pass.
7. **Chaos read-only fixture:** the same fixture-local correction is used. All
   six focused tests pass.

## Files Reviewed

- `MAP_System/artifacts/recovery/ws3-green-baseline.md`
- `MAP_System/artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`
- `MAP_System/events/warning_baseline.json`
- `MAP_System/shared/active-lane-annotations.json`
- `MAP_System/shared/current-state.md`
- `MAP_System/tests/test_chaos_resilience.py`
- `MAP_System/tests/test_liveness_reaper.py`
- `MAP_System/artifacts/recovery/ws3-readonly-fixture-finding.md`
- `MAP_System/artifacts/tests/map-health-baseline-2026-07-28.md`
- `MAP_System/artifacts/operations/biggie-smalls-source-convergence-20260801.md`
- `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_KICKOFF.md`

## Authority And State Check

- Canonical gateway reads report TASK-254 `RETIRED`, TASK-263
  `CHANGES_REQUESTED`, TASK-294 `SUBMITTED`, TASK-311 `APPROVED`, and TASK-312
  `SUBMITTED`.
- Biggie's production `MAP_System/map.db` is mode `0444`. Read-only inspection
  gives the same TASK-254, TASK-263, and TASK-294 statuses as the Smalls gateway.
- The generated active-lane table and annotations contain TASK-263 and no
  TASK-254. `validate_shared_state_tasks.py` confirms that the generated table
  matches the mirrored database.
- No Biggie writer, local database mutation, validator exclusion, or writable
  production-database workaround was used.
- A post-run `map-authority status/route` probe correctly failed closed as
  `INVALID` because this invocation could not establish writer-service
  inactivity through the user service-manager bus. The same report records a
  successful mirror sync at `2026-08-01T18:16:02.234101Z`; direct Smalls
  gateway reads and read-only mirror rows agree. This operational diagnostic
  does not alter the content match above and was not bypassed.

## Independent Verification

- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_research_artifacts.py` — PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_events.py --fail-on-new` — PASS; `errors=0`, `new_warnings=0`, `baseline_line_count=2145`.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_shared_state_tasks.py` — PASS.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_validate_layer1` — PASS; 8/8.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_local_ollama_lane` — PASS; 5/5.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_liveness_reaper` — PASS; 18/18.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_chaos_resilience` — PASS; 6/6.
- `bash MAP_System/scripts/run_tests.sh` — PASS; 84/84, exit status zero.
- Declared-output SHA-256 values were identical immediately before and after
  the full run, demonstrating that verification did not mutate the candidate
  evidence or tests.

## Non-Blocking Publication Dependency

TASK-294 remains canonically `SUBMITTED` and owns the local-lane assertion
change on which this candidate baseline relies. TASK-315 must continue to
respect TASK-294's independent review and lifecycle gate before publishing the
combined source. This is not a TASK-312 acceptance failure: the present task
truthfully identifies the dependency and independently demonstrates the green
candidate rather than claiming ownership of TASK-294's change.

## Forbidden Changes Check

This review did not edit implementation files, tests, task records, shared
state, Git state, or the external CommandCenterUI. It did not synchronize the
mirror, mutate local `map.db`, approve TASK-312, or approve TASK-294. Its only
workspace change is this review artifact; the canonical review claim and its
release use the sanctioned `map-authority` gateway.
