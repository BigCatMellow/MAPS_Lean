# Task: adapter-qualified run/session lineage Wave 3

- Status: `IN_PROGRESS`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/run-session-lineage-wave3`
- Risk: `MEDIUM`
- Goal: Add the smallest durable, append-only adapter-qualified run/session relationship needed by the merged harness guard without mutating immutable run manifests or creating task/session authority duplication.

## Inputs and source of truth

- Root `AGENTS.md`.
- Execution-lineage design in PR #38 (`work/notes/2026-08-15-execution-lineage-design.md`).
- Current merged harness foundations #20-#23.
- PR #24 exact head `4ec42de3398258ebde0e0645516caef953a6a0ed` as the stack base; Runtime CI #219 passed on that head.
- `runtime/state/schema.sql`, `runtime/state/integrity.py`, `runtime/state/store.py`, and `runtime/state/observability.py`.
- `runtime/policy/harness_guard.py`.

Current accepted/prospective boundary:

- `run_manifests` remain immutable initial task/run/worker contracts.
- merged #23 deliberately fails session-bound operations with `SESSION_ADAPTER_UNPROVEN` when only bare `run_manifests.session_id` exists.
- PR #24 adds mandatory canonical-guard composition but does not add a session lineage store.
- this branch may stack on #24, but must resynchronize if #24 changes before integration.

## Change boundary

MAY CHANGE:

- `runtime/state/schema.sql`;
- a new bounded run/session-lineage state mixin;
- `runtime/state/store.py`;
- `runtime/state/observability.py` only to expose derived lineage evidence;
- `runtime/policy/harness_guard.py` only to consume the accepted resolver rather than a bare manifest session ID;
- focused tests;
- this task and its implementation note.

MUST NOT CHANGE:

- task ownership/lease semantics;
- immutable `run_manifests` rows or triggers;
- review/policy/operator authority;
- provider process/session liveness semantics;
- helper/recovery/submission/communication lineage;
- PR #24's branch.

## Decision authority

The owner may implement the smallest append-only relationship and resolver consistent with the inspected sources.

Escalate rather than guess if implementation would require:

- a mutable `tasks.current_session_id` or equivalent duplicate truth;
- mutating an existing run manifest to attach/replace a session;
- treating provider liveness as task authority/readiness;
- inferring adapter/session identity from names, timestamps, or message prose;
- changing worker identity on an existing run.

## Required semantics

1. A relationship is adapter-qualified: `(adapter_id, session_id)`.
2. First explicit relationship for a run is an `ATTACH`.
3. A manifest that already contains legacy/bare `session_id` may only be adapter-qualified with that same session ID; a different first session conflicts with immutable evidence.
4. Replacement is explicit and linear: a `REPLACE` must name the current link it replaces.
5. A link may have at most one replacement; branching is invalid.
6. One adapter-qualified provider session may not be durably bound to multiple runs.
7. Recording requires the same worker as the immutable run manifest and the current live task claim; worker change requires a new run.
8. Existing runs with no explicit link remain readable:
   - no manifest session -> `UNBOUND`;
   - bare manifest session -> `ADAPTER_UNPROVEN`.
9. Resolver output is evidence only. It grants no task authority, approval, readiness, or provider liveness.
10. Canonical guard may accept session-bound operations only when the resolver returns the exact requested adapter-qualified current session.

## Acceptance criteria

- [ ] `run_session_links` is append-only and references an existing run.
- [ ] run manifests remain unchanged and immutable.
- [ ] late attachment to a run with no manifest session is supported explicitly.
- [ ] adapter qualification of an existing bare manifest session is supported only for the same session ID.
- [ ] conflicting first attachment is rejected.
- [ ] replacement requires the exact current link and cannot branch.
- [ ] duplicate provider session binding across runs is rejected.
- [ ] worker mismatch / inactive claim / expired lease / changed task revision are rejected when recording a link.
- [ ] resolver preserves `UNBOUND` and `ADAPTER_UNPROVEN` for legacy data.
- [ ] canonical guard consumes the resolver and keeps bare legacy session evidence fail-closed.
- [ ] trace exposes the append-only lineage without claiming provider liveness or communication completeness.
- [ ] focused adversarial tests pass.
- [ ] full Runtime CI passes on the exact PR head.

## Verification

Focused target:

```text
python -m unittest tests.test_run_session_lineage -v
```

Then full PR-triggered Runtime stack CI.

Review required: `INDEPENDENT_REVIEW` before merge/completion.

## Stop / continuation

Stop this tranche after adapter-qualified run/session lineage is durable, resolvable, guard-consumable, traced, and tested.

Do not continue into helper/recovery lineage (A2), submission lineage (A3), communication task/run joins (A4c), or explainable waits (A4d) on this branch.
