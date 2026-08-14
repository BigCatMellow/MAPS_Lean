# TASK-221 — persistent local RnS supervisor evidence

Date: 2026-07-17  
Owner: codex-lab-lilo  
Risk lane: medium (local coordination infrastructure; no application behavior)

## Retrieval capsule

- Purpose: Records the measured verification of the persistent local Rise and Shine session-limit supervisor that watches live provider evidence and resumes an exhausted agent only when its reset is due.
- Proves: Fresh-versus-stale quota detection, provider provenance, replay suppression, durable reset-window persistence, one-wake-per-window behavior, retry handling, service installation, and dry-run results.
- Applies to: TASK-221's local `limit_watcher.py`, its focused tests, and the installed user-service behavior verified on 2026-07-17.
- Does not provide: A guarantee for future provider formats, transcript encryption, general agent scheduling authority, remote supervision, or evidence about behavior after the recorded verification watermark.
- Evidence type: measured_outcome
- Status: historical

## Delivered behavior

- The existing deterministic `limit_watcher.py` now inspects bounded live
  transcript tails for fresh provider-originated quota records.
- Provider provenance is required: Claude rate-limit/429 metadata or a Codex
  provider event. Exact text copied into tool output, user prompts, or hcom is
  rejected.
- Records older than 15 minutes are rejected, preventing an old `resets 7pm`
  line from becoming tomorrow's schedule.
- Reset times receive a five-minute grace and are persisted SQLite-first as
  `standby / out_of_tokens` with ISO `resume_after`; mirrors are regenerated.
- Event fingerprints suppress duplicate handling.
- Successful wake status is also cleared SQLite-first; persistence failure
  leaves the due record retryable.
- The installed systemd user service runs every 300 seconds, restarts on
  failure, and is enabled for the user session/reboot lifecycle.
- Temporary one-shot RnS timers were removed after the persistent service was
  enabled.

## Verification

| Check | Result |
|---|---|
| `python3 MAP_System/tests/test_limit_watcher.py` | PASS — 32 focused tests |
| Fresh synthetic provider record | PASS — detected once; reset parsed with five-minute grace |
| Stale provider record | PASS — ignored |
| Exact marker quoted without provider provenance | PASS — ignored |
| `python3 MAP_System/scripts/limit_watcher.py --once --dry-run` against live sessions | PASS — no false detection after provenance hardening |
| `systemctl --user is-enabled map-rns-watcher.service` | PASS — `enabled` |
| `systemctl --user is-active map-rns-watcher.service` | PASS — `active` |
| Live process command | PASS — `/usr/bin/python3 -u .../limit_watcher.py --interval 300` |
| `systemctl --user list-timers 'map-rns-*' --all` | PASS — zero temporary one-shot timers |
| `MAP_System/scripts/run_tests.sh` | PARTIAL — 65/67 pass; TASK-221 graph/mirror/layer1/focused tests pass |

The two full-suite failures are pre-existing and outside TASK-221:

1. `validate_risk_registers`: ClearFront's `risks/RISK_REGISTER.md` lacks
   three required template headings.
2. `command_center_intake_test`: the real queue currently returns
   `next_route=None`, violating that test's environment-sensitive assertion.

The first full-suite run also exposed an active-output collision with the older
READY TASK-210. TASK-210 was retired as superseded, its watcher output ownership
was removed, and a dedicated supersession note preserves the history. Task
graph validation then passed.

## Operator-friction closeout

No new operator-friction candidate found beyond the failure mode TASK-221 was
created to resolve. The service now remains available when all cloud agents are
token-exhausted; no Ollama or paid model participates in monitoring.
