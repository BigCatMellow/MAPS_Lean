# Regression evaluator checkpoint — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

Purpose: preserve exact continuation state for the comparative frozen-regression evaluator tranche without creating another authority store.

## Repository state recovered before implementation

- merged `main` head: `086e066f723d793273441dd52b500e62ac981deb`
- PR #34: `agent/frozen-regression-case-wave2` → `agent/portable-run-record-wave2`
- PR #34 current head when this tranche started: `f803cd24e5acbd3630075b3f316535ba50540b0b`
- PR #34 current-head Runtime CI: `31899450620` — success
- PR #34 remained draft with no review comments/reviews/threads; no material review-driven contract change blocked downstream implementation.

## Current stack

```text
main
  ↓
PR #33  portable Run Record v1
  ↓
PR #34  frozen regression case v1
  ↓
PR #35  comparative frozen regression evaluator v1
```

PR #35:

- branch: `agent/regression-evaluator-wave2`
- base: `agent/frozen-regression-case-wave2`
- implementation/test head before task/checkpoint documentation: `ac9ec15d34e57f37199dbefa4cad1ba31cd053c8`
- implementation Runtime stack CI: `31900484536` — success
- full unittest discovery: 139 tests passed, including all 7 `tests.test_regression_evaluator` cases
- task: `work/tasks/regression-evaluator-wave2.md`
- task state after implementation verification: `READY_FOR_REVIEW`
- PR remains **draft** and still requires independent review.

## Implemented evaluator contract

`runtime/evaluation/regression_case.py` now exposes exact frozen-case validation before evaluation.

`runtime/evaluation/evaluator.py` adds a model/provider-neutral read-only evaluator that:

- validates exact frozen `case_id` / `content_sha256` and embedded Run Record integrity;
- accepts externally produced property states only: `PASS`, `FAIL`, `UNKNOWN`, `NOT_RUN`;
- binds results to exact case hash and expected property ID;
- rejects unknown cases/properties, duplicate case results, hash mismatches, malformed states, and unknown measurement fields;
- reports missing property results explicitly as incomplete;
- preserves incident categories and tags;
- aggregates integer case/property counts and numerator/denominator fractions;
- produces deterministic report/corpus IDs and SHA-256 identities;
- compares baseline and candidate only over the same exact frozen corpus;
- classifies property comparison as `IMPROVED`, `REGRESSED`, `UNCHANGED`, or `INCOMPLETE`;
- keeps a case incomplete if either side lacks concrete comparable evidence for any expected property;
- records cost/latency only when explicitly supplied as measured values and computes comparison deltas only for paired measured cases.

## Authority boundary

The evaluator is evidence only. It does not:

- execute a task, model, provider, Skill, Hook, harness adapter, or recovery operation;
- mutate canonical task/run/review/policy state;
- modify routing/harness/policy configuration;
- create a second task/session/review/corpus authority store;
- promote a candidate.

Required path remains:

```text
frozen cases
→ candidate results
→ comparative report
→ proposal
→ independent review/operator gate where required
→ promotion
```

Never:

```text
better score → automatic production change
```

## Preserved invariants

- one authority per fact;
- capability is not authority;
- session liveness is not task truth;
- Hooks can narrow/block but cannot grant task/operator authority;
- consequential review binds exact/fresh evidence;
- environment compatibility is evidence only;
- `CLEAR` Skill scan is not approval;
- partial Run Records/frozen cases do not claim complete replay;
- evaluation success cannot self-authorize promotion;
- no second task/session/review authority store.

## Verification already completed

Runtime stack CI `31900484536` passed on implementation head `ac9ec15d34e57f37199dbefa4cad1ba31cd053c8`:

- legacy dependency gate: pass
- compile: pass
- Ruff fatal checks: pass
- Bandit medium/high: pass
- dependency consistency: pass
- full unittest discovery: 139 passed / 0 failed
- all 7 new evaluator tests: pass
- LangGraph disposable smoke: pass
- installer syntax/preview: pass

A final PR-triggered Runtime run should be checked on the documentation/current head after this checkpoint. A green run does not satisfy independent review and must not change the PR out of draft.

## Continuation

Immediate next action:

1. verify final current-head Runtime stack CI for PR #35;
2. leave PR #35 draft at `READY_FOR_REVIEW`;
3. independent review is the completion gate.

If upstream review later changes PR #34 frozen-case identity or semantics materially, propagate those changes through PR #35 before merge. Do not heuristically reconcile mismatched case/property identities.
