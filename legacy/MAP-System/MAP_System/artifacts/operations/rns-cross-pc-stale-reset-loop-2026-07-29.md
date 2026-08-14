# RnS cross-PC stale reset loop — 2026-07-29

## Status

Confirmed operational defect; no live service or canonical task state changed.

## Observed behavior

- `claude-lab-nene` received 15+ `recorded-reset-live` messages at roughly
  five-minute intervals despite remaining continuously live.
- After the operator-authorized agent cleanup stopped
  `codex-lab-replacement-valo`, the old session was resumed with the RnS
  prompt. Valo verified that TASK-305 remained `SUBMITTED`, with no claim,
  lease, open review, or background process, and confirmed it was safe to
  stop again.
- The cleanup preserved the fixed Biggie roster and current Smalls
  continuity holders.

## Reproduced cause

Biggie/KUDU is a read-only MAP mirror. Its exported
`MAP_System/agents/status.json` still records `claude-lab-nene` as
`standby/out_of_tokens` with a passed `resume_after`, while live hcom reports
the session as listening.

`live_due_recorded_resets()` correctly detects that mismatch and sends an
active-session nudge. It then calls `persist_agent_availability()`, which
opens the local `MAP_System/map.db` directly. That write cannot succeed on
the read-only mirror. The failure is stored in `failed_nudges` for only the
retry interval, so the same stale authoritative row causes another nudge on
the next eligible poll.

The current reviewed `register-agent` gateway operation does not resolve this
case: it is `INSERT OR IGNORE` and does not update an existing agent's
availability fields.

## Safety decision

- Do not make local mirror DB writable.
- Do not directly edit `agents/status.json`; it is an exported view.
- Do not stop the watcher without an operator decision, because it also
  provides legitimate reset and liveness recovery.
- Agents receiving the false `recorded-reset-live` message should preserve
  their current session and avoid changing task state solely because of the
  message.

## Required follow-up

After the reviewed TASK-308 gateway deployment is complete, implement a
bounded, independently reviewed cross-PC availability-clear path with these
properties:

1. An allowlisted authority operation updates only the named existing agent's
   `status`, `reason`, and `resume_after` fields under explicit preconditions.
2. The KUDU watcher uses that authority operation instead of writing local
   `map.db`.
3. A successful live-session nudge cannot repeat every polling interval while
   an authority clear is pending or unavailable; the pending state remains
   visible rather than being treated as success.
4. Tests cover mirror mode, repeated polls, real later session loss, terminal
   suppression, and fail-closed behavior for unknown agents or invalid state.
5. Deployment preserves RUKI as sole database authority and receives an
   independent security-framed review.

## Immediate containment

Valo was reopened a second time from the same RnS incident after its explicit
safe-to-stop report. The session was stopped again without changing TASK-305.
The local operational incident record was advanced to its existing terminal
probe state (`probes_sent: 6`, `gave_up: true`). This does not change MAP task
ownership, agent lifecycle state, or RUKI data; it only prevents the obsolete
KUDU watcher incident from launching Valo again.

Validation:

- `limit_watcher.py --once --dry-run` emits no Valo action.
- `limit-watcher-state.json` parses as valid JSON.
- The live roster contains only the fixed Biggie agents and current Smalls
  continuity holders.

After a later CCL restart, the same presumed-down race opened an incident for
the still-live fixed Codex slot (`codex-lab-mebo`). MAP already recorded MeBo
as available and hcom showed the original session active. That obsolete local
incident was likewise advanced to its terminal probe state. Dry-run now
classifies MeBo as live and would close the incident, with no reset/resume
probe action.

## Evidence

- `MAP_System/agents/limit-watcher-state.json`
- `MAP_System/scripts/limit_watcher.py`
  - `live_due_recorded_resets()`
  - `persist_agent_availability()`
  - recorded-reset loop in `run_once()`
- hcom events `3867`–`3951` (Valo reopen and safe stop)
- hcom message `3969` (Nene repeated false probes)
