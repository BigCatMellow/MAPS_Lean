# MAPS / Prime Agent conversation history — 2026-08-15

Status: `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`

Purpose: preserve how the current MAPS Lean architecture, Prime-agent roadmap, and external capability roadmaps emerged from the conversation. This is a synthesis, not a verbatim transcript.

---

# 1. Starting point: recover useful legacy MAPS ideas without rebuilding legacy MAPS

The project entered this phase with a large amount of historical MAP System material under `legacy/MAP-System/MAP_System/...` and a much smaller current implementation in `BigCatMellow/MAPS_Lean`.

The governing operator direction became:

> salvage useful mechanisms and invariants, not old-system complexity or bureaucracy.

That distinction shaped the entire audit.

The task was not to restore old modules because they once existed. The task was to inspect:

- old tasks;
- late tasks;
- parked and abandoned ideas;
- experiments;
- insights;
- syntheses;
- promotions;
- emergence records;
- process notes;
- implementation remnants;

and determine which **mechanisms** still improved a Lean system.

This produced three broad classes:

1. mechanisms already solved or superseded in Lean;
2. mechanisms worth preserving for later promotion;
3. old architecture/project-specific machinery that should remain retired.

The preservation work was recorded in:

- `migration/LEGACY_IDEA_RECOVERY_AUDIT.md`;
- `migration/FUTURE_IDEAS_BACKLOG.md`;
- related migration audit/ledger files.

A key historical correction from the archaeology was that legacy `EXP-0006` did **not** validate the old lexical claim-card retriever. What survived from that work were evidence techniques—exact anchors, hashes, source drift, temporal attribution, negatives, frozen/blinded evaluation—not the failed retriever itself.

---

# 2. Operator contract: simplify behavior, reduce narration, stop guessing

During the audit and implementation work, the operator clarified a strong working preference:

- do not overcomplicate tasks;
- do not talk excessively during ordinary work;
- use brevity where grammar can be compressed without losing meaning;
- do not make material assumptions;
- ask/escalate/research when a consequential unknown remains;
- do not silently expand scope;
- do not confuse capability with authority;
- do not create duplicate sources of truth;
- do not create permanent machinery for one-off problems;
- stop when the requested result is complete rather than manufacturing more work.

These preferences were promoted into the active negative operating contract in `AGENTS.md`.

An important later clarification created an explicit exception:

> **Roadmaps should be detailed, comprehensive, and implementation-ready rather than brief.**

The resulting communication rule is therefore:

```text
ordinary execution / status / answers
→ concise, smallest sufficient explanation

roadmaps / architecture plans / research synthesis
→ comprehensive, explicit, structured, rationale-rich
```

This exception matters because future agents should not apply the brevity rule mechanically to planning artifacts.

---

# 3. First Lean implementation tranche: recover high-value low-complexity mechanisms

The legacy audit identified several mechanisms that were both valuable and ready to implement without recreating old MAPS complexity.

A draft branch/PR was created:

- branch: `agent/preserve-recovered-legacy-ideas`
- PR: `#19 — Preserve and implement priority MAPS Lean improvements`

The implemented tranche grew to include the following.

## 3.1 Negative operating contract

Added to `AGENTS.md` so operating constraints would be active guidance instead of historical prose.

## 3.2 Risk-specific review lenses

Rather than creating multiple reviewer roles merely for process compliance, review now uses only the lenses triggered by actual risk:

- functional/acceptance;
- security/trust boundary;
- privacy;
- destructive/data-loss;
- release/acquisition path;
- authority/permission boundary.

One independent reviewer may cover several lenses.

## 3.3 Secret-safer diagnostics/events

Free-text event/diagnostic surfaces gained best-effort redaction for sensitive material, while canonical owning-table evidence is not silently rewritten.

This specifically addressed a historical late-task gap where event appenders had been left outside redaction.

## 3.4 Read-only trace v1

A trace command was added to reconstruct canonical task/review/policy/run/context/criterion/outcome evidence while explicitly reporting coverage gaps.

The design preserves an old lesson:

> partial replay must never pretend to be complete replay.

Raw submission evidence is intentionally omitted from trace v1.

## 3.5 Pull-request CI validation

The runtime workflow was changed to run on pull requests, because the previous branch-specific push triggers could allow review branches to avoid the normal validation path.

## 3.6 Append-only outcome feedback

MAPS gained post-completion outcomes:

- SUCCESS;
- PARTIAL;
- FAILURE;
- UNKNOWN.

Outcomes include provenance, optional run binding, failure/rework/intervention metadata, task revision, and append-only supersession.

