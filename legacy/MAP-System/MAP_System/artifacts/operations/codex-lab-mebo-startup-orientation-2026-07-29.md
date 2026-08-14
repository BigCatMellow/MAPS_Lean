# Codex Lab Startup Orientation — 2026-07-29

- agent_id: codex-lab-mebo
- host_role: KUDU read-only MAP mirror
- canonical_authority: RUKI through `map-authority`
- task_claims: none
- review_claims: none
- coordinator_designation: none
- status: oriented_waiting_for_routing

## Continuity

- `context_rotation.py validate` read ledger revision 75 and returned
  `ok: false`.
- The reported substantive validation issues are historical drift for
  `codex-lab-kazu` and `task278-levi`.
- The newest relevant Damo/Nivo and Rosa checkpoint entries report no issues
  and no task or touched-path drift.
- This fresh `codex-lab-mebo` session did not inherit a task, review, or
  coordinator obligation from a finalized checkpoint.

## Rotation Advice

- state: below_threshold
- used_tokens: 39040
- threshold_tokens: 150000
- used_percent_of_context_window: 15.1
- recommendation: Continue in the current session. Do not prepare or finalize
  a rotation.

## Startup Validation

- `validate_shared_state_tasks.py`: pass; the active-lane table matches the
  local mirror.
- `operational_lessons.py orientation`: pass; model-backed helpers must remain
  visible, and review helpers use visible Codex capacity when Claude is not
  ready.
- local `graph/runner.py`: recommended independent review routing; its
  emergence scan was stale with zero pending candidates.
- `emergence_sentinel.py list`: zero pending candidates; no curation action
  available.
- authoritative `map-authority route`: no global halt; emergence scan current
  with zero pending candidates.

## Authoritative Queue

- SUBMITTED without an open review claim: `TASK-294`, `TASK-295`.
- SUBMITTED with an existing review claim: `TASK-298` claimed for review by
  `codex-lab-loki`.
- CHANGES_REQUESTED: `TASK-263`; the local mirror still showed it as submitted
  during the first graph run.
- IN_PROGRESS: `TASK-254`, `TASK-292`, `TASK-296`.
- Policy-gated: `TASK-297`, `TASK-304`.
- Released: `TASK-303`.

## Resume Plan

1. Preserve RUKI as the sole task-lifecycle authority; do not write local
   `MAP_System/map.db`.
2. Coordinate with the fixed visible roster and avoid duplicate review
   ownership.
3. Wait for the operator's response to Claude Lab's priority request before
   claiming `TASK-294` or `TASK-295`.
4. If assigned, claim through `map-authority claim-review`, heartbeat through
   `map-authority heartbeat`, and produce an independent review artifact.
5. Keep the untracked rotation-gateway changes separate for independent
   security review and operator disposition.

## Librarian Follow-up

- The fixed Librarian reported a task-graph/output collision: `TASK-295`
  (`SUBMITTED`) and policy-gated `TASK-297` (`READY`) both declare
  `MAP_System/scripts/map_task.py`.
- RUKI `map-authority task show` confirmed both statuses and output paths.
- The collision blocks treating these tasks as independent implementation
  lanes. No implementation or review claim was made.
- The Librarian also found `TASK-301` in `APPROVED` state with a SQLite review
  row but no durable review artifact. Treat it as not release-ready until
  review provenance is reconciled.
- The authoritative task or review state was not changed.
