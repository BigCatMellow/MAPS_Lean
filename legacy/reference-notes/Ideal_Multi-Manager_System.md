# Ideal Multi-Manager, Multi-Agent Management System

I would not build this as a traditional company hierarchy where managers constantly supervise permanent groups of agents. I would build it as a **federated operating system**:

* Multiple managers jointly establish direction.
* Every task has exactly one operational owner.
* Agents receive bounded missions rather than continuous instructions.
* Review, triage, research, and knowledge management operate independently from production.
* All important activity produces durable records outside the agents’ conversations.

I am assuming the managers and agents are primarily AI roles, with a human retaining authority over consequential or irreversible decisions.

---

## 1. The real-world systems worth combining

No single real-world organization provides the complete answer. The strongest model combines selected elements from several systems.

| Real-world system                            | Principle to borrow                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| FEMA Incident Command System                 | Multiple leaders can establish common objectives, but each worker reports to one supervisor             |
| Military mission command                     | Managers define intent, boundaries, and desired outcomes without dictating every step                   |
| NASA Independent Verification and Validation | Critical work is checked by people or systems independent of those who produced it                      |
| Google Site Reliability Engineering          | Incidents have explicit owners, measurable reliability targets, postmortems, and corrective actions     |
| Toyota Production System                     | Any worker or automated process can stop work when an abnormality is detected                           |
| DARPA program management                     | High-risk research is organized around hypotheses, milestones, experiments, and clear program ownership |
| NASA Lessons Learned                         | Knowledge is collected, reviewed, distributed, and deliberately incorporated into future practice       |
| NIST AI Risk Management Framework            | Governance, risk identification, measurement, and response must operate throughout the system           |

FEMA distinguishes **Unified Command**, where multiple authorities agree on shared objectives, from **unity of command**, where each person still reports to only one supervisor. That distinction solves the basic problem created by having two or more managers. ([FEMA Emergency Management Institute][1])

---

# 2. Recommended organizational structure

```text
Human Owner
│
├── Governing Command
│   ├── Manager A
│   ├── Manager B
│   ├── Additional Managers
│   └── Project DRI / Chief Orchestrator
│
├── Delivery Cell A
│   ├── Manager A
│   └── Specialist Agents
│
├── Delivery Cell B
│   ├── Manager B
│   └── Specialist Agents
│
├── Independent Assurance Office
│   ├── Review Agents
│   ├── Test Agents
│   └── Risk and Compliance Agent
│
├── Operations and Triage Office
│   ├── Triage Agent
│   ├── Incident Commander
│   └── Diagnostic and Recovery Agents
│
├── Research and Emergence Office
│   ├── Research Program Manager
│   ├── Research Agents
│   └── Experimental Agents
│
└── Knowledge and State Office
    ├── State Steward
    ├── Indexing Agent
    ├── Lessons-Learned Agent
    └── Emergence/Integration Agent
```

These should be understood as **roles**, not necessarily as permanently running models. One model may fill several roles at different times, provided conflicting roles are never combined on the same task.

For example, an agent may act as a researcher on one task and a reviewer on another. It must never review work it produced or directed.

---

# 3. The command structure

## Governing Command

The managers jointly own:

* The project charter.
* Strategic objectives.
* Priority order.
* Resource allocation.
* Risk tolerance.
* Global constraints.
* Criteria for success.
* Authority boundaries.

They do **not** jointly manage individual agents.

The Governing Command produces a single authoritative operating plan. This is the equivalent of FEMA’s Unified Command: the managers may represent different specialties, but they establish one set of objectives rather than issuing competing instructions. ([FEMA Emergency Management Institute][1])

## Project DRI

“DRI” means **directly responsible individual**. In this system, it may be a human or AI role.

The Project DRI:

* Resolves cross-manager conflicts.
* Maintains the integrated project plan.
* Decides which manager owns each workstream.
* Allocates shared resources.
* Prevents duplicated work.
* Integrates accepted results.
* Escalates consequential decisions to the human owner.

The Project DRI should not personally perform most production work. Otherwise it becomes both a bottleneck and an unchecked authority.

## Domain managers

Each manager owns a clearly bounded area, such as:

* Architecture.
* Implementation.
* Research.
* User experience.
* Testing.
* Operations.
* Documentation.

A manager may advise another domain but cannot silently take ownership of it.

## Active span of control

Each manager should normally supervise approximately **three to seven active agents or active work packages**, with five as a reasonable default.

FEMA uses three to seven as a manageable human span of control. This is not scientific proof that five is optimal for AI managers, but it is a useful starting constraint because coordination overhead still increases as active assignments accumulate. ([FEMA Emergency Management Institute][2])

The limit should apply to **simultaneously active work**, not the total number of agents registered in the system.

---

# 4. One task, one operational owner

This is the most important rule in the system:

> A task may have multiple contributors, advisers, reviewers, or stakeholders, but it has exactly one Task DRI.

Every task record should include:

```yaml
task_id: TASK-0241
objective: Implement project-search indexing
task_dri: agent-index-01
managing_unit: knowledge-office
decision_owner: manager-knowledge
review_owner: reviewer-02
risk_level: R1
dependencies:
  - TASK-0233
inputs:
  - ARTIFACT-182
  - DECISION-041
constraints:
  - Do not alter canonical project files
  - Preserve existing task identifiers
expected_outputs:
  - Search index implementation
  - Tests
  - Update documentation
acceptance_tests:
  - All existing tests pass
  - Search retrieves known test records
permissions:
  - Read repository
  - Modify assigned worktree
  - Run tests
stopping_condition:
  - Acceptance evidence submitted
```

An agent should never receive a vague instruction such as:

> Work with the other agents to improve indexing.

That creates uncertain ownership, duplicated work, and conversational drift.

Instead, the manager gives the agent a **mission order**:

* Why the work matters.
* What outcome is required.
* What boundaries apply.
* What evidence will demonstrate success.
* What conditions require escalation.

This resembles military mission command: subordinates receive the situation, intent, desired results, and required tasks while retaining freedom over how to accomplish them. ([Army University Press][3])

---

# 5. Independent checks and assurance

The checking system should have several layers.

## Layer 1: Local verification

The producing agent checks its own work using:

* Tests.
* Schemas.
* Linters.
* Static analysis.
* Required-field checks.
* Comparison against acceptance criteria.
* Source and citation validation.
* Permission-boundary checks.

This is necessary but not sufficient.

## Layer 2: Independent review

Another agent evaluates:

* Whether the output satisfies the task.
* Whether the evidence is sufficient.
* Whether assumptions were unsupported.
* Whether requirements were missed.
* Whether the work creates new risks.
* Whether the result conflicts with other accepted decisions.

NASA uses Independent Verification and Validation to find defects earlier, improve reliability, and reduce operational risk in safety- and mission-critical software. The relevant organizational principle is that critical assurance must retain functional independence from production. ([NASA][4])

## Layer 3: System validation

Verification asks:

> Did we produce the requested output correctly?

Validation asks:

> Was this actually the right output to produce?

A technically correct implementation can still be the wrong solution. Validation should compare the work against:

* The project charter.
* User intent.
* Current system state.
* Operational consequences.
* Other workstreams.
* Longer-term maintainability.

## Layer 4: Human approval

The human owner should approve actions that are:

* Irreversible.
* Financially consequential.
* Externally published.
* Legally or ethically sensitive.
* Security-sensitive.
* Capable of deleting or overwriting important information.
* Outside the established charter.
* Based on unresolved disagreement.

---

## Risk-based review levels

