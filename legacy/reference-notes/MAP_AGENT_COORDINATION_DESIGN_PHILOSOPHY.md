# MAP Agent Coordination Design Philosophy

**Version:** 1.0  
**Date:** July 17, 2026  
**Purpose:** A framework-independent philosophy and operating model for coordinating AI agents on long-running or complex projects.

---

## Executive Summary

AI agents do not inherently need meetings. They need the **functions that useful meetings perform**:

- establishing a shared objective;
- assigning responsibility;
- sharing discoveries;
- detecting conflicts and failures;
- revising plans when reality changes;
- making decisions with clear authority;
- preserving knowledge across agents and sessions;
- evaluating whether the work actually succeeded.

A human meeting is only one way to perform those functions. For AI systems, continuous structured state-sharing and event-triggered review will usually be more efficient, reliable, and auditable than open-ended conversation.

MAP should therefore treat a “meeting” as a **temporary coordination protocol**, not as a calendar event or social ritual. Agents should deliberate only when deliberation is likely to improve a decision. Routine progress should be communicated through shared records, tests, state transitions, and concise handoffs.

> **The purpose of agent coordination is not to prove that the plan is working. It is to maintain the clearest available shared model of reality and decide what that reality now requires.**

The default MAP coordination model should be:

1. **Initialize the project explicitly.**
2. **Keep one authoritative project state.**
3. **Give every agent a narrow role and output contract.**
4. **Coordinate asynchronously by default.**
5. **Trigger deliberation only when defined conditions occur.**
6. **Separate proposals, evidence, decisions, and execution.**
7. **Assign one owner to every decision and deliverable.**
8. **Test outcomes instead of trusting reports.**
9. **Record why important decisions were made.**
10. **Escalate uncertainty and consequences, not ordinary work.**
11. **Preserve validated lessons, not untested impressions.**
12. **Use the simplest architecture that can reliably complete the task.**

---

# 1. The Central Distinction: Meetings Versus Coordination

Human organizations often use meetings because people have fragmented knowledge, limited visibility, social obligations, and a need to negotiate shared commitment. Meetings also compensate for weak documentation and disconnected systems.

AI agents do not require the social form of a meeting. They do not need to feel included, maintain status, read a room, or receive emotional reassurance. They do, however, require technical equivalents for the informational and governance functions underneath those human needs.

| Human meeting function | MAP equivalent |
|---|---|
| Agree on the purpose | Project charter and success criteria |
| Assign roles | Agent contracts, permissions, and ownership |
| Report progress | Authoritative project state and task ledger |
| Share findings | Structured discovery records with evidence |
| Discuss alternatives | Bounded proposal-and-review protocol |
| Resolve disagreement | Decision rule and named decision owner |
| Approve a change | Change classification and approval gate |
| Identify blockers | Automated checks and exception events |
| Preserve institutional memory | Decision records, artifacts, and validated memory |
| Learn after completion | Evaluation, retrospective, and updated tests |

The design question should never begin with:

> “How often should the agents meet?”

It should begin with:

> “What information, decision, or coordination failure requires interaction, and what is the least expensive reliable mechanism for handling it?”

---

# 2. MAP’s Core Philosophy

## 2.1 Reality outranks the plan

The plan is a model of how the project is expected to unfold. It is not the project itself.

Agents must be permitted—and required—to revise a plan when evidence shows that its assumptions are false, its dependencies have changed, or its path no longer serves the goal. Adherence to an obsolete plan is not discipline. It is failure to incorporate information.

At the same time, novelty alone is not evidence. A new idea should not interrupt execution merely because it is interesting. Proposed changes must identify the affected assumption, expected benefit, cost, risk, and verification method.

**Rule:** Preserve the objective when possible; revise the route when justified.

---

## 2.2 Shared state outranks shared conversation

A conversation is transient and sequential. An authoritative state record is persistent, inspectable, and available to every authorized agent.

Agents should not depend on having read every earlier message. Important information must be promoted from conversation into durable project artifacts.

**Rule:** If another agent must know it later, it does not belong only in chat history.

Examples of information that must be durable:

- current objective and success criteria;
- active constraints;
- task status and ownership;
- accepted discoveries;
- unresolved questions;
- approved decisions;
- test results;
- known risks;
- changes to scope or architecture;
- instructions needed by the next agent or session.

---

## 2.3 Evidence outranks confidence

Language models can express certainty without reliable grounding. Confidence statements may be useful, but they are not substitutes for evidence.

Every material claim should be accompanied by one or more of the following when possible:

- a source;
- a reproducible observation;
- a test result;
- a file, trace, or log location;
- an explicit derivation;
- a clearly labeled inference;
- a statement that verification is unavailable.

**Rule:** The system should reward verifiability, not persuasive wording.

