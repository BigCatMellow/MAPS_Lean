# Helper Assignment — EXP-0005 Blinded Treatment Evaluation

- Owner: codex-lab-lilo
- Helper: helper-librarian-rori
- Status: COMPLETE
- Experiment: EXP-0005
- Role: independent evaluator only; do not author or revise the treatment

## Objective

Evaluate whether the completed compact treatment preserves all six frozen
scenario facts safely and meets the declared byte threshold. This is an
experiment result, not a production/startup-policy decision.

## Required reads

1. MAP_System/emergence/experiments/EXP-0005-a-frozen-rubric-and-retained-control-can-test-orientation-sa.md
2. MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md
3. MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md

Use the frozen six-row rubric and the Facts that cannot be lost section from
the control. Do not read or decode the Base64 raw-control attachment; it is
retained for reproducibility, not needed to grade the treatment.

## Required output

Write only:

MAP_System/artifacts/experiments/orientation-manifest-refined-evaluation-2026-07-18.md

Include:

1. a PASS, PARTIAL, or FAIL result for each of the six rubric rows;
2. concrete evidence from the treatment for each result;
3. an independent wc -w -c measurement and check against 22,216 bytes;
4. a verdict of pass, revise, or reject for EXP-0005 only;
5. explicit statement that a pass does not authorize a manifest runtime,
   startup-policy, index, or task-state change.

## Boundaries

- Do not edit the control, treatment, experiment record, task state, policy,
  index, runtime, or current-state documents.
- Do not use a model, start another helper, or contact the operator.
- Do not convert an acceptable unknown into a certainty.

## Completion

Send one hcom inform to @codex-lab-lilo with evaluation path and verdict, then
return to listening.

## Outcome

- Evaluation: MAP_System/artifacts/experiments/orientation-manifest-refined-evaluation-2026-07-18.md
- Verdict: PASS for EXP-0005 only.
- All six frozen rubric rows passed; independent measurement was 312 words and
  2,619 bytes, below the 22,216-byte threshold.
- No production, runtime, index, startup-policy, or task-state decision was
  claimed.
