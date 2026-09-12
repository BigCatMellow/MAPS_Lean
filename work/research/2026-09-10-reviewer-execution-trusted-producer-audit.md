# Research Brief: does MAPS_L currently have a trusted reviewer-execution producer?

- Owner: MAPS orchestration operator
- Decision or task supported: [reviewer-execution trusted-producer audit](../tasks/reviewer-execution-trusted-producer-audit.md)
- Time-sensitive: `YES` — current runtime/coordination surfaces may change
- Needed by: reviewer execution lineage Stage 1

## Question and why it matters

Does current accepted MAPS_L contain a component that can observe the execution which actually performs a machine review and emit a stable execution/principal identity **outside the reviewer-controlled verdict payload**?

If yes, reviewer execution lineage can proceed to a producer-first proof and only then consider an immutable review-to-execution binding. If no, adding `model`, `provider`, `session_id`, or similar fields to `reviews` would merely persist self-description and would falsely strengthen the evidence model.

Stage-0 invariant from independently reviewed PR #336:

```text
logical reviewer_id
!= immutable review subject
!= actual reviewer execution
```

A trusted producer must be able to support, at minimum:

```text
execution identity observed by issuer
+ logical principal observed/bound outside verdict payload
+ evidence that the reviewer cannot relabel as another principal
```

## What would count as an answer

A current source qualifies only if all of these hold:

1. it observes or creates a stable execution identity;
2. the logical reviewer principal is bound by a party/surface outside the reviewer's own verdict payload;
3. the reviewer cannot rewrite the observation by changing free text, commit trailers, CLI arguments, or review-evidence fields;
4. MAPS can retrieve/validate the observation through an existing integration;
5. it can be kept distinct from review authority and review-subject identity.

A source may still be useful provenance without satisfying this stronger predicate.

## Claims, sources, and assumptions

| Candidate source | What it currently proves | Trusted producer for reviewer execution? | Evidence / reason |
| --- | --- | --- | --- |
| `reviews.reviewer_id` | Logical identity that claimed/records the review | **NO** | `runtime/state/review.py` accepts `reviewer_id` as an operation argument. It is the review principal, not independent evidence of the execution that supplied it. |
| `review_subjects.run_id` | Optional run provenance of the **work being reviewed** | **NO** | `runtime/state/review_binding.py` binds the subject submission/task revision/run/artifacts. Reusing it for reviewer execution would conflate subject with reviewer. |
| `run_manifests` / run-session lineage | Immutable ACTIVE task-execution and provider-session relations | **NO for current review flow** | `create_run_manifest()` requires the current `ACTIVE` claimant. Review occurs at `READY_FOR_REVIEW`; widening this would change the lifecycle semantics Stage 0 explicitly preserved. |
| committed `work/reviews/pr-<N>-review-evidence.md` + `review-evidence` workflow | Exact reviewed-head binding and required review-shaped artifact | **NO** | `.github/workflows/review-evidence.yml` explicitly states the check does **not** prove reviewer identity is distinct from the author. The evidence fields remain repository-authored text. |
| GitHub account / PR review actor | Which GitHub credential posted a review/comment/commit | **PARTIAL, not execution proof** | A distinct identity/App can provide stronger credential-level actor evidence. Current repo historically uses the same `BigCatMellow` identity, and even a second actor does not by itself prove which model/process performed the review unless that actor controls or validates the execution. |
| Git commit trailers such as `Co-Authored-By` / `Claude-Session` | Free-text provenance hints carried in commit messages | **NO** | Current repository verification does not validate those trailers against a provider-issued attestation. A commit signature authenticates the commit/committer, not the truth of arbitrary message text. |
| GitHub Actions run metadata | Exact workflow/run/actor context for CI | **NO for reviewer execution** | Useful trusted execution evidence for CI jobs, but the review is performed before/elsewhere; no current relation binds an Actions run to the browser/model process that authored the review. |
| `EnvironmentFingerprint` | Local runtime/tool versions, repo revision, worktree state, selected availability facts | **NO** | `runtime/environment/fingerprint.py` intentionally observes environment compatibility, not reviewer/model/principal execution identity. Some availability values are supplied by caller. |
| hcom session/event observation | hcom session names/IDs, status, process-bound state and event facts | **NO for current browser review flow** | `runtime/communication/hcom_adapter.py` can observe hcom-managed sessions, but the accepted browser-review protocol does not launch/attach reviewer browser executions through hcom or mechanically bind hcom session identity to `reviews.reviewer_id`. |
| SENTINEL continuity label / review claim text | Coordination identity and duplicate-work claim | **NO** | `work/coordination/agents/SENTINEL.md` explicitly says labels are coordination identities only and never prove independence. Claims are GitHub text, not execution attestations. |
| operator role binding in browser conversation | Human-assigned role/continuity intent | **NO as current machine evidence** | `work/coordination/GITHUB_ASYNC_WORK_PULL.md` requires explicit role binding, but the repository/runtime receives no trusted browser-session identifier that mechanically connects that conversation to the resulting review row/evidence. |

