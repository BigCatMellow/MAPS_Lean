# First Task Walkthrough

A concrete MAPS_L execution path for a fresh agent. This page is intentionally
portable: use it whether the target is MAPS_Lean itself or another project using
MAPS_L methods.

Back to [[Home]]. For runtime maturity and live-state rules, see
[[Capability Status]].

---

## Step 0 — Establish the target and authority

Answer these before acting:

```text
What project am I operating on?
What observable outcome does the human want?
What source defines project authority?
What roadmap/task scope is already approved?
What would require fresh human reauthorization?
```

If the target project has local agent instructions, read them. If working inside
MAPS_Lean, the canonical entry route is
[`docs/FIRST_RUN.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md)
and the sole repository-wide contract is
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md).

Do not transplant MAPS_Lean-specific permissions into another repository.

---

## Step 1 — Recover reality before planning

Inspect current evidence instead of starting from memory or a stale summary.
Depending on the project, that may include:

- current code/product behavior;
- live repository/PR/CI state;
- approved roadmap and active task;
- current handoff/continuation state;
- relevant data, logs, tests, or user-visible output.

Separate `VERIFIED`, `REPORTED`, `ASSUMED`, and `UNKNOWN` when the distinction
matters.

A fresh operator should know what is true **now** before deciding what happens
next.

---

## Step 2 — Define DONE and shape the work

If the project spans sessions, multiple tasks, or multiple agents, first use
[`PROJECT_BOOTSTRAP.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROJECT_BOOTSTRAP.md)
to inspect reality, define the parent DONE condition, plan backward, build the
working roadmap, and identify the first wave. Do not jump straight into isolated
child tasks without a coherent parent destination.

For a small low-risk task, a concise working contract may be enough.

For consequential, multi-agent, or durable work, use the MAPS_L task contract
shape:

```text
GOAL / observable result
SOURCE OF TRUTH
OWNER
ALLOWED OUTPUTS / NON-GOALS
INHERITED AUTHORITY
DEPENDENCIES
ACCEPTANCE CRITERIA
VERIFICATION / EVIDENCE
REVIEW REQUIREMENT
FAILURE / RECOVERY / ESCALATION
```

Inside MAPS_Lean, the canonical template is
[`templates/task.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/templates/task.md)
and consequential work must be `AGI READY` under
[`playbook/AGI_STANDARD.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/AGI_STANDARD.md).

The purpose is not longer prompts. It is removing consequential ambiguity.

---

## Step 3 — Choose the smallest useful operating depth

### Method-only

Use when one capable agent can own the task safely. Apply the contract, one
relevant method, verification, and stop conditions. Do not add a control plane
for ceremony.

### Orchestrated

Use when work benefits from multiple bounded workers, parallel investigation,
independent review, or multi-task continuity.

The orchestration operator keeps parent ownership and creates **agent slots**
with narrow jobs such as:

```text
worker A → inspect/reproduce
worker B → implement bounded change
worker C → independent review
operator → reconcile all results and decide next action
```

Give every slot a bounded question/output, relevant context, evidence target,
stop condition, and integration owner.

### Runtime-backed

Use when concurrent/resumable work needs durable machine coordination. Then the
active runtime can supply task claims/lifecycle, routing, communication,
recovery, and execution-integrity state. Verify the needed capability is
actually wired before depending on it; see [[Capability Status]].

---

## Step 4 — Orchestrate; do not merely delegate

The operator's loop is:

```text
inspect parent state
→ choose highest-value eligible action
→ act directly OR dispatch bounded slot(s)
→ observe returned evidence/results
→ reconcile into parent state
→ verify what is now true
→ select the next action
```

Delegation is not a handoff of accountability. If a worker fails, stalls, or
returns incomplete work, responsibility returns to the operator for retry,
reassignment, re-planning, scope correction, research, or escalation.

Do not let parallelism create duplicate edits or multiple owners for the same
output surface.

---

## Step 5 — Execute against evidence

Prefer the smallest change that satisfies the observable requirement.

During execution:

- inspect before changing uncertain systems;
- keep work inside the task/roadmap boundary;
- amend/re-shape an in-scope task when evidence reveals a necessary dependency
  or output path;
- use tests, logs, screenshots, benchmarks, database state, or other direct proof
  appropriate to the work;
- do not hide failed assumptions or unresolved uncertainty.

A task is not complete because the implementation “looks right.”

---

## Step 6 — Verify and review proportionally

Use the smallest proof that is strong enough for the risk:

| Risk | Typical minimum |
| --- | --- |
| Low | accountable owner verifies observable result |
| Medium | relevant tests/reproduction + independent review |
| High | explicit criteria + reproduced evidence + independent review + operator-visible completion summary |

An independent reviewer checks the task, outputs, criteria, and evidence. Review
routes back to the orchestration operator:

```text
APPROVED          → reconcile and continue
CHANGES_REQUESTED → correct and re-review as needed
BLOCKED           → recover/research/reassign or escalate a true boundary
```

Review is a quality gate, not a routine human permission gate.

---

## Step 7 — Reconcile the child task into the parent

When a child task reaches DONE, the orchestration operator must not stop merely
because one unit of work finished.

It should:

1. record/reconcile what became true;
2. update parent/roadmap state where appropriate;
3. identify newly unblocked or highest-value eligible work;
4. shape/check the next task;
5. dispatch or execute it; and
6. continue until the **parent scope** is genuinely complete or a true authority
   boundary blocks further progress.

A status report, commit, PR, checkpoint, or review verdict is visibility, not a
request for permission to continue inside approved scope.

---

## Step 8 — Know the terminal state

There are only a few legitimate reasons for the operator to stop driving:

### COMPLETE

Parent acceptance criteria and required verification/review are satisfied. Stop;
do not manufacture additional scope.

### BLOCKED / ESCALATE

A specific unresolved dependency, safety condition, or authority boundary makes
productive in-scope action impossible. Name the exact blocker.

Fresh human reauthorization is appropriate when the next action would materially
leave the approved permission envelope or requires a human-only preference or
authority. It is **not** the default response to ordinary uncertainty: inspect,
research, use helpers/challenge, and decide inside authority first.

### ACTIVE WAIT

Waiting is legitimate only when a specific active dependency is expected to
return (for example a running worker/job). The operator should know what it is
waiting for and what happens when it returns or times out.

---

## Quick self-check before you call the work done

A fresh operator should be able to answer:

- What parent outcome am I accountable for?
- What is the live source of truth?
- What work is pending, active, returned-but-unreconciled, or blocked?
- Which worker owns each bounded execution slot?
- What evidence proves each completed criterion?
- What review is still required?
- What is the next authorized action?
- If I am stopping, is the parent complete or is there an exact blocker?

If those answers are unclear, the orchestration state is not yet healthy.

---

## When the target is the MAPS_Lean repository

Do not rely on this wiki for repo-specific commands or current queue state.
Follow the live repo:

- [`docs/FIRST_RUN.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md)
- [`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md)
- [`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md)
- [`docs/CHECKS_AND_BALANCES.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CHECKS_AND_BALANCES.md)
- live GitHub/CI and the active roadmap/task

Repository mechanics change faster than this orientation page. The linked live
files win.
