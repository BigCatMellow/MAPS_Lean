# System Improvement Kickoff

- Status: `open`
- Owner: `codex-lab-lilo`
- Source paths:
  - `MAP_System/shared/architecture.md`
  - `Guidelines/6.13/MAP-System/00-MAP-Index.md`
  - `Guidelines/6.13/MAP-System/01-MAP-Thesis.md`
  - `Guidelines/6.13/MAP-System/07-MAP-Philosophical-Foundations.md`
  - `MAP_System/notes/book-lessons-agent-system.md`
  - `MAP_System/notes/book-reading-for-system.md`
  - `MAP_System/notes/architect-agent-guide.md`
- Outcome location: `MAP_System/notes/system-improvement-kickoff.md`

## Purpose

Capture the implementation plan for the recent system-improvement thread as a project kickoff record. The goal is to make the next execution pass easy to resume, easy to review, and hard to drift.

## North-Star Outcome

MAP succeeds when an operator can take a real project from intent to a useful,
reviewed result — and an available agent can recover that path after an
interruption — without hidden authority, chat archaeology, or process work
that exceeds the work's risk. The system should learn this capability like a
walker learns balance: attempt a small complete path, observe where it falls,
add only the support that changes the next attempt, and keep testing the
outcome rather than optimizing isolated motions.

Every proposed improvement should therefore state which part of this outcome
it improves and what observation would show that it did not help. Metrics can
include time-to-correct-orientation, files/context needed to reach a valid
first action, recovery correctness after interruption, operator ability to
identify ownership/blockers, and defects that escape a risk-calibrated review.

## Design Spine

MAP is a coordination system that uses AI workers. The work is therefore about structure, feedback, authority, visibility, and durable memory.

The kickoff uses the following constraints:

- Prefer shared durable state over chat memory.
- Make operator-visible state the default.
- Keep helper scope narrow and reviewable.
- Use explicit decisions and fitness checks.
- Treat every model-backed helper as bounded analysis, not hidden authority.
- Convert repeated confusion into durable notes or rules.
- Treat MAP's current architecture, roles, and gates as revisable hypotheses.
  A finding may challenge a foundational assumption when it identifies a
  concrete failure mode, compares a materially simpler alternative, and names
  a smallest reversible experiment. Existing structure is evidence, not an
  exemption from review.

## Working Principles

### From `Thinking in Systems`

- Fix the loop, not just the symptom.
- Look for leverage points before adding more process.
- Make delays visible when they matter.

### From `Sources of Power`

- Optimize for decision support under uncertainty.
- Preserve intent, not just status.
- Use story, simulation, and concrete examples when they shorten real operator judgment.

### From `Fundamentals of Software Architecture`

- Write down architecture decisions.
- Govern the important constraints with fitness checks.
- Treat tradeoffs as real, even when they are not visible yet.

### From `The Design of Everyday Things`

- Make state obvious.
- Make actions discoverable.
- Make feedback immediate enough to confirm the action.
- Constrain error-prone operations rather than only documenting them.

### From `AI Engineering`

- Bound the context.
- Evaluate outputs against the actual job.
- Keep feedback loops explicit.
- Never let a model call become an unreviewed control plane.

### Foundational Reconsideration

The improvement pass must be able to discover that a root-level MAP design
choice is wrong or has outlived its purpose. This does **not** create an
automatic mandate to rebuild the system: the proposal must distinguish a
verified structural failure from ordinary implementation friction, preserve
the useful behavior that would otherwise be lost, and begin with the smallest
safe experiment. Retaining a design merely because it already exists is not a
valid reason; replacing it merely because replacement is novel is not valid
either.

### Continuous Improvement Cycle

While this system-improvement lane is active, use a visible, bounded loop:

1. Observe a real workflow or run a small practice scenario.
2. Record the baseline, friction, and the hypothesis in a durable artifact.
3. Test the smallest safe alternative, including a first-principles
   alternative when the existing layer itself may be the problem.
