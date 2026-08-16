# Independent review progress — 2026-08-15

## Purpose

This note records the independent-review lane's current technical findings and integration state so another agent can resume without reconstructing the full review session.

This reviewer did not implement fixes on the reviewed PR branches. Findings were recorded on GitHub and repaired work was re-reviewed on new exact heads. Because the connected GitHub identity is also the PR author, GitHub refuses formal `APPROVE` / `REQUEST_CHANGES` review states on these PRs; clean/blocking conclusions were therefore recorded as non-approval review comments where necessary. Treat those comments as technical review evidence, not as a substitute for any repository rule that specifically requires a distinct GitHub reviewer identity.

## Current main

At this checkpoint:

- `main`: `c9e52cfcea2afd6c1fab3956baedcf62117450af`
- latest merge: PR #23 — canonical run guard

The critical harness sequence has now advanced through PRs #20 → #21 → #22 → #23.

## Harness / agentic-security stack

### PR #20 — harness contract foundation

Status: **MERGED**.

Independent review originally found shallow `OperationResult.data` immutability / serialization aliasing. The repair recursively detached/froze nested result data and added behavioral coverage. The repaired head was subsequently accepted and merged before this note.

### PR #21 — hcom normalization + Hook registry

Status: **MERGED**.

Independent review found and then re-reviewed fixes for:

- unsupported mutable Hook leaves escaping recursive immutability;
- invalid enum / failure-policy values reaching fail-open behavior;
- hcom `stop()` leaking low-level `ValueError`;
- duck-typed unvalidated Hook specs bypassing constructor validation at registry registration.

Final repaired head was technically clean before merge.

### PR #22 — provider-neutral HarnessService

Status: **MERGED**.

Independent blocker found: `start()` normalized adapter identity for lookup but exposed the unnormalized caller value to Hooks, allowing policy/guard logic to inspect a different adapter identity than the service actually invoked.

Repair used the canonical selected adapter ID in Hook context and added focused behavioral coverage. Final exact head was technically clean before merge.

### PR #23 — canonical run guard

Status: **MERGED**.

Independent blocker found: durable session checking originally compared bare `session_id` only even though HarnessService routes by adapter. Provider-local session IDs are not sufficient provider-neutral identity.

Final accepted behavior:

- routed adapter, `SessionRef.adapter`, durable session ID, and durable adapter identity must agree;
- current canonical manifests containing only bare `run_manifests.session_id` fail closed as `SESSION_ADAPTER_UNPROVEN`;
- the guard does not invent a second mutable session authority or silently change run-manifest schema;
- historical `stop` keeps relaxed lease/revision semantics only when adapter-qualified historical identity is actually proven;
- adversarial tests cover bare-ID insufficiency, same-ID/different-adapter rejection, service-level fail-closed behavior, and historical-stop behavior.

Final Runtime CI #217 passed before merge.

### PR #24 — initial agentic security baseline

Status: **OPEN / BLOCKED / MUST SYNCHRONIZE TO MERGED #23**.

Independent findings:

1. **Canonical guarding is optional wiring.** `HarnessService` can be constructed with its default empty Hook registry, and no mandatory composition/factory currently guarantees installation of `CanonicalRunGuard` before consequential `send` / `resume` / `stop` operations. Security tests that manually install the guard do not make the public service boundary unavoidable.
2. The PR also carries several checkpoint/handoff files outside the security task's declared change boundary. These are merge-hygiene / repository-truth concerns and should be removed or explicitly justified before merge.

The currently observed #24 branch was still diverged from the repaired/merged #23 ancestry at the last check. Synchronize first, then repair/re-review the exact remaining delta.

## Portable Run Record / evaluation stack

### PR #33 — portable Run Record v1

Status: **OPEN / BLOCKED**.

Current exact-head findings:

1. `criterion_evidence` copies task-level criterion claims/verdicts without filtering each claim's existing `run_id` to the selected run. A Run Record for run A can therefore contain acceptance evidence produced by run B.
2. Future review-subject enrichment can mark `review_subject` coverage `VERIFIED` merely because a projected review subject exists, without proving that subject binds the selected run.

Required direction: exact-run filtering / binding, with explicit `UNKNOWN` or task-level labeling when the run join is not proved.

### PR #34 — frozen regression case v1

Status: **OPEN / BLOCKED; downstream of #33**.

Independent blocker: `_validate_run_record()` validates hash/version/replay properties but does not validate the expected Run Record `record_kind` / shape. A different self-consistent v1 object can be accepted and embedded as though it were a MAPS portable Run Record.

Required direction: fail closed on wrong artifact kind/shape and add adversarial type-confusion coverage.

### PR #35 — comparative frozen regression evaluator

