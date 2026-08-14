# Helper Assignment — EXP-0004 Baseline Evaluation

- Owner: codex-lab-lilo
- Helper tag: helper-review-steward-moku
- Status: COMPLETE
- Experiment: `EXP-0004`
- Objective: Independently evaluate the already-written orientation-manifest
  treatment against the canonical control and the discovery preflight. This is
  a baseline/exploratory evaluation, not proof that a generalized manifest
  should be adopted.

## Required reading

1. `MAP_System/emergence/experiments/EXP-0004-a-scoped-orientation-manifest-can-reduce-a-resumed-agent-s-conte.md`
2. `MAP_System/artifacts/experiments/orientation-manifest-canonical-control-2026-07-18.md`
3. `MAP_System/artifacts/experiments/orientation-manifest-control-treatment-2026-07-18.md`
4. `MAP_System/artifacts/experiments/orientation-manifest-discovery-preflight-2026-07-18.md`
5. Named canonical sources only where an answer needs verification.

## Evaluation protocol

- Treat the canonical-control answer record as frozen before the treatment was
  read. Do not change it.
- Score these separately, with PASS, PARTIAL, or FAIL and evidence:
  1. terminal/current task state and owner;
  2. immediate safe read before mutation;
  3. later permitted rework mutation and the five required findings;
  4. authority boundary;
  5. helper boundary;
  6. interruption recovery and live/durable availability uncertainty.
- Verify the treatment's stated 51,378-byte control and 5,653-byte treatment
  counts, calculate scenario-local reduction, and explicitly say that this is
  **not** a measured reduction of the mandatory startup contract.
- The preflight found that the baseline lacked a pre-frozen six-question rubric
  and a predeclared materiality threshold. Do not retrofit a confirmatory pass
  claim. Decide whether EXP-0004 should record `revise`, `reject`, or (only if
  justified despite the design gap) `park`; name the smallest next experiment.

## Required output

`MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md`

Include scoring table, exact missing/invented facts, measurement method,
preflight limitation, recommendation, and a concise owner-facing next step.

## Boundaries

- Read-only review; do not edit EXP-0004, treatment/control/preflight,
  tasks, policy, decision records, or canonical sources.
- Do not make an hcom request, promote an E/I record, or generalize the
  manifest into runtime/index work.
- Completion: reported `MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md` through hcom with verdict REVISE; returned to visible listening.
