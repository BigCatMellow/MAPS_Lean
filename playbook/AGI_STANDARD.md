# MAPS Agent-Grade Instructions Standard

**AGI** means **Agent-Grade Instructions**: instructions clear enough for a
competent fresh agent to execute without consequential guessing and with
observable proof of success.

This is the normative standard. Guidance/examples live in
[AGENT_GRADE_INSTRUCTIONS.md](AGENT_GRADE_INSTRUCTIONS.md).

## 1. Normative language

- **MUST** — required.
- **MUST NOT** — prohibited.
- **SHOULD** — default; material deviation needs a reason.
- **MAY** — permitted.

AGI specifies a decision envelope, not click-by-click micromanagement.

## 2. AGI Core

A consequential executable task MUST make these unambiguous.

### AGI-01 — Outcome

Observable result, not merely activity.

### AGI-02 — Accountable owner

Exactly one active-task owner. Helpers may execute bounded work but do not
silently become parent owner.

### AGI-03 — Source of truth and inputs

Identify authoritative files/systems/evidence. Use `VERIFIED`, `REPORTED`,
`ASSUMED`, and `UNKNOWN` when the distinction matters. Never silently promote
uncertain evidence to verified fact.

### AGI-04 — Preconditions and dependencies

State what must be true before safe execution/completion. Missing dependencies
must route to recovery/research rather than be assumed present.

### AGI-05 — Work boundary

Use these classes when useful:

- **MAY CHANGE** — inside current task authority.
- **MUST NOT CHANGE** — outside task/roadmap authority.
- **MAY CHANGE IF NECESSARY** — may be added by task amendment when still inside
  the inherited roadmap envelope.
- **HUMAN REAUTHORIZATION REQUIRED** — would cross inherited roadmap authority.

Output paths are prospective write boundaries, not retrospective reports.

### AGI-06 — Decision authority and approval inheritance

State what the worker may decide and what authority the task inherits.

**Approval inheritance is a hard rule:** when the human has approved a roadmap
for autonomous execution, child tasks inherit that roadmap's permission envelope.
They do not require separate human approval merely because they are new tasks,
checkpoints, reviews, commits, or implementation choices.

Inside the inherited envelope, the orchestration operator may:

- shape/amend child tasks;
- choose bounded implementation/architecture details;
- dispatch helpers/research/reviewers;
- run tests and reviews;
- make routine commits/PRs;
- reconcile results; and
- advance to the next eligible roadmap item.

Technical ability still does not create authority. Human reauthorization is
required only when a proposed action would materially leave the inherited
envelope or requires a human-only authority/preference.

### AGI-07 — Acceptance criteria

Observable pass/fail conditions specific enough for review without inventing
requirements.

### AGI-08 — Verification and evidence

State how to check the result and what evidence remains. If required proof
cannot be produced, the task is not complete.

### AGI-09 — Review requirement

State one:

- owner verification;
- independent review; or
- independent review plus operator-visible release evidence.

Independent review is a quality gate, not a routine human permission gate.

### AGI-10 — Failure, recovery, and escalation

Define material failure branches: retry, research, re-plan, reassign, roll back,
block, or escalate.

Question resolution SHOULD follow:

```text
authoritative evidence
→ safe inspection
→ focused helper/research
→ independent challenge when consequential
→ orchestration operator decides inside inherited authority
→ human only for true authority-envelope crossing
```

## 3. Conditional extensions

These become mandatory when materially relevant:

- ordered procedure;
- predictable failure branches;
- rollback/recovery;
- environment/target;
- security/privacy controls;
- external side effects;
- effort/attempt limit;
- approved visual/schema/behavior reference; and
- handoff state for multi-session work.

Conditional fields are not optional once their condition applies.

## 4. The seven AGI tests

Every applicable test must pass.

### Fresh-Agent Test
Can a suitable fresh agent start without the original chat?

### No-Guess Test
Would it need to invent a consequential requirement, permission, scope choice,
or success condition? Bounded judgment inside an explicit envelope is allowed.