| Level             | Example                                                 | Required checks                                    |
| ----------------- | ------------------------------------------------------- | -------------------------------------------------- |
| **R0 — Low**      | Search, summary, internal formatting                    | Local verification                                 |
| **R1 — Normal**   | Reversible code or document changes                     | Local checks plus independent review               |
| **R2 — High**     | Architecture, migrations, security, system-wide changes | Independent assurance plus manager approval        |
| **R3 — Critical** | Irreversible, external, legal, financial, destructive   | Independent assurance plus explicit human approval |

This prevents both extremes:

* Reviewing every trivial action until the system becomes unusable.
* Allowing consequential work to pass through unchecked.

NIST similarly treats governance as a cross-cutting function and divides AI risk management into governing, mapping, measuring, and managing risk throughout the lifecycle. ([NIST AI Resource Center][5])

---

# 6. Operations and live triage

Triage should not be a normal manager responsibility. Managers are concerned with completing work; triage is concerned with understanding why the operating system is failing.

## Required task states

```text
BACKLOG
READY
CLAIMED
ACTIVE
WAITING
BLOCKED
REVIEW
REJECTED
FAILED
CANCELLED
DONE
```

A task may legitimately wait. It may not wait ambiguously.

Every waiting or blocked task should record:

```yaml
state: WAITING
waiting_for: TASK-0212
reason: API schema must be finalized
since: 2026-07-21T09:42:00-04:00
owner: agent-api-02
next_check: 2026-07-21T10:42:00-04:00
escalate_after: 4h
fallback_action: Continue documentation work
```

## What creates an incident

An incident should be opened when:

* An agent repeatedly fails the same task.
* A task remains blocked beyond its escalation limit.
* Two agents modify conflicting state.
* Accepted work breaks existing functionality.
* An agent acts outside its permissions.
* Canonical state and actual system state diverge.
* A dependency cycle prevents progress.
* Resource use becomes abnormal.
* Review failures reveal a systemic pattern.
* The same mistake recurs after a previous correction.

## Incident command

For each incident, appoint exactly one temporary **Incident Commander**.

Other roles may include:

* Operations lead.
* Investigator.
* Recovery agent.
* Communications/scribe agent.
* Subject-matter adviser.

During the incident, the Incident Commander controls the response, even when the affected work normally belongs to another manager. This authority ends when the incident is closed.

## Stop-the-line authority

Any agent should be able to flag:

```text
STOP_REQUESTED
```

This should pause affected downstream work until triage determines whether continuation is safe.

Toyota’s *jidoka* system allows machines or operators to stop production when an abnormality, quality problem, or delay is detected, preventing defective work from flowing into later stages. That is the correct model for agent systems: detecting a failure is not enough; the system must prevent the failure from propagating. ([トヨタ自動車株式会社 公式企業サイト][6])

## Post-incident learning

Every significant incident should produce:

* Summary.
* Impact.
* Timeline.
* Trigger.
* Contributing conditions.
* Detection method.
* Recovery actions.
* Where the system behaved correctly.
* Where controls failed.
* Corrective actions.
* One owner per corrective action.
* Verification that the correction was completed.

Google’s SRE guidance emphasizes factual, non-blaming postmortems, measurable impact, specific action items, and clear ownership. ([Google SRE][7])

---

# 7. Reliability budgets

The system should have an explicit policy for balancing new development against repair.

Example:

```yaml
reliability_target:
  accepted_without_rework: 90%
  maximum_repeat_incidents_per_month: 2
  maximum_critical_failures: 0
  maximum_median_blocked_time: 4h
```

When performance remains within the defined limits, managers may prioritize features and experiments.

When the reliability budget is exhausted:

* Reduce or pause new feature work.
* Divert agents to repair and testing.
* Address recurring causes.
* Improve checks and documentation.
* Resume normal work only after recovery criteria are met.

Google SRE uses error budgets as a control mechanism for balancing innovation and reliability, including policies that temporarily redirect work toward reliability after excessive failures. ([Google SRE][8])

For MAP, this should be broader than system uptime. It could include:

* Failed tasks.
* Rejected reviews.
* Repeated work.
* Unresolved incidents.
* Incorrect state updates.
* Excessive token or compute use.
* Unexplained blocked time.

---

# 8. Research and Development department

The R&D department should be structurally separate from production.

Its job is not to generate unlimited ideas. Its job is to convert uncertainty into evidence.

## R&D inputs

Research proposals can originate from:

* Unresolved task questions.
* Repeated failures.
* User feedback.
* Emerging technical capabilities.
* Contradictions between projects.
* Patterns found across completed tasks.
* New external research.
* Inefficient workflows.
* Opportunities found by the Emergence/Integration agent.

## R&D process

```text
Observation
    ↓
Research question
    ↓
Hypothesis
    ↓
Experiment design
    ↓
Sandbox experiment
    ↓
Evidence
    ↓
Independent evaluation
    ↓
Reject / Continue / Pilot
    ↓
Production transition
```

Each research program should have:

```yaml
experiment_id: EXP-0038
program_manager: manager-rd-01
question: Can task capsules replace full-history retrieval?
hypothesis: Capsules reduce retrieval cost without materially reducing accuracy
baseline: Full raw-history retrieval
success_metrics:
  - Retrieval accuracy
  - Context size
  - Processing time
  - Missed dependency rate
timebox: 14 days
resource_budget:
  agent_runs: 100
  compute_hours: 20
kill_conditions:
  - Accuracy drops more than 5%
  - No measurable context reduction
transition_owner: manager-knowledge
```

DARPA’s program managers define challenges and milestones, oversee high-risk research, and work with research performers to refine approaches. The applicable principle is that research needs a named owner, a defined challenge, milestones, and a path toward transition—not simply an open-ended “creative agent.” ([darpa.mil][9])

## Separation from production

Research agents must not directly change production systems.

They may produce:

* Findings.
* Prototypes.
* Experimental branches.
* Benchmarks.
* Recommendations.
* Proposed decision records.

Production adoption requires:

1. Evidence.
2. Independent review.
3. A transition owner.
4. A migration and rollback plan.
5. Defined success criteria.

This prevents the R&D department from becoming an uncontrolled source of architectural drift.

---

# 9. Emergence and cross-task idea discovery

Your E/I system should not repeatedly read every historical task in full. That will become increasingly expensive and noisy.

Use a layered memory architecture.

## Layer 1: Full archive

Preserve:

* Original task.
* Inputs.
* Conversations when necessary.
* Outputs.
* Tests.
* Reviews.
* Artifacts.
* Events.

This is the evidentiary record, not the everyday working memory.

## Layer 2: Task outcome capsule

Every completed task generates a compact capsule:

```yaml
task_id: TASK-0241
objective: Add project search
outcome: Implemented full-text search across task capsules
status: accepted
key_decisions:
  - SQLite FTS index is derived, not authoritative
problems_encountered:
  - Older capsules lacked normalized tags
reusable_patterns:
  - Filter by project and workstream before semantic search
unresolved_questions:
  - Whether artifact bodies should be indexed
related_concepts:
  - retrieval
  - memory
  - indexing
  - provenance
source_artifacts:
  - ARTIFACT-182
  - REVIEW-081
```

## Layer 3: Workstream digest

Periodically consolidate multiple capsules into a digest containing:

* Current state.
* Important decisions.
* Repeated patterns.
* Open questions.
* Known failures.
* Existing capabilities.
* Superseded approaches.

## Layer 4: Insight ledger

The E/I agent records possible connections:

