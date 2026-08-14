# Independent Review: TASK-235

- task_id: TASK-235
- reviewer: codex-lab-kiri
- task_owner: claude-lab-lure
- verdict: APPROVED
- reviewed_at: 2026-07-19

## Verdict

APPROVED. The dated manifest satisfies all four acceptance criteria without
crossing its read-only or decision-authority boundaries.

## Scope

Reviewed the deployment-source manifest as a dated, read-only evidence artifact.
I checked its configured launch chain, template/installed-copy distinction,
fingerprint evidence, runtime-provenance method, deployment decision gate, and
forbidden-change boundary against the referenced audit and accessible source
files.

## Acceptance Criteria

1. **PASS — configured source and provenance are distinguished.** The manifest
   records the desktop entry, rendered launcher, installed bundle, window
   wrapper, template source, candidate accessibility, dated fingerprints, and
   the difference between a configured target and the process actually owning
   port 8765.
2. **PASS — repeat check is bounded and read-only.** Section 5 covers free,
   occupied-and-verified, and occupied-but-unverified outcomes. The unverified
   case escalates instead of guessing, and none of the commands starts, stops,
   signals, or changes a process.
3. **PASS — deployment choice remains a human decision.** Section 6 separates
   intentional template deployment from a direct installed-copy edit. It
   requires explicit authorization for deployment, restart, and the external
   installed path, and selects neither boundary by inference.
4. **PASS — durable research output only.** The task adds the registered audit
   artifact and does not alter UI source, the installer, deployment state,
   policy, authority, shared state, or TASK-227.

## Evidence

- The current desktop entry still invokes
  `/home/mellow/.local/bin/command-center-ui`; that launcher still defaults to
  `/home/mellow/Projects/CommandCenterUI` and executes its runtime launcher.
- `app/window.py` in the template and installed copy remains byte-identical and
  implements the described port-probe behavior.
- The dated `app/server.py` fingerprints in the manifest remain reproducible:
  template `3881cdb17f86963d...`, installed `5adb2cade4c0da73...`.
- The installer still backs up and copies the complete template bundle to the
  configured installed destination (`install-map-system.sh`,
  `install_command_center_ui_bundle`).
- The referenced TASK-234 audit supports the historical parity findings and
  explicitly leaves runtime provenance unresolved for TASK-235 to address.

## Files Reviewed

- `MAP_System/artifacts/audits/command-center-deployment-source-manifest-2026-07-18.md`
- `MAP_System/artifacts/experiments/command-center-deployment-source-parity-audit-2026-07-18.md`
- `MAP_System/tasks/TASK-235.json`
- `MAP_System/templates/install/command-center-ui/app/window.py`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `install-map-system.sh`
- `/home/mellow/.local/bin/command-center-ui`
- `/home/mellow/.local/share/applications/command-center-ui.desktop`
- `/home/mellow/Projects/CommandCenterUI/run-command-center-app.sh`

## Forbidden Changes

PASS. Review found no task-owned change outside the single registered manifest
output. The manifest is descriptive and expressly withholds authorization for
deployment, restart, source selection, or external-copy editing.

## Risks

- The listener PID and UI fingerprints are intentionally point-in-time
  evidence from 2026-07-18. Subsequent UI work changed `src/chat.*`, so those
  hashes must not be interpreted as a current deployment check. The document
  already labels itself as a dated snapshot and supplies the repeat procedure.
- This sandbox cannot independently observe the host listener namespace. That
  does not invalidate the recorded 2026-07-18 provenance evidence; future
  implementation work must rerun the manifest's host-side read-only check
  before acting.

Neither risk is a defect in the bounded research deliverable.
