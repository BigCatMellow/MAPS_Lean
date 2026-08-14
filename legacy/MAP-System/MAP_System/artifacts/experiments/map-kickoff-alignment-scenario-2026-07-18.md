# MAP Kickoff-Alignment Practice Scenario

- task_id: TASK-233
- scenario_status: KICK-01_complete; review-repaired v2 confirmation complete
- coordinator: codex-lab-lilo
- scenario_id: KICK-01
- started_at: 2026-07-18T06:25:52Z
- change_authority: none — practice/shaping only

## Retrieval capsule

- Purpose: Records the measured KICK-01 MAP kickoff-alignment practice exercise that shaped an implementation-ready Command Center coordination-card brief without changing product code or policy.
- Proves: Participant timing, shared-frame revisions, retrieval and handoff behavior, observed terminal and fallback race, independent review repair, and deployment-source uncertainty discovered during the run.
- Applies to: TASK-233's bounded 2026-07-18 practice scenario and its frozen participant, coordinator, review, and confirmation evidence.
- Does not provide: Product implementation, approval for the coordination card, a universal performance claim, resolution of deployment provenance, or permission to bypass the released practice-scenario runbook.
- Evidence type: measured_outcome
- Status: historical

## 0. Scenario purpose

Exercise the first MAP lifecycle stage as a real kickoff rather than a status
round. The scenario is deliberately bounded: shape, but do not implement, a
future operator coordination card for the Command Center. The test asks whether
agents can reach a shared, evidence-backed project brief with low retrieval and
handoff cost before a task owner writes code.

## 1. Shared project frame — v1 (frozen before participant input)

### Purpose

Let an operator see, for each live core agent or visible helper, the separately
labelled durable status, active claim, latest durable action, and actionable
exception needed to understand coordination without manually joining raw hcom,
the task database, and repository files.

### Success condition

The kickoff produces one later-task-ready brief with exact sources, explicit
conflict behavior, a small test matrix, defined non-goals, named authority
boundaries, and a measurement plan. It is successful only if the brief does
not introduce a new state store, infer a single synthetic agent status, or
require a policy/authority decision.

### In scope

- A read-only Command Center coordination card for live core agents and
  currently running helpers.
- Existing sources only: map.db, agents/status.json, hcom presence, and MAP
  events.
- Source labels, freshness/unknown treatment, and three staged mixed-state
  fixtures.
- A later implementation task's acceptance evidence.

### Non-goals

- No Command Center code or styling changes in this practice scenario.
- No new durable state store, status writer, helper authority rule, background
  automation, or Pi dependency.
- No adoption of an incident-role framework or any candidate experiment as
  policy.

## 2. Known facts and evidence packet

1. `artifacts/experiments/coordination-surface-readiness-audit-2026-07-18.md`
   establishes map.db as the claim authority, hcom as live-presence authority,
   status.json as a separate durable field with only file-level freshness, and
   events as historical action evidence.
2. `artifacts/reviews/task227-review-lilo.md` requires source authority,
   freshness, conflict behavior, and staged mixed-state tests before a status
   surface task is admitted.
3. `tasks/TASK-227.json` remains CHANGES_REQUESTED and owned by
   claude-lab-gome. This scenario is evidence only and does not edit that plan
   or transfer its ownership.
4. The current Command Center already exposes presence and an attention inbox,
   but not the unified per-agent coordination read model described above.

## 2a. Review-repaired v2 assumptions and risks (frozen before v2 confirmation)

The v1 packet omitted an explicit assumptions/risks section. Independent review
identified that as a valid acceptance-evidence failure. This v2 baseline is an
honest iteration, not a claim that v1 contained these fields. It is frozen
before the short v2 participant-confirmation pass described in section 6a.

### Assumptions

- The card can read existing local sources without writing or synchronizing
  them; a source read failure must be shown rather than repaired by inference.
- A process-bound hcom presence response is current live-presence evidence;
  fallbacks are useful but must carry a weaker source label.
- Existing identities may be joinable across sources for some agents, but an
  unmatched identity remains visible/unknown rather than being guessed.
- The installer template is inspectable in this workspace, but it may not be
  the source that updates the operator's live Command Center.

### Risks

- Deployable-source parity may be absent, so a correct template edit could
  fail to change the operator surface.
- Event history may be missing, malformed, or stale and must never prove live
  work or task completion.
- hcom, durable board, and claim identifiers may not share one join key.
- TASK-227's CHANGES_REQUESTED plan and its owner may constrain later task
  admission even when the UI brief is otherwise sound.

## 3. Authority and decision boundaries

| Area | Bound in this scenario |
|---|---|
| Project scope | Coordinator may shape a later task; no implementation action is authorized. |
| Claims | map.db remains the only claim authority. |
| Agent availability | Durable board and live hcom remain separately rendered facts; neither participant may synthesize a replacement status. |
| Policy / authority | Out of scope. Any finding that changes what an agent may do is recorded as an escalation candidate, not adopted. |
| Participant output | Proposal/evidence only; coordinator integrates only supported observations. |

