# CommandCenterUI

CommandCenterUI is the graphical MAP command-center app bundled by the MAP
fresh installer.

The installer places this directory at `~/Projects/CommandCenterUI` by default
and installs a `command-center-ui` launcher in `~/.local/bin`. That launcher
sets `COMMAND_CENTER_UI_WORKSPACE` to the current MAP checkout before starting
the app, so the UI does not depend on a hard-coded workstation path.

## Run

```bash
command-center-ui
```

Or, from this directory:

```bash
./run-command-center-app.sh
./run-command-center-app.sh --server-only
```

The app starts a localhost backend on `127.0.0.1:8765`, opens a native
GTK/WebKit window when available, and falls back to Firefox through
`app/window.py`.

## What It Shows

- Live hcom conversation and agent presence.
- MAP state and runtime health.
- Persistent operator attention inbox for questions, approvals, and terminal
  prompts. Dismissing or snoozing an alert never removes its live inbox item.
- Local and relayed agent identities, including cross-host names such as
  `vumo:RUKI`.
- Verbatim hcom messages, with the exact source available under
  **Show original message** and in the agent terminal. Background model-backed
  summaries are disabled because MAP requires model helpers to remain visible
  to the operator.
- Embedded ProjectUpdater at `/project-updater/`.
- Standalone ProjectUpdater launch/status actions.

ProjectUpdater itself lives in the MAP checkout at:

```text
Projects/ProjectUpdater/app/index.html
```

ProjectUpdater records remain browser-localStorage owned. CommandCenterUI reads
only the explicit status export at `~/Downloads/project-updater-status.json`.

## Entrypoints

- `run-command-center-app.sh` - full app window, or `--server-only`.
- `app/window.py` - GTK/WebKit wrapper with Firefox fallback.
- `app/server.py` - localhost backend; serves `src/orchestrator.html` at `/`.
- `src/orchestrator.html`, `src/orchestrator.js`, `src/orchestrator.css` - the
  UI: an agent hierarchy tree (grouped by real hcom `tag`) on the left, a
  per-agent/all-agents thread on the right.
- `CommandCenterUI.desktop` - local desktop launcher metadata.

The prior `chat.html`/`app.html`/`index.html`/`studio.html` views (and an
intermediate `room.html`) were retired 2026-07-29 in favor of
`orchestrator.html` as the sole UI; their files were moved, not deleted, to
`_legacy-ui-removed-2026-07-29/` at the repo root.

Runtime logs, injection audit logs, and relay-summary caches are generated under
`runtime/` after the app runs.
