# Experiment Record

Experiment ID: EXP-0004
Project: MAP
Source idea: SYN-0002
Owner: codex-lab-lilo
Date: 2026-07-18
Status: COMPLETE

## Hypothesis


- hyp: A scoped orientation manifest can reduce a resumed agent’s context load without losing the authority and safety facts needed for a correct first action.

## Test


- test: Build a read-only manifest for one fixed interrupted-task scenario, have an independent evaluator answer five routing questions from it before source verification, then compare correctness and measured bytes with the current required startup path.

## Scope


- scope: Experiment artifacts and helper notes only; no change to AGENTS, policy, task state, launch defaults, or canonical index behavior.

## Limits


- limits: The manifest is a test packet, not a new canonical source. Full canonical files remain available for verification. No authority or safety boundary may be omitted for compression.

## Success criteria


- pass: Evaluator identifies task state and owner, first valid action, decision boundary, helper visibility rule, and safe interruption recovery path; packet is materially smaller than the measured baseline.

## Failure criteria


- fail: Evaluator misses or guesses any authority, safety, current-state, or recovery fact; or compact packet does not materially reduce bytes.

## Evidence to collect

- ev: `MAP_System/artifacts/experiments/orientation-manifest-canonical-control-2026-07-18.md` froze the original five-answer canonical control before the treatment was read.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-control-treatment-2026-07-18.md` declared a 51,378-byte scenario-local control and a 5,653-byte treatment.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-discovery-preflight-2026-07-18.md` found that a frozen rubric, separate read/mutate action, and predeclared comparator were missing.
- ev: `MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md` independently scored PASS 5/6 and PARTIAL on immediate read-before-mutate; it verified 45,725 bytes / 89.00% stated scenario-local reduction but not startup-contract savings or the historical raw measurement.

## Review path

- review: `helper-review-steward-moku` wrote the independent baseline evaluation after producing the canonical control without reading the treatment.

## Result

- result: REVISE. The packet preserved task state, later rework, authority, helper, and interruption facts, but did not explicitly require the review/handoff read before the rework mutation. The baseline also lacked a six-row pre-frozen rubric, retained raw-control snapshot/hash, and predeclared threshold. The 89.00% figure is promising scenario-local arithmetic only, not proof of a safer or cheaper mandatory startup contract.

## Decision

- [ ] adopt
- [x] revise
- [ ] reject
- [ ] park

## Notes

- note: No runtime, index, AGENTS, policy, or task-state change follows from this result. A further test, if independently admitted, must use a new fixed scenario, frozen six-row rubric, retained/hashes control, predeclared at-least-50%-smaller scenario-local threshold, and blinded evaluator. The canonical startup path remains unchanged.
