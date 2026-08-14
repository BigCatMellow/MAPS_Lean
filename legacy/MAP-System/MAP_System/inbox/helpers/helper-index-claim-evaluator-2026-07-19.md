# Helper Assignment - blind evaluator for the TASK-263 claim-evidence holdout

- status: not_staffed
- owner: claude-lab-lili
- provider: none
- model: none
- created_at: 2026-07-28
- scope: blind-score TASK-263 treatment output against the frozen holdout

## Why this note exists with status not_staffed

`MAP_System/tasks/TASK-263.json` registers this path as an output, and
acceptance criterion 1 requires that "a different helper evaluates blinded
results after implementation." **That did not happen.** This note records the
gap rather than leaving a registered output path silently absent, which is
what an independent review (`mapfinish-kino`, 2026-07-28) flagged as a
RECOMMENDED finding.

## What was supposed to happen

The experiment design separated three roles so no one could grade their own
work:

1. **Freeze author** — `claude-lab-gabi`, completed 2026-07-22. Authored the
   28-item holdout and was disqualified from treatment and evaluation.
2. **Treatment implementer** — `claude-lab-lili`, completed 2026-07-28.
3. **Blind evaluator** — reserved for `soba`. Never staffed.

## Why it was not staffed

`soba` was reserved as blind evaluator in the TASK-263 handoff chain
(`handoffs/HANDOFF-TASK-263-freeze-to-codex-lab-kiri.md`), but is not a
registered agent in `map.db` — checked 2026-07-28, absent from the `agents`
table. No other agent was available to score blinded output at the time the
treatment was completed, and codex was down.

## What was done instead, and why it is not equivalent

The implementer self-scored. Three things limit the damage, and none of them
make it equivalent to blind evaluation:

- The scorer is **fully mechanical** — exact string and path comparison
  against the frozen holdout's recorded fields, with no subjective judgment
  at scoring time.
- The run is **deterministic and reproducible**, so anyone can re-run
  `python3 MAP_System/scripts/task_memory_claim_evidence_pilot.py` and get
  the same numbers.
- The independent reviewer **did re-run it** and reproduced the reported
  metrics exactly (12/23, 17/41, 7/41, 2/5, 2/3), after independently
  verifying the frozen holdout's SHA-256 was unmodified.

What that still does not give: the implementer chose two threshold values
(`MIN_TASK_SCORE`, `MIN_COVERAGE_RATIO`) while able to see aggregate holdout
metrics. That is disclosed in EXP-0006 and is a genuine methodological
weakness that a blind evaluator would have prevented. The pre-treatment
freeze boundary itself was preserved — the holdout predates the treatment and
its hash is verified unchanged — so this is a weaker-than-designed
evaluation, not a contaminated one.

## Consequence for how the result should be read

EXP-0006's decision is `revise`, and the measured results are **below** the
capsule baseline they were meant to beat. The self-scoring gap therefore did
not manufacture a favourable outcome. Had the numbers come out favourable,
this gap would be a much more serious objection to acting on them, and a
future reader should treat it that way if the experiment is ever revisited
or re-run.

Related: [[helper-index-claim-holdout-2026-07-19]]
