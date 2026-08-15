# External agent-harness pattern scan — 2026-08

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Purpose: identify mechanisms, practices, and reusable skill patterns that mature agent systems and adjacent reliability/security projects have already refined, then classify which ones MAPS Lean should absorb, experiment with, defer, or reject.

This is not a product feature checklist. The question is:

> What hard-won operating mechanisms have other teams converged on that would materially improve MAPS without recreating their architecture wholesale?

## Research method

Primary sources were preferred: official product/framework documentation, official repositories, standards, and original research papers. Stronger weight is given when multiple independent systems converge on the same mechanism.

Systems/standards sampled:

- Claude Code / Claude Agent SDK
- GitHub Copilot coding agent / CLI
- OpenAI Agents SDK
- OpenHands
- SWE-agent
- aider
- Devin
- Kiro
- goose
- LangGraph
- Temporal durable-execution concepts
- Agent Skills open specification
- OpenTelemetry semantic conventions
- OWASP Agentic Security Initiative

---

# Executive findings

The strongest cross-system convergence is not toward “more autonomous agents.” It is toward **better harness mechanics around agents**:

1. deterministic lifecycle hooks and interception points;
2. progressive, portable skills instead of giant always-loaded prompts;
3. reproducible environment setup and sandbox/snapshot boundaries;
4. deliberately designed agent-computer interfaces rather than raw shell/file access alone;
5. complete trajectories and replayable run configuration;
6. deterministic verification immediately around edits/tool use;
7. clear separation between facts, procedures, tools, and reusable workflows;
8. dynamic tool/capability loading to avoid context overload;
9. standardized observability and correlation identifiers;
10. explicit agentic threat modeling, especially around memory, tools, identity, and supply chain;
11. time-travel/fork debugging for stateful workflows;
12. quality/provenance governance for third-party skills and capability bundles.

The strongest immediate MAPS candidates are **Hooks/Interceptors**, **Agent Skills support + skill governance**, **Environment Blueprints**, **ACI/tool ergonomics**, and **standardized trajectory/telemetry semantics**.

---

# 1. Deterministic lifecycle hooks / interception bus

## What others learned

Claude Code and GitHub Copilot both expose lifecycle hooks around events such as:

- session start / resume;
- prompt submission;
- before tool use;
- after tool use;
- agent/subagent stop;
- errors;
- permission requests.

Claude Code explicitly frames hooks as deterministic control: project rules, validation, logging, and automation should run because the event occurred, not because the model remembered to invoke them.

GitHub Copilot similarly allows pre-tool hooks to approve/deny executions and post-tool hooks to audit results.

## Why this matters for MAPS

MAPS already has policy, authority, review, trace, and event boundaries, but these checks currently live in subsystem-specific code paths. A small common interception contract could make cross-cutting guarantees mechanically consistent.

Candidate events:

```text
run_starting
run_started
before_tool
before_write
before_external_action
before_destructive_action
after_tool
after_write
submission_created
review_starting
review_completing
session_stopping
run_failed
```

Candidate hook outcomes:

```text
ALLOW
DENY(reason)
REQUIRE_APPROVAL(reason)
ANNOTATE(evidence)
```

Important rule:

> A hook may narrow or block authority. A hook may not invent authority that task/policy state did not grant.

## Lean implementation shape

Do **not** create an event-bus service. Start with an in-process deterministic hook registry used by the Harness API / guarded operations.

Likely uses:

- prevent destructive commands without policy approval;
- enforce output/write scope;
- trigger deterministic lint/security checks after edits;
- capture normalized operation telemetry;
- ensure secret scanning before diagnostic persistence;
- attach immutable evidence before review.

## Classification

**P1 — strong adoption candidate.**

This may be more valuable than adding many individual one-off policy checks.

---

# 2. Agent Skills as the portable procedural layer

## What others learned

