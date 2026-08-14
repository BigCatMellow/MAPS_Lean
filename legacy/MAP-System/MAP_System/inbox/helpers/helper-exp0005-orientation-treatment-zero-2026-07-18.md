# Helper Assignment — EXP-0005 Compact Orientation Treatment

- Owner: codex-lab-lilo
- Helper: helper-discovery-clearfront-zero
- Status: COMPLETE
- Experiment: EXP-0005
- Role: treatment author only; not evaluator or decision-maker

## Objective

Create one compact recovery-orientation treatment for the frozen EXP-0005
scenario. It must preserve the six fixed facts while being materially smaller
than the retained 44,432-byte raw control.

## Required reads

1. MAP_System/emergence/experiments/EXP-0005-a-frozen-rubric-and-retained-control-can-test-orientation-sa.md
2. MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md

Read the rubric, sources, and the Facts that cannot be lost section. Do not
copy, transform, or rely on the attached Base64 raw-control packet as treatment
content.

## Required output

Write only:

MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md

The treatment must contain:

1. a concise current-state statement for TASK-227 and TASK-220;
2. the exact first required read-before-mutate instruction;
3. the later permitted rework path and all-five-findings constraint;
4. authority and helper boundaries;
5. the live/durable availability uncertainty without inventing a resolution;
6. canonical source pointers for each item;
7. a wc -w -c result for the treatment and the explicit 50%-fewer-than-44,432
   byte threshold check.

## Boundaries

- Do not change a task, policy, index, runtime, current state, decision, or
  any file other than the one output above.
- Do not run a model, launch a helper, or contact the operator.
- Do not evaluate or claim that the treatment passes the frozen rubric.
- Do not select a production change. This is one experiment artifact.

## Completion

Send one hcom inform to @codex-lab-lilo with output path, byte count, and
threshold result. Then return to listening. A distinct helper will evaluate
the treatment.

## Outcome

- Output: MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md
- Measurement: 312 words, 2,619 bytes.
- Threshold: PASS for the size requirement only (2,619 <= 22,216 bytes).
- No rubric, production, or startup-policy decision was claimed.
