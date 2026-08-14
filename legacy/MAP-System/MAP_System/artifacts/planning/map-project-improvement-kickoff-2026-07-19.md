<!-- hpom: file: artifacts/planning/map-project-improvement-kickoff-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: SCOPED -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-251 live runner, status, metrics, task graph, practice evidence, and Claude/Codex kickoff assessments -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# MAP Project Kickoff: From Building the System to Proving the System

- task: TASK-251
- date: 2026-07-19
- status: PROPOSED — operator ratification required
- synthesis owner: codex-lab-kiri
- independent framing: claude-lab-lure
- executive sponsor and final priority owner: bigboss

## 1. Why this kickoff exists

MAP has reached an important transition. It is no longer an early prototype
that needs every plausible coordination feature. It now has a real task
ledger, claims, routing, review, release, recovery, communication, local-helper
boundaries, observability, and a human-facing Command Center.

The next risk is not that MAP lacks machinery. The next risk is that MAP keeps
improving its machinery without proving that the machinery helps the operator
finish meaningful projects.

This kickoff therefore changes the governing question from:

> What else should MAP be able to do?

to:

> Can one operator use MAP to ship a meaningful real-project outcome with
> trustworthy state, recoverable work, acceptable coordination cost, and less
> manual supervision than the work would otherwise require?

This document is a proposed execution roadmap. It does not silently authorize
new agents, new autonomous authority, deployment, policy changes, or a new
database. Those decisions remain with the operator and the normal MAP gates.

---

## 2. Joint conclusion

Codex and Claude assessed the system independently before reconciling their
views. Both reached the same central conclusion:

> MAP's coordination architecture is credible, but its real-project outcome
> evidence is weaker than its process evidence.

Both also selected the same two supporting weaknesses:

1. durable agent availability does not reliably describe live capacity;
2. coordination and review overhead can exceed the risk or size of the work.

The priority order is therefore:

1. **G1 — prove MAP on one real external project outcome;**
2. **G2 — make routing and operator views honest about liveness;**
3. **G3 — reduce and measure coordination cost.**

G2 and G3 are subordinate to G1. They are not invitations for another open-
ended MAP improvement program. They earn work only when they unblock or
improve the prove-it project.

---

## 3. Evidence baseline at kickoff

These are point-in-time observations collected on 2026-07-19. Counts will
change; the structural conclusions should be retested at each phase gate.

| Signal | Observed state | Meaning |
|---|---:|---|
| Canonical task records | 241 tasks | MAP has substantial operating history, not merely a design proposal. |
| Released tasks | 134 | The release mechanism is actively used. |
| Approved tasks | 62 | APPROVED is intentionally terminal for some low-risk work, but the board does not distinguish those items from approved work still awaiting release closeout. |
| Submitted awaiting review | 10 | The present bottleneck is review/consolidation, not lack of implementation work. |
| Tasks with at least one `MAP_System/` output | 180 | The portfolio is heavily weighted toward MAP improving MAP. Counts overlap other lanes. |
| Tasks with at least one `Projects/` output | 32 | Real-project work exists, but is a minority of the recorded portfolio. |
| Durable agents marked `available` | 62 | This is registered capacity, not credible live capacity. |
| Live hcom sessions at sampling | 7 | Only four were live cloud-core sessions; two Pi sessions remain unqualified for critical work and one was a Librarian helper. |
| Task-graph validator | RED | Rapid UI refinements TASK-241–248 claim overlapping files and tests. |
| Metrics conflict count | 0 | The metrics surface does not reflect the graph's active output collisions. |
| Recorded `outcome_pass` / `outcome_fail` events | 0 | The event schema and metric exist, but MAP has no real outcome-feedback sample to learn from. |

### 3.1 Evidence that the system has real strengths

- Independent review is substantive. The current change-request rate is about
  20%, which means review is finding real mismatches rather than merely
  certifying authors.
- RnS performed a real recovery during this kickoff window: it detected
  Claude's provider-limit record, retained the scheduled 01:15 reset, delivered
  a live-session nudge at 01:17, and cleared durable status.
- The refined orientation experiment preserved six frozen recovery facts in
  2,619 bytes versus a 44,432-byte retained control, a 94.11% scenario-local
  reduction. It was correctly parked instead of generalized from one result.
- ClearFront work produced multiple released product tasks and deterministic
  tests, proving MAP can support more than self-documentation.
