# Research Summary

Summary ID: SUMMARY-CLEARFRONT-DELIVERY-2026-07-17

- Related brief: TASK-222 description and acceptance criteria
- Related claim matrix: Embedded in the evidence, comparison, and source-classification sections below
- Related assumption register: Embedded in Evidence boundaries
- Task: TASK-222
- Owner: codex-lab-lilo
- Date: 2026-07-17
- Status: SUBMITTED
- Question: Did MAP's multi-agent handling of ClearFront improve outcomes enough to justify its coordination cost, and what operating model should replace the uniform workflow?
- Confidence: HIGH for the observed ClearFront process; MEDIUM for projected improvements until controlled trials exist.
- Reverify: agent-framework claims after 2027-01-17 or when MAP materially changes its orchestration model.

## Question

Did MAP's multi-agent handling of ClearFront improve outcomes enough to justify its coordination cost, and what operating model should replace the uniform workflow?

## Answer

## Executive answer

ClearFront was handled carefully but inefficiently. The strongest parts of MAP—one accountable owner, preserved source, deterministic evidence, adversarial review, and durable defect records—changed outcomes. Reviews caught path traversal and atomicity failures, a hidden-information undo exploit, a missing render binding, and four runtime-only extraction defects. Those controls should remain where failure is expensive.

The weak part was uniformity. High-assurance ceremony was applied to security-sensitive extraction, state/combat logic, a 78-line dependency-free input move, and cosmetic card art alike. Across TASK-207–217 the system recorded 89 events, including 53 `PROGRESS` messages, and produced 60 artifacts (~8 MiB). The expanded TASK-207–222 window now contains 100 events (59 `PROGRESS`) and 64 ClearFront artifact files (7.83 MiB). Shared-file dependencies also limited real parallelism. Multiple agents therefore increased review independence, but often not implementation throughput.

The right target is not “one agent” or “many agents.” It is **one product owner by default, deterministic gates continuously, and extra agents only when they add genuine parallel search, distinct capability, or independent risk reduction**. This matches current first-party guidance across Anthropic, OpenAI, Google, Microsoft, AWS, and LangGraph and maps cleanly to proven operating mechanisms from DORA, Toyota, Google SRE, and Amazon.

## Confidence

- [x] HIGH for the observed ClearFront process: direct task, event, artifact, decision, test, and review records agree.
- [x] MEDIUM for projected improvements: sources support the mechanisms, but MAP has not yet run a controlled single-owner versus multi-agent comparison.

## Confidence decays after

Reverify current agent-framework guidance after 2027-01-17 or when MAP materially changes its orchestration model. The historical ClearFront measurements do not decay, though later events can expand the comparison window.

## Open questions

- What is the outcome-adjusted token and wall-clock difference between a single owner and multiple agents on comparable MAP work? Current telemetry cannot answer this.
- What low-risk sampling rate preserves review yield without restoring universal ceremony? This requires the proposed 30-day calibration trial.
- What immutable snapshot mechanism works safely while the shared repository contains unrelated in-flight changes?

## Downstream effect

- [x] Feeds TASK-222 review and the proposed measured process pilots.
- [ ] Feeds a new decision immediately. Recommendations should be reviewed and tested before becoming additional mandatory policy.
- [ ] Informational only.

## Evidence and limitations

### Verified local facts

