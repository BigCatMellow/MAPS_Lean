# Task: append-only run environment evidence

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: bind exact EnvironmentSpec/fingerprint/compatibility observations to immutable runs as append-only canonical evidence without changing run contracts, task authority, leases, recovery behavior, or policy.

## Inputs and source of truth

- Inputs: `AGENTS.md`, accepted EnvironmentSpec/fingerprint foundation on `main`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, `runtime/state/observability.py`, Environment/Reproducibility roadmap E3.
- Authoritative sources: canonical task/run state remains authoritative for task ownership/lifecycle; EnvironmentSpec/fingerprint objects provide bounded execution evidence only.
- Dependencies / preconditions: EnvironmentSpec PR #28 and EnvironmentFingerprint PR #29 are merged. PR #32 review-subject binding is serialized ahead of this branch because both touch `runtime/state/schema.sql` and `runtime/state/store.py`.

## Change boundary

- MAY CHANGE: `runtime/state/environment.py`, `runtime/state/store.py`, `runtime/state/schema.sql`, focused run-environment tests, narrow Run Record integration expectations required by the accepted trace surface, this task file.
- MUST NOT CHANGE: `run_manifests` columns/immutability, task claim/lease semantics, review/policy authority, Harness/recovery behavior, EnvironmentSpec/fingerprint semantics, provider/external systems.
- MAY CHANGE IF NECESSARY: narrow append-only evidence schema/trace composition inside this E3 boundary.
- OPERATOR APPROVAL REQUIRED: automatic resume/recovery decisions, task/run authority changes, secret storage, environment mutation, destructive/external behavior, or material scope expansion.

## Decision authority

- Owner may decide: append-only evidence row shape, snapshot/hash validation, compatibility derivation at record time, trace projection, event summary, and focused tests consistent with E3.
- Owner must escalate: any design requiring mutation of `run_manifests`, a second task/run authority store, compatibility-driven task state changes, or persistent credential values.

## Acceptance criteria

- [x] existing `run_manifests` schema and immutable contract remain unchanged.
- [x] new run-environment evidence is append-only and keyed to an existing run.
- [x] each row preserves `spec_ref`, exact EnvironmentSpec hash, fingerprint hash, compatibility state, optional reference fingerprint hash, normalized spec snapshot, bounded fingerprint snapshot, derived compatibility snapshot, actor, and timestamp.
- [x] record path verifies fingerprint is bound to the supplied EnvironmentSpec and derives compatibility internally rather than accepting a caller-supplied verdict.
- [x] compatible, warning, drifted, incompatible, and unknown observations may all be recorded as evidence; recording any state does not authorize or block task execution by itself.
- [x] task status/claim/lease/heartbeat and immutable run manifest remain unchanged after evidence recording.
- [x] multiple observations append rather than replace prior evidence.
- [x] SQLite UPDATE/DELETE of environment evidence is blocked by triggers.
- [x] missing run and spec/fingerprint mismatch fail explicitly.
- [x] EnvironmentSpec parser rejects credential-like persisted command text at its own boundary.
- [x] evidence persistence independently refuses a sensitive typed EnvironmentSpec snapshot even if such an object is constructed without the parser; it does not silently redact a hashed snapshot.
- [x] existing read-only task trace includes environment evidence under the exact run through MRO composition, without making trace writable authority.
- [x] event summary records only run/evidence ID + compatibility state, not full snapshots.
- [x] focused environment-evidence tests pass on repair head `8b1d8b784a0eabbd9669aa482ce5d6d2e9904f23`.
- [ ] after PR #32 merges, synchronize this layer onto then-current accepted `main` without dropping #32 state/review changes.
- [ ] adapt the accepted Run Record integration expectation so selected-run environment evidence projects as `VERIFIED`, while preserving all then-current review-subject coverage semantics.
- [ ] fresh exact-head full Runtime stack CI passes after synchronization.
- [ ] independent exact-head review remains required before completion.

## Verification and evidence

