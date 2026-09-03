# Claude/Codex external mechanism scan — 2026-08-27 through 2026-09-03

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Purpose: consolidate the useful mechanisms surfaced across repeated external scans of public Claude/Codex repos, frameworks, papers, plugins, MCP systems, and workflow tools. This note intentionally extracts mechanisms rather than recommending product integration.

Related research:
- [Research routing index](../README.md)
- [Earlier agent-harness pattern scan](../agent-harness-patterns-scan-2026-08.md)
- [Skills/tools findings](../skills-and-tools/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Evaluation/reliability findings](../evaluation-and-reliability/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Security/authority findings](../security-and-authority/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)

## Executive findings

The strongest recurring harness lessons were:

1. durable state should outlive model context and interface sessions;
2. handoffs should reconstruct observable state rather than trust self-report;
3. runtime events belong at the boundary where the invariant becomes knowable;
4. context should be delivered selectively, often just-in-time or by objective cue;
5. continuation should be earned by validated progress, not mere process liveness;
6. provider-specific transports should sit behind narrow stable contracts;
7. task-specific harness variation is worth testing, but autonomous self-rewriting is premature.

---

## 1. Transcript-free controller continuity

**Sources:**
- Agentflow — https://github.com/saintdle/agentflow
- Anthropic Managed Agents — https://www.anthropic.com/engineering/managed-agents

**Mechanism:** treat chat/model context as replaceable working memory while keeping durable task/event state outside the model. Fresh controller sessions reconstruct from structured state rather than continuously carrying accumulated transcript.

**Problem solved:** context growth, compaction loss, stale conversational assumptions, and coupling continuity to one model session.

**Why it may matter:** MAPS already stores task, review, handoff, environment, and evidence state. A fresh-agent reconstruction experiment could test whether those records are sufficient to preserve continuity without long conversational history.

**Evidence:** Anthropic publicly describes durable session logs separate from model context and a brain/hands split for managed agents. Agentflow reports dogfooding a fresh-controller model across Claude, Codex, and Copilot, but remains early-stage.

**Failure modes:** durable state can omit tacit information; retrieval becomes the hard problem; over-aggressive transcript disposal can erase important nuance.

**MAPS disposition:** `STUDY / TEST` fresh reconstruction against long-lived-context baselines. Do not add another memory database solely for this.

---

## 2. Verified handoff reconstruction

**Sources:**
- Baton — https://github.com/Myst1C13/Baton
- smaller convergent Baton implementation — https://github.com/blader/baton

**Mechanism:** rebuild factual handoff state from independently observable evidence such as Git diff, tests, exit codes, and current repository state; let the outgoing agent contribute interpretation, intent, dead ends, and next moves.

**Problem solved:** agents are unreliable narrators of what actually happened, especially after interruptions or partial failures.

**Why it may matter:** MAPS already values source evidence over prose. Handoffs can explicitly separate observed facts from interpretation.

**Evidence:** Baton demonstrates forced interruption and transfer with deterministic fake agents plus real fixture verification; evidence remains project-authored rather than independently benchmarked.

**Failure modes:** logging every event recreates transcript bloat; reconstructed facts may still miss non-observable reasoning constraints.

**MAPS disposition:** `ADAPT PRINCIPLE`. Prefer regenerated observable state plus compact authored interpretation.

---

## 3. Orchestrator manages work; worker cognition stays replaceable

**Sources:**
- OpenAI Symphony — https://github.com/openai/symphony
- specification — https://github.com/openai/symphony/blob/main/SPEC.md

**Mechanism:** deterministic orchestration owns work polling, dispatch, isolated workspaces, retry, reconciliation, and evidence collection while coding agents remain replaceable workers.

**Problem solved:** tying project coordination to one agent's internal reasoning/session state.

**Why it may matter:** this is a useful comparison target for deciding which MAPS controller responsibilities are truly necessary versus scheduler-like mechanics.

**Evidence:** official OpenAI specification and reference implementation; several independent implementations suggest portability of the specification.

