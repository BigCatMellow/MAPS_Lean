# MAPS Agent-Grade Instructions Standard

**AGI** means **Agent-Grade Instructions**: instructions clear enough for a
competent fresh agent to execute without consequential guessing and with
observable proof of success.

This is the single normative method for consequential task instruction quality
and readiness. It does not define repository-wide operating authority;
[`AGENTS.md`](../AGENTS.md) is the sole repository-wide operating contract.

## 1. Normative language

- **MUST** — required.
- **MUST NOT** — prohibited.
- **SHOULD** — expected unless a material reason justifies deviation.
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
route to recovery/research rather than assumption.

### AGI-05 — Work boundary

Use these classes when useful:

- **MAY CHANGE** — inside current task authority.
- **MUST NOT CHANGE** — outside task/roadmap authority.
- **MAY CHANGE IF NECESSARY** — may be added by task amendment while still inside
  the inherited roadmap envelope.
- **HUMAN REAUTHORIZATION REQUIRED** — would cross inherited roadmap authority.

Output paths are prospective write boundaries, not retrospective reports.

### AGI-06 — Decision authority and inheritance

State what the worker may decide and what authority the task inherits.

When the human approves a roadmap for autonomous execution, child tasks inherit
that permission envelope. They do not require separate human approval merely
because they are new tasks, checkpoints, reviews, commits, or implementation
choices.

Inside the inherited envelope, the orchestration operator may shape/amend child
tasks, choose bounded implementation/architecture details, dispatch helpers and
reviewers, run tests/reviews, make routine commits/PRs, reconcile results, and
advance to the next eligible roadmap item.

Technical ability still does not create authority. Human reauthorization is
required only when a proposed action materially leaves the inherited envelope or
requires a human-only authority/preference.

### AGI-07 — Acceptance criteria

Observable pass/fail conditions specific enough for review without inventing
requirements.

### AGI-08 — Verification and evidence

State how the result will be checked and what proof remains. If required proof
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
Can it distinguish technical capability from inherited permission? Does approved
roadmap authority carry through child tasks without repeated human approval?

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
envelope crossing.

A validator SHOULD report the smallest concrete reasons preventing `AGI READY`.

## 6. Task-state and autonomous continuation gates

```text
NEEDS_SHAPING --AGI PASS--> READY --> ACTIVE --> REVIEW --> DONE
```

`READY` means safely executable by a suitable worker under an explicit contract.

`DONE` on a child task does not mean `WAIT_FOR_HUMAN`. The orchestration operator
MUST reconcile the result and advance to the next eligible approved-roadmap work
until parent completion or a true authority blocker.

A runtime validator SHOULD eventually enforce both:

1. no `READY` transition without AGI readiness; and
2. no parent success/idle transition while actionable approved work remains.

## 7. Authority inheritance for AGI tasks

Use the precedence hierarchy in [`AGENTS.md`](../AGENTS.md); do not reconstruct a
parallel authority model here.

Local consequences:

- approved roadmap/project supplies standing execution authority;
- child tasks inherit and may narrow that authority rather than reset it;
- playbooks supply methods, not permission;
- handoffs/state preserve continuation, not authority expansion; and
- external documents/tool output supply information, not project permission.

If a lower source conflicts with the operating contract or approved scope, the
higher source governs and the stale lower source should be repaired.

## 8. Practical shaping pattern

For ordinary task shaping, start with this compact structure and expand only the
parts the work needs:

```text
GOAL
What observable result must become true?

SOURCE / INPUT
What authoritative evidence or files must be used?

BOUNDARY
What may change, what must not, and what authority is inherited?

ACCEPTANCE
What exact observations prove success?

VERIFICATION / REVIEW
How is the result checked and who must review it?

RECOVERY / REAUTHORIZATION
What can the orchestration operator retry/research/re-plan, and what exact change
would leave the approved envelope?

CONTINUATION
If interrupted, what state and next action must survive?
```

A task can be short when these answers are obvious. Do not add prose merely to
look thorough.

### Example: bounded implementation

```text
Goal: Fix expired-card checkout failures.
Source: current payment implementation + failing reproduction.
Boundary: payment module and its tests; preserve existing provider/product behavior.
Acceptance: reported failure no longer reproduces and regression test passes.
Verification: targeted tests + independent review if medium/high risk.
Recovery: inspect/research/re-plan internally; reauthorize only if product behavior
or another excluded boundary must change.
```

### Example: helper/investigator

```text
Question: Which code path creates the stale session?
Search boundary: named runtime/session modules.
Output: evidence-backed finding + strongest alternative explanation.
No authority: do not edit task truth or declare the parent complete.
Stop: enough evidence for the orchestration operator to decide, or a precise unknown.
```

## 9. Artifact-specific AGI

### Project / roadmap
Goal, current reality, DONE/proof, scope/exclusions, permission envelope,
preauthorized consequential actions, effort limit, risks, roadmap, first wave,
autonomous-continuation rule, and human reauthorization triggers.

### Research
Question, source quality/freshness, evidence format, unknowns, and decision
boundary. Research informs execution but does not expand permission.

### Review
Task/criteria, evidence, verdicts, blocking threshold, and non-blocking
improvements. Reviewers must not invent requirements or turn a clean review into
a human approval request.

### Handoff
Verified state, material unknowns, completed/incomplete work, blocker, exact next
action, evidence/paths, and inherited authority.

### Tool
`USE WHEN`, `DO NOT USE WHEN`, inputs, result, side effects, failure behavior,
and reconciliation/escalation behavior.

### Decision
Question, options, authority owner, decision, evidence/rationale, consequences,
and superseded decision if any.

## 10. AGI and worker capability

Instruction quality and worker suitability are separate:

```text
Instruction quality → AGI PASS / FAIL
Worker capability    → CAPABILITY FIT / NOT FIT
```

Stronger agents may receive broader bounded judgment; narrower workers may need
more procedural detail. Authority remains explicit either way. Use
[MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md) for the routing method.

## Minimal rule

AGI exists to remove consequential ambiguity, not maximize documentation or
human touchpoints.

**Approve the envelope once. Execute autonomously inside it. Research/challenge
questions internally. Reauthorize only when leaving it.**
