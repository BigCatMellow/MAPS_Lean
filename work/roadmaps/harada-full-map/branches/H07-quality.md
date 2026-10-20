# H07 — Verification, revision-bound evidence, and independent review

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** none
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
MAPS_L and a genuinely independent reviewer can demonstrate **what changed, why it satisfies the accepted task, which revision was inspected and what happened afterward**, without promoting unverified completion claims.

## Recursive conditions
- **H07.1 — Acceptance before implementation.** Specific, testable criteria and risk-appropriate validation plan exist for every consequential task. **Proof:** reviewer can make pass/fail determination without inventing criteria.
- **H07.2 — Deterministic low-cost feedback.** Static analysis, syntax, unit/property tests and targeted integration checks run at the right boundary. **Proof:** representative bad mutation is caught and recoverable; link [H03.3](H03.3-validation.md).
- **H07.3 — No self-certification of substantive work.** One accountable owner, independent reviewer for medium/high risk, coherent review lenses. **Proof:** the same actor cannot launder its own review into accepted task truth.
- **H07.4 — Review exactly the right subject.** Bind artifact/hash, task revision, accepted base, feature and integrated heads; invalidate stale evidence. **Proof:** a changed revision requires revalidation or demonstrable equivalence.
- **H07.5 — Trace lineage and outcome.** Task, run, session, helper, environment, operation, submission, review, criteria and post-completion outcome remain linked; missing source is visible as UNKNOWN.
- **H07.6 — Operator-visible success and independent operation.** No hidden corrective work remains after DONE; documentation/handoff allows another operator to repeat safe work without reconstructing a chat.
- **H07.7 — Failing review repairs the bounded defect.** Keep observations separate from required changes; after correction inspect the new exact head. **Proof:** escape/regression rate improves, unnecessary process does not increase.

## Current status and relationships
Strong task/review, criterion evidence, Run Record, execution integrity and CI mechanisms exist in [runtime](../../../../runtime/README.md) and [checks and balances](../../../../docs/CHECKS_AND_BALANCES.md). This branch owns the **success condition**, not a new independent review or merge policy. Existing `AGENTS.md` and project role contracts govern review/merge.

## Plan
Choose a consequential representative task and an adverse changed-head case. Verify that acceptance, test and review remain correct through author changes, external contributions, integrations and resumed execution. Do not equate passing tests with independent judgment.
