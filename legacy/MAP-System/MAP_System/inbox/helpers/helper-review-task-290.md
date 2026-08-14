# Helper Assignment - Independent review of TASK-290 (orchestrator auto-spawns a reviewer for unclaimed SUBMITTED tasks)

- status: active
- owner: lili-replacement-nisa
- provider: claude
- model: sonnet
- created_at: 2026-07-28
- scope: Independent review of TASK-290's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `lili-replacement-nisa` or `claude-lab-lili` (same
  disqualification reasoning as `helper-review-task-288.md` — rotation
  lineage, not just literal agent_id). `task288-review-valo` is neither, so
  reassigning this second review to the same reviewer is not a conflict;
  it also already has full context on the surrounding code from TASK-288.

## Tier escalation

Same justification and same approver reasoning as
`helper-review-task-288.md`'s escalation (codex still down, only other
live Claude session is the disqualified `claude-lab-lili`) — not repeated
here in full. Sonnet, one bounded review.

## Why this task exists

Directly follows TASK-288/F5's closeout: the operator asked whether
"catching what self-review misses" should become a standing part of
Command Center Lab startup, the same way Librarian/E-I/Triage are
sometimes described. Checked the actual precedent first
(`emergence/ideas/IDEA-0010`, `IDEA-0012`, `IDEA-0013` — each proposed a
standing scouting/adherence role and each was redirected to a bounded
cadence/audit instead; `notes/command-center-orchestrator-lifecycle.md`
TASK-286, released this session, actively *removed* Librarian/Claude/Pi
from default auto-start for the same reason: idle standing lanes
accumulate noise). TASK-290 is the cadence-shaped version instead: extend
the orchestrator's existing on-demand lane-opening rule to independent
review specifically, triggered by `graph/runner.py`'s existing
`next_route=review` signal, not a new standing role and not a change to
CCL's default boot lanes.

## What TASK-290 actually built

- `scripts/review_routing.py` (new): `rotation_chain()` walks
  `shared/context-continuity.md`'s embedded rotation ledger (reusing
  `context_rotation.py.parse_master`, not a new parser) to find every
  ancestor/predecessor identity of a given agent. `disqualified_reviewers()`
  combines the submission author (`db/review_authorship.get_submission_author`)
  with that author's full rotation lineage. `needs_reviewer()` wraps
  `db/claims.get_open_review_claim`. `eligible_reviewer()` picks one live,
  non-disqualified candidate, or `None` if every live candidate is
  disqualified (the caller should then escalate to the operator instead of
  spawning a compromised reviewer).
- `tests/test_review_routing.py` (new, 7 tests): claim presence/absence,
  author-only disqualification, single-hop and two-hop rotation-lineage
  disqualification, eligible-candidate selection, and the
  every-candidate-disqualified escalation case.
- `notes/command-center-orchestrator-lifecycle.md`: new section
  documenting the auto-spawn behavior — check `get_open_review_claim`,
  determine disqualified reviewers, spawn a visible tagged helper with a
  durable helper note if an eligible candidate exists, escalate to bigboss
  via `--intent request` if not.
- `templates/install/bin/ai-command-center-lab-codex`: the orchestrator's
  `PROMPT` string gained one clause implementing the same logic inline
  (this is a single-quoted shell string — watch for stray apostrophes if
  you edit it further; the first version of this edit broke the script's
  syntax with one).

## Input paths (TASK-290's registered output_paths)

- `MAP_System/notes/command-center-orchestrator-lifecycle.md`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex`
- `MAP_System/scripts/review_routing.py`
- `MAP_System/tests/test_review_routing.py`

## Task record

`MAP_System/tasks/TASK-290.json` — read `acceptance_criteria` there.

## Expected review artifact

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence.
2. **Reproduce, don't trust**: run
   `MAP_System/.venv/bin/python3 MAP_System/tests/test_review_routing.py`
   (7 tests) yourself. Also run
   `bash -n MAP_System/templates/install/bin/ai-command-center-lab-codex`
   to confirm the shell script is still syntactically valid — this is
   exactly the kind of thing a self-review would plausibly skip (it broke
   once already during this task, from an apostrophe in the inserted
   text).
3. Read `rotation_chain()` in `scripts/review_routing.py` and confirm the
   fixed-point walk is actually correct for a multi-hop lineage (not just
   the one-hop case) — the test suite has one two-hop test
   (`test_rotation_chain_walks_multiple_hops`); consider whether a cycle
   in the rotation ledger (should not exist in practice, but the walk
   doesn't explicitly guard against one) could infinite-loop. It shouldn't
   (the `changed` flag only re-loops while new members are added to a
   finite agent-id universe), but verify the reasoning yourself.
4. Sanity-check against real live data, same way I did before submitting:
   `MAP_System/.venv/bin/python3 MAP_System/scripts/review_routing.py TASK-288 --live-agent lili-replacement-nisa --live-agent claude-lab-lili --live-agent claude-lab-venu` — should disqualify both lili identities and pick venu. Confirm this still holds.
5. Whether the orchestrator-prompt clause and the lifecycle-doc section
   actually describe the *same* behavior as `review_routing.py`
   implements, or have drifted from it already — this is the exact class
   of gap TASK-288's own review caught (docs and code stating slightly
   different things). Read all three side by side.
6. Whether it was reasonable to build `review_routing.py` as real,
   tested code rather than leaving this purely as prompt guidance for the
   orchestrator to interpret each time — given this session's `INS-0053`
   finding (prose-only rules get missed even by the agent who just wrote
   about that failure mode), is this the right amount of mechanization,
   or should more of the orchestrator's decision (not just eligibility
   checking, but the actual spawn trigger) be code rather than prompt?
   Not necessarily a blocker — record your view either way.
7. Forbidden-changes check: everything touched should be in TASK-290's
   registered `output_paths` above. `MAP_System/inbox/helpers/` note
   files (this one and the TASK-288 one, now marked complete) are
   process/coordination artifacts, not task output, consistent with how
   TASK-288's review handled the same category.

Save the review artifact to
`MAP_System/artifacts/reviews/task290-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-290", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself and verify canonical
status actually changed. Report your verdict back to `lili-replacement-nisa`
and `bigboss` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.
