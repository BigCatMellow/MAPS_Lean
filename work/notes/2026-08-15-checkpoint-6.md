# Development checkpoint 6 — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

This supplements earlier handoff/checkpoint notes. Canonical code, active instructions, task/PR state, and reviewed/merged decisions remain authoritative.

## Operator direction still in force

- Continue downstream work while upstream draft PRs await independent review when the dependency is explicit and the next task does not require the review result.
- Keep stacked dependencies visible.
- CI success is evidence, not approval.
- Do not self-approve, mark ready, or merge review-gated work.
- Keep durable notes during long implementation sessions.

---

# Newly verified since checkpoint 5

## PR #32 — consequential review subject / evidence binding

Branch:

`agent/review-subject-binding-wave2`

Independent from merged `main`.

Initial implementation commit:

`1bf786995336a088e465028932720664dac699f7`

Corrective implementation commit:

`fde24736323cdd196309fb753422e053399e9171`

Task-validation head after CI:

`489a2524b513d6d9ab5eb186874cbc04e6e4ba4a`

Initial CI:

`31898581152` — failed in active tests.

Corrected CI:

`31898786757` — full Runtime stack success.

Task:

`work/tasks/review-subject-binding-wave2.md` → `READY_FOR_REVIEW`

### Implemented

- immutable one-to-one `review_subjects` attached to claimed reviews;
- snapshots:
  - task ID;
  - submission count;
  - task revision;
  - optional run ID;
  - immutable artifact/evidence refs;
  - freshness mode;
  - binder;
  - timestamp;
- v1 immutable artifact refs limited to:
  - `sha256:<64 hex>`
  - `git:<40/64 hex>`
- freshness modes:
  - `REVISION_BOUND`
  - `REDERIVED_AT_REVIEW`
  - `NON_CONSEQUENTIAL`
- consequential approval requires freshness evidence when existing canonical task data says the review is high-risk/operator-gated/destructive/external/security-sensitive/broad-architecture/operator-visible-release;
- low-risk/medium unflagged review keeps the existing simple path;
- subject rows are SQLite immutable;
- approval subject validation occurs inside the existing `ReviewMixin.record_review()` SQLite transaction;
- changed submission/task revision/stale run/criterion-vs-overall run or revision mismatch blocks approval;
- `REDERIVED_AT_REVIEW` requires exact matching immutable refs at final approval;
- trace includes the exact subject under the owning review;
- binding events do not dump artifact refs.

### Important CI-discovered design correction

The first implementation made review-subject validation run before existing criterion completeness validation. Existing high-risk criterion-mode behavior expected:

`CRITERION_VERIFICATION_INCOMPLETE`

but the new code returned:

`REVIEW_SUBJECT_REQUIRED`

This was not merely patched by changing the old test.

The corrected design now:

1. preserves existing criterion completeness failure precedence;
2. runs review-subject validation afterward inside the same transaction;
3. if consequential work has no explicit review subject but criterion mode is fully complete/confirmed, MAPS examines the **latest current claim for each criterion**;
4. when all latest confirmed claims identify the same non-null run and current task revision, MAPS atomically derives an immutable overall `REVISION_BOUND` subject from that evidence;
5. if criterion evidence is ambiguous, missing a run, or revision-inconsistent, MAPS does not derive a subject and consequential approval still requires an explicit immutable binding.

This avoids redundant reviewer ceremony while strengthening the exact-subject guarantee.

Critical invariant:

> A review subject identifies exactly what was reviewed. It does not grant reviewer authority, operator approval, task ownership, or capability.

---

# Current verified implementation inventory

CI-green, review-gated implementation tranches now exist for:

1. typed provider-neutral Harness contracts — PR #20;
2. hcom normalization + deterministic Hooks — PR #21;
3. HarnessService — PR #22;
4. canonical run/lease/session continuation guard — PR #23;
5. initial agentic adversarial security baseline — PR #24;
6. Agent Skills format/progressive loading — PR #25;
7. Skills catalog/provenance read model — PR #26;
8. frozen Skill-selection evaluation corpus — PR #27;
9. EnvironmentSpec v1 — PR #28;
10. EnvironmentFingerprint/compatibility v1 — PR #29;
11. append-only run-environment evidence + trace — PR #30;
12. static Skill quality/security gate — PR #31;
13. consequential review subject/evidence binding — PR #32.

All remain subject to their stated independent review gates.

---

# Deliberately unresolved boundaries

## Durable session lineage

Still unresolved:

- late session attachment;
- replacement session lineage;
- helper lineage joins;
- durable session/run reconciliation.

Do not create a hidden mutable second session authority.

## Skill approval/trust lifecycle

Still unresolved:

- approval authority;
- approval scope;
- review requirements;
- expiry/supersession;
- hash-change invalidation;
- persistent quarantine lifting.

`CLEAR` from PR #31 is not approval.

## Production Skill routing

PR #27 provides the frozen benchmark. Production routing remains unimplemented and promotion-gated.

## Environment-driven continuation/recovery

PRs #28–#30 provide environment requirements, observations, compatibility, and append-only run evidence. Compatibility remains evidence only.

## Review artifact registry

PR #32 intentionally accepts only already-immutable-looking refs (`sha256:` / `git:`). There is no general artifact registry or release-acquisition path yet.

---

# Next work: portable Run Record read model

Preferred next task:

Build a read-only portable Run Record over evidence already present in accepted `main`, while being explicit about missing draft-only/external sources.

Important design constraints:

- do not require PR #30 or #32 to be merged before beginning;
- branch independently from `main` unless a specific enrichment requires a stacked dependency;
- first version should aggregate existing canonical task/run/submission/review/criterion/outcome/event data;
- expose stable run/task revision, scopes, context hashes, review/outcome evidence, and coverage/completeness labels;
- do not copy task authority into a new writable store;
- do not claim hcom/helper/recovery/session lineage is complete when it is not;
- use explicit coverage states such as `VERIFIED`, `SOURCE_LOCAL`, `MISSING`, `UNKNOWN` where appropriate;
- output should be serializable/portable for future frozen regression cases;
- it should be a read model, not an event-sourced replacement for SQLite;
- later accepted Environment evidence / review-subject bindings can enrich the record through adapters/projections without changing its authority model.

Potential future bridge:

`real failure → portable Run Record → frozen regression case → harness candidate → comparative eval → reviewed promotion`
