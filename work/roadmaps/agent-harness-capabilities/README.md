# MAPS agent-harness capability roadmaps

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: turn the external agent-harness research into implementation-ready MAPS Lean roadmaps. These documents describe how to add the strongest transferable mechanisms without importing another framework's architecture wholesale.

Source research: `work/research/agent-harness-patterns-scan-2026-08.md`

Related master roadmap: `work/roadmaps/prime-agent-capability-roadmap.md`

---

# 1. Roadmap set

This directory contains five coordinated roadmaps.

| Roadmap | Core question | Major mechanisms |
|---|---|---|
| [01 — Harness Mechanics](01-harness-mechanics.md) | How should MAPS control and observe agents deterministically? | typed Harness API, hooks/interceptors, ACI result standard, lifecycle lineage, Run Records, deterministic local verification |
| [02 — Procedural Knowledge & Skills](02-procedural-knowledge-and-skills.md) | How should MAPS package reusable expertise without giant prompts or persona agents? | Agent Skills compatibility, knowledge/procedure separation, progressive disclosure, skill routing/evals, trust/provenance, Capability Packs |
| [03 — Environment & Reproducibility](03-environment-and-reproducibility.md) | How do we make executions reproducible and recoverable across machines/sandboxes? | EnvironmentSpec, environment fingerprints, setup/validation, harness/compute separation, snapshots/rehydration, worktree/sandbox integration |
| [04 — Agentic Security](04-agentic-security.md) | How do we safely expand tools, skills, memory, and autonomy? | threat model, adversarial regression corpus, memory trust classes, skill/MCP supply-chain controls, least privilege, credential brokering, cross-agent trust boundaries |
| [05 — Learning & Evaluation](05-learning-and-evaluation.md) | How does MAPS learn from real runs without self-authorizing changes? | portable trajectories, frozen incident corpus, three-layer evals, skill/ACI/environment evals, outcome-linked metrics, operational learning, controlled harness refinement |

Each roadmap is intentionally detailed. They are planning artifacts, not instructions to implement every feature immediately.

---

# 2. Shared design rules

These rules apply across all five roadmaps.

## 2.1 Existing MAPS authorities remain authoritative

- SQLite remains task/lifecycle/ownership/policy/review/evidence truth.
- immutable run manifests remain execution binding.
- hcom remains communication/session transport.
- LangGraph remains route/checkpoint machinery.
- RnS remains bounded recovery.
- helper state remains helper evidence, not task authority.
- outcomes remain append-only post-completion observations.
- Markdown roadmaps/research/review packets remain non-authoritative.

No roadmap may create a second task state machine simply because its subsystem needs metadata.

## 2.2 Capability does not grant authority

A tool, Skill, hook, session, provider, environment, or capability bundle may describe what can be done. The task/policy/operator path decides what is allowed for a specific run.

## 2.3 Prefer deterministic mechanisms over model memory

Use:

```text
must always happen          → hook / invariant / validator
reusable procedure          → Skill
concrete operation          → tool / script
stable repeated sequence    → deterministic flow
specific facts              → context / source
judgment / exploration      → agent / helper
high-impact permission      → policy / operator
future improvement          → outcome → eval → reviewed proposal
```

Do not create an agent whose only purpose is to remember a deterministic chore.

## 2.4 Derived views do not become truth

Trace, status, context plans, trajectories, lineage diagrams, dashboards, eval reports, and skill catalogs are projections. They must reference canonical evidence rather than silently copying mutable truth.

## 2.5 No self-authorizing improvement

MAPS may measure, evaluate, propose, and compare changes. It may not promote its own policy, authority, safety, routing, or persistent guidance changes without the normal review/decision path.

---

# 3. Shared primitives

The roadmaps should converge on a small number of common concepts rather than inventing subsystem-specific equivalents.

## 3.1 Stable identifiers

At minimum:

```text
task_id
run_id
worker_id
session_id
helper_run_id / child_run_id where appropriate
review_id
outcome_id
skill_id + skill_version/hash
environment_spec_id + hash
operation_id
```

Every cross-store join must use an explicit identifier. Do not infer lineage from timestamps, names, free text, or “probably the only active session.”

## 3.2 Normalized operation result

All harness-facing operations should converge toward a bounded, unambiguous result envelope such as:

```json
{
  "ok": true,
  "code": "NO_MATCHES",
  "summary": "Search completed; no matching files.",
  "data": [],
  "evidence_refs": [],
  "mutated": false,
  "complete": true,
  "next": null
}
```

The exact schema can evolve, but the semantic distinctions should remain:

- success versus failure;
- success-with-no-output versus missing result;
- complete versus paginated/partial;
- read versus mutation;
- concise summary versus structured details;
- evidence references rather than unsupported prose.

## 3.3 Provenance

New durable/portable records should preserve where possible:

```text
producer / actor class
producer identity
source mechanism
created_at
related task/run/session
revision/hash
trust/authority classification
```

Unknown provenance must be represented as `UNKNOWN`, not guessed.

