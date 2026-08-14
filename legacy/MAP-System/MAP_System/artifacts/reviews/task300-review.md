# TASK-300 Review

task_id: TASK-300
reviewer: task299-security-review-todo
task_owner: codex-live
review_date: 2026-07-28

## Verdict

APPROVED.

TASK-300 passes independent pre-deployment and final workflow review. The
watchdog is bounded to mirror sync health: it records state, retries alerts
when the desktop notification bus is unavailable, rate-limits repeated failure
notifications, sends recovery notification after a notified failure, and does
not start UI, agent, Codex, Claude, Ollama, WezTerm, or local LLM processes.

## Acceptance Criteria Check

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | `map_authority_notify.py` persists failure state in `~/.local/state/map-authority/health.json` using an atomic tempfile/fsync/chmod/replace write. `test_first_failure_records_state_and_notifies` and `test_notification_retries_when_desktop_was_unavailable` cover persistence and retry when `notify-send` initially fails. |
| 2 | PASS | Repeated failure alerts are rate-limited by `last_notification_epoch` and `repeat_seconds`; `test_repeated_failure_is_rate_limited` verifies no per-minute notification storm. |
| 3 | PASS | Recovery after notified failure sends one recovery notification and records healthy state. `test_recovery_notifies_once_after_notified_failure` and `test_recovery_notification_retries_when_desktop_was_unavailable` verify recovery and retry when the desktop bus was unavailable. |
| 4 | PASS | The service template executes only `map-authority-sync`; the wrapper execs Python `map_authority_notify.py` with `--authority-bin map-authority`. No UI, Codex session, hcom agent, local LLM, Ollama, WezTerm, or Command Center UI process is started by the watchdog. |
| 5 | PASS | `install-map-system.sh` installs `map-authority-sync` and points the mirror service at it while preserving standalone and authority service defaults. |

## Files Reviewed

- `MAP_System/scripts/map_authority_notify.py`
- `MAP_System/templates/install/bin/map-authority-sync`
- `MAP_System/templates/install/systemd/map-authority-mirror.service`
- `MAP_System/tests/test_map_authority_notify.py`
- `MAP_System/notes/cross-pc-map-authority.md`
- `install-map-system.sh`

Reviewed checksums:

- `MAP_System/scripts/map_authority_notify.py`: `481cefb211bba0d20ed2bc60aed62f417ded863ac3fc96dc1f5653e878498e03`
- `MAP_System/tests/test_map_authority_notify.py`: `434764d8fe8b33eb942934e08cb2ad89874d0b5b0f8b4f8f6ccd56a70f89c775`
- `MAP_System/templates/install/bin/map-authority-sync`: `6f441f3d7bf5aa61282f28e3e028b5fb174263cca3bc36d2183e60f14f6c3e5f`
- `MAP_System/templates/install/systemd/map-authority-mirror.service`: `c1c503544808f632ef367fe9b22e8a70682a62bd9a83b921bc257bab9cda5965`
- `install-map-system.sh`: `c4a3994337f21af8fbc44a57ef0a2453da3aea1c4531e508e384512efff5e99d`
- `MAP_System/notes/cross-pc-map-authority.md`: `bcaba3d324d5f46457e2da07d2560c8c2caa7373893b6afa267ffc7a79a69d91`

## Forbidden Changes Check

PASS. This review wrote only `MAP_System/artifacts/reviews/task300-review.md`.
No implementation, installer, service, deployment, database, UI, or MAP state
file was edited directly by the reviewer. No services were activated by the
reviewer.

## Verification

Commands run during independent review:

- `PYTHONDONTWRITEBYTECODE=1 MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_authority_notify -v` returned 6/6 OK.
- `sh -n MAP_System/templates/install/bin/map-authority-sync install-map-system.sh` returned OK.
- `PYTHONDONTWRITEBYTECODE=1 MAP_System/.venv/bin/python -m py_compile MAP_System/scripts/map_authority_notify.py MAP_System/tests/test_map_authority_notify.py` returned OK.

Security and failure-mode checks:

- Notification retry: failure notification retries if the desktop notification
  call returns false; recovery notification also remains pending and retries.
- Rate limiting: repeated failure notification uses `repeat_seconds`, defaulting
  to 30 minutes.
- Recovery: a successful sync after a notified failure records healthy state and
  sends or retries a recovery notification.
- Error handling: sync stdout/stderr, including `TimeoutExpired` byte output,
  is normalized before compacting; operator-visible error text is whitespace
  normalized and truncated to 500 characters.
- State atomicity: health state writes use a sibling tempfile, JSON dump, flush,
  fsync, chmod `0600`, and `os.replace`.
- Subprocess safety: both `notify-send` and `map-authority sync` are invoked as
  argument arrays; no shell execution is used.
- Boot/no-GUI behavior: if `notify-send` fails because no graphical session or
  desktop bus is available, the watchdog records state and exits based on sync
  status; the user timer retries later.

## Live Deployment Evidence

The final workflow request reported the following live deployment facts, which
match the reviewed behavior:

- TASK-300 is installed on both hosts.
- KUDU `map-authority-mirror.service` uses `ExecStart=.../map-authority-sync`.
- Live sync completed with `Result=success` and `ExecMainStatus=0`.
- KUDU health state `health.json` reports `status=healthy`.
- The mirror timer is enabled.
- A test notification returned `0`.
