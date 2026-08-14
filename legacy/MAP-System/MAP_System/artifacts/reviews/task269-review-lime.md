# Review: TASK-269

task_id: TASK-269
reviewer: codex-lab-lime
task_owner: claude-lab-gabi
review_date: 2026-07-22

## Verdict

APPROVED

The approved helper tier now has one documented storage field and one visible
runtime drift signal. No `BLOCKER` or `REQUIRED` finding remains.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Helper-note contract documents the approved model tier and escalation context. | PASS | `MAP_System/AGENTS.md` adds `model:` to the plain metadata block, distinguishes it from provider, and requires approver/lower-tier context for above-default use. |
| 2 | Runner surfaces active notes missing a tier. | PASS | Live runner output contains `helpers_missing_model_tier: [helper-local-map-advisor-4b-2026-07-18]` and a matching event line. The current tiered Herdr helper is correctly absent from the warning. |
| 3 | Helper guide and storage contract are connected. | PASS | `helper-agent-guide.md` points directly to the `model:` contract field and explains which escalation details remain in the note body. |
| 4 | Tests cover tiered active, untiered active, and untiered completed notes. | PASS | Focused suite passes; active untiered is reported, tiered active is not, blank counts as missing, and completed untiered is excluded. |
| 5 | Capacity behavior is unchanged. | PASS | The same live runner reports two active notes and capacity `2/4`; the new warning contains one note without changing `active_helper_notes`. Existing capacity test also passes unchanged. |

## Forbidden Changes Check

| Boundary | Status |
|---|---|
| Do not change the tier rubric itself. | NOT BROKEN — selection guidance and escalation thresholds are unchanged. |
| Do not reopen historical completed notes for backfill. | NOT BROKEN — missing-tier reporting is restricted to active/running/in-progress notes. |
| Do not change helper-capacity accounting. | NOT BROKEN — capacity still derives only from `active_helper_notes`. |
| Do not give the runner approval or enforcement authority. | NOT BROKEN — output is an advisory drift signal; no helper is stopped, reassigned, or promoted automatically. |

The active-only scope is appropriate. Completed notes are immutable historical
evidence and cannot be repaired operationally; reporting all 76 historical
omissions would create permanent noise while obscuring the actionable active
set.

## Files Reviewed

- `MAP_System/AGENTS.md`
- `MAP_System/graph/runner.py`
- `MAP_System/notes/helper-agent-guide.md`
- `MAP_System/tests/test_runner_helper_notes.py`
- `MAP_System/tasks/TASK-269.json`
- Live helper notes and runner JSON, for end-to-end behavior only

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_runner_helper_notes.py` -
  PASS, four behavioral checks.
- Live `MAP_System/.venv/bin/python MAP_System/graph/runner.py` - PASS; warning
  key and event agree, tiered active helper is excluded, capacity remains 2/4.
- Mutation removing missing-tier computation - expected FAIL in active and
  blank-tier tests; unchanged capacity test still passes.
- Mutation removing the `MapState` declaration - expected FAIL in the
  propagation guard, reproducing the class of real-graph omission found during
  implementation.
- Task mirror and graph validators - PASS.
- Full `MAP_System/scripts/run_tests.sh` - 70 pass / 2 fail, matching the known
  baseline. Both failures derive from the pre-existing non-canonical
  `TASK_SUBMITTED` event at `events.jsonl:2145`; no TASK-269 or runner consumer
  failed.

## Security And Policy Review

PASS. The runner remains read-only over helper notes, adds no command execution,
network access, write path, secret handling, or automatic policy action. The
new field is advisory metadata and does not grant model authority. A malformed
or absent field only creates a visible warning.

Non-blocking limitation: the existing metadata reader detects field presence
but does not validate the tier vocabulary or constrain fields to the opening
metadata block. TASK-269's requested absence signal is correctly delivered;
stricter schema validation can be considered separately if invalid tier values
become an observed problem.
