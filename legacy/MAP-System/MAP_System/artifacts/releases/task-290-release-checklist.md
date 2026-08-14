# Release Checklist: TASK-290

## Header

```
task_id:      TASK-290
released_by:  lili-replacement-nisa
release_date: 2026-07-28
review_record: MAP_System/artifacts/reviews/task290-independent-review-task288-review-valo.md (CHANGES_REQUESTED),
                MAP_System/artifacts/reviews/task290-rereview-task288-review-valo.md (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Extends TASK-286's orchestrator on-demand lane-opening rule to independent
review. Before this task, `graph/runner.py` already reported
`next_route=review` with `submitted_tasks`, but nothing acted on that
signal automatically — a submitted task sat waiting until some agent
happened to notice (exactly what happened with TASK-288 this session: its
reviewer was spawned by hand).

New `scripts/review_routing.py` provides `needs_reviewer()` (wraps
`db.claims.get_open_review_claim`), `disqualified_reviewers()` /
`rotation_chain()` (combines the submission author with that author's
full rotation lineage from `shared/context-continuity.md`, walked to a
fixed point so multi-hop chains are covered, not just one predecessor
hop), and `eligible_reviewer()` (returns a non-disqualified live
candidate, or `None` to signal the caller should escalate to the operator
instead of spawning a compromised reviewer). Validated against real
production data: run against TASK-288 itself, it correctly disqualifies
both `lili-replacement-nisa` and its rotation predecessor
`claude-lab-lili`.

`notes/command-center-orchestrator-lifecycle.md` and the
`ai-command-center-lab-codex` orchestrator prompt both document the
behavior and explicitly point at `review_routing.py` rather than
re-describing the check in raw prose — the independent reviewer's first
pass (CHANGES_REQUESTED) caught that the initial docs described the logic
inline instead of naming the tested module, which is exactly the kind of
prose-drifts-from-code gap this session's `INS-0053` is about; fixed in
the second round.

This is additive to TASK-286, not a reversal of it: no lane auto-starts at
Command Center Lab boot as a result of this task. A reviewer spawns only
against live SUBMITTED state with no existing claim, matching the same
"open a lane only when work genuinely needs it" principle TASK-286
established. It is also deliberately not a standing role: three prior MAP
ideas proposing a standing scouting/adherence role (IDEA-0010, IDEA-0012,
IDEA-0013) were each redirected to a bounded cadence/audit instead, and
this task follows that same precedent.

## Verification

- `MAP_System/.venv/bin/python3 MAP_System/tests/test_review_routing.py` —
  7/7 PASS (claim presence/absence, author-only disqualification,
  single-hop and two-hop rotation-lineage disqualification, eligible-
  candidate selection, every-candidate-disqualified escalation case).
- `MAP_System/.venv/bin/python3 MAP_System/tests/test_release_gate.py` —
  9/9 PASS (unrelated suite, re-run to confirm no cross-task regression).
- `bash -n MAP_System/templates/install/bin/ai-command-center-lab-codex` —
  clean. This shell script's `PROMPT` is a single-quoted string; an
  earlier draft broke it with a stray apostrophe, caught before submission
  and again independently by the reviewer after the second edit.
- Independent review: `task288-review-valo`. First pass CHANGES_REQUESTED
  (one REQUIRED finding: neither doc named `review_routing.py`, both
  hand-described the check via raw primitives instead of pointing at the
  tested multi-hop-correct module — risk of a future hand-rolled
  single-hop regression). Fixed, text-only. Re-review APPROVED: reviewer
  independently reproduced both test suites, re-ran `bash -n`, and
  confirmed the doc/prompt wording now actually instructs using
  `review_routing.py` rather than just mentioning its filename.

## Rollback

Reversible by normal means: `scripts/review_routing.py` is new and
additive (no schema change, no migration); the doc and prompt edits are
textual additions to existing sections. Reverting this task's output
paths returns the orchestrator to TASK-286's prior behavior (no automatic
review-routing), with no data-layer cleanup required.
