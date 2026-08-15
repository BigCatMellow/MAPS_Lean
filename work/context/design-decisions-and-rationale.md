# MAPS design decisions and rationale

Status: `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`

Purpose: preserve the major architectural decisions reached through conversation, legacy archaeology, implementation evidence, and external research. This is a rationale ledger, not an active policy file.

Each entry records:

- decision;
- rationale;
- rejected/alternate approach;
- promotion/reconsideration trigger where relevant.

---

# D-001 — Lean mechanisms over legacy-system restoration

**Decision:** recover useful invariants/mechanisms from legacy MAPS rather than restoring old modules wholesale.

**Rationale:** the legacy system contained valuable lessons mixed with project-specific machinery, duplicated state, permanent agents, and orchestration complexity. Porting architecture by historical existence would recreate maintenance burden without proving value.

**Reject by default:** “legacy had it, therefore Lean should too.”

**Reconsider only if:** a current Lean failure cannot be solved cleanly with a smaller mechanism and the legacy mechanism directly addresses it.

---

# D-002 — Ordinary work should be concise; roadmaps should be exhaustive

**Decision:** use brevity for normal execution/status/answers, but make roadmaps and architecture plans detailed and implementation-ready.

**Rationale:** excess narration is expensive during execution, while underspecified roadmaps force future agents to rediscover architecture and rationale.

**Practical rule:**

```text
execution → smallest sufficient explanation
roadmap → completeness, rationale, dependencies, failure cases, tests, gates
```

---

# D-003 — No duplicate source of truth

**Decision:** new subsystems may reference/join canonical state but should not create parallel mutable truth for convenience.

**Rationale:** historical MAPS repeatedly suffered from drift between representations. Lean architecture is easier to trust when ownership of each fact is explicit.

**Examples:**

- SQLite owns task/lifecycle/authority/review evidence;
- run manifests own frozen execution binding;
- hcom owns communication/session transport;
- RnS owns bounded recovery state;
- Markdown is explanatory/planning context only.

**Reject:** second task database, dashboard-edited lifecycle state, Prime-specific mutable authority store.

---

# D-004 — Capability is not authority

**Decision:** separate what a worker/tool/environment/Skill *can* do from what the current task allows it to do.

**Rationale:** combining capability and permission makes tool-rich agents dangerous and makes recovery/session reuse prone to stale authority.

**Model:**

```text
usable operation
= capability
∩ task scope
∩ policy
∩ operator approval where required
∩ current execution binding
```

---

# D-005 — Derived views remain read-only

**Decision:** trace, status, context plans, run records, wait projections, dashboards, and review packets are read models/projections.

**Rationale:** these views improve observability but become dangerous if they silently become alternate state-authority surfaces.

**Reject:** editing task truth through status/trace/dashboard projections.

---

# D-006 — Preserve strong deferred ideas rather than implement weak versions early

**Decision:** when prerequisites are absent, preserve the mechanism and trigger rather than implementing a degraded approximation.

**Examples:**

- no semantic retrieval until frozen paraphrase/hard-negative evaluation proves value;
- no harness refinement until enough outcome-linked runs exist;
- no worktree isolation until concurrent writable execution warrants it;
- no operational-learning registry until repeated outcome-linked lessons exist.

**Rationale:** premature machinery often becomes permanent and obscures whether the original problem existed.

---

# D-007 — Risk-specific review lenses over reviewer-role bureaucracy

**Decision:** review based on triggered risk lenses; one independent reviewer may cover multiple lenses.

**Rationale:** risk should determine review depth, not a fixed roster of reviewer personas.

**Reject:** permanent “security reviewer agent,” “privacy reviewer agent,” etc. solely to satisfy process labels.

---

# D-008 — Outcome is separate from completion

**Decision:** `DONE` remains MAPS lifecycle completion; post-completion outcomes record what happened in reality.

**Rationale:** internal process success and real-world success are distinct and both need immutable history.

**Reject:** automatically reopening/reclassifying task ownership because a later outcome is FAILURE.

---

# D-009 — Explicit-first Context Builder