---

## 2.4 Outcomes outrank activity

Agents can generate large amounts of apparently productive work: plans, summaries, code, analyses, or discussion. Activity is not progress unless it changes the project’s verified state.

Progress should be defined by observable conditions such as:

- a test changing from failing to passing;
- an accepted deliverable being produced;
- a dependency being resolved;
- a decision being made and recorded;
- a risk being reduced;
- a user-visible requirement being satisfied;
- a verified research question being answered.

**Rule:** Reports describe progress; tests and accepted artifacts establish it.

---

## 2.5 Clear ownership outranks collective ambiguity

Multiple agents may contribute ideas, evidence, criticism, and alternatives. That does not mean every decision should be collective.

Each task and decision should have one accountable owner. Other agents may advise, review, or veto within explicitly defined limits. Without ownership, agents can circulate suggestions indefinitely, duplicate work, or assume another agent will act.

**Rule:** Collaboration may be distributed; accountability may not be undefined.

---

## 2.6 Simplicity outranks theatrical intelligence

A complex multi-agent conversation can look sophisticated while performing worse than a simple workflow.

MAP should begin with one capable agent and deterministic tools where possible. Additional agents should be introduced only when they provide a concrete advantage, such as:

- independent parallel work;
- different tools or permissions;
- genuinely different expertise or instructions;
- context isolation;
- independent verification;
- policy separation;
- clearer traceability;
- resilience against a single agent’s blind spots.

**Rule:** Do not create an agent merely to imitate an organizational role.

---

# 3. The Default Coordination Architecture

MAP should use a **shared-state, event-driven, orchestrator-supported** model.

## 3.1 Authoritative project state

Each project should have one canonical state store. It may be a set of Markdown and JSON files, a database, or another durable system, but agents must know which representation is authoritative.

A practical project structure might be:

```text
/project
├── CHARTER.md
├── STATE.json
├── TASKS.json
├── REQUIREMENTS.json
├── RISKS.md
├── DECISIONS/
├── DISCOVERIES/
├── HANDOFFS/
├── EVALUATIONS/
├── ARTIFACTS/
└── CHANGELOG.md
```

Suggested responsibilities:

- `CHARTER.md`: stable purpose, scope, constraints, roles, and success criteria.
- `STATE.json`: current phase, health, blockers, active assumptions, and next required action.
- `TASKS.json`: task status, owner, dependencies, and acceptance conditions.
- `REQUIREMENTS.json`: testable requirements and pass/fail status.
- `RISKS.md`: material risks, likelihood, impact, mitigation, and owner.
- `DECISIONS/`: durable records of significant decisions.
- `DISCOVERIES/`: new evidence or findings that may affect the plan.
- `HANDOFFS/`: concise context needed by the next agent or session.
- `EVALUATIONS/`: tests, graders, results, and known limitations.
- `ARTIFACTS/`: outputs produced by the project.
- `CHANGELOG.md`: material changes to project state or direction.

The exact file layout is optional. The principle is not.

---

## 3.2 Orchestrator

The orchestrator is responsible for coordination, not for pretending to be an executive.

Its duties should include:

- interpreting the project charter;
- decomposing work when decomposition is useful;
- selecting the simplest adequate workflow;
- assigning bounded tasks;
- preventing duplicate work;
- checking dependencies;
- deciding whether a coordination event is necessary;
- collecting structured results;
- routing results to reviewers or decision owners;
- updating or verifying the authoritative state;
- stopping work when success or a stopping condition is reached.

The orchestrator should not automatically perform all substantive work. It should also not create agents without a reason.

### Orchestrator anti-goals

The orchestrator must not:

- spawn agents merely because capacity is available;
- request frequent status narration;
- allow agents to redefine the project objective silently;
- accept summaries without checking required evidence;
- let agents modify authoritative records outside their permissions;
- confuse a majority opinion with a validated conclusion;
- continue research after the stopping criteria are met.

---

## 3.3 Specialist agents

A specialist agent should have a narrow, explicit contract.

Every assignment should specify:

```yaml
agent_role: Security reviewer
objective: Identify exploitable authentication weaknesses in the proposed design
inputs:
  - CHARTER.md
  - ARTIFACTS/auth-design.md
scope:
  include:
    - session handling
    - credential storage
    - privilege escalation paths
  exclude:
    - visual design
required_output:
  format: discovery_record
  fields:
    - finding
    - evidence
    - severity
    - affected_requirement
    - recommended_action
    - confidence
permissions:
  read: [project files]
  write: [DISCOVERIES/security-review.md]
  prohibited: [production changes, requirement deletion]
stopping_condition: All in-scope components reviewed or a blocking limitation documented
```