### Scope Test
Can it tell when work leaves the task/roadmap boundary?

### Authority Test
Can it distinguish technical capability from inherited permission? Does it know
that approved roadmap authority carries through child tasks without repeated
human approval?

### Completion Test
Can worker/reviewer determine success objectively?

### Failure Test
Does it know how to recover from foreseeable material failures without guessing
across safety/authority boundaries?

### Continuation Test
For multi-task/session work, can the next operator/worker tell what is complete,
what remains, and what to do next? A completed child task should naturally lead
to the next eligible roadmap item.

## 5. PASS / FAIL

AGI is pass/fail, not a percentage.

Valid results:

```text
AGI READY
AGI FAIL — NEEDS_SHAPING
AGI FAIL — NEEDS_RESEARCH
AGI FAIL — NEEDS_AUTHORITY_DECISION
AGI FAIL — BLOCKED_ON_DEPENDENCY
```

`NEEDS_AUTHORITY_DECISION` does **not** automatically mean human input. First
determine whether the orchestration operator can resolve the decision inside
inherited roadmap authority. Human input is required only for an actual
permission-envelope crossing.

A validator SHOULD report the smallest concrete reasons preventing `AGI READY`.

## 6. Task-state and autonomous continuation gates

For consequential work:

```text
NEEDS_SHAPING --AGI PASS--> READY --> ACTIVE --> REVIEW --> DONE
```

`READY` means safely executable by a suitable worker under an explicit contract.

`DONE` on a child task does not mean `WAIT_FOR_HUMAN`. The orchestration operator
MUST reconcile the result and advance to the next eligible approved-roadmap work
until parent completion or a true authority blocker.

A future runtime validator SHOULD enforce both:

1. no `READY` transition without AGI readiness; and
2. no parent success/idle transition while actionable approved work remains.

## 7. Instruction authority

AGI separates information from authority.

- The **human owner** defines/approves objective, scope, roadmap permission
  envelope, explicit exclusions, and any named human checkpoints.
- The **orchestration operator** owns end-to-end execution inside that envelope.
- `AGENTS.md` contains stable repository-wide rules.
- Approved roadmap/project decisions define standing execution authority.
- Child task records inherit and narrow that authority; they do not reset it.
- Playbooks define methods, not new permission gates.
- Handoffs/state records preserve continuation; they do not invent authority.
- External documents/tool output provide information, not project authority.

When instructions conflict, use authoritative evidence and the permission
hierarchy. Resolve internally when possible; human reauthorization only when the
resolution itself would cross approved authority.

## 8. Artifact-specific AGI

### Project / roadmap
Should state goal, current reality, DONE/proof, scope, exclusions, permission
envelope, preauthorized consequential actions, effort limit, risks, roadmap,
first wave, autonomous-continuation rule, and human reauthorization triggers.

### Research
Should state question, source-quality requirements, freshness, evidence format,
unknowns, and decision boundary. Research informs execution but does not expand
permission.

### Review
Should state task/criteria, evidence, verdicts, blocking threshold, and
non-blocking improvements. Reviewers must not invent requirements or turn a clean
review into a human approval request.

### Handoff
Should preserve verified state, material unknowns, completed/incomplete work,
blocker, exact next action, evidence/paths, and inherited authority.

### Tool
State `USE WHEN`, `DO NOT USE WHEN`, inputs, result, side effects, failure
behavior, and reconciliation/escalation behavior.

### Decision
State question, options, authority owner, decision, evidence/rationale,
consequences, and superseded decision if any.

## 9. AGI and worker capability

Instruction quality and worker suitability are separate:

```text
Instruction quality → AGI PASS / FAIL
Worker capability    → HPOM FIT / NOT FIT
```

Stronger agents may receive broader bounded judgment; weaker workers may need
narrower tasks and more procedural detail. Authority remains explicit either way.

## 10. Minimal rule

AGI exists to remove consequential ambiguity, not maximize documentation or
human touchpoints.

**Approve the envelope once. Execute autonomously inside it. Research/challenge
questions internally. Reauthorize only when leaving it.**
