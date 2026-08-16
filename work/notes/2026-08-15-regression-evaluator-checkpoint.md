# Regression evaluator checkpoint — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

Purpose: preserve exact continuation state for the comparative frozen-regression evaluator tranche without creating another authority store.

## Repository state recovered before implementation

- merged `main` head: `086e066f723d793273441dd52b500e62ac981deb`
- PR #34: `agent/frozen-regression-case-wave2` → `agent/portable-run-record-wave2`
- PR #34 head when this tranche started: `f803cd24e5acbd3630075b3f316535ba50540b0b`
- initial PR #34 Runtime CI: `31899450620` — success
- PR #34 was draft and had no upstream review changes when evaluator implementation began.

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
- task: `work/tasks/regression-evaluator-wave2.md`
- task state: `READY_FOR_REVIEW`
- PR remains **draft** and still requires independent review.

## Implemented evaluator contract

`runtime/evaluation/regression_case.py` exposes exact frozen-case validation before evaluation.

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

## Review remediation propagated after implementation

A later review pass found four root issues elsewhere in the open stacks. The relevant frozen-case issue was material to PR #35 and was propagated rather than ignored.

PR #34 now includes the complete initial Learning/Evaluation incident taxonomy, including the previously omitted:

- `RUNAWAY_LOOP`
- `SKILL_PROCEDURE_ERROR`
- `SECURITY_BOUNDARY_FAILURE`

A taxonomy regression test now locks the exact initial set. Corrected PR #34 head before this checkpoint update:

- head: `aca786cf1af71a38c453f9aa2d69998b492ea4bc`
- Runtime CI: `31901219722` — success

PR #35 explicitly merged that corrected #34 head and preserved evaluator validation over the expanded enum. Corrected PR #35 head before this checkpoint update:

- head: `6f48c0fabd8b15b70f08b37b1e077cce51e0653b`
- Runtime CI: `31901459957` — success

Other review-remediation stacks were also corrected and green before this checkpoint:

- Harness/Security #21 → #24: recursive Hook-context immutability prevents an earlier Hook from rewriting identity observed by a later canonical guard; #24 includes an adversarial authority-bypass regression. Current-head Runtime CI passed across #21/#22/#23/#24.
- Environment #29 → #30: dependency inputs that resolve outside the repo or traverse symlinks are rejected before probes/reads; direct module imports receive the same guarded implementation. Current-head Runtime CI passed for #29/#30.
- Skill gate #31: complete frontmatter/custom metadata is included in static security assessment; authority claims in metadata quarantine, benign custom metadata requires review, and direct module imports receive the same hardened implementation. Current-head Runtime CI passed.

These fixes do not change the evaluator authority model.

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

## Verification history

Initial implementation Runtime stack CI `31900484536` passed on `ac9ec15d34e57f37199dbefa4cad1ba31cd053c8` with 139 tests, including all 7 evaluator-focused tests.

Initial documentation/current-head Runtime CI `31900576771` passed on `b5522d91b31b966197b05a6a600a83469e9ca38f`.

After review remediation and #34 taxonomy propagation, Runtime CI `31901459957` passed on PR #35 head `6f48c0fabd8b15b70f08b37b1e077cce51e0653b`.

A final PR-triggered Runtime run must be checked on the new documentation head created by this checkpoint update. A green run is mechanical evidence only and does not satisfy independent review.

## Continuation

Immediate next action:

1. verify final current-head Runtime stack CI for PR #35 after this checkpoint commit;
2. leave PR #35 draft at `READY_FOR_REVIEW`;
3. obtain genuinely independent review before any review-gated promotion/merge.

If future upstream review changes frozen-case identity or semantics materially, propagate those changes through PR #35 before merge. Do not heuristically reconcile mismatched case/property identities.
