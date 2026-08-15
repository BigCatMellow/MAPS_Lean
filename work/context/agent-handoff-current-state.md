# MAPS Lean — current agent handoff

Status: `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`

Purpose: give a new agent enough orientation to continue work without rereading the entire conversation or rediscovering the design history.

Read `AGENTS.md` and the current task first. This file is explanatory context only.

---

# 1. Project direction

MAPS Lean is evolving from a large historical multi-agent orchestration system into a smaller system that keeps the strongest mechanisms while rejecting unnecessary bureaucracy.

The recurring design rule is:

> preserve useful guarantees, evidence, and lifecycle mechanics; do not recreate old complexity because it once existed.

A second major rule is:

> use agents for judgment/exploration; use deterministic mechanisms for things that must always happen.

---

# 2. Current development branch / PR

Current branch used for the recovery/research/roadmap tranche:

`agent/preserve-recovered-legacy-ideas`

Draft PR:

`#19 — Preserve and implement priority MAPS Lean improvements`

At the time this handoff note was written, the PR remained open/draft pending independent review.

Do not treat draft-branch behavior as settled `main` authority merely because it is described here.

---

# 3. Important active/draft implementation already built

The current tranche includes:

- negative operating contract in `AGENTS.md`;
- risk-specific review lenses;
- secret-safer event/diagnostic boundaries;
- read-only task trace v1;
- PR-triggered runtime CI;
- append-only post-completion outcomes;
- Context Builder v1;
- read-only status surface v1;
- review staging packets under `work/review_queue/`.

The integrated feature head previously passed the full runtime CI stack; later planning/research/documentation commits should not be assumed equivalent to a new full validation run unless CI confirms them.

---

# 4. Legacy archaeology already completed

The legacy MAP System was audited broadly enough to recover high-signal ideas from:

- task history;
- late tasks;
- ideas;
- experiments;
- insights;
- syntheses;
- promotions;
- candidate records;
- selected emergence/process material.

Key files:

- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`
- `migration/FUTURE_IDEAS_BACKLOG.md`
- `migration/LEGACY_KNOWLEDGE_AUDIT.md`
- `migration/LEGACY_PROMOTION_LEDGER.md`

Important correction:

Legacy `EXP-0006` did not validate the old lexical claim-card retriever. Preserve exact evidence anchors/hashes/drift/temporal negatives/eval methodology, not that retriever.

---

# 5. Prime Agent work

The Prime Agent harness was **not** rebuilt as a separate system.

Instead, useful Prime concepts were translated into a Lean adoption roadmap:

`work/roadmaps/prime-agent-capability-roadmap.md`

Prime's useful value is treated as lifecycle guarantees around workers:

- provider-neutral start/attach/send/inspect/recover/stop/collect;
- explicit run/session/helper lineage;
- continuity through interruption;
- safe delegation;
- review/evidence revision binding;
- optional worktree isolation;
- controlled helper continuity;
- deterministic lifecycle flows;
- capability/skill composition;
- operational learning;
- measured harness refinement.

Explicitly rejected by default:

- large `mapd` daemon;
- second task/session authority database;
- fixed permanent agent roster;
- persona-heavy roles;
- autonomous self-promotion/self-modification;
- giant knowledge graph;
- universal sandbox/microVM per worker absent a need.

---

# 6. External agent-harness research

Before implementing the Prime roadmap, external systems were researched to mine hard-won mechanisms rather than copy products.

Research file:

`work/research/agent-harness-patterns-scan-2026-08.md`

Major recovered patterns:

- deterministic lifecycle hooks/interceptors;
- Agent Skills/progressive procedural loading;
- environment blueprints/reproducibility;
- Agent-Computer Interface quality;
- portable trajectories/Run Records;
- immediate deterministic checks around mutations;
- explicit separation of facts/procedures/tools/flows/authority;
- dynamic capability loading;
- stable telemetry/correlation identifiers;
- agentic threat modeling;
- time-travel/fork debugging as a later tool;
- third-party skill/tool supply-chain governance.

---

# 7. Five detailed capability roadmaps

Directory:

`work/roadmaps/agent-harness-capabilities/`

Read the directory `README.md` first.

Roadmaps:

1. `01-harness-mechanics.md`
   - typed Harness API;
   - hooks/interceptors;
   - normalized operation results / ACI standard;
   - session/run lineage;
   - immediate deterministic validation;
   - Run Record foundations.

2. `02-procedural-knowledge-and-skills.md`
   - Agent Skills compatibility;
   - progressive disclosure;
   - Skill provenance/trust/lifecycle;
   - Skill routing/evaluation;
   - Capability Packs later;
   - clear knowledge/procedure/tool/flow distinction.

3. `03-environment-and-reproducibility.md`
   - `EnvironmentSpec`;
   - environment fingerprints;
   - drift/compatibility;
   - harness/compute separation;
   - worktree/sandbox integration;
   - snapshots/rehydration later.

4. `04-agentic-security.md`
   - threat model;
   - prompt/goal hijacking;
   - tool misuse;
   - excessive privilege;
   - identity confusion;
   - Skill/MCP supply chain;
   - memory poisoning;
   - stale recovery/session attacks;
   - adversarial regression corpus;
   - future credential broker.

5. `05-learning-and-evaluation.md`
   - portable Run Records;
   - incident taxonomy;
   - frozen regression cases;
   - three-layer evaluation;
   - Skill/ACI/environment experiments;
   - operational learning;
   - proposal-only harness refinement.

---

# 8. Current recommended implementation order

Do not jump straight to “self-improvement.”

The roadmap sequence is:

```text
Wave 0
review/stabilize current PR foundation

