# Review: TASK-234 Deployment-Source Parity Audit

```text
task_id: TASK-234
reviewer: helper-librarian-rori
review_date: 2026-07-18
task_owner: codex-lab-lilo
```

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Record candidate live/template locations, accessibility, and deployable-source evidence without modification. | PARTIAL | Direct checks confirm `/home/home/Projects/CommandCenterUI` is absent, the template and `/home/mellow/Projects/CommandCenterUI` are present, the rendered desktop invokes `~/.local/bin/command-center-ui`, and that launcher targets the installed directory. However, the audit's displayed chain skips `app/window.py`: the normal runtime launcher executes `window.py`, whose `ensure_server()` starts installed `server.py` only if port 8765 is not already open. If it is open, the window reuses that listener without proving its provenance. |
| 2 | Bound template-versus-installed differences and installer-copy conclusions without claiming an update occurred. | PASS | Independent SHA-256 checks reproduce equal README/runtime/chat hashes and the material `app/server.py` mismatch (`054b8f05…0e74` installed vs `3881cdb1…f291` template). The installer source does back up and copy the bundle to the configured destination. The audit correctly labels this a possible mechanism and does not claim it ran or refreshed the installed copy. |
| 3 | Propose evidence-supported future boundaries without granting external-edit authority or duplicating TASK-227 ownership. | PASS | The audit defers implementation, requires explicit operator approval for installed external paths, separately requires deployment/restart verification, and leaves TASK-227 rework with its existing owner. Neither proposed boundary is presented as authorized by TASK-234. |
| 4 | Meet TASK-234 criteria without UI, deployment, policy, authority, shared-state, or TASK-227 change. | PARTIAL | The read-only evidence, material parity mismatch, installer uncertainty, and deferred next action are otherwise sufficient. The configured/runtime provenance description must include the `window.py`/existing-listener branch before the update and verification path is exact enough for acceptance. |

## Files Reviewed

- `MAP_System/tasks/TASK-234.json`
- `MAP_System/artifacts/experiments/command-center-deployment-source-parity-audit-2026-07-18.md`
- `MAP_System/artifacts/experiments/task234-template-trace-moku-2026-07-18.md`
- `MAP_System/artifacts/experiments/task234-parity-contradiction-zero-2026-07-18.md`
- `install-map-system.sh`
- `MAP_System/templates/install/bin/command-center-ui`
- `MAP_System/templates/install/command-center-ui/` cited files
- `/home/mellow/.local/bin/command-center-ui`
- `/home/mellow/.local/share/applications/command-center-ui.desktop`
- `/home/mellow/Projects/CommandCenterUI/` cited launcher, desktop, window, server, and chat files

## Forbidden Changes Check

- PASS: review checks were read-only; no source, UI, deployment, task, policy, authority, shared-state, or TASK-227 mutation was performed.
- PASS: the audit does not grant external-edit authority or claim a deployment/update occurred.
- PASS: reviewer `helper-librarian-rori` is independent of owner `codex-lab-lilo`.

## Required Finding

Correct the configured launch-chain evidence to state `desktop -> rendered launcher -> installed run-command-center-app.sh -> app/window.py`. Then record the branch: `window.py` starts the installed `app/server.py` only when port 8765 is free; if the port is already open, it reuses the listener and its source remains unverified. This is a factual provenance correction and does not change the supported `PARITY_NOT_ESTABLISHED` conclusion.

## Independent Checks

- Rendered launcher and desktop targets matched the audit.
- Installed/template existence and absence claims matched.
- Installed copy has no `.git` directory.
- Cited installed/template hashes and mtimes matched.
- `bash -n` passed for the rendered and runtime launchers.

## Risk

Low correction cost, high relevance to the audit's purpose. Omitting the existing-listener branch could make a configured target look like proof of the backend serving the operator window—the exact inference TASK-234 is intended to prevent.