## 4. Roles and questions

| Role | Participant | Bounded contribution |
|---|---|---|
| Coordinator | codex-lab-lilo | Freeze inputs, integrate evidence, count cost/friction, and decide whether the brief is ready. |
| Architecture / delivery | codex-lab-hana | Propose the smallest later-task boundary, interface seams, and test evidence; flag scope or implementation risk. |
| Discovery / contradiction | helper-discovery-clearfront-zero | Challenge assumptions, identify omissions/contradictions, and distinguish essential gaps from optional polish. |

Questions each participant must answer independently:

1. What must the later card answer for the operator, and what must it not
   imply?
2. What is the smallest reversible implementation boundary and test matrix?
3. What would make this kickoff misleading, slow, or over-scoped?

## 5. Measurement plan

Record these direct counts before evaluating effectiveness:

- kickoff retrieval set: 4 prerequisite artifacts listed in section 2;
- participant roles: 2 independent, visible non-owner roles;
- participant turns: hcom assignment plus final durable report per role;
- convergence: count shared conclusions and unresolved conflicts;
- rework: count participant findings that require changing the frozen frame;
- decision latency: task-created time through coordinator's later-task-ready
  brief time, reported as an observed interval rather than a target metric;
- context cost: paths required by each role beyond this packet.

No score is assumed in advance. A finding that the packet is too broad,
ambiguous, or expensive is a successful result of the practice.

## 6. Participant contributions — v1

### Discovery / contradiction — Zero

Report:
`MAP_System/artifacts/experiments/kickoff-discovery-contribution-zero-2026-07-18.md`

Zero used no context beyond this kickoff packet. It found two essential frame
refinements: the field must be called **latest recorded MAP action** and be
explicitly historical, and hcom presence must reveal whether it is
process-bound live, degraded fallback, or unavailable/unknown. It also named
two likely clarifications (the live-helper inclusion predicate and a factual
exception versus an operator-decision boundary) and rejected visual controls
as premature scope.

### Architecture / delivery — Moku

Report:
`MAP_System/artifacts/experiments/kickoff-architecture-contribution-moku-2026-07-18.md`

Moku independently converged on one read-only, four-source projection:
process-bound hcom presence, durable status.json, read-only SQLite claim state,
and event-log action history. It supplied a minimal test matrix and identified
two essential readiness conditions: identify the real deployable CommandCenter
source before editing an installer template, and leave TASK-227's
CHANGES_REQUESTED plan under its current owner.

### Observed handoff exceptions

1. Hana's visible terminal closed at the hcom delivery boundary before work
   began. Its assignment was marked superseded; no contribution was counted.
2. Moku produced the needed report at the same delivery boundary that a
   time-boxed Rori fallback was launched. Rori was immediately stopped and
   produced no report. This preserved correctness but added one avoidable
   assignment/cancellation round.

Both exceptions are retained as evidence of kickoff coordination cost; neither
is hidden as a successful participant turn.

## 6a. Participant confirmation — v2

The review-repair confirmation was dispatched at `2026-07-18T06:37:40Z` via
hcom events `4611` (Moku) and `4613` (Zero), after section 2a had been frozen.
Both participants were restricted to their v1 report and sections 2a/10: no
new source inspection, proposal generation, implementation, policy, task, or
shared-state change was allowed.

| Participant | Durable confirmation | Result | Effect on the brief |
|---|---|---|---|
| Zero (discovery) | `kickoff-v2-confirmation-zero-2026-07-18.md` | Confirmed source-failure and degraded-presence boundaries; refined join-key handling as explicitly test-gated. | No v1 decision changes. D-03 remains a fixture/admission test, not a matching rule. |
| Moku (architecture) | `kickoff-v2-confirmation-moku-2026-07-18.md` | Confirmed all added assumptions/risks. | No v1 decision changes; deployable-source parity and TASK-227 rework remain admission constraints. |

The corresponding reports arrived at `06:38:09Z` (Moku, event `4625`) and
`06:38:44Z` (Zero, event `4631`). This repair has two successful assignment +
report turns and no research-path expansion. Both confirm that the later task
brief remains deferred for the same evidence-backed reasons. The coordinator
integrates that result here; it does not backdate the missing v1 fields.

## 7. Integrated kickoff decisions

These are scoped design choices for a future task brief, not policy or
authority decisions.

| Topic | Integrated result | Basis |
|---|---|---|
| Operator question | Show separately labelled live presence, durable status, active claim, latest recorded MAP action, and factual attention reasons. | Both participants converge; readiness audit supplies authorities. |
| Claim truth | Only map.db decides active claim/expired lease. | Frozen evidence and Moku report. |
| Action semantics | Rename the proposed field to `latest recorded MAP action`; retain event timestamp/source and state that it is historical, not liveness/completion. | Zero D-01; Moku's event-history boundary. |
| Presence degradation | Surface `process-bound live`, `degraded fallback`, or `unavailable/unknown`; do not label a fallback as equally live. | Zero D-02. |
| Attention | Render a source-labelled set of factual reasons. Only existing request/approval sources may say the operator must decide. | Zero D-04 and frozen authority boundary. |
| UI scope | One passive card plus read-only endpoint; no writer, action control, new state store, background worker, Pi use, or incident-role system. | Frozen non-goals and Moku boundary. |
| Readiness | Defer the UI implementation task until deployable-source parity and TASK-227 plan rework are explicitly resolved. | Moku deployment evidence; existing owner/review state. |

