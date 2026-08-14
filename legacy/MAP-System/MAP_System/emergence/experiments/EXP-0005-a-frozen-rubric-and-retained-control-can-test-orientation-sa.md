# Experiment Record

Experiment ID: EXP-0005
Project: MAP
Source idea: SYN-0002
Owner: codex-lab-lilo
Date: 2026-07-18
Status: COMPLETE

## Hypothesis

- hyp: A compact orientation treatment can retain all six fixed recovery facts—including the immediate read-before-mutate boundary—while using at least 50% fewer bytes than a retained point-in-time scenario control.

## Test

- test: Freeze a six-row rubric and full raw control before the treatment is written; independently construct a treatment for one new fixed scenario; give only treatment plus questions to a blinded evaluator; then verify every answer and exact byte counts against retained control content.

## Scope

- scope: Read-only experiment artifacts and bounded helper notes. The canonical startup path, MAP policy, task state, index behavior, and runtime remain unchanged.

## Limits

- limits: The control must retain complete point-in-time contents, including dynamic command output; static-source hashes supplement but never replace retained control content. This is one scenario-local comparison, not a claimed reduction of mandatory startup context.

## Success criteria

- pass: The evaluator passes all six rubric rows without guessing; the treatment explicitly separates the first required read from the later permitted mutation; exact `wc -w -c` shows at least 50% fewer treatment bytes than the retained scenario control; uncertainty and canonical references remain intact.

## Failure criteria

- fail: Any rubric row is missing, guessed, or unsafe; raw control cannot be reproduced/inspected; the reduction is below 50%; or the work requires a runtime/index/policy expansion to continue.

## Evidence to collect

- ev: `MAP_System/artifacts/experiments/orientation-manifest-post-evaluation-discovery-2026-07-18.md` admits this repeat and requires complete dynamic control retention.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md` records the prior partial read-before-mutate result and unreplayable control weakness.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md` retains the independently reverified 44,432-byte control.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md` is the compact treatment.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-refined-evaluation-2026-07-18.md` records six PASS rows and the independent byte measurement.

## Review path

- review: A helper freezes the rubric/control without reading any treatment; a distinct evaluator reads treatment after the control is frozen. The owner records the result; no experiment self-certifies a production change.

## Result

- result: pass. The distinct evaluator passed all six frozen rows without
  guessing. The treatment measured 312 words / 2,619 bytes against the
  retained 44,432-byte control, a 94.11% scenario-local reduction and below
  the 22,216-byte predeclared maximum.

## Decision

- [ ] adopt
- [ ] revise
- [ ] reject
- [x] park

## Notes

- note: Parked as bounded evidence rather than adopted as a system change.
  The pass validates one safe retrieval pattern only. It cannot authorize a
  manifest runtime, index behavior, task-state change, or MAP startup-policy
  change; a later proposal needs repeated evidence and mandatory-startup
  measurement.
