# Release Checklist: TASK-280

## Header

```
task_id:      TASK-280
released_by:  mapfinish2-dove
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Implements the approved TASK-277 role-semantics slice: defines a small stable
role vocabulary and compact authority contracts, validates new tasks against
it, maps historical free-form values through a compatibility mode, and makes
routing consume normalized roles instead of provider names or incidental
prose.

**Checklist evidence:**

- **Shared-file updates complete:** not applicable in the shared/-folder
  sense — outputs are `graph/runner.py`, `notes/role-contracts.md`,
  `scripts/map_task.py`, `scripts/run_tests.sh`,
  `scripts/validate_task_schema.py`, a delivery note, tests, and
  `workflow/role_registry.yaml`. `notes/role-contracts.md`, read directly,
  is the durable documentation of the new role vocabulary/contracts and is
  itself the "shared" reference this task's own scope calls for.
- **Decisions recorded:** yes — a `DECISION_RECORDED` event ties directly to
  this task: 2026-07-26T19:43:55Z, `bigboss`, "Operator explicitly
  authorized completing every remaining registered roles-system roadmap
  task without stopping; this clears TASK-280 structural pre-dispatch
  approval for its registered scope."
- **Follow-up tasks created:** none created directly. Not needed: role
  normalization is consumed by later tasks in the same TASK-277 roadmap
  (e.g., TASK-281's run manifests reference `role_id`/`role_source` from
  this task's registry) as a dependency, not a newly spawned task.
- **Event log entry prepared:** `events.jsonl` shows two rework cycles —
  rejected by `codex-lab-nita` (2026-07-26T19:58:51Z, unknown role IDs not
  accepted by sanctioned task creation), reworked, rejected again by
  `codex-lab-diro` (2026-07-27T13:19:21Z, a registered test failing under
  exact batch order — `REPAIR-0010` raised the attempt ceiling to allow a
  fourth attempt), reworked again, then `APPROVED` (13:38:36Z, same
  reviewer). This release appends the canonical `RELEASED` event.
- **Emergence capture considered:** considered; no `emergence/` record
  names TASK-280 directly, and none is warranted beyond the review record
  itself, which already captured the two rework findings inline.

## Verification

- All 8 output paths confirmed to exist.
- `test_role_registry.py` passes as part of the full `run_tests.sh` run
  (73/79; unrelated pre-existing failures noted in TASK-268's checklist).
- Independent review: `APPROVED` by `codex-lab-diro`, 2026-07-27T13:38:36Z,
  after two rejection/rework cycles, the second requiring `REPAIR-0010` to
  raise `max_attempts` from 3 to 4 — both repairs are durable, disclosed
  events, not silent overrides.
- Output-path sequencing against `scripts/map_task.py` (also touched by
  TASK-268/TASK-274/TASK-278) is resolved: all three have already released
  earlier in this same batch.