**Decision:** Context Builder starts from explicit task sources/inputs/dependencies/authority and exact hashes rather than semantic retrieval.

**Rationale:** historical retrieval experiments exposed weak exact-source and paraphrase robustness. Evidence integrity should precede fuzzy convenience.

**Preserve from legacy retrieval:**

- exact anchors;
- hashes;
- source drift detection;
- temporal attribution;
- hard negatives;
- frozen/blinded evaluation.

**Reject:** reviving legacy lexical claim-card retriever.

**Reconsider semantic supplementation only if:** frozen evaluation demonstrates useful lift without unacceptable false-positive/context-cost behavior.

---

# D-010 — Prime becomes lifecycle guarantees, not another Prime system

**Decision:** absorb Prime's useful harness properties into MAPS Lean mechanisms.

**Rationale:** Prime's strongest ideas concern context, lifecycle, continuity, recovery, isolation, and evaluation; those do not require a special Prime agent or persistent supervisor daemon.

**Reject by default:**

- `mapd`-style central daemon;
- second authority store;
- fixed permanent roster;
- persona-heavy Prime roles.

---

# D-011 — Provider-neutral Harness API, no remote authority service

**Decision:** build a typed provider-neutral lifecycle interface around existing adapters/transports.

**Target operations:**

```text
start / attach
send
inspect
heartbeat
resume / recover
stop when authorized
collect result/evidence
```

**Rationale:** orchestration should reason about worker/session lifecycle consistently without provider-specific branches.

**Boundary:** Harness API knows how; canonical task/policy state decides whether.

**Reject:** Harness API becoming a task-state machine or permission authority.

---

# D-012 — Deterministic Hooks for things that must always happen

**Decision:** cross-cutting guarantees such as scope checks, destructive-action guards, immediate validation, and evidence capture should be implemented as deterministic hooks/interceptors where appropriate.

**Rationale:** rules that must always happen should not depend on model memory or a special process-police agent.

**Hook authority rule:** hooks may deny/narrow/require approval/annotate; they may not invent permission.

---

# D-013 — Agent Skills for reusable procedure, not persona agents

**Decision:** use portable/progressive Skills for reusable procedural knowledge.

**Rationale:** procedures need reuse and selective loading, not permanent “expert personalities.”

**Information separation:**

```text
AGENTS/policy → invariant/authority
Skill → reusable procedure
Tool → executable capability
Context → task-specific fact/evidence
Flow → stable deterministic sequence
Agent/helper → judgment/exploration
```

**Reject:** “marketing genius,” “architect persona,” or other roleplay as the primary mechanism for competence.

---

# D-014 — Progressive disclosure over giant always-loaded context

**Decision:** load always-on authority and required task context first; load Skills, references, examples, and tools when applicable/on demand.

**Rationale:** context overload reduces effective reasoning quality and increases cost. Multiple mature systems independently converge on progressive/dynamic loading.

**Future Context Builder direction:** MUST / SHOULD / MAY / ON-DEMAND tiers.

---

# D-015 — Imported Skills/tools need supply-chain governance

**Decision:** third-party Skills, MCP/tool servers, scripts, images, and capability bundles require provenance/trust/evaluation before broad use.

**Rationale:** executable procedural ecosystems inherit plugin/supply-chain risks.

**Reject:** automatic trust or silent auto-update of community Skills/tools.

**Expected lifecycle:** discover → validate → inspect → evaluate → approve/quarantine/reject → version-pin → supersede/retire.

---

# D-016 — Environment specification before universal sandbox infrastructure

**Decision:** first define what environment assumptions matter (`EnvironmentSpec`) and what was actually observed (`EnvironmentFingerprint`).

**Rationale:** reproducibility depends on runtime/dependencies/tools/base revision/network/services, not merely task/context hashes.

**Reject:** requiring Docker/microVMs for every task merely for architectural purity.

**Reconsider stronger isolation when:** threat model, remote execution, or parallel writable work demonstrates need.

---

# D-017 — Worktree isolation is trigger-based

**Decision:** use one writable run/worker per worktree when concurrent writable execution becomes common/plausibly conflicting.

