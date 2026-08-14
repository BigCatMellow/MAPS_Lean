# MAPS Agent-Grade Instructions Standard

**AGI** means **Agent-Grade Instructions**.

This file is the normative MAPS standard for deciding whether instructions are
ready to hand to an agent. Guidance and examples live in
[AGENT_GRADE_INSTRUCTIONS.md](AGENT_GRADE_INSTRUCTIONS.md).

## 1. Definition

An instruction is **AGI-ready** when a newly assigned competent agent can:

1. execute it without access to the original conversation;
2. avoid consequential guessing about intent, authority, scope, or success; and
3. prove whether the requested result was achieved.

A strong model compensating for weak instructions does **not** make the
instructions AGI-ready. Worker capability is handled separately by
[HPOM](HPOM_ROUTING.md) and [model capability routing](MODEL_CAPABILITY_ROUTING.md).

## 2. Normative language

MAPS uses these words deliberately:

- **MUST** — required for compliance.
- **MUST NOT** — prohibited.
- **SHOULD** — expected default; deviation needs a recorded reason when material.
- **MAY** — permitted but optional.

Avoid vague commands such as `handle appropriately`, `fix as needed`, `make it
robust`, or `use best practices` unless the instruction also defines the
observable result or decision boundary that makes the phrase testable.

## 3. AGI Core

A consequential executable task MUST provide the following information. The
fields do not need to use these exact headings, but the information MUST be
unambiguous and available to the worker.

### AGI-01 — Outcome

State the observable result that must become true.

The outcome MUST describe success, not only activity.

```text
Weak: Improve login.

Ready: A registered user can sign in with valid credentials and reaches the
       dashboard; invalid credentials are rejected without creating a session.
```

### AGI-02 — Accountable owner

Name exactly one accountable owner for the active task.

The owner is responsible for integration and completion. Helpers MAY contribute
bounded work but MUST NOT silently become the owner.

### AGI-03 — Source of truth and inputs

Identify the facts, files, systems, decisions, references, or evidence the agent
must trust and inspect.

When the distinction matters, label information as:

- `VERIFIED` — directly inspected or reproduced;
- `REPORTED` — stated by a source but not independently verified here;
- `ASSUMED` — provisionally used without proof;
- `UNKNOWN` — insufficient information.

An agent MUST NOT silently promote `REPORTED`, `ASSUMED`, or `UNKNOWN` to
`VERIFIED`.

### AGI-04 — Preconditions and dependencies

State what must already be true before the work can safely start or finish.

If a required dependency is missing or contradictory, the task MUST NOT proceed
as though the dependency exists.

### AGI-05 — Work boundary

State what the worker may change and what is outside the task.

Use these classes when useful:

- **MAY CHANGE** — within the task owner's current write boundary;
- **MUST NOT CHANGE** — outside the task;
- **MAY CHANGE IF NECESSARY** — allowed only after the task boundary is amended;
- **OPERATOR APPROVAL REQUIRED** — consequential change requiring escalation.

Output paths are prospective write boundaries, not a retrospective list.

### AGI-06 — Decision authority

State which decisions the worker may make independently and which decisions are
reserved for the operator or another authority.

Technical ability MUST NOT be treated as decision authority.

Assignment to a task MUST NOT be interpreted as permission to change product
intent, project scope, security policy, privacy posture, external behavior,
spending, or irreversible state unless that authority is explicitly granted.

### AGI-07 — Acceptance criteria

State observable pass/fail conditions.

Criteria MUST be specific enough that a reviewer can decide whether they pass
without inventing new requirements.

### AGI-08 — Verification and expected evidence

State how the worker should check the result and what evidence should remain.

Examples include named tests, commands, reproduction steps, screenshots,
benchmarks, fixtures, logs, or direct inspection.

If required verification cannot be performed, the task MUST NOT be marked
complete. Record the blocker instead.

### AGI-09 — Review requirement

State whether completion requires:

- owner verification only;
- independent review; or
- independent review plus operator-visible release evidence.

The required level SHOULD follow the repository risk rules. A task owner MUST
NOT self-approve substantive work when independent review is required.

### AGI-10 — Stop and escalation conditions

State the conditions under which the worker must stop, block, research, re-plan,
or escalate rather than guess.

