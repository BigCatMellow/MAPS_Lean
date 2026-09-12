# Reviewer execution lineage — Stage 0 design

Status: `DESIGN READY FOR INDEPENDENT REVIEW — NO RUNTIME/SCHEMA CHANGE`

Parent: `work/tasks/reviewer-execution-lineage-design.md`.

Origin: `work/notes/2026-09-09-competitor-borrow-integration-log.md` Slice 04 identified that MAPS_L can prove review eligibility/freshness but does not mechanically bind a machine review decision to the execution that actually performed it.

## 1. Exact problem

Current MAPS_L distinguishes several important facts correctly:

```text
submission author
!=
reviewer_id

reviewer_id
!=
review subject

review subject
!=
reviewer execution
```

Today:

- `reviews` stores `reviewer_id`, verdict, summary, and timestamps;
- continuity links disqualify the submission author and continuation identities from independent review;
- `review_subjects` immutably binds what is reviewed: task, submission count, task revision, optional subject run, immutable artifact refs, freshness mode;
- repository `work/reviews/pr-*-review-evidence.md` binds a Git review artifact to an exact code head.

Those are useful controls. None proves which process/session/provider/model execution actually produced a machine review verdict.

The target is not “record more labels.” The target is:

```text
logical review claim R
+ trusted execution observation E made outside the reviewer's own payload
+ immutable R -> E binding
=> review provenance can state what actually executed the review
```

## 2. What current owners mean

### `reviews.reviewer_id`

Logical review principal. It is used for claim ownership and continuity-based independence checks. It is not a provider/session/model attestation.

### `review_subjects.run_id`

The run being reviewed/provenance of the reviewed subject. It is not the reviewer execution. Reusing this field for a reviewer run would collapse subject identity and reviewer identity into one ambiguous relation.

### `run_manifests`

Task execution bindings. `create_run_manifest()` requires the current `ACTIVE` claimant, AGI-ready task, task-bounded writable scope, and a task revision. Review occurs after submission while the task is `READY_FOR_REVIEW`.

Therefore a reviewer execution is not honestly a normal task run under the current contract. Relaxing run-manifest semantics just to fit review would widen a well-defined execution authority object.

### `continuity_links`

Evidence that identities share inherited execution context. It can disqualify independent review, but it does not itself identify the actual process/session/model that performed a review.

### Git review-evidence files

They bind the review artifact to the code head. The connected GitHub identity may be the same repository author identity for multiple agents, so the Git commit identity alone does not prove the independent execution that performed the review.

## 3. Rejected shortcuts

### A. Add `provider`, `model`, and `session_id` columns to `reviews`

Rejected as a first step.

If those values are supplied by the same reviewer command/payload that records the verdict, they are self-description, not evidence. The database would make an unverifiable claim look canonical.

### B. Treat a different model as independent

Rejected.

Different model/provider does not prove independent continuity; the same context may have been handed across. Conversely, two genuinely fresh executions of the same model can be independent. Model identity is provenance/telemetry, not the independence primitive.

### C. Require every review to have machine execution lineage

Rejected.

Human/manual review must remain representable without invented machine metadata. MAPS_L may later require machine-verifiable execution provenance for a specifically defined class of machine reviews, but absence of machine lineage must not make a real human review lie about having one.

### D. Reuse `review_subjects.run_id` for the reviewer execution

Rejected because it already means the subject run.

### E. Create reviewer `run_manifests`

Rejected under current semantics. A run manifest requires ACTIVE task ownership and execution scope; changing that contract would be a broader execution-lifecycle redesign.

## 4. Minimum trustworthy future contract

The first useful future object is conceptually a **review execution attestation**, not necessarily a new table yet.

Minimum fields/claims:

```text
execution_id              stable identity of the observed review execution
principal_id              actual logical principal observed by the trusted issuer
execution_kind            MACHINE | HUMAN/EXTERNAL where representable honestly
project_id                 project namespace if applicable
adapter/session identity   when a machine session exists
provider_id                optional provenance
model_id                   optional observed/effective model provenance
issuer                     trusted component/source that observed these facts
evidence_ref               immutable reference to the observation
observed_at                timestamp
```

A later immutable review link would bind:

```text
review_id -> execution_id
```

with a hard invariant:

```text
attested principal_id == reviews.reviewer_id
```

before the execution record is allowed to strengthen an independence claim.

Provider/model/session fields may enrich provenance but do not grant review authority and do not themselves establish independence.

## 5. Trust requirement

This is the critical design point.

An execution attestation only has evidentiary value when the relevant identity facts are observed by a component **outside the reviewer-controlled verdict payload**.

