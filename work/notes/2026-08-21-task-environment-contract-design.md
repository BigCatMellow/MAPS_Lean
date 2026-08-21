# Task environment contract design

Date: 2026-08-21
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

The next 6.24 gap after the routing report envelope is explicit task-contract
storage for environment requirements.

VERIFIED current state:

- `runtime/state/schema.sql` stores task contracts across `tasks`,
  `task_inputs`, `task_sources`, `task_dependencies`, `task_output_paths`,
  `task_non_goals`, `task_acceptance_criteria`, `task_stop_conditions`, and
  `task_policy`.
- `runtime/state/base.py::update_contract()` owns the shaping transaction and
  writes scalar/list contract fields.
- `runtime/state/policy.py::PolicyStateMixin` validates `contract["policy"]`
  before write and applies it via the one optional `_apply_policy_contract_conn`
  hook.
- `runtime/state/integrity.py::_task_definition_conn()` computes task revision
  from scalar/list contract fields plus policy flags.
- No task contract field currently names an `EnvironmentSpec`, freshness TTL,
  or whether environment evidence is required for routing.

This is why PR #151's routing envelope still needs the envelope JSON to carry
`spec_ref` and `task_revision` itself. MAPS has no canonical task-level place
to say "this task expects this environment spec."

## Decision: additive `task_environment` contract table

Future implementation should add one optional row per task:

```sql
CREATE TABLE IF NOT EXISTS task_environment (
    task_id TEXT PRIMARY KEY REFERENCES tasks(task_id) ON DELETE CASCADE,
    spec_ref TEXT NOT NULL,
    max_age_seconds INTEGER NOT NULL CHECK (max_age_seconds > 0),
    required_for_routing INTEGER NOT NULL DEFAULT 0 CHECK (required_for_routing IN (0,1)),
    allow_older_task_revision INTEGER NOT NULL DEFAULT 0 CHECK (allow_older_task_revision IN (0,1))
);
```

Field meaning:

- `spec_ref`: safe repo-relative path to an `EnvironmentSpec`.
- `max_age_seconds`: freshness TTL for routing report envelopes.
- `required_for_routing`: default `false`; if `true`, a later behavior-change
  task may route missing fresh evidence to a policy gate.
- `allow_older_task_revision`: default `false`; if `true`, a future envelope
  selector may accept a report produced for an older task revision.

Do not add `report_ref` yet. PR #151 already supports caller-supplied envelope
JSON; durable report/cache location is a separate production-source decision.

## Store integration

Recommended implementation shape:

1. Add a dedicated `EnvironmentContractMixin`, placed before `BaseStore` in
   `TaskStore`.
2. Validate `contract["environment"]` in `update_contract()` before delegating.
3. Extend `BaseStore.update_contract()` from a single hard-coded optional policy
   hook to a tuple/list of shaping hooks, so policy and environment contract
   writes occur in the same transaction.
4. `get_task()` should include:

   ```python
   task["environment"] = None | {
       "spec_ref": str,
       "max_age_seconds": int,
       "required_for_routing": bool,
       "allow_older_task_revision": bool,
   }
   ```

5. `_task_definition_conn()` must include this environment contract in the
   task revision. A changed environment requirement is a changed task contract.
6. `validate_ready()` should validate shape/path/positive TTL if an environment
   contract is present, but absence must not block AGI readiness.

## Routing behavior preserved

This schema alone must not change routing.

- No environment contract: current behavior.
- Environment contract present with no report: current behavior unless a later
  task explicitly implements `required_for_routing`.
- `DRIFTED`/`UNKNOWN`: remain non-rejecting.
- Only fresh explicit `INCOMPATIBLE` reports gate routing.

## Bounded follow-up implementation

Recommended next task: `Task environment contract storage`.

Allowed implementation scope:

- Add `task_environment` table.
- Add `EnvironmentContractMixin` validation/read/write.
- Generalize BaseStore contract hooks so policy and environment writes are
  atomic in one shaping transaction.
- Include environment contract in task revision.
- Add readiness validation for malformed optional environment contracts.
- Add tests for:
  - absent environment contract defaults to `None` and does not block READY;
  - valid environment contract round-trips through `update_contract()` /
    `get_task()`;
  - invalid `spec_ref`, non-positive TTL, and non-boolean flags fail
    `INVALID_CONTRACT`;
  - changing environment contract changes task revision;
  - contract freezes after READY;
  - policy and environment contract updates remain atomic.

Must not do in that follow-up:

- Wire routing to require reports.
- Inspect environments.
- Persist report cache entries.
- Choose a universal default `EnvironmentSpec`.

## Roadmap impact

This design does not complete 6.24. It defines the next storage surface needed
for explicit task-to-`EnvironmentSpec` association while preserving the current
non-blocking environment behavior.