- TASK-207–217 produced 89 global MAP events: 53 `PROGRESS`, 11 `APPROVED`, 9 `RELEASED`, 8 `SUBMISSION`, 5 `CHANGES_REQUESTED`, 2 `BLOCKED`, and 1 decision event. Source: `MAP_System/events/events.jsonl`, independently counted by the ClearFront audit.
- The current TASK-207–222 window contains 100 events: 59 `PROGRESS`, 13 `APPROVED`, 11 `RELEASED`, 8 `SUBMISSION`, 6 `CHANGES_REQUESTED`, 2 `BLOCKED`, and 1 decision event. This count includes later process-improvement and infrastructure tasks and is not directly comparable as product-only throughput.
- `Projects/ClearFront/artifacts/` currently contains 64 files totaling 8,209,839 bytes (7.83 MiB). The earlier audit measured 60 files and roughly 8 MiB before follow-up work.
- Independent reviews found material defects in TASK-207, TASK-213, TASK-214, and TASK-215. Review was therefore not merely ceremonial.
- TASK-212 re-entered review because nine existing evidence paths were missing from metadata; product evidence itself had passed. TASK-209 was retired after incorrect role classification. These are process failures, not product failures.
- TASK-216 and TASK-217 each received separate task, verification, review, release, current-state, and event cycles despite low-risk scopes.
- TASK-218/219 already implemented the first corrective step: risk-tiered review, a one-command test gate, and a consolidated delivery-note template.
- MAP's broader calibration found a median task span of 0.33 hours, median submission-to-approval of 4.8 minutes, and 36/156 submitted tasks (23.1%) receiving changes requested. It also found 2,524 agent messages versus 1,074 durable events (2.35:1). These system-wide figures show review yield, but they do not isolate ClearFront's causal benefit or token cost.

Primary local sources:

- `Projects/ClearFront/artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`
- `Projects/ClearFront/shared/current-state.md`
- `Projects/ClearFront/shared/decisions.md` (DEC-CF-008)
- `MAP_System/artifacts/audits/map-real-parameter-calibration-results-2026-07-14.md`
- `MAP_System/artifacts/reviews/agent-coordination-documents-review-2026-07-17.md`

### Evidence boundaries

- There was no controlled one-agent counterfactual. Claims that one agent would have been faster are well-supported inference from shared-file serialization and repeated gates, not measured fact.
- Artifact count and message count are cost proxies, not direct token or wall-clock measurements.
- Vendor framework documentation describes intended patterns and vendor experience; it is not neutral comparative benchmarking.
- Anthropic's 90.2% result is an internal breadth-first research evaluation, not evidence that multi-agent coding is generally superior.
- Business practices transfer as mechanisms, not metaphors. Software agents are not factories or human organizations; each recommendation below names the specific transferable control.

## What went right

1. **The original was preserved and reproducible.** Hashes, extraction tests, parity baselines, screenshots, and seeded replays made a risky decomposition inspectable.
2. **Independent review changed the product.** It found security, hidden-information, integration, and live-runtime defects that implementation self-checks missed.
3. **Owners disclosed discoveries.** TASK-214/215 recorded scope gaps and runtime defects instead of smoothing them out of the release narrative.
4. **Refactor and rules changes stayed separate.** Baseline parity was not falsely described as game-rules conformance.
5. **The process learned while running.** DEC-CF-008, TASK-218, and TASK-219 turned the audit into risk lanes, automated gates, and less evidence duplication.
6. **Durable state made restart possible.** Task records, artifacts, and handoffs preserve enough context to continue after agent limits or session loss.

## What went wrong

1. **Risk did not determine process weight.** Low-risk presentation and mechanical extraction work paid nearly the same review/release tax as security and state-engine changes.
2. **Tasks were sliced by file/function cluster rather than end-to-end outcome.** Several slices touched the same host and mutable context, so parallel agents could not safely create proportional throughput.
3. **Narration was mistaken for state.** Fifty-three progress events in the original phase diluted transitions, findings, decisions, and blockers.
4. **Mirrors and evidence registration could reject correct work.** Metadata-only rework consumed the same status path as product defects.
5. **No immutable phase snapshot anchored reviews.** Working-tree files and saved evidence were reviewed without a clean commit boundary.
6. **Test orchestration initially depended on manual Chromium setup and arguments.** This increased reviewer reconstruction cost until TASK-219.
7. **Agent availability was treated as capacity even when it was not useful capacity.** Pi failed a bounded task over many turns; a helper ran out of credits; session-limit recovery required infrastructure work. A named agent is not throughput unless it has a clear scope, tools, and stopping condition.
8. **Project-local and global records diverged.** ClearFront's local event stream was empty while narrative events accumulated globally.

## Comparison with current agent-orchestration models