A role name alone is not a contract. “Researcher,” “critic,” or “developer” is too vague unless the expected behavior, boundaries, and output are defined.

---

# 4. Coordination Should Be Asynchronous by Default

Routine work should not require a multi-agent conversation.

An agent should normally:

1. read the current project state;
2. claim or receive a bounded task;
3. perform the work;
4. validate the result;
5. update the permitted state or submit a structured result;
6. identify any trigger requiring review;
7. stop.

This is the AI equivalent of effective asynchronous work. It avoids repeated context transfer, conversational drift, and token-heavy status exchanges.

## 4.1 Routine status update schema

```yaml
update_type: task_status
task_id: T-014
agent: implementation-agent
previous_status: in_progress
current_status: complete
artifact: ARTIFACTS/parser.py
acceptance_checks:
  - name: unit_tests
    result: pass
    evidence: EVALUATIONS/parser-tests.txt
  - name: malformed_input_test
    result: pass
    evidence: EVALUATIONS/parser-tests.txt
new_risks: []
new_discoveries: []
blocked: false
recommended_next_action: Begin T-015
```

No discussion is needed unless the update contains a trigger.

---

# 5. When an Agent “Meeting” Is Justified

MAP should convene a temporary deliberation only when one or more predefined triggers occur.

## 5.1 Recommended triggers

### A. Contradictory evidence

Two credible findings support incompatible conclusions.

### B. Material discovery

New information changes a central assumption, requirement, dependency, risk, or expected outcome.

### C. Major proposed change

A proposed action would materially affect scope, cost, architecture, safety, schedule, permissions, or user expectations.

### D. Decision under meaningful uncertainty

Several plausible paths exist, the consequences differ materially, and no deterministic rule resolves the choice.

### E. Failed evaluation

A critical test fails, repeated attempts do not resolve it, or an apparent improvement creates a regression elsewhere.

### F. Blocked dependency

Progress requires information, permission, or an artifact that is unavailable or disputed.

### G. Goal ambiguity

Agents are optimizing incompatible interpretations of success.

### H. High-consequence action

The action is difficult to reverse, externally visible, expensive, destructive, legally sensitive, security-sensitive, or safety-sensitive.

### I. Handoff failure

The receiving agent cannot continue because the prior state or rationale is incomplete.

### J. Scheduled strategic checkpoint

A limited periodic review may be justified for long-running projects when important drift could occur without producing an obvious event. This should be infrequent and focused on project-level health, not routine status recitation.

---

## 5.2 Conditions that do not justify a meeting

Do not convene deliberation merely because:

- a task was completed normally;
- an agent has an idea with no material effect;
- the system reached an arbitrary time interval;
- multiple agents are available;
- the orchestrator wants reassurance;
- information already exists in the state record;
- the question can be resolved by a test, lookup, or deterministic rule;
- one qualified owner can decide within established policy.

---

# 6. The Deliberation Protocol

When deliberation is justified, it should be bounded, structured, and decision-oriented. It should not be an unmoderated group chat.

## 6.1 Phase 1: Frame the decision

The orchestrator or requesting agent must create a decision brief:

```yaml
decision_id: D-027
question: Should the project replace local storage with a database?
reason_for_review: Current storage method fails the concurrency requirement
objective_affected: Reliable multi-user operation
constraints:
  - must run on existing hardware
  - migration must preserve current data
  - implementation budget is limited
known_facts:
  - concurrent writes can overwrite records
  - current data volume is small
uncertainties:
  - expected growth over 12 months
  - acceptable migration downtime
options_requested: 2-4
owner: architecture-agent
decision_deadline: before task T-021 begins
```

A poorly framed question produces poorly bounded debate.

---

## 6.2 Phase 2: Independent proposals

Agents should generate their initial proposals independently when independence matters. Showing every agent the first proposal can cause anchoring and false consensus.

Each proposal should contain:

```yaml
option_id: O-1
summary: Adopt SQLite with write serialization
assumptions:
  - deployment remains single-host
expected_benefits:
  - transactional writes
  - minimal operational overhead
costs:
  - migration work
risks:
  - later scaling may require another migration
evidence:
  - test result or source reference
reversibility: medium
verification:
  - concurrency test suite
confidence: 0.78
```

The purpose of multiple agents is not to create more prose. It is to generate meaningfully independent alternatives, evidence, or critiques.

---

## 6.3 Phase 3: Adversarial review

A reviewer should test the proposals rather than merely summarize them.

The review should ask:

- Which assumptions are unsupported?
- What failure modes are missing?
- What evidence contradicts the proposal?
- What requirements does it fail to satisfy?
- What second-order effects could occur?
- Is a simpler option available?
- Can the decision be delayed until uncertainty is reduced?
- Is a reversible experiment preferable to a permanent choice?

Critique should target the proposal, not the agent.

