# AI instruction and context architecture review

Status: **deferred architecture finding**. Related issue: **#248**.

## Bottom line

MAPS_L should **not** be redesigned from scratch. The review found that its core architecture is already directionally strong: authority hierarchy, role separation, task shaping, independent review, handoffs, information lifecycle, Skill routing/progressive loading, and live-vs-durable coordination separation.

The opportunity is to make those mechanisms cheaper for an AI to consume, easier to route mechanically, and less vulnerable to duplicated/stale prose.

## Core principles

> **Minimum necessary context + explicit authority + conditional routing + measurable completion.**

> **Instructions should be routing, not documentation.**

> **Do not tell the AI everything. Tell it how to find what it needs, what it may do, and how to know it is finished.**

The intended optimization is:

> **Not fewer rules — fewer always-loaded rules.**

Rules that matter only for a particular role/state/task should remain available behind explicit triggers instead of being deleted or always loaded.

## Desired instruction shape

For AI-facing operational instructions, prefer an execution-mapped structure:

```text
OBJECTIVE
  → SUCCESS
  → AUTHORITY
  → SCOPE
  → EXECUTION
  → VERIFY
  → HANDOFF / DONE
```

Equivalent formal shape:

```text
Objective → Authority → Router → Constraints → Action → Verification → Done
```

For reusable procedures:

```text
WHEN
READ
DO
VERIFY
STOP / OTHERWISE
```

For individual rules:

```text
trigger → condition → action → verification
```

The point is not formatting aesthetics. It is to make branching, authority, and completion mechanically legible.

## Wording standard

Replace wording that rewards shortness alone with:

> **Minimum sufficient context. Remove words that do not change correctness, action, evidence, risk, or understanding. Never shorten past ambiguity.**

This is safer than wording such as `Concision is king. Brevity over grammar.` because an agent can optimize the latter by dropping load-bearing qualification.

Additional wording guidance:

1. Put action-driving information first.
2. Keep rationale near the action only when it changes execution/risk; otherwise route to a design/source document.
3. Prefer explicit nouns over ambiguous pronouns.
4. Use typed vocabularies for states/verdicts when agents/machines branch on them.
5. Deliberately distinguish **MUST / SHOULD / MAY**.
6. State trigger and scope explicitly.
7. Put stop/escalation conditions next to the action they constrain.
8. Put acceptance/verification next to the outcome being claimed.
9. Keep narrative explanation out of always-loaded surfaces when a router can point to it.
10. One rule should own one concept; avoid slightly different paraphrases across high-authority docs.

## Root `AGENTS.md` should become a compact kernel

The review concluded that root `AGENTS.md` is conceptually correct but risks becoming an always-loaded manual.

Target: retain in the root kernel only rules whose absence would materially change correctness, authority, safety, routing, or completion for a large fraction of sessions.

Candidate kernel categories:

- authority/precedence;
- source-of-truth/live-state recovery;
- scope/action boundaries;
- ownership/review independence;
- routing to task/role/method docs;
- verification/DONE;
- explicit stop/escalate conditions.

Useful line-level test:

> If this line disappeared from the always-loaded kernel, would correctness, authority, safety, routing, or completion materially change for many sessions?

If not, it may belong behind a trigger/specialist route. Do **not** move a rule merely to reduce line count if the move makes the trigger undiscoverable.

## Existing anti-sprawl architecture worth preserving/revalidating

The earlier review/archaeology found several mechanisms already moving in the desired direction. These are historical findings to re-check before implementation, not frozen current facts:

- root `AGENTS.md` as the single repository-wide operating contract;
- no competing global operating contracts;
- formal precedence for conflicts;
- “Hard operating invariants” rather than ambiguous negative-default prose;
- **One concept, one owner document**;
- a common-case reading target roughly:

```text
AGENTS.md
+ approved roadmap/task
+ one relevant playbook method
```

- needing chains of roughly five playbooks for ordinary work was identified as a design smell;
- `playbook/INDEX.md` routes core vs specialist methods;
- documentation-sprawl checks/budgets existed to make information-routing cost mechanically visible rather than unbounded.

