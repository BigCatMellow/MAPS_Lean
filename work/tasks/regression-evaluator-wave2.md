# Task: comparative regression evaluator v1

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a deterministic, read-only comparative evaluator over frozen regression cases and externally produced property results, producing exact baseline-vs-candidate reports without executing models/tasks/providers or promoting a candidate.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #34 / `agent/frozen-regression-case-wave2`, `work/tasks/frozen-regression-case-wave2.md`, `work/tasks/portable-run-record-wave2.md`, Learning & Evaluation roadmap, Prime capability roadmap.
- Authoritative sources: exact frozen case artifacts and their validated case IDs/content hashes; externally supplied result artifacts are evaluation inputs only; canonical MAPS task/run/policy/review state remains authoritative elsewhere.
- Evidence labels: PR #34 current head/CI `VERIFIED`; evaluator implementation and Runtime CI `VERIFIED`; independent review `PENDING`.
- Dependencies / preconditions: PR #34 head `f803cd24e5acbd3630075b3f316535ba50540b0b`; PR remains draft/review-gated and no upstream review has materially changed its contracts.

## Change boundary

- MAY CHANGE: `runtime/evaluation/**`, focused evaluator tests, this task file, minimal read-only CLI/docs only if needed to exercise/export the report.
- MUST NOT CHANGE: canonical SQLite schema/state, task/session/review authority, harness/routing/policy behavior, provider/model execution, candidate promotion, PR #34 review state.
- MAY CHANGE IF NECESSARY: evaluator/result/report v1 schema inside this task after amending this record.
- OPERATOR APPROVAL REQUIRED: automatic task/model/provider execution, automatic routing/harness/policy mutation, candidate promotion, new persistent authority/state store, or material scope expansion.

## Decision authority

- Owner may decide: strict input/result/report schema, deterministic IDs/hashes, aggregation formulas, comparison classification rules, validation/error behavior, and bounded optional measured cost/latency fields.
- Owner must escalate: any design that executes evaluations itself, infers missing results as success/failure, treats evaluation evidence as authority, or allows a better score to directly change production behavior.

## Acceptance criteria

- [x] evaluator validates every frozen case `case_id` and `content_sha256` against the exact payload before scoring.
- [x] externally produced property results support exactly `PASS`, `FAIL`, `UNKNOWN`, and `NOT_RUN`.
- [x] results bind to exact case ID/hash and property ID; unknown cases/properties, duplicate results, hash mismatches, or malformed records fail explicitly.
- [x] missing property results are reported as incomplete rather than silently converted to another outcome.
- [x] report preserves case incident categories and tags.
- [x] report aggregates property/case/corpus counts and completion/pass metrics without fake precision.
- [x] exact baseline-vs-candidate comparison mechanically identifies `IMPROVED`, `REGRESSED`, `UNCHANGED`, and `INCOMPLETE` outcomes.
- [x] comparison is only between the same exact frozen case ID/hash and expected property IDs.
- [x] cost and latency are included only when explicitly measured in supplied results; absent measurements remain absent/unknown and are never inferred.
- [x] report is deterministic for identical inputs and has an exact content hash/ID.
- [x] implementation is model/provider agnostic and read-only.
- [x] implementation does not execute tasks/models/providers, mutate canonical MAPS state, modify routing/harness/policy, create a second task/session/review authority store, or promote a candidate.
- [x] report explicitly preserves the promotion path `frozen cases → candidate results → comparative report → proposal → independent review/operator gate where required → promotion` and rejects `better score → automatic production change` semantics.
- [x] focused tests cover tampered cases, missing/duplicate/unknown results, all result states, aggregation, exact comparison classification, category/tag preservation, optional measured cost/latency, determinism, and authority/read-only boundaries.
- [x] focused evaluator tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: implementation head `ac9ec15d34e57f37199dbefa4cad1ba31cd053c8` passed PR-triggered Runtime stack CI run `31900484536`; full discovery ran 139 tests with all 7 `test_regression_evaluator` tests passing, plus compile, Ruff fatal checks, Bandit, dependency consistency, LangGraph smoke, and installer syntax/preview.
- Evidence to preserve: test output/CI run `31900484536`, exact implementation head, draft PR #35 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: Python runtime/standard library plus existing frozen regression-case module; no provider access.
- Ordered procedure: validate frozen case contract → define external result schema → aggregate single candidate → exact baseline/candidate comparison → focused tests → draft stacked PR → full Runtime stack CI → durable checkpoint.
- Failure branches: IF a required property result is absent THEN mark report incomplete; IF case identity/hash/property set differs THEN reject comparison; IF cost/latency lacks explicit measurement THEN omit/unknown rather than estimate.
- Rollback / recovery: revert isolated stacked branch/PR; no schema/data migration.
- Security / privacy controls: consume only already-sanitized frozen cases plus structured result metadata; do not add raw prompt/task/provider transcript fields.
- External side effects: Git branch/commits/draft PR and GitHub Actions only.
- Effort limit: comparative evaluation/reporting v1 only; no evaluator execution engine, proposal authorizer, production selector, or persistent corpus authority.
- Approved reference: Learning & Evaluation roadmap sections 7–9, 16, 19, 21 plus Prime no-self-authorizing-refinement rule.

## Stop / escalate

Stop rather than guess if:

- an upstream review materially changes PR #34 frozen-case identity/contracts;
- comparison would require joining non-identical case/property identities heuristically;
- a requested metric requires inferred cost/latency or untrusted free-form data;
- evaluation output would become production authority or automatically change routing/harness/policy.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task intentionally stacks on PR #34 while upstream review remains independent; the dependency is exact and implementation does not require the review result.
- Evaluation success is evidence only. The evaluator may classify comparison results but cannot authorize promotion.
- Missing data stays incomplete/unknown; the layer must not manufacture certainty.
- Aggregate fractions retain numerator/denominator counts rather than presenting unjustified statistical precision.
- A case with any missing/`UNKNOWN`/`NOT_RUN` property is `INCOMPLETE`; an exact comparison likewise remains incomplete where either side lacks a concrete `PASS`/`FAIL` result.
- Cost/latency comparison uses only paired explicit measurements. No estimate is derived for absent data.

## Completion / handoff

- Completed: exact frozen-case validation, externally supplied property-result validation, deterministic case/corpus reporting, exact baseline-vs-candidate comparison, optional measured cost/latency reporting, focused tests, draft PR #35, and successful Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion.
- Next action if not DONE: independently review PR #35; do not mark ready or merge merely because CI is green.