### Remaining disagreement and disposition

Zero treats degraded hcom labelling as essential; Moku treats a broad bad/missing
source test as likely. The integrated brief resolves this without expanding the
main fixture set: the source label is **essential**, while an unavailable or
fallback subcase may live inside the existing bad/missing-source fixture. No
other material conflict remained.

## 8. Measured kickoff efficiency and effectiveness

| Signal | Observation | Interpretation |
|---|---|---|
| Frozen retrieval set | 4 prerequisite durable records before participant input. | Small enough for Zero to contribute with zero extra paths; it prevented generic re-explanation. |
| Successful independent roles | 2: discovery and architecture. | Both supplied durable artifacts and converged on source separation/no-new-state constraints. |
| Participant assignment attempts | 4: Hana, Moku, Zero, then Rori fallback. | Two succeeded; one terminal closed; one fallback was cancelled before output. This is visible coordination waste, not silent success. |
| Essential frame rework | 2 refinements from Zero plus deployment parity/readiness stop from Moku. | The kickoff prevented misleading field semantics and a template-only UI task before code began. |
| Likely clarifications | 2 from Zero, plus meaningful-event/join-key detail from Moku. | These belong in a later brief/test matrix, not a policy change. |
| Scope discipline | 1 rejected visual expansion; no policy, authority, UI, state, or helper changes. | The packet kept discovery from turning into feature accumulation. |
| Participant turns | Planned successful-role turns: 4 (assignment + final report for each of two roles). Observed successful turns: Zero assignment `4325` + report `4375`; Moku replacement assignment `4347` + report `4410`. | The four planned successful turns occurred. Hana's closed delivery and Rori's cancelled fallback are separately counted as exception overhead, not successful work. |
| Time/order evidence | Task created `06:25:52Z`; first dispatch `06:26:57Z` (events `4325`/`4330`); Zero report `06:28:30Z` (`4375`); Moku report `06:30:39Z` (`4410`); task submission state `06:32:52Z`; review dispatch `06:33:20Z` (`4477`). | First report arrived 2m38s after task creation. Start-to-submission was 7m00s; start-to-review-dispatch was 7m28s. All timestamps are UTC. |
| Context cost | Zero: 0 paths beyond packet. Moku: 9 cited direct paths beyond packet. | The packet supported a fast contradiction pass; architecture still needed source inspection. Future packets should name the deployable source boundary before dispatch. |
| Review-repair confirmation | 2 additional successful turns: assignments at `06:37:40Z` (events `4611`/`4613`) and reports at `06:38:09Z`/`06:38:44Z` (events `4625`/`4631`); 0 new research paths. | The narrowly scoped repair took 1m04s from dispatch to second report. It confirmed the corrective baseline without reopening the frame or generating scope. |

## 9. Effectiveness verdict and next iteration

**Verdict: PASS WITH TARGETED TUNING.** The kickoff created a shared,
evidence-backed later-task brief and surfaced three high-value constraints
before implementation: historical action semantics, degraded-presence truth,
and deployable-source parity. It did not manufacture a policy decision or
pretend that unavailable/late agents had contributed.

### Smallest next task candidate

Before a coordination-card implementation task, run a read-only
**CommandCenter deployment-source parity audit**. It should identify the live
editable checkout (or explicitly establish the installer template as the
deployment source), document the update/verification path, and name the exact
allowed UI output paths. It must not edit the UI or change deployment state.

### Process hypothesis for the next practice stage

At each helper timebox boundary, check the required durable output path and
the agent's terminal/liveness before launching a fallback. This is an
operational experiment, not yet a new rule: one kickoff observed a closed
terminal and a report/fallback race, but it has not established a repeated
pattern worth automating.

## 10. Final brief and outcome

The future coordination-card task is **not yet admitted**. Once the parity
audit and TASK-227 rework are complete, it should be medium risk and retain:

1. A source-labelled, read-only four-source projection (hcom, status board,
   SQLite claims, events).
2. `latest recorded MAP action` as historical evidence, never live activity.
3. Explicit process-bound/degraded/unavailable presence state and no synthetic
   agent status.
4. Fixtures for normal state, stale durable disagreement, newer action without
   status overwrite, expired claim, and source failure.
5. An explicit join-key test for live core agent, visible helper, and excluded
   non-session identity.
6. A real deployment verification plus independent review before release.

This finishes KICK-01, including the bounded v2 confirmation that corrected
the v1 acceptance-evidence omission. The next scenario stage after independent
re-review should exercise the parity audit, task
shaping, implementation, review, release, interruption, and recovery in
sequence, measuring whether the same durable packet prevents repeated
retrieval and coordination failures.