**Failure modes:** always-on autonomous issue consumption expands authority substantially; orchestration layers can duplicate existing task systems.

**MAPS disposition:** `COMPARE`, not integrate. Preserve the separation if useful; avoid another scheduler.

---

## 4. Per-action versus per-batch lifecycle boundaries

**Source:** OpenAI Codex hook discussions/issues, including batch-hook limitations: https://github.com/openai/codex/issues/41589

**Mechanism:** distinguish events where an invariant is knowable after one tool call from those knowable only after all parallel tool calls in a reasoning step settle.

**Problem solved:** hooks firing too early or too granularly can produce incorrect validation, duplicate work, or noisy feedback.

**Why it may matter:** MAPS guards, verification, and recovery should be attached to the smallest boundary where their invariant is actually observable.

**Evidence:** concrete Codex protocol limitation documented when `PostToolUse` fires independently for parallel operations.

**Failure modes:** adding too many lifecycle event types creates an event-processing framework without payoff.

**MAPS disposition:** `STUDY / AUDIT`. Classify existing mechanisms as per-action, per-batch, per-turn, per-task, or per-run before adding new hooks.

---

## 5. Stateful worker control is not the same abstraction as a tool call

**Sources:**
- OpenAI Codex App Server — https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md
- mcp-agents community adapter — https://github.com/thomaswitt/mcp-agents

**Mechanism:** long-running workers have durable identity, streaming events, approvals, cancellation, reconnection, and follow-up; provider-native protocols can sit behind a stable MAPS-facing adapter.

**Problem solved:** pretending a multi-minute interactive worker is a blocking request/response tool leads to poor recovery and approval handling.

**Why it may matter:** Portable MAPS should keep worker/session supervision separate from ordinary capability invocation.

**Evidence:** official Codex App Server exposes threads/turns/events/approvals; community adapters have already had to translate stable MCP-facing contracts onto newer Codex protocols.

**Failure modes:** compatibility wrappers accumulate provider quirks and can become permanent infrastructure.

**MAPS disposition:** `STUDY / COMPARE` against current HarnessService contracts. Add provider adapters only when a real portability need appears.

---

## 6. Out-of-band control-plane signals

**Source:** AgentCommons — https://github.com/DrishtantKaushal/AgentCommons

**Mechanism:** deliver mechanical control signals such as permission resolution, terminal liveness, reconnection, and pending messages outside model semantic context when the model does not need to reason about them.

**Problem solved:** token waste and allowing agents to reason around state that should be mechanical.

**Why it may matter:** MAPS should ask whether each coordination fact belongs in model context or merely in the harness.

**Evidence:** working community implementation using PTY/daemon coordination; adoption evidence is limited.

**Failure modes:** hiding a state transition the model actually needs to understand can create confusion.

**MAPS disposition:** `STUDY AS ARCHITECTURAL CHECK`; do not add another daemon.

---

## 7. Just-in-time and cue-triggered context delivery

**Sources:**
- Gaia — https://github.com/metraton/gaia
- OMP — https://github.com/YanwuZeng/omp
- Delivery, Not Storage — https://arxiv.org/abs/2607.20972

**Mechanism:** keep context sparse until a concrete event, path, symbol, action, or output pattern makes a specific rule/memory relevant; inject only then.

**Problem solved:** large always-loaded prompts dilute important instructions and consume context.

**Why it may matter:** MAPS has durable findings, decisions, skills, and warnings that may be more effective when attached to objective triggers than globally loaded.

**Evidence:** the cue-anchored memory paper reports voluntary memory going unused in a 114-turn trial while deterministic injection consistently delivered configured memories; OMP and Gaia provide concrete community implementations but weaker independent evidence.

**Failure modes:** poor semantic triggers can spam context or fire stale guidance; late injection can waste planning effort before denial.

**MAPS disposition:** `TEST` one objective trigger tied to an existing known fragile path or action. Do not build a general semantic trigger engine first.

---

## 8. Runtime adaptation from evidence, with fixed authority/policy