| Approach | Primary-source mechanism | Where it fits ClearFront | Where it does not |
|---|---|---|---|
| Anthropic orchestrator-workers | A lead agent delegates explicit, parallel research scopes. Anthropic reports 90.2% better performance than a single Opus agent on its internal breadth-first research eval, while warning that multi-agent systems use substantially more tokens and fit poorly when tasks share dependencies. [Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system) | Rules research, asset exploration, test-matrix enumeration, independent security review. | Adjacent edits to `index.html`, mutable `ctx`, or tightly sequential refactors. ClearFront used multiple agents in precisely this low-parallelism region. |
| Anthropic composable workflows | Start with the simplest solution; add agentic complexity only when it improves the outcome. Distinguish predictable workflows from autonomous agents. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Deterministic extraction, syntax, engine, browser, and release gates should be code, not agents. | Using a new agent to perform a check a script can make exact and repeatable. |
| OpenAI single agent / manager / handoff | Maximize a single agent first. Split when conditional logic or tool overlap overwhelms it. Use a manager for central synthesis or decentralized handoffs when another specialist should take over. [OpenAI practical guide](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) | One implementation owner with reviewers/researchers as tools matches ClearFront's need for central integration. | Peer handoffs between agents editing the same coupled surface create reconstruction and ownership cost. |
| Microsoft AutoGen / Magentic-One | A lead orchestrator maintains a Task Ledger and Progress Ledger, delegates to specialized agents, and replans when progress stalls. [Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html) | Explicit progress detection and replanning would have stopped the unproductive Pi lane sooner. Durable MAP tasks resemble a task ledger. | A second free-form progress ledger would duplicate MAP state unless generated from the canonical task/event store. |
| LangGraph supervisor patterns | Supervisor, handoff, subagent, router, and custom workflow patterns support different information-flow needs; multi-agent is not required for every complex task. [LangGraph multi-agent overview](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) | MAP already benefits from explicit state transitions and resumability. A supervisor is useful for routing independent work. | Graph complexity is not a cure for unclear ownership or too many records. The current pending bootstrap gate also shows that unused graph ceremony can become noise rather than flow control. |
| Google Cloud architecture guidance | Start with a single agent, then choose multi-agent only after evaluating complexity, latency, cost, performance, and human involvement. [Google agent design patterns](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system) | Provides the missing escalation rule: multi-agent must earn its overhead against a measured baseline. | “Multi-agent by default” because several sessions are available. |
| AWS supervisor/collaborator pattern | Give collaborators clear, non-overlapping responsibilities under a supervisor. [AWS Bedrock collaboration](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-multi-agent-collaboration.html) | Separate test design, rules audit, security review, and asset work are bounded specialties. | Vague roles or overlapping ownership of the same files/tasks. |

### Synthesis from agent frameworks

The frameworks disagree on implementation style—graphs, code-first loops, event runtimes, supervisors, or handoffs—but converge on five operating rules:

1. Start with one capable agent and deterministic tools.
2. Add agents for specialization, parallelism, context isolation, or independent verification.
3. Give every delegation a bounded objective, output, permissions, and exit condition.
4. Preserve shared state and observability; replan when progress stalls.
5. Evaluate end results, latency, and cost—not agent activity.

MAP already implements pieces of 3 and 4. ClearFront's main deviation was failing rules 1, 2, and 5 consistently.

## Transferable business operating mechanisms