---

## 6.4 Phase 4: Decision

The named decision owner selects one of the following:

- approve an option;
- approve with modifications;
- request a targeted experiment;
- defer pending specific information;
- reject all options and reframe the problem;
- escalate to a human.

The decision must include its rationale and the evidence that mattered most.

A vote should not be the default. Agents may share correlated errors, similar training biases, or the same incomplete context. Three agents repeating the same unsupported claim do not create three independent pieces of evidence.

---

## 6.5 Phase 5: Commit and propagate

After a decision:

1. record it;
2. update affected tasks and requirements;
3. identify superseded instructions;
4. notify only affected agents;
5. execute the decision;
6. define how the result will be evaluated.

Discussion that does not alter state, assign action, reduce uncertainty, or document a justified decision has not completed its purpose.

---

# 7. Decision Records

Significant decisions should be stored in a durable format similar to an architecture decision record.

```markdown
# D-027: Replace flat-file storage with SQLite

## Status
Accepted

## Context
Concurrent writes can overwrite records, violating requirement R-012.

## Decision
Use SQLite with serialized writes for the current single-host deployment.

## Evidence
- Concurrency test C-04 reproduces data loss in the flat-file implementation.
- SQLite passes the same test under the expected workload.

## Alternatives Considered
- Continue using flat files with file locking.
- Deploy a client-server database.

## Rationale
SQLite satisfies the current concurrency requirement with less operational cost than a server database. File locking reduced but did not eliminate failure cases.

## Consequences
- A migration task is required.
- The design must be reconsidered if deployment becomes multi-host.

## Owner
Architecture agent

## Review Trigger
Reassess if expected concurrent users exceed 50 or multi-host deployment is proposed.
```

A decision record is not just a historical note. It prevents later agents from unknowingly reopening settled questions or repeating discarded approaches without new evidence.

---

# 8. Discoveries and Change Control

A discovery is not automatically a change. It is new information that may justify one.

## 8.1 Discovery record

```yaml
discovery_id: F-019
agent: research-agent
finding: The selected API does not permit commercial redistribution
source_or_evidence: source reference and quoted clause location
confidence: high
assumptions_affected:
  - A-004: selected API can be included in the distributed application
requirements_affected:
  - R-008
recommended_action: Evaluate replacement APIs
urgency: blocking
```

## 8.2 Change classifications

### Level 0: Routine implementation choice

Characteristics:

- within approved scope;
- low-risk and reversible;
- no requirement or external behavior changes;
- owned by the implementing agent.

**Approval:** Agent may proceed and log the choice if useful.

### Level 1: Local project adjustment

Characteristics:

- affects a small number of tasks;
- limited cost or schedule impact;
- does not alter core goals or safety boundaries;
- reasonably reversible.

**Approval:** Task owner or orchestrator.

### Level 2: Material project change

Characteristics:

- changes architecture, scope, requirements, major dependencies, or delivery plan;
- affects multiple agents or workstreams;
- meaningful cost, quality, or schedule impact.

**Approval:** Named project decision owner after structured review.

### Level 3: Human-governed change

Characteristics:

- changes the user’s objective;
- creates legal, financial, privacy, security, safety, or reputational consequences;
- performs an irreversible or externally consequential action;
- exceeds delegated authority;
- involves value judgments not established by policy.

**Approval:** Human authorization required.

---

# 9. Handoffs Across Agents and Context Windows

A handoff is successful only when the receiving agent can continue without reconstructing the entire project history.

## 9.1 Minimum handoff packet

```yaml
handoff_id: H-033
from: implementation-agent
to: testing-agent
project_goal: One-sentence current objective
current_state: Parser implemented; integration not yet verified
completed:
  - T-014 parser implementation
artifacts:
  - ARTIFACTS/parser.py
  - EVALUATIONS/parser-unit-tests.txt
important_decisions:
  - D-019 strict parsing mode
unresolved:
  - Unicode normalization behavior
known_risks:
  - large inputs have not been performance-tested
next_task:
  id: T-015
  objective: Run integration and performance tests
acceptance_criteria:
  - all integration cases pass
  - 50 MB input processes within defined limit
warnings:
  - do not modify REQUIREMENTS.json except pass/fail fields
```

## 9.2 Handoff principles

- State what changed, not everything that happened.
- Link to evidence instead of repeating it.
- Separate facts from interpretations.
- Identify unresolved questions explicitly.
- Include the next concrete action.
- Preserve decision rationale when it affects future choices.
- Do not rely on hidden reasoning or private context.

---

# 10. Evaluation Is the Primary Form of Accountability

Human projects often rely on verbal assurances. MAP should rely on observable evaluation.

## 10.1 Evaluation layers

### Deterministic checks

Use when correctness can be directly tested:

- unit tests;
- schema validation;
- static analysis;
- file existence and integrity;
- numerical comparison;
- permission checks;
- reproducible commands.

### Model-based review

Use when judgment is required:

- clarity;
- factual support;
- requirement coverage;
- design coherence;
- usability;
- risk analysis.

Model-based review should use explicit rubrics and, where consequences matter, independent review or human inspection.

### Real-world or user evaluation

Use when success depends on human experience or external outcomes:

- user acceptance;
- task completion rate;
- production behavior;
- stakeholder approval;
- observed reliability over time.

## 10.2 Requirement state should be difficult to manipulate

Agents should not be allowed to achieve apparent success by deleting tests, weakening requirements, changing acceptance criteria, or redefining the objective after failure.

Changes to requirements must follow the change-control process. Test modifications should be separately reviewed when the test protects a material requirement.

---

# 11. Memory and Knowledge Management

Agent systems can drift when temporary conclusions become permanent instructions.

MAP should distinguish four kinds of memory:

## 11.1 Charter memory

Stable project purpose, constraints, and governance. Changes rarely and only through explicit approval.

## 11.2 Operational state

Current tasks, progress, blockers, and recent changes. Changes frequently and should be concise.

## 11.3 Decision memory

Accepted decisions and their rationale. Changes through superseding records, not silent rewriting.

## 11.4 Learned memory

Validated lessons that may improve future behavior. This should be written only when supported by repeated evidence, evaluation, or clear causal analysis.

### Memory rule

Do not store:

- speculation as fact;
- a one-time failure as a universal rule;
- an agent’s self-assessment without evidence;
- outdated instructions without marking them superseded;
- verbose transcripts when a concise artifact captures the relevant state.

---

# 12. Communication Design

Agent communication should optimize for precision, relevance, and machine readability—not for sounding natural.

## 12.1 Required distinctions

Every substantive message should distinguish among:

- **Fact:** Directly supported or observed.
- **Inference:** Reasoned conclusion from stated evidence.
- **Proposal:** Suggested action not yet approved.
- **Decision:** Authorized direction.
- **Unknown:** Information not currently established.
- **Risk:** Possible future harm or failure.

## 12.2 Message economy

Agents should not:

- greet one another;
- thank one another;
- repeat the assignment before answering unless needed for disambiguation;
- narrate routine internal steps;
- restate project history already available in canonical state;
- produce a long summary when structured fields are sufficient;
- send progress updates that do not change state.

Conciseness should not remove necessary evidence, assumptions, limitations, or next actions.

## 12.3 Structured first, prose second

Use structured fields for routing, state, evidence, and decisions. Use prose where explanation, interpretation, or synthesis is genuinely needed.

---

# 13. Conflict Resolution

Agent disagreement is useful only if the system can identify what the disagreement is about.

## 13.1 Classify the conflict

A conflict may concern:

- different facts;
- different interpretations of the same facts;
- different objectives;
- different risk tolerances;
- different constraints;
- different estimates;
- different value judgments;
- incompatible permissions or policies.

The resolution mechanism depends on the class.

| Conflict type | Preferred resolution |
|---|---|
| Factual | Retrieve evidence or run a test |
| Interpretive | Compare reasoning against requirements and evidence |
| Objective | Refer to charter or human owner |
| Risk tolerance | Apply policy or escalate |
| Estimate | Run a bounded experiment or use ranges |
| Value judgment | Human decision unless clearly delegated |
| Policy or permission | Follow higher-authority rule |

## 13.2 Do not resolve disagreement through rhetoric

An agent should not win because it writes more confidently, speaks last, produces more text, or is nominally senior. The system should prefer:

1. verified evidence;
2. explicit requirements;
3. reproducible tests;
4. relevant expertise or tool access;
5. documented authority;
6. clearly labeled uncertainty.

---

# 14. Human Oversight

Humans should not be inserted into every routine step. Human attention is limited and should be reserved for decisions where human authority, values, or accountability are genuinely required.

## 14.1 Escalate when

- the goal is ambiguous or contested;
- the requested action exceeds agent authority;
- consequences are irreversible or externally significant;
- safety, legality, privacy, security, or finances are materially affected;
- no option satisfies the established constraints;
- evidence remains materially uncertain after reasonable investigation;
- a value judgment has not been delegated;
- the user must accept a tradeoff;
- the system detects possible objective drift.

## 14.2 Do not escalate merely when

- an agent encounters normal difficulty;
- another tool call or test can resolve the question;
- the agent wants reassurance;
- a reversible low-risk choice is within delegated authority;
- a minor implementation detail lacks an explicit preference.

## 14.3 Escalation packet

A human should receive a compact decision-ready brief:

```yaml
question: Choose storage architecture for production release
why_human_is_needed: The options create different recurring costs and data-control obligations
current_objective: Reliable deployment for up to 500 users
options:
  - option: managed database
    benefit: lower operations burden
    cost: recurring fee and external hosting
  - option: self-hosted database
    benefit: direct data control
    cost: maintenance and reliability responsibility
recommended_option: managed database
basis: lower operational risk under current staffing
uncertainties:
  - future data residency requirements
required_decision: Select option A or B
```

Do not ask a human to read the entire agent conversation to discover what decision is needed.

---

# 15. Cost and Token Discipline

Multi-agent systems can improve breadth and independent exploration, but they can also multiply token use, latency, and coordination errors.

MAP should treat additional agents and deliberation as investments that require justification.

## 15.1 Before spawning another agent, ask

- Can a deterministic tool perform this task?
- Can the current agent perform it within its context and capabilities?
- Is the task actually parallelizable?
- Does the specialist have different tools, instructions, permissions, or expertise?
- Is independent verification valuable enough to justify the cost?
- Can the expected output be clearly bounded?
- Will the result reduce uncertainty or improve a decision?

## 15.2 Stop conditions

Every research or deliberation task should have stopping criteria, such as:

- required questions answered;
- sufficient evidence collected;
- confidence threshold reached with supporting evidence;
- all options evaluated against the rubric;
- test passes;
- budget or attempt limit reached;
- remaining uncertainty no longer changes the decision;
- human escalation required.

Without stopping rules, agents may continue searching, discussing, or refining after the result is already adequate.

---

# 16. Common Failure Modes

## 16.1 Meeting theater

**Symptom:** Agents simulate executives, departments, or committees without adding independent evidence or capability.

**Correction:** Replace roleplay with bounded tasks and output contracts.

---

## 16.2 Status narration

**Symptom:** Agents repeatedly describe what they are doing without changing project state.

**Correction:** Report only state changes, exceptions, evidence, and required decisions.

---

## 16.3 Consensus laundering

**Symptom:** Several agents agree because they share context, model biases, or copied reasoning, and the agreement is treated as proof.

**Correction:** Require independent proposals, evidence, or tests. Do not equate vote count with truth.

---

## 16.4 Orchestrator bottleneck

**Symptom:** Every detail must pass through a lead agent, consuming context and slowing progress.

**Correction:** Delegate bounded authority and allow direct state updates within permissions.

---

## 16.5 Silent objective drift

**Symptom:** Agents optimize an easier substitute for the actual goal.

**Correction:** Re-read the charter at checkpoints and tie tasks and evaluations to explicit success criteria.

---

## 16.6 Plan worship

**Symptom:** Agents continue an approved approach despite contradictory evidence.

**Correction:** Define discovery and failure events that automatically trigger reassessment.

---

## 16.7 Novelty churn

**Symptom:** Every new idea causes reprioritization.

**Correction:** Require materiality, evidence, cost analysis, and an approval threshold for changes.

---

## 16.8 Documentation as a substitute for work

**Symptom:** The project accumulates plans and reports while requirements remain unfulfilled.

**Correction:** Make accepted artifacts and evaluation results the measure of progress.

---

## 16.9 Unbounded critique

**Symptom:** Reviewer agents continually identify hypothetical problems without prioritization or stopping.

**Correction:** Require severity, evidence, affected requirement, and recommended action; stop when the review scope is exhausted.

---

## 16.10 Memory contamination

**Symptom:** Temporary guesses or failed approaches become permanent instructions.

**Correction:** Separate working notes from validated decision and learned memory.

---

## 16.11 Duplicate work

**Symptom:** Agents investigate the same question because task boundaries are unclear.

**Correction:** Use task claims, explicit scopes, and orchestrator checks before delegation.

---

## 16.12 Premature completion

**Symptom:** An agent declares success after producing an artifact without running acceptance checks.

**Correction:** Completion requires evidence that stated acceptance criteria pass.

---

# 17. MAP Coordination Lifecycle

## Phase 1: Initialization

Create or confirm:

- objective;
- user need;
- success criteria;
- scope and exclusions;
- requirements;
- constraints;
- assumptions;
- risks;
- decision authority;
- agent roles;
- evaluation method;
- stopping conditions.

**Output:** Project charter and initial task graph.

---

## Phase 2: Decomposition

Determine:

- which work must be sequential;
- which work can be parallel;
- which tasks require specialists;
- which tasks can be deterministic;
- what context each agent actually needs;
- where independent review is valuable.

**Output:** Bounded tasks with owners, dependencies, and acceptance criteria.

---

## Phase 3: Execution

Agents work asynchronously, update state, validate outputs, and record discoveries.

**Output:** Verified artifacts and state changes.

---

## Phase 4: Exception and review

