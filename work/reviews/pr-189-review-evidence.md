# PR #189 review evidence

reviewer: independent-reviewer-nova
head_sha: 8cea723584302e717dc3972b65fe314d88e0d844
independent: true
summary: APPROVE — Q4/Q5 each answered with an explicit decision; every supervisor.py / execution.py / harness_guard.py / run_lineage.py callsite claim re-derived at HEAD and confirmed; §3c correctly left UNKNOWN; diff docs-only.

## Method

- Fresh worktree at branch `canonical-enforcement-first-exposure-design`, not the main worktree.
- `git diff --name-only origin/main...HEAD`: only
  `work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md` and
  `work/reviews/pr-189-review-evidence.md`. No `runtime/`, `tests/`, or
  `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- `git diff --check origin/main...HEAD`: clean.
- head_sha walks past the evidence-only commit `636faac` to `8cea723`, the
  commit that adds the design note (same rule as scripts/check_review_evidence.py).

### Claims spot-checked against the repo at this HEAD (rule 14)

- `supervisor.py:24` `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}` — confirmed.
- `supervisor.py:11` `DEFAULT_BACKOFF_SECONDS = (300, 900, 1800, 3600, 7200)` — confirmed.
- `supervisor.py` `tick()`: the `elif str(result.code) in _CANONICAL_DENIAL_CODES`
  branch (L447) sets `action = "resume_denied"`, `resolved = True` and does NOT
  `continue`; control falls through `if not resolved:` (L469, skipped) to the
  unconditional `attempt += 1` / `state = "probing"` / `next_attempt_at` tail.
  Confirmed — a canonical denial consumes a retry attempt exactly as §1 states.
- The `state = "resolved"` branch (L362) and the `retry_budget_exhausted` branch
  (L384) both `continue`; the denial branch does not — §2c's "make the tail
  conditional, mirroring the branches that already continue" is accurate.
- `execution.py` `heartbeat` (def L103): refuses `claimed_by != worker_id` with
  `NOT_CLAIM_OWNER` (L122/126) and an already-expired lease with `LEASE_EXPIRED`
  (`if lease is not None and lease <= current`, L130-138, "claim lease has
  expired"). Matches §3a verbatim.
- `execution.py` `claim_task`: ACTIVE branch has `LEASE_ACTIVE` refusal for a
  live lease (L52), `ATTEMPT_LIMIT` for `attempt >= max_attempts` (L60),
  `recover = True` for an expired ACTIVE claim (L64), and the recovery UPDATE
  sets `status='ACTIVE'`, fresh lease, `attempt = attempt + 1` (L82-83).
  Matches §3b verbatim.
- `harness_guard.py` `_require_live_claim` → `NOT_CLAIM_OWNER` (L79/83);
  `RUN_WORKER_MISMATCH` (L70) and `RUN_REVISION_MISMATCH` (L72);
  `run_lineage.py` `RUN_WORKER_MISMATCH` (L309) / `RUN_NOT_OWNED` (L331).
  Supports §3b's "recover under a different worker id trips a worker-mismatch
  denial on the same pass" reasoning.
- `integrity.py` `compute_task_revision` exists (L108); §3c's question of
  whether claim-recovery's `attempt+1` feeds it is correctly left UNKNOWN and
  assigned to the implementer, not guessed.

### Decision completeness

- Q4: explicit decision — a canonical denial should NOT consume a transient
  attempt; distinct `state = "denied"`, deny code as `last_error`, flat
  reschedule, separate consecutive-denial ceiling → distinct `failed` code.
  Not a hedge. Correctly scoped as a separate slice, with the composition-root
  PR shipping current behaviour (acceptable only for default-off first exposure).
- Q5: explicit decision — the workflow is `maps claim <task> --worker-id
  <ORIGINAL worker> --lease-seconds N` then re-run the enforced pass, NOT
  `maps heartbeat` (which refuses an expired lease). Documented in the impl PR
  description + a `docs/CONTROL_PLANE_SETUP.md` subsection. One open risk (§3c)
  flagged UNKNOWN, not papered over.

## Verdict

APPROVE. Design-only, both questions answered with concrete decisions, all
consequential factual claims verified, the single UNKNOWN is explicit.