4. Compare the outcome to the baseline; preserve both positive and negative
   evidence.
5. Tune through the ordinary task/decision gates, then repeat on the next
   highest-value uncertainty.

Do not keep an agent busy merely to produce activity. A completed pass returns
to a visible listening state until it has another concrete question. Token
economy is itself a measured outcome: durable notes, indexes, and wikilinks
must reduce retrieval cost without hiding the authority or evidence needed to
act.

## Implementation Workstreams

### 1. Visible Coordination Surface

Goal: every important agent and helper state should be visible to the operator.

Implementation notes:

- Keep the Command Center as the attention surface.
- Show status, last meaningful action, current mode, and failure state directly.
- Preserve clear pause/resume/refresh behavior.
- Avoid hidden background work unless it is explicitly designed to be invisible and safe.

Acceptance shape:

- An operator can tell what is active, what is paused, and what needs attention without reading the repo manually.

### 2. Durable Memory and Learning

Goal: turn repeated work into stored knowledge rather than repeated re-explanation.

Implementation notes:

- Store lessons in `MAP_System/notes/` when they are reusable.
- Promote recurring issues into `shared/decisions.md`, `shared/improvement-backlog.md`, or task files when they are actionable.
- Keep helper conclusions in review artifacts or handoffs when they are historical evidence.

Acceptance shape:

- A new session can recover the project’s current reasoning from files alone.

### 3. Helper Boundaries

Goal: local helpers and core agents should have explicit lanes.

Implementation notes:

- Local helpers may summarize, draft, classify, or check, but should not silently mutate core truth.
- Core agents own judgment, promotion, and decision accountability.
- Every helper should have a named purpose, a visible record, and a bounded output path.

Acceptance shape:

- No helper can become an unreviewed policy engine.

### 4. Discovery and Review Loop

Goal: new ideas should enter through a disciplined discover-evaluate-adopt path.

Implementation notes:

- Keep the Discovery Agent proposal-only.
- Freeze known findings before helper output.
- Adjudicate novelty, utility, and scope drift explicitly.
- Reject ideas that are interesting but not justified.

Acceptance shape:

- Discovery can find new opportunities without automatically promoting them.

### 5. Monitoring and Nudge Behavior

Goal: reminders and scheduled nudges should be visible, intentional, and non-noisy.

Implementation notes:

- Track scheduled nudges in durable notes or task records.
- Define when a nudge should be `inform` versus `request`.
- Use a monitor/helper only if it has a bounded purpose and a visible output path.
- Avoid invisible background processes that the operator cannot inspect.

Acceptance shape:

- A scheduled reminder is recorded, explainable, and observable in the same system that depends on it.

### 6. Command Center and UX Cleanup

Goal: the operator surface should reduce interpretation work.

Implementation notes:

- Use labels that describe consequences, not just actions.
- Prefer a card or panel for each distinct agent role.
- Show hover/help detail where it helps decision-making.
- Keep the layout aligned with actual workflow stages.

Acceptance shape:

- The operator can infer what to do next from the UI without hunting through files or chat history.

## Suggested Initial Order

1. Freeze the current learning notes and kickoff plan.
2. Convert the most recent system-improvement threads into durable backlog items or task files.
3. Tighten the visible coordination surface.
4. Strengthen helper boundary notes and acceptance criteria.
5. Add or refine monitoring/nudge behavior only after its visibility path is clear.
6. Keep extracting lessons from the book set into system rules.

## Open Questions

- Which improvements become tasks immediately versus backlog notes?
- Which helper roles need visible UI cards now?
- Which reminders should be tracked as operator-facing events rather than background automation?
- Which rules belong in `shared/decisions.md` versus `notes/`?

## Follow-Up

- Review this kickoff against `shared/current-state.md` before implementation.
- Create tasks from the highest-priority workstreams only.
- Keep new learning durable as it appears.
