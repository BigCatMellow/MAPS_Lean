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
- Dependencies / preconditions: EnvironmentSpec PR #28, EnvironmentFingerprint PR #29, and review-subject PR #32 are merged. Final synchronization starts from accepted `main@a3430799c756d7afb88c059b39f650e8d7568bc9`.

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
- [x] focused environment-evidence tests pass on the repaired feature layer.
- [x] synchronized onto accepted post-#32 main with a genuine two-parent commit without dropping review-subject state/schema/store composition.
- [x] accepted Run Record integration expectation now reports selected-run environment coverage `VERIFIED` while retaining #32 review-subject coverage `UNKNOWN` when exact selected-run review binding is unproven.
- [ ] fresh exact-head full Runtime stack CI passes after final task-record update.
- [ ] independent exact-head review remains required before completion.

## Verification and evidence

- Original implementation CI: `31898071184` passed on implementation commit `cf47e82f58586091becc5d298f27833ae97f0aac`.
- Independent review later identified an integration mismatch with the stronger accepted #28 parser: the old sensitive-snapshot test tried to create a secret-bearing EnvironmentSpec via `parse_environment_spec()`, which now correctly fails earlier.
- Repair head `8b1d8b784a0eabbd9669aa482ce5d6d2e9904f23` updates that regression to prove both boundaries: parse-time secret rejection and persistence-time rejection of a deliberately constructed typed sensitive spec.
- Runtime CI #338 / `31928764586` reached the full active suite. All focused environment evidence tests passed; its sole failure was the now-corrected Run Record environment coverage expectation.
- Genuine synchronization commit `a7754ebea3e6e46a2a816218a3d746a5d7c108d2` has parents accepted `main@a3430799c756d7afb88c059b39f650e8d7568bc9` and repaired feature head `74e5137a7729dbe6451e1e8d78d2398c7e99c93f`.
- Post-sync Run Record adaptation commit `540160ae73766ccb4ed641c7c4e2183cf2798edb` changes only the environment coverage expectation while preserving review-subject UNKNOWN semantics.
- Exact accepted-main delta after that adaptation is six files: `runtime/state/environment.py`, `runtime/state/schema.sql`, `runtime/state/store.py`, `tests/test_run_environment_evidence.py`, `tests/test_run_record.py`, and this task file.
- Evidence to preserve: exact synchronized head, fresh final CI, six-file compare, independent review result.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: canonical MAPS SQLite state with accepted E1/E2 environment types and accepted #32 review-subject state.
- Ordered procedure: append-only schema → evidence mixin → trace composition → behavioral/immutability tests → parse/persistence secret-boundary regression → synchronize from accepted post-#32 main → narrow Run Record expectation adaptation → full CI → independent exact-head review.
- Failure branches: IF safe persistence requires redacting the normalized spec snapshot THEN reject recording instead, because redaction would invalidate spec identity; IF compatibility should affect continuation THEN defer that policy/recovery decision to a later guarded integration task; IF synchronization would drop or rewrite accepted #32 state THEN stop and rebuild from accepted main rather than resolving by historical branch preference.
- Rollback / recovery: revert isolated PR; new table is additive and no existing row is rewritten.
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
- integrated state cannot preserve both review-subject and environment-evidence facts exactly.

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
- Trace integration is composed in `EnvironmentEvidenceMixin.trace_task()` and coexists with accepted `ReviewBindingMixin.trace_task()` through TaskStore MRO; neither becomes writable authority.
- E3 does not make compatibility a gate. A later Harness/recovery task may consume this evidence only with canonical task/policy checks.
- The final integration tree starts from accepted post-#32 main and adds only the six-file E3/Run Record delta.

## Completion / handoff

- Completed: append-only run-environment evidence, trace projection, immutability/safety tests, dual parse/persistence sensitive-spec regression, genuine post-#32 synchronization, and narrow Run Record integration adaptation.
- Not completed: fresh exact-head full Runtime CI on this final task-record head, independent exact-head review, merge.
- Current blocker: fresh CI and independent review only; there is no remaining implementation or upstream dependency blocker known at this head.
- Next action if not DONE: require green exact-head Runtime CI, then independent review by an agent that did not implement this repair. Do not make compatibility an execution/recovery gate.