```yaml
insight_id: INSIGHT-0092
observation:
  - Task capsule retrieval reduced context use
  - Review failures often follow missing constraints
connection:
  - Task packets could retrieve constraint capsules automatically
confidence: medium
evidence:
  - TASK-0241
  - INCIDENT-0018
proposed_test:
  - Compare review failure rates with automatic constraint retrieval
status: proposed
```

## Layer 5: Promoted knowledge

Only reviewed insights become:

* Policies.
* Design principles.
* Standard operating procedures.
* Reusable patterns.
* Requirements.
* New R&D programs.

The process should therefore be:

```text
Observe → Connect → Synthesize → Name → Test → Promote
```

Ideas may be captured freely. They should not change the project until they are tested and promoted.

---

# 10. Knowledge and indexing architecture

The indexing department should maintain four distinct layers.

## A. Canonical project truth

Human-readable files:

```text
CHARTER.md
STATE.json
REQUIREMENTS.json
RISKS.md
DECISIONS/
DISCOVERIES/
HANDOFFS/
EVALUATIONS/
ARTIFACTS/
TASK_MEMORY/
TRIAGE/
```

These explain what the project means.

## B. Coordination state

SQLite should hold:

* Task claims.
* Leases.
* Status.
* Dependencies.
* Agent availability.
* Permissions.
* Review assignments.
* Incident state.
* Resource use.

This explains what is happening now.

## C. Append-only event log

Examples:

```json
{"event":"task_created","task_id":"TASK-0241","at":"..."}
{"event":"task_claimed","task_id":"TASK-0241","agent":"agent-index-01","at":"..."}
{"event":"task_blocked","task_id":"TASK-0241","reason":"...","at":"..."}
{"event":"review_rejected","task_id":"TASK-0241","review":"REVIEW-081","at":"..."}
```

Events should normally be appended, not rewritten. Current state can be reconstructed from the history when necessary.

## D. Retrieval indexes

Derived indexes may include:

* Exact metadata indexes.
* Full-text search.
* Embedding-based semantic search.
* Knowledge connections.
* Artifact references.
* Dependency graphs.

The retrieval index must not become the source of truth. It is a replaceable map pointing back to authoritative records.

## Retrieval order

Agents should retrieve information in this order:

1. Project and workstream filter.
2. Current state.
3. Relevant decisions and requirements.
4. Exact text or metadata matches.
5. Task capsules.
6. Semantic matches.
7. Raw archived records only when necessary.

This is more efficient and safer than placing a large undifferentiated semantic search over the complete archive.

NASA’s lessons-learned process follows a comparable lifecycle: collect knowledge, record it, disseminate it, and then deliberately apply it through updated processes, policies, handbooks, and checklists. Merely storing lessons is not enough. ([NASA][10])

---

# 11. Manager disagreement protocol

Multiple managers require an explicit disagreement process.

## Decision order

1. **Domain decision:** The designated domain manager decides within their authority.
2. **Cross-domain consultation:** Affected managers submit evidence and concerns.
3. **Project decision:** The Project DRI resolves the disagreement.
4. **Human escalation:** The human decides when the issue is irreversible, outside the charter, or above the Project DRI’s authority.
5. **Decision record:** The result and dissent are permanently recorded.

A decision record should contain:

```yaml
decision_id: DECISION-0048
question: Should project search use a separate vector database?
decision_owner: project-dri
participants:
  - manager-architecture
  - manager-knowledge
options:
  - Separate vector database
  - SQLite plus derived embedding index
decision: SQLite plus derived embedding index
reason:
  - Fewer authoritative systems
  - Easier backup and reconstruction
dissent:
  manager-architecture:
    - May become limiting at larger scale
revisit_when:
  - More than 1,000,000 indexed records
  - Search latency exceeds target
```

Recording dissent is important. It preserves potentially useful reasoning without preventing a decision.

---

# 12. Communication model

Agents should not operate through unrestricted group conversation.

Use structured communication packets.

## Assignment packet

```text
TASK
CONTEXT REFERENCES
OBJECTIVE
WHY IT MATTERS
SCOPE IN
SCOPE OUT
CONSTRAINTS
PERMISSIONS
EXPECTED OUTPUT
ACCEPTANCE EVIDENCE
ESCALATION CONDITIONS
STOPPING CONDITION
```

## Result packet

```text
TASK ID
STATUS
SUMMARY
ARTIFACTS
EVIDENCE
TEST RESULTS
DECISIONS MADE
ASSUMPTIONS
DISCOVERIES
RISKS
UNRESOLVED ITEMS
RECOMMENDED FOLLOW-UP
```

## Event-based updates

Agents should report when something changes:

* Claimed.
* Started.
* Blocked.
* Waiting.
* Material discovery.
* Scope conflict.
* Review ready.
* Failed.
* Completed.

They should not produce constant narration merely to reassure the manager that they are still working.

---

# 13. Minimum database structure

A practical first version would need approximately these tables:

```text
projects
workstreams
tasks
task_dependencies
task_claims
agents
agent_capabilities
events
artifacts
reviews
decisions
risks
incidents
incident_actions
experiments
lessons
task_capsules
knowledge_nodes
knowledge_edges
```

The critical relationships are:

```text
Project
  └── Workstream
       └── Task
            ├── Claim
            ├── Dependencies
            ├── Events
            ├── Artifacts
            ├── Reviews
            ├── Decisions
            └── Task Capsule
```

A task should not become `DONE` merely because an agent says it is finished.

```text
DONE =
    output exists
    + acceptance evidence exists
    + required review passed
    + authoritative state updated
    + task capsule created
```

---

# 14. Metrics that would reveal whether the system works

Measure outcomes rather than activity.

## Delivery

* Time from ready to claimed.
* Time from claimed to accepted.
* Percentage completed without rework.
* Review rejection rate.
* Dependency wait time.
* Age of blocked tasks.

## Quality

* Defects found before acceptance.
* Defects found after acceptance.
* Repeat incident rate.
* Requirements missed.
* Unsupported claims detected.
* Rollback frequency.

## Coordination

* Duplicate task rate.
* Ownership conflicts.
* Manager escalations.
* Tasks with ambiguous status.
* Cross-workstream conflicts.

## Knowledge

* Task capsule completion rate.
* Successful retrieval rate.
* Lessons reused.
* Decisions retrieved before conflicting work.
* Stale or superseded knowledge discovered.
* Insights promoted into actual improvements.

## R&D

* Experiments completed.
* Hypotheses rejected.
* Experiments promoted to pilots.
* Pilots adopted.
* Improvements produced per unit of compute.
* Production failures caused by research transitions.

## Efficiency

* Compute cost per accepted task.
* Tokens per accepted task.
* Retrieval context size.
* Repeated reading of the same material.
* Agent idle and blocked time.

Do not optimize for:

* Number of agent messages.
* Number of ideas generated.
* Number of tasks created.
* Apparent agent activity.

Those can increase while actual productivity decreases.

---

# 15. Recommended implementation order for MAP

Building every department at once would create a large, difficult-to-debug bureaucracy. Implement the system in layers.

## Phase 1: Command and ownership

Build:

* Charter.
* Project state.
* Workstreams.
* Task records.
* One Task DRI per task.
* Atomic task claiming.
* Structured assignment and result packets.
* Append-only event log.
* Git-based artifact history.
* Basic review gate.

This establishes controlled execution.

## Phase 2: Triage and assurance

Add:

* Waiting and blocking records.
* Escalation deadlines.
* Incident records.
* Independent reviewers.
* Risk levels.
* Stop-the-line authority.
* Postmortems.
* Corrective-action tracking.

This establishes resilience.

## Phase 3: Memory and indexing

Add:

* Task capsules.
* Workstream digests.
* Full-text search.
* Semantic retrieval.
* Decision and requirement retrieval.
* Knowledge connections.
* Provenance links.