Do not preserve old exact budget numbers blindly. Preserve the principle: **common-path read cost and active-method sprawl should be bounded/measured**.

## Stable rule IDs / canonical ownership

Normative duplication can emerge across `AGENTS.md`, task lifecycle, AGI standard, checks/balances, coordination docs, and other methods.

Candidate stable IDs:

- `AUTH-*` — authority/precedence;
- `TRUTH-*` — source truth/live-state recovery;
- `SCOPE-*` — write/action boundary;
- `OWNER-*` — ownership/claims;
- `REV-*` — independent review;
- `FLOW-*` — lifecycle/routing;
- `DOC-*` — information durability/anti-sprawl;
- `DONE-*` — completion/verification.

A stable ID is useful only when it has:

- one canonical owner;
- stable semantics;
- multiple consumers or a clear inheritance need;
- a deliberate migration/review path if semantics change.

The goal is for subordinate docs to **inherit/reference** a load-bearing rule rather than maintain quasi-authoritative paraphrases. Do not assign IDs to every sentence.

## `AGENTS.md` vs `AGI_STANDARD.md`

Preserve this conceptual distinction:

```text
AGENTS.md
= how AI operates in the repository

AGI_STANDARD.md
= how work is shaped/spec'd so AI can execute reliably
```

“AGI” here means **Agent-Grade Instructions**, not artificial general intelligence. Future wording should make that meaning obvious without forcing rename churn unless a rename has clear net value.

A well-shaped task should expose at minimum:

- objective/observable result;
- verified source truth;
- assumptions/unknowns;
- write/action boundary;
- decision authority;
- acceptance criteria;
- verification;
- review requirement;
- stop/escalate conditions;
- completion/next action.

## Role-triggered loading

A role-bound session can require a chain similar to:

```text
AGENTS
→ coordination README
→ GITHUB_ASYNC_WORK_PULL
→ BACKLOG_RECOVERY when active
→ role contract
→ task/PR evidence
```

The safe improvement is to make **inactive steps conditional**, not to skip applicable authority.

A role/task router should answer:

```text
What role/state am I in?
Which methods apply?
Which methods are inactive?
What exact source must I read next?
```

Success must be measured as **authority/safety equivalence + lower irrelevant context**, not token reduction alone.

## Automatic context compilation

Explore a surface such as:

```text
maps context --role SENTINEL --pr <N>
```

or equivalent.

The output should be an **ephemeral, non-authoritative context packet** assembled from accepted/canonical sources.

Candidate packet:

```text
OBJECTIVE
APPLICABLE AUTHORITY
ROLE
SUBJECT / TASK
WRITE & ACTION BOUNDARY
REQUIRED METHODS
VERIFIED LIVE STATE
ACCEPTANCE / REVIEW CRITERIA
STOP CONDITIONS
NEXT LEGITIMATE ACTION
```

A useful builder should distinguish:

- **Required** context;
- **Optional** context;
- **Excluded** context.

Useful metadata:

- selection reason;
- authority/canonicality;
- source identity/path;
- revision/hash where useful;
- freshness/timestamp where useful;
- retrieval/query reason where applicable;
- token/size estimate;
- warnings/ambiguities.

Important ranking rule:

> **Canonical documents and exact task inputs outrank semantically similar but stale/indirect artifacts.**

Semantic retrieval must not cause a similar old note to beat an exact current task/source.

## Context packet is a view, not truth

```text
authoritative sources
        ↓
context compiler/router
        ↓
ephemeral packet
        ↓
agent
```

If packet content conflicts with the source, the source wins. The packet should expose enough provenance/freshness to detect staleness.

Do not create another mutable context/status database merely to make packets convenient.

## Relationship to project memory

Durable Project Memory and Context Compilation are complementary but distinct:

```text
Durable Project Memory
= what the project durably knows / current meaning reconciliation

Context Compilation
= the minimum relevant subset for this agent/task now
```

