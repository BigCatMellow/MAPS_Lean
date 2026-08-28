# MAPS_L — Agent Start Here

This wiki is the **orientation surface for a fresh agent**. It teaches you how to
enter and use MAPS_L. It is **not an authority store** and must not become a
second operating contract.

If this wiki disagrees with the target project's live instructions or with
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md)
while working inside the MAPS_Lean repository, follow the higher/current source
and treat the wiki text as stale.

## If someone points you here and says “use MAPS_L”

Do this before broad reading:

1. **Identify the target project and objective.** Do not assume the MAPS_Lean
   repository itself is the target.
2. **Recover the target project's authority and live state.** Read its local
   agent instructions, approved roadmap/project scope, active task, and current
   evidence as applicable.
3. **Use MAPS_L as the operating method.** Preserve the target project's
   authority; do not import MAPS_Lean-specific permissions or repository rules
   into another project.
4. **If you are working on MAPS_Lean itself**, follow the canonical
   [`docs/FIRST_RUN.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md)
   route and read
   [`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md)
   first.
5. Read only the MAPS_L method your work needs. The normal reading budget is:

```text
target authority + approved roadmap/task + one relevant MAPS_L method
```

Do not read the whole wiki/playbook as a prerequisite ritual.

---

## What MAPS_L is

MAPS_L is a provider-neutral operating system for reliable agentic work. Its
purpose is to make capable agents easier to direct, coordinate, verify, recover,
and continue across tasks without replacing judgment with ceremony.

The core idea is:

> Use intelligence for judgment; use explicit contracts, deterministic state,
> evidence, and interfaces for the things that should not depend on memory or
> improvisation.

MAPS_L can be used at three depths. Use the **smallest depth that solves the
actual coordination problem**:

| Depth | Use when | Typical pieces |
| --- | --- | --- |
| **Method-only** | One agent or a small bounded task | objective, DONE, task boundary, verification, one relevant playbook method |
| **Orchestrated** | Multi-agent, multi-task, or long-lived work | roadmap, orchestration operator, bounded agent slots, task records, handoffs, independent review |
| **Runtime-backed** | Concurrent/resumable work needs durable machine state | SQLite task truth, LangGraph routing, hcom transport, RnS recovery, execution-integrity binding |

Do not install or invoke the full control plane merely because it exists.

---

## The control relationship

MAPS_L separates **authority**, **orchestration**, and **execution**:

```text
human owner / approved project authority
                 ↓
       orchestration operator
        ↓        ↓        ↓
    agent slot agent slot agent slot
        \        |        /
          returned work
                 ↓
       orchestration operator
   reconcile → decide → act/dispatch again
                 ↓
       verify acceptance criteria
          ↙             ↘
      complete        escalate
```

### Human owner

Defines the objective and approves the project/roadmap permission envelope.
Fresh human reauthorization is for a **true boundary crossing**, not routine
child tasks, checkpoints, reviews, or “continue?” prompts.

### Orchestration operator

The accountable director for the parent scope. It owns decomposition, dispatch,
supervision, recovery, reconciliation, verification, and the next-action
choice. **Delegation transfers execution, never ownership.**

While authorized actionable work remains, the operator continues driving the
parent scope. A finished child task is a reconciliation point, not a default
pause for the human.

### Agent slots

Subordinate execution resources for bounded work: implementation, research,
inspection, reproduction, review, classification, or another clearly scoped
job. They return evidence/results to the operator; they do not silently take
ownership of the parent scope or declare the whole project complete.

---

## The MAPS_L operating loop

Use this as the default mental model:

```text
RECOVER REALITY
      ↓
DEFINE OUTCOME + DONE
      ↓
SHAPE BOUNDED WORK / AGI CHECK
      ↓
SELECT WORKER + DISPATCH OR ACT
      ↓
EXECUTE + OBSERVE EVIDENCE
      ↓
VERIFY / REVIEW
      ↓
RECONCILE INTO PARENT STATE
      ↓
next authorized work? ── yes ──> shape/dispatch again
      │
      no
      ↓
PARENT COMPLETE

true authority boundary anywhere → isolate affected branch → escalate
```

Each operator cycle should create a meaningful state transition: act, dispatch,
reconcile, verify, recover, re-plan, resolve a dependency, or escalate a specific
boundary blocker. Repeated narration, observation, or waiting without a defined
dependency is not progress.

For a concrete pass through this loop, use [[First Task Walkthrough]].

---

## How to choose the right MAPS_L method

The canonical method index is
[`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md).
It is navigation, not another constitution.

Common routes:

| Need | Start with |
| --- | --- |
| Start a durable project | [`PROJECT_BOOTSTRAP.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROJECT_BOOTSTRAP.md) |
| Turn a normal request into an executable contract | [`REQUEST_COMPILATION.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/REQUEST_COMPILATION.md) |
| Check whether a consequential task is clear enough | [`AGI_STANDARD.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/AGI_STANDARD.md) |
| Run a task through ownership/review/completion | [`TASK_LIFECYCLE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/TASK_LIFECYCLE.md) |
| Use helpers / subordinate agents | [`HELPERS_AND_COMMUNICATION.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/HELPERS_AND_COMMUNICATION.md) |
| Choose a worker/model/harness | [`MODEL_CAPABILITY_ROUTING.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/MODEL_CAPABILITY_ROUTING.md) |
| Decide whether the next self-selected task is actually useful | [`PROGRAM_STEERING.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/PROGRAM_STEERING.md) |
| Reassess a multi-task roadmap | [`ROADMAP_TRAJECTORY_CHECK.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/ROADMAP_TRAJECTORY_CHECK.md) |
| Use the runtime/control plane | [`CONTROL_PLANE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/CONTROL_PLANE.md) |

Start with one. Follow a second only when a distinct concern actually requires
it.

---

## What the runtime does — and does not do

```text
SQLite      = mutable task truth / claims / lifecycle / review evidence
LangGraph   = deterministic next-route selection + checkpoint state
hcom        = communication / session transport
RnS         = bounded recovery of known active sessions
helpers     = bounded delegated work
integrity   = frozen execution contract + proof
Markdown    = durable human-readable roadmap, task, decision, evidence, handoff
```

None of these components creates project permission by itself. A route,
message, helper result, session, or runtime capability is not authority.

See [[Capability Status]] before assuming a particular runtime capability is
production-wired.

---

## Do not make these mistakes

- Do **not** treat this wiki as a competing rulebook.
- Do **not** import MAPS_Lean repository-specific permissions into another
  project.
- Do **not** treat delegation as completion.
- Do **not** ask the human to approve every child task or normal continuation
  inside an already approved envelope.
- Do **not** let a worker silently become parent owner.
- Do **not** call a parent complete while actionable work, active assignments,
  unreconciled results, recoverable blockers, unmet criteria, or required review
  remain.
- Do **not** chain-read methods by default.
- Do **not** create a second mutable source of truth when canonical state exists.
- Do **not** mistake a designed/tested capability for a production-wired one.
- Do **not** manufacture new work after genuine parent completion.

---

## If you are developing MAPS_Lean itself

Use the repository's own first-run path rather than relying on wiki summaries:

1. [`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md)
2. approved roadmap/project + active task
3. current state/handoff only when continuation requires it
4. control-plane docs only when relevant
5. one method from [`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md)

Then use [[First Task Walkthrough]] for the practical operator loop. Live
capability state belongs in the repository, not in a dated wiki snapshot.