Quality: all classifications above are based on direct reads of accepted `main@7dfcbd09a2df930ee3449ce047984e4da5cec460` plus the independently reviewed Stage-0 design in PR #336. This audit makes no claim about provider capabilities that are not integrated into MAPS.

## Existing accepted evidence already anticipated the limitation

`work/notes/2026-08-17-independent-review-enforcement-design.md` previously separated two problems:

- internal MAPS continuity-aware anti-self-review is mechanically real but local;
- committed GitHub review evidence can be exact-head-bound but does not prove a distinct reviewer identity.

The operator-selected Option B implemented the current `review-evidence` check while explicitly preserving that limitation. That design also noted that a second GitHub identity/App can improve identity evidence, but requires external provisioning and still must be operated in a way that corresponds to actual independent work.

The Stage-1 audit therefore does not discover a contradiction in current MAPS. It sharpens the next missing relation:

```text
trusted execution observation
→ logical reviewer principal
→ existing review row
```

## Result

**`BLOCKED_ON_TRUSTED_PRODUCER` for reviewer-execution lineage implementation.**

No current accepted MAPS integration satisfies the full predicate for the browser/machine review workflow. Several sources provide useful partial evidence, but combining partial facts does not make them stronger than their issuers:

```text
GitHub actor
+ free-text model/session trailer
+ reviewer_id argument
!= trusted proof of actual reviewer execution
```

Likewise:

```text
hcom session id
+ manually assigned SENTINEL label
!= mechanical binding to the browser reviewer that produced the verdict
```

## Smallest next engineering gate

Do **not** add review-execution schema yet.

The next valid proof must start at an execution surface that MAPS can actually trust. Two bounded producer classes are acceptable candidates:

### A. MAPS-controlled reviewer launcher / broker — preferred if feasible

A controller outside the reviewer process:

1. receives an already-authorized logical reviewer principal;
2. creates a stable `execution_id` **before** launching review execution;
3. starts/attaches the actual reviewer execution through a provider/runner integration it controls;
4. observes provider/session identity from that integration rather than from verdict text;
5. emits an immutable/signed or otherwise mechanically protected attestation;
6. never grants review authority merely because the execution exists.

Minimum adversarial proof before schema:

```text
principal = SENTINEL-A
controller issues execution E
reviewer attempts to claim principal SENTINEL-B
→ mismatch rejected / attestation remains SENTINEL-A
```

plus deterministic duplicate/replay behavior for the same attestation.

### B. Independently issued provider/platform attestation

If an execution provider exposes verifiable session/execution metadata to MAPS, consume that evidence through a narrow adapter. MAPS must verify the issuer/evidence rather than accepting copied IDs/URLs as truth.

This audit does not assume such an API exists; it is simply the alternate trust shape.

### What does not qualify as the next implementation

- add `provider`, `model`, `session_id`, or `execution_id` fields supplied to `record_review()`;
- parse `Claude-Session:` or similar commit text and call it verified;
- treat a different model/provider as continuity independence;
- create reviewer-shaped `run_manifests` by weakening ACTIVE-claimant invariants;
- introduce a general-purpose identity/attestation platform before one real producer is proven.

## Consequence for the recommended gap sequence

Item 2 has reached an honest external/integration dependency. No current in-repo implementation can close it without first creating or integrating a trusted launch/attestation source.

Per the parent operating rule, this branch should not hold the rest of the reviewed-gap sequence idle. After independent review of this audit:

1. preserve reviewer execution lineage as `BLOCKED_ON_TRUSTED_PRODUCER`;
2. if a trusted producer can be built using already-authorized existing access, shape that bounded producer experiment;
3. if it requires new credentials/account/App/provider access, that specific branch requires human reauthorization;
4. meanwhile continue to item 3: define the task/history retention contract.

## Summary and next step

Supported conclusion: **there is currently no trusted reviewer-execution producer integrated into MAPS_L for the browser review workflow.** The correct next implementation boundary is producer-first, not schema-first.

Next gate: independent review of this classification. If clean, route reviewer-execution lineage to `BLOCKED_ON_TRUSTED_PRODUCER` and continue the already-authorized sequence to task/history retention while the producer dependency remains explicit.