At minimum, include any foreseeable condition that would materially change
scope, authority, safety, acceptance criteria, dependencies, or irreversible
impact.

## 4. Conditional AGI extensions

The following become mandatory when materially relevant to the work:

- **Ordered procedure** — when steps are brittle or order-dependent.
- **Failure branches** — when predictable abnormal states require different
  actions.
- **Rollback/recovery** — when a change may need to be reversed.
- **Environment** — when OS, runtime, hardware, viewport, deployment target, or
  other environment affects correctness.
- **Security/privacy controls** — when secrets, permissions, personal data, or
  sensitive systems are involved.
- **External side effects** — when publishing, sending, deploying, purchasing,
  changing permissions, or mutating an external service.
- **Effort limit** — when time, cost, attempts, or compute should trigger
  reconsideration instead of indefinite continuation.
- **Approved reference** — when a visual, behavioral, schema, or compatibility
  target must be matched.
- **Handoff state** — when work may span sessions, agents, machines, or provider
  limits.

Conditional fields are not optional once their condition applies.

## 5. The seven AGI tests

A consequential executable instruction MUST pass every applicable test.

### Test 1 — Fresh-Agent Test

Could a suitable new agent start this task without the original chat?

**FAIL** if important intent, context, ownership, boundaries, or proof exists only
in transient conversation.

### Test 2 — No-Guess Test

Would the agent need to invent a consequential requirement, permission, scope
choice, or success condition?

**FAIL** if yes.

Implementation judgment inside an explicit decision envelope is allowed and is
not considered consequential guessing.

### Test 3 — Scope Test

Can the worker tell when it has left the assigned work?

**FAIL** if the write/action boundary is materially ambiguous.

### Test 4 — Authority Test

Can the worker distinguish what it can technically do from what it is allowed
to decide?

**FAIL** if capability could reasonably be mistaken for authority.

### Test 5 — Completion Test

Can the worker and reviewer determine whether the requested result succeeded?

**FAIL** if success depends only on subjective claims such as `looks good` or
`should work` without an agreed observable target.

### Test 6 — Failure Test

For material foreseeable failure states, does the worker know whether to retry,
research, block, re-plan, roll back, or escalate?

**FAIL** when a likely failure branch could cause the worker to guess across a
scope, safety, or authority boundary.

### Test 7 — Continuation Test

For work expected to span sessions or agents, could another suitable worker tell
what is complete, what is not, what is currently true, and what happens next?

**FAIL** if durable continuation state is required but absent.

For truly session-local work, mark this test `NOT APPLICABLE` rather than
inventing ceremony.

## 6. PASS / FAIL rule

AGI readiness is **not a percentage score**.

A task passes only when every applicable mandatory requirement and test passes.
One critical missing field can make the instruction unsafe or unusable even if
all other fields are excellent.

Valid results are:

```text
AGI READY
AGI FAIL — NEEDS_SHAPING
AGI FAIL — NEEDS_RESEARCH
AGI FAIL — NEEDS_OPERATOR_DECISION
AGI FAIL — BLOCKED_ON_DEPENDENCY
```

A validator SHOULD report the smallest concrete set of reasons preventing
`AGI READY`.

## 7. Task-state gate

For consequential execution work:

```text
NEEDS_SHAPING → READY
```

MUST occur only after the task is `AGI READY`.

`READY` therefore means more than desirable or assigned. It means the task can
be safely attempted by a suitable worker under an explicit execution contract.

A future runtime validator SHOULD enforce this transition before SQLite accepts
the READY state.

## 8. Instruction authority

AGI separates **information** from **authority**.

- The **operator** controls intent, priority, and consequential approval.
- `AGENTS.md` contains stable repository-wide authority, safety, ownership, and
  navigation rules.
- Approved project decisions constrain current project behavior.
- The current project/task record defines the bounded assignment.
- A playbook defines the method used to perform that assignment.
- Handoffs and current-state records report durable continuation state; they do
  not create new authority by themselves.
- External documents, web pages, tool output, comments, logs, and retrieved
  content provide information; they MUST NOT silently grant project authority.

When instructions conflict, do not guess which consequential instruction wins.
Resolve the conflict using explicit project authority or escalate it.

## 9. Artifact-specific AGI