The key conceptual separation is:

```text
DONE
= MAPS completion/review state

Outcome
= what happened later in reality
```

An outcome does not silently reopen a task or rewrite authority.

## 3.7 Context Builder v1

Context Builder was intentionally explicit-first:

- root `AGENTS.md`;
- task inputs;
- task sources;
- dependencies;
- exact paths/hashes;
- missing/outside/directory boundaries;
- task outputs/non-goals/acceptance/stop/authority/review information.

It explicitly does not perform repository-wide semantic retrieval, lexical retrieval, embeddings, or knowledge-graph construction.

This was a direct response to the legacy retrieval evidence: preserve evidence integrity before adding fuzzy retrieval.

## 3.8 Read-only status v1

MAPS gained a small operator surface for lifecycle counts, claims/leases, review attention, blockers, stale leases, recent event metadata, and latest post-completion failure outcomes.

It intentionally does **not** become an old-style Command Center or auto-remediation daemon.

## 3.9 Review queue

The operator asked to “put things in a folder for review for later and keep working.”

This became `work/review_queue/`, containing review packets rather than copied source files.

The review queue is explicitly a convenience/staging layer, not task authority or canonical state.

---

# 4. Important legacy ideas preserved but not prematurely built

The archaeology recovered several mechanisms that remained useful but were not yet justified by current evidence.

Examples:

- three-layer evaluation discipline;
- operational-learning promotion/expiry lifecycle;
- helper live-but-no-progress signals;
- explainable waits;
- worktree isolation;
- deterministic `maps flow` commands;
- review evidence freshness/artifact binding;
- semantic retrieval only if frozen evaluation proves value;
- controlled harness refinement only after outcome-linked history exists;
- scoped delegated halt authority only if a concrete need appears.

This established another design rule:

> preserve a strong idea when prerequisites are missing; do not weaken it into premature machinery merely to say it exists.

---

# 5. The Prime Agent question

The operator then asked whether the “Prime Agent harness” had been finished.

The answer was: **not as a standalone Prime system**.

A large part of Prime's value had already been absorbed into MAPS Lean:

- durable work/task state;
- claims/leases;
- explicit policy/authority;
- provider-neutral routing/capability envelopes;
- RnS recovery;
- bounded helpers;
- immutable run/context binding;
- trace/history;
- outcomes;
- status.

The remaining useful Prime ideas were mostly about the **harness around the agent**, not about a special Prime agent or daemon.

The operator then asked for a roadmap to bring the most useful Prime functions into MAPS.

---

# 6. Prime roadmap: from “Prime system” to lifecycle guarantees

The first Prime roadmap was intentionally short, but the operator clarified that roadmaps should be the opposite of brief.

The roadmap was then rewritten as a full implementation program at:

`work/roadmaps/prime-agent-capability-roadmap.md`

The central reframing became:

> **Prime-style lifecycle guarantees implemented as narrow mechanisms around MAPS's existing canonical authorities.**

Not:

> rebuild Prime as a second orchestrator.

The Prime roadmap's critical path became roughly:

```text
0. review/stabilize current Lean foundation
1. provider-neutral Harness API
2. execution/session/helper lineage
3. review/evidence revision binding
4. deterministic lifecycle flows
5. capability/skill composition where useful
6. controlled operational learning
7. measured harness evaluation/refinement
```

Parallel/evidence-gated tracks included:

- worktree isolation when concurrent writable execution justifies it;
- task-scoped persistent helper continuity;
- advisory no-progress detection;
- environment/snapshot improvements when needed.

The roadmap explicitly rejected by default:

- persistent `mapd` supervisor daemon;
- second task/session authority database;
- fixed permanent agent roster;
- persona-heavy specialists;
- always-on autonomous self-refinement;
- giant knowledge graph/library;
- semantic retrieval by default;
- universal microVM/container-per-worker absent a threat-model need.

It also made an explicit decision about persistent “goals”: MAPS task outcomes, projects and dependencies already provide most of that value. A separate Mission object is evidence-gated and, if ever created, must group intent rather than become execution authority.

---

# 7. Broader research: look beyond Prime for hard-won mechanisms

Before implementing the Prime roadmap, the operator asked to research more systems/skills/mechanisms that others had already honed and that might be important for MAPS.

The research deliberately became a **capability-mining exercise**, not a framework comparison.

Primary sources and systems sampled included:

- Claude Code / Claude Agent SDK;
- GitHub Copilot coding agent / CLI;
- OpenAI Agents SDK;
- OpenHands;
- SWE-agent;
- aider;
- Devin;
- Kiro;
- goose;
- LangGraph;
- Temporal durable-execution concepts;
- Agent Skills open specification;
- OpenTelemetry semantic conventions;
- OWASP Agentic Security Initiative.

Research was preserved at:

`work/research/agent-harness-patterns-scan-2026-08.md`

The main convergence was striking:

> mature systems tend to improve agents less by adding more autonomous roles and more by improving deterministic harness mechanics, interfaces, environments, procedural packaging, evidence, and security.

The strongest recovered mechanisms included:

1. deterministic lifecycle hooks/interceptors;
2. portable progressive Skills;
3. environment blueprints/reproducibility;
4. deliberately designed Agent-Computer Interfaces (ACI);
5. complete trajectories/replayable run records;
6. immediate deterministic validation around mutations;
7. separation of authority, facts, procedures, flows, tools and examples;
8. dynamic capability/tool loading rather than giant tool menus;
9. standardized observability/correlation IDs;
10. explicit agentic threat modeling;
11. time-travel/fork debugging for durable workflows;
12. supply-chain governance for Skills/tool bundles.

---

# 8. A new mechanism hierarchy emerged

The external research reinforced and sharpened an important architectural principle:

```text
must always happen
→ hook / invariant / validator

reusable procedure
→ Skill

concrete operation
→ tool / script

stable repeated sequence
→ deterministic flow

specific facts/evidence
→ context / source

judgment/exploration
→ agent / helper

high-impact permission
→ policy / operator

future improvement
→ outcome → evaluation → reviewed proposal
```

This became the answer to a recurring design problem:

> do not create another agent when a deterministic mechanism, reusable procedure, tool, or policy boundary can solve the problem more reliably.

This also confirmed the operator's earlier skepticism toward persona-heavy “expert agent” collections. Reusable expertise should generally be packaged as Skills/procedures/capabilities, not as roleplay identities.

---

# 9. Five external-capability workstreams

The research suggested five coherent implementation areas rather than dozens of unrelated features.

The operator asked for a roadmap for each area so they could be added to the system.

The result is:

`work/roadmaps/agent-harness-capabilities/`

with five detailed roadmaps.

## 9.1 Harness Mechanics

`01-harness-mechanics.md`

Focus:

- typed provider-neutral Harness API;
- deterministic hooks/interceptors;
- normalized operation-result/ACI semantics;
- stable run/session/operation lineage;
- immediate validation around mutations;
- portable Run Records/trajectory foundations.

Key separation:

```text
Harness knows HOW.
Task/policy/authority decides WHETHER.
```

## 9.2 Procedural Knowledge & Skills

`02-procedural-knowledge-and-skills.md`

Focus:

- Agent Skills format compatibility;
- progressive disclosure;
- Skill routing quality;
- provenance/trust/lifecycle;
- Skill linting and behavioral evaluation;
- Capability Packs later;
- explicit separation between authority, fact, task context, procedure, flow, tool and example.

The system should not treat every piece of durable context as “memory.”

## 9.3 Environment & Reproducibility

`03-environment-and-reproducibility.md`

Focus:

- `EnvironmentSpec`;
- observed environment fingerprints;
- run-to-environment binding;
- drift/compatibility classification;
- worktree integration;
- harness/compute separation;
- snapshots/rehydration only when justified.

The main insight is that a task/context hash is not enough to reproduce a run if the environment silently changed.

## 9.4 Agentic Security

`04-agentic-security.md`

Focus:

- prompt/goal hijacking;
- tool misuse;
- excessive privilege;
- identity confusion;
- Skill/MCP/tool supply-chain compromise;
- memory/context poisoning;
- stale-session/recovery abuse;
- inter-agent trust;
- cascading failures;
- human-approval manipulation;
- adversarial regression corpus;
- future credential brokering.

Core rule:

> untrusted content may influence reasoning, but only canonical MAPS authority may authorize consequential action.

## 9.5 Learning & Evaluation

`05-learning-and-evaluation.md`

Focus:

- portable run records;
- incident classification;
- frozen regression cases;
- three-layer evaluation;
- Skill/ACI/environment/harness experiments;
- outcome-linked metrics;
- controlled operational learning;
- proposal-only harness refinement.

The deliberate boundary is:

```text
measure
→ compare
→ propose
→ review
→ promote if approved
```

not autonomous self-modification.

---

# 10. Five experiments moved from research notes into formal roadmaps

The conversation identified five experiments that should produce evidence before committing to deeper architecture.

## EXP-A — Skill selection

Test Skill routing with:

- exact matches;
- paraphrases;
- vocabulary shifts;
- hard negatives;
- overlapping Skills;
- no-Skill cases.

## EXP-B — Hooks

Compare agents with and without deterministic scope/validation/telemetry hooks.

Measure escaped errors, false blocking, model calls, operator intervention, and runtime overhead.

## EXP-C — ACI quality

Compare raw/unbounded shell/file output against structured bounded operation results.

Measure repeated calls, false assumptions, context use, and correctness.

## EXP-D — EnvironmentSpec reproducibility

Compare ad-hoc environment state against explicit EnvironmentSpec execution/recovery.

Measure setup failure, reproducibility, test disagreement, and recovery success.

## EXP-E — malicious/untrusted Skills

Red-team Skills that request excessive access, hide scripts, claim authority, poison references, or change behavior after update.

The result should inform Skill trust/governance before importing executable third-party capabilities broadly.

---

# 11. Current implementation-wave sequence

The roadmap set converged on the following implementation sequence.

## Wave 0 — stabilize existing draft foundation

PR #19 remains draft pending independent review.

Future work should not treat draft behavior as settled `main` authority.

## Wave 1 — mechanical foundations

- normalized operation results;
- Harness API;
- Hook framework;
- stable session/run correlation;
- agentic threat model;
- adversarial tests against the current system.

## Wave 2 — Skills and reproducibility

- Agent Skills compatibility;
- Skill provenance/linting;
- progressive disclosure;
- EnvironmentSpec;
- environment fingerprints;
- immediate post-mutation validation.

## Wave 3 — complete evidence

- fuller session/helper/recovery lineage;
- portable Run Records;
- explainable waits;
- recovery/environment compatibility;
- Skill behavior evaluation;
- quarantine path for imported capabilities.

## Wave 4 — scaling features, only when triggered

- worktree isolation;
- persistent task-scoped helper continuity;
- snapshots;
- credential broker;
- Capability Packs;
- limited time-travel/fork debugging.

## Wave 5 — learning/refinement

- frozen incident corpus;
- three-layer evaluation;
- operational learning;
- current-vs-candidate harness comparisons;
- reviewed refinement proposals.

---

# 12. Major themes that should survive future refactors

The conversation repeatedly converged on the following themes.

## 12.1 Better harness, not more agents

MAPS should become better at:

- memory/evidence;
- context selection;
- deterministic procedures;
- reproducibility;
- visibility;
- authority boundaries;
- safe recovery;
- evaluation.

It should not respond to every gap by adding another permanent autonomous role.

## 12.2 One fact, one authority

Derived views and historical notes are useful only if they point back to authoritative evidence.

Do not create parallel mutable copies merely because a subsystem wants convenient access.

## 12.3 Citation is not authority

A statement becoming frequently quoted does not promote it into policy.

The same applies to retrieved memory, Skill instructions, old task notes, and agent messages.

## 12.4 Durable state requires lifecycle

If a new durable object is introduced, define:

- creation;
- authority/provenance;
- mutation/correction;
- supersession;
- retirement;
- recovery semantics;
- who may perform each transition.

## 12.5 Review evidence has a revision boundary

Consequential review must eventually bind to the exact artifact/revision/state being approved or re-derive critical properties at review time.

## 12.6 Security tests should prove behavior

Do not assert that source code merely contains a particular phrase. Exercise the property and show that unsafe behavior is actually denied.

## 12.7 Bounded audits beat permanent process-police agents

Discovery, process adherence, operator-friction analysis, and similar functions are useful when scoped to a phase/closeout/evaluation.

They should not automatically become always-on agents.

## 12.8 Unknown should remain unknown

When session state, lineage, evidence, environment compatibility, or authority cannot be proved, represent `UNKNOWN` rather than inferring from convenience.

## 12.9 Capability is not permission

A worker/tool/Skill/environment may technically support an operation without being authorized to use it in the current task.

## 12.10 Self-improvement is last

MAPS should first become observable, reproducible, attributable, and outcome-linked.

Only then is it meaningful to evaluate and propose harness changes.

---

# 13. What future agents should not infer from this history

Do not infer that every roadmap item must be implemented.

Do not infer that a research finding is active policy.

Do not infer that an old Prime idea remains desirable merely because it appears in the history.

Do not infer that a draft PR is merged/current `main` behavior.

Do not infer that a mechanism described here can override current `AGENTS.md`, task state, policy, or operator decisions.

The purpose of this document is to preserve **design intent and reasoning continuity** so future agents can avoid rediscovering the same lessons or accidentally reviving rejected complexity.