Status: **OPEN / BLOCKED; downstream of #34**.

Independent blocker: the evaluator proves exact frozen cases/results, but baseline and candidate identities are only free-form labels. It cannot prove which exact configuration/artifact produced either result set.

Required direction: bind baseline/candidate to stable artifact/configuration identity (hash/reference), while preserving evaluation-only / no-auto-promotion semantics.

## Skills stack

### PR #25 — Agent Skills format foundation

Status: **OPEN / BLOCKED**.

Independent blocker: `load_skill()` verifies the whole-directory hash and then reopens `SKILL.md` separately to read the procedure body. Content can change between verification and activation, so the returned body may not match the verified `content_sha256`.

Required direction: activate from bytes that are part of the same verified snapshot / revalidate the exact bytes used, with an adversarial drift-between-check-and-read test.

### PR #26 — Skills catalog provenance read model

Status: **NO NEW INDEPENDENT BLOCKER** beyond PR #25.

The catalog remains authority-neutral and deterministic. Final disposition depends on the #25 activation fix and later synchronization.

### PR #27 — frozen Skill selection evaluation corpus

Status: **OPEN / BLOCKED**.

Independent blocker: false Skill selections on expected-`ABSTAIN` cases increment `false_activation_cases` but do not count as false positives in `selection_precision`. The benchmark can therefore report perfect precision while activating Skills on hard negatives.

Required direction: include negative-case false activations in the precision denominator and add a direct precision regression test.

### PR #31 — static Skill quality/security gate

Status: **OPEN / BLOCKED; downstream of #27**.

Independent blocker: the report is labeled with the descriptor's verified `content_sha256`, then metadata/resources are reread for scanning without proving the scanned bytes still match that hash. A gate result can therefore describe one Skill identity while scanning different bytes.

Required direction: atomically bind scanned bytes to the reported content identity or revalidate immediately over the exact scanned snapshot.

## Environment / reproducibility stack

### PR #28 — EnvironmentSpec v1

Status: **OPEN / BLOCKED**.

Independent blocker: the "no secret values" boundary is enforced only inside `secrets.required_names`. Credential literals can still be embedded in setup/maintenance/validation command strings and become persisted normalized spec/hash material.

Required direction: reject credential-like literal material across all persistent string fields that can contain commands, or otherwise define a safe structured representation that cannot persist secret values.

### PR #29 — environment fingerprint / compatibility

Status: **OPEN / BLOCKED; downstream of #28**.

Independent blocker: repository containment is checked before later normal path I/O. A dependency path can be replaced with a symlink after validation and before use, producing a check/use escape outside the repository.

Required direction: perform containment-safe open/read semantics at use time (or otherwise make the validation/use operation race-safe), with an adversarial replacement test.

### PR #30 — append-only environment evidence

Status: **NO NEW INDEPENDENT BLOCKER** beyond #28/#29.

The E3 layer remained derived/append-only and did not turn compatibility evidence into task permission or authority.

## Review-freshness stack

### PR #32 — immutable review subjects

Status: **OPEN / BLOCKED**.

Independent blocker: a consequential `REVISION_BOUND` review subject may rely on `run_id` alone without immutable output/artifact references. A run manifest proves the execution contract, not the final reviewed output bytes; output can change without changing task revision/submission/run identity.

Required direction: consequential approval must bind immutable reviewed output identity (or an equivalently strong rederived-at-review proof), not just a run identity.

## Legacy reconciliation / research

### PR #36 — legacy-recovery reconciliation

Status: **PLANNING CONTENT NEEDS REFRESH**.

The architecture/reconciliation model was coherent, but its "current baseline" section became stale as #20-#23 merged and new independent review blockers were recorded. Refresh current PR/main state before treating the reconciliation document as current planning truth.

### PR #37 — bounded legacy archaeology

Status: **SUBSTANTIVELY CLEAN; synchronization/final integration still required**.

Independent spot checks supported the report's load-bearing claims:

- the stale acquisition-path incident was real;
- EXP-0006 ended in revise / weak metrics and did not validate the lexical retriever;
- `SYN-0004` remains genuinely incomplete/UNKNOWN;
- `EXP-0007` remains proposed/pending.

The report is explicitly a dated research snapshot, so later merges do not invalidate it in the same way they invalidate a "current baseline" document.

## Wave 3 planning / evaluation work

### PR #38 — execution-lineage design

Status: **OPEN / DESIGN BLOCKER**.

Independent finding: the design defines provider/project-qualified `SessionRef` identity but proposed replacement/predecessor chains still use bare `predecessor_session_id`. Exact lineage should use the full provider-scoped identity or a stable internal lineage-link identity.

