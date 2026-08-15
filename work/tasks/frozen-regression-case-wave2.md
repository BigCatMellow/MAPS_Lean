# Task: frozen regression case v1

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a deterministic frozen regression-case artifact that references and embeds a validated portable Run Record plus explicitly triaged incident category, sanitized fixture, and expected-property IDs, without automatic classification, replay, promotion, or new authority state.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #33 / `agent/portable-run-record-wave2`, Learning & Evaluation roadmap incident taxonomy/frozen corpus requirements.
- Authoritative sources: canonical task/run evidence remains in source systems; the portable Run Record is a validated read model; frozen case is evaluation evidence only.
- Dependencies / preconditions: verified Run Record v1 implementation with full Runtime stack CI `31899074481`.

## Change boundary

- MAY CHANGE: new `runtime/evaluation/**`, stacked `runtime/cli.py` read-only case export command, focused regression-case tests, this task file.
- MUST NOT CHANGE: canonical SQLite schema/state, task/run/review/outcome authority, Run Record privacy/coverage semantics, provider/harness/recovery execution, external systems.
- MAY CHANGE IF NECESSARY: frozen case v1 artifact schema/taxonomy validation within this task.
- OPERATOR APPROVAL REQUIRED: automatic incident classification, automatic harness/policy/routing promotion, external publication, model/provider execution, or material scope expansion.

## Decision authority

- Owner may decide: incident taxonomy enum from roadmap, deterministic artifact identity, sanitized fixture bounds/checks, expected-property/tag ID syntax, Run Record integrity validation, and read-only CLI shape.
- Owner must escalate: any design that changes MAPS behavior after freezing, stores raw sensitive source material by default, infers an incident category without review, or treats case success as self-authorizing promotion.

## Acceptance criteria

- [ ] define the roadmap incident taxonomy as explicit enum values including tool/context/routing/helper/recovery/environment/review/validator/authority/ACI/supply-chain/operator-friction/unknown categories.
- [ ] `freeze_regression_case()` requires an explicit category, sanitized fixture, at least one structured expected-property ID, freezer identity, and optional structured tags.
- [ ] function revalidates embedded Run Record v1 record ID/content SHA against its payload before freezing.
- [ ] tampered or unsupported Run Record is rejected.
- [ ] Run Record partial-replay semantics are preserved; case cannot imply complete replay.
- [ ] sanitized fixture is bounded in size and rejected if the existing MAPS sensitive-text detector finds likely credential material.
- [ ] expected-property and tag identifiers are normalized/deterministic and reject free-form invalid IDs/duplicates.
- [ ] case embeds the already-sanitized Run Record so the artifact is portable/self-contained without changing Run Record privacy defaults.
- [ ] case explicitly states automatic promotion is false.
- [ ] case identity/content SHA is deterministic for identical reviewed inputs and contains no clock timestamp.
- [ ] no classification model, replay engine, evaluator, persistent corpus database, or MAPS behavior mutation is introduced.
- [ ] CLI `freeze-case` reads sanitized fixture from file or stdin rather than requiring it in shell arguments, emits JSON only, and does not mutate canonical state.
- [ ] focused tests cover tampering, sensitive fixture, taxonomy, identifier normalization, deterministic identity, JSON round trip, and CLI read-only behavior.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: `python -m unittest tests.test_frozen_regression_case -v` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: case-schema tests, Run Record tamper tests, privacy tests, PR diff, CI run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: verified portable Run Record v1 and standard library/local TaskStore only.
- Ordered procedure: taxonomy + case integrity → deterministic freeze artifact → CLI → focused tests → stacked draft PR → full CI → independent review.
- Failure branches: IF source material is not sanitized THEN reject freezing rather than copying it; IF incident category is uncertain THEN caller must choose `UNKNOWN` or triage it separately; IF replay/execution is needed THEN defer to later evaluation harness work.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: validated sanitized Run Record, explicit sanitized fixture, sensitive-text rejection, no raw source auto-copy, no external publication.
- External side effects: Git branch/PR publication only; CLI emits JSON to stdout.
- Effort limit: frozen case artifact v1 only; no corpus registry, incident classifier, comparative evaluator, or promotion workflow.
- Approved reference: Learning & Evaluation roadmap sections 5–7.

## Stop / escalate

Stop rather than guess if:

- freezing would require raw private/sensitive source text;
- incident classification would be automated without a reviewed classifier;
- a case artifact would become writable canonical task/policy state;
- case pass/fail would directly modify harness configuration.

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

- This task stacks on verified PR #33 so frozen cases can bind to stable Run Record identity while upstream review remains independent.
- The case embeds the Run Record rather than only referencing it, preserving portability without introducing a new database.
- `sanitized_fixture` is deliberately explicit. Run Record v1 omits free-text task prose by default; regression fixtures add only the reviewed text needed to reproduce/evaluate a specific incident.
- `frozen_by` and all semantic case inputs are included in the deterministic case hash; no timestamp is included, so identical frozen inputs remain identical artifacts.
- Incident taxonomy is not a classifier. The caller supplies the category after triage; `UNKNOWN` is valid when evidence is insufficient.
- Expected properties are stable IDs, not arbitrary prose. A later eval harness may map IDs to executable/property checks without changing this artifact format.
- `freeze-case --fixture-file` avoids placing sanitized incident text directly in shell history; `-` can be used for stdin.

## Completion / handoff

- Completed: implementation prepared on `agent/frozen-regression-case-wave2`.
- Not completed: commit/PR/CI/review.
- Current blocker: none.
- Next action if not DONE: update stacked CLI, open draft PR against `agent/portable-run-record-wave2`, and run full Runtime stack CI.