This establishes long-term memory.

## Phase 4: Research and emergence

Add:

* Insight ledger.
* Research proposals.
* Experiment records.
* Research sandboxes.
* Promotion gates.
* Transition reviews.
* Cross-task connection scanning.

This establishes disciplined innovation.

## Phase 5: Adaptive governance

Add:

* Reliability budgets.
* Resource allocation metrics.
* Automatic workflow selection.
* Manager load balancing.
* Capability performance history.
* Periodic policy review.
* Organizational restructuring based on actual workload.

This establishes self-improvement.

---

# Final model

The ideal system is:

> **Unified at the level of intent, singular at the level of ownership, decentralized at the level of execution, independent at the level of assurance, interruptible at the level of operations, experimental at the level of research, and durable at the level of memory.**

For MAP specifically, the central design should remain:

```text
Markdown and artifacts = project meaning
SQLite = operational coordination
Git = history and recovery
Task packets = communication
Independent review = assurance
Incident system = resilience
Task capsules and indexes = memory
R&D experiments = innovation
Human approval = final consequential authority
```

The central mistake to avoid is creating more intelligent-sounding agents without creating clearer ownership and state. A system with twenty capable agents and ambiguous authority will usually perform worse than a system with five agents, explicit contracts, independent review, and a reliable project record.

[1]: https://emilms.fema.gov/_is0200c/groups/242.html "emilms.fema.gov"
[2]: https://emilms.fema.gov/is_0362a/groups/103.html "emilms.fema.gov"
[3]: https://www.armyupress.army.mil/Journals/NCO-Journal/Archives/2020/May/Mission-Command/ "
	Mission Command
"
[4]: https://www.nasa.gov/about-nasas-ivv-program/ "About NASA's IV&V Program"
[5]: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ "

      
  AI RMF Core


      
  
  \- AIRC


    "
[6]: https://global.toyota/en/company/vision-and-philosophy/production-system/?padid=ag478_from_header_menu&utm_source=chatgpt.com "Toyota Production System | Vision & Philosophy | Company | Toyota Motor Corporation Official Global Website"
[7]: https://sre.google/workbook/postmortem-culture/ "Google SRE - Postmortem Practices for Incident Management"
[8]: https://sre.google/workbook/error-budget-policy/ "Google SRE - Error Budget Policy for Service Reliability"
[9]: https://www.darpa.mil/about/program-managers "Program Managers | DARPA"
[10]: https://www.nasa.gov/learning-resources/for-professionals/appel-lessons-learned/ "Lessons Learned - NASA"














====================
====================








# The Index Is Not Just Search; It Is the Project’s Thinking Memory

The system you are describing needs to do more than retrieve documents related to a question.

It must help an agent answer questions such as:

* What problems keep recurring?
* What capability built for one task could solve another problem?
* What did the user imply they would eventually need?
* Which ideas were previously rejected, and have the circumstances changed?
* Where are two parts of the project solving the same problem differently?
* What important feature is absent from the current plan?
* What temporary workaround should become a permanent feature?
* What information from six months ago has suddenly become relevant?

A normal vector database is not enough for this. Vector search finds text that is semantically similar to a query. It does not inherently understand project history, dependencies, contradictions, repeated friction, abandoned ideas, or the relationship between an unresolved problem and a newly created capability.

The proper design is a **layered project intelligence index**.

---

# 1. The central architecture

The system should maintain six representations of the project:

```text
Raw project record
        ↓
Contextual source chunks
        ↓
Task and document capsules
        ↓
Structured knowledge records
        ↓
Project relationship graph
        ↓
Hierarchical project summaries
```

Each layer serves a different purpose.

| Layer                  | Purpose                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| Raw record             | Preserves complete evidence                                         |
| Contextual chunks      | Supports precise retrieval of passages                              |
| Capsules               | Provides compact summaries of tasks and documents                   |
| Knowledge records      | Separates decisions, problems, ideas, constraints, and capabilities |
| Relationship graph     | Enables cross-referencing and multi-step reasoning                  |
| Hierarchical summaries | Lets the agent reason about the project globally                    |

The idea agent normally works with the upper layers. It follows links back to the raw record only when it needs evidence or clarification.

This is similar to the distinction between local retrieval and global understanding in Microsoft’s GraphRAG work. Traditional retrieval works reasonably well for specific questions but struggles with questions requiring understanding of an entire corpus. GraphRAG addresses this by extracting entities and relationships, grouping them into hierarchical communities, and generating summaries at multiple levels. ([Microsoft][1])

---

# 2. The canonical record must remain untouched

The index is not the project’s source of truth.

The source of truth consists of:

* Original project documents.
* Task instructions.
* Agent reports.
* User feedback.
* Decisions.
* Code changes.
* Test results.
* Reviews.
* Incidents.
* Research.
* Rejected proposals.
* Discussion records when materially important.

These records must be preserved because every summary and relationship produced by an AI may contain omissions or interpretation errors.

Each indexed item should therefore include provenance:

```yaml
record_id: KNOW-00881
record_type: constraint
statement: Search results must always link to their original evidence.
source_refs:
  - task: TASK-0142
    artifact: ART-0291
    location: "lines 44-51"
extracted_by: indexer-v3
extracted_at: 2026-07-21T11:42:00-04:00
confidence: 0.96
review_status: accepted
```

The AI may propose an interpretation, but the system must always be able to answer:

> Where did this information come from?

Without that, the index will slowly become a collection of summaries of summaries whose relationship to the actual project becomes uncertain.

---

# 3. Contextual source chunks

Documents and task reports still need to be divided into smaller passages for search. But the chunks cannot be stored without context.

A passage like:

> “This should be moved into the background process.”

is nearly useless by itself. The index needs to know:

* What “this” means.
* Which component is being discussed.
* Who proposed the change.
* Whether it was accepted.
* When it happened.
* Which project version it concerned.

The indexed version might therefore be:

```yaml
chunk_id: CHUNK-18442
source_id: TASK-REPORT-0317
source_type: task_report
project: MAP
workstream: indexing
task: TASK-0317
date: 2026-07-18
context: >
  The indexing agent is discussing the full-project graph rebuild,
  which currently blocks interactive project work.
text: >
  This should be moved into the background process.
entities:
  - indexing pipeline
  - graph rebuild
concepts:
  - background processing
  - performance bottleneck
status_context: recommendation
```

Contextual retrieval techniques add concise document-specific context before generating lexical and semantic indexes. This reduces the problem of passages losing their meaning when separated from their original documents. Anthropic’s published testing also found that combining exact-text retrieval with embeddings outperformed embeddings alone. ([Anthropic][2])

---

# 4. Task capsules

Every completed task should produce a compact, standardized record called a **task capsule**.

This is the primary unit the idea agent will review.

A capsule should not merely summarize what the agent said. It should extract the parts that could matter later.

