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
- Merged harness foundations #20-#24.
- Historical PR #24 accepted head `3be75c654051d27ad9beaf7d2620953f1e28d9ee`.
- Accepted harness identity contract: `SessionRef(session_id, worker_id, adapter, project_id)` and `ExecutionBinding.project_id`.
- Independent PR #48 review findings:
  1. provider session identity cannot be globally unique across all projects when accepted harness/provider state is project-scoped;
  2. SQLite must enforce the same canonical identity representation as runtime code so raw whitespace/normalization variants cannot bypass uniqueness.
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
- repair of the independently reviewed project/provider-context identity defect;
- repair of the independently reviewed raw-string/normalization uniqueness defect.

Not changed:

- task ownership/lease semantics;
- immutable `run_manifests` rows or triggers;
- review/policy/operator authority;
- provider process/session liveness semantics;
- helper/recovery/submission/communication lineage.

## Required semantics

1. Durable provider identity is project-scoped: `(project_id, adapter_id, session_id)`.
2. `project_id` is derived from the owning run's canonical task state; callers do not supply a second mutable project authority.
3. SQLite requires stored project identity to exactly equal the canonical owning task project; trim-equivalent project aliases are rejected.
4. SQLite restricts adapter/session identity to the same lexical form accepted by runtime `_lineage_id`: alphanumeric first character, only `[A-Za-z0-9_.:@-]`, maximum 128 characters. Raw whitespace/control variants cannot create a second logical identity.
5. First explicit relationship for a run is an `ATTACH`.
6. A manifest that already contains legacy/bare `session_id` may only be adapter-qualified with that same session ID.
7. Replacement is explicit and linear: a `REPLACE` names the current link it replaces.
8. A link has at most one replacement; replacement predecessors stay inside the same run and therefore the same canonical project context.
9. One project-scoped adapter-qualified provider session may not be durably bound to multiple runs; the same provider-local adapter/session ID may exist independently in another project.
10. Recording requires the same worker as the immutable run manifest and the current live task claim; worker change requires a new run.
11. Existing runs preserve `UNBOUND` and `ADAPTER_UNPROVEN` rather than guessing.
12. Resolver output is evidence only. It grants no task authority, approval, readiness, or provider liveness.
13. Canonical guard accepts session-bound operations only for the exact current explicit project + adapter + session relationship.
14. PR #24's mandatory enforcement role remains internal to trusted guard composition and cannot be spoofed by callback attributes/lookalike guards.

## Acceptance criteria

- [x] `run_session_links` is append-only and references an existing run.
- [x] run manifests remain unchanged and immutable.
- [x] late attachment to a run with no manifest session is supported explicitly.
- [x] adapter qualification of an existing bare manifest session is supported only for the same session ID.
- [x] conflicting first attachment is rejected through the API and SQLite boundary.
- [x] replacement requires the exact current link, remains within one run, and cannot branch.
- [x] durable uniqueness is scoped to canonical `project_id + adapter_id + session_id` rather than falsely global adapter/session identity.
- [x] two different projects may each bind the same provider-local adapter/session ID.
- [x] direct SQL cannot persist a lineage project different from or merely trim-equivalent to the owning run's canonical task project.
- [x] direct SQL cannot bypass project/adapter/session uniqueness with leading/trailing space, tab, newline, or other characters outside the runtime identity alphabet.
- [x] worker mismatch / inactive claim / expired lease / changed task revision are rejected when recording a link.
- [x] resolver preserves `UNBOUND` and `ADAPTER_UNPROVEN` for legacy data and exposes canonical project context.
- [x] canonical guard consumes the resolver, keeps bare legacy session evidence fail-closed, and rejects project-context mismatch even when adapter/session strings match.
- [x] PR #24 anti-spoof enforcement regressions remain intact in the implementation surface.
- [x] trace exposes project-scoped append-only lineage without claiming provider liveness or complete external coverage.
- [ ] fresh full Runtime CI passes on the final repaired/task-record head.
- [ ] independent exact-head review confirms both HIGH identity-model blockers are mechanically closed.

## Verification

Focused targets:

```text
python -m unittest tests.test_run_session_lineage -v
python -m unittest tests.test_harness_canonical_guard -v
```

Historical evidence:

- Runtime CI #245 passed on integrated A1/#24 head `2541bae2433d2011a027494817c0348b450d28ec`.
- Runtime CI #248 / `31924691827` passed on pre-project-scope-repair head `13b3293781a43980066f642edb79cf7f4528d4aa`.
- Runtime CI #386 / `31930919472` passed on project-scoping repair head `a9284c1a00fc42eb26807ea01e8ca667aaa5ebac`, but SENTINEL correctly found that raw SQLite identity whitespace variants could still bypass the intended logical uniqueness.
- Normalization repair changes only `runtime/state/schema.sql` and `tests/test_run_session_lineage.py` relative to `a9284c1a...` before this task-record update: exact project matching, adapter/session lexical checks, and direct-SQL normalization adversarial coverage.

Old CI/review does not satisfy the final repaired head. Fresh exact-head Runtime CI and fresh independent review are required.

Review required: `INDEPENDENT_REVIEW` before merge/completion. FOUNDRY implemented both repairs and is not eligible to supply that review.

## Stop / continuation

A1 stops after project-scoped durable provider identity and SQLite canonical uniqueness are mechanically correct and independently reviewed.

A2 helper/recovery lineage remains a separate branch/PR. FOUNDRY must not widen #48 into A2/A3/A4 work.

Final current-main synchronization, exact-delta gating, and merge belong to SWITCHYARD, not this development branch.