- The local Ollama lane is loopback-bound and advisory-only. Pi's failed
  requalification evidence has been preserved instead of being explained away.

### 3.2 Evidence that the operating model is under strain

- One continuous Command Center design conversation became eight separate
  submitted tasks touching the same files. The task abstraction did not match
  the work's iterative shape.
- Reviewer sessions disappeared or resumed with stale context, producing
  scarcity and near-duplicate review work while the durable registry continued
  to report broad availability.
- A safe read-only task was policy-gated because its guardrail named forbidden
  actions. TASK-249 fixed the immediate classifier defect, but the incident
  illustrates the cost of safety machinery when it cannot interpret task
  shape accurately.
- `shared/current-state.md`, `shared/memory-map.md`, and
  `shared/improvement-backlog.md` contain useful truth but their verification
  metadata trails the latest releases.
- MAP has a first-class outcome-event shape, but no outcome events are
  recorded. The capability therefore has not yet produced evidence about
  whether the operator's intended external outcome was achieved.

---

## 4. Root-cause model

The present problems reinforce one another:

```text
no chosen external proving outcome
            │
            ▼
MAP improvements become the easiest available work
            │
            ▼
more tasks, rules, dashboards, and micro-fixes
            │
            ▼
review backlog + overlapping ownership + stale projections
            │
            ▼
more coordination work is proposed to manage the coordination work
```

A second loop amplifies it:

```text
stale durable availability
        → incorrect capacity assumptions
        → stranded or duplicate assignments
        → handoffs and recovery overhead
        → more status machinery
```

Neither loop is solved by adding another general-purpose agent. The first is
solved by an external goal and portfolio discipline. The second is solved by
reconciling live evidence and durable state, then making disagreement visible.

---

## 5. Goals and success measures

### G1 — Ship one meaningful real-project outcome through MAP

#### Goal

Take one operator-selected milestone in an existing project from clarified
intent through implementation, interruption if it naturally occurs, review,
release, and operator acceptance.

#### Success measures

- The operator accepts the milestone as useful project progress, not merely a
  successful MAP exercise.
- The complete path from intent to release is reconstructable from current
  MAP records without reading private model transcripts.
- The milestone has domain evidence: tests for software, acceptance against a
  story/product brief for creative work, or another predeclared outcome check.
- Operator `request` messages are limited to actual product, authority, scope,
  privacy, deployment, or blocker decisions. Routine progress uses `inform`.
- Before implementation, the operator and milestone owner record a rough
  no-MAP counterfactual: expected effort, manual coordination, likely error or
  recovery risks, and confidence in those estimates. The retrospective
  compares actual MAP-assisted delivery with that estimate rather than merely
  proving that MAP completed its own process.
- A retrospective records elapsed cycle time, rework, interruptions, operator
  attention requests, coordination actions, and the final real-world result.

#### Recommended proving project

**ClearFront is the recommended first target.** It already has deterministic
tests, recent released work, a domain-specific product surface, and enough
complexity to exercise real coordination without first inventing a new
project structure.

Alternatives for the operator:

- **Pathwell:** better for testing research/creative collaboration, but its
  outcomes are less mechanically measurable.
- **Project Updater:** directly relevant to operator workflow, but risks
  turning the prove-it run into more meta-tooling.

### G2 — Make capacity and routing truth honest

#### Goal

No task should be routed, reviewed, or presented to the operator on the basis
of a stale `available` record alone.

#### Success measures

- Routing distinguishes registered identity, durable declared status, live
  hcom presence, freshness, and active task claim.
- A disappeared session is marked unavailable or explicitly unknown within
  two watcher cycles; it does not remain silently eligible for assignment.
- Reappearing sessions reconcile safely without erasing a meaningful
  `out_of_tokens`, terminal, or operator-set reason prematurely.
- `map_status`, the runner, metrics, and Command Center either agree or expose
  their disagreement with source labels.
- A staged fixture demonstrates live/durable agreement, stale durable
  availability, an active limit window, and a recovered session.

### G3 — Reduce coordination cost without weakening authority

#### Goal

Make MAP's process proportional to consequence. Small iterative work should
not require a new task, reviewer search, and release ceremony for every text or
color adjustment.

#### Success measures

- One continuous low-risk iteration on one owned surface uses one work package
  with appended acceptance evidence, not a chain of overlapping microtasks.
- The task graph is green at every phase exit.
- The review queue is at most two items before new discretionary MAP work is
  admitted.
