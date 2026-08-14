# TASK-313 Disposition Review — Independent Read

- reviewer: claude-lab-mimi
- reviewed: `MAP_System/artifacts/recovery/ws1-path-ownership-prerequisite.md` (owner codex-lab-vumo)
- date: 2026-07-30
- against: Sequence Amendment 1 (approved) and live TASK-304/306/310/313 rows
- action taken: none — analysis only, no claim/mutation

## Verdict

Option A is **directionally sound but broader than Amendment 1's mandate as
written**, in two specific ways. Recommend conditional endorsement with two
guards, not unconditional A, and not C (C is strictly broader/riskier per the
document's own honest risk notes — no reason to prefer it).

## Verified

- Live rows confirm the doc's before-state table is accurate: TASK-304
  READY/`command-center`, TASK-306 CHANGES_REQUESTED/`claude-lab-nene`, both
  nonterminal on `server.py`; TASK-304 alone on `runner.py`; TASK-310 owns
  neither yet.
- TASK-313 itself is correctly owned by codex-lab-vumo, not risa — satisfies
  the ownership-separation guard from the Amendment 1 review.
- "No verb removes a single output path from a nonterminal task in place" is
  correct per `AGENTS.md`'s sanctioned verb list (`retire`, `rework`,
  `reassign-owner`, `extend-attempts`, `add-output-path`) — full retirement
  really is the only sanctioned way to free `runner.py`/`server.py` from
  TASK-304 today. Not a shortcut; a real tooling constraint, honestly stated.
- Option A does not touch TASK-306, TASK-308, or acceptance criteria —
  consistent with Amendment 1's exclusions.
- "Command Center disposition" is the correct authority tier per
  `AGENTS.md`'s hierarchy (bigboss/operator/Command Center are one top tier),
  so gating the mutation on that decision is sufficient authority — no
  separate operator sign-off needed beyond what's already required.

## Two Gaps Between "Retire TASK-304" And Amendment 1's Narrow Mandate

Amendment 1 authorized disposition "limited to the two conflicted
integration paths." TASK-304 has ten output paths; only two are contested.
Full retirement is a path-count-nine-out-of-ten wider action than the
amendment scoped, with two concrete side effects the current doc doesn't
account for:

1. **Silently resolves a different WS-2 baseline collision.** TASK-304 also
   collides with TASK-307 on `db/claims.py` and `context_rotation.py` — one
   of the original approved nine collision groups, chartered to TASK-311
   (before-state/decision/actor/after-state ledger), not TASK-313. If TASK-304
   is retired here, that collision vanishes before TASK-311 ever runs, with
   no entry in TASK-311's required nine-group ledger.
   **Guard:** the Command Center decision approving retirement must also
   explicitly record disposition of the TASK-304/TASK-307 pair, and TASK-311
   must cite that record rather than silently finding the collision already
   gone.

2. **Drops priority-100 work with no committed successor.** TASK-304 is the
   single highest-priority task on record (coordinator-enforcement,
   operator/security-gated). Its other five unique paths (`migration/schema.sql`,
   `scripts/run_manifest.py`, `.../index.html`, `test_coordinator_enforcement.py`,
   `workflow/role_registry.yaml`, plus its planning artifact) aren't in
   collision with anything — retiring the whole task discards them too, on
   the strength of "recreated later as a smaller follow-up," with no task ID,
   owner, or commitment attached.
   **Guard:** the Command Center decision should either open a concrete
   successor placeholder for coordinator-enforcement scope in the same
   action, or explicitly confirm the operator is deprioritizing that
   priority-100 work for now. Either is fine; silence is not.

## Recommendation To Command Center

Approve Option A's mechanism (retire TASK-304, keep TASK-306, reserve
`runner.py` for TASK-310 only if implementation needs it) **conditioned on**
the two guards above being part of the same disposition record. This keeps
the fix at the size Amendment 1 actually authorized and prevents the
TASK-304/TASK-307 collision and the coordinator-enforcement backlog item from
falling out of the record unattributed.
