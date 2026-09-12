# Task: reviewer execution lineage design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: orchestration operator
- Risk: `MEDIUM`
- Goal: define the smallest trustworthy contract that can bind a canonical review to the execution that actually performed it without turning caller-supplied labels into false proof.
- Parent roadmap: `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md` — H6 lineage/trace principles, within the operator-approved reviewed-gap sequence begun 2026-09-09.
- Related records: `work/notes/2026-09-09-competitor-borrow-integration-log.md` Slice 04; `docs/CHECKS_AND_BALANCES.md`; PR #326.
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `runtime/state/review.py`, `runtime/state/review_binding.py`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, `runtime/flow_review.py`, `docs/CHECKS_AND_BALANCES.md`, `work/notes/2026-09-09-competitor-borrow-integration-log.md`.
- Authoritative sources: `AGENTS.md` > approved roadmap/operator objective > this task > current runtime/schema.
- Evidence labels: current runtime/schema findings are `VERIFIED`; future attestation-source mechanics are `PROPOSED` until implemented and exercised.
- Dependencies / preconditions: PR #335 may remain independently review-complete but unmerged; this design does not depend on its runtime delta and must not edit its paths.

## Change boundary

- MAY CHANGE: this task record; `work/notes/2026-09-10-reviewer-execution-lineage-design.md`; PR metadata/comments for this design.
- MUST NOT CHANGE: runtime code; SQLite schema; review approval behavior; review-evidence workflow; `run_manifests`; `review_subjects`; capability status; provider/hcom behavior; PR #335.
- MAY CHANGE IF NECESSARY: one additional bounded design record only if independent review identifies a missing design fact that cannot fit the owning note.
- HUMAN REAUTHORIZATION REQUIRED: any change that weakens existing review independence, changes human-review eligibility, creates external/provider authority, or materially expands beyond reviewer execution provenance.

## Decision authority

- Inherited roadmap authority: operator instruction to proceed through the recommended reviewed-gap order, with reviewer execution lineage second.
- Owner may decide: design distinctions, trust boundary, non-goals, staged implementation recommendation, and smallest future proof.
- Resolve internally first: whether current review/run/session owners can represent the needed fact without semantic overloading.
- Human escalation only if: future implementation requires a materially broader identity/credential trust system or changes which human/manual reviews are allowed.

## Acceptance criteria

- [x] Distinguish logical `reviewer_id`, immutable review subject, and actual reviewer execution provenance.
- [x] Determine whether `review_subjects.run_id` or `run_manifests` can honestly represent reviewer execution without semantic overloading.
- [x] State what evidence may and may not prove reviewer independence.
- [x] Preserve human/manual review without fabricating machine lineage.
- [x] Define a minimum future machine-review execution-attestation contract and its trust requirement.
- [x] Define the first implementation proof and explicit stop conditions before schema/runtime work.
- [x] Avoid schema/runtime changes in the design lane.

## Verification and evidence

- Verification: direct inspection of current review claim/record flow, review-subject binding, run-manifest creation rules, continuity semantics, and repository review-evidence contract.
- Evidence to preserve: `work/notes/2026-09-10-reviewer-execution-lineage-design.md` plus exact PR diff.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository design only.
- Ordered procedure: current owner recovery -> semantic-gap audit -> rejected shortcuts -> minimum trust contract -> staged implementation boundary -> independent review.
- Failure branches: if no trusted non-reviewer-controlled source can attest actual execution identity, do not add a schema field that pretends caller-supplied provider/model/session text is proof.
- Rollback / recovery: docs-only branch can be revised or closed without runtime migration.
- Security / privacy controls: record structural identity/provenance only; do not require prompts, transcripts, hidden reasoning, or raw provider payloads.
- External side effects: GitHub design PR only.
- Effort limit: one owning design note; no generic identity platform.
- Approved reference: existing review-subject and run-lineage separation in current MAPS_L.
- Operational independence: `N/A — architecture design, not a repeatable operational procedure`.
- Reproduction package: direct file paths and falsifiable future proofs are in the design note.

## Question-resolution ladder

Current authoritative code and schema were inspected before proposing any new record. The design deliberately stops before implementation where the missing fact requires a trusted execution-attestation source rather than another label.

## Stop / escalate

Stop this design lane if the proposal would:

- redefine `run_manifests` to include non-ACTIVE review executions;
- overload `review_subjects.run_id` as the reviewer run;
- treat provider/model/session strings supplied by the reviewer as machine proof;
- make model difference itself an independence criterion;
- make human/manual review require fake machine execution metadata;
- introduce credentials/cryptographic identity or a broad generic actor-identity platform.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

The design recommendation is intentionally narrower than “store model/provider on reviews.” The source-trust problem must be solved first; otherwise the extra fields only make unverified self-description look authoritative.

## Completion / handoff

- Completed: current-state audit and Stage-0 design shaped for independent review.
- Not completed: runtime/schema implementation; trusted attestation source; enforcement.
- Triage capture: none — no new §2 friction signal specific to this task.
- Reproduction package: see owning design note.
- Current blocker: implementation must not begin until independent review accepts the trust boundary and a concrete trusted attestation source is selected.
- Next eligible roadmap task: after design approval, shape the smallest execution-attestation producer/proof; then reviewer linkage only if that producer is real.
- Human action required: none at design stage.