- A simple machinery-to-work scorecard records coordination actions, operator
  requests, handoffs, and review cycles beside the real deliverable. The first
  run establishes a baseline; it is not turned into a target before it is
  understood.
- Any proposed autonomous coordination-write lane is narrow, reversible,
  mechanically bounded, and separately approved as an authority change. It is
  not smuggled in as a documentation or convenience fix.

---

## 6. Operating principles for the improvement program

1. **Real work first.** Every MAP improvement must name the prove-it failure it
   prevents or the measure it improves.
2. **Stabilize before extending.** Clear current review debt and graph
   collisions before adding discretionary capabilities.
3. **Batch by work surface and risk.** One iterative UI conversation is one
   work package until a stable review boundary is reached.
4. **Truth may remain plural, but disagreement must be visible.** Live hcom,
   durable status, task claims, and event history answer different questions.
5. **No metric becomes a goal on its first use.** Baseline it, inspect how it
   can be gamed, and only then decide whether to retain it.
6. **Experiments do not silently become policy.** Pass, partial, and negative
   results all remain evidence; adoption is a separate decision.
7. **The operator owns product meaning and authority.** Agents own execution
   inside ratified boundaries.

---

## 7. Phased roadmap

The phases are gated by evidence, not fixed calendar dates. Session estimates
are planning aids, not deadlines.

### Phase 0 — Ratify direction

**Estimated effort:** one operator decision session.

Decisions:

1. select the G1 proving project and one meaningful milestone;
2. ratify the proposed role split;
3. approve a temporary freeze on discretionary MAP features during
   stabilization;
4. decide whether an autonomous coordination-write experiment may be designed
   now or must wait until the G1 baseline demonstrates the need.

**Exit evidence:** an operator decision record and a bounded milestone brief.

### Phase 1 — Stabilize the current board

**Estimated effort:** no more than two core-agent sessions. This is a hard
bound: stabilization cannot expand into a new MAP-improvement phase.

Actions:

1. Review TASK-239 and transition the already-approved TASK-250 record.
2. Repair TASK-241–248's canonical output ownership **before** review. For
   each colliding path, the final task that changed the composite file retains
   active ownership; earlier serial tasks relinquish that shared path and keep
   only truthful task-specific test/evidence outputs. Update SQLite first,
   export mirrors, and preserve historical events unchanged. If no existing
   record can truthfully own the final composite, create one explicit
   consolidation record and supersede the duplicate implementation ownership
   rather than pretending the collision is only a validator problem.
3. Review the repaired TASK-241–248 chain as one low/medium-risk batch: verify
   that the final files preserve every task's criterion, record one batch
   evidence packet, transition each task without re-editing the shared files,
   and complete only the release closeout appropriate to its risk tier.
4. Triage all 62 APPROVED tasks into three explicit groups: release required,
   intentionally approval-terminal under the risk-tier guide, or superseded /
   parked. Do not run 62 ceremonial releases; record the disposition and close
   only genuine delivery debt.
5. Re-run task graph, mirror, focused UI, deployment-parity, and Librarian
   checks. The three current Librarian findings caused by literal example
   wikilinks in TASK-238 review/release artifacts are a bounded cleanup item,
   not justification for a Librarian redesign.
6. Reconcile stale durable agent records against live hcom and terminal facts;
   do not simply mark every absent historical identity `available` or delete
   provenance.
7. Refresh current-state and active-memory routes only where the latest
   released behavior made them stale.
8. **In parallel, not afterward,** bigboss and the program lead shape the
   one-page G1 milestone brief. No project source changes begin until its
   acceptance outcome and ownership boundary are ratified, but MAP cleanup may
   not postpone choosing the real work.

**Exit criteria:**

- task graph green;
- review queue no larger than two;
- no task is stranded solely because its presumed reviewer is not live;
- approved-state triage is recorded without assuming every APPROVED task needs
  a release ceremony;
- the live/template UI relationship is explicitly verified;
- current-state metadata reflects the stabilization evidence.

**Stop rule:** if closing the UI chain requires selecting a deployment source,
restarting a service, or overwriting a meaningful installed-copy difference,
stop and request the operator's deployment decision.

**Time-box rule:** if any exit criterion remains unmet after two sessions,
record the exact blocker, owner, and safe containment. Continue shaping G1 and
return the unresolved cleanup to the operator instead of expanding Phase 1.

### Phase 2 — Establish the prove-it baseline

**Estimated effort:** one planning/measurement session.

Actions:

