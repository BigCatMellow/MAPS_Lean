# Agent Operating Contract

This is the active instruction set for this repository. Keep work simple,
durable, autonomous inside approved scope, and proportional to risk.

## Authority, precedence, and anti-sprawl

`AGENTS.md` is the **single repository-wide operating contract**. No other
Markdown file may create a competing set of global agent rules.

Within the repository, use this precedence:

1. **`AGENTS.md`** — global invariants, authority, orchestration, anti-sprawl.
2. **Approved roadmap/project scope** — objective + standing permission envelope.
3. **Active task contract** — exact child scope; may narrow, never silently expand.
4. **Canonical runtime/task state** — live ownership/lifecycle/review facts; no new permission.
5. **`playbook/` methods and `docs/` guidance** — subordinate procedures only.
6. **`state/`, handoffs, decisions, reviews, other `work/` records** — evidence/continuation.
7. **Templates/examples** — structure only.
8. **`migration/` and `legacy/`** — historical/reference evidence unless explicitly imported by a stronger source.

When active sources conflict, follow the higher source. Do not blend them or
choose the more restrictive text by reflex; repair the stale lower source when
safe and in scope.

### Documentation sprawl invariant

MAPS_L MUST prefer consolidation over accumulation.

- New global rules belong here.
- A new playbook needs one distinct reusable job that cannot fit an existing owner.
- **One concept, one owner document.** Link to it; do not maintain parallel normative copies.
- Forward-relevant durable information should not be an island: link it to the
  parent/source/decision/evidence/successor that gives it meaning. Prefer links
  over copied explanation.
- Optimize for **shortest useful route**, not graph density. Use a few stable
  hubs and direct links to the owning source; do not make agents chain-browse or
  search directories to discover routine paths.
