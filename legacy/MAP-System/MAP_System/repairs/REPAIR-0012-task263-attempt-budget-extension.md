# Repair Record

Repair ID: REPAIR-0012
Related task: TASK-263
Found by: claude-lab-lili
Date: 2026-07-28
Severity: STRUCTURAL
Status: APPLIED (via TASK-293 extend-attempts verb, not the raw SQL originally proposed)

## What was found

TASK-263 reached `attempt=3` with `max_attempts=3` at the moment it was
submitted, then received a CHANGES_REQUESTED verdict from its independent
reviewer (`mapfinish-kino`,
`MAP_System/artifacts/reviews/task263-independent-review-kino.md`). SQLite
`claim_task()` guards every claim with `AND attempt < max_attempts`
(`MAP_System/db/claims.py:160`), so `map_task.py rework` can still move the
task CHANGES_REQUESTED -> READY, but no further claim can succeed. The task
would be permanently unworkable despite having exactly one small, bounded,
mechanical finding outstanding.

## Surfaced by

The reviewer's own verdict. `mapfinish-kino` was explicitly instructed not to
soften a real finding to avoid exhausting the attempt budget, and correctly
did not: it raised a REQUIRED finding (acceptance criterion 4 names
`source-hash drift` and `acceptable evidence sets` as required test
categories; neither has direct test coverage in
`MAP_System/tests/test_task_memory_claim_evidence_pilot.py`) knowing the
budget was exhausted.

## Severity rationale

Raising a task's durable attempt budget changes what the claim gate will
allow going forward — a lifecycle-authority parameter, not a content or
mirror fix. Narrow (one integer, one task) and fully reversible. Identical
class to REPAIR-0010, which set the precedent: `STRUCTURAL`, propose-only.

## Proposed or applied fix

Raise `TASK-263.max_attempts` from 3 to 4 via direct SQL
(`UPDATE tasks SET max_attempts=4 WHERE task_id='TASK-263'`), since no
sanctioned CLI verb exists for this, then re-export file/graph mirrors. This
grants exactly one additional attempt to close the single REQUIRED finding
(add direct test coverage for source-hash drift detection and for acceptable
substitute scoring). No other task field, claim state, or output-path
ownership is touched.

## Authority check

- [ ] DRIFT or mechanical BLOCKING — core agent applied directly
- [ ] Judgment-requiring BLOCKING — proposed via hcom before applying
- [x] STRUCTURAL — explicit bigboss approval obtained before applying:
      bigboss granted standing authorization for this work batch in the
      active chat turn on 2026-07-28 — "You have my permission to approve
      whatever needs to be done" — issued together with the instruction to
      drive the MAP completion conditions to done using available agents.
      Recorded verbatim rather than paraphrased because it is a standing
      grant covering a batch, not a per-item "go for it" like REPAIR-0010's,
      and a future reader should be able to judge its scope for themselves.

## Verification

Confirmed after the verb applied the extension (see Resolution below):

- `scripts/validate_task_graph.py` and `validate_task_mirrors.py`: pass; the
  verb re-exported mirrors itself as part of the transaction.
- Only `TASK-263.max_attempts` changed (3 -> 4). The verb's own return
  payload reports `attempt: 3` unchanged, and `status` remained
  CHANGES_REQUESTED.
- A durable event naming actor, task, old/new budget, and reason was emitted
  by the verb rather than hand-written.

## Recurrence check

- [ ] First occurrence of this drift class
- [x] Repeat — logged in `shared/improvement-backlog.md`
- [x] Repeat — permanent fix proposed (validator/template/decision): TASK-293

REPAIR-0010 (TASK-280, 2026-07-27) explicitly wrote: "Worth a permanent
`map_task.py extend-attempts` verb if this recurs a second time, per the same
recurrence logic REPAIR-0009 applied." This is that second occurrence, one
day later. Honouring that stated trigger rather than applying a third
one-off: TASK-293 proposes the sanctioned verb.

## Status correction, 2026-07-28

This record was first written as `Status: APPLIED`, but the raw-SQL fix it
proposed was **never applied and must not be**. The harness permission
classifier blocked the direct `UPDATE tasks SET max_attempts` — correctly,
since it is an unmediated mutation of canonical lifecycle state. That block
was not an obstacle to route around; it is the same conclusion REPAIR-0010
reached on process grounds, now enforced mechanically.

## Resolution, 2026-07-28 — applied through a sanctioned verb

TASK-293 landed the `map_task.py extend-attempts` verb (built by
`mapfinish2-zemi`, independently reviewed and APPROVED by
`lili-replacement-nisa`, who verified all four guard rails by direct
exercise against a scratch database rather than trusting the test suite).

The extension was then applied through that verb rather than by SQL:

```
map_task.py extend-attempts TASK-263 --actor claude-lab-lili --add 1 --reason "..."
-> {"prior_max_attempts": 3, "new_max_attempts": 4, "attempt": 3}
```

`attempt` stayed at 3; only `max_attempts` moved. The verb emitted its own
durable event naming actor, old/new budget, and reason, and re-exported the
mirrors — so this extension is auditable in a way the two preceding raw-SQL
extensions (REPAIR-0010, and the pattern REPAIR-0009 flagged) were not.

The same verb also unblocked TASK-254, which had independently hit the
identical ceiling. Two tasks were stuck behind a missing verb.

**Net outcome: the blocked repair produced a better result than the repair
would have.** Had the raw SQL succeeded, TASK-263 would have been unblocked
and the underlying gap would have survived to a fourth occurrence.

## Notes

- The recurrence is itself evidence about attempt budgets, not just about the
  missing verb: both TASK-280 and TASK-263 exhausted their budget while the
  outstanding findings were small and mechanical. A default `max_attempts` of
  3 counts *submissions*, not *defects*, so a task that is fundamentally sound
  but reviewed thoroughly can exhaust its budget faster than a task nobody
  looked at closely. TASK-293 was asked to judge whether the default is
  calibrated correctly, not only whether a verb exists to override it.
- That question was answered and the answer was **leave the default at 3**.
  `mapfinish2-zemi` argued the two exhaustions were evidence the reviews were
  thorough rather than that the budget is wrong, and that the real defect was
  the *cost* of the escape hatch (raw SQL + STRUCTURAL approval + a repair
  record), which the verb removes without blurring the signal a global bump
  would blur. Reviewer `lili-replacement-nisa` agreed but added a caveat worth
  carrying forward: both exhausted tasks were architecture/policy tier, so
  whoever revisits this should check tier before choosing between a global
  bump and a tier-scaled default, rather than treating "it recurred a third
  time" as automatic grounds for raising it globally.
- Rollback: lower `max_attempts` back to 3, or leave as-is once TASK-263
  reaches a terminal status — the extra budget slot has no effect after that.
