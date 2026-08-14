# MAP Practice-Scenario Queue — 2026-07-18

- status: proposed
- owner: codex-lab-kiri
- last_reworked: 2026-07-19 (TASK-239 independent review)
- runbook: [[practice-scenario-runbook]]
- source: KICK-01, TASK-233 release evidence, current runner route

## Selection rule

Choose the first scenario whose admission gate is satisfied and whose owner
can participate. Do not start a later item merely to keep an agent busy.

| Order | Scenario | Hypothesis | Minimum evidence | Operator decision points | Non-goals | Admission gate |
|---|---|---|---|---|---|---|
| 1 | `PRACTICE-02` Deployment-source truth | A frozen launcher/listener/source packet lets two core agents name the real editable CommandCenterUI source before a UI change, without restarting a service or guessing from template location. | Read-only manifest, fingerprints, configured launcher chain, listener provenance result, independent contradiction check. | Scope admission; later request only if source remains unverified or a deployment boundary must be selected. | No UI edit, installer run, service restart, or source selection by inference. | TASK-235 command-center policy gate is resolved and its owner confirms scope. |
| 2 | `PRACTICE-03` Interruption → safe resume | A compact handoff plus the current task/review record lets a returning agent choose the first valid action after interruption without relying on chat replay. | Controlled handoff, current SQLite/task state, review record, resumed-agent answer, independent review. | Scope admission; later request only for a real ownership, authority, scope, or privacy gate. Routine resume routing stays with the task owner. | No startup-policy replacement, automatic task mutation, or simulated authority decision. | A low-risk task with a willing owner and a different available reviewer. |
| 3 | `PRACTICE-04` Review-to-release visibility | The Command Center and durable artifacts make a review/release decision understandable to the operator without opening raw task mirrors. | One submitted low-risk task, review record, release checklist, operator explanation from visible state, independent correctness check. | Scope admission plus only the approval/deployment decision already required by the underlying task; the scenario adds no gate. | No auto-approval, notification policy change, or new status store. | A newly submitted low-risk task with its owner and reviewer available. |
| 4 | `PRACTICE-05` Advisory signal quality | A proposal-only monitor distinguishes a real stale/contradictory condition from clean state and yields a useful core decision without claiming or mutating. | TASK-236 rework evidence, clean/dirty fixtures, visible proposal, core disposition, independent review. | Scope admission; later request only for a standing-process design or authority to mutate/promote. | No standing deployment, model judgment in deterministic path, auto-promotion, or task mutation. | TASK-236 owner reworks and resubmits; command-center separately chooses any standing-process design. |

Each selected queue row must be expanded into the full runbook packet before
launch, including exact `evidence_paths` and `operator_decision_points`. This
queue is prioritization evidence, not scope authorization. If either field is
missing or a new unlisted decision arises, follow the runbook's STOPPED /
ordinary-routing rule instead of inferring a destination or escalating by
default.

## First planned pairing when Claude is available

- Coordinator: Codex owns packet, measurements, and integration.
- Independent Claude role: contradiction/freshness check for `PRACTICE-02`,
  then reviewer for the final evidence packet.
- Operator role: approve only the scenario’s stated scope and decide only
  surfaced gates; routine progress stays `inform`.
- Completion condition: a reviewed verdict and a single next action or a
  preserved negative result—not an unbounded improvement program.

## KICK-01 carry-forward constraints

1. Freeze source authority before discussion: SQLite claims, hcom live
   presence, durable status, and event history answer different questions.
2. Check terminal liveness and exact output paths before spawning a fallback.
3. Treat deployment-source parity as a prerequisite to UI conclusions.
4. Count cancelled/failed handoffs as friction, not as successful work.
5. Do not generalize a one-scenario win into startup policy or authority.