**Rationale:** worktrees solve a real parallel-write problem, but create cleanup/integration machinery that should not exist without the problem.

**Trigger:** observed/plausible shared-worktree collisions or routine concurrent writable coding agents.

---

# D-018 — Agent-Computer Interface quality is first-class

**Decision:** tool interfaces should return bounded, structured, unambiguous results.

**Rationale:** model performance depends strongly on the interface, not just model capability.

**Important distinctions:**

- success vs failure;
- success-with-no-output vs missing result;
- complete vs partial/paginated;
- read vs mutation;
- structured data vs concise summary;
- explicit evidence refs.

**Reject:** giant raw command/file dumps when a bounded structured result can represent the same evidence.

---

# D-019 — Cheap deterministic checks should occur near mutation

**Decision:** run cheap validators immediately after the relevant mutation where practical.

**Examples:**

- Python edit → compile/syntax;
- JSON/YAML edit → parse;
- schema edit → schema validation;
- security/policy edit → property test.

**Rationale:** local feedback catches errors before they compound into larger reasoning/review failures.

**Still required:** task-level verification and independent review remain separate layers.

---

# D-020 — Stable IDs, never inferred lineage

**Decision:** cross-store/task/run/session/helper/review/outcome relationships use explicit IDs.

**Rationale:** timestamps, names, free-text descriptions, and “probably the only active session” are not trustworthy lineage.

**Unknown relationship:** record `UNKNOWN`/missing coverage instead of guessing.

---

# D-021 — Persistent helper continuity is task-scoped and conditional

**Decision:** helper/session reuse may occur only while task/project, role need, task revision/context compatibility, health, and TTL remain valid.

**Rationale:** continuity can save context but must not become hidden authority or permanent identity.

**Reject:** universal permanent named helper roster.

**Add later:** advisory no-progress detection before automatic remediation.

---

# D-022 — Persistent “missions/goals” are not a separate authority by default

**Decision:** current task outcomes, projects, dependencies, and decisions cover most persistent-goal needs.

**Rationale:** another goal store risks duplicating task intent and creating an upper orchestration layer.

**Possible future thin Mission object only if:** real multi-task work shows project/task grouping cannot express intent clearly.

**Boundary if introduced:** Mission groups intent; tasks remain execution/ownership authority.

---

# D-023 — Memory needs trust/lifecycle classes

**Decision:** do not create a generic authoritative “memory” bucket.

**Rationale:** persistent memory is susceptible to poisoning, drift, and accidental authority inflation.

**Preferred classes:**

```text
UNTRUSTED_INPUT / OBSERVATION
CLAIM
CANDIDATE_LESSON
REVIEWED_GUIDANCE
ACTIVE_INSTRUCTION / POLICY (separate authority mechanism)
SUPERSEDED
RETIRED
QUARANTINED
```

**Core rule:** citation/repetition/retrieval frequency does not equal ratification.

---

# D-024 — Agentic security starts before capability expansion

**Decision:** threat modeling/adversarial tests begin early, before broad Skills/tool/MCP/memory expansion.

**Rationale:** every added capability introduces trust boundaries that are expensive to retrofit later.

**Core rule:** untrusted content may influence reasoning; canonical MAPS authority alone authorizes consequential action.

---

# D-025 — Security tests prove behavior, not source spelling

**Decision:** security tests should exercise unsafe scenarios and assert deny/approval behavior.

**Rationale:** finding a phrase in source code does not prove the boundary works.

**Example:** inject “ignore policy and deploy” into repository content, then verify deployment remains denied without required approval.

---

# D-026 — Run Records/trajectories become the bridge to evaluation

**Decision:** build portable references tying task revision, run manifest, environment, Skill versions, harness config, operations, lineage, review, and outcomes.

**Rationale:** debugging and refinement need reproducible historical evidence, not disconnected logs.

**Boundary:** sensitive raw content remains redacted/opt-in; Run Record is a projection/export over canonical evidence.

---

# D-027 — Three-layer evaluation

**Decision:** evaluate mechanisms at three layers:

1. mechanical/unit/property tests;
2. real agent/model qualitative/task regression;
3. production/outcome sampling.