Acceptable future source classes include a harness/session launcher, orchestration composition root, or provider/session adapter that can observe the execution identity it actually invoked. The exact source must be selected and tested before persistence is added.

Insufficient sources include:

- `--reviewer-model gpt-x` supplied on the review CLI;
- a review summary saying which model/session was used;
- a reviewer-authored JSON blob containing its own identity;
- Git author identity when all agent writes are proxied through the same repository account;
- prompt/transcript text claiming independence.

A schema cannot manufacture trust that the source does not provide.

## 6. Independence semantics

Keep the current logical continuity rule. A future attestation strengthens it by proving which principal/session actually executed the review; it should not replace existing author/continuity checks.

Recommended order for a machine-verifiable review:

```text
review claim has reviewer_id R
-> trusted source observes execution E with principal R
-> immutable R/E binding recorded
-> current continuity checks still run on R
-> subject freshness/criterion/release checks still run
-> verdict may complete
```

If the trusted source observes principal `X` while the review is claimed by `R`, the execution evidence must be rejected as a mismatch rather than silently rewriting reviewer ownership.

A later design may use session-level continuity as an additional disqualifier once MAPS has a canonical mapping from observed review sessions into the continuity graph. Do not infer that mapping from names or timestamps.

## 7. Human/manual review

Human/manual review stays valid under the existing review contract unless a future task/policy explicitly requires machine-verifiable execution provenance.

The system should represent the distinction honestly:

```text
review is valid under current human/manual policy
execution provenance: NOT_MACHINE_ATTESTED / UNKNOWN
```

not:

```text
provider=human
model=human
session_id=human
```

Fake machine-shaped fields would make evidence quality worse.

## 8. First implementation proof

Do not start with SQLite migration.

First prove a **trusted producer** can emit a bounded immutable observation for a review execution without accepting the critical identity fields from the reviewer verdict payload.

Provider-free/fake-adapter proof shape:

```text
1. orchestration/harness starts or observes review execution E for principal R;
2. producer emits E with immutable execution_id + principal_id + session/provider/model provenance it observed;
3. caller attempts to relabel the review as principal X;
4. binding rejects principal mismatch;
5. unchanged attestation binds once to review R;
6. duplicate identical bind is deterministic/idempotent or explicitly duplicate;
7. changed attestation for the same review/execution is rejected;
8. current review subject and continuity behavior is unchanged.
```

Only after that producer exists should MAPS decide whether the persistence owner is:

- a narrow immutable `review_execution_links` relation plus an existing execution-attestation owner; or
- a small review-owned immutable attestation record if no generic execution owner exists and creating one would be unnecessary sprawl.

The implementation reviewer must challenge that choice against the then-current harness lineage model.

## 9. Enforcement staging

Do not immediately make missing execution provenance block every review.

Recommended stages:

1. **Producer proof** — trusted execution observation exists.
2. **Immutable binding** — a review can reference that observation; trace exposes it as provenance only.
3. **Mismatch enforcement** — if execution evidence is supplied, principal mismatch fails closed.
4. **Policy-gated requirement** — only a specifically authorized class of machine reviews requires verified execution provenance before approval.
5. **Operational exposure** — prove the requirement on real review traffic before claiming the gap closed broadly.

This avoids breaking human/manual review and avoids claiming more trust than the producer supplies.

## 10. Privacy/content boundary

Reviewer execution lineage should be structural and content-minimal.

Do not store by default:

- prompts;
- chain-of-thought;
- full transcripts;
- tool payloads;
- provider credentials;
- raw private messages.

The needed evidence is identity/provenance, not internal reasoning content.

## 11. Decision recommendation

`REAL GAP — DESIGN OWNER IDENTIFIED; IMPLEMENTATION BLOCKED ON TRUSTED PRODUCER`.

Recommended decision:

- preserve `reviews.reviewer_id` as logical review principal;
- preserve `review_subjects` as subject identity only;
- preserve `run_manifests` as task execution only;
- treat provider/model as provenance, not independence authority;
- keep human/manual review representable without fake lineage;
- require an externally observed execution attestation before adding any field that claims actual reviewer execution;
- then add the smallest immutable review-to-execution binding rather than a broad identity platform.

## 12. Next step after independent design review

Shape one bounded **trusted review-execution producer** task against the current Harness/orchestration composition root.

Do not implement a review schema migration until that task can identify a real source that observes the executor identity outside the reviewer-controlled verdict payload.

If no such source exists in the current architecture, record that as the blocker. Do not substitute self-attestation.