Wave 1
normalized operation results
Harness API
Hook framework
stable run/session correlation
agentic threat model
current-system adversarial tests

Wave 2
Agent Skills compatibility
Skill provenance/linting
progressive disclosure
EnvironmentSpec
EnvironmentFingerprint
immediate post-mutation validation

Wave 3
fuller session/helper/recovery lineage
portable Run Records
explainable waits
recovery/environment compatibility
Skill behavioral evaluation
quarantine path for imported capabilities

Wave 4 (trigger-based)
worktree isolation
persistent task-scoped helper continuity
snapshots
credential broker
Capability Packs
time-travel/fork debugging

Wave 5 (evidence-gated)
frozen incident corpus
three-layer eval system
operational learning
current-vs-candidate harness comparisons
reviewed refinement proposals
```

---

# 9. Shared mechanism hierarchy

Use this as a design heuristic, not active authority:

```text
must always happen
→ hook / invariant / validator

reusable expertise
→ Skill

concrete action
→ tool / script

stable repeated sequence
→ flow

task-specific fact/evidence
→ context / source

judgment/exploration
→ agent / helper

high-impact permission
→ policy / operator

future improvement
→ outcome → evaluation → reviewed proposal
```

A recurring anti-pattern is creating a new agent for a problem that is actually deterministic procedure, validation, packaging, or policy.

---

# 10. Important invariants and lessons

## One fact, one authority

Do not duplicate mutable truth across subsystems.

## Capability is not permission

Tool/worker support for an operation does not authorize its use for the current task.

## Citation is not ratification

Repeated memory/notes/Skill text do not become policy merely because agents cite them.

## Unknown remains unknown

Do not infer missing lineage/session/environment/authority facts from convenience.

## Durable state needs lifecycle

Any new durable object should define create, correct, supersede, retire, recovery, and authority semantics.

## Review evidence has a revision boundary

Eventually bind approval to exact artifacts/revisions or re-derive critical evidence at review time.

## Security tests prove behavior

Exercise the boundary; do not rely on source text containing the right phrase.

## Bounded audits beat permanent watchdog agents

Use meta-analysis where useful, but keep it scoped unless repeated evidence proves continuous machinery is warranted.

---

# 11. Operator working preferences that affect project execution

These preferences were explicit in conversation and partly promoted into `AGENTS.md`.

For ordinary work:

- do not overcomplicate;
- do not over-explain;
- avoid material assumptions;
- do not silently widen scope;
- ask/research/escalate rather than guess across consequential uncertainty;
- do not create duplicate truth;
- do not manufacture work after success.

For roadmaps/architecture/research:

- **do not be brief**;
- include rationale;
- current state;
- target state;
- architecture;
- dependencies;
- implementation sequence;
- candidate interfaces/schemas;
- authority boundaries;
- failure/recovery behavior;
- security/concurrency implications;
- tests;
- acceptance criteria;
- promotion gates;
- metrics;
- alternatives/rejections;
- non-goals;
- future extensions;
- task breakdown.

This difference is intentional.

---

# 12. What to inspect before implementing next

For a new implementation task, inspect in this order:

1. current `AGENTS.md`;
2. current canonical task state/requirements;
3. current relevant implementation/tests;
4. `work/roadmaps/agent-harness-capabilities/README.md`;
5. the specific capability roadmap;
6. `work/context/design-decisions-and-rationale.md` if a design tradeoff appears;
7. original research only when source rationale/evidence matters.

Do not implement directly from this handoff note.

---

# 13. Likely next concrete work after review

Once the current draft foundation is independently reviewed/stabilized, the strongest first implementation tranche is expected to be:

```text
normalized operation result contract
        ↓
provider-neutral Harness API
        ↓
small deterministic Hook framework
        ↓
stable session/run correlation
        ↓
security/adversarial tests around those boundaries
```

That gives later Skills, EnvironmentSpec, security enforcement, and learning infrastructure a common mechanical foundation.
