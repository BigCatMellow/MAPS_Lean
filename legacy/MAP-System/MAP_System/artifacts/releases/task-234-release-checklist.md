# Release Checklist — TASK-234

- task_id: TASK-234
- released_by: codex-lab-lilo
- release_scope: read-only CommandCenter deployment-source parity audit

## Verification

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Release record

TASK-234 releases an evidence-only finding: the configured new-window entry
chain reaches `~/Projects/CommandCenterUI/app/window.py`, but that wrapper can
reuse an existing port-8765 listener of unverified provenance. The installed
copy's `app/server.py` is materially out of parity with the installer template,
and historical `/home/home/...` references do not identify the current
configured target in this session. No UI, deployment, installer, policy,
authority, shared-state, or TASK-227 change was made.

TASK-235 has been created as the bounded follow-up: it will preserve a current
source manifest and define read-only provenance checks before any external UI
task is selected. A future implementation task still requires TASK-227 rework
and explicit operator approval for any edit outside this MAP workspace.