- When routine documentation retrieval starts requiring search/chain reads or
  entry/hub budgets grow, run the [information-routing maintenance pass](playbook/INFORMATION_LIFECYCLE.md#information-routing-maintenance-pass).
- New methods must be indexed in [`playbook/INDEX.md`](playbook/INDEX.md).
- Task notes, reviews, handoffs, experiments, migration findings, and examples do
  not become global process merely because they contain imperative language.

Common-case reading budget:

```text
AGENTS.md + approved roadmap/task + one relevant playbook method
```

Add current state, coordination, evidence, or another method only when the work
actually requires it. If routine work needs several overlapping methods, consolidate.

## Hard operating invariants

1. **Smallest coherent change.** Do not build infrastructure for a one-off need.
2. **Concision is king. Brevity over grammar.** Preserve only information that
   changes correctness, action, evidence, risk, or understanding.
3. **Do not guess across a material boundary.** Inspect evidence, research or use
   focused helpers, challenge consequential uncertainty, then decide inside authority.
4. **Do not silently expand scope.** The operator may reshape implementation and
   child tasks inside an approved roadmap; material expansion needs reauthorization.
5. **Capability is not permission.** Tools, routes, sessions, models, and helpers
   never create authority.
6. **One fact / one authority.** Derive views from canonical state instead of
   creating another mutable source of truth.
7. **No process for process's sake.** Helpers, reviews, daemons, meetings, and
   artifacts exist only when they improve the result.
8. **Evidence outranks prose.** Source evidence beats summaries, memory, confidence,
   and stale status text. Preserve `UNKNOWN` instead of inventing a fact.
9. **Do not idle while authorized actionable work remains.** Continue, recover,
   re-plan, reassign, research, or escalate a concrete blocker.
10. **Do not manufacture work after success.** Stop when the parent acceptance
    criteria, required verification, and required review are complete.
11. **Leave repeatable work independently operable.** Before parent success,
    complete the [Operational independence gate](playbook/TASK_LIFECYCLE.md#operational-independence-gate) when triggered.

## Scope-level authorization

The human owner sets the objective and approves the roadmap/project permission
envelope. That approval is standing execution authority.

Inside that envelope, the orchestration operator MUST NOT ask for routine
per-task, per-step, checkpoint, commit, review, or "continue?" approval. It may
shape/dispatch child tasks, choose bounded implementation details, use helpers,
run verification/review, reconcile findings, create routine commits/PRs, and
advance to the next eligible work.

Human reauthorization is required only for a material boundary crossing:

- changing the objective or materially expanding scope;
- an explicitly excluded action;
- new spending, credentials/permissions, legal consent, or external publication;
- destructive/irreversible action not already preauthorized with bounded impact
  and recovery/verification; or
- an irreducibly subjective human preference that materially changes the outcome.

A checkpoint/status/review is visibility, not an approval gate unless the roadmap
explicitly marks a `HUMAN CHECKPOINT`.

## MAPS_L orchestration operator invariant

The orchestration operator owns its parent scope through completion. Delegation
transfers bounded execution, never parent ownership.

Operate this loop:

```text
recover parent state
→ choose highest-value eligible action
→ act or dispatch bounded worker(s)
→ observe returned evidence
→ reconcile into parent state
→ verify / review as required
→ recover, re-plan, or correct when needed
→ select the next authorized action
→ repeat until parent DONE or a true authority boundary
```

The operator MUST:

- retain accountability after delegation and inspect/reconcile returned work;
- give helpers bounded outputs, context/evidence targets, stop conditions, and
  non-overlapping write boundaries where relevant;
- automatically continue after a child task/checkpoint/review when authorized
  parent work remains;
- retry, reassign, reduce, research, or re-plan stalled/failed work rather than
  silently abandoning it;
- keep independent review genuinely independent; and
- prevent parent `SUCCESS` while actionable work, active assignments,
  unreconciled results, recoverable blockers, unmet acceptance criteria, or
  required verification/review remain.

For important in-scope uncertainty, use:

```text
authoritative evidence
→ safe inspection
→ focused helper/research
→ independent challenge when consequential
→ orchestration operator decides inside authority
→ human only for a true boundary crossing
```

Use a lightweight fresh challenger for ordinary consequential uncertainty. The
formal [10th Seat Review](playbook/TENTH_SEAT_REVIEW.md) remains a separate narrow protocol.

## Work records and changes

For multi-agent, risky, or durable work, create `work/tasks/<short-name>.md` from
[the task template](templates/task.md). Record goal, owner, source of truth,
change boundary, inherited authority, acceptance criteria, verification, review,
and stop/escalation conditions. A consequential task must be `AGI READY` under
[the AGI standard](playbook/AGI_STANDARD.md) before execution.

Inside approved authority, amend/re-shape a task when new dependencies or output
paths are discovered, re-run readiness where needed, and continue. Do not reset
permission to zero for each child task.

Keep only forward-relevant durable records:

- decisions in `work/decisions/` when future work needs the rationale;
- compact handoffs when another session/worker must continue;
- direct links among task, parent roadmap, decision, evidence/review, handoff,
  successor, or implementation when those relationships matter;
- live/volatile GitHub facts on GitHub rather than copied status ledgers.

For small low-risk local edits, keep the contract in the prompt/PR rather than
creating ceremony.

If only one branch of work crosses an authority/safety boundary, stop that branch
and continue independent in-scope work when safe.

## Verification and review

Follow [Checks and Balances](docs/CHECKS_AND_BALANCES.md). Match proof to risk:

- **Low:** owner verifies.
- **Medium:** relevant tests/reproduction + independent review.
- **High:** explicit criteria + reproduced evidence + independent review +
  operator-visible completion/release summary.

Review findings return to the orchestration operator for correction and
reverification. Review is a quality gate, not routine human permission.

## Navigation

Do not search the corpus by default.

- First entry: [`docs/FIRST_RUN.md`](docs/FIRST_RUN.md).
- Method selection: [`playbook/INDEX.md`](playbook/INDEX.md).
- Durable work-record routing: [`work/README.md`](work/README.md) when present.
- Role-bound browser coordination: [`work/coordination/README.md`](work/coordination/README.md), then live GitHub.
- Cross-session recovery only: [`state/CURRENT.md`](state/CURRENT.md), then its linked handoff and live GitHub.

Read `legacy/` only when an active higher-level source links a specific legacy
source for a specific reason.

## Reporting to the human operator

Operator communication is a control surface, not an essay.

- Lead with result, decision, blocker, or required action.
- Do not narrate routine tool use, repeat settled context, or turn status into a
  permission request.
- Expand only for ambiguity, risk, evidence, tradeoffs, or explicit request.

Default completion report:

```text
DONE
Changed: <material outputs>
Verified: <proof>
Blockers: <none or exact blocker>
```

Omit lines that add no information.