```yaml
capsule_id: CAPSULE-0317
task_id: TASK-0317
project_id: MAP
workstream: indexing

objective:
  Reduce the time required to rebuild the project knowledge index.

trigger:
  Full rebuilds were blocking active project work.

inputs:
  - Existing indexing pipeline
  - Performance logs
  - TASK-0294

actions:
  - Profiled indexing stages
  - Added incremental document hashing
  - Skipped unchanged source records

outcome:
  Incremental rebuild implemented.

results:
  rebuild_time_before: 18m
  rebuild_time_after: 2m
  unchanged_records_skipped: 91%

decisions:
  - Incremental indexing is now the default.
  - Full rebuild remains available as a maintenance action.

capabilities_created:
  - Detect changed project records
  - Re-index only affected records
  - Track source-to-index dependencies

problems_encountered:
  - Community summaries can become stale after partial updates.

workarounds:
  - Rebuild affected community summaries after each batch.

unresolved_questions:
  - When should the entire hierarchy be recomputed?
  - How much change makes a community summary unreliable?

constraints_discovered:
  - Index outputs must be reproducible from canonical sources.
  - Stale summaries must be visibly marked.

reusable_patterns:
  - Content hashing for change detection
  - Dependency-based invalidation

possible_opportunities:
  - Use change detection to trigger the idea-discovery agent.
  - Apply dependency invalidation to documentation builds.

related_records:
  - TASK-0294
  - DECISION-0081
  - INCIDENT-0019

source_refs:
  - ARTIFACT-0442
  - REVIEW-0188
```

The capsule is normally between approximately 300 and 800 tokens. Complex tasks may require more, but the schema should remain consistent.

## Why capsules matter

Assume a project has 10,000 completed tasks.

At an average of 3,000 tokens per complete task record, reading everything would require approximately 30 million tokens.

At an average of 500 tokens per capsule, the compressed task history would require approximately 5 million tokens. That is still too large for one prompt, but it is small enough to:

* Cluster.
* Index.
* Summarize hierarchically.
* Search efficiently.
* Analyze in batches.
* Track coverage.

The raw record remains available behind each capsule.

---

# 5. Structured knowledge records

Capsules are compact, but they are still documents. Important concepts must also be extracted into individually addressable records.

I would use the following knowledge types.

## Core record types

| Type          | Meaning                                               |
| ------------- | ----------------------------------------------------- |
| `GOAL`        | Desired project outcome                               |
| `REQUIREMENT` | Something the system must do                          |
| `CONSTRAINT`  | A limit or boundary                                   |
| `DECISION`    | An accepted choice                                    |
| `ASSUMPTION`  | Something currently treated as true                   |
| `PROBLEM`     | A known failure or deficiency                         |
| `FRICTION`    | Repeated difficulty or inefficiency                   |
| `CAPABILITY`  | Something the project can currently do                |
| `WORKAROUND`  | Temporary solution                                    |
| `IDEA`        | Proposed improvement                                  |
| `QUESTION`    | Unresolved uncertainty                                |
| `RISK`        | Potential harmful outcome                             |
| `LESSON`      | Reusable conclusion from experience                   |
| `PATTERN`     | Repeated structure across records                     |
| `METRIC`      | Observable measurement                                |
| `EXPERIMENT`  | Controlled test                                       |
| `USER_SIGNAL` | User behavior, preference, complaint, or request      |
| `ARTIFACT`    | Produced file, component, document, or implementation |

Example:

```yaml
knowledge_id: PROBLEM-0144
type: problem
name: Community summaries become stale
description: >
  Incremental indexing updates source records and local graph nodes,
  but higher-level community summaries may still describe the previous state.
status: active
severity: moderate
first_observed: 2026-07-18
last_observed: 2026-07-21
observed_count: 3
source_refs:
  - CAPSULE-0317
  - INCIDENT-0019
related_capabilities:
  - CAPABILITY-0082
related_constraints:
  - CONSTRAINT-0037
owner: knowledge-office
```

This allows the system to search directly for all:

* Active problems.
* Unused capabilities.
* Repeated workarounds.
* Unresolved questions.
* Decisions potentially affected by new evidence.
* User complaints associated with a particular component.

---

# 6. The project relationship graph

The knowledge records become nodes in a graph.

The graph records not just that two items are “similar,” but **how they are related**.

## Important relationship types

```text
REQUIRES
DEPENDS_ON
IMPLEMENTS
CONTRADICTS
SUPPORTS
CAUSES
MITIGATES
BLOCKS
SUPERSEDES
DERIVED_FROM
DISCOVERED_DURING
REUSES
CO_OCCURS_WITH
AFFECTS
PRODUCES
VALIDATES
INVALIDATES
SIMILAR_TO
ALTERNATIVE_TO
PART_OF
OWNED_BY
REQUESTED_BY
FAILED_BECAUSE
WORKAROUND_FOR
POTENTIAL_APPLICATION_OF
```

Example:

```text
[User Goal: natural agent collaboration]
        REQUIRES
[Capability: shared project memory]

[Problem: repeated rereading]
        MITIGATED_BY
[Capability: task capsules]

[Capability: change detection]
        POTENTIAL_APPLICATION_OF
[Problem: stale documentation]

[Constraint: low token use]
        CONFLICTS_WITH
[Approach: full-history scan]

[Workaround: manually rebuild summaries]
        WORKAROUND_FOR
[Problem: stale community summaries]
```

The graph is what permits the agent to discover that a capability built for indexing might also solve a documentation problem, even when the wording in the two source tasks is not especially similar.

Vector similarity might say:

> These two passages discuss updating information.

The graph can say:

> This capability detects changed records, and this unresolved problem requires detecting changed records.

That is a much stronger basis for generating an idea.

GraphRAG’s indexing pipeline similarly separates document chunking, graph and claim extraction, entity embedding, community detection, and community-report generation. ([Microsoft][3])

---

# 7. Hierarchical summaries

Even task capsules eventually become too numerous for direct review.

The system therefore needs summaries at several levels.

```text
Individual source passage
        ↓
Task capsule
        ↓
Topic summary
        ↓
Workstream summary
        ↓
Project-area summary
        ↓
Whole-project strategic summary
```

Example:

```text
Project: MAP
│
├── Agent Coordination
│   ├── Task claiming
│   ├── Manager-agent communication
│   └── Handoffs
│
├── Knowledge System
│   ├── Task capsules
│   ├── Retrieval
│   ├── Graph relationships
│   └── Archival storage
│
├── Reliability
│   ├── Triage
│   ├── Incident response
│   └── Review systems
│
└── Research and Emergence
    ├── Idea discovery
    ├── Experimentation
    └── Project-wide pattern detection
```

Each node receives its own summary:

```yaml
community_id: COMMUNITY-KNOWLEDGE-RETRIEVAL
level: 3
title: Project knowledge retrieval
summary: >
  MAP uses task capsules and layered retrieval to avoid repeatedly
  loading complete task histories. Current work has established incremental
  indexing and exact-text search. The main unresolved issue is keeping
  higher-level summaries synchronized after partial updates.
major_capabilities:
  - Incremental indexing
  - Task capsule generation
  - Exact metadata retrieval
major_problems:
  - Summary invalidation
  - Weak cross-workstream relationship extraction
open_questions:
  - Rebuild threshold
  - Appropriate graph depth
recent_changes:
  - TASK-0317
child_communities:
  - COMMUNITY-CAPSULES
  - COMMUNITY-GRAPH
  - COMMUNITY-SEARCH
```

Recursive tree-based retrieval methods such as RAPTOR construct multiple levels of abstraction by clustering and summarizing lower-level records. This allows retrieval from both detailed sources and broader summaries instead of relying only on isolated text chunks. ([arXiv][4])

---

# 8. The indexes that should exist

The project should not have one search index. It should have several complementary indexes.

## A. Metadata index

For exact filtering:

* Project.
* Workstream.
* Date.
* Task status.
* Knowledge type.
* Owner.
* Risk.
* Confidence.
* Review status.
* Source.
* Version.

Example:

```sql
SELECT *
FROM knowledge_records
WHERE project_id = 'MAP'
  AND record_type = 'problem'
  AND status = 'active'
  AND last_observed_at > '2026-06-01';
```

## B. Full-text index

For exact language, identifiers, names, and terminology.

It handles searches such as:

* `TASK-0317`
* `"stale community summary"`
* `"user must approve"`
* `"markdown export"`
* `token limit`

SQLite’s FTS5 extension provides built-in full-text indexing suitable for an initial local implementation. ([SQLite][5])

## C. Semantic vector index

For conceptually related material that uses different language.

For example:

* “Agents repeatedly reread old reports.”
* “Historical context consumes too many tokens.”
* “Each run reconstructs prior project state.”

These may be semantically close even though they share few exact words.

Vector search should never be the sole retrieval mechanism. Exact-text and semantic searches return differently scaled scores, so their results should be ranked separately and then combined through rank fusion or reranking rather than comparing raw values directly. ([Anthropic][2])

## D. Relationship index

For traversing explicit graph connections:

```text
problem
  → caused by
  → constraint
  → affected component
  → related capability
  → previous experiment
```

## E. Temporal index

For questions involving change:

* What recently changed?
* Which old decisions predate a major new capability?
* Which unresolved problem has remained open longest?
* Which workaround has become permanent in practice?
* Which idea was rejected before its prerequisites existed?

## F. Coverage index

This is essential for idea discovery.

It records:

* When every task was last considered by the idea agent.
* Which other project areas it was compared against.
* At what abstraction level it was reviewed.
* Whether its raw sources were sampled.
* What discoveries resulted.

Example:

```yaml
record_id: CAPSULE-0317
last_local_review: 2026-07-21
last_cross_workstream_review: 2026-07-21
last_global_review: 2026-07-19
comparison_communities:
  - documentation
  - incident-management
  - retrieval
coverage_score: 0.84
next_review_due: 2026-07-28
```

Without this, the agent will preferentially revisit recent, popular, or highly connected information and overlook quiet areas of the project.

---

# 9. Incremental indexing

The entire index should not be rebuilt every time a task changes.

Every canonical item receives a content hash:

```text
source record
    ↓
calculate content hash
    ↓
compare with previously indexed hash
    ↓
unchanged → do nothing
changed → update affected layers
```

## Update sequence

When a task completes:

```text
1. Save the complete task record.
2. Generate or update its task capsule.
3. Extract structured knowledge records.
4. Extract entities, concepts, claims, and relationships.
5. Update the full-text index.
6. Generate embeddings for changed records.
7. Update graph nodes and edges.
8. Identify affected topic communities.
9. Mark their summaries stale.
10. Regenerate only affected summaries.
11. Add the changed material to the idea-agent queue.
12. Update the coverage ledger.
```

The dependency chain might look like:

```text
TASK-0317
   ├── CAPSULE-0317
   ├── PROBLEM-0144
   ├── CAPABILITY-0082
   ├── DECISION-0081
   ├── COMMUNITY-INCREMENTAL-INDEXING
   └── COMMUNITY-KNOWLEDGE-SYSTEM
```

Changing `TASK-0317` invalidates these derived records. It does not require rebuilding unrelated project areas.

Microsoft’s GraphRAG implementation similarly treats indexing as a sequence of separate workflows and uses caching so repeated calls with the same inputs can return existing results. Its configuration also supports incremental indexing and preserved outputs. ([Microsoft][3])

---

# 10. How the idea agent examines the entire project

The idea agent should use four complementary modes.

## Mode 1: Change-triggered review

Runs whenever meaningful new information is added.

It asks:

> What existing project knowledge does this new information affect?

Process:

```text
New task or decision
        ↓
Extract concepts, problems, capabilities, and constraints
        ↓
Retrieve nearest lexical and semantic matches
        ↓
Traverse connected graph neighborhoods
        ↓
Compare with relevant community summaries
        ↓
Generate possible connections
```

This is the cheapest and most frequent mode.

---

## Mode 2: Problem-driven review

Starts with active problems, friction, workarounds, and unresolved questions.

For every active problem:

1. Retrieve capabilities semantically related to the problem.
2. Retrieve capabilities connected through shared entities.
3. Retrieve solutions used in other workstreams.
4. Retrieve previous failed attempts.
5. Check whether the conditions causing previous failure still apply.
6. Search external research when allowed.
7. Generate candidate solutions.

Example:

```text
Problem:
Community summaries become stale after incremental changes.

Available capabilities:
- Source hashing
- Dependency invalidation
- Change event stream
- Task relationship graph

Potential idea:
Use graph dependency propagation to identify and refresh only summaries
whose supporting nodes changed.
```

No source had to explicitly state that idea. It emerges from connecting a problem with separately created capabilities.

---

## Mode 3: Cross-community review

This is where genuinely unexpected ideas are most likely to emerge.

The agent deliberately compares project areas that are not normally reviewed together.

Examples:

```text
Indexing × Incident Management
User Interface × Agent Permissions
Task Handoffs × Knowledge Retrieval
Research Experiments × Review Failures
User Feedback × System Metrics
```

For each pair, the agent asks:

* Can a capability from one area solve a problem in the other?
* Are both areas independently duplicating the same mechanism?
* Does one area violate a constraint established by the other?
* Can their data be combined into a new feature?
* Does one create information the other is currently missing?

The system should prioritize community pairs based on:

* Shared concepts.
* Complementary problem and capability records.
* Common user goals.
* Dependency proximity.
* Lack of previous comparison.
* Recent changes.
* Repeated friction.
* Strategic importance.

But it should also reserve some capacity for weakly connected or randomly selected pairs. Otherwise it will only discover obvious relationships.

---

## Mode 4: Global coverage sweep

This runs less frequently.

It examines the hierarchical summaries of the whole project rather than every raw record.

The process is:

```text
Whole-project summary
        ↓
Major project-area summaries
        ↓
Relevant workstream summaries
        ↓
Selected task capsules
        ↓
Raw evidence only where required
```

Microsoft’s dynamic community-selection approach uses this type of top-down traversal: begin with high-level communities, remove irrelevant branches early, and descend only into relevant subcommunities. This permits broad corpus coverage without loading every source into the model at once. ([Microsoft][6])

The global review should ask:

* What project goals are receiving little current work?
* Which requirements lack implementing capabilities?
* Which capabilities have no current use?
* Which problems have no owners?
* Which user requests are not represented in the roadmap?
* Which decisions rely on outdated assumptions?
* Which workstreams are converging on the same concept?
* Which areas have accumulated many workarounds?
* Which project principles are frequently violated?
* What expected feature is absent?

---

# 11. The idea-generation operators

The agent should not merely receive the prompt:

> Find good ideas.

It should apply explicit reasoning operators.

## Operator 1: Requirement completion

```text
Goal + missing prerequisite → proposed feature
```

Example:

```text
Goal: Users can safely close and reopen a project.
Known capabilities: Create and edit documents.
Missing prerequisite: Persistent storage.
Idea: Add save, autosave, and recovery.
```

This is how the system would infer that a word processor needs saving even if the original request did not mention it.

---

## Operator 2: Capability recombination

```text
Capability A + capability B → new combined feature
```

Example:

```text
Markdown parser
+ project search
= searchable wikilinked project notebook
```

---

## Operator 3: Problem-capability matching

```text
Unresolved problem in Area A
+ capability from Area B
= possible solution
```

---

## Operator 4: Workaround promotion

```text
Repeated workaround
+ frequent use
+ stable results
= candidate permanent feature
```

A workaround used once may remain temporary. A workaround appearing in twelve task capsules should become a design candidate.

---

## Operator 5: Contradiction detection

```text
Decision A contradicts requirement B
```

Example:

```text
Decision:
Agents may write directly to the project folder.

Constraint:
All consequential changes require independent review.

Idea:
Introduce staging branches and gated promotion.
```

