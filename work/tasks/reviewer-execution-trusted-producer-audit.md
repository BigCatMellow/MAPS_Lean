# Task: audit trusted reviewer-execution producer

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: MAPS orchestration operator
- Risk: `MEDIUM`
- Goal: Determine whether current MAPS_L has a trustworthy producer that can observe a machine reviewer execution outside the reviewer-controlled verdict payload, and identify the smallest honest next gate.
- Parent roadmap: operator-approved reviewed-gap sequence; item 2, reviewer execution lineage
- Related records: PR #336 (`Design trusted reviewer execution lineage`, reviewed design head `98681be136237e6dbbd2128825785bc50a22306d`); [competitor borrow-integration log](../notes/2026-09-09-competitor-borrow-integration-log.md); [independent-review enforcement design](../notes/2026-08-17-independent-review-enforcement-design.md); [research result](../research/2026-09-10-reviewer-execution-trusted-producer-audit.md)
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: current `reviews` / `review_subjects` / continuity / run-manifest semantics; review-evidence workflow/checker contract; browser-agent coordination; hcom session observation; environment fingerprints; current GitHub identity limitation.
- Authoritative sources: `AGENTS.md`; accepted `main`; current runtime/workflow code; accepted coordination rules; live GitHub state.
- Evidence labels: repository/runtime observations are `VERIFIED`; existence of any provider-side attestation API not integrated into MAPS is `UNKNOWN` and is not assumed.
- Dependencies / preconditions: Stage-0 design in PR #336 must be independently reviewed before this result is used to justify implementation. That review is reported APPROVED at exact design head `98681be...306d` with evidence-only tip `826d487e...7d7`.

## Change boundary

- MAY CHANGE: this task record; one bounded research brief; PR metadata/comments.
- MUST NOT CHANGE: runtime code, SQLite schema, review policy, review-evidence workflow/checker behavior, provider adapters, hcom behavior, capability status, authority, or PR #336.
- MAY CHANGE IF NECESSARY: additional research-only evidence inside this branch if a missing source materially changes the conclusion.
- HUMAN REAUTHORIZATION REQUIRED: new credentials/identity provisioning, provider/platform integration requiring access not already available, or any material expansion beyond the approved reviewer-lineage objective.

## Decision authority

- Inherited roadmap authority: investigate and shape the next bounded reviewer-lineage step without inventing untrusted provenance.
- Owner may decide: whether current MAPS surfaces satisfy the Stage-0 trusted-producer predicate; what evidence is sufficient to classify a source as trusted, self-attested, orthogonal, or unavailable.
- Resolve internally first: code/workflow/coordination inspection; historical design evidence; exact current behavior.
- Human escalation only if: the next valid step requires new credentials, external account/App provisioning, paid access, or another boundary outside current authority.

## Acceptance criteria

- [x] Enumerate current plausible observation sources rather than assuming a producer exists.
- [x] Distinguish exact-head evidence binding, GitHub actor identity, hcom session facts, environment facts, task-run lineage, and actual reviewer execution identity.
- [x] Reject reviewer-controlled labels/trailers as proof unless an independent issuer validates them.
- [x] Determine whether any current source can bind `execution_id -> reviewer principal` outside the reviewer verdict payload.
- [x] Preserve `UNKNOWN` where provider/platform facts are not exposed to current MAPS integration.
- [x] Identify the smallest next engineering gate without adding schema or a generic identity platform.

## Verification and evidence

- Verification: direct read of `runtime/state/review.py`, `runtime/state/review_binding.py`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, `runtime/environment/fingerprint.py`, `runtime/communication/hcom_adapter.py`, `.github/workflows/review-evidence.yml`, `docs/CHECKS_AND_BALANCES.md`, `work/coordination/README.md`, `work/coordination/GITHUB_ASYNC_WORK_PULL.md`, `work/coordination/agents/SENTINEL.md`, and `work/notes/2026-08-17-independent-review-enforcement-design.md` on accepted `main@7dfcbd09a2df930ee3449ce047984e4da5cec460`.
- Evidence to preserve: [research result](../research/2026-09-10-reviewer-execution-trusted-producer-audit.md) and exact PR head.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: accepted repository state plus live GitHub review workflow.
- Ordered procedure: recover Stage-0 invariant -> inspect every plausible existing producer -> classify trust -> stop before implementation if none satisfies the invariant.
- Failure branches: IF no trusted producer exists THEN record `BLOCKED_ON_TRUSTED_PRODUCER` for implementation and do not add lineage schema. IF one exists THEN design a producer-first executable proof before schema.
- Rollback / recovery: docs-only branch; close or amend if review finds the evidence classification wrong.
- Security / privacy controls: no secrets, transcripts, hidden chain-of-thought, raw prompts, or provider credentials collected.
- External side effects: GitHub branch/PR evidence only.
- Effort limit: bounded to existing MAPS integration surfaces; no broad vendor survey.
- Approved reference: PR #336 Stage-0 invariant.
- Operational independence: `N/A — one-time architecture audit; future implementation must satisfy its own operational-independence gate.`
- Reproduction package: read the listed accepted-main files and check whether any source can independently prove both stable execution identity and logical reviewer principal for a browser/machine review.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Result: current MAPS_L has **no trusted producer** that satisfies the Stage-0 execution-attestation predicate for browser reviewer executions.
- This is not evidence that provider platforms cannot expose such provenance; it means the current MAPS integration does not receive or validate it.
- A second GitHub identity/App can strengthen GitHub actor identity but is not, by itself, proof of which model/process performed the review.
- Do not create a `review_execution_*` table merely to store self-reported model/provider/session labels.

## Completion / handoff

- Completed: current producer surfaces audited; implementation precondition classified.
- Not completed: trusted execution producer implementation; review-to-execution binding; any schema migration.
- Triage capture: `none — no Repair-and-Learning friction trigger fired during this bounded audit.`
- Reproduction package: listed source inspection + research classification table.
- Current blocker: `BLOCKED_ON_TRUSTED_PRODUCER` for reviewer-execution lineage implementation.
- Next eligible roadmap task: design/prove a MAPS-controlled or independently issued reviewer-execution attestation producer; if that requires new external credentials/access, stop that branch and continue item 3 of the operator-approved gap sequence.
- Human action required: `none now`; only required if a chosen producer needs new credentials/account/App/provider access.