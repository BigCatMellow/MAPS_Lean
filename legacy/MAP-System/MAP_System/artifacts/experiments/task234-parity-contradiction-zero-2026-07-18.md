# TASK-234 Source-Parity Contradiction Pass — Zero

## Result

**Deployment-source parity is not established.** The accessible installed
candidate is the configured desktop-launch target, but MAP records still name
a different absolute path and its backend differs from the installer template.
No UI output path is safe to admit from the template alone.

## Evidence-backed findings

### P-01 — Recorded external path contradicts the configured launch path

- classification: **blocker**
- observation: The installed desktop entry runs
  `/home/mellow/.local/bin/command-center-ui`; that launcher defaults to
  `/home/mellow/Projects/CommandCenterUI` and exports the current MAP
  workspace (`/home/mellow/.local/share/applications/command-center-ui.desktop:5`;
  `/home/mellow/.local/bin/command-center-ui:4-14`). The directory is present
  and readable.
- contradiction: MAP's CommandCenter artifact and proposed boundary decision
  instead name `/home/home/Projects/CommandCenterUI`
  (`MAP_System/artifacts/command-center-ui/README.md:6-11`;
  `MAP_System/artifacts/planning/commandcenterui-boundary-decision.md:21-25,105-119`).
- implication: Those records cannot currently identify the configured target
  or provide a valid external-edit boundary.

### P-02 — Template and installed backend are not the same source version

- classification: **blocker**
- observation: `chat.html`, `chat.js`, and `chat.css` have equal SHA-256 values
  in the installed candidate and template. `app/server.py` does not:
  installed `054b8f05…0e74`; template `3881cdb1…f291`.
- evidence: The installed backend still enables a background summary model and
  older Goose/Pi/local-model launch definitions
  (`/home/mellow/Projects/CommandCenterUI/app/server.py:88-96,140-160,819-838,1438-1475`);
  the template disables background summarization and permits only the visible
  `qwen3.5:4b` advisory lane
  (`MAP_System/templates/install/command-center-ui/app/server.py:88-97,141-168,798-819,1450-1459`).
- implication: A template-only backend edit neither proves deployment nor
  preserves the installed runtime's present behavior.

### P-03 — The installer defines a copy deployment path, not ongoing parity

- classification: **evidence gap**
- observation: `install-map-system.sh` defaults its destination to
  `$HOME/Projects/CommandCenterUI` (lines 14-15), then copies the complete
  template bundle there on an installer run (lines 143-166).
- implication: The observable update chain is template → installer run →
  installed copy. No record in the inspected sources proves that the current
  installed copy was refreshed after the current template backend changed;
  its server mtime is `2026-07-17 21:45:52 -0400`, versus template
  `2026-07-18 01:27:48 -0400`. The candidate has no `.git` directory, so no
  repository revision supplies that missing link.

## Boundary and minimal read-only next action

The no-deployment-change boundary remains appropriate. Do not edit either
copy, run the installer, or restart a UI process. The smallest next action is
to retain a parity manifest in TASK-234's owner audit: configured launcher and
desktop paths, candidate accessibility, the four source hashes, installer copy
semantics, and the explicit unknown of which source the operator's currently
running UI used. Only after that audit can a separate approved task choose one
of two exact boundaries: template plus a declared installer/deployment step,
or the installed `/home/mellow/Projects/CommandCenterUI` copy plus its own
external-edit approval and verification plan.

## Rejected inference

The accessible installed copy is the configured launch target; it is **not**
proof that a currently running operator window was launched from it. No active
process or operator-session verification was established in this read-only
pass.