The project-memory feature may become one important source for the context compiler, but a compiled packet must remain ephemeral.

## Information reconciliation principles also apply to context

The broader finding was that MAPS_L's challenge is often **disposition drift**, not lack of stored information.

Preserve:

> **Preserve history deeply, surface current meaning shallowly.**

Context routing should prefer reconciled current meaning while preserving routes to deeper historical evidence when it is relevant.

“Nothing should be an island” also applies:

- link rather than duplicate;
- preserve forward disposition when older records change meaning;
- make proposal → decision → implementation → partial/full resolution → remaining/rejected/dormant relationships recoverable.

This is one reason semantic similarity cannot mechanically decide which text to delete.

## Stable policy vs configuration vs live state

Preserve a three-way distinction:

```text
STABLE POLICY
  durable invariants / authority / rules

CURRENT CONFIGURATION
  workflows, branch protection, enabled checks, tool settings

LIVE STATE
  PR heads, CI, blockers, reviewer claims, current queue
```

Review `docs/CHECKS_AND_BALANCES.md` and similar surfaces for accidental mixing. Configuration should be mechanically inspectable or explicitly snapshot-labeled. Live state belongs on GitHub/accepted state stores, not durable prose that needs a commit every time the queue changes.

## Shortest useful retrieval, not link density

Documentation maintenance should optimize for:

- shortest useful route to the owner;
- a few strong hubs;
- direct links where the question is common;
- specialist/history surfaces behind routers;
- no graph-density work for its own sake.

A link should exist because it improves future retrieval, not because “more links” looks more documented.

This aligns with [`playbook/INFORMATION_LIFECYCLE.md`](../../../playbook/INFORMATION_LIFECYCLE.md).

## Digital Fungus / route-level evaluation

Evaluation should measure real agent routes, not only static file size.

Representative scenarios:

- ordinary bounded implementation;
- independent SENTINEL review;
- SWITCHYARD/integration work;
- research-only task;
- operator-decision-blocked task;
- Portable Deployment/external-project work;
- fresh-session continuation using Durable Project Memory.

Candidate metrics:

- tokens/bytes loaded before first legitimate action;
- number of documents traversed;
- irrelevant-context proportion;
- duplicate/near-duplicate normative claims;
- correct authority/source selection;
- missing required specialist method;
- stale/live-state confusion;
- task success/correctness;
- verification/review quality.

Token count is a planning metric, not the objective.

## Semantic duplication detection

Potential advisory flow:

```text
high-authority docs
    ↓
semantic/structural similarity scan
    ↓
possible duplicate normative concepts
    ↓
reviewer decides canonical owner/reference strategy
```

Do not auto-delete repeated safety text based on embeddings/string similarity. Critical repetition may be intentional and justified.

## Candidate implementation arc

1. Recover current accepted architecture/live coordination.
2. Measure baseline context routes before changing them.
3. Identify actual normative duplication and canonical owners.
4. Define compact kernel/trigger model and stable-rule-ID policy.
5. Normalize compiler-friendly task concepts where necessary.
6. Prototype routing/context compilation without changing authority.
7. Compare representative routes to baseline.
8. Only then compress/move normative text.
9. Add mechanical safeguards only for repeated failure patterns.
10. Independently review authority/safety equivalence.
11. Roll out incrementally rather than rewriting all docs at once.

Conceptual pipeline:

```text
HUMAN INTENT
    ↓
AGENT-GRADE TASK SHAPING
    ↓
AUTHORITY + BOUNDARY
    ↓
TASK CLASS
    ↓
CONTEXT ROUTER
    ↓
MINIMUM CONTEXT PACKET
    ↓
AI
    ↓
EXECUTION
    ↓
VERIFY
    ↓
DONE
```

## Non-goals

- redesign MAPS_L from scratch;
- delete safety rules merely to save tokens;
- make generated context authoritative;
- create another live-status ledger;
- embed volatile PR/CI facts in stable policy;
- require one giant packet for every task;
- create stable IDs for trivial prose;
- treat token minimization as success if correctness or recoverability declines.