---

## Operator 6: Assumption invalidation

```text
Old decision
+ changed assumption
= decision requiring reconsideration
```

Example:

```text
Old decision:
Full project scans are acceptable because the corpus is small.

Changed condition:
The project now contains 8,000 tasks.

Idea:
Replace full scans with incremental hierarchical retrieval.
```

---

## Operator 7: Repeated-friction consolidation

```text
Several superficially different problems
+ shared cause
= structural improvement
```

Example:

```text
- Agents reread instructions.
- Reviewers miss prior decisions.
- Managers repeat project context.
- Research agents duplicate experiments.

Shared cause:
Weak project memory retrieval.

Idea:
Create a common context assembly service.
```

---

## Operator 8: Negative-space analysis

The agent examines what is missing.

For each major system object, ask:

```text
How is it created?
How is it viewed?
How is it changed?
How is it saved?
How is it recovered?
How is it deleted?
How is it audited?
How is it shared?
How does failure appear?
```

This finds ordinary but necessary features that creative brainstorming often overlooks.

---

## Operator 9: Analogy transfer

The agent compares the project with patterns from other systems.

Example:

```text
Observed problem:
Agents continue producing dependent work after an upstream failure.

Analogous system:
Toyota stop-the-line authority.

Idea:
Create a dependency-aware STOP_REQUESTED event that pauses downstream tasks.
```

---

## Operator 10: Simplification

The agent asks:

* Which mechanisms overlap?
* Which steps exist only because of an earlier limitation?
* Which policy can become an automatic invariant?
* Which communication can be replaced with shared state?
* Which summary can be generated from structured records?

Idea generation should include removal and consolidation, not just adding features.

---

# 12. Candidate idea generation

The agent should first generate **connections**, not polished proposals.

Example intermediate record:

```yaml
connection_id: CONNECTION-0192

trigger:
  - PROBLEM-0144

connected_records:
  - CAPABILITY-0082
  - CAPABILITY-0061
  - DECISION-0081

connection_type: problem_capability_match

observation: >
  The system already tracks source-to-index dependencies and changed
  records. Those capabilities appear sufficient to identify which
  community summaries need regeneration.

initial_confidence: 0.78
```

Only after generating multiple connections should it produce an idea:

```yaml
idea_id: IDEA-0094
title: Dependency-aware summary invalidation

problem:
  Higher-level project summaries become stale after incremental updates.

proposal:
  Track which source nodes support each generated summary. When a source
  changes, traverse the dependency graph and mark only dependent summaries
  stale. Rebuild them in bottom-up order.

benefit:
  - Preserves incremental indexing speed
  - Reduces stale project understanding
  - Avoids unnecessary global rebuilds

evidence:
  - PROBLEM-0144
  - CAPABILITY-0082
  - CAPABILITY-0061
  - TASK-0317

novelty_check:
  similar_existing_ideas: []
  status: apparently_new

risks:
  - Dependency maps may become incomplete
  - Minor changes may cause unnecessary invalidation

proposed_experiment:
  Compare summary freshness and rebuild cost against full regeneration.

confidence: 0.82
status: proposed
```

---

# 13. Scoring ideas

The idea agent should not submit every possible connection.

A practical score could be:

```text
Idea Score =
    strategic_alignment
  × expected_value
  × evidence_strength
  × novelty
  × feasibility
  × confidence
  × affected_scope

divided by:

    implementation_cost
  × operational_risk
  × complexity_penalty
```

Each factor can be scored from 0.1 to 1.0.

Example:

```yaml
strategic_alignment: 0.95
expected_value: 0.80
evidence_strength: 0.90
novelty: 0.75
feasibility: 0.85
confidence: 0.82
affected_scope: 0.80

implementation_cost: 0.40
operational_risk: 0.30
complexity_penalty: 0.35
```

The system should maintain separate categories rather than relying only on one number:

| Category               | Meaning                                |
| ---------------------- | -------------------------------------- |
| Quick win              | High value, low cost                   |
| Strategic opportunity  | High value, larger investment          |
| Research candidate     | Promising but uncertain                |
| Quality improvement    | Reduces error or friction              |
| Architectural issue    | Requires system-level attention        |
| Speculative connection | Interesting but weak evidence          |
| Rejected               | Duplicated, misaligned, or impractical |

---

# 14. Ensuring that all information is eventually reviewed

This is the hardest part.

Incremental retrieval alone does **not** guarantee that the agent truly considers the whole project. It may repeatedly inspect:

* Recent material.
* Highly connected nodes.
* Frequently mentioned concepts.
* Areas using common vocabulary.
* Areas already considered important.

The solution is a **coverage scheduler**.

## Coverage dimensions

Every record should be reviewed along several dimensions:

```text
Local review
    Compared with its direct neighbors.

Workstream review
    Compared with records in the same area.

Cross-workstream review
    Compared with other project areas.

Temporal review
    Compared with older and newer information.

Strategic review
    Compared with project goals and principles.

Random exploration
    Compared with weakly related or previously unexamined material.
```

## Coverage matrix

```text
                    Coordination  Memory  Reliability  R&D  Interface
Coordination             —          ✓        ✓         ○       ✓
Memory                    ✓          —        ✓         ✓       ○
Reliability               ✓          ✓        —         ○       ✓
R&D                       ○          ✓        ○         —       ✓
Interface                 ✓          ○        ✓         ✓       —
```

Legend:

* `✓` reviewed recently.
* `○` overdue.
* `—` same area.

The scheduler prioritizes overdue comparisons.

## Coverage debt

Each record accumulates coverage debt over time:

```text
Coverage debt increases when:
- The record has not been reviewed recently.
- Its source changed.
- A related project area changed.
- Its underlying assumptions changed.
- It has never been compared with a particular community.
- It is strategically important.
- It represents an unresolved problem.

Coverage debt decreases when:
- It is reviewed.
- The agent follows its evidence.
- It is compared across communities.
- A resulting connection is evaluated.
```

This makes corpus review systematic instead of dependent on what the model happens to retrieve.

---

# 15. Preventing summaries from hiding important details

Hierarchical summarization creates a real risk:

> A detail omitted at a lower level may never appear at a higher level.

Several protections are necessary.

## Preserve typed exceptions

Some information must never be compressed away:

* Hard constraints.
* Unresolved safety risks.
* Human directives.
* Rejected decisions and their rationale.
* Legal or security boundaries.
* Critical incidents.
* Open blockers.
* Explicit user dissatisfaction.
* High-confidence contradictions.

These records should be attached directly to all relevant higher-level summaries.

## Maintain source diversity

When building a project summary, the system should not simply select the most similar records. It should include:

* Major goals.
* Major capabilities.
* Major problems.
* Constraints.
* Unresolved questions.
* Recent changes.
* Contradictions.
* Minority or dissenting views.
* Low-frequency but high-severity items.

## Periodic raw-source sampling

The idea agent should periodically inspect randomly selected raw records and compare them with their capsules.

This answers:

* Did the capsule omit something important?
* Has the extraction schema become biased?
* Are certain kinds of information routinely lost?
* Are agents reporting information in a form the indexer cannot understand?

## Capsule quality audits

```text
Raw task
   ↓
Independent capsule regeneration
   ↓
Compare against stored capsule
   ↓
Identify missing or distorted knowledge
```

---

# 16. Recommended retrieval process for the idea agent

When performing a project-improvement review, the system should assemble context in this order.

```text
1. Current project charter and principles
2. Current strategic goals
3. Current high-level project summary
4. Recent changes
5. Active problems and unresolved questions
6. Existing capabilities
7. Repeated workarounds and friction
8. Relevant community summaries
9. Candidate task capsules
10. Exact source passages for verification
```