Defined triggers initiate targeted deliberation, replanning, or escalation.

**Output:** Decision, experiment, revised plan, or human question.

---

## Phase 5: Integration

A designated owner combines accepted outputs and checks system-level consistency.

**Output:** Integrated deliverable with traceable component sources.

---

## Phase 6: Acceptance

Evaluate against the original success criteria, not merely the final plan.

**Output:** Accepted result, documented limitations, or remaining failures.

---

## Phase 7: Retrospective and memory update

Compare:

- expected versus actual results;
- successful versus failed assumptions;
- estimated versus actual cost;
- planned versus actual coordination needs;
- useful versus wasteful agent roles;
- discovered failure modes;
- evaluation gaps.

Only validated lessons should become durable guidance.

**Output:** Retrospective, new tests, and carefully updated operating memory.

---

# 18. Metrics for Coordination Quality

MAP should measure whether coordination improves outcomes rather than merely counting messages or agents.

Possible measures include:

## Outcome measures

- percentage of requirements passing;
- user acceptance rate;
- factual or functional error rate;
- regression rate;
- unresolved critical risks;
- deliverable quality against rubric.

## Coordination measures

- duplicated task rate;
- number of handoffs requiring reconstruction;
- percentage of decisions with evidence and owner;
- time or tokens spent in deliberation;
- percentage of deliberations that changed the decision or reduced uncertainty;
- number of stale or contradictory state records;
- frequency of unauthorized scope change;
- escalation precision: necessary versus avoidable human interruptions.

## Efficiency measures

- cost per accepted requirement;
- tokens per verified deliverable;
- proportion of agent outputs reused in the final product;
- research performed after stopping criteria were already met;
- agent count relative to independent task count.

A coordination mechanism should be removed or simplified when it consumes resources without improving quality, safety, speed, or traceability.

---

# 19. Normative Operating Rules

The following terms are used deliberately:

- **MUST:** Required for reliable operation.
- **SHOULD:** Default unless a documented reason justifies an exception.
- **MAY:** Optional when useful.

## 19.1 Project state

1. Every project **MUST** have an authoritative objective and success criteria.
2. Material state **MUST** exist outside transient conversation history.
3. Each active task **MUST** have one owner and acceptance criteria.
4. Agents **MUST NOT** silently change requirements, scope, or authority.
5. Superseded decisions **MUST** remain traceable.

## 19.2 Delegation

6. An agent assignment **MUST** define objective, scope, inputs, output format, and stopping condition.
7. Agents **SHOULD** receive only the context needed for their task.
8. Additional agents **SHOULD** be used only when they add distinct capability, independence, or parallelism.
9. The orchestrator **MUST** prevent or detect duplicate assignments.

## 19.3 Evidence and evaluation

10. Material findings **MUST** distinguish fact, inference, and proposal.
11. Completion **MUST** be supported by acceptance evidence.
12. Tests and requirements **MUST NOT** be weakened solely to make an output pass.
13. High-consequence decisions **SHOULD** receive independent review.

## 19.4 Deliberation

14. Deliberation **MUST** begin with a framed question and named decision owner.
15. Initial proposals **SHOULD** be independent when correlation is a material risk.
16. Deliberation **MUST** have a stopping condition.
17. The final decision **MUST** update authoritative state and affected tasks.
18. A majority vote **MUST NOT** substitute for evidence or authority.

## 19.5 Change and escalation

19. Proposed changes **MUST** identify affected goals, requirements, cost, risk, and verification method when material.
20. Irreversible or high-consequence actions **MUST** use an appropriate approval gate.
21. Human escalation **MUST** present a concise decision-ready brief.
22. Agents **SHOULD NOT** escalate routine reversible choices within delegated authority.

## 19.6 Memory

23. Durable learned memory **MUST** be based on validated evidence.
24. Temporary hypotheses **MUST NOT** be stored as settled facts.
25. Handoffs **MUST** include current state, relevant artifacts, unresolved issues, and next action.

---

# 20. Minimal Implementation for MAP

A first implementation does not need a large framework. The following is sufficient to begin:

## Required artifacts

1. `CHARTER.md`
2. `TASKS.json`
3. `STATE.json`
4. `DECISIONS/`
5. `DISCOVERIES/`
6. `EVALUATIONS/`
7. `HANDOFF.md`

## Required behaviors

1. Agents read the charter and current state before acting.
2. Each agent works on one claimed task at a time unless explicitly assigned parallel tasks.
3. Completion requires acceptance evidence.
4. Discoveries use a standard record.
5. Material changes trigger a decision record.
6. Human approval gates protect high-consequence actions.
7. Every session leaves a handoff for the next session.
8. The orchestrator stops spawning work when the project’s success or stopping conditions are met.