## 3.4 Trust classes

Across Skills, memory, external tool output, imported examples, and learned guidance, use an explicit distinction between:

```text
UNTRUSTED INPUT
OBSERVATION
CANDIDATE
REVIEWED / APPROVED PROCEDURE
ACTIVE GUIDANCE
CANONICAL POLICY / AUTHORITY
SUPERSEDED / RETIRED
```

Frequent retrieval or repeated citation does not increase authority.

---

# 4. Dependency map

The roadmaps are related but should not be implemented as one mega-project.

```text
CURRENT MAPS LEAN FOUNDATION
          │
          ├───────────────────────────────────────┐
          │                                       │
          ▼                                       ▼
01 HARNESS MECHANICS                    04 SECURITY BASELINE
 typed API                               threat model
 ACI result schema                       adversarial cases
 hooks/interceptors                      supply-chain rules
 run/session lineage                     trust classes
          │                                       │
          ├──────────────┬────────────────────────┘
          │              │
          ▼              ▼
02 SKILLS /         03 ENVIRONMENT /
PROCEDURAL KNOWLEDGE REPRODUCIBILITY
 progressive load    EnvironmentSpec
 skill governance    fingerprints
 capability packs    rehydration
          │              │
          └───────┬──────┘
                  ▼
          05 LEARNING / EVAL
          portable Run Records
          frozen incident cases
          outcome-linked evaluation
          controlled refinement
```

Security is cross-cutting and begins early; it is not a final hardening pass.

Learning/evaluation begins with instrumentation early, but **automatic or semi-automatic harness refinement comes last**, after trustworthy trajectories and outcomes exist.

---

# 5. Recommended implementation order

## Wave 0 — Stabilize current foundation

Before building these roadmaps onto runtime behavior:

1. independently review current PR #19;
2. resolve review findings;
3. merge or otherwise establish the accepted baseline;
4. preserve current CI as a required gate;
5. confirm current task/run/policy/trace/outcome invariants.

## Wave 1 — Mechanical foundations

Implement small primitives that benefit almost everything else:

1. normalized operation-result contract;
2. typed provider-neutral Harness API;
3. lifecycle hook/interceptor contract;
4. stable run/session correlation rules;
5. initial OWASP-derived agentic threat model;
6. adversarial tests for current authority boundaries.

## Wave 2 — Reusable knowledge + reproducibility

1. Agent Skills compatibility;
2. Skill metadata/provenance/linting;
3. progressive context loading;
4. EnvironmentSpec v1;
5. run → environment hash binding;
6. local deterministic post-mutation validation hooks.

## Wave 3 — Rich evidence and portability

1. fuller task/run/session/helper/recovery lineage;
2. portable Run Record export;
3. explainable waits;
4. environment compatibility checks for recovery;
5. Skill and Capability Pack behavioral evaluation;
6. third-party skill/tool quarantine workflow.

## Wave 4 — Conditional scaling features

Only after evidence warrants them:

- Git worktree isolation for concurrent writable runs;
- reusable task-scoped helper sessions;
- environment snapshots/rehydration;
- credential broker;
- Capability Packs combining Skill + tools + hooks + environment requirements;
- time-travel/fork debugging for selected stateful flows.

## Wave 5 — Learning and refinement

After enough real outcome-linked runs exist:

1. frozen incident regression corpus;
2. three-layer evaluation harness;
3. skill-selection and ACI eval suites;
4. operational-learning promotion/expiry;
5. candidate harness configuration comparison;
6. proposal-only refinement with independent review/operator approval.

---

# 6. Cross-roadmap acceptance criteria

The program is successful when:

1. agents use a provider-neutral lifecycle interface rather than orchestration code branching by provider;
2. consequential lifecycle events can trigger deterministic guards/validation independent of model memory;
3. tools return bounded, unambiguous structured outcomes;
4. reusable procedures can be loaded on demand without bloating always-active instructions;
5. imported procedures/tools have explicit provenance and trust classification;
6. a run records the task revision, context, environment, worker/session lineage, and relevant operation evidence needed to reproduce or diagnose it;
7. recovery can distinguish compatible from materially changed environments/context;
8. current policy/authority always outranks imported Skill text, memory, tool output, or old lessons;
9. real incidents can become frozen regression cases;
10. proposed harness changes can be compared against the current harness using the same evaluation corpus;
11. no subsystem quietly becomes a new task authority or always-on autonomous supervisor.

---

# 7. Explicit non-goals

Do not use these roadmaps to justify by default:

- a large `mapd` daemon;
- a second task/session authority database;
- permanent named agent personas;
- downloading arbitrary community Skills and trusting them;
- giving every worker every MCP/tool server;
- universal containers/microVMs without a threat-model reason;
- semantic retrieval as the default context mechanism;
- always-on process-police/discovery agents;
- autonomous self-rewriting instructions or policy;
- metrics that reward number of agents, messages, tool calls, or “activity.”

The goal is **more reliable capability**, not a larger orchestration product.