1. Shape the selected project milestone into the smallest coherent task tree,
   with no more than three independent concurrent work packages.
2. Freeze a scorecard before implementation:
   - start and release timestamps;
   - product acceptance check;
   - number of task records and coordination events;
   - operator requests by decision class;
   - review cycles and required findings;
   - interruption/recovery time;
   - duplicate work, collisions, or abandoned work;
   - final operator outcome assessment.
3. Freeze the no-MAP counterfactual with the operator and milestone owner:
   expected effort, manual coordination, likely defects, interruption/recovery
   approach, and confidence for each estimate. This is an honest comparison,
   not a randomized scientific control; its purpose is to make “MAP helped”
   falsifiable rather than assumed.
4. Record the current liveness-routing behavior as the G2 control.
5. Define the low-risk batching rule for this run as a scoped experiment, not
   global policy.

**Exit criteria:** the milestone, ownership boundaries, scorecard, control,
and stop rules are frozen before implementation begins.

### Phase 3 — Execute the prove-it project

**Estimated effort:** three to seven focused work sessions, depending on the
operator-selected milestone.

Actions:

1. Run real project work through normal MAP intake, claim, implementation,
   evidence, independent review, and release.
2. Apply G2 liveness reconciliation only where the run demonstrates a routing
   or recovery failure; retain the control and compare behavior.
3. Use the scoped G3 batching rule for iterative low-risk changes on one
   surface. Split work only for real ownership, dependency, risk, or review
   boundaries.
4. Record interruptions naturally. Do not manufacture provider failures merely
   to make the scenario interesting.
5. Keep helpers advisory and visible. No helper owns the critical path.

**Exit criteria:** a shipped milestone with operator acceptance or a preserved
negative result explaining exactly why MAP failed to deliver it.

### Phase 4 — Decide what MAP actually learned

**Estimated effort:** one retrospective and one independent review.

Actions:

1. Compare the scorecard with both the frozen MAP baseline and the no-MAP
   counterfactual. State uncertainty openly; if MAP does not appear to improve
   delivery, supervision, quality, or recovery enough to justify its cost,
   record that negative result.
2. Classify each attempted improvement as adopt, revise, park, or reject.
3. Promote only repeated or high-consequence lessons into rules, validators,
   templates, or code.
4. Archive superseded planning narratives; refresh current state, memory
   routing, backlog, and the deep-dive guide only where facts changed.
5. Select the next real milestone only after the operator judges whether MAP's
   value exceeded its coordination cost.

**Exit criteria:** an outcome retrospective, reviewed adoption decisions, and
no unowned follow-up work.

---

## 8. Roles and accountability

Roles are proposed for operator ratification. A named person is still subject
to a fresh liveness check before assignment.

| Role | Proposed owner | Accountable for | Must not do |
|---|---|---|---|
| Executive sponsor / product owner | bigboss | Select G1 project and milestone; define useful outcome; decide authority, deployment, privacy, and scope gates; accept final result. | Arbitrate routine implementation details or serve as the system's manual scheduler. |
| Program and delivery lead | codex-lab-kiri | Maintain TASK-251 plan; stabilize board; shape prove-it task tree; collect scorecard; coordinate bounded execution; publish phase snapshots. | Review or approve Kiri-authored substantive outputs or retain undocumented single-person context. |
| Architecture, simplification, and continuity lead | claude-lab-lure | Challenge task shape; lead coordination-cost/ceremony audit; define scoped batching experiment; test whether proposed machinery is necessary; resume program coordination from the latest snapshot if Kiri stops. | Turn simplification proposals into authority changes without operator approval or silently take output ownership. |
| Liveness reliability lead | codex-lab-hana, subject to a fresh atomic claim; Lure is fallback if Hana is unavailable | Diagnose registry/live divergence; propose and implement a bounded reconciliation fix if G1 evidence justifies it. | Treat hcom presence as durable authority, erase operator-set reasons, or begin from stale session context. |
| Independent reviewer / release steward | codex-lab-hana or codex-lab-lilo, whichever is freshly live and did not author the item | Review phase evidence, task outputs, and release packets; prevent self-approval. | Accept assignments based only on stale registry availability or duplicate an open review claim. |
| Documentation integrity helper | helper-librarian-dora | Bounded path, link, and canonical-route checks after approved edits. | Decide authority, task status, project priority, or review verdict. |
| Local advisory model | qwen3.5:4b through the approved visible Ollama lane | Bounded drafts, classification, or comparison when a core owner defines inputs and output. | Own tasks, mutate core truth, review, release, or run hidden background work. |
| Pi sessions | none on critical path | Optional future requalification only under a separately authorized, visible, no-write experiment. | Tasks, reviews, releases, handoffs, issue tracking, or unattended output. |
| Command Center | operator surface, not a decision-maker | Present attention, source-labelled state, and required decisions. | Become a competing state store or infer authority from UI state. |

