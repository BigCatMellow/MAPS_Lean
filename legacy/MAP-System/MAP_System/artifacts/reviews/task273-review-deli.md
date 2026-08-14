# Review: TASK-273 — Add a sanctioned owner-reassignment verb for tasks whose owner agent no longer exists

task_id: TASK-273
reviewer_id: claude-lab-deli
task_owner: command-center
review_date: 2026-07-23

## Verdict

APPROVED

## Context

Independent review of the submission by `codex-lab-mubo` at 2026-07-23T03:55:07Z.
Review slot claimed via `claim_review("TASK-273", "claude-lab-deli")` → True
(`REV-TASK-273-claude-lab-deli-ed4043cd`).

**Independence.** This reviewer authored nothing in TASK-273, created no upstream
or downstream task, and holds no interest in the outcome. Every other live agent
has a declared conflict: `claude-lab-bima` created TASK-273, `claude-lab-zaro`
owns TASK-274 which depends on it, `codex-lab-mubo` implemented it, `codex-lab-feta`
was routing its review. The task's durable owner is `command-center`, so the
mechanical no-self-review guard in `claim_review()` could not have enforced
separation for anyone here (INS-0039); separation on this task is operational.

**Disclosed pressure on the verdict.** `validate_task_graph` is currently failing
repo-wide on `Output path collision: MAP_System/db/claims.py owned by TASK-273
and TASK-274`. Reading `scripts/validate_task_graph.py:94` and `:107-116`, the
collision check skips tasks in `{DONE, APPROVED, RELEASED, RETIRED} | {BLOCKED}`.
`CHANGES_REQUESTED` is in the validator's *active* set. So **approval is the only
disposition that clears the red gate; rejection leaves it red.** That is a live
incentive to approve, and it is recorded here so the verdict can be checked
against it. The findings below were reached from the code and from independently
reproduced evidence, not from mubo's or bima's summaries, and nothing in the
implementation was waved through on that basis. Had a BLOCKER or REQUIRED finding
survived, the correct action was rejection with the gate left red.

## Files Reviewed

- `MAP_System/db/claims.py` (`TERMINAL_TASK_STATUSES`, `reassign_task_owner`)
- `MAP_System/scripts/map_task.py` (`reassign_owner`, `reassign-owner` subparser)
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/tests/test_reassign_owner.py`
- `MAP_System/scripts/validate_review.py` and `MAP_System/tests/test_no_self_review.py` (confirmed untouched)
- `MAP_System/scripts/validate_task_graph.py`, `MAP_System/scripts/advisory_monitor.py` (terminal-status precedent)
- `MAP_System/migration/schema.sql`, live `map.db` (read-only)

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Sanctioned function + CLI verb reassigns `tasks.owner` on a nonterminal task; requires actor, new owner, written reason; refuses terminal status | PASS | `reassign_task_owner()` at `db/claims.py:352`; CLI `reassign-owner` at `scripts/map_task.py:668` with `--actor`, `--new-owner`, `--reason` all `required=True`. All three arguments raise `ValueError` when empty or whitespace-only. Reviewer probe against the **real** `schema.sql`, not the test's synthetic table: `DONE`, `RELEASED`, `RETIRED` each returned `None` with the row unchanged; `READY`, `IN_PROGRESS`, `SUBMITTED`, `CHANGES_REQUESTED`, `APPROVED`, `BLOCKED`, `CONFLICT` all succeeded. |
| 2 | New owner registered via the same `ensure_agent` contract | PASS | The `INSERT OR IGNORE INTO agents (agent_id, label, agent_type, status) VALUES (?, ?, 'core', 'available')` at `claims.py:398` is byte-for-byte the statement in `map_task.py:ensure_agent()` (`:47`), including the `agent_id.replace("-", " ").title()` label. `connect()` sets `PRAGMA foreign_keys = ON`, and the reviewer probe confirmed the `tasks.owner` FK target exists after reassignment to a previously unknown agent. `INSERT OR IGNORE` means an existing agent's `status` is never overwritten, so reassigning to a live agent cannot flip its status, and reassigning to a dead one cannot resurrect it. |
| 3 | Durable event names actor, prior owner, new owner, and reason | PASS | `map_task.py:reassign_owner` appends a `PROGRESS` event whose summary is `"{task} owner reassigned by {actor}: {prior} -> {new}. Reason: {reason}"`. Verified end-to-end in the CLI test against a real-schema DB: the `events` row carries `sender_id=review-actor` and all four fragments, and the mirrored `events.jsonl` line carries `old-owner -> replacement-owner`. Same event shape and `PROGRESS` type as the `recover-orphan` precedent from TASK-266. |
| 4 | Only `owner` changes; `status`, `claimed_by`, `lease_expires_at`, `heartbeat_at`, `attempt` provably untouched | PASS | Reviewer probe on a task populated with a live claimant, a future lease, a heartbeat and `attempt=3`, using the real schema. After reassignment the only differing column was `owner`. `status`, `claimed_by`, `lease_expires_at`, `heartbeat_at`, `attempt`, `updated_at`, `priority`, `max_attempts`, and `required_agent` were all byte-identical. The `UPDATE` sets `owner` alone; the `owner IS ?` predicate is a compare-and-swap that also handles a `NULL` prior owner correctly (verified: a `NULL`-owner task reassigns rather than silently no-op'ing, which `owner = ?` would have broken). |
| 5 | Tests cover happy path, terminal refusal, missing/empty new owner, unknown task, non-mutation; registered in `run_tests.sh`; suite green; mirrors pass | PASS with a correction to the submitted numbers — see Findings | All five cases present in `tests/test_reassign_owner.py` and reproduced by this reviewer: 5/5. Registered at `run_tests.sh:44`. `validate_task_mirrors` passes. Full suite reproduced independently at **71 pass / 4 fail**, not the submitted 72/3 — see F1. |
| 6 | No-self-review guards in `claim_review()` and `validate_review.py` left unchanged | PASS | `scripts/validate_review.py` and `tests/test_no_self_review.py` are clean in Git and carry `mtime 2026-07-15`, eight days before this task. In `claims.py`, the self-review line `if owner and owner.lower() == reviewer_id.lower(): return False` is unmodified context in the diff. The other `claim_review()` changes in the working tree (reviewer registration, `IntegrityError` classification) are TASK-270's released work, self-identified as such in their comments, and predate this submission. INS-0039 was not folded in. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Changing the no-self-review guards (INS-0039 scope, explicit NON-GOAL) | NOT BROKEN |
| Modifying paths outside the four registered `output_paths` | NOT BROKEN |
| Widening reassignment to terminal tasks | NOT BROKEN |
| Coupling owner reassignment to claim state | NOT BROKEN |

## Findings

**F1 — REQUIRED (resolved during review, no rework needed).** The submission
reported "full suite 72 pass / 3 disclosed baseline failures." This reviewer
reproduces **71 pass / 4 fail**. The discrepancy is fully explained and is not a
defect in the delivered code: TASK-273 was submitted at 03:55:07Z and TASK-274,
which registers the same `claims.py` output path, was created 29 seconds later at
03:55:36Z. The collision — and therefore the `validate_task_graph` failure — did
not exist when mubo measured. The submitted figure was accurate when taken and is
stale rather than wrong. Recorded so the release record carries the reproducible
number.

The four current failures, and what happens to each on approval:

- `validate_task_graph` — the TASK-273/TASK-274 `claims.py` collision. **Clears on
  approval**, because `APPROVED` is in the validator's terminal set.
- `validate_layer1_test` — asserts `overall_pass`, failing on
  `['validate_events', 'validate_task_graph']`. Partially clears; still fails on
  `validate_events`.
- `validate_research_artifacts` — 8 missing template fragments in
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`. Pre-existing,
  unrelated.
