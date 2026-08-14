# Extracted Legacy Runtime Source

This directory is a **temporary migration staging area** for the small subset of the original MAP runtime that MAPS Lean still needs after `legacy/` is removed.

The files under this directory are exact source snapshots from legacy commit `77723d16f77efc5e1fe03a74adab920dc7534f16` unless a file says otherwise.

## Authority

- These files are **reference implementation**, not active MAPS Lean runtime.
- Root `AGENTS.md`, the active playbook, AGI standard, project decisions, and current task records remain authoritative.
- Historical `AGENTS.md`, task state, UI assumptions, or identity conventions from legacy do not gain authority by being preserved here.
- Active code MUST NOT import from `migration/legacy-runtime-source/`.

## Why preserve source instead of rewriting from memory

Legacy contains tested behavior for:

- atomic task claims, leases, heartbeats, submission authorship, and independent review;
- release and approval gates;
- deterministic pre-dispatch policy and halt behavior;
- LangGraph routing and checkpoint behavior;
- recovery/liveness/RnS behavior;
- bounded Ollama and Aider helper lanes;
- schema migration and task-mirror validation;
- installation safety and hcom setup.

MAPS Lean should preserve those **behaviors and invariants**, not blindly preserve the old folder layout or cockpit.

## Extracted areas

### Task state and lifecycle

- `db/`
- `migration/`
- `scripts/map_task.py`
- `scripts/promote_task.py`
- `scripts/release_task.py`
- `scripts/validate_task_schema.py`
- `scripts/validate_task_graph.py`
- `scripts/validate_task_mirrors.py`
- `scripts/verify_run_scope.py`

### Routing, authority, and policy

- `graph/`
- `workflow/runtime_policy.yaml`
- `workflow/role_registry.yaml`
- `scripts/pre_dispatch_policy.py`
- `scripts/halt_state.py`
- `scripts/map_authority.py`
- `scripts/context_rotation.py`

### Recovery and resilience

- `scripts/agent_loop.py`
- `scripts/limit_watcher.py`
- `scripts/liveness_reaper.py`
- `scripts/durable_execution.py`
- `scripts/resilience_controls.py`
- `scripts/dead_letter_queue.py`
- `scripts/reconcile_agents.py`

### Local/helper execution

- `scripts/local_runner.py`
- `scripts/local_assistant_health.py`
- `scripts/aider_wrapper.py`
- `scripts/event_trace.py`
- `scripts/redaction.py`

### Tests

Only tests that protect retained Lean behavior are preserved. Historical task/review/release records are not copied.

### Design and install references

The snapshot retains the old migration inventory/plan, subsystem API map, fresh-install guide, communication boundary, state-machine guardrails, operations runbook, local-model helper guide, and installer source.

## Required adaptations before promotion

Do **not** copy these files directly into the active runtime without resolving these differences:

1. **Task states:** legacy uses states such as `IN_PROGRESS` and `SUBMITTED`; Lean currently documents `ACTIVE` and `READY_FOR_REVIEW`. Choose one canonical runtime vocabulary and test every transition.
2. **AGI gate:** Lean requires `AGI READY` before a consequential task can enter `READY`. Legacy promotion code predates that standard.
3. **LangGraph persistence:** legacy `db/checkpointer.py` stores checkpoint tables inside `map.db`. Lean deliberately separates `.maps/state/maps.db` from `.maps/state/langgraph-checkpoints.db`.
4. **hcom authority:** hcom is communication/session transport only. Its internal state must never become task authority.
5. **RnS presentation coupling:** legacy `limit_watcher.py` contains WezTerm-visible-resume assumptions. Preserve recovery behavior, replace terminal presentation coupling with a provider/session adapter.
6. **Task mirrors:** legacy maintained SQLite + per-task JSON + a giant `task_graph.json`. Lean should avoid three competing mutable truths. Preserve export/import compatibility only where it provides real value.
7. **Agent identity:** legacy found drift between SQLite agent rows, `status.json`, and hcom sessions. Lean needs one durable identity/ownership model plus adapters, not three manually synchronized registries.
8. **Installer:** preserve dry-run, backup-before-overwrite, user-local installation, and post-install verification; remove required WezTerm, fixed roster, and CommandCenterUI installation.

## Promotion rule

For each retained subsystem:

```text
extract exact source
→ identify invariant
→ port the smallest active implementation
→ port relevant tests
→ run tests against disposable state
→ remove dependency on this staging source
```

Once every retained invariant has an active implementation and passing test, this staging directory can be removed too.
