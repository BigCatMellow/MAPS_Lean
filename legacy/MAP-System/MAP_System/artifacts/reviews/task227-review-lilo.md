# Review: TASK-227 system-improvement implementation plan

task_id: TASK-227  
reviewer: codex-lab-lilo  
task_owner: claude-lab-gome

## Verdict

CHANGES_REQUESTED

## Acceptance Criteria Check

- PASS — The six current workstreams are in an explicit priority order with
  grounded reasons, and the plan correctly avoids re-planning recently shipped
  work.
- PARTIAL — Each workstream names actions and file targets, but the immediate
  slate lacks three constraints needed to turn the actions into safely
  implementable tasks: source-conflict behavior for the status surface, a
  bounded/testable index population, and an authority decision route for the
  proposed helper-mutation rule.
- PASS — The note links to both the kickoff and book-lessons records as
  resumable context.

## Files Reviewed

- `MAP_System/tasks/TASK-227.json`
- `MAP_System/notes/system-improvement-implementation-plan.md`
- `MAP_System/notes/system-improvement-kickoff.md`
- `MAP_System/notes/book-lessons-agent-system.md`
- `MAP_System/artifacts/experiments/system-improvement-plan-challenge-2026-07-18.md`
- `MAP_System/artifacts/experiments/map-practice-lifecycle-audit-2026-07-18.md`
- `MAP_System/artifacts/experiments/map-discovery-practice-lifecycle-2026-07-18.md`
- `MAP_System/DECISION_CLASSES.md`
- `MAP_System/DECISION_AUTHORITY_SYSTEM.md`

## Forbidden Changes Check

TASK-227's only registered output is the plan note. No implementation, policy,
decision, task-state, or runtime mutation appears in the submitted output.

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/notes/system-improvement-implementation-plan.md` §1a | The proposed status surface combines `agents/status.json`, `map.db` claims, and event-log activity but does not define field authority, freshness, or the operator-facing behavior when those sources disagree. Existing lifecycle evidence shows live/durable ambiguity; rendering without this contract can make stale state look authoritative. | Add a compact read-model contract to the 1a task shape: source of each field, timestamp/freshness treatment, conflict/unknown state, and one deterministic mixed-state test in addition to a screenshot. Keep existing sources; do not add a new state store. |
| REQUIRED | `MAP_System/notes/system-improvement-implementation-plan.md` §2a | The phrase “any active convention in ≤2 hops” has no bounded initial inventory, owning update path, or lookup sample. It cannot distinguish a useful index from another incomplete directory. | Define the initial indexed population, a concrete five-convention lookup acceptance sample, how a new note is classified, and its maintainer/update path. Defer a validator until actual index drift is measured. |
| REQUIRED | `MAP_System/notes/system-improvement-implementation-plan.md` §3a and “decisions.md vs notes” answer | The plan calls “helpers may never mutate core truth” a low-risk documentation batch but also correctly identifies it as a `decisions.md` item. It changes who may act, so `DECISION_CLASSES.md` makes it an AUTHORITY-class decision requiring command-center approval. | Split the authority proposal from the documentation batch, or make its exact AUTHORITY class, command-center request, and post-approval record prerequisites explicit. Do not present this rule as independently implementable low-risk prose. |
| REQUIRED | `MAP_System/notes/system-improvement-implementation-plan.md` immediate slate | The plan predates the operator-directed practice lifecycle, token-efficiency, operating-model, and philosophical-discovery evidence loop. Without a small intake section, new evidence will either be ignored or silently grow the slate. | Add an “evidence intake and iteration” subsection: link the practice-lifecycle/discovery artifacts already complete, state that new experiment results become candidates rather than automatic tasks, and name how the next plan revision considers their measured evidence. Do not create a permanent autonomous policy engine. |
| REQUIRED | `MAP_System/notes/system-improvement-implementation-plan.md` design spine and immediate slate | The plan lists valuable workstreams, but it does not state the concrete operator outcome they jointly serve or how a practice-project loop will show that a change helped. That risks optimizing individual motions (more status, more notes, more rules) without teaching the system to complete the real lifecycle. | Add a short north-star outcome for an operator-guided project from intent through interruption/recovery to reviewed release. For each immediate task, name the outcome slice and one observable measure or practice scenario it must improve; record a negative result rather than preserving a change that does not help. |

## Verification

- Read all TASK-227 acceptance criteria against the submitted plan.
- Cross-checked C1–C3 independently against the plan-challenge memo and the
  current decision-class/authority rules.
- Cross-checked the broader lifecycle concern against two independent,
  read-only practice artifacts: the lifecycle audit and the Discovery Agent
  pass. Both identify concrete lifecycle seams rather than recommending a
  replacement of MAP's durable-state architecture.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` —
  PASS before review.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` —
  PASS before review.

## Risks

The plan's principle is sound: prefer leverage-point changes over more process.
The requested corrections preserve that principle. They ensure that the first
two implementation tasks make conflicting state visible, that the index has a
measurable scope, and that an authority change does not bypass the human
decision path. The lifecycle artifacts also propose bounded experiments for
deeper seams (bootstrap/readiness and release-tier alignment); they remain
investigations until separately promoted.

## Notes

The reviewer helper's five findings informed this review but did not alter task
state. The two completed practice artifacts provide independent convergence:
MAP's durable spine is valuable, while several transition contracts and
retrieval paths need evidence-first simplification. The requested rework is a
small plan correction, not a new framework or a demand to preserve every
existing MAP layer.
