# Task: append-only run environment evidence

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: bind exact EnvironmentSpec/fingerprint/compatibility observations to immutable runs as append-only canonical evidence without changing run contracts, task authority, leases, recovery behavior, or policy.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #29 / `agent/environment-fingerprint-wave2`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, `runtime/state/observability.py`, Environment/Reproducibility roadmap E3.
- Authoritative sources: canonical task/run state remains authoritative for task ownership/lifecycle; EnvironmentSpec/fingerprint objects provide bounded execution evidence only.
- Dependencies / preconditions: verified E2 implementation head `620834a0db9cce7e2de3d4750c98f1c49687ccdd`; full Runtime stack CI `31897745175` passed on E2 implementation commit.

## Change boundary

- MAY CHANGE: `runtime/state/environment.py`, `runtime/state/store.py`, `runtime/state/schema.sql`, focused run-environment tests, this task file.
- MUST NOT CHANGE: `run_manifests` columns/immutability, task claim/lease semantics, review/policy authority, Harness/recovery behavior, EnvironmentSpec/fingerprint semantics, provider/external systems.
- MAY CHANGE IF NECESSARY: narrow append-only evidence schema/trace composition inside this E3 boundary.
- OPERATOR APPROVAL REQUIRED: automatic resume/recovery decisions, task/run authority changes, secret storage, environment mutation, destructive/external behavior, or material scope expansion.

## Decision authority

- Owner may decide: append-only evidence row shape, snapshot/hash validation, compatibility derivation at record time, trace projection, event summary, and focused tests consistent with E3.
- Owner must escalate: any design requiring mutation of `run_manifests`, a second task/run authority store, compatibility-driven task state changes, or persistent credential values.

## Acceptance criteria

- [ ] existing `run_manifests` schema and immutable contract remain unchanged.
- [ ] new run-environment evidence is append-only and keyed to an existing run.
- [ ] each row preserves `spec_ref`, exact EnvironmentSpec hash, fingerprint hash, compatibility state, optional reference fingerprint hash, normalized spec snapshot, bounded fingerprint snapshot, derived compatibility snapshot, actor, and timestamp.
- [ ] record path verifies fingerprint is bound to the supplied EnvironmentSpec and derives compatibility internally rather than accepting a caller-supplied verdict.
- [ ] compatible, warning, drifted, incompatible, and unknown observations may all be recorded as evidence; recording any state does not authorize or block task execution by itself.
- [ ] task status/claim/lease/heartbeat and immutable run manifest remain unchanged after evidence recording.
- [ ] multiple observations append rather than replace prior evidence.
- [ ] SQLite UPDATE/DELETE of environment evidence is blocked by triggers.
- [ ] missing run and spec/fingerprint mismatch fail explicitly.
- [ ] evidence persistence refuses snapshots/references that trigger the existing sensitive-text detector; it does not silently redact a hashed EnvironmentSpec snapshot.
- [ ] existing read-only task trace includes environment evidence under the exact run through MRO composition, without making trace writable authority.
- [ ] event summary records only run/evidence ID + compatibility state, not full snapshots.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: `python -m unittest tests.test_run_environment_evidence -v` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: schema diff, PR diff, GitHub Actions run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: canonical MAPS SQLite state with E1/E2 environment types.
- Ordered procedure: append-only schema → evidence mixin → trace composition → behavioral/immutability tests → stacked draft PR → CI → independent review.
- Failure branches: IF safe persistence requires redacting the normalized spec snapshot THEN reject recording instead, because redaction would invalidate spec identity; IF compatibility should affect continuation THEN defer that policy/recovery decision to a later guarded integration task.
- Rollback / recovery: revert isolated stacked commit/PR; new table is additive and no existing row is rewritten.
- Security / privacy controls: no credential values; bounded fingerprint only; sensitive-text persistence check; event summary omits snapshots.
- External side effects: Git branch/PR publication only.
- Effort limit: E3 evidence binding only; no environment setup, worktrees, snapshots, or recovery automation.
- Approved reference: Environment & Reproducibility roadmap E3.

## Stop / escalate

Stop rather than guess if:

- environment evidence must mutate `run_manifests` to work;
- compatibility needs to renew/claim/stop/resume tasks automatically;
- snapshot persistence would require storing credential values;
- a separate mutable run/environment authority begins to emerge.

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
- EnvironmentSpec snapshots are persisted exactly, not redacted. If the existing secret detector identifies sensitive text, recording fails so the exact spec hash remains meaningful.
- Trace integration is composed in `EnvironmentEvidenceMixin.trace_task()` rather than editing the older observability implementation directly.
- E3 does not make compatibility a gate. A later Harness/recovery task may consume this evidence only with canonical task/policy checks.

## Completion / handoff

- Completed: implementation prepared on `agent/environment-run-evidence-wave2`.
- Not completed: commit/PR/CI/review.
- Current blocker: none.
- Next action if not DONE: commit isolated E3 implementation, open stacked draft PR against `agent/environment-fingerprint-wave2`, and run full Runtime stack CI.
