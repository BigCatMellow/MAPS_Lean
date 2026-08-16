# Task: adapter-qualified run/session lineage Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/run-session-lineage-wave3`
- Risk: `MEDIUM`
- Goal: Add the smallest durable, append-only adapter-qualified run/session relationship needed by the merged harness guard without mutating immutable run manifests or creating task/session authority duplication.

## Inputs and source of truth

- Root `AGENTS.md`.
- Execution-lineage design in PR #38 (`work/notes/2026-08-15-execution-lineage-design.md`).
- Merged harness foundations #20-#23.
- PR #24 synchronization head `3be75c654051d27ad9beaf7d2620953f1e28d9ee`.
- A1 integrated head before this status-only update: `2541bae2433d2011a027494817c0348b450d28ec`; Runtime CI #245 passed on that exact integrated state.
- `runtime/state/schema.sql`, `runtime/state/integrity.py`, `runtime/state/store.py`, and `runtime/state/observability.py`.
- `runtime/policy/harness_guard.py`.

Current boundary:

- `run_manifests` remain immutable initial task/run/worker contracts.
- bare `run_manifests.session_id` remains adapter-unproven.
- PR #24's mandatory canonical enforcement and anti-spoof composition are preserved.
- this branch must resynchronize and rerun full CI if PR #24 moves again before integration.

## Change boundary

Implemented only:

- append-only adapter-qualified run/session relationship storage;
- resolver and trace projection;
- canonical guard consumption of the resolver;
- focused compatibility/adversarial tests;
- SQLite invariant hardening.

Not changed:

- task ownership/lease semantics;
- immutable `run_manifests` rows or triggers;
- review/policy/operator authority;
- provider process/session liveness semantics;
- helper/recovery/submission/communication lineage.

## Required semantics

1. A relationship is adapter-qualified: `(adapter_id, session_id)`.
2. First explicit relationship for a run is an `ATTACH`.
3. A manifest that already contains legacy/bare `session_id` may only be adapter-qualified with that same session ID.
4. Replacement is explicit and linear: a `REPLACE` names the current link it replaces.
5. A link has at most one replacement; replacement predecessors stay inside the same run.
6. One adapter-qualified provider session may not be durably bound to multiple runs.
7. Recording requires the same worker as the immutable run manifest and the current live task claim; worker change requires a new run.
8. Existing runs preserve `UNBOUND` and `ADAPTER_UNPROVEN` rather than guessing.
9. Resolver output is evidence only. It grants no task authority, approval, readiness, or provider liveness.
10. Canonical guard accepts session-bound operations only for the exact current explicit adapter-qualified relationship.
11. PR #24's mandatory enforcement role remains internal to trusted guard composition and cannot be spoofed by callback attributes/lookalike guards.

## Acceptance criteria

- [x] `run_session_links` is append-only and references an existing run.
- [x] run manifests remain unchanged and immutable.
- [x] late attachment to a run with no manifest session is supported explicitly.
- [x] adapter qualification of an existing bare manifest session is supported only for the same session ID.
- [x] conflicting first attachment is rejected through the API and SQLite boundary.
- [x] replacement requires the exact current link, remains within one run, and cannot branch.
- [x] duplicate provider session binding across runs is rejected.
- [x] worker mismatch / inactive claim / expired lease / changed task revision are rejected when recording a link.
- [x] resolver preserves `UNBOUND` and `ADAPTER_UNPROVEN` for legacy data.
- [x] canonical guard consumes the resolver and keeps bare legacy session evidence fail-closed.
- [x] PR #24 anti-spoof enforcement regressions remain intact.
- [x] trace exposes append-only lineage without claiming provider liveness or complete external coverage.
- [x] focused adversarial tests pass in full active discovery.
- [x] full Runtime CI #245 passed on integrated head `2541bae2433d2011a027494817c0348b450d28ec`.

## Verification

Focused target:

```text
python -m unittest tests.test_run_session_lineage -v
```

Full validation: Runtime stack CI #245 — PASS on the exact integrated A1/#24 state before this documentation-only status commit.

Review required: `INDEPENDENT_REVIEW` before merge/completion.

## Stop / continuation

A1 implementation scope is mechanically complete and stops here.

A2 helper/recovery lineage must be developed on a separate branch/PR so it cannot silently widen this review unit.
