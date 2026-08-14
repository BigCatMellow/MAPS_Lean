# CommandCenter Deployment-Source Parity Audit

- task_id: TASK-234
- date: 2026-07-18
- owner: codex-lab-lilo
- scope: read-only source and launch-path audit
- result: `PARITY_NOT_ESTABLISHED — coordination-card implementation deferred`

## Purpose and guardrail

KICK-01 required evidence that a proposed Command Center change would reach the
operator-facing application before any implementation task was admitted. This
audit identifies the configured launch target, the installer/template path,
their observed relationship, and the uncertainty that remains. It does not
edit a UI, run the installer, restart a process, alter deployment state, or
change policy, authority, TASK-227, or shared state.

## Method and evidence boundary

Read-only checks used file existence, rendered launcher/desktop entries,
SHA-256 comparisons, `diff -qr`, installer source inspection, `bash -n`, and a
dry-run installer invocation with package, hcom, WezTerm, venv, and desktop
installation disabled. The dry run printed a plan only; it did not install or
restart anything. Moku independently traced workspace-only installer evidence;
Zero independently ran the contradiction pass against the explicitly
accessible installed candidate.

Supporting reports:

- `MAP_System/artifacts/experiments/task234-template-trace-moku-2026-07-18.md`
- `MAP_System/artifacts/experiments/task234-parity-contradiction-zero-2026-07-18.md`

## Candidate source and launch-path evidence

| Candidate | Observed result | Evidence | Assessment |
|---|---|---|---|
| Historical external path `/home/home/Projects/CommandCenterUI` | Absent in this session. | Direct existence check; it remains named by `artifacts/command-center-ui/README.md` and `artifacts/planning/commandcenterui-boundary-decision.md`. | Historical record is not a valid current source boundary here. |
| Installer template `MAP_System/templates/install/command-center-ui/` | Present, complete bundle. | Template README and source tree; `install-map-system.sh:143-166`. | Install source only; not proof of deployed state. |
| Configured launcher `~/.local/bin/command-center-ui` | Present. It sets the MAP workspace and defaults `COMMAND_CENTER_UI_DIR` to `~/Projects/CommandCenterUI`, then executes that directory's `run-command-center-app.sh`. | Rendered launcher lines 4-14. | Strong evidence for the configured launch target. |
| Desktop entry `~/.local/share/applications/command-center-ui.desktop` | Present and invokes the rendered launcher. The installed bundle's own desktop entry invokes `~/Projects/CommandCenterUI/run-command-center-app.sh`. | Rendered desktop entry; installed `CommandCenterUI.desktop`. | Confirms the intended operator launch chain. |
| Installed candidate `~/Projects/CommandCenterUI` | Present and readable; not a Git checkout. | Direct directory check; no `.git`; installed launcher and desktop targets. | The configured installed copy, but not proof of a currently running window. |

The configured **new-window entry path** is therefore:

```text
desktop entry -> ~/.local/bin/command-center-ui ->
~/Projects/CommandCenterUI/run-command-center-app.sh -> app/window.py
```

The installed `window.py` first probes `127.0.0.1:8765`. If the port is free,
it starts that installed copy's `app/server.py`; if the port is already open,
it reuses the listener and does not establish which source owns it. No active
operator-window/process verification was established in this audit. The path
above is therefore a configured-entry finding, not proof of a current server
or liveness claim.

## Parity result

**Parity is not established.** The installed candidate and template have equal
hashes for `README.md`, `run-command-center-app.sh`, `src/chat.html`,
`src/chat.js`, and `src/chat.css`; the installed desktop entry differs only by
its rendered absolute target. Ephemeral `__pycache__` and `runtime/` content
also differ, as expected for an installed copy.

The material source mismatch is `app/server.py`:

| File | Installed SHA-256 | Template SHA-256 | Consequence |
|---|---|---|---|
| `app/server.py` | `054b8f05…0e74` | `3881cdb1…f291` | Template-only backend work cannot be claimed to affect the installed copy; a pre-existing listener's source is separately unproven. |

The installed server retains a configurable Ollama endpoint, default
background summary model, and Goose/Pi/general local-model launcher
definitions. The template fixes Ollama to loopback, disables background
summaries, and limits visible local-model work to the bounded `qwen3.5:4b`
advisory lane. These are material runtime differences, not cosmetic drift.
This audit does not choose between those behaviours or change either source.

## Update and verification path

`install-map-system.sh` defaults its destination to
`$HOME/Projects/CommandCenterUI` (`lines 14-15`) and its bundle installer
backs up then copies the complete template to that destination (`lines
143-166`). A bounded dry run reported:

```text
CommandCenterUI: /home/mellow/Projects/CommandCenterUI
[dry-run] Back up …/Projects/CommandCenterUI …
[dry-run] Install bundled CommandCenterUI to …/Projects/CommandCenterUI
[dry-run] Keep unchanged …/.local/bin/command-center-ui
```

This establishes the *possible* update mechanism:

```text
MAP template -> explicit installer application -> installed copy -> launcher ->
window wrapper -> installed server only if port 8765 is free
```

It does not establish when the installed server was last refreshed, whether an
operator currently runs it, or whether applying the installer would preserve
locally meaningful changes. The installed server timestamp (`2026-07-17
21:45:52 -0400`) predates the template server timestamp (`2026-07-18
01:27:48 -0400`), and the absence of `.git` provides no revision history to
close that gap. Running the installer or starting/restarting the UI is outside
this task's no-deployment-change boundary.

`bash -n` passed for both the rendered launcher and installed runtime launcher;
that verifies shell syntax only, not current process provenance or visual UI
behaviour.

## Admission decision and exact future boundaries

**Do not admit a coordination-card implementation task yet.** A template-only
task would target a source whose deployed parity is disproven. An installed-copy
task would be an external-path edit and requires explicit operator approval,
exact output paths, a restart plan, and independent validation.

The smallest next MAP task is a non-UI **deployment-source manifest and
verification-protocol task**. It should preserve the observed configured path,
record hashes/mtime and template-versus-installed status, define a deliberate
installer-versus-installed-copy choice, and specify a no-write runtime
provenance check. It must not normalize or rewrite historical provenance.

Only after that task and the existing TASK-227 rework may a future UI task use
one of these evidence-supported boundaries:

1. **Template + intentional deployment:**
   `MAP_System/templates/install/command-center-ui/app/server.py`, selected
   `src/chat.*` files, `install-map-system.sh`, and—only if its contract
   changes—the rendered launcher template. The task must separately authorize
   and verify installer application.
2. **Installed external copy:**
   `~/Projects/CommandCenterUI/app/server.py` and exact selected `src/chat.*`
   paths. This requires explicit operator approval for that external path and
   its own restart/verification plan.

Neither boundary is authorized by TASK-234. The audit records the discrepancy
instead of silently selecting a source or treating a template as live.

## Outcome

TASK-234 satisfies the read-only parity-audit purpose: it identifies the
configured target, proves a material source mismatch, records the installer
copy mechanism and its limit, and leaves implementation correctly deferred.
No UI, deployment, policy, authority, shared-state, or TASK-227 change was
made.