## Recommended sequence for adoption

### Stage 1: State discipline

Introduce charter, task ownership, acceptance criteria, and handoffs.

### Stage 2: Evidence discipline

Add structured discoveries, test evidence, and decision records.

### Stage 3: Event-driven review

Define triggers for conflict, failure, material discovery, and major change.

### Stage 4: Multi-agent specialization

Add specialist agents only where repeated evidence shows a single-agent bottleneck.

### Stage 5: Evaluation and optimization

Measure coordination cost, duplicate work, handoff failures, and outcome quality. Remove unnecessary roles and protocols.

---

# 21. Compact Coordination Protocol

This section can be provided directly to MAP agents as an operating covenant.

```markdown
## MAP Coordination Covenant

1. Treat the project charter as the authoritative statement of purpose.
2. Read current state before beginning work.
3. Work only within your assigned objective, scope, and permissions.
4. Distinguish facts, inferences, proposals, decisions, unknowns, and risks.
5. Support material claims with evidence or state that verification is unavailable.
6. Update shared state instead of relying on conversation history.
7. Do not request a meeting for routine progress. Record the state change.
8. Trigger review when evidence conflicts, a critical test fails, a material discovery changes assumptions, a major change is proposed, or authority is insufficient.
9. In a review, frame one decision, produce bounded options, test assumptions, and stop when the named owner can decide.
10. Critique the work, not the agent.
11. Do not treat agreement among agents as proof.
12. Do not change goals, requirements, tests, or scope merely to make the current approach succeed.
13. Prefer reversible experiments when uncertainty can be reduced cheaply.
14. Every accepted decision must identify its owner, rationale, consequences, and review trigger.
15. Completion requires evidence that acceptance criteria pass.
16. Leave a concise handoff containing current state, artifacts, unresolved issues, and next action.
17. Preserve validated lessons; do not turn speculation into durable memory.
18. Use the simplest workflow and fewest agents that can reliably complete the task.
```

---

# 22. Final Design Principle

The goal is not to eliminate communication. It is to eliminate communication that does not improve shared understanding, decisions, execution, or accountability.

Human meetings often combine information exchange, social reassurance, authority, negotiation, and decision-making in one event. MAP should separate those functions and implement each with the most reliable mechanism available:

- **state for shared reality;**
- **tests for accountability;**
- **records for memory;**
- **permissions for authority;**
- **events for attention;**
- **deliberation for genuine uncertainty;**
- **humans for values and consequential approval.**

> **Agents should not meet because that is how humans work. They should coordinate because no complex project succeeds without a reliable way to share reality, resolve uncertainty, and convert learning into action.**

---

# References and Intellectual Foundations

This document is an original synthesis informed by the following sources and traditions:

1. **OpenAI, “Orchestration and handoffs.”** Describes handoffs, manager-style agents-as-tools, clear specialist boundaries, and the principle of adding specialists only when they materially improve the workflow.  
   https://developers.openai.com/api/docs/guides/agents/orchestration

2. **Anthropic, “Building effective agents” (2024).** Recommends simple, composable patterns and using agentic complexity only when its performance benefits justify added latency and cost.  
   https://www.anthropic.com/engineering/building-effective-agents

3. **Anthropic, “How we built our multi-agent research system” (2025).** Discusses orchestrator-worker architecture, parallel specialist research, explicit delegation, coordination complexity, token cost, and the limits of multi-agent systems for tightly dependent work.  
   https://www.anthropic.com/engineering/multi-agent-research-system

4. **Anthropic, “Effective harnesses for long-running agents” (2025).** Describes initializer agents, incremental progress, persistent feature requirements, testing, and clear artifacts that allow later sessions to continue reliably.  
   https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

5. **Anthropic, “Demystifying evals for AI agents” (2026).** Emphasizes explicit success criteria, realistic evaluations, regression detection, and converting observed failures into durable tests.  
   https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

6. **Manifesto for Agile Software Development and its principles.** Contributes the ideas of responding to change, frequent evaluation of working outcomes, simplicity, and regular adjustment based on experience.  
   https://agilemanifesto.org/  
   https://agilemanifesto.org/principles.html

7. **Blackboard systems and shared-workspace architectures.** A longstanding AI and software design tradition in which independent components contribute to a common representation of the problem rather than depending on continuous direct conversation.

8. **Architecture Decision Records.** A software-engineering practice for preserving the context, alternatives, rationale, and consequences of significant decisions.

9. **After-action review practices.** A family of retrospective methods centered on comparing intended outcomes with actual events, explaining the difference, and changing future behavior.

---

## Document Status

This is a design philosophy, not a claim that one coordination architecture is optimal for every project. MAP should treat these principles as defaults, measure their results, and revise their implementation when evidence supports a better approach.