Claude Code, GitHub Copilot, OpenHands, Kiro, Devin and other tools now support the Agent Skills pattern: a `SKILL.md` plus optional scripts, references, and assets.

The open Agent Skills specification uses **progressive disclosure**:

1. startup: load only skill name/description;
2. activation: load full instructions;
3. execution: load scripts/references/assets only when needed.

This directly addresses context bloat while preserving reusable procedural expertise.

## Why this is distinct from AGENTS.md

MAPS should distinguish:

```text
AGENTS.md
= always-on repository operating contract / invariants

Skill
= reusable procedure or domain method loaded only when applicable

Tool
= executable capability

Context/source
= facts/evidence needed for this task
```

A deployment procedure, migration checklist, incident triage method, database-review method, or release verification procedure belongs in a skill—not permanently in AGENTS.md.

## Important skill-authoring lesson

The skill description is effectively routing metadata. If it poorly describes **what the skill does and when to use it**, agents fail to select it.

Recent empirical work on public `SKILL.md` files found widespread quality defects, especially weak routing metadata, bloated/non-actionable bodies, and poor resource organization. This strongly argues against “download lots of community skills and trust them.”

## MAPS candidate

Support the open Agent Skills directory format, but with a MAPS quality gate:

```text
skill discovery
↓
metadata validation
↓
provenance / trust classification
↓
required tool/capability inspection
↓
static safety checks for scripts
↓
behavioral eval on representative tasks
↓
approved / quarantined / rejected
```

Possible MAPS-specific metadata extension:

```yaml
metadata:
  maps-risk: low|medium|high
  maps-authority: advisory|procedure|guarded-tool
  maps-review: owner|independent
```

Do not make these extensions mandatory until needed; preserve open-standard compatibility.

## Classification

**P1 — strong adoption candidate.**

MAPS should likely treat Skills as the standard packaging format for reusable procedural knowledge.

---

# 3. Separate knowledge, procedure, and workflow-template concepts

## What Devin learned

Devin explicitly separates:

- **Knowledge** — concise contextual facts/tips recalled when relevant;
- **Skills** — repository-scoped reusable procedures;
- **Playbooks** — reusable prompt/workflow templates attached to sessions;
- **Blueprints** — declarative environment setup and reference commands.

This separation is useful because these information types have different lifecycle and loading needs.

## MAPS translation

MAPS currently risks treating too many things as generic “context.” A clearer classification would be:

```text
FACT / KNOWLEDGE
“Service X uses port 8443.”

INVARIANT / AUTHORITY
“Production deploy requires operator approval.”

SKILL / PROCEDURE
“How to perform a safe database migration.”

FLOW / DETERMINISTIC PROCEDURE
“Prepare review → run required checks → claim review.”

TASK CONTEXT
“The specific migration requested for TASK-0042.”
```

This classification should help Context Builder decide **what to load and why**.

## Classification

**P1 design invariant.**

Probably implement through metadata/context classification before inventing another knowledge product.

---

# 4. Environment blueprints and known-good snapshots

## What others learned

Devin treats environment setup as one of the highest-leverage parts of agent performance. Its current model separates declarative environment configuration into initialization, maintenance, and knowledge, then produces a known-good snapshot from which sessions start.

OpenHands similarly treats the sandbox/runtime as a first-class execution environment with controlled providers.

The 2026 OpenAI Agents SDK explicitly separates the agent harness from compute and introduces sandbox workspace manifests, snapshotting, and rehydration.

## Why MAPS should care

A run manifest currently freezes task/context/scope, but not necessarily the complete **execution environment recipe**.

Future problems otherwise include:

- agent A works because a package happened to be installed;
- agent B cannot reproduce the run;
- environment drift is mistaken for model failure;
- recovery resumes in a materially different workspace;
- test results cannot be confidently reproduced.

## Candidate MAPS artifact

A lightweight `EnvironmentSpec` / workspace blueprint:

```text
base environment identifier
repo/base revision
language/runtime versions
deterministic setup command references
dependency lock/checksum references
required tools
network requirements
secret names (never values)
expected validation commands
```

The run manifest can bind to the blueprint hash.

Do not require Docker for every task. The spec should describe the environment independently of whether the implementation is local, worktree, Docker, remote sandbox, etc.

## Classification

**P1/P2 — strong candidate after Harness API lineage.**

The specification is more important initially than building snapshot infrastructure.

---

# 5. Harness/compute separation and sandbox portability

## What others learned

OpenAI’s updated Agents SDK emphasizes separating harness state from compute so:

- credentials do not need to live inside model-controlled execution environments;
- sandbox/container loss does not destroy run state;
- runs can be rehydrated elsewhere;
- subagents can use isolated compute;
- compute can scale independently.

OpenHands likewise recommends Docker sandboxing for isolation, consistency, resource control, and reproducibility.

## MAPS translation

This strongly reinforces the Prime roadmap’s typed Harness API.

The MAPS harness should hold:

- canonical run/session IDs;
- authority references;
- context/environment hashes;
- recovery state;
- evidence lineage.

The execution environment should receive only what it needs.

## Security boundary

Secrets should be brokered narrowly rather than copied wholesale into every agent environment.

Potential future mechanism:

```text
agent requests credential capability
↓
policy checks task authority
↓
credential broker grants task-scoped / time-scoped access
↓
secret value never becomes durable task text
```

## Classification

**P1 architectural invariant; implementation depth depends on threat model.**

No immediate requirement for universal containers or microVMs.

---

# 6. Agent-Computer Interface (ACI) design as a first-class discipline

## What SWE-agent learned

SWE-agent’s central research claim is that agent performance depends strongly on the **interface offered to the model**, not only the model itself.

Their ACI refinements included:

- automatically linting edits and rejecting syntactically invalid changes;
- a bounded/windowed file viewer rather than unconstrained file dumps;
- concise repository search outputs rather than overwhelming snippets;
- explicit output when a command succeeds but prints nothing.

These details sound small, but they improve the information architecture the model reasons over.

## MAPS implication

MAPS should review every tool not only for capability/security, but for **agent usability**:

```text
Does success/failure have an unambiguous structured result?
Is output bounded?
Are identifiers stable?
Can the agent ask for the next page/chunk?
Does the tool distinguish “no result” from “tool failed”?
Does the tool expose enough evidence without flooding context?
Are destructive options separate from safe reads?
```

## Candidate MAPS practice

Create an **ACI quality checklist** for Harness API tools and internal CLI commands.

Potential standard operation envelope:

```json
{
  "ok": true,
  "code": "NO_MATCHES",
  "summary": "Search completed; no matching files.",
  "data": [],
  "evidence_refs": [],
  "next": null
}
```

## Classification

**P1 — highly transferable and cheap.**

MAPS should treat tool-output design as part of agent engineering, not plumbing.

---

# 7. Trajectories as reproducible experimental artifacts

## What SWE-agent learned

SWE-agent writes complete trajectory artifacts containing the run interaction history plus configuration and model/run metadata. It also preserves a configuration that can reproduce the experiment, and trajectories can become demonstrations.

This is stronger than plain logging because it connects:

```text
problem
+ configuration
+ actions
+ observations
+ model statistics
+ result
```

## MAPS translation

Our `trace` and run manifests are moving in this direction, but MAPS should eventually define a portable **Run Record export**:

```text
Task contract revision
Run manifest
EnvironmentSpec
Harness/provider config identifiers
Tool-operation timeline
Session/helper/recovery lineage
Submission/review evidence references
Outcome observations
Cost/token/runtime summary
```

Sensitive raw content should remain opt-in/redacted.

## Why useful

This enables:

- debugging;
- incident reconstruction;
- regression corpus creation;
- comparing harness configurations;
- teaching/evaluating skills;
- reproducing failures.

