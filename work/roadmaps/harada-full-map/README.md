# MAPS_L — Full recursive Harada goal roadmap

**Status:** COMPLETE *CANDIDATE REVISION* of the entire MAPS_L capability program; NOT YET APPROVED OR ACTIVE AUTHORITY  
**Evidence checkpoint:** 2026-10-20 · source \`main\` \`69879cd0375f687c1df753fb5a4b83dda76b562e\`  
**Owner of accepted program planning:** [Existing master roadmap](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) until this proposal receives the appropriate review/disposition.  
**Rules:** [AGENTS.md](../../../AGENTS.md) > approved roadmap/task > canonical state/code/tests > dated planning/evidence. New branches authorize no execution, PR merges, cost, or external effects.

## Overall goal (not just the next pilot)

> **MAPS_L is a trustworthy, provider-neutral operating system around capable AI workers:** it turns bounded human objectives into correct work; supplies relevant context, tools and environments; coordinates execution and recovery without losing task truth or authority; independently verifies real outcomes; operates across projects; and improves from evidence without unreviewed self-modification or avoidable complexity.

**Observable full DONE:** all ten properties in the original [master §15](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) (control, context, reproducibility, safety, coordination, evidence, review integrity, learning, human authority and complexity control) are demonstrated in relevant real/end-to-end scenarios, with independently inspectable proof. The original [six scenarios (§16)](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) are retained and revised into [explicit wave-level proof](WAVES.md). One external pilot is a major milestone, **not** the full goal. Nor does DONE mean shipping every speculative capability.

This is a **manual use of Harada-inspired recursive decomposition**. The original Harada Open Window 64 is a fixed brainstorming exercise; unbounded recursion and branch-per-meaningful-file are proposed software-planning extensions, not experimentally validated THINK/PLAN behavior.

## Start at a branch, not the whole roadmap

Every branch link is direct. Read just the node you need, its explicit dependency links and source evidence.

| ID | Necessary success condition | Direct owner |
| --- | --- | --- |
| **H01** | Human intent, bounded scope and useful DONE | [Intent and goal shaping](branches/H01-intent.md) |
| **H02** | Proportional planning, canonical task truth and coordination | [Planning/orchestration](branches/H02-planning-orchestration.md) |
| **H03** | Portable execution, normalized tools and hooks | [Harness and tools](branches/H03-harness.md) |
| **H04** | Compatible environments, recoverable runs and isolation | [Continuity/reproducibility](branches/H04-continuity.md) |
| **H05** | Trustworthy, minimal, useful context and Skills | [Knowledge/Skills/context](branches/H05-knowledge.md) |
| **H06** | Enforced authority, security and supply-chain trust | [Security/policy](branches/H06-security.md) |
| **H07** | Independently reproducible testing, review and evidence | [Verification/review](branches/H07-quality.md) |
| **H08** | Safe adoption in real external projects and usable operation | [Deployment/portability](branches/H08-portability.md) |
| **H09** | Real outcome measurement and evidence-controlled learning | [Evaluation/learning](branches/H09-learning.md) |

### Significant child branches — direct one-hop access

| Logical node(s) | Direct owner | Parent |
| --- | --- | --- |
| **H03.3**, validation timing and actual enforcement | [Immediate deterministic validation](branches/H03.3-validation.md) | H03 |
| **H04.3**, including **H04.3.2.1–H04.3.2.4** | [Safe recovery under changed conditions](branches/H04.3-recovery.md) | H04 |
| **H06.3**, effect-class capability/permission hooks | [Consequential side-effect guards](branches/H06.3-consequential-actions.md) | H06 |
| **H08.3**, including **H08.3.1–H08.3.7** | [First real external-project proof](branches/H08.3-external-v1.md) | H08 |
| **H09.3**, comparator/experiment/learning proof | [Comparative evaluation](branches/H09.3-comparison.md) | H09 |

All smaller child nodes live in their nearest owning branch file. **Logical depth is unlimited; file count and directory depth are not.** Stable IDs survive reprioritization; parent pointers and sibling/other-branch dependencies are direct links, not duplicate mutable copies.

## Read by planning job

| Task | Open this file |
| --- | --- |
| What exactly does *recursive* Harada decomposition mean here? When to split/stop? | [METHOD.md](METHOD.md) |
| Which new condition corresponds to any of the **45 old milestones** or **35 master capabilities**? | [COVERAGE.md](COVERAGE.md) |
| What depends on what; what is optional versus required? | [DEPENDENCIES.md](DEPENDENCIES.md) |
| What is the complete destination and prioritized **next work**? | [WAVES.md](WAVES.md) |
| What might be wrong with this restructuring or with its priorities? | [CHALLENGE.md](CHALLENGE.md) |
| What are the detailed original implementation ideas and acceptance mechanisms? | [Six subsystem roadmaps](../agent-harness-capabilities/README.md) |
| What is actually open/merged/approved *today*? | [Coordination + live GitHub](../../coordination/README.md) |

## Work already present versus actual missing proof

The source checklist records **29 DONE, 6 IN PROGRESS and 10 NOT STARTED** among 45 rows. This is **not** a truthful overall completion percentage. The key near-term uncertainties include actual effect-time validation (H4), environment-compatible recovery (E5), complete worktree enforcement (E6), consequential operation hooks (SEC3), Skill/tool activation trust coverage (SEC4), and real-run harness-config identity despite the L6 primitive marked DONE. A first real external project D3 is still not evidenced; evaluating success after it is also unfinished.

Many of these rows have genuine code/test foundations; the question is whether a specific in-scope **operational property** is really satisfied. Recheck source, tests and actual call sites before generating new work. Conditional extras (packs, snapshots, credential broker, fleet, universal compiler/search/time travel) **do not automatically become required** merely because they appear on the map.

## Roadmap status and promotion boundaries

- This **revises the full program reasoning and proposed sequence**, not \`AGENTS.md\`, existing task truth, live PR status, accepted scope or policy.
- The original 57 KB master and six subsystem design documents remain available and own legacy references / detailed design until the revised planning is reviewed and formally adopted. The linked baseline is **not silently superseded**.
- Review must test **goal coverage, factual gaps, dependency correctness, safety, file navigation and whether the Harada adaptation improves planning**. If a condition is already satisfied or not required, avoid creating implementation work.
- Independent review and operator roadmap disposition are needed before claiming these waves are approved or merged; the present full set is a self-contained **candidate** that can be revised without expanding the user-approved implementation permission envelope.

**Navigation principle:** read \`AGENTS.md\` + the accepted task/roadmap + **one directly relevant goal node**; follow dependency/source links only when the decision demands them. Do not pre-read twenty roadmap files for routine work.
