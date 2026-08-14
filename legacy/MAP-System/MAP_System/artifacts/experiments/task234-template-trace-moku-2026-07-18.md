# TASK-234 Template and Update-Path Trace — Moku

- Status: `read-only evidence`
- Task: `TASK-234`
- Helper: `helper-review-steward-moku`
- Boundary: workspace sources only; no deployment or UI inspection outside the workspace

## Conclusion

The workspace contains a complete **installer template and installation path**
for CommandCenterUI, but no observed deployable checkout or installed launcher
target. It supports the claim that MAP *can install* a bundled UI; it does not
support the claim that this template currently updates the operator's UI.

## Candidate-source trace

| Candidate | Exact path | Observed result | Evidence strength | Conclusion |
|---|---|---|---|---|
| Bundled UI source | `MAP_System/templates/install/command-center-ui/` | EXISTS; includes `app/server.py`, `src/chat.html`, `src/chat.js`, `src/chat.css`, runtime launcher, and README. | Direct workspace observation. | Installable template, not proof of live deployment. |
| Installer/update script | `install-map-system.sh` | EXISTS; `install_command_center_ui_bundle()` copies the bundle to `$COMMAND_CENTER_UI_DIR`. | Direct workspace observation. | Defines a possible update mechanism. |
| Launcher template | `MAP_System/templates/install/bin/command-center-ui` | EXISTS; rendered launcher sets `COMMAND_CENTER_UI_WORKSPACE` and executes `$COMMAND_CENTER_UI_DIR/run-command-center-app.sh`. | Direct workspace observation. | Defines an installed-launcher shape, not its installed value. |
| Repository-local live checkout | `Projects/CommandCenterUI` | MISSING. | Direct workspace path check. | No vendored/live checkout is available in this workspace. |
| Historical external checkout | `/home/home/Projects/CommandCenterUI` | Recorded only in `artifacts/command-center-ui/task-182-map-health-cards.md`; outside this assignment's workspace-read boundary. | Recorded claim, not re-observed here. | Neither accessible nor confirmed as current deployment source by this trace. |

## Observed update and verification path

`install-map-system.sh` defaults `COMMAND_CENTER_UI_DIR` to
`$HOME/Projects/CommandCenterUI` and permits an override through
`MAP_INSTALL_COMMAND_CENTER_UI_DIR`. In dry-run mode it only plans work; with
`--yes`, it backs up the destination, copies the entire template bundle with
`cp -a`, marks launch scripts executable, and renders the launcher with the
chosen destination. The template runtime then starts its local server from its
own directory.

The observed script's health summary checks only whether
`$COMMAND_CENTER_UI_DIR/run-command-center-app.sh` exists. It does not compare
installed files to the template, identify a running process's source tree, or
verify the operator-facing UI. No installed destination, rendered launcher, or
runtime process is inspectable within this workspace, so those checks remain
unavailable rather than failed or passed.

## Evidence-supported future output boundary

If a later decision establishes the installer template as the deployment
source, the defensible candidate UI outputs are:

- `install-map-system.sh`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/templates/install/command-center-ui/src/chat.html`
- `MAP_System/templates/install/command-center-ui/src/chat.js`
- `MAP_System/templates/install/command-center-ui/src/chat.css`
- `MAP_System/templates/install/bin/command-center-ui` only if launcher
  contract/path behavior changes.

If the live external checkout is the source, its exact accessible path and
update mechanism must be supplied before task output paths are named. This
trace does not authorize substituting template paths for that checkout.

## Uncertainty and smallest defensible recommendation

**Recommendation: keep the coordination-card implementation deferred.** First
run an operator-visible, read-only deployment-source verification that names
the actual launcher/check-out used by the operator and compares its server/UI
files or establishes installer provenance. Record the exact source path,
rendered launcher destination, verification command/result, and whether an
installer update is intended. Then shape the UI task against that confirmed
source and retain TASK-227's existing rework/ownership boundary.

No UI, deployment, policy, authority, task, shared-state, or TASK-227 change
was made.

## Sources

- `MAP_System/tasks/TASK-234.json`
- `install-map-system.sh`
- `MAP_System/templates/install/command-center-ui/README.md`
- `MAP_System/templates/install/command-center-ui/run-command-center-app.sh`
- `MAP_System/templates/install/bin/command-center-ui`
- `MAP_System/artifacts/command-center-ui/task-182-map-health-cards.md`