## Classification

**P1 — strong extension of current trace/outcome work.**

---

# 8. Demonstrations / exemplar trajectories as skills evidence

## What SWE-agent learned

SWE-agent supports using successful trajectories as demonstrations of how to interact with an environment. Their docs explicitly describe replaying/editing trajectory demos.

## MAPS translation

Do not globally stuff demonstrations into every prompt. Instead, a Skill may optionally include a **small validated exemplar** when behavior is hard to convey procedurally.

Candidate structure:

```text
skills/database-migration/
  SKILL.md
  references/
  scripts/
  examples/
    successful-run.yaml
```

Exemplars should be:

- sanitized;
- compact;
- revisioned;
- validated against current tools;
- used only when the skill activates.

## Classification

**P2 experiment candidate.**

Useful for difficult operational skills; dangerous as generic context bloat.

---

# 9. Automatic verification immediately around edits

## What aider and SWE-agent learned

Aider can automatically lint files after edits and optionally run tests after changes, feeding failures back for repair. SWE-agent similarly places syntax validation directly in the edit interface.

This reflects a useful principle:

> Cheap deterministic checks should happen close to the mutation that can violate them.

## MAPS translation

MAPS currently emphasizes final verification/review. We should consider **local mutation checks** that are declared by task/environment/skill:

```text
edit Python file
→ syntax/compile check

edit schema
→ schema validator

edit generated configuration
→ parse validator

change security policy
→ property tests
```

These are not substitutes for task-level tests or independent review.

## Classification

**P1 — adopt selectively through hooks + skills/environment configuration.**

---

# 10. Planner / editor separation when the models or task benefit

## What aider learned

Aider’s architect mode deliberately separates:

1. reasoning about the solution;
2. translating the solution into precise edits.

The models can even differ.

## MAPS interpretation

Do not create permanent “Architect Agent” and “Editor Agent” roles.

But MAPS should support a **two-stage execution strategy** as an optional capability when evidence shows it helps:

```text
plan artifact / proposed patch intent
↓
implementation worker
↓
verification
```

Potential triggers:

- high reasoning complexity;
- model is strong at planning but unreliable at edits;
- broad refactor with narrow allowed-write scope;
- security-sensitive change where intent should be reviewable before mutation.

## Classification

**P2 — strategy, not architecture.**

Evaluate empirically; do not make universal.

---

# 11. Dynamic tool/capability loading (“Powers” pattern)

## What Kiro learned

Kiro’s Powers combine:

- relevant expertise/instructions;
- MCP/tool definitions;
- optional hooks/workflows;

and load them dynamically rather than loading every MCP tool at session start.

Their stated problem is context overload from large numbers of tool definitions.

## MAPS translation

This suggests a concept above a plain Skill:

```text
Capability Pack
= Skill/procedure
+ required tools/adapters
+ optional deterministic hooks
+ compatibility/environment requirements
```

Example:

```text
postgres-migration
  instructions
  postgres MCP/tool adapter
  schema-diff script
  pre-write backup check
  post-write migration validation
```

But MAPS should preserve open Agent Skills compatibility. A Capability Pack could simply *reference* one or more skills/tools rather than inventing a competing format.

## Classification

**P2 — promising after skill support and Harness API.**

Especially useful if MCP/tool catalogs become large.

---

# 12. Time travel, replay, and forked debugging

## What LangGraph learned

LangGraph checkpoints support:

- replay from earlier state;
- fork from an earlier checkpoint with modified state;
- human interrupts and later resume;
- fault recovery from last successful state.

A key implementation lesson is that code before an interrupt can execute again, so side effects before resumable interruption points must be idempotent.

## MAPS translation

MAPS should **not** use time-travel to rewrite canonical task history.

But for derived execution/routing state, a useful future debugging tool is:

```text
run trace
↓
select checkpoint / decision point
↓
fork disposable simulation
↓
change candidate route/context/config
↓
compare resulting behavior
```

This could become important for harness evaluation.

## Classification

**P2/P3 — debugging/eval tool, not task authority.**

Current LangGraph checkpoint capability may already provide much of the mechanism.

---

# 13. Standardized observability vocabulary

## What OpenTelemetry learned

OpenTelemetry now defines GenAI semantic concepts including agent identity, conversation/session IDs, workflow names, provider identity, tool operations, usage, evaluation labels, and more.

It also explicitly warns that prompts/messages/retrieval queries may contain sensitive information and should not necessarily be recorded by default.

## MAPS opportunity

Instead of inventing every trace field name independently, align new telemetry where practical with established vocabulary:

```text
agent / worker id
conversation / session id
workflow / flow name
provider
operation
model
input/output token usage
tool name/type
error status
```

MAPS-specific authority fields remain MAPS-specific.

## Benefits

- easier external tooling later;
- consistent metrics across providers;
- less schema churn;
- standard correlation vocabulary;
- clearer opt-in handling for sensitive content.

## Classification

**P2 — adopt conventions, not necessarily an OpenTelemetry deployment.**

Start by mapping our event/run vocabulary before adding an exporter.

---

# 14. Agentic security must be threat-modeled as a system, not prompt-filtered

## What OWASP learned

OWASP’s 2026 agentic security work emphasizes threats including:

- goal hijacking;
- tool misuse;
- identity and privilege abuse;
- agentic supply-chain compromise;
- unexpected code execution;
- memory/context poisoning;
- insecure inter-agent communication;
- cascading failures;
- human-agent trust exploitation;
- rogue/misaligned behavior.

Their MCP guidance emphasizes authentication/authorization, session isolation, validation, least privilege, and human oversight.

## MAPS translation

MAPS already has strong authority separation, but the security program should explicitly test these agent-specific properties.

Candidate adversarial regression classes:

```text
untrusted repo tries to change agent instructions
malicious skill requests undeclared tools
MCP server description/tool output attempts prompt injection
helper claims authority it never received
stale session continues after task reshaping
spoofed worker/session ID attempts review
memory/lesson tries to override current policy
operator is shown misleading “approved/safe” language unsupported by evidence
one failed agent causes unsafe cascading retries
```

## Classification

**P1 — build the threat model and regression corpus before expanding tool/skill autonomy.**

---

# 15. Memory/knowledge is a privileged attack surface

## Cross-system lesson

Devin, Claude, OpenHands and others gain substantial value from persistent knowledge, but OWASP explicitly identifies memory/context poisoning as an agentic security risk.

Therefore MAPS should not treat future operational learning or skill suggestions as benign text storage.

## Required MAPS memory classes

At minimum distinguish:

```text
UNTRUSTED OBSERVATION
CANDIDATE LESSON
REVIEWED GUIDANCE
ACTIVE AUTHORITY / POLICY (separate mechanism)
RETIRED / SUPERSEDED
```

No untrusted/candidate memory may become instruction authority merely because it is retrieved often.

## Classification

**P1 invariant for Operational Learning.**

---

# 16. Third-party skill/tool supply-chain governance

## Why this is now necessary

Agent Skills and MCP make capability import easy. That convenience creates a software supply-chain problem:

- instructions can be malicious;
- scripts can execute code;
- tool servers can access secrets/files/network;
- descriptions can influence routing;
- updates can silently change behavior.

Kiro explicitly warns that MCP stdio servers run with the agent environment’s privileges. OWASP treats tool and supply-chain compromise as central agentic threats.

## Candidate MAPS trust tiers

```text
T0 — bundled / locally authored / reviewed
T1 — pinned third-party, source-reviewed and behavior-tested
T2 — third-party advisory-only skill, no executable scripts/tools
T3 — untrusted/quarantine; inspect only
```

