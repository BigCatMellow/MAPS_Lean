# PR #189 review evidence

reviewer: PLACEHOLDER — pending independent reviewer assignment
head_sha: PLACEHOLDER
independent: true
summary: PLACEHOLDER — awaiting independent review. Do not merge until this file carries a real reviewer, the current head_sha, and an APPROVE verdict.

## Scope claim to verify

- `git diff --stat origin/main...HEAD` should show only `work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md` and this evidence file under `work/reviews/`.
- `git diff --check` clean.
- No `runtime/` code, no test, no `work/roadmaps/CAPABILITY_CHECKLIST.md`, no `tick()` logic touched.

## Claims the reviewer should re-derive at their own HEAD

- `runtime/recovery/supervisor.py` `tick()`: the `_CANONICAL_DENIAL_CODES` branch sets `resolved = True` but does NOT `continue`, so a canonical denial reaches the unconditional `attempt += 1` / `state = "probing"` / `next_attempt_at` tail (note §1).
- `runtime/state/execution.py` `heartbeat` refuses an already-expired lease with `LEASE_EXPIRED` (~line 130) and requires `claimed_by == worker_id` (note §3a).
- `runtime/state/execution.py` `claim_task` has a `recover = True` path for an expired `ACTIVE` claim that does `attempt = attempt + 1` (note §3b).
- The §3c UNKNOWN (does claim-recovery bump `compute_task_revision()`?) is correctly left UNKNOWN, not guessed.

## Checks performed

_(to be filled by the independent reviewer)_
