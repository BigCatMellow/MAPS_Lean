# Task: comparative regression evaluator v1

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a deterministic, read-only comparative evaluator over frozen regression cases and externally produced property results, producing exact baseline-vs-candidate reports without executing models/tasks/providers or promoting a candidate.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #34 / `agent/frozen-regression-case-wave2`, `work/tasks/frozen-regression-case-wave2.md`, `work/tasks/portable-run-record-wave2.md`, Learning & Evaluation roadmap, Prime capability roadmap.
- Authoritative sources: exact frozen case artifacts and their validated case IDs/content hashes; externally supplied result artifacts are evaluation inputs only; canonical MAPS task/run/policy/review state remains authoritative elsewhere.
- Evidence labels: PR #34 current head/CI `VERIFIED`; evaluator behavior is `UNKNOWN` until focused tests and full Runtime stack CI pass.
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

- [ ] evaluator validates every frozen case `case_id` and `content_sha256` against the exact payload before scoring.
- [ ] externally produced property results support exactly `PASS`, `FAIL`, `UNKNOWN`, and `NOT_RUN`.
- [ ] results bind to exact case ID/hash and property ID; unknown cases/properties, duplicate results, hash mismatches, or malformed records fail explicitly.
- [ ] missing property results are reported as incomplete rather than silently converted to another outcome.
- [ ] report preserves case incident categories and tags.
- [ ] report aggregates property/case/corpus counts and completion/pass metrics without fake precision.
- [ ] exact baseline-vs-candidate comparison mechanically identifies `IMPROVED`, `REGRESSED`, `UNCHANGED`, and `INCOMPLETE` outcomes.
- [ ] comparison is only between the same exact frozen case ID/hash and expected property IDs.
- [ ] cost and latency are included only when explicitly measured in supplied results; absent measurements remain absent/unknown and are never inferred.
- [ ] report is deterministic for identical inputs and has an exact content hash/ID.
- [ ] implementation is model/provider agnostic and read-only.
- [ ] implementation does not execute tasks/models/providers, mutate canonical MAPS state, modify routing/harness/policy, create a second task/session/review authority store, or promote a candidate.
- [ ] report explicitly preserves the promotion path `frozen cases → candidate results → comparative report → proposal → independent review/operator gate where required → promotion` and rejects `better score → automatic production change` semantics.
- [ ] focused tests cover tampered cases, missing/duplicate/unknown results, all result states, aggregation, exact comparison classification, category/tag preservation, optional measured cost/latency, determinism, and authority/read-only boundaries.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: focused unit tests for the evaluator, then PR-triggered full Runtime stack CI on the exact branch head.
- Evidence to preserve: test output/CI run ID, exact implementation head, draft PR diff, independent review result.
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

## Completion / handoff

- Completed: task shaped and stacked branch created.
- Not completed: evaluator implementation, verification, draft PR, independent review.
- Current blocker: none.
- Next action if not DONE: implement the deterministic result/report schemas and focused tests.
