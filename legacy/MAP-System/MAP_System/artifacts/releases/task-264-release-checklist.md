# Release Checklist: TASK-264

## Header

```
task_id:      TASK-264
released_by:  mapfinish-guru
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Restores three CommandCenterUI local-model security controls that an
untracked 2026-07-21 edit silently reverted in the live `app/server.py`.
`risk_class=SECURITY`, `risk_severity=STRUCTURAL` — classifies `full` tier
under `release_task.py`'s `classify_release()`; no shortcut applies.

**Deliverable verified live and today** (independent re-check, not taken from
`artifacts/planning/release-backlog-triage-2026-07-28.md`'s table on trust):

- `../../CommandCenterUI/app/server.py:116-117`: `OLLAMA_HOST_PORT =
  "127.0.0.1:11434"`, `OLLAMA_URL = f"http://{OLLAMA_HOST_PORT}"` — loopback
  pin restored and consolidated to one configuration point.
- Line 122: `SUMMARY_MODEL = os.environ.get("COMMAND_CENTER_UI_SUMMARY_MODEL")
  or None` — background summarizer opt-in by default, not on.
- Line 1764 and the worker-thread start both guard on `SUMMARY_MODEL is
  None` — confirmed the guard genuinely disables the summarizer rather than
  only unsetting a label.
- `launch_local_agent()` (line 459) and `ollama_models()` (line 882) both pin
  `env["OLLAMA_HOST"] = OLLAMA_HOST_PORT` — discovery and launch use the same
  loopback-only endpoint, matching the template's rationale.
- Feature work preserved: `clean_response()`'s quoted-summary extraction
  (`clean_response` static method) is intact and unmodified.
- `python3 -m py_compile` on the live file: clean.
- No `server.py` process is currently running (`ps aux` checked) — no
  restart risk from this release; the fix takes effect on next launch.
- Live and template `app/server.py` are byte-identical (`diff -q` clean),
  confirming TASK-265's later reconciliation carried this fix into the
  template too.

**Shared-file updates complete**: `shared/decisions.md` DEC-029 ("Remote
OLLAMA_HOST is Permitted Only as Explicit, UI-Visible Configuration") and
DEC-030 (live/template merge direction) both cite and build on TASK-264's
restored hardening as their baseline; no further shared-file update is
needed for this task specifically.

**Decisions recorded**: operator authorization for TASK-264 itself is the
`DECISION_RECORDED` event at `events.jsonl:2229` (2026-07-21T18:40:00-04:00,
claude-lab-niko): "Operator (bigboss) authorized claude-lab-niko to own and
execute the CommandCenterUI security-hardening restore... clears the
REQUIRE_SECURITY_STRUCTURAL_APPROVAL pre-dispatch gate." One rework round
followed (`audit-untracked-bozo`'s 2026-07-21 review found two further gaps
of the same class — env-overridable `OLLAMA_URL` and an unpinned
`launch_local_agent`); both were fixed and bozo approved on the same day
(`events.jsonl:2231-2233`). The three controls verified live today match
that approved, reworked state, not the earlier pre-rework partial fix.

**Follow-up tasks created**: TASK-265 (`RELEASED`) is the explicit follow-up
that reconciled live/template `server.py` byte-parity and settled the
remote-Ollama policy question (DEC-029/030/033) that TASK-264 deliberately
left open.

**Event log entry prepared**: appended automatically by `map_task.py release`
on release (RELEASED event type, standard trace fields).

**Emergence capture considered**: already captured. This is downstream
execution of the pattern `emergence/synthesis/SYN-0001-two-readers-one-truth.md`
already synthesizes (an untracked edit colliding with concurrent hardening
work, "one piece of state, two readers, no declared authority") — no new
emergence capture warranted specifically for releasing TASK-264.