For imported packages preserve:

- source URL/repository;
- exact commit/hash;
- license;
- install date;
- requested tools/network;
- behavioral eval result;
- reviewer/approver;
- superseded version.

Never auto-update executable agent capabilities without review.

## Classification

**P1 if external skills/MCP imports become normal.**

---

# 17. Reproducible environment onboarding as a “skill” in its own right

## Convergence

Devin Blueprints, OpenHands setup scripts, Claude/AGENTS guidance, and OpenAI sandbox manifests all converge on the idea that agents perform much better when the environment tells them exactly:

- how to install/maintain dependencies;
- how to lint;
- how to test;
- how to build/run;
- what tools are expected;
- where outputs belong.

## MAPS candidate

Every repository could eventually expose a validated **development-environment skill/spec** generated from real commands, not guessed documentation.

Example:

```text
bootstrap
quick validation
full validation
run app
clean generated state
known expensive checks
```

Context Builder would reference this when execution requires it.

## Classification

**P1 procedural candidate.**

---

# 18. Context budgeting should be explicit

## Cross-system lesson

Aider uses a token budget for its repo map. Agent Skills uses progressive disclosure. Kiro dynamically loads tools/powers. Claude uses subagents to keep exploration out of the parent context.

The common lesson:

> “Available information” and “information that should occupy the current context window” are different things.

## MAPS translation

Future Context Builder should have an explicit context budget and priority classes:

```text
MUST LOAD — active authority, task contract, exact changed files
SHOULD LOAD — direct dependencies, applicable skill
MAY LOAD — secondary references
ON DEMAND — broad repository exploration, external docs
```

This is safer than simply increasing retrieval volume.

## Classification

**P1 refinement for Context Builder v2.**

---

# 19. Subagents are primarily a context-management mechanism

## What mature systems emphasize

Claude’s documentation frames subagents as useful when exploration/logs/file content would flood the main context. OpenHands/goose similarly use isolated subtasks.

This supports MAPS’s current stance: do not create agents just to make an org chart.

## MAPS criterion for spawning/delegating

A helper/subagent should have at least one concrete advantage:

```text
context isolation
parallel independent work
special tool/capability boundary
cost reduction
independent review
fault isolation
```

If none apply, keep the task with the current owner.

## Classification

**Already conceptually solved; preserve as dispatch invariant.**

---

# 20. “Hooks for deterministic things, skills for procedural things, agents for judgment”

This may be the most useful synthesis from the ecosystem.

Use the narrowest mechanism that provides the required guarantee:

| Need | Best default mechanism |
|---|---|
| Must always happen at a lifecycle boundary | deterministic hook/check |
| Reusable multi-step know-how | Skill |
| Concrete executable operation | Tool/script |
| Repetitive stable orchestration | deterministic flow |
| Broad facts/reference | context/knowledge source |
| Independent judgment/research | agent/helper |
| High-impact permission | policy/operator approval |
| Historical improvement | outcome + eval + reviewed promotion |

This prevents MAPS from turning every requirement into prompt prose or another agent.

---

# Ranked candidates for MAPS

## Tier A — should materially influence the near-term architecture

### A1. Deterministic Hook / Interceptor layer

Reason: convergent pattern across Claude Code and Copilot; consolidates safety, validation, telemetry and lifecycle guarantees.

### A2. Open Agent Skills compatibility + quality/provenance gate

Reason: ecosystem convergence; progressive disclosure; reusable procedures; cross-agent portability.

### A3. EnvironmentSpec / declarative environment blueprint

Reason: reproducibility, recovery, model-independent execution quality.

### A4. ACI/tool-result design standard

Reason: low complexity, potentially large impact; SWE-agent empirical motivation.

### A5. Agentic security regression suite based on OWASP threat classes

Reason: MAPS is becoming powerful enough that tool/identity/memory/supply-chain risks are now system-level concerns.

