# Operator Intent Compiler / Request Normalizer

Status: `PLANNING — NOT ACTIVE AUTHORITY`

Purpose: define the missing operator-facing intake layer that turns concise natural-language requests into bounded MAPS execution contracts without creating a second task authority or treating prompt text as canonical state.

## Placement

```text
OPERATOR
   │
   │  ordinary-language request
   ▼
OPERATOR INTENT COMPILER / REQUEST NORMALIZER
   │
   │  proposed structured task intent
   ▼
TASK SHAPING + AGI READINESS GATE
   │
   │  accepted canonical execution contract
   ▼
CANONICAL TASK / POLICY STATE
   │
   ├──────────────► Context Builder
   │                    │
   │                    ▼
   │               worker context
   │
   └──────────────► routing / harness / review / evidence
```

The Intent Compiler belongs **before Context Builder**.

- Intent Compiler answers: **What is the operator asking MAPS to accomplish, within what boundaries?**
- Context Builder answers: **What information/evidence does the worker need to execute that accepted contract?**

The compiler does not own task state. It proposes/shapes a contract that enters the existing MAPS task lifecycle and AGI gate.

## Why this exists

Operators should be able to speak naturally:

- "continue";
- "get these PRs under control";
- "fix the next blocker";
- "make this easier for a new agent";
- "do what you need to make progress."

A human collaborator can resolve those requests from shared context. A fresh agent needs the same intent expanded into durable fields: goal, current-state requirements, scope, authority, dependencies, acceptance criteria, evidence, stop conditions, and continuity.

MAPS should adapt concise operator intent into an agent-grade contract rather than requiring the operator to become a prompt engineer.

## Architecture rule

```text
operator request
+ authoritative current state
+ existing constraints
        ↓
structured proposed contract
        ↓
AGI/task gate
        ↓
canonical task state
        ↓
derived worker prompt
```

Never:

```text
operator request
+ model imagination
        ↓
expanded permission / new project scope
```

## Inputs

The compiler may consume only what is necessary to resolve the request:

- the operator's request;
- current canonical task/project state for continuation references;
- applicable `AGENTS.md`, policy, accepted decisions, and active task contracts;
- live repository/system evidence required to resolve current-state references.

Broad history is not a default input.

## Output

The target output is a **proposed execution contract**, using existing MAPS concepts rather than a new schema where possible:

- goal / observable outcome;
- source of truth;
- current-state inputs;
- output/change boundary;
- non-goals;
- bounded worker decision authority;
- operator/policy approval boundary;
- dependencies/preconditions/order;
- pass/fail acceptance criteria;
- verification/evidence;
- material unknowns/conflicts;
- stop/escalation conditions;
- continuity/handoff requirements.

A provider-specific prompt is a derived rendering of this contract.

## Authority and safety invariants

1. **Compilation is not authorization.** The compiler may clarify or structure existing intent but may not create operator approval, task ownership, destructive permission, external-action authority, or policy exceptions.
2. **One task truth remains canonical.** No separate mutable "intent database" should compete with canonical task state.
3. **Unknown remains unknown.** Material missing intent/authority stays `UNKNOWN` / `NEEDS_SHAPING` / `BLOCKED`.
4. **Constraints may narrow, not enlarge.** Repository and policy constraints can reduce what the request permits; they cannot silently expand the request.
5. **Prompt text is derived.** Worker prompts can be regenerated from the accepted task contract and current context; they are not a new authority layer.
6. **Reference resolution uses live state.** "Continue" or "the next PR" must be resolved against current authoritative evidence rather than stale conversation summaries when current state exists.
7. **No mandatory service/daemon.** The capability can begin as a shaping method and only become runtime machinery if evidence shows it is useful.

## Relationship to existing MAPS mechanisms

### Agent-Grade Instructions

The Intent Compiler is the **producer/shaper**; AGI is the **quality gate**.

```text
request compiler proposes contract
→ AGI checks whether material fields are sufficient
→ READY only if the contract passes
```

Do not weaken AGI because the compiler is model-assisted.

### Task lifecycle

The compiler feeds the existing `NEEDS_SHAPING → READY` path. It does not create another lifecycle.

### Context Builder

Context Builder runs after intent/task shaping. The compiler may identify **context requirements** (for example "recover current open PR state"), while Context Builder decides which exact sources satisfy those requirements.

### Policy/operator approval

Policy and operator authority remain external inputs/gates. The compiler can surface "operator approval required" but cannot manufacture the approval.

### Skills

A reusable request-compilation procedure may eventually be packaged as a Skill, but Skill content remains procedure, not authority.

### Evaluation

A future automated compiler should be promoted only through the existing evaluation path:

```text
frozen request cases
→ candidate compiled contracts
→ comparative report
→ proposal
→ independent review/operator gate where required
→ promotion
```

## Suggested phases

### Phase OIC-0 — Manual method / prompt recipe — `NOW`

Use `playbook/REQUEST_COMPILATION.md` as the active method for human/agent shapers.

Acceptance:

- concise requests can be expanded without inventing authority;
- existing task fields/AGI standard are reused;
- simple requests remain concise;
- continuation references are explicitly resolved from live state.

### Phase OIC-1 — Frozen request corpus — `P1/P2`

Build a small, representative frozen corpus containing:

- simple one-shot requests;
- continuation requests;
- repository/integration requests;
- ambiguous but harmless defaults;
- material authority ambiguity;
- conflicting current state;
- requests that should remain small;
- requests that require a full long-running contract.

Expected truth should distinguish explicit operator facts from derived constraints and intentional unknowns.

### Phase OIC-2 — Deterministic contract shape — `P2`

If the corpus shows value, define a bounded machine-readable projection using existing task-contract concepts.

Do **not** add persistent state unless the canonical task store genuinely cannot represent a required fact.

### Phase OIC-3 — Candidate compiler evaluation — `EVIDENCE-GATED`

Evaluate model/rule/hybrid compilers for:

- intent preservation;
- false scope expansion rate;
- invented authority/approval rate;
- missed-boundary rate;
- material-unknown detection;
- unnecessary clarification rate;
- AGI readiness accuracy;
- prompt/context economy;
- live-reference resolution correctness.

Security-critical gates should require zero invented permission/approval on the frozen corpus before a candidate can be proposed for normal use.

### Phase OIC-4 — Assisted intake — `EVIDENCE-GATED`

If a candidate wins the frozen comparison and passes review, expose it as an assisted task-shaping action.

It should produce a proposed contract for validation, not directly bypass the existing AGI/task/policy gates.

## Non-goals / rejected forms

Do not build:

- a second task/intention database;
- a permanent "prompt engineering agent" persona;
- a giant conversation summarizer that treats chat history as authority;
- automatic permission inference;
- automatic promotion from compiler quality score;
- a requirement that every tiny request become a verbose 13-section prompt;
- provider-specific prompt templates as canonical task truth.

## Definition of done

This capability is mature when an operator can give a concise request and MAPS can reliably produce a fresh-agent-ready task contract that:

- preserves the requested outcome;
- recovers live referents correctly;
- carries all material boundaries and evidence requirements;
- exposes material unknowns rather than guessing;
- never enlarges authority;
- passes the existing AGI readiness gate;
- supplies Context Builder with explicit context requirements;
- can be rendered into provider-neutral worker instructions without becoming a competing authority store.

Until then, the manual playbook method is the accepted implementation path.
