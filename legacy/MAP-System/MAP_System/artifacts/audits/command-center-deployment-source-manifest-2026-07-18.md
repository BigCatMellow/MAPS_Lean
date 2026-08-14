# CommandCenter Deployment-Source Manifest and Provenance Check

- task_id: TASK-235
- date: 2026-07-18
- owner: claude-lab-lure
- scope: read-only deployment-source manifest + repeatable runtime-provenance check
- source evidence: `MAP_System/artifacts/experiments/command-center-deployment-source-parity-audit-2026-07-18.md` (TASK-234, RELEASED)
- policy: `REQUIRE_CORE_DESTRUCTIVE_APPROVAL` gate cleared by explicit operator instruction (bigboss, 2026-07-18) to produce this read-only manifest. No deployment, installer, service, UI, policy, authority, shared-state, or TASK-227 change is made.

## 0. Guardrail and method

This manifest is a durable, read-only snapshot. All evidence below was gathered
with non-mutating checks only: `cat`/`sha256sum`/`stat`/`date` on files,
`ss -ltnp` for the listener, and `/proc/<pid>/{cmdline,cwd,environ}` plus `ps`
for process provenance. No process was started, stopped, or signalled; no file
under either source was written; the installer was not run. It supersedes
TASK-234's point-in-time fingerprints where files have since changed, and it
does **not** rewrite TASK-234's historical record.

Two source locations are referenced throughout:

- **Template** (install source): `MAP_System/templates/install/command-center-ui/`
- **Installed copy** (configured launch target): `~/Projects/CommandCenterUI/`
  = `/home/mellow/Projects/CommandCenterUI/` (same path; `~` = `/home/mellow`).

## 1. Configured launch chain (AC1)

```text
~/.local/share/applications/command-center-ui.desktop
  Exec= /home/mellow/.local/bin/command-center-ui
    -> COMMAND_CENTER_UI_DIR default = /home/mellow/Projects/CommandCenterUI
    -> exec  $COMMAND_CENTER_UI_DIR/run-command-center-app.sh
      -> app/window.py  (probes 127.0.0.1:8765; starts installed app/server.py
         only if the port is free, else reuses the existing listener)
```

Evidence:

- Desktop entry `Exec=/home/mellow/.local/bin/command-center-ui`, `Terminal=false`.
- Launcher `~/.local/bin/command-center-ui`: sets
  `PROJECT_DIR=/home/mellow/Projects/MultiAgentProject/Source`,
  `COMMAND_CENTER_UI_DIR` default `/home/mellow/Projects/CommandCenterUI`,
  exports `COMMAND_CENTER_UI_WORKSPACE=$PROJECT_DIR`, then
  `exec "$COMMAND_CENTER_UI_DIR/run-command-center-app.sh"`.
- window-probe behaviour unchanged from TASK-234 (`app/window.py` identical hash
  in template and installed copy — see §3).

## 2. Candidate-path accessibility (AC1)

| Candidate | Present | Notes |
|---|---|---|
| Configured launcher `~/.local/bin/command-center-ui` | yes | executable; targets the installed copy |
| Desktop entry `~/.local/share/applications/command-center-ui.desktop` | yes | invokes the launcher |
| Installed copy `~/Projects/CommandCenterUI/` | yes | readable; **not** a git checkout (no `.git`); dir mtime 2026-07-15 20:56 |
| Install template `MAP_System/templates/install/command-center-ui/` | yes | complete bundle; install source only |
| Historical external path `/home/home/Projects/CommandCenterUI` | no | absent this session; named only in historical records (TASK-234) — not a current boundary |

## 3. Template-vs-installed fingerprints (AC1) — current as of 2026-07-18

SHA-256 (first 16 hex) and mtime, template vs installed copy:

| File | Status | Template (mtime) | Installed (mtime) |
|---|---|---|---|
| `app/server.py` | **DIFFER** | `3881cdb17f86963d` (01:27:48) | `5adb2cade4c0da73` (11:14:28) |
| `app/window.py` | EQUAL | `03a5489cf59d97ae` (07-17 16:33:02) | `03a5489cf59d97ae` (07-17 16:33:02) |
| `src/chat.js` | EQUAL | `174bb454a901aa84` (18:10:57) | `174bb454a901aa84` (18:10:57) |
| `src/chat.html` | EQUAL | `5fe552c15463a827` (17:29:49) | `5fe552c15463a827` (17:29:49) |
| `src/chat.css` | EQUAL | `dc3fb949c116d90e` (18:10:58) | `dc3fb949c116d90e` (18:10:58) |
| `run-command-center-app.sh` | EQUAL | `31b378fd5bd1d88d` (07-15 20:56:01) | `31b378fd5bd1d88d` (07-15 20:56:01) |
| `README.md` | EQUAL | `b8b085e19e388485` (07-15 20:56:01) | `b8b085e19e388485` (07-15 20:56:01) |

### Change since TASK-234 (2026-07-18 earlier)

- **`src/chat.*` now EQUAL.** TASK-234 recorded these equal; they diverged when
  TASK-237 landed the attention-popup in the template and the "Send as"
  message-intent feature in the installed/live copy, then were re-equalized by
  the TASK-237 parity port (installed → template sync, operator-approved). The
  18:10/17:29 mtimes reflect that port.