- `validate_events_no_new_warnings` — one new non-canonical event type,
  `TASK_SUBMITTED` at `events.jsonl:2145`, written by `codex-lab-kiri` for
  TASK-257 on **2026-07-19**. Pre-existing, unrelated, and four days older than
  this task.

None of the three surviving failures touch any TASK-273 output path. Expected
post-approval state is 72 pass / 3 fail.

**F2 — RECOMMENDED.** `reassign_task_owner` does not set `updated_at`, while every
other mutating verb in `claims.py` does (`release_task` `:216`, `expire_leases`,
`recover_orphan_task`). The consequence is that a reassignment changes the durable
owner and the exported task mirror while the row still reports it was last updated
before the change. The audit trail survives in `events` and in `events.jsonl`, so
nothing is lost and this does not block. But the current behaviour is *locked in*
by `test_reassign_owner.py:98`, which asserts `updated_at` unchanged, so it now
reads as a deliberate contract rather than an omission — and criterion 4 does not
list `updated_at` among the fields required to be untouched. Someone should decide
which it is on the record instead of inheriting it from a test assertion. Not for
this task.

**F3 — OPTIONAL.** When the compare-and-swap at `claims.py:404` loses a race (a
concurrent writer changed `owner` between the `SELECT` and the `UPDATE`),
`reassign_task_owner` returns `None`, and `map_task.py:reassign_owner` then reports
`"{task} is {status}, not reassignable. Owner reassignment refuses terminal
DONE/RELEASED/RETIRED tasks."` — which is false for a nonterminal task that simply
lost the race. Narrow and self-correcting on retry.

**F4 — OPTIONAL.** On that same lost race, the `INSERT OR IGNORE` into `agents` has
already executed and commits with the transaction, so a failed reassignment can
leave a newly registered agent row behind. Registration is idempotent and carries
no authority, so the effect is a harmless orphan row.
`test_unknown_task_returns_none_without_registering_owner` covers the unknown-task
path, where the early return means no such row is created; the race path is
uncovered.

**Observation, not a finding.** `TERMINAL_TASK_STATUSES = {DONE, RELEASED, RETIRED}`
deliberately excludes `APPROVED`, which `validate_task_graph` treats as terminal.
That is correct for this task's purpose: all 76 `APPROVED` tasks are awaiting
release, and the 21 stale-owner tasks the triage measured are in exactly that
state, so excluding `APPROVED` would have made the verb useless. The chosen set is
identical to `advisory_monitor.py:50`, the closest precedent. `CONFLICT`-frozen
tasks are also reassignable; this reviewer judges that correct — owner is durable
accountability, and changing it neither advances nor unfreezes contested work.

## Risks Identified

- **Authority.** The verb has no gate beyond a written reason: any actor can
  reassign any nonterminal task to any owner. That matches `recover-orphan`, which
  TASK-273 was scoped to model, and the event log makes every use attributable. It
  is worth knowing that reassignment is auditable rather than prevented.
- **Sequencing.** TASK-274 registers the same `claims.py` path and depends on this
  task. Approval clears the collision; TASK-274 must not be claimed before
  TASK-273 releases, or the collision returns from the other side.

## Conclusion

All six acceptance criteria are met. Every criterion was verified by reproducing
the evidence — a live probe against the real schema, an independent full-suite
run, and direct inspection of the guard files — rather than by reading the
submission report. No BLOCKER or REQUIRED finding survives. F2 through F4 are
non-blocking and are recorded for follow-up, not rework.

**APPROVED.**