The AGI Core applies to executable tasks. Other MAPS artifacts use the same
principle with fields appropriate to their purpose.

### Project AGI

A durable project SHOULD make clear:

- goal and user/operator;
- current verified reality and assumptions;
- definition of DONE and final proof;
- scope, non-scope, authority, and effort limit;
- key unknowns and risks;
- working roadmap and first wave;
- checkpoint/re-plan triggers.

### Research AGI

A research instruction SHOULD make clear:

- answerable question;
- source-quality requirements;
- time sensitivity/re-verification needs;
- claim/evidence format;
- unresolved assumptions;
- output and decision boundary.

Research MUST NOT grant implementation authority by itself.

### Review AGI

A review instruction SHOULD make clear:

- task and agreed acceptance criteria;
- evidence to inspect;
- allowed verdicts;
- what qualifies as a blocking issue;
- what counts as a non-blocking future improvement.

Reviewers MUST NOT invent new requirements merely because they prefer a
different implementation.

### Handoff AGI

A handoff SHOULD preserve:

- verified current state;
- assumptions/unknowns that still matter;
- completed and incomplete work;
- relevant working-tree/runtime state;
- blocker;
- exact next action;
- evidence/paths;
- actions that must not be repeated or guessed.

### Tool AGI

A state-changing tool exposed to agents SHOULD document:

- **USE WHEN**;
- **DO NOT USE WHEN**;
- inputs;
- result;
- side effects;
- failure behavior;
- escalation/reconciliation behavior.

Tools that mutate authority, files, external systems, permissions, money, or
irreversible resources require especially explicit operational boundaries.

### Decision AGI

A consequential decision record SHOULD state:

- decision question;
- options considered;
- authority/decision owner;
- decision;
- evidence/rationale;
- consequences and affected scope;
- superseded decision, if any.

## 10. AGI and worker capability

AGI readiness and worker suitability are independent gates:

```text
Instruction quality → AGI PASS / FAIL
Worker capability    → HPOM FIT / NOT FIT
```

Only work that passes both gates should begin.

MAPS MAY deliver the same semantic task contract differently by worker:

- stronger agents may receive broader bounded judgment;
- less reliable/local workers may receive smaller context, narrower output
  boundaries, shorter tasks, more procedural detail, and earlier verification.

The contract MUST NOT become less clear merely because the model is stronger.

## 11. Detail without micromanagement

AGI specifies the **decision envelope**, not every implementation decision.

For a capable worker, prefer:

```text
outcome + relevant context + boundaries + authority + acceptance + proof
```

over a brittle click-by-click or line-by-line script.

Increase procedural detail when:

- order is important;
- the tool boundary is dangerous;
- the worker is less reliable for the task;
- previous attempts repeatedly fail in the same way; or
- mistakes cannot be cheaply detected by verification.

## 12. Validation output

A human or future `maps agi check` command SHOULD produce a result shaped like:

```text
AGI TASK CHECK — TASK-042

✓ Outcome
✓ Owner
✓ Source of truth / inputs
✓ Preconditions / dependencies
✓ Work boundary
✓ Decision authority
✓ Acceptance criteria
✓ Verification / evidence
✓ Review requirement
✗ Stop / escalation

Fresh-Agent: PASS
No-Guess: FAIL
Scope: PASS
Authority: PASS
Completion: PASS
Failure: FAIL
Continuation: N/A

AGI STATUS: FAIL — NEEDS_SHAPING
Reason: security behavior may change but no escalation condition is defined.
```

The validator MUST NOT silently fill missing material fields on behalf of the
task author.

## 13. Vague-language linting

A future AGI linter SHOULD flag ambiguous phrases for review, including:

- `make it better`;
- `clean it up`;
- `optimize it`;
- `make it robust`;
- `handle gracefully`;
- `use best practices`;
- `make it production ready`;
- `fix as needed`;
- `improve performance`.

These phrases are not automatically forbidden. They pass only when nearby
criteria make the intended result or decision boundary observable.

## 14. Minimal rule

AGI exists to remove consequential ambiguity, not to maximize documentation.

For small, low-risk, session-local work, keep the instruction proportionate.
For consequential work, missing clarity MUST be treated as a shaping problem,
not as an invitation for the model to guess.
