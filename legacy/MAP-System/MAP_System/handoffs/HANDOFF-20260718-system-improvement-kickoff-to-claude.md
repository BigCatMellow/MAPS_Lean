# HANDOFF 20260718 System Improvement Kickoff to Claude

Task ID: N/A
Sender: codex-lab-lilo
Intended recipient: claude-lab
Status: SUBMITTED
Created: 2026-07-18 00:00 EDT

## Context

Recent work converted the system-improvement discussion into durable notes:

- `MAP_System/notes/book-reading-for-system.md`
- `MAP_System/notes/book-lessons-agent-system.md`
- `MAP_System/notes/system-improvement-kickoff.md`
- `MAP_System/tasks/TASK-227.json`

The project framing that should govern the next pass is:

- MAP is a coordination system that uses AI workers.
- Improvements should target structure, visibility, feedback, authority, and durable learning.
- Hidden state and hidden authority are the main risks to avoid.
- Helper scope should stay narrow and reviewable.

## What Was Captured

The kickoff note currently groups the work into these workstreams:

- visible coordination surface
- durable memory and learning
- helper boundaries
- discovery and review loop
- monitoring and nudge behavior
- Command Center UX cleanup

The book lessons note now translates the reading into MAP-specific guidance, with chapter anchors preserved for recovery.

The task record for the next pass is:

- `TASK-227` - Turn system-improvement kickoff into implementation plan
- Owner: `claude-lab-gome`
- Status: `READY`
- Output path: `MAP_System/notes/system-improvement-implementation-plan.md`

## Requested Next Step

Pick up from `MAP_System/notes/system-improvement-kickoff.md` and turn the highest-priority workstreams into concrete implementation tasks with observable acceptance criteria.

### Current Review Update — 2026-07-18

`TASK-227` was reviewed and moved to `CHANGES_REQUESTED`. Its rework record is
`MAP_System/artifacts/reviews/task227-review-lilo.md`. Before resubmitting the
plan, resolve its five bounded points: define status-read-model precedence and
freshness; make the index population/test/ownership observable; route the
helper no-mutation rule as an AUTHORITY-class decision; add an evidence-intake
loop; and state the north-star practice-project outcome plus a measure for
each immediate task. Rework with `map_task.py rework` only when ready to edit;
then resubmit under the normal task flow.

Prefer the following order:

1. Visible coordination surface
2. Durable memory and learning
3. Helper boundaries
4. Discovery and review loop
5. Monitoring and nudge behavior
6. Command Center UX cleanup

## Broader Operator Direction

Outside ClearFront, the operator wants the system-improvement lane to stay active:

- keep improving the MAP system itself;
- read the books and other references that help explain how to streamline and strengthen the system;
- use E/I and any other bounded helpers that can find flaws while the system is being designed and run;
- run hypothetical end-to-end project passes to look for holes in the system before they become failures;
- take notes durably and report back with the findings.
- Treat current MAP structure as revisable from the ground up. A foundational
  alternative is welcome when evidence identifies a real structural failure
  and a reversible experiment can test it; neither legacy nor novelty is a
  sufficient reason by itself.
- Continue the improvement lane as a bounded observe → experiment → evidence
  → tune → re-measure cycle. Assess whether durable notes and wikilinks lower
  context cost without losing authority, provenance, or actionable detail;
  compare HPOM with evidence-backed real operating models and retain only the
  useful parts that fit MAP's visible-human-control constraints.

## Guardrails

- Do not let a helper become an unreviewed policy engine.
- Keep operator-visible state the default.
- Use durable files as the source of truth.
- Promote only work that has clear acceptance criteria.
- Keep reminder and monitor behavior visible, explainable, and non-noisy.

## Notes for Resume

The user explicitly wants Claude to handle the implementation planning when it comes back. Start from the kickoff note rather than re-deriving the discussion from chat.