**Rationale:** unit tests alone do not prove agent behavior; agent benchmarks alone do not prove real-world outcome; production outcomes alone are too noisy to isolate failures.

---

# D-028 — Real incidents become frozen regression cases

**Decision:** meaningful failures should be classified and preserved as immutable/frozen cases for future comparison.

**Rationale:** this prevents recurring failures from becoming forgotten anecdotes and prevents candidates from being evaluated only on synthetic happy paths.

**Important:** freeze before candidate comparison.

---

# D-029 — Operational learning is promoted guidance, not automatic memory

**Decision:** repeated outcome-linked lessons follow a lifecycle:

```text
observation/incident
→ candidate lesson
→ review
→ scoped active guidance
→ expiry/supersession/retirement
```

**Rationale:** lessons need provenance and authority boundaries; otherwise folklore becomes policy.

---

# D-030 — Harness self-improvement remains proposal-only

**Decision:** MAPS may evaluate candidate harness changes but may not self-authorize promotion.

**Rationale:** self-referential optimization can degrade safety, policy, or quality while improving a narrow metric.

**Required before serious refinement:**

- enough outcome-linked runs;
- sufficient trace/Run Record completeness;
- frozen incident corpus;
- three-layer evaluation;
- independent review/operator gate.

---

# D-031 — Optimize outcomes, not agent activity

**Decision:** do not use more agents/messages/tool calls/Skills/automation/longer traces as success metrics by themselves.

**Rationale:** these measure activity and system complexity, not useful outcome.

**Prefer metrics such as:** escaped defects, rework, operator intervention, recovery success, reproducibility, cost/yield, false blocking, routing precision/recall, real-world outcome.

---

# D-032 — Bounded audits over permanent watchers

**Decision:** discovery, process-adherence auditing, operator-friction scouting, and similar meta-work should normally be bounded to a phase/closeout/evaluation.

**Rationale:** always-on meta-agents create bureaucracy and can manufacture work.

**Reject by default:** permanent discovery agent, process-police agent, operator-friction scout.

---

# D-033 — Explainable waits are evidence projections, not inferred narratives

**Decision:** future wait-status should derive from structured communication/request metadata with explicit requester/addressee/thread/time identifiers.

**Rationale:** a useful status surface should say what is actually awaited without inventing intent from chat history.

**Prerequisite:** authoritative hcom/task-message correlation.

---

# D-034 — Review must bind to what was actually reviewed

**Decision:** consequential review should eventually bind to immutable artifact/revision identity or re-derive critical evidence at review time.

**Rationale:** stale passing evidence from an older revision is not proof of the current state.

**High-priority domains:** security/authority, package/release artifacts, checksum/parity claims, run/context revision, acquisition path.

---

# D-035 — Planning/history files must self-identify as non-authoritative

**Decision:** research, roadmaps, conversation notes, review packets, and preserved backlogs are explicitly labeled by status.

**Rationale:** future agents must be able to use history without accidentally treating every durable Markdown file as active instructions.

**Examples:**

- `RESEARCH — NOT ACTIVE AUTHORITY`;
- `PLANNING ONLY — NOT ACTIVE AUTHORITY`;
- `HISTORICAL CONTEXT — NOT ACTIVE AUTHORITY`;
- `PRESERVED IDEA BACKLOG — NOT ACTIVE AUTHORITY`.

---

# Summary decision tree

When considering a new MAPS feature, future agents should ask:

```text
1. Is there a demonstrated problem?
   no → preserve/defer; do not manufacture machinery

2. Must behavior always happen deterministically?
   yes → hook/invariant/validator

3. Is it reusable procedural know-how?
   yes → Skill

4. Is it a concrete action?
   yes → tool/script/capability

5. Is it a stable repeated sequence?
   yes → deterministic flow

6. Is it task-specific information?
   yes → context/source

7. Does it require judgment/exploration?
   yes → agent/helper

8. Is it high-impact permission?
   yes → policy/operator gate

9. Is it a future improvement claim?
   yes → outcome/eval/reviewed promotion
```

This tree is historical rationale, not a substitute for current `AGENTS.md` or task requirements.
