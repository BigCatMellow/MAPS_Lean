# Independent review progress addendum — 2026-08-16

This is a reviewer-only checkpoint. It does not modify any implementation PR and does not grant approval/authority. Exact live state must still be re-resolved before action.

## Accepted main

Latest accepted `main` observed by this reviewer:

- `0c0e48f97b58570bb5a8ea5a2ee3db0d9780350b`
- merge: PR #35 — comparative frozen regression evaluator v1

The following stacks are now merged through their reviewed heads:

- Wave 1 harness/security: #20 → #21 → #22 → #23 → #24
- portable evaluation: #33 → #34 → #35

## Evaluation stack

### #33 Portable Run Record

Merged after exact-main synchronization and final integrated review. Prior cross-run criterion/review-subject attribution blockers were repaired before merge.

### #34 Frozen regression case

Merged after exact-main synchronization and final integrated review. Run Record artifact-kind/shape validation and incident-taxonomy concerns were closed before merge.

### #35 Comparative regression evaluator

Merged at feature head `2e87acb705d83d7d0607e9a70b679fb17ccb6c55`; final exact-head Runtime CI #273 passed before merge. Baseline/candidate identity uses immutable configuration refs and evaluation remains non-authoritative/no-auto-promotion.

## Skills stack

### #25 Skills format

Current reviewed feature head: `378b66dda487bfe956499a0167dc46cfd2b4cb5d`.

TOCTOU activation bug is fixed: load uses the exact verified byte snapshot. Feature layer is clean, but root still needs synchronization to current main before final merge review.

### #26 Skills catalog

Current head: `f599bfa4559560c3bcd26a05dbb73d9fb0edacd4`.

Prior destructive ancestry bug is fixed. The repair restored upstream harness files accidentally removed by the old head; exact current #25→#26 delta is now catalog-only. Runtime CI #270 passed. Feature layer is clean; current-main synchronization remains.

### #27 Skill selection evaluation

Current head: `a7370c2760b438e11acf5f996094b80677078743`.

False activations on expected-ABSTAIN cases now reduce precision/F1. Repaired #26 ancestry propagated without feature changes. Runtime CI #275 passed. Feature layer clean; current-main synchronization remains.

### #31 Skill static gate

Current head: `340995da515516a5d5df8ff6b0645f41fd01e012`.

Gate scans one verified byte snapshot and reports that exact hash; the prior scan/hash TOCTOU is closed. Repaired Skills ancestry propagated without feature changes. Runtime CI #276 passed. Feature layer clean; current-main synchronization remains.

## Environment stack

### #28 EnvironmentSpec

Current reviewed head: `63ae7a23730920a1975531654bc95416447e6c15`.

Credential literals in persistent free-form fields are now rejected using the existing sensitive-text boundary rather than stored/redacted. Runtime CI #258 passed. Feature layer clean; current-main synchronization remains.

### #29 Environment fingerprint

Current reviewed head: `4c863b5c7c33840b6764a1a6a806c21a17946303`.

Dependency hashing now uses repo-anchored fd traversal + `O_NOFOLLOW`; symlink replacement after precheck fails closed. Runtime CI #262 passed. Feature layer clean; current-main synchronization remains.

### #30 Run environment evidence

Current head: `3693a22954a8c66ba99ed63eed4e9f3ab0131ee0`.

No new E3 semantic/authority defect found, but exact-head Runtime CI #269 fails because an old E3 test expects secret-bearing EnvironmentSpec construction to succeed and be rejected later. Repaired #28 correctly rejects the secret at parse time. Update the downstream test to preserve the stronger upstream boundary; do not weaken #28. Then rerun full CI and later synchronize the full #28→#30 stack to current main.

## Review freshness

### #32 Immutable review subjects

Current head remains `489a2524b513d6d9ab5eb186874cbc04e6e4ba4a`.

Still blocked: consequential `REVISION_BOUND` review can be satisfied by a run ID without immutable reviewed-output identity. Run identity proves the execution contract, not final reviewed bytes. Consequential subjects need immutable output/evidence identity or equivalent exact rederivation.

## Execution lineage

### #48 A1 run/session lineage

Current head: `13b3293781a43980066f642edb79cf7f4528d4aa`.

Still blocked. Durable provider identity is encoded as global `(adapter_id, session_id)` even though accepted `SessionRef`/hcom identity is project-scoped. Add/derive canonical project/provider context, scope uniqueness accordingly, preserve it in resolution, and verify it at the guard. Then synchronize to current main.

### #49 A2 helper/recovery lineage

Current head: `ed865be729cf2d15663258fd46c9296ea32d28e7`.

Pre-integration review found no new A2-specific blocker. Helper IDs are allocated before consequential helper work, helper links recheck run authority, helper/recovery stores retain ownership of their own facts, recovery structural invariants are enforced, and trace coverage remains incomplete. Runtime CI #268 passed. Final review waits for #48 repair and stack synchronization.

### #50 A3 submission-attempt lineage

Current reviewed head: `832fa4ab2c3e97a8f7cdc22a73baca0d276adfc0`.

Two A3-specific blockers:

1. `UNKNOWN` is represented by absence of a row, while SQLite permits later insertion for an already-existing submission count. A submission made without `run_id` can therefore be changed semantically from UNKNOWN to EXPLICIT after the fact; one current test explicitly performs that backfill. The A3 contract says attribution exists when and only when the submitter supplies the run. Omitted A3-era attribution must be mechanically sealed/immutable rather than left as an insertable absence.
2. Runtime CI #274 fails the active-legacy dependency gate because the new runtime coverage reason contains the literal `legacy/omitted`. Reword without the prohibited `legacy/` token and rerun full CI.

Normal explicit submission linkage otherwise has good transactional shape: run/task/worker/revision checks and relation insertion occur in the submission transaction; forced link failure rolls back the submission/task transition; public read logic does not infer from timing or single-run state.

Final integration of #50 also waits for #48→#49 repair/synchronization.

## Other open reviewed work

- #39 Context Builder corpus remains blocked on an invalid acceptable substitute for an authorization-status query.
- #40 benchmark protocol remains substantively clean but needs current-main synchronization.
- #41 Context evidence scorer remains blocked on non-structural `CODE_SYMBOL` ownership resolution and upstream #39.
- #42 benchmark results remain blocked on exact protocol identity binding and preservation of validated evidence refs.
- #43 operational-learning runtime semantics remain clean; amend task change boundary to include the added schema-test file, then synchronize.
- #44 hcom lineage capability remains blocked until duplicate bare local event IDs are rejected.
- #45 message relationships remain blocked until optional correlation values are required to agree with `field_presence` evidence.
- #36 live roadmap status remains stale and must be refreshed before merge.
- #37 archaeology remains substantively clean dated research evidence.
- #38 design note remains historically stale and should be reconciled with the actual A1/A2/A3 implementation state.

## Reviewer operating rule

Other agents are actively implementing/synchronizing these branches. This lane should continue to:

1. avoid implementation changes on reviewed PRs;
2. re-resolve exact base/head/CI before every review;
3. review only heads that actually moved;
4. keep inherited blockers separate from new layer-specific findings;
5. treat UNKNOWN as evidence, not a gap to fill by inference;
6. require behavioral evidence for security/authority fixes;
7. invalidate prior integration clearance when a material base/head changes.
