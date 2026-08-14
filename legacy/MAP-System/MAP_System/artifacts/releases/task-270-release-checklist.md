<!-- hpom: file: artifacts/releases/task-270-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-270

## Header

```
task_id:      TASK-270
released_by:  claude-lab-gabi
release_date: 2026-07-22
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Fixes the `claim_review` false negative that let an unregistered reviewer
self-eject from an open review queue — a defect proven live on 2026-07-22 when
`codex-lab-lime` got `False` on an empty queue, read it as already-claimed
exactly as `review-guide.md` then instructed, and stood down. The submission
would have stalled with nobody reviewing it.

**Two defects fixed in `db/claims.py claim_review`:**

1. **Missing registration.** `reviews.reviewer_id` is a foreign key to
   `agents(agent_id)`, and `claim_review` had no registration step while
   `scripts/map_task.py` has had `ensure_agent` all along. An unregistered
   reviewer hit a `FOREIGN KEY` violation. Registration now uses the same
   `INSERT OR IGNORE` shape, so identity handling matches across modules.

2. **Indiscriminate exception flattening.** The function caught every
   `sqlite3.IntegrityError` and returned a bare `False`, indistinguishable from
   already-claimed. Classification is now by the **invariant, not the error
   text**: after an insert failure, `claim_review` re-checks whether an open
   claim actually exists (`WHERE completed_at IS NULL`) and returns `False` only
   if one does; otherwise it re-raises.

**Why the second fix was reworked once.** The first attempt classified the
already-claimed case with `"unique" in str(exc).lower()`. Independent re-review
(`codex-lab-lime`) reproduced that this also swallows `reviews.review_id`
primary-key collisions — the same silent stand-down for a different error. The
invariant-query approach removes the dependence on SQLite message text entirely.
This is a concrete case of independent review catching a defect that both the
implementation and its own first regression test missed.

**Guidance corrected.** `notes/review-guide.md` no longer equates every `False`
with already-claimed. It states all four `False` cases (task missing, not
SUBMITTED, self-review, open claim held), that any other integrity failure now
raises, and tells a reviewer who sees `False` on an apparently open queue to
check `get_open_review_claim` for an actual claimant before standing down.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py` — 12 pass
  (was 8). Three new regression tests: an unregistered reviewer claiming
  successfully, a genuine second claimant still refused (auto-registration must
  not weaken the one-open-claim rule), and a `review_id` PK collision with no
  open claim that must raise. The collision test was confirmed to FAIL against
  the earlier substring logic, so it genuinely covers the re-review finding.
- `bash MAP_System/scripts/run_tests.sh` — pass=72 fail=2, matching baseline.
  The two failures are the pre-existing non-canonical `TASK_SUBMITTED` event at
  `events/events.jsonl:2145` and are unrelated. Not "fixed" by rewriting the
  append-only log.
- `validate_task_mirrors.py`, `validate_events.py` (errors=0) — pass.
- Independent review + re-review: `artifacts/reviews/task270-review-lime.md`
  (CHANGES_REQUESTED, three REQUIRED findings) and
  `artifacts/reviews/task270-rereview-lime.md` (APPROVED — invariant classifier
  verified, forced collision raises, four-case contract aligned, four targeted
  mutants killed).

## Related records

- This closes the trap recorded before the session by `claude-lab-niko`
  ("claim_review missing ensure_agent") and referenced in operator memory.
- Same SYN-0001 shape as the other findings this session: one piece of state
  (agent identity) with two readers (`map_task.py` registers, `claims.py`
  assumed registered) and no declared authority. See INS-0038 for a sibling
  instance in the claim/mirror path.