The agent should not start with a general semantic query such as:

> Find interesting things.

It should perform a set of targeted retrieval passes.

## Suggested retrieval passes

```text
Pass A: active problems → possible capabilities
Pass B: capabilities → unused applications
Pass C: repeated friction → shared causes
Pass D: requirements → missing implementation
Pass E: old decisions → changed assumptions
Pass F: recent changes → affected project areas
Pass G: rejected ideas → newly satisfied prerequisites
Pass H: workarounds → permanent-feature candidates
Pass I: community pairings → cross-domain opportunities
Pass J: coverage debt → neglected material
```

Each pass produces a candidate set. The sets are deduplicated, reranked, and then verified against their sources.

---

# 17. A complete example

Assume the project is building a word processor.

## Existing records

```text
GOAL-01:
Create a simple writing application.

CAPABILITY-01:
The editor can accept and display text.

CAPABILITY-02:
The application can parse Markdown.

PROBLEM-01:
Users lose work when the program closes.

FRICTION-01:
Users manually copy text into another program for backup.

USER-SIGNAL-01:
Users frequently reopen documents they worked on previously.

CONSTRAINT-01:
The interface must remain simple.
```

## Indexed relationships

```text
GOAL-01 REQUIRES CAPABILITY-01
PROBLEM-01 AFFECTS GOAL-01
FRICTION-01 WORKAROUND_FOR PROBLEM-01
USER-SIGNAL-01 IMPLIES persistent document access
CAPABILITY-02 SUPPORTS structured document format
CONSTRAINT-01 LIMITS interface complexity
```

## Idea-agent reasoning

### Requirement completion

A writing tool that users reopen later requires persistence.

### Workaround promotion

Repeated copying into another program indicates an unmet save requirement.

### Capability recombination

Markdown already provides a portable storage representation.

### Simplicity constraint

Saving should not require a complicated project-management interface.

## Resulting idea

```yaml
title: Automatic Markdown-backed document persistence

proposal: >
  Store documents automatically as Markdown files while providing a
  simple Save As command for explicit control.

derived_from:
  - GOAL-01
  - CAPABILITY-02
  - PROBLEM-01
  - FRICTION-01
  - USER-SIGNAL-01
  - CONSTRAINT-01

reasoning:
  - Persistence is required by observed user behavior.
  - Markdown capability already exists.
  - Automatic persistence reduces interface complexity.
```

The system did not invent randomly. It combined project evidence into a missing feature.

---

# 18. Practical first implementation

For a local or medium-sized MAP implementation, I would not begin with a separate graph database.

Start with:

```text
Canonical Markdown/JSON files
        +
SQLite operational database
        +
SQLite FTS5
        +
A vector index
        +
Relationship tables in SQLite
```

## Minimum tables

```sql
sources
source_versions
chunks
task_capsules
knowledge_records
knowledge_sources
entities
relationships
communities
community_members
community_summaries
embeddings
ideas
idea_evidence
coverage_records
coverage_comparisons
index_jobs
```

## Relationship table

```sql
CREATE TABLE relationships (
    relationship_id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    description TEXT,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_relationship_source
ON relationships(source_node_id, relationship_type);

CREATE INDEX idx_relationship_target
ON relationships(target_node_id, relationship_type);
```

## Coverage table

```sql
CREATE TABLE coverage_records (
    record_id TEXT PRIMARY KEY,
    last_local_review_at TEXT,
    last_workstream_review_at TEXT,
    last_cross_project_review_at TEXT,
    last_global_review_at TEXT,
    last_raw_source_check_at TEXT,
    coverage_debt REAL NOT NULL DEFAULT 1.0,
    next_review_at TEXT
);
```

## Pairwise coverage

```sql
CREATE TABLE coverage_comparisons (
    community_a TEXT NOT NULL,
    community_b TEXT NOT NULL,
    last_compared_at TEXT,
    comparison_count INTEGER NOT NULL DEFAULT 0,
    discoveries_count INTEGER NOT NULL DEFAULT 0,
    coverage_debt REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (community_a, community_b)
);
```

At larger scale, the graph can be moved to a dedicated graph database. A graph database can combine explicit relationship traversal with vector similarity over nodes and relationships, but that additional infrastructure is not required for the first working version. ([Graph Database & Analytics][7])

---

# 19. Agent roles within the indexing system

The indexing system should use several distinct roles.

## Ingestion agent

* Detects new or changed sources.
* Normalizes metadata.
* Creates chunks.
* Preserves provenance.

## Capsule agent

* Generates task and document capsules.
* Extracts outcomes, problems, capabilities, and questions.
* Does not generate new project ideas.

## Knowledge extraction agent

* Creates typed knowledge records.
* Extracts graph relationships.
* Assigns confidence.
* Flags uncertain relationships.

## Community agent

* Groups related concepts.
* Maintains topic hierarchies.
* Regenerates affected summaries.

## Idea-discovery agent

* Applies the reasoning operators.
* Generates candidate connections and proposals.
* Cannot modify project requirements directly.

## Evidence reviewer

* Follows candidate ideas back to source material.
* Rejects unsupported connections.
* Detects duplicate ideas.
* Checks whether an idea was already considered.

## Knowledge steward

* Resolves duplicate entities.
* Corrects misleading summaries.
* Maintains taxonomy.
* Approves promoted knowledge.

Separating extraction from idea generation matters. Otherwise an idea-producing agent may subtly rewrite the index to make its own idea appear better supported.

---

# 20. The complete operating cycle

```text
New project activity
        ↓
Canonical record saved
        ↓
Changed content detected
        ↓
Capsule and knowledge extraction
        ↓
Text, vector, graph, and timeline indexes updated
        ↓
Affected summaries invalidated and refreshed
        ↓
Change-triggered idea review
        ↓
Candidate connections generated
        ↓
Evidence review and duplicate check
        ↓
Idea scored
        ↓
Reject / Archive / Research / Recommend
        ↓
Coverage ledger updated
        ↓
Periodic cross-community and global sweeps
```

The core principle is:

> **The agent does not reread the entire project. It reviews an incrementally maintained map of the entire project, then follows selected paths back to the evidence.**

That distinction makes the system scalable while still allowing project-wide reasoning.

The index tells the agent:

* What exists.
* What changed.
* What remains unresolved.
* How things are connected.
* Which areas have not recently been compared.
* Where the original evidence can be found.

The idea agent then operates over that map using deliberate discovery procedures rather than open-ended brainstorming.

[1]: https://www.microsoft.com/en-us/research/blog/graphrag-new-tool-for-complex-data-discovery-now-on-github/?msockid=3e7cddf773fa60560651cb96726f6172&utm_source=chatgpt.com "GraphRAG: New tool for complex data discovery now on GitHub - Microsoft Research"
[2]: https://www.anthropic.com/engineering/contextual-retrieval?utm_source=chatgpt.com "Contextual Retrieval in AI Systems \ Anthropic"
[3]: https://microsoft.github.io/graphrag/index/architecture/?utm_source=chatgpt.com "Architecture - GraphRAG"
[4]: https://arxiv.org/abs/2401.18059?utm_source=chatgpt.com "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval"
[5]: https://www.sqlite.org/fts5.html?utm_source=chatgpt.com "SQLite FTS5 Extension"
[6]: https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/?lang=ja&utm_source=chatgpt.com "GraphRAG: Improving global search via dynamic community selection - Microsoft Research"
[7]: https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/?utm_source=chatgpt.com "Vector indexes - Cypher Manual"

