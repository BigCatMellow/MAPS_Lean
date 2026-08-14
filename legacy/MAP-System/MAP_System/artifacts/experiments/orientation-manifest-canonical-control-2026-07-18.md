# EXP-0004 Canonical Orientation Control Answer

- Scenario: resumed Claude agent; system-improvement lane
- Method: source verification before treatment comparison
- Measured after final write: `05104` bytes; `0601` words

## 1. What is the task state and owner?

- Answer: `TASK-227` is `CHANGES_REQUESTED`; its accountable owner is
  `claude-lab-gome`.
- Canonical sources: `MAP_System/tasks/TASK-227.json`; review record header in
  `MAP_System/artifacts/reviews/task227-review-lilo.md`.
- Confidence: high.
- Ambiguity: the older handoff's original `READY` statement is historical; its
  dated review update correctly supersedes it for recovery orientation.

## 2. What is the first valid action?

- Answer: Read the TASK-227 review and system-improvement handoff, then—only
  when ready to edit—run the normal rework transition for TASK-227 and resume
  the task's owner-led plan correction. The rework must address the five named
  review findings before resubmission. Do not create a replacement task merely
  because the operator wants continued improvement.
- Canonical sources: `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`
  ("Current Review Update"); `MAP_System/artifacts/reviews/task227-review-lilo.md`
  (five REQUIRED actions); `MAP_System/AGENTS.md` (SQLite claim/rework flow).
- Confidence: high.
- Ambiguity: the runner presently recommends `wait_or_reconcile` and has no
  ready task. That is compatible with the task's `CHANGES_REQUESTED` state;
  it does not replace the owner-led rework path.

## 3. What is the authority boundary?

- Answer: A Tier-1 core agent may revise and submit the task's implementation
  plan within its approved scope. It may not make binding AUTHORITY or POLICY
  decisions. In particular, the proposed rule restricting helper mutation is
  an AUTHORITY-class change and requires a command-center request/approval
  before an approved decision is recorded.
- Canonical sources: `MAP_System/DECISION_AUTHORITY_SYSTEM.md` (tiers,
  human-approval requirements, proposal-to-decision promotion);
  `MAP_System/artifacts/reviews/task227-review-lilo.md` (finding on §3a).
- Confidence: high.
- Ambiguity: none material; a core agent may draft/propose the decision but
  must not present it as binding.

## 4. What is the helper boundary?

- Answer: A helper may assist only as a visible, bounded, durable-scope
  support worker. It needs a named tag, owner, helper note, specific output,
  and stop condition. It cannot own TASK-227, take over its final integration,
  bypass review/approval gates, or directly record a binding decision.
- Canonical sources: `MAP_System/AGENTS.md` (Elastic Helper Agents and routine
  reviewer routing); `MAP_System/DECISION_AUTHORITY_SYSTEM.md` (Tier 2);
  `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`
  (guardrails).
- Confidence: high.
- Ambiguity: a helper may produce a recommendation or bounded research artifact;
  its coordinator decides whether to use it.

## 5. What is the interruption-safe recovery path?

- Answer: Start from durable task state, review, and handoff—not chat. Confirm
  live availability through hcom before relying on the durable status mirror.
  The current mirror records `claude-lab-gome` as `standby/out_of_tokens` until
  `2026-07-18T05:05:00-04:00`; after recovery, read the bounded rework record,
  transition TASK-227 to rework only when editing can begin, claim/heartbeat
  through the SQLite workflow, then submit for independent review. Until then,
  perform only non-mutating, bounded support work.
- Canonical sources: `MAP_System/agents/status.json`; `MAP_System/agents/README.md`
  (hcom is live authority; mirror is durable record); `MAP_System/AGENTS.md`
  (claim/heartbeat/submit); `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`.
- Confidence: high.
- Ambiguity: the runner's current `wait_or_reconcile` result is an orientation
  signal, not permission to modify another owner's task or invent new work.

## Source list

1. `MAP_System/tasks/TASK-227.json`
2. `MAP_System/artifacts/reviews/task227-review-lilo.md`
3. `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md`
4. `AGENTS.md`
5. `MAP_System/AGENTS.md`
6. `MAP_System/DECISION_AUTHORITY_SYSTEM.md`
7. `MAP_System/agents/README.md`
8. `MAP_System/agents/status.json`
9. `MAP_System/graph/runner.py` output, executed during this control pass

## Facts that must not be compressed away

- `TASK-227` is CHANGES_REQUESTED and owned by `claude-lab-gome`.
- The five review findings are required before resubmission.
- The helper-mutation rule is an authority proposal, not low-risk prose that a
  core agent can make binding alone.
- Helper work must remain visible, bounded, durable, and non-owning.
- Live hcom availability outranks the durable status mirror; the current
  recorded interruption is `out_of_tokens` through the stated ISO timestamp.
- Continued system improvement means resume the governed rework/evidence loop,
  not create autonomous work or bypass the task/review path.
