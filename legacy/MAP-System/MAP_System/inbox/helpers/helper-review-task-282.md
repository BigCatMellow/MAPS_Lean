# Helper Assignment - Independent review of TASK-282 (structured submission claims)

- status: complete
- outcome: TASK-282 APPROVED cleanly on first pass. Review artifact:
  `MAP_System/artifacts/reviews/task282-independent-review-rita.md`.
  The forbidden-changes process note (avoid raw `git diff`) worked as
  intended -- no false-positive BLOCKER this time.
- owner: claude-lab-venu
- provider: claude
- model: haiku
- created_at: 2026-07-27
- scope: Independent review of TASK-282's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `claude-lab-venu` (submitter) or `claude-lab-nora`
  (predecessor session this session replaced).

## Why a helper

`codex-lab-diro` ack'd the review request but cannot claim: it is at
mandatory context-rotation threshold with a replacement pending (same
situation it hit on TASK-281's review). No other clean core reviewer
(Codex or Claude core session) is currently live. Per
`notes/helper-agent-guide.md`'s Review-Conflict Default, routing to a
spawned visible helper rather than escalating routing to the operator.

## Important process note from the TASK-281 review

The helper that reviewed TASK-281 (also spawned for this exact reason)
initially issued an incorrect BLOCKER/REJECT by running `git diff` against
`git HEAD` and treating every uncommitted change in the repo as if it were
caused by the submission under review. **This repo has not committed since
2026-07-15/23**, so `git diff` shows roughly two weeks of cumulative,
unrelated work from many different tasks and sessions — it is NOT a valid
forbidden-changes check here. If you need to confirm a submission touched
only its registered output paths, either (a) compare the repo-relative
paths actually written against the exact list in the task's `output_paths`
(see `MAP_System/tasks/TASK-282.json`), or (b) check `stat` mtimes for any
file you suspect might be out-of-scope — a file last modified before this
task's claim window is not something this submission touched, regardless of
what `git diff` shows.

## Task summary

TASK-282: "Add criterion-level submission claims and independent
verification records" (TASK-277 roadmap item 5). Fresh, greenfield
implementation (attempt 1/3), submitted and unclaimed. Standalone additive
capability — does not read or write `tasks.status`, is not wired into
`submit`/`approve`, same "pilot, not production integration" posture as the
already-approved TASK-281.

## Input paths (output_paths registered to TASK-282)

- `MAP_System/artifacts/tests/task282-structured-submission-delivery-note.md`
  (delivery note — read this first)
- `MAP_System/migration/submission_record_schema.sql` (new, additive SQL
  schema; intentionally separate from `migration/schema.sql`)
- `MAP_System/scripts/submission_records.py` (new script: `claim`/`verdict`/
  `show` over two new tables)
- `MAP_System/tests/test_submission_records.py` (9 focused tests)
- `MAP_System/workflow/templates/submission_record.json` (documentation
  template for the record shape)

## Task record

`MAP_System/tasks/TASK-282.json` — read `acceptance_criteria` there.

## Expected review artifact

A review record following `AGENTS.md`'s Review Standard, using these exact
section headers (required by `scripts/validate_review.py` before
`map_task.py approve` will accept it — this tripped up the TASK-281 review
too):

```
## Verdict
## Acceptance Criteria Check
## Files Reviewed
## Forbidden Changes Check
```

Cover:

1. Each acceptance criterion in `TASK-282.json`, PASS/FAIL/PARTIAL with
   evidence.
2. Forbidden-changes check using the method above (output-path list or
   mtimes), NOT a raw `git diff`.
3. Independent verification: run `MAP_System/.venv/bin/python
   MAP_System/tests/test_submission_records.py` directly and confirm 9/9;
   reproduce at least one or two claims yourself rather than trusting the
   delivery note (e.g. that a `complete` claim with a missing evidence path
   is genuinely rejected with zero rows inserted, or that
   `record_verdict()` genuinely refuses a reviewer verifying their own
   claim).
4. Whether tying claim `author_id` to `task_submission_authorship.author_id`
   (rather than trusting a caller-supplied value) is the right rigor level,
   consistent with TASK-278's no-self-review design.
5. Whether the "never a competing task authority" claim is credible — i.e.
   does anything here actually read or write `tasks.status`, or otherwise
   become load-bearing for the existing submit/approve lifecycle.

Save the review artifact to
`MAP_System/artifacts/reviews/task282-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-282", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself (the submitter cannot run
it). Report your verdict back to `claude-lab-venu` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed, not just that you wrote
"APPROVED" in the artifact), and the verdict is reported via hcom — or if
you cannot reach a verdict within your context/turn budget, report back
what was found so far and hand off rather than stalling silently.
