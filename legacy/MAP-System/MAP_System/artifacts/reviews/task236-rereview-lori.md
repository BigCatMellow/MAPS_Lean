# Re-review: TASK-236

task_id: TASK-236
reviewer: codex-lab-lori
task_owner: claude-lab-gome
submitter: claude-lab-zaro
review_date: 2026-07-23

## Verdict

CHANGES_REQUESTED

The two `REQUIRED` findings from
`MAP_System/artifacts/reviews/task236-review-lilo.md` are closed, and all five
registered acceptance criteria reproduce. One `REQUIRED` finding remains in
the declared operator-directed owner-liveness addition.

## Findings

### REQUIRED — A `busy` owner is live and working, not departed

Affected paths:

- `MAP_System/scripts/advisory_monitor.py`
- `MAP_System/tests/test_advisory_monitor.py`
- `MAP_System/artifacts/tests/task-advisory-monitor-delivery-note.md`

`check_owner_liveness()` treats only `available` as live. Every other known
status falls into `owner-unavailable`, including `busy`. MAP's durable status
contract explicitly defines `busy`, and `ai agent busy` sets it when an agent
is working. A task owned by that agent therefore produces a MEDIUM stale-owner
finding whose impact says the owner is departed, no one is accountable, and
the identity cannot object. All three claims are false for a busy agent.

The defect is currently hidden by the live fixture: zero nonterminal tasks have
a busy owner, so the reported 23 findings do not exercise this branch. A direct
probe with an `IN_PROGRESS` task owned by an agent whose SQLite and
`status.json` status are both `busy` produces:

```text
owner-unavailable / MEDIUM
Nothing detects a departed owner ... no one accountable ...
```

This is blocking for a standing observer because ordinary active work would
create persistent false-positive noise and misleading remediation advice.

Required change:

- Treat `busy` as a live owner state with no stale-owner finding.
- Add an explicit busy-owner fixture proving no finding.
- Keep `standby` as a separately described MEDIUM attention signal if desired:
  it can mean declared idle or temporarily unavailable, so the existing
  confirm-before-action suggestion is proportionate.
- Update the delivery note's judgment-call section and status table so they
  match the implemented contract.

If command-center truly wants busy owners surfaced, it must be a distinct,
truthfully worded occupied-owner signal rather than the departed-owner branch.

## Acceptance Criteria

| # | Result | Evidence |
|---|---|---|
| 1 | PASS | Read-only SQLite URI rejects `UPDATE`; pre/post SHA-256 values for `map.db`, `events.jsonl`, and `agents/status.json` are identical after a live run. Exit is 1 with findings. No mutation surface found. |
| 2 | PASS | Focused suite passes 23/23. Mirror drift and event-log interpretation now have isolated tests; T-3a through T-3d cover the four malformed claim shapes; the clean fixture exercises every check. Test remains registered in `run_tests.sh`. |
| 3 | PASS | Delivery note presents trigger, output surface, owner, grouping, and repeat-suppression as command-center decisions. No standing process was deployed. |
| 4 | PASS | Recurrence/novelty layer is specified as candidate-only, core-promoted, and outside the deterministic path. |
| 5 | PASS | Combined delivery note records the TASK-186 first-run catch and maps all criteria. |
| Added owner-liveness scope | CHANGES_REQUESTED | Expected live distribution reproduces exactly, but the busy-owner semantics above are incorrect. |

## Judgment Calls

1. **APPROVED is nonterminal: ACCEPTED.** Release is still owed, and the
   measured backlog exists entirely in APPROVED. Treating it as terminal would
   blind this check to the operator's actual problem.
2. **Busy owners are flagged MEDIUM: REJECTED.** Busy is a live working state,
   not evidence that an owner no longer exists.
3. **One finding per task: ACCEPTED.** Each task has its own release or
   reassignment action. Grouping and change-only display belong to the future
   output surface and are correctly left as command-center presentation
   decisions.

## Reproduced Verification

- Focused suite: 23/23 pass.
- Live monitor: exit 1, 23 findings.
  - 15 `owner-inactive`
  - 6 `owner-unavailable` for standby owners
  - 1 `expired-lease`
  - 1 `event-log-health`
- Owner distribution matches the delivery note:
  `codex-lab-mozu` ×11, `codex-lab-limo` ×6,
  `claude-lab-lure` ×3, `codex-lab-nivo` ×1.
- Full suite: pass=71, fail=3, total=74. The failures match the disclosed
  pre-existing research-artifact issue, non-canonical event warning at line
  2145, and the layer-1 cascade from that event warning.
- Scoped `map-git diff --check`: pass.
- Prior mirror desynchronization: closed; task mirrors and graph pass.

## Boundaries

- Review interaction over the earlier mirror desynchronization was
  coordination, not authorship, and creates no self-review conflict.
- `db/claims.py`, `scripts/map_task.py`, TASK-273, and INS-0039 were not
  changed or absorbed into this review.