- Original implementation CI: `31898071184` passed on implementation commit `cf47e82f58586091becc5d298f27833ae97f0aac`.
- Independent review later identified an integration mismatch with the stronger accepted #28 parser: the old sensitive-snapshot test tried to create a secret-bearing EnvironmentSpec via `parse_environment_spec()`, which now correctly fails earlier.
- Repair head `8b1d8b784a0eabbd9669aa482ce5d6d2e9904f23` updates that regression to prove both boundaries: parse-time secret rejection and persistence-time rejection of a deliberately constructed typed sensitive spec.
- Runtime CI #338 / `31928764586` on that repair head reached the full active test suite. All focused environment evidence tests passed. Its only failure was the accepted-base Run Record expectation `environment == MISSING`; with E3 trace evidence present the implementation correctly reports `VERIFIED`. This is a stale integration expectation, not evidence of environment runtime failure.
- `tests/test_run_record.py` does not exist on this historical feature branch itself; it came from the stacked base. Do not add a stale duplicate here. Apply the one-line environment coverage adaptation only when building the post-#32 synchronization tree from then-current accepted main.
- Evidence to preserve: schema diff, original green CI, #338 failure log and focused-test pass, final synchronized CI, PR #30 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: canonical MAPS SQLite state with accepted E1/E2 environment types and, after serialization, accepted #32 review-subject state.
- Ordered procedure: append-only schema → evidence mixin → trace composition → behavioral/immutability tests → parse/persistence secret-boundary regression → wait for #32 → synchronize from accepted main → narrow Run Record expectation adaptation → full CI → independent exact-head review.
- Failure branches: IF safe persistence requires redacting the normalized spec snapshot THEN reject recording instead, because redaction would invalidate spec identity; IF compatibility should affect continuation THEN defer that policy/recovery decision to a later guarded integration task; IF synchronization would drop or rewrite accepted #32 state THEN stop and rebuild from accepted main rather than resolving by historical branch preference.
- Rollback / recovery: revert isolated stacked commit/PR; new table is additive and no existing row is rewritten.
- Security / privacy controls: no credential values; bounded fingerprint only; parse-time and persistence-time sensitive-text checks; event summary omits snapshots.
- External side effects: Git branch/PR publication only.
- Effort limit: E3 evidence binding only; no environment setup, worktrees, snapshots, or recovery automation.
- Approved reference: Environment & Reproducibility roadmap E3.

## Stop / escalate

Stop rather than guess if:

- environment evidence must mutate `run_manifests` to work;
- compatibility needs to renew/claim/stop/resume tasks automatically;
- snapshot persistence would require storing credential values;
- a separate mutable run/environment authority begins to emerge;
- post-#32 synchronization cannot preserve both review-subject and environment-evidence state changes exactly.

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

- E3 deliberately adds a separate `run_environment_evidence` table instead of modifying immutable `run_manifests`.
- Evidence rows are historical observations, so multiple rows per run are expected and useful for later recovery/equivalence analysis.
- Compatibility is recomputed from the supplied spec/fingerprint/reference at record time. A caller cannot write an arbitrary `COMPATIBLE` verdict.
- EnvironmentSpec snapshots are persisted exactly, not redacted. If either the parser or the persistence boundary identifies sensitive text, recording/creation fails so the exact spec hash remains meaningful.
- Trace integration is composed in `EnvironmentEvidenceMixin.trace_task()` rather than editing the older observability implementation directly.
- E3 does not make compatibility a gate. A later Harness/recovery task may consume this evidence only with canonical task/policy checks.
- PR #30 must remain behind #32 because both edit shared canonical state composition. The final integration tree must start from accepted main, not from the historical stacked base.

## Completion / handoff

- Completed in the feature/repair layer: append-only run-environment evidence, trace projection, immutability/safety tests, dual parse/persistence sensitive-spec regression.
- Not completed: post-#32 synchronization, Run Record environment coverage adaptation, fresh exact-head full Runtime CI, independent exact-head review, merge.
- Current blocker: PR #32 exact head `f89a98264501567db667f7284df16ffe7abd5120` has Runtime CI #337 PASS but still requires a separate independent exact-head review before it may merge.
- Next action if not DONE: after #32 is accepted, build #30 from the new accepted main, overlay only the intended environment-evidence layer plus the narrow current Run Record expectation, run fresh CI, and hand the exact immutable packet to an independent reviewer. Do not make compatibility an execution/recovery gate.
