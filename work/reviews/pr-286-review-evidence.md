# PR #286 review evidence

reviewer: pr286-reviewer-sana (independent reviewer, session maps-lean-sana / session-26 coordinator rotated out; did NOT author PR #286 — muzo (session-28 coordinator) authored the docstring tidy; muzo dispatched this review)
head_sha: d0760091dc872aa5c158c73e7d9aff554efb0b3e
independent: true
summary: APPROVE — no findings, no observations. Docstring-only tidy, 2 files, +12/-1, ZERO executable change. (1) runtime/recovery/production.py L392-398 `build_canonical_harness_service` docstring: "most likely via LEASE_EXPIRED" → now correctly states the guard veto carries `guard_code="LEASE_EXPIRED"` as an annotation and the resulting `OperationResult.code` is `HOOK_DENIED`, with a pointer to the #276 trace in work/notes/2026-09-03-roadmap-trajectory-check-21.md §2. Verified against the actual code, not the PR body: runtime/policy/harness_guard.py:101 `_deny("LEASE_EXPIRED", ...)` → :52 `HookOutcome(HookDirective.DENY, reason, annotations={"guard_code": code})` (guard_code is an annotation) → runtime/harness/service.py:137 `code = "HOOK_DENIED" if result.denied else "APPROVAL_REQUIRED"` (OperationResult.code is "HOOK_DENIED"). The new text is exactly right and matches duro's #276 reviewer verdict. traj-check-21 note §2 (lines 132-137 on origin/main) contains the exact trace the docstring cites. (2) scripts/check_review_evidence.py module docstring: +1 paragraph making explicit that the per-merge rebind churn is an *expected consequence* of the "walk-back stops at every merge commit" safety property — do NOT loosen the walk-back to cross merge commits (that would reopen the hole the docstring describes). References work/notes/2026-08-18-review-evidence-resync-classifier-friction.md (exists on origin/main) and INSIGHT-29a10ad4 (exists on origin/main — this PR is that insight's "promote (small)" disposition from trajectory check #22 §4.2). Accurate and well-grounded. CI `test` PASS (no behaviour change). Scope: `git diff origin/main --name-only` = exactly runtime/recovery/production.py + scripts/check_review_evidence.py; both changes are comment/docstring text only. Evidence bound to the post-rebase code head d0760091dc872aa5c158c73e7d9aff554efb0b3e (branch rebased onto 371d49e / traj-check-22 by the coordinator; the rebased diff is byte-identical to the pre-rebase 95aa3fe reviewed at Phase 1, so the Phase-1 review carries unchanged — bound once here, not double-rebound).

## Method

- Fresh detached worktree at PR #286 branch tip
  `d0760091dc872aa5c158c73e7d9aff554efb0b3e` (== origin/chore/docstring-tidy-recovery-cre
  after the coordinator's rebase onto 371d49e). Coordinator checkout untouched.
- `git diff origin/main` read in full — 2 hunks, both docstring text.
- Claim verification: `/usr/bin/grep -n "LEASE_EXPIRED|guard_code|HOOK_DENIED"
  runtime/policy/harness_guard.py runtime/harness/service.py` → harness_guard.py:101
  (`_deny("LEASE_EXPIRED", …)`), :52 (`annotations={"guard_code": code}`),
  service.py:137 (`code = "HOOK_DENIED" if result.denied`).
- `ls work/notes/2026-09-03-roadmap-trajectory-check-21.md
  work/notes/2026-08-18-review-evidence-resync-classifier-friction.md` → both
  present; `/usr/bin/grep -n "HOOK_DENIED|guard_code" work/notes/2026-09-03-roadmap-trajectory-check-21.md`
  → §2 trace at lines 132-137.
- `ls work/insights/*29a10ad4*` → present.
- Phase-1 findings posted to `@muzo` on hcom before this evidence commit.

## Disposition

**APPROVE.** No blocking or non-blocking findings — a correct, well-referenced
docstring tidy with no executable change. Evidence bound to code head
`d0760091dc872aa5c158c73e7d9aff554efb0b3e`.