### 8.1 Review pairing

- Kiri-authored work → Lure, Hana, or Lilo reviews.
- Lure-authored work → Kiri, Hana, or Lilo reviews.
- Product implementation and plan acceptance use different reviewers when risk
  or scope warrants it.
- Atomic review claims are required before substantial review work so a stale
  session does not cause duplicate effort.

### 8.2 Program continuity

- The program lead writes a `STATE_SNAPSHOT` at every phase exit and before an
  anticipated limit or absence. It names current task state, decisions,
  evidence paths, and the first safe next action.
- Lure is the named coordination fallback and may resume from that snapshot
  after checking SQLite, current decisions, and live output ownership.
- An unplanned disappearance triggers liveness reconciliation and an explicit
  handoff/claim change; it does not authorize two simultaneous program leads.

---

## 9. Work packages after ratification

These are proposed packages, not yet authorized tasks.

| Package | Goal | Owner | Reviewer | Durable output | Admission gate |
|---|---|---|---|---|---|
| WP-0 Board stabilization | Clear review debt and collisions, time-boxed to two sessions | Kiri | fresh non-author core reviewer | ownership repair + batch evidence + green validator + approved-state triage | Operator accepts temporary feature freeze |
| WP-1 Prove-it milestone brief | Define useful external outcome in parallel with WP-0 | bigboss with Kiri shaping | Lure challenge | project milestone brief + task tree | Operator selects project |
| WP-2 Liveness truth control | Measure registry/live divergence | Hana, fresh claim required; Lure fallback | non-author core reviewer | frozen fixture + reconciliation proposal | G1 route needs reliable capacity |
| WP-3 Coordination-cost baseline | Define machinery-to-work scorecard and scoped batching | Lure | Kiri or Lilo | baseline packet + experiment protocol | G1 milestone shaped |
| WP-4 Product implementation | Deliver selected milestone | assigned by non-overlapping output paths | non-author reviewer | project source + domain evidence | WP-1/WP-3 complete |
| WP-5 Outcome retrospective | Decide adopt/revise/park/reject | Kiri integrates; bigboss judges outcome | independent core reviewer | retrospective + decision proposals | Product result released or stopped |

No package may create downstream tasks automatically. A core owner shapes each
task, and authority-class proposals return to the operator.

---

## 10. Risks and countermeasures

| Risk | Early warning | Countermeasure |
|---|---|---|
| Self-improvement spiral | New MAP tasks appear without a named G1 failure or measure | Freeze discretionary MAP work; require a link to the prove-it scorecard. |
| Measurement theater | Counts improve while operator value is unclear | Operator outcome acceptance is the primary result; metrics remain explanatory. |
| Stale capacity | Assigned reviewer is absent or resumes with old context | Fresh hcom/liveness check plus atomic review claim before assignment. |
| Over-batching | One task becomes broad, risky, or impossible to review | Split on output ownership, dependency, risk, or stable review boundary—not every iteration. |
| Under-batching | Successive microtasks collide on the same files | Append scoped refinements to the active work package and review the stable final state. |
| Authority creep | A convenience fix begins writing coordination state autonomously | Stop; classify as AUTHORITY; require explicit operator approval and rollback design. |
| UI/source ambiguity | Template and installed copy differ or listener source is unverified | Run the approved read-only provenance check; request deployment-source decision. |
| Reviewer scarcity | Review queue grows while registry claims broad availability | Cap new work, reconcile liveness, and use one freshly live non-author reviewer per item. |
| Helper scope drift | Helper accepts another sender or writes outside its note | Stop helper, preserve negative evidence, and keep it off critical path. |

---

## 11. Explicit non-goals

During this program, do not:

- add another general-purpose agent role;
- widen Pi's authority or rely on Pi for delivery;
- create a new outcome database before a simple artifact scorecard proves the
  questions and fields are useful;
- replace the existing task ledger, hcom, or Command Center wholesale;
- add permanent autonomous discovery or task-generation processes;
- turn one successful practice scenario into global policy;
- optimize agent count, task count, release count, or message count as ends in
  themselves;
