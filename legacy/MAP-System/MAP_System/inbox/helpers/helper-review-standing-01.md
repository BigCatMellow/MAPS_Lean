# Helper Assignment - Standing independent review helper

- status: active
- owner: claude-lab-neko
- provider: claude
- model: sonnet
- created_at: 2026-08-09
- scope: Sit and wait (Librarian-style, not a continuous scanner). On an
  explicit hcom request naming one SUBMITTED task, produce an independent
  review packet for that task under the standard MAP Review Standard
  (`AGENTS.md` -> Review Standard: BLOCKER / REQUIRED / RECOMMENDED /
  OPTIONAL findings). Do not act without an explicit named-task request.

## Why standing instead of one-off

Avoids re-spawning a fresh `helper-review-task-NNN` helper (and re-deriving
context) for every submission. Requested by bigboss 2026-08-09 after
claude-lab-neko proposed it as a lower-risk alternative to granting a
Librarian-style agent real approval authority.

## Boundaries (hard limits, do not exceed)

- No task claim, approve, or release authority. Item 4 of the MAP authority
  hierarchy (`MAP_System/AGENTS.md`) is explicit: helpers gain no task,
  review, release, routing, policy, or operator authority. This helper
  produces a review packet; a core agent (Codex or Claude) who is not the
  task's owner still performs the actual approve/release action.
- No self-review: if the requesting core agent is also the task's owner,
  this helper may still review (it is not the owner), but must say so
  explicitly in the packet so the requesting agent does not treat the
  packet as satisfying the no-self-review rule on its own — the formal
  approve step still has to come from a different core agent per Core
  Protocol #9.
- Do not claim tasks, edit `map.db`, or write task JSON/graph state.
- Do not act while MAP authority freshness is STALE (see
  `shared/context-continuity.md` / `map_authority.py route`) — a review
  packet produced against stale mirror state is not trustworthy evidence.
  Say so and stop if the caller hasn't already confirmed freshness.
- Findings go in `MAP_System/artifacts/reviews/` per the existing review
  artifact convention (see `validate_review.py`), plus a short hcom
  `--intent inform` back to the requester when the packet is ready.
- Owner (claude-lab-neko) is accountable for integrating or discarding this
  helper's output, and for flipping `status` to `complete`/`stopped` when no
  longer needed (helper capacity is currently 3/4; this note is the 4th).

## Requesting a review

Live identity: `helper-review-standing-zolu` (tag `helper-review-standing`,
spawned 2026-08-09 by claude-lab-neko, batch 5f405209). Send hcom to that
name or the tag naming: task ID, output paths to review, and why (owner
conflict, no other reviewer available, etc.). See `AGENTS.md` -> Routine
Reviewer Conflict Routing for the packet format.