**Sources:**
- openJiuwen — https://github.com/openJiuwen-ai/
- JIT-Agent — https://github.com/bingreeky/JIT

**Mechanism:** allow bounded changes in context, feedback, or execution strategy based on newly observed evidence while keeping the underlying authority model fixed. JIT-Agent composes task-specific harnesses before execution; openJiuwen emphasizes evidence-driven adaptation during execution.

**Problem solved:** a universal harness profile may be inefficient or inappropriate across different task/risk classes.

**Why it may matter:** MAPS can test a small number of predefined profiles or one evidence-triggered adaptation rather than one-size-fits-all control depth.

**Evidence:** both projects report benchmark gains across multiple models; results are author-reported and need independent replication.

**Failure modes:** autonomous harness generation or self-modification creates a second-order governance problem and can learn from bad assumptions.

**MAPS disposition:** `STUDY`; `TEST` bounded predefined profiles. Explicitly **do not** add self-rewriting harness machinery without demonstrated need.

---

## 9. Human approval as durable suspended workflow state

**Source:** Codex SDK deferred-request discussion — https://github.com/openai/codex/issues/42219

**Mechanism:** represent an approval as a durable `WAITING_FOR_HUMAN` state with request identity and explicit resume behavior rather than blocking a control thread/tool call.

**Problem solved:** human latency can stall or corrupt long-running agent control loops.

**Why it may matter:** MAPS already contains authority gates; this provides a concrete failure-injection scenario for checking whether they survive delay/restart.

**Evidence:** issue/proposal rather than an implemented benchmark.

**Failure modes:** excessive approval states create process friction; stale approvals need expiry/cancellation semantics where appropriate.

**MAPS disposition:** `TEST CURRENT BEHAVIOR`; add nothing unless the test fails.

---

## 10. Progress earns continuation

**Source:** LoopX — https://github.com/huangruiteng/loopx

**Mechanism:** continuation quota is spent only after validated writeback/progress; failed preflight, dry runs, and quiet skips do not count as useful progress.

**Problem solved:** autonomous loops can keep consuming resources while producing no state change.

**Why it may matter:** MAPS already has no-progress/recovery concepts; this is a clean invariant for checking whether attempts alone preserve the right to continue.

**Evidence:** project/user reports of multi-day and 200+ hour runs demonstrate feasibility, not comparative superiority.

**Failure modes:** overly strict progress definitions can stop useful exploratory work; unsafe retries can duplicate side effects.

**MAPS disposition:** `STUDY / FAILURE-INJECTION TEST` against existing retry and lease behavior.

---

## 11. Scheduled-worker leases and heartbeats

**Source:** Claude Code routine liveness report — https://github.com/anthropics/claude-code/issues/91371

**Mechanism:** replace durable `running=true` assumptions with claims/leases plus heartbeat or progress evidence and recovery when the lease expires.

**Problem solved:** dead/stalled workers can permanently block later scheduled work.

**Why it may matter:** MAPS already uses claim/lease concepts; this is a useful adversarial test.

**Evidence:** reproduced user report across multiple scheduled runs; not an Anthropic-confirmed root cause.

**Failure modes:** liveness is not progress; heartbeats can keep a stuck worker alive indefinitely unless no-progress is separately tracked.

**MAPS disposition:** `TEST`. Preserve separate meanings for alive, running, and progressing.

---

## Complexity warnings

Do not infer that these findings justify:

- another general orchestration daemon;
- universal transcript/event capture in model context;
- automatic self-rewriting harnesses;
- a provider-independent worker protocol before current abstractions fail;
- a broad semantic trigger/memory service.

The smallest useful principle should be tested first.

## Highest-value next mechanism tests

1. **Verified handoff reconstruction:** observable Git/test/task state versus agent-authored factual summary.
2. **Cue-triggered context delivery:** one existing durable warning injected at an objective relevant event.
3. **Progress-earned continuation:** hang a worker after claim but before validated progress and verify safe recovery.