- continue cosmetic Command Center work while its underlying state or
  deployment source is untrustworthy;
- rewrite historical evidence to make current state look cleaner.

---

## 12. Decisions needed from the operator

### Decision 1 — Prove-it project

- **Issue:** MAP needs one external outcome that governs the next phase.
- **Options:** ClearFront; Pathwell; Project Updater; another operator-named
  milestone.
- **Recommendation:** ClearFront, because it combines real product value with
  deterministic verification and existing delivery context.
- **Needed:** name the project and one outcome that would feel meaningfully
  complete.

### Decision 2 — Stabilization freeze

- **Issue:** the graph and review queue are carrying debt from rapid UI
  iteration.
- **Options:** temporarily pause discretionary MAP/UI features until Phase 1
  exits; or continue feature intake while cleaning the queue.
- **Recommendation:** pause discretionary features; continue only operator
  blockers, safety fixes, and already-scoped closeout.
- **Needed:** ratify or reject the temporary freeze.

### Decision 3 — Autonomous coordination-write experiment

- **Issue:** routine coordination transitions consume operator attention, but
  autonomous state mutation changes authority and can hide mistakes.
- **Options:** postpone until the G1 baseline shows actual cost; authorize only
  a design/experiment proposal now; authorize implementation now.
- **Recommendation:** postpone implementation. Permit a bounded proposal only
  after the baseline identifies the exact repeated transition and rollback.
- **Needed:** choose the allowed planning boundary.

### Decision 4 — Role ratification

- **Issue:** the plan proposes named accountability, but live availability
  remains volatile.
- **Options:** ratify the role model with fresh-liveness substitution; or name
  different leads.
- **Recommendation:** ratify the roles while allowing Hana/Lilo substitution
  only after a fresh liveness and conflict check.
- **Needed:** approve or amend the role table.

---

## 13. Collaboration and challenge record

This roadmap was not produced by averaging two conversational summaries.

1. Codex independently inspected the live runner, status board, metrics, task
   graph, hcom presence, current-state memory, prior implementation plan, and
   practice evidence.
2. Claude independently named its top weaknesses, goals, phases, and role
   split before reading Codex's synthesis. The independent diagnosis converged
   on outcome blindness, liveness fragility, and coordination-cost inversion.
3. Claude then performed a contradiction pass on the full draft. It found no
   blocker or hidden authority grant, but required two corrections:
   - add a no-MAP counterfactual so the prove-it run can evaluate whether MAP
     helped rather than merely whether MAP operated;
   - repair duplicate output-path ownership before claiming the UI task graph
     can become green.
4. The contradiction pass also recommended distributing program continuity,
   triaging APPROVED states instead of assuming release debt, and shaping G1 in
   parallel with time-boxed cleanup. All three recommendations were adopted.

This record preserves the disagreement that improved the plan. It is not an
independent approval of TASK-251; formal review remains a separate state
transition after submission.

## 14. Relationship to existing plans

This kickoff incorporates rather than discards the evidence in:

- `MAP_System/notes/system-improvement-kickoff.md`;
- `MAP_System/notes/system-improvement-implementation-plan.md` (TASK-227);
- `MAP_System/artifacts/reports/system-improvement-iteration-2026-07-18.md`;
- `MAP_System/notes/practice-scenario-runbook.md`;
- `MAP_System/artifacts/planning/map-practice-scenario-queue-2026-07-18.md`;
- `MAP_System/notes/map-system-deep-dive.md`.

TASK-227's north star—trustworthy intent-to-release operation without hidden
state—remains valid. TASK-251 adds a sharper portfolio constraint: that loop
must now be proved on an operator-valued external outcome.

This document does not supersede TASK-227 merely by existing. If the operator
ratifies it, the active memory map and older planning records should be updated
to state which plan governs execution and which remain historical evidence.

---

## 15. Kickoff close

MAP has enough architecture to begin proving itself. Its next advance should
not be measured by how many coordination capabilities it adds. It should be
measured by whether the operator can use it to finish a meaningful project
with trustworthy state, recoverable work, proportionate supervision, and a
clear explanation of what the system contributed.

The proposed sequence is deliberately simple:

```text
choose a real outcome
    → clean the current board
    → freeze baseline and roles
    → deliver the outcome
    → measure coordination honestly
    → keep only what evidence justifies
```

That is the path from a sophisticated multi-agent system to a useful one.
