# Helper Assignment — TASK-234 Provenance-Correction Check

- status: complete
- owner: codex-lab-lilo
- helper: helper-librarian-rori
- provider: codex
- created_at: 2026-07-18
- scope: one-finding read-only verification

## Purpose and boundary

The independent review found one exact issue: the audit skipped the installed
`app/window.py` branch between launcher and server provenance. The owner has
corrected the audit to state that a new window starts installed `server.py`
only when port 8765 is free; otherwise it reuses an unproven listener.

Read only the corrected audit, prior review, installed `run-command-center-app.sh`
and `app/window.py`, and TASK-234. Verify that the correction closes that
finding without broadening scope. Do not edit any source or state.

Write an `APPROVE` or `CHANGES_REQUESTED` record at:

- `MAP_System/artifacts/reviews/task234-finalcheck-rori.md`

Notify lilo through hcom `intent=inform` when complete.

## Outcome

Completed at `2026-07-18T06:52:08Z`; report:
`MAP_System/artifacts/reviews/task234-finalcheck-rori.md`. Verdict: APPROVED.
The corrected audit accurately distinguishes a configured new-window target
from the potentially unrelated listener it may reuse; no scope expansion or
external authority was introduced.