| Discipline/example | Verified mechanism | MAP transfer |
|---|---|---|
| DORA / continuous delivery | DORA recommends baselining delivery performance, finding the greatest constraint, reducing batch size, and improving iteratively. Small batches correlate with better software and organizational outcomes. [DORA metrics](https://dora.dev/guides/dora-metrics/), [working in small batches](https://dora.dev/capabilities/working-in-small-batches/) | Keep implementation batches small and coherent, but do **not** make each small change pay a separate governance/release ceremony. Measure lead time, recovery, rework, and change failure together. |
| Toyota Production System | Just-in-Time limits work/inventory to what downstream needs; jidoka automatically stops on abnormality so quality is built into the process without constant watching. [Toyota TPS](https://www.toyota-global.com/company/history_of_toyota/75years/data/automotive_business/production/system/change.html), [jidoka origin](https://www.toyota-global.com/company/history_of_toyota/75years/text/taking_on_the_automotive_business/chapter1/section1/item4.html) | Use pull-based task claims and WIP limits. Make deterministic tests stop bad work immediately. Do not substitute a human/agent watcher for an automatable gate. |
| Google SRE | Error budgets balance reliability and feature velocity; monitoring should page for immediate action, ticket delayed action, or log non-actionable information. Blameless postmortems turn failures into system changes; toil should be engineered away. [SRE service practices](https://sre.google/sre-book/service-best-practices/), [postmortem culture](https://sre.google/sre-book/postmortem-culture/), [eliminating toil](https://sre.google/resources/book-update/eliminating-toil/) | Replace constant progress notifications with attention classes: request only for decisions/blockers, task for deferred work, log for routine evidence. Automate recurring session-limit and test toil. Tighten assurance when a project's quality budget is being spent. |
| Amazon single-threaded ownership | Small teams own the full value stream under “you build it, you run it,” minimizing handoffs; centralized functions enable rather than directly oversee every action. [AWS value-stream ownership](https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/oa.std.6-provide-teams-ownership-of-the-entire-value-stream-for-their-product.html) | One owner should integrate a coherent ClearFront outcome through implementation, test, and release readiness. Reviewers provide independent challenge at risk boundaries, not serial custody transfer after every file. |

These mechanisms resolve an apparent contradiction: DORA favors small batches, while the ClearFront audit recommends batching low-risk work. The compatible rule is **small implementation batches, aggregated low-risk governance**. Keep changes reviewable and releasable; avoid multiplying administrative cycles that do not reduce product risk.

## Recommended MAP operating model

### Adopt now

| Priority | Change | Expected benefit | Cost/risk | Success measure |
|---|---|---|---|---|
| P0 | One accountable owner for each coherent product outcome; agents beyond the owner require a stated source of value: parallelism, specialty, context isolation, or independence. | Fewer handoffs and conflicts; clearer integration. | Larger owner scope can concentrate context/risk. | At least 80% of routine product batches use one implementation owner; duplicate/overlapping work trends toward zero. |
| P0 | Keep the three risk lanes and put review at the risk boundary, not every file boundary. | Preserves defect-catching where valuable while shortening low-risk flow. | Misclassification could under-review a change. | Review-caught `BLOCKER`/`REQUIRED` findings per lane; escaped defects per lane; low-risk median lead time falls without higher escaped defects. |
| P0 | Make deterministic gates the jidoka layer: one command, fail fast, exact exit status, managed dependencies. | Faster feedback and less reviewer reconstruction. | Test maintenance. | Reviewer setup time under 5 minutes; all releases cite one reproducible gate; flaky retry rate measured and declining. |
| P0 | Require immutable snapshot IDs for medium/high-risk review. | Review and release refer to the same bytes; rollback improves. | Dirty shared worktree complicates adoption. | 100% of medium/high reviews name a commit or content-addressed manifest. |
| P1 | Emit events only for transitions, new evidence, changed risk, decisions, blockers, submission/review/release. | Higher signal and lower context cost. | Over-pruning could hide useful diagnostics. | `PROGRESS` share falls from ClearFront's 59% while restart tests remain successful. Raw logs remain available outside the attention stream. |
| P1 | Set a WIP limit of one shared-surface implementation task per project owner; pull new work only when the current batch reaches a stable boundary. | Reduces contention on coupled files and half-finished inventory. | May idle agents when work is not decomposable. That is preferable to fake parallelism. | Fewer blocked tasks due to shared paths; lower first-event-to-submission tail. |
| P1 | Generate mirrors, manifests, and routine checklists from canonical state. Add a metadata-amend path that does not replay product review when bytes/evidence are unchanged. | Removes administrative rework like TASK-212. | Generator bugs could propagate errors. | Metadata-only `CHANGES_REQUESTED` cycles approach zero; mirror validators remain green. |
| P1 | Use SRE-style attention classes in Command Center: request/page, queued task, durable log. | Protects operator attention and makes alerts actionable. | Requires routing discipline. | Operator requests consist only of genuine decisions/risks; routine informs do not require acknowledgement. |
| P1 | Add a stagnation rule: after a bounded number of turns or repeated unchanged reports, stop/replan/reassign. | Avoids Pi-like non-progress loops and token waste. | Prematurely stopping difficult work. | Track stopped lanes, recovered outcomes, and false stops; every helper has explicit exit criteria. |

### Avoid

- Do not assign extra agents merely because they are available.
- Do not let multiple agents own adjacent edits on a coupled shared surface.
- Do not create a second canonical state or progress ledger beside MAP's task/database/event authority.
- Do not require a standalone release checklist for every low-risk item.
- Do not equate message, event, artifact, or agent count with progress.
- Do not delegate exact deterministic checks to LLMs.
- Do not remove independent review globally; ClearFront provides direct evidence that it catches important defects.
- Do not adopt the proposed MAP/1 shorthand globally until parsing, validation, versioning, rendering, and a measured pilot exist.

### Pilot before standardizing

1. **Single-owner versus multi-agent batch trial.** Select paired, similarly sized ClearFront or MAP changes. Record risk lane, active agents, wall time, model turns/tokens where available, handoffs, review findings, rework, and escaped defects. Multi-agent wins only if outcome-adjusted lead time or defect prevention justifies its cost.
2. **State-change-only event trial.** For three batches, suppress narrative progress from the durable event stream while retaining raw tool logs. Test restart reconstruction with a fresh agent. Pass if reconstruction remains accurate and event volume falls at least 40%.
3. **Risk-lane calibration trial.** Review a sample of low-risk work at batch boundaries and all high-risk work independently. Compare caught findings and escaped defects for 30 days. Tighten or loosen lane definitions from evidence.
4. **Stagnation/replan trial.** Instrument helpers with `max_turns_without_new_evidence`, required durable output, and a replan path. Measure useful recoveries and false stops.
5. **MAP/1 communication trial.** Only after a parser/validator exists, compare shorthand with concise structured English on interpretation accuracy, receiving-context tokens, latency, and rework.

## 30/60/90-day learning plan

### First 30 days

- Apply DEC-CF-008 consistently to ClearFront's next work.
- Finish TASK-220's deterministic engine matrix and use it as the high-risk gate.
- Add snapshot identity to medium/high delivery notes.
- Start collecting per-batch lead time, active-agent count, review findings by severity, metadata-only rework, and escaped defects.
- Route Command Center messages by attention class and stop routine polling/narration.

### By 60 days

- Run at least three paired single-owner/multi-agent comparisons.
- Implement or prototype generated release manifests and metadata-only amendment.
- Review the WIP limit and stagnation threshold using observed false stops and blocked-path time.
- Publish a short monthly flow report; do not build a dashboard until the fields prove useful.

### By 90 days

- Decide which agent patterns earned permanent use by task class.
- Recalibrate risk lanes from real escaped-defect and review-yield data.
- Retire redundant narrative records and generators that do not change decisions.
- Decide whether a MAP/1 parser pilot is worthwhile; do not proceed on token-saving estimates alone.

## Final diagnosis

MAP is not fundamentally getting in its own way because it uses multiple agents. It gets in its own way when **coordination is treated as intrinsically valuable instead of as an investment that must buy parallel work, specialization, or independence**. ClearFront shows both sides: independent review prevented serious defects, while repeated ownership transfers, status narration, evidence duplication, and uniform gates slowed low-risk delivery.

The durable improvement is a thinner control system: a single accountable flow owner, small coherent batches, automated stop-the-line quality, risk-triggered independent review, immutable evidence, pull-based work, and measured experiments. That model preserves what made ClearFront trustworthy while removing the ceremony that made it feel slow.

## Source classification

All external sources cited above are `PRIMARY`: first-party vendor documentation or first-party operating-system guidance. Local task, event, decision, review, and audit records are also `PRIMARY` for what occurred in MAP. No community source is load-bearing. Recommendations are explicitly proposals; causal claims without a controlled comparison are labeled inference or pilot hypotheses.