- **`app/server.py` remains the one material mismatch, and the installed hash
  changed.** TASK-234 recorded installed `054b8f05…`; it is now `5adb2cad…`
  (installed mtime 11:14:28, later than TASK-234's recorded 2026-07-17 21:45:52).
  The template server (`3881cdb1…`) is unchanged. The functional gap TASK-234
  described still holds in kind: the template server fixes Ollama to loopback,
  disables background summaries, and bounds local-model work to the
  `qwen3.5:4b` advisory lane, whereas the installed server retains a
  configurable Ollama endpoint, a background summary model, and broader
  local-model launchers. This manifest records the mismatch; it does not choose
  between the two behaviours.

## 4. Configured target vs running listener (AC1) — VERIFIED this session

The configured target (§1) is distinct from whatever process currently owns the
port. This session establishes the running listener's provenance directly:

- Port `127.0.0.1:8765`: **occupied.** `ss -ltnp` → `python3` pid **54278**.
- `/proc/54278/cmdline`:
  `/usr/bin/python3 /home/mellow/Projects/CommandCenterUI/app/server.py --host 127.0.0.1 --port 8765`
  → the listener is the **installed copy's** `app/server.py`, **not** the template.
- `/proc/54278/environ`: `COMMAND_CENTER_UI_WORKSPACE` and `PROJECT_DIR` =
  `/home/mellow/Projects/MultiAgentProject/Source`;
  `COMMAND_CENTER_UI_SKIP_LAB_AUTOSTART=1`. `cwd` = the Source workspace.
- Freshness: process start `Sat 2026-07-18 14:22:03`; installed `server.py`
  mtime `11:14:28` (earlier). The on-disk installed server is **not** newer than
  the running process, so the listener reflects the current installed
  `server.py` (hash `5adb2cad…`), not a stale in-memory copy.

Conclusion: the current operator-facing backend is the installed copy, running
its present-on-disk `server.py`. Template-only backend edits do **not** reach
this listener until the installer is applied and the server is restarted.

## 5. Repeatable read-only provenance check (AC2)

Run from any shell; none of these mutate state. `PORT=8765`.

```sh
# (a) listener presence + owning pid
ss -ltnp 2>/dev/null | grep ':8765'
# (b) if occupied, resolve the pid's provenance (read-only)
PID=<pid from (a)>
tr '\0' ' ' < /proc/$PID/cmdline; echo
cat /proc/$PID/environ | tr '\0' '\n' | grep -E 'COMMAND_CENTER|PROJECT_DIR'
# (c) fingerprint drift, template vs installed
for f in app/server.py app/window.py src/chat.js src/chat.html src/chat.css \
         run-command-center-app.sh README.md; do
  sha256sum "MAP_System/templates/install/command-center-ui/$f" \
            "$HOME/Projects/CommandCenterUI/$f"
done
```

### Expected outcomes

| Port state | Provenance result | Interpretation | Safe action |
|---|---|---|---|
| **Free** (no listener) | n/a | No operator window bound; launching starts the **installed** `server.py`. | A launch or installer-then-launch is unambiguous; still requires the normal approval for any deploy. |
| **Occupied, VERIFIED** | `/proc/<pid>/cmdline` resolves to a known copy's `app/server.py` (as in §4: installed copy) | The running backend's source is proven; compare its file hash (§3) to decide if it is current. | No restart needed to identify source; a deploy still needs explicit approval + restart plan. |
| **Occupied, UNVERIFIED** | `cmdline`/`environ` unreadable, or points outside both known copies | Listener source is unproven; do **not** assume template or installed. | Do not deploy or restart on inference; escalate for operator decision before any change. |

The check never starts, stops, or modifies a process; "occupied, unverified"
resolves to escalation, never to a silent restart.

## 6. Bounded deployment decision gate (AC3)

No implementation source is selected by inference here. A future UI/backend
change must pick exactly one boundary and carry its own authorization:

1. **Template + intentional deployment.** Edit
   `MAP_System/templates/install/command-center-ui/…`, then separately authorize
   and run `install-map-system.sh` (default destination
   `$HOME/Projects/CommandCenterUI`; it backs up then copies the bundle,
   `install-map-system.sh:143-166`), then restart the server so the new
   `server.py` is the listener. Requires: explicit deploy authorization, a
   restart plan, and post-deploy re-run of §5 showing the intended hash live.
2. **Installed external-copy edit.** Edit `~/Projects/CommandCenterUI/…`
   directly. This is an out-of-repo path and requires **explicit operator
   approval for that external path**, exact output paths, and its own
   restart/verification plan.

Neither boundary is authorized by this manifest. The one open material decision
—reconciling `app/server.py` (template loopback/bounded-advisory vs installed
configurable/broader)—is recorded for an operator decision, not resolved here.

## 7. Outcome (AC4)

This manifest records the configured launch chain, candidate-path
accessibility, current template-vs-installed fingerprints, and a
**verified** running-listener provenance (installed copy, current on-disk
server), and specifies a repeatable no-write provenance check with expected
outcomes for free / occupied-verified / occupied-unverified ports. It defines
the template-vs-installed decision gate while selecting no source by inference.
No UI, deployment, installer, service, policy, authority, shared-state, or
TASK-227 change was made. It is an independently reviewable input to a future
implementation task.