## Tier B — likely valuable after current Prime phases mature

### B1. Portable Run Record / trajectory export

Build on trace + lineage + outcomes.

### B2. Context Builder v2 budgets + progressive skill/tool loading

Explicit priority tiers; avoid context flooding.

### B3. Capability Packs referencing skills + tools + hooks

Use when MCP/tool catalog becomes large.

### B4. OpenTelemetry-compatible naming/export mapping

Standardize telemetry before broad observability integrations.

### B5. Environment snapshots / rehydration

Only after EnvironmentSpec and recovery needs justify implementation.

## Tier C — experiment before promotion

### C1. Exemplars/demonstrations inside skills

Test whether validated trajectories improve complex procedures.

### C2. Architect/editor split execution strategy

Compare against one-agent execution for suitable tasks.

### C3. Disposable checkpoint forks/time-travel for harness evaluation

Useful for debugging and controlled experiments; never rewrite canonical task history.

---

# Things researched that should NOT become default MAPS mechanisms

## Large always-loaded skill libraries

Progressive disclosure exists specifically because this degrades context quality.

## Unreviewed community skills / one-click executable imports

Convenient, but the supply-chain and routing risks are unacceptable for a system with real authority.

## Persona-driven specialist agents

Skills/tool restrictions are more concrete and portable than roleplay identities.

## Universal Docker/microVM requirement

Isolation is valuable, but execution environments should be threat/risk appropriate.

## Automatic self-generated knowledge promotion

Suggestions are useful. Promotion without provenance/review is memory poisoning waiting to happen.

## Dynamic tool loading controlled solely by fuzzy semantic relevance

Promising, but capability activation must also honor explicit task authority and trust policy.

---

# Recommended additions to the Prime roadmap

The current Prime roadmap should eventually incorporate these cross-system findings:

```text
Phase 0 — foundation review

Phase 1 — Harness API
  + ACI operation envelope standard
  + common Hook/Interceptor contract

Phase 2 — lineage / trace
  + portable Run Record format
  + OpenTelemetry-compatible correlation vocabulary

Phase 3 — review/evidence binding
  + post-edit deterministic validation hooks

Parallel security track
  + OWASP-derived adversarial regression corpus
  + skill/tool supply-chain trust tiers

Context/skill track
  + Agent Skills open-standard compatibility
  + skill lint/provenance/eval gate
  + Context Builder budget classes

Environment track
  + EnvironmentSpec
  + later snapshot/rehydration if justified

Later capability track
  + capability packs / dynamic tool loading
  + exemplar trajectories
  + optional architect/editor strategy

Learning/eval track
  + trajectory exports
  + frozen real-incident eval cases
  + proposal-only harness improvement
```

---

# Suggested immediate research experiments before implementation

## EXP-A — Skill selection quality

Create 10–20 small MAPS skills with deliberately clear/ambiguous descriptions. Test whether multiple providers correctly select or abstain. Include hard negatives and paraphrases.

Purpose: avoid building a skill system whose routing metadata is unreliable.

## EXP-B — Hook value

Instrument a small coding task with deterministic hooks:

- write-scope check;
- secret scan;
- syntax/lint;
- event telemetry.

Compare error escape rate and agent friction versus the current path.

## EXP-C — ACI output ergonomics

Give agents equivalent tasks using:

1. raw shell/file outputs;
2. bounded structured result envelopes.

Measure mistakes, repeated tool calls, context usage, and time-to-correct-action.

## EXP-D — Environment reproducibility

Run the same task from:

1. ad-hoc local state;
2. an explicit EnvironmentSpec setup.

Measure setup failure, test reproducibility, and recovery quality.

## EXP-E — External skill red-team

Build/import deliberately malicious or ambiguous skills:

- requests excessive tools;
- attempts to override AGENTS/policy;
- hidden executable script;
- misleading description;
- poisoned reference file.

