# Review: TASK-293 (map_task.py extend-attempts verb)

## Verdict

APPROVED

## Reviewer

lili-replacement-nisa. Not a self-review: submission author is
`mapfinish2-zemi` (`db/review_authorship.get_submission_author`), unrelated
to my identity or rotation lineage. Claimed via
`claim_review("TASK-293", "lili-replacement-nisa")` — `True` on first call.

## Files Reviewed

- `MAP_System/db/claims.py` (`extend_task_attempts`, `TERMINAL_ATTEMPT_STATUSES`)
- `MAP_System/scripts/map_task.py` (`extend_attempts`, CLI wiring)
- `MAP_System/tests/test_map_task_extend_attempts.py` (9 tests)
- `MAP_System/scripts/run_tests.sh` (wiring)
- `MAP_System/tasks/TASK-293.json` (acceptance criteria, calibration judgment)
- `MAP_System/scripts/validate_task_graph.py` (cross-check for item a)
- `MAP_System/events/events.jsonl` (output-path registration event, item b)

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Focused tests cover success/refusal cases, wired into run_tests.sh, suite passes | PASS | 9/9 tests pass, reproduced myself. `run_tests.sh:46` runs the file. |
| 2 | Durable canonical event names actor, task, old/new budget, reason | PASS | `map_task.py:598-602`: `"{task} max_attempts extended by {actor}: {prior} -> {new} (attempt={n}). Reason: {reason}"`, type `PROGRESS` — same event type every other lifecycle verb in this file uses (`create`, `reassign-owner`, `recover-orphan`, `add-output-path` all append `PROGRESS`), not an inconsistency unique to this change. |
| 3 | Task record states calibration reasoning for default max_attempts | PASS | See "Criterion 5" section below — read and independently assessed, not just checked for presence. |
| 4 | Refuses lowering below current attempt, refuses terminal status, requires non-empty reason | PASS | Verified by direct exercise (not just reading), see below. |
| 5 | `map_task.py` gains `extend-attempts` verb: task_id, --actor, --max-attempts/--add, required --reason, transactional, re-exports mirrors | PASS | `map_task.py:542-607`. Mutual-exclusivity of `--max-attempts`/`--add` enforced (`if (args.max_attempts is None) == (args.add is None): raise UsageError`), `ensure_agent` called for actor, `sync_files` called after. |

## Verified by direct exercise, not just reading

Built a scratch SQLite DB from `migration/schema.sql` and called
`extend_task_attempts()` directly (not the CLI, not the test suite) against
four synthetic tasks:

1. `CHANGES_REQUESTED`, attempt=3/max=3 → raise to 4: **succeeds**, returns
   the expected dict.
2. `APPROVED`, attempt=3/max=3 → raise to 4: **refused** (`None`).
3. `DONE`, attempt=1/max=3 → raise to 4: **refused** (`None`) — this is
   zemi's disclosed addition beyond the literal criterion text (see item a).
4. `CHANGES_REQUESTED`, attempt=2/max=3 → lower to 1: **refused** (`None`).
5. Empty actor: **raises `ValueError`** with an attributability message.
6. Whitespace-only reason: **raises `ValueError`** with an auditability
   message.
7. Unknown task_id: returns `None`, does not raise.

All seven match the acceptance criteria and the docstring's stated
contract exactly. The SQL update itself
(`UPDATE ... WHERE status NOT IN (...) AND max_attempts = ? AND attempt <= ?`)
is a real optimistic-concurrency guard, not just a pre-check followed by
an unconditional write — a second, concurrent extension attempt between
the read and the write would find `rowcount != 1` and correctly return
`None` rather than silently overwriting a race.

## Item (a): was adding `DONE` to the terminal set correct, or scope creep?

**Correct, not scope creep.** `validate_task_graph.py:94` defines its own
terminal set as `{"DONE", "APPROVED", "RELEASED", "RETIRED"}` — `DONE` is
already treated as terminal elsewhere in this system's canonical logic.
25 tasks currently sit at `status=DONE` in `map.db` (confirmed live). The
acceptance criterion's parenthetical `(APPROVED/RELEASED/RETIRED)` reads as
an illustrative list, not an exhaustive one, given the verb's whole
purpose is "never let a terminal task's history be quietly altered" — and
`DONE` is terminal by every other measure in this codebase. Leaving it out
would have been the actual gap.

## Item (b): was registering `db/claims.py` via `add-output-path` done properly?

**Yes.** Verified via `events.jsonl` (2026-07-28T16:48:32Z): zemi
registered the path *before* editing, not after — matches the honest
ordering this session has repeatedly required. Precedent confirmed
directly: `TASK-266` and `TASK-273` both have `MAP_System/db/claims.py` in
their own registered `output_paths` for the same kind of claims.py
extension. This is not a novel or unusual registration.

## Criterion 5: the max_attempts calibration question — my own assessment, not a rubric check

I agree with keeping the default at 3, but I want to sharpen the
reasoning rather than just endorse it as written.

Zemi's argument: two exhaustions (`REPAIR-0010`/TASK-280,
`REPAIR-0012`/TASK-263) in two days is evidence of thorough review
converging on small findings, not evidence the default is too tight; the
actual problem was the *cost* of the escape hatch (raw SQL + STRUCTURAL
operator approval + a repair record), which this task now reduces to one
audited CLI call. I find this basically right, but it frames the decision
as a binary (raise the global default vs. leave it at 3) when there's a
third option worth naming: **both recurrences were `architecture`/`policy`
tier tasks** (TASK-280, TASK-263), not mechanical/bounded ones. A
tier-scaled default (e.g., a higher ceiling specifically for
architecture/policy-tier tasks, which structurally invite more review
rounds, while leaving 3 as the default everywhere else) would be a more
targeted fix than either extreme. I'm not recommending this be built now —
two data points is not enough to justify a new dimension of
configuration, and zemi's stated revisit condition ("a 3rd/4th occurrence
recurs despite extend-attempts being available") is a sound, falsifiable
trigger. But if a third occurrence happens and it is *also*
architecture/policy tier, that pattern (not just "recurred again") is the
signal worth acting on, and it should be named explicitly in whatever
revisits this rather than defaulting straight to "raise everyone's
budget to 4."

Net: keep default=3 for now, as zemi recommends, with the added note that
the next review of this question should check *which tier* is recurring
before deciding between a global bump and a tier-scaled one.

## Forbidden Changes Check

`git status --porcelain` shows `db/claims.py`, `scripts/map_task.py`,
`scripts/run_tests.sh` modified and `tests/test_map_task_extend_attempts.py`
new — all four match TASK-293's registered `output_paths` exactly.
`tests/test_review_claims.py` also shows modified; `git diff` on it shows
TASK-278-authored content (a submission-authorship fixture requirement and
a TASK-270 regression test), unrelated to this submission and already
released — pre-existing uncommitted state in a repo with no recent commit,
not scope creep by this task.

## Findings

None.

## Notes

This is a well-scoped, carefully guarded lifecycle-authority verb. Both
things flagged for independent judgment (the `DONE` addition, the
`claims.py` output-path registration) check out against real evidence
rather than just the submitter's own account of them. The calibration
question has a real, reasoned answer rather than a placeholder. Approving
unblocks TASK-254 and TASK-263's rework path as intended.