A separate stale `UNKNOWN` in the design should also be refreshed because later A0/hcom work already resolved it.

### PR #39 — Context Builder v2 evidence-integrity corpus

Status: **OPEN / BLOCKED**.

Independent blocker: case `CBI-010` allows a baseline document about current implementation state as an acceptable substitute for a query about whether a proposal was authorized. Implementation state does not prove authorization state.

Required direction: remove that substitute or replace it with evidence that actually proves the queried authorization fact.

### PR #40 — Layer 2 / Layer 3 benchmark protocol

Status: **SUBSTANTIVELY CLEAN; synchronization/final integration still required**.

No technical blocker found in the frozen protocol. Layer 2/Layer 3 evidence separation, non-tradeable blockers, external authority requirements, and no-auto-promotion semantics were coherent.

### PR #41 — Stage 1 Context Builder evidence projector/scorer

Status: **OPEN / BLOCKED; downstream of #39**.

Independent blocker: `CODE_SYMBOL` resolution is implemented as two independent substring checks (`class X` somewhere + `def y` somewhere), so `X.y` can be certified even when `y` is not a member of `X`.

Required direction: structural/syntactic resolution of the exact symbol relationship, with adversarial same-file wrong-class coverage.

### PR #42 — benchmark result validation

Status: **OPEN / BLOCKED; downstream of #40**.

Independent findings:

1. result artifacts are not mechanically bound to the exact frozen benchmark-protocol bytes/identity;
2. output reports drop the exact property/provenance references they validate, leaving counts/status but insufficient information for independent reproduction from the report itself.

The scorer's deliberate boundary—accepting adapter-supplied `VERIFIED` provenance rather than itself becoming canonical-evidence authority—is not by itself a defect.

### PR #43 — operational-learning projection

Status: **RUNTIME SEMANTICS SUBSTANTIVELY CLEAN; CHANGE-BOUNDARY MISMATCH**.

The projector remains guidance-only, withholds candidate/review-due/retired/superseded/non-applicable/UNKNOWN guidance, and does not self-promote or grant task/policy authority.

Remaining issue: the task/PR declare four changed paths but the actual delta contains an additional schema-test file. Correct the declared boundary or remove the extra file before final integration.

### PR #44 — full-fidelity hcom lineage read

Status: **OPEN / BLOCKED**.

Independent blocker: `probe_lineage_capability()` can report `SUPPORTED` after validating only that each event has a positive integer ID. It does not prove event IDs are unique.

Pinned upstream hcom inspection clarified the correct model: `reply_to_local` resolves into a single local SQLite event-ID namespace. The fix should therefore reject duplicate **bare local event IDs** in the bounded capability sample; instance-qualified uniqueness is not the right requirement.

### PR #45 — exact hcom message relationships

Status: **OPEN / BLOCKED; downstream of #44**.

The bare-event-ID relationship model itself is consistent with upstream hcom's single local event-ID namespace.

Independent blocker: the resolver trusts optional correlation values (`reply_to_local`, `intent`, `thread`, etc.) without checking consistency with PR #44's `coverage.field_presence`. An input can claim a concrete `reply_to_local` while simultaneously saying that field was not observed, and #45 will still create an exact reply edge.

Required direction: optional values may produce relationship evidence only when their corresponding field-presence proof is true; contradictions must fail closed.

## Recommended integration / repair queue

Highest leverage sequence from this checkpoint:

1. **Synchronize and repair #24** on merged `main` / merged #23; then exact-head security re-review.
2. Repair **#33**, then propagate/re-review **#34 → #35**.
3. Repair **#25**, then propagate/re-review **#26 → #27 → #31**.
4. Repair **#28 → #29**, then re-check clean downstream **#30**.
5. Repair **#32**; remember its state-layer overlap with #30 requires real synchronization and fresh CI whichever lands second.
6. Repair **#39**, then **#41**; #40 remains a comparatively clean independent benchmark root.
7. Repair **#44**, then **#45**.
8. Refresh planning truth in **#36/#38** after the implementation heads settle.
9. Preserve #37 as research evidence and #43 as a clean runtime concept pending scope declaration correction.

## Reviewer operating constraints for continuation

For every re-review:

- re-check current `main`, PR base, base SHA, head, head SHA, draft/merge state, and exact CI;
- review the new exact delta, not the old head number or historical review packet;
- stacked approval does not survive a material base/diff change automatically;
- treat `UNKNOWN` as a valid state rather than filling gaps by inference;
- capability/evidence never becomes permission or authority by itself;
- do not accept duplicate authority stores or prose/prompt-only enforcement for security boundaries;
- behavioral adversarial tests are required for consequential boundary fixes;
- if this reviewer implements a fix, it is no longer independent for that changed work.