Ensure MAPS trust/lint/eval design can surface the risk before activation.

---

# Primary sources consulted

## Claude Code / Anthropic

- Hooks reference: https://code.claude.com/docs/en/hooks
- Hooks guide: https://code.claude.com/docs/en/hooks-guide
- Subagents: https://code.claude.com/docs/en/sub-agents
- Parallel agents/worktrees: https://code.claude.com/docs/en/agents
- Skills: https://code.claude.com/docs/en/slash-commands
- Agent SDK hooks: https://code.claude.com/docs/en/agent-sdk/hooks

## GitHub Copilot

- Hooks concepts: https://docs.github.com/en/copilot/concepts/agents/hooks
- Hooks reference: https://docs.github.com/en/copilot/reference/hooks-reference
- Customization overview/skills: https://docs.github.com/en/copilot/reference/customization-cheat-sheet

## OpenAI

- Updated Agents SDK harness/sandbox architecture: https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- Agents platform/tracing overview: https://openai.com/index/new-tools-for-building-agents/

## OpenHands

- Skills overview: https://docs.openhands.dev/overview/skills
- SDK skills/progressive disclosure: https://docs.openhands.dev/sdk/guides/skill
- Sandboxes: https://docs.openhands.dev/openhands/usage/sandboxes/overview
- Runtime/sandbox architecture: https://docs.openhands.dev/openhands/usage/architecture/runtime

## SWE-agent

- Agent-Computer Interface: https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md
- Trajectories: https://github.com/SWE-agent/SWE-agent/blob/main/docs/usage/trajectories.md
- Demonstrations: https://github.com/SWE-agent/SWE-agent/blob/main/docs/config/demonstrations.md

## aider

- Repository map: https://aider.chat/docs/repomap.html
- Lint/test loop: https://aider.chat/docs/usage/lint-test.html
- Architect/editor mode: https://aider.chat/docs/usage/modes.html

## Devin

- Environment configuration: https://docs.devin.ai/onboard-devin/environment
- Blueprint reference: https://docs.devin.ai/onboard-devin/environment/blueprint-reference
- Knowledge: https://docs.devin.ai/product-guides/knowledge
- Skills: https://docs.devin.ai/product-guides/skills
- Playbooks: https://docs.devin.ai/product-guides/creating-playbooks

## Kiro

- Agent Skills: https://kiro.dev/docs/skills/
- Powers: https://kiro.dev/docs/powers/
- Power architecture: https://kiro.dev/blog/introducing-powers/

## goose

- Project/features/recipes/subagents/security: https://block.github.io/goose/

## LangGraph

- Persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- Interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Time travel: https://docs.langchain.com/oss/python/langgraph/use-time-travel

## Agent Skills standard

- Specification: https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
- Overview: https://agentskills.io/home

## Observability

- OpenTelemetry GenAI attributes: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- OpenTelemetry semantic conventions: https://opentelemetry.io/docs/specs/semconv/

## Agentic security

- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Agentic Threats Navigator: https://genai.owasp.org/resource/owasp-gen-ai-security-project-agentic-threats-navigator/
- Secure third-party MCP guidance: https://genai.owasp.org/resource/cheatsheet-a-practical-guide-for-securely-using-third-party-mcp-servers-1-0/
- Secure MCP server development: https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/
- Memory/context poisoning discussion: https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/

## Recent original research on skill quality

- “Authoring Agent Skills: A Software-Engineering Approach” (2026): https://arxiv.org/abs/2607.25032
- “What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files” (2026): https://arxiv.org/abs/2608.08453

---

# Bottom line

The next evolution of MAPS should not be “more orchestration.”

The ecosystem’s strongest lessons point toward:

> **deterministic interception + portable procedural skills + reproducible environments + better tool interfaces + complete trajectories + explicit security/provenance.**

These mechanisms make existing agents more reliable and teachable without requiring a larger permanent agent hierarchy.
