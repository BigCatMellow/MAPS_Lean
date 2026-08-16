# Task: adapter-qualified run/session lineage Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/run-session-lineage-wave3` / FOUNDRY repair continuity
- Risk: `MEDIUM`
- Goal: Add the smallest durable, append-only project/adapter-qualified run/session relationship needed by the harness guard without mutating immutable run manifests or creating task/session authority duplication.

## Inputs and source of truth

- Root `AGENTS.md`.
- Execution-lineage design in PR #38 (`work/notes/2026-08-15-execution-lineage-design.md`).
- Merged harness foundations #20-#23.
- Historical PR #24 synchronization head `3be75c654051d27ad9beaf7d2620953f1e28d9ee`.
- Accepted harness identity contract: `SessionRef(session_id, worker_id, adapter, project_id)` and `ExecutionBinding.project_id`.
- Independent review blocker recorded on PR #48: provider session identity cannot be globally unique across all projects when accepted harness/provider state is project-scoped.
- `runtime/state/schema.sql`, `runtime/state/integrity.py`, `runtime/state/store.py`, and `runtime/state/observability.py`.
- `runtime/policy/harness_guard.py`.

Current boundary:

- `run_manifests` remain immutable initial task/run/worker contracts.
- bare `run_manifests.session_id` remains adapter-unproven.
- task `project_id` remains canonical project truth; lineage only copies that immutable-at-record evidence to preserve provider namespace identity.
- PR #24's mandatory canonical enforcement and anti-spoof composition are preserved.
- final integration must be synchronized by SWITCHYARD onto then-current accepted `main`; this development branch does not self-integrate.

## Change boundary

Implemented only:

- append-only project/adapter-qualified run/session relationship storage;
- resolver and trace projection;
- canonical guard consumption of the resolver;
- focused compatibility/adversarial tests;
- SQLite invariant hardening;
- repair of the independently reviewed project/provider-context identity defect.

Not changed:

- task ownership/lease semantics;
- immutable `run_manifests` rows or triggers;
- review/policy/operator authority;
- provider process/session liveness semantics;
- helper/recovery/submission/communication lineage.

## Required semantics

1. Durable provider identity is project-scoped: `(project_id, adapter_id, session_id)`.
2. `project_id` is derived from the owning run's canonical task state; callers do not supply a second mutable project authority.
3. First explicit relationship for a run is an `ATTACH`.
4. A manifest that already contains legacy/bare `session_id` may only be adapter-qualified with that same session ID.
5. Replacement is explicit and linear: a `REPLACE` names the current link it replaces.
6. A link has at most one replacement; replacement predecessors stay inside the same run and therefore the same canonical project context.
7. One project-scoped adapter-qualified provider session may not be durably bound to multiple runs; the same provider-local adapter/session ID may exist independently in another project.
8. Recording requires the same worker as the immutable run manifest and the current live task claim; worker change requires a new run.
9. Existing runs preserve `UNBOUND` and `ADAPTER_UNPROVEN` rather than guessing.
10. Resolver output is evidence only. It grants no task authority, approval, readiness, or provider liveness.
11. Canonical guard accepts session-bound operations only for the exact current explicit project + adapter + session relationship.
12. PR #24's mandatory enforcement role remains internal to trusted guard composition and cannot be spoofed by callback attributes/lookalike guards.

## Acceptance criteria

- [x] `run_session_links` is append-only and references an existing run.
- [x] run manifests remain unchanged and immutable.
- [x] late attachment to a run with no manifest session is supported explicitly.
- [x] adapter qualification of an existing bare manifest session is supported only for the same session ID.
- [x] conflicting first attachment is rejected through the API and SQLite boundary.
- [x] replacement requires the exact current link, remains within one run, and cannot branch.
- [x] durable uniqueness is scoped to canonical `project_id + adapter_id + session_id` rather than falsely global adapter/session identity.
- [x] two different projects may each bind the same provider-local adapter/session ID.
- [x] direct SQL cannot persist a lineage project different from the owning run's canonical task project.
- [x] worker mismatch / inactive claim / expired lease / changed task revision are rejected when recording a link.
- [x] resolver preserves `UNBOUND` and `ADAPTER_UNPROVEN` for legacy data and exposes canonical project context.
- [x] canonical guard consumes the resolver, keeps bare legacy session evidence fail-closed, and rejects project-context mismatch even when adapter/session strings match.
- [x] PR #24 anti-spoof enforcement regressions remain intact in the implementation surface.
- [x] trace exposes project-scoped append-only lineage without claiming provider liveness or complete external coverage.
- [ ] focused adversarial tests pass on the repaired head.
- [ ] fresh full Runtime CI passes on the repaired head.
- [ ] independent exact-head review confirms the HIGH identity-model blocker is mechanically closed.

## Verification

Focused targets:

```text
python -m unittest tests.test_run_session_lineage -v
python -m unittest tests.test_harness_canonical_guard -v
```

Historical evidence before repair:

- Runtime CI #245 passed on integrated A1/#24 head `2541bae2433d2011a027494817c0348b450d28ec`.
- Runtime CI #248 / `31924691827` passed on pre-repair head `13b3293781a43980066f642edb79cf7f4528d4aa`.
- Independent review still required changes because the runtime encoded false global `(adapter_id, session_id)` uniqueness.

Current repair evidence must come from the new exact head; old CI does not satisfy the repaired implementation.

Review required: `INDEPENDENT_REVIEW` before merge/completion. FOUNDRY implemented the repair and is not eligible to supply that review.

## Stop / continuation

A1 stops after project-scoped durable provider identity is mechanically correct and independently reviewed.

A2 helper/recovery lineage remains a separate branch/PR. FOUNDRY must not widen #48 into A2/A3/A4 work.

Final current-main synchronization, exact-delta gating, and merge belong to SWITCHYARD, not this development branch.
