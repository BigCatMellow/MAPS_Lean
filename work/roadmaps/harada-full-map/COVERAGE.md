# Coverage: every historical milestone and master capability

- **Role:** crosswalk / evidence overlay, **not** the source of live state or permission
- **Parent:** [MAPS_L full Harada goal map](README.md) · [Method](METHOD.md)
- **Evidence:** [master roadmap](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) (35 §6 areas), [capability checklist](../CAPABILITY_CHECKLIST.md) (45 rows), main SHA `69879cd0375f687c1df753fb5a4b83dda76b562e`, last checked 2026-10-20
- **Important:** mapping to a goal condition does **not** mark a code feature present, adopted or authorized. Dated DONE status records a completed *source checklist exit gate*, which may be narrower than a full end-to-end proof.

## Summary of existing 45 checklist classifications

- **DONE: 29**
- **IN PROGRESS: 6**
- **NOT STARTED: 10**

**Do not infer overall MAPS_L completion percentage** from these counts. Conditional tracks can remain NOT STARTED without blocking a valid outcome; several DONE primitives still need integrated proof.

## Source milestone → stable success-condition ID

| Source milestone | Source classification | Harada condition(s) |
| --- | --- | --- |
| [H1 — Result envelope and state vocabulary](../CAPABILITY_CHECKLIST.md) | DONE | H03.1 |
| [H2 — Harness interface + one adapter](../CAPABILITY_CHECKLIST.md) | DONE | H03.2 |
| [H3 — Hook registry](../CAPABILITY_CHECKLIST.md) | DONE | H03.3 |
| [H4 — Immediate validation hooks](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H03.3 |
| [H5 — Remaining adapters + contract suite](../CAPABILITY_CHECKLIST.md) | DONE | H03.2 |
| [H6 — Lineage/trace integration](../CAPABILITY_CHECKLIST.md) | DONE | H04.2 + H07.5 |
| [S1 — Information classification](../CAPABILITY_CHECKLIST.md) | DONE | H05.1 |
| [S2 — Skills format support](../CAPABILITY_CHECKLIST.md) | DONE | H05.2 |
| [S3 — Catalog + provenance](../CAPABILITY_CHECKLIST.md) | DONE | H05.2 |
| [S4 — Routing evaluation](../CAPABILITY_CHECKLIST.md) | DONE | H05.4 |
| [S5 — Quality/security gate](../CAPABILITY_CHECKLIST.md) | DONE | H05.2 + H06.4 |
| [S6 — Context Builder integration](../CAPABILITY_CHECKLIST.md) | DONE | H05.3 |
| [S7 — Capability Packs experiment](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H05.6 |
| [E1 — EnvironmentSpec schema](../CAPABILITY_CHECKLIST.md) | DONE | H04.1 |
| [E2 — Fingerprint + compatibility](../CAPABILITY_CHECKLIST.md) | DONE | H04.1 |
| [E3 — Run binding](../CAPABILITY_CHECKLIST.md) | DONE | H04.2 |
| [E4 — Validation tiers](../CAPABILITY_CHECKLIST.md) | DONE | H03.3 |
| [E5 — Recovery compatibility](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H04.3 |
| [E6 — Worktree isolation](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H04.4 |
| [E7 — Snapshot/rehydration experiment](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H04.6 |
| [SEC1 — Threat model + trust taxonomy](../CAPABILITY_CHECKLIST.md) | DONE | H06.1 |
| [SEC2 — Current-system adversarial baseline](../CAPABILITY_CHECKLIST.md) | DONE | H06.8 |
| [SEC3 — Security hooks](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H06.3 |
| [SEC4 — Skill/tool supply-chain controls](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H06.4 |
| [SEC5 — Memory/learning security](../CAPABILITY_CHECKLIST.md) | DONE | H06.5 |
| [SEC6 — Credential broker experiment](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H06.6 |
| [SEC7 — Ongoing incident corpus](../CAPABILITY_CHECKLIST.md) | DONE | H06.8 |
| [L1 — Run Record v1](../CAPABILITY_CHECKLIST.md) | DONE | H09.1 + H07.5 |
| [L2 — Incident taxonomy + case format](../CAPABILITY_CHECKLIST.md) | DONE | H09.1 |
| [L3 — Three-layer eval harness](../CAPABILITY_CHECKLIST.md) | DONE | H09.3 |
| [L4 — Research experiments A–E](../CAPABILITY_CHECKLIST.md) | IN PROGRESS | H09.7 |
| [L5 — Operational-learning lifecycle](../CAPABILITY_CHECKLIST.md) | DONE | H09.5 |
| [L6 — Harness configuration identity](../CAPABILITY_CHECKLIST.md) | DONE | H09.2 |
| [L7 — Comparative harness evaluation](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H09.3 |
| [L8 — Proposal-only refinement workflow](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H09.6 |
| [L9 — Fork/time-travel experiment](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H09.7 |
| [D0 — Portability audit](../CAPABILITY_CHECKLIST.md) | DONE | H08.2 |
| [D1 — Installer targeting design](../CAPABILITY_CHECKLIST.md) | DONE | H08.2 |
| [D2a — File-convention shape design](../CAPABILITY_CHECKLIST.md) | DONE | H08.2 |
| [D2b — Sibling-clone adapter design](../CAPABILITY_CHECKLIST.md) | DONE | H08.2 |
| [D2c — First external pilot selection plan](../CAPABILITY_CHECKLIST.md) | DONE | H08.3 |
| [D3 — First real external pilot](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H08.3 |
| [D4 — Stack-specific onboarding packs](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H08.5 |
| [D5 — Cross-project review/CI portability](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H08.5 |
| [D6 — Multi-project/fleet management](../CAPABILITY_CHECKLIST.md) | NOT STARTED | H08.6 |

**Known important discrepancies:** **H4** is not fully promoted merely because quick pre-resume validation has an opt-in enforcing path; **E5** is documented as environment advice without the complete incompatible-resume blocking property; **E6/SEC3/SEC4** have real partial guards but not uniform cross-path proof; **L6** is recorded DONE at the primitive/hash level while the same checklist says real run-manifest configuration identity is not consistently persisted, so **L7** remains NOT STARTED. Preserve all distinctions until tested against live code.

## Every master roadmap capability (§6.1–§6.35)

The 2026-08-15 master inventory remains evidence and technical background. Every named capability below is routed to a goal owner; **this table does not make all 35 required for v1**.

| Original master capability | New goal owner |
| --- | --- |
| [§6.1 — Task truth, ownership and authority](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#61-task-truth-ownership-and-authority) | H01 + H02 |
| [§6.2 — Provider-neutral Harness API](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#62-provider-neutral-harness-api) | H03.2 |
| [§6.3 — Normalized Agent-Computer Interface results](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#63-normalized-agent-computer-interface-results) | H03.1 |
| [§6.4 — Deterministic Hooks / Interceptors](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#64-deterministic-hooks-interceptors) | H03.3 + H06.3 |
| [§6.5 — Immediate deterministic validation](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#65-immediate-deterministic-validation) | H03.3 |
| [§6.6 — Explicit run/session/helper/recovery lineage](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#66-explicit-runsessionhelperrecovery-lineage) | H04.2 + H07.5 |
| [§6.7 — Explainable waits](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#67-explainable-waits) | H02.3 |
| [§6.8 — Reusable Agent Skills](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#68-reusable-agent-skills) | H05.2 |
| [§6.9 — Skill routing and progressive disclosure](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#69-skill-routing-and-progressive-disclosure) | H05.4 |
| [§6.10 — Skill provenance, trust and quarantine](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#610-skill-provenance-trust-and-quarantine) | H05.2 + H06.4 |
| [§6.11 — Context budgets / progressive context](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#611-context-budgets-progressive-context) | H05.3 |
| [§6.12 — Capability Packs](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#612-capability-packs) | H05.6 |
| [§6.13 — EnvironmentSpec](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#613-environmentspec) | H04.1 |
| [§6.14 — EnvironmentFingerprint and compatibility](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#614-environmentfingerprint-and-compatibility) | H04.1 + H04.3 |
| [§6.15 — Harness / compute separation](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#615-harness-compute-separation) | H03.6 + H04.1 |
| [§6.16 — Git worktree isolation](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#616-git-worktree-isolation) | H04.4 |
| [§6.17 — Sandboxes / snapshots / rehydration](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#617-sandboxes-snapshots-rehydration) | H04.6 |
| [§6.18 — Revision-bound review/evidence](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#618-revision-bound-reviewevidence) | H07.3 + H07.4 |
| [§6.19 — Task-scoped helper continuity](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#619-task-scoped-helper-continuity) | H02.4 + H04.5 |
| [§6.20 — Advisory NO_PROGRESS detection](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#620-advisory-noprogress-detection) | H02.5 |
| [§6.21 — Deterministic `maps flow` lifecycle operations](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#621-deterministic-maps-flow-lifecycle-operations) | H02.6 |
| [§6.22 — Memory trust classes](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#622-memory-trust-classes) | H05.1 + H06.5 |
| [§6.23 — Agentic threat model and adversarial regression corpus](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#623-agentic-threat-model-and-adversarial-regression-corpus) | H06.1 + H06.8 |
| [§6.24 — Least-privilege capability intersection](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#624-least-privilege-capability-intersection) | H06.2 |
| [§6.25 — Credential broker](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#625-credential-broker) | H06.6 |
| [§6.26 — Portable Run Records / trajectories](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#626-portable-run-records-trajectories) | H09.1 |
| [§6.27 — Outcome-linked incident taxonomy](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#627-outcome-linked-incident-taxonomy) | H09.4 |
| [§6.28 — Frozen regression corpus](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#628-frozen-regression-corpus) | H09.4 |
| [§6.29 — Three-layer evaluation](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#629-three-layer-evaluation) | H09.3 |
| [§6.30 — Operational learning lifecycle](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#630-operational-learning-lifecycle) | H09.5 |
| [§6.31 — Controlled harness refinement](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#631-controlled-harness-refinement) | H09.6 |
| [§6.32 — Time-travel / fork debugging](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#632-time-travel-fork-debugging) | H09.7 |
| [§6.33 — Semantic retrieval / query expansion](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#633-semantic-retrieval-query-expansion) | H05.5 |
| [§6.34 — Mission / multi-task goal object](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#634-mission-multi-task-goal-object) | H01.6 |
| [§6.35 — Portable deployment to external projects](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md#635-portable-deployment-to-external-projects) | H08.2 + H08.3 |

## Coverage of important sources not given their own checklist milestone

- [Operator Intent Compiler planning](../operator-intent-compiler.md) → **H01.1 / H01.3 / H01.4**, optional automation after comparison, never additional authority.
- Project Bootstrap, AGI readiness, canonical dependencies, LangGraph/hcom and orchestration roles → **H01 / H02 / H07**.
- Portfolio stabilization / Pilot THINK + PLAN experimental evidence → **H01.4 / H09.3 / [DEPENDENCIES](DEPENDENCIES.md)**; not MAPS_L runtime permission.
- Provider-neutral DecisionBroker or other new decision seams → H02/H03 only if independently justified and compatible; a pending PR is not a mandatory success condition.
- Historical legacy corpus remains intentionally retained; no deletion goal is generated by this revision.

## Proof standards

1. Source classification (e.g. DONE) is copied only as a **dated claim**.
2. A Harada condition completes only when its observable acceptance evidence holds in the intended operational context.
3. A real target, environment, independent reviewer and operator authority cannot be filled in by a speculative planning file.
4. If an already-present mechanism is adequate, record **NO WORK / reuse**. If an idea is optional and its trigger is absent, record **TRIGGERED / PARKED**; do not fabricate implementation work to fill the branch.
