<!-- hpom: file: artifacts/planning/map-bedrock-phase-checklist-2026-08-10.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-sumi -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-08-10 -->
<!-- hpom: confidence: HIGH -->

<!--
Canonical, agent-readable checklist for the MAP Bedrock program
(map-2-research-adoption-implementation-program-2026-08-09.md), formatted
per Projects/ProjectUpdater/shared/project-brief.md's "Steps outline
format" convention. This file is the durable source of truth; the
ProjectUpdater app's "MAP Bedrock" project is a human-facing dashboard
imported FROM this file (via
Projects/ProjectUpdater/scripts/project_updater_command.py update
"MAP Bedrock" --steps-file <this file>). Codex and future Claude sessions:
re-read this file for current program status/next-action before assuming
the plan document alone reflects live state - the plan is the design, this
file is the tracked execution state. Keep both in sync when either changes;
re-import into ProjectUpdater after editing this file.
-->

## Phase 0 — Trustworthy baseline

Combined exit gate CLOSED 2026-08-10 — see
`artifacts/planning/phase0-baseline-packet-2026-08-10.md` for the
single-revision packet showing P0.1/P0.2/P0.3 all passing together.
- [x] P0.1: Authority and rotation incidents resolved
  - [x] TASK-321: authority sandbox/cgroup fallback fix
  - [x] TASK-316/317: writer-service quiet window + describe verb
  - [x] TASK-307/308: gateway patch deploy + live verify
  - [x] 3 consecutive scheduled sync cycles verified
- [x] P0.2: Durable validation debt (TASK-323, RELEASED)
  - [x] events.jsonl NUL corruption repaired on Smalls (REPAIR-0013 follow-up
    by helper-releases-batch2-bela, applied directly on Smalls this time;
    verified byte-identical clean line 18785 on both Smalls and Biggie,
    validate_events.py errors=0, 2026-08-10)
  - [x] TASK-315 stale backlink fixed (REPAIR-0014, confirmed on Smalls)
  - [x] 22 wikilink findings triaged
  - [x] Resubmitted, independently re-verified and approved
    (helper-review-task323-fenn re-checked all three parts directly, not
    just re-read the submission), released 2026-08-10
- [x] P0.3: Lifecycle backlog disposition (TASK-324, RELEASED)
  - [x] Disposition record written (11 ready, 1 blocked: TASK-311)
  - [x] Independent review + approve TASK-324
  - [ ] Execute the 11 ready-to-release checklists (10/11 done: TASK-295,
    298, 299, 300, 301, 302, 303, 305, 309, 313 RELEASED. TASK-297 HELD —
    requires_operator_approval=true with no operator-approval event found
    in events.jsonl/decisions.md/hcom transcripts, only a peer APPROVED;
    needs operator sign-off before release, not a mechanical gap)
## Phase 1 — Freeze the architecture contract
- [x] D0: coordinator designation confirmed (claude-lab-sumi, DEC-042 —
  operator-directed 2026-08-10; supersedes the earlier checklist entry
  citing DEC-039, which was a different role scoped to the now-closed
  MAP-BOOTSTRAP-20260617 recovery epic, not this program)
- [ ] Architecture decision packet — DRAFTED 2026-08-10, routed to Codex
  for independent review (see
  `artifacts/planning/phase1-architecture-decision-packet-2026-08-10.md`
  and `handoffs/HANDOFF-phase1-architecture-packet-review-to-codex-2026-08-10.md`).
  Not checked off until Codex review clears and D1 operator approval
  lands on the exact decision hash.
  - [ ] Authority seam: sole mutation path, no second writer
  - [ ] Projection contract: task/graph/current-state/events as one-way
  - [ ] Event model: transactional canonical events
  - [ ] Identity/version semantics (expected_version, idempotency_key)
- [ ] Schema/command contract
  - [ ] Additive tables (map_events, command_dedup, operator_approvals)
  - [ ] Threat model: spoofing, stale version, duplicate retries, replay
- [ ] D1: operator approval on exact decision hash
## Phase 2 — Transactional authority slice
- [ ] P2.1: In-process command layer
  - [ ] Command modules (commands/queries/lifecycle/authz/events/idempotency)
  - [ ] First command transaction (authn to commit to projection rebuild)
- [ ] P2.2: Fault-injection matrix
  - [ ] Concurrent claims + crash-window cases
  - [ ] Retry/dedup + SQLITE_BUSY + malformed payload cases
- [ ] P2.3: Minimal noncanonical telemetry spans
- [ ] Cutover: shadow-read, reversible feature gate, no dual-write
- [ ] D2: crash-after-commit proof passes before production pilot
## Phase 3 — Migrate lifecycle verbs, one-way projections
- [ ] P3.1: Verb migration
  - [ ] heartbeat / release expired lease
  - [ ] submit, review claim/release, reject, approve, release
  - [ ] create/describe/amend/add-output/retire
  - [ ] agent registration + rotation transfer/restore
  - [ ] operator approvals + halt operations
- [ ] P3.2: Deterministic projection contract
  - [ ] tasks/graph/current-state/events forward projection
  - [ ] Command Center read models
- [ ] P3.3: Direct-writer retirement + allowlist validator
- [ ] Exit gate: old writers fail closed, rollback drill restores last approved
## Phase 4 — Deterministic flows and Agent Skills
- [ ] P4.1: Thin native release-verification flow
  - [ ] load -> validate -> verify -> approval-if-needed -> release -> emit
  - [ ] D3: Lobster comparison decision (if pursued)
- [ ] P4.2: Repository Agent Skills
  - [ ] map-review + map-task first, measure context/token reduction
  - [ ] Remaining skills after measured benefit
- [ ] Exit gate: one flow completes+resumes safely, two skills show benefit
## Phase 5 — Isolated work, provider-neutral runtime
- [ ] P5.1: AgentRuntime contract (start/resume/send/steer/pause/cancel)
- [ ] P5.2: Per-task Git worktree pilot
  - [ ] Verify claim+output paths, record clean/dirty base
  - [ ] Task branch/worktree, scoped worker, tests+evidence
  - [ ] Independent review of exact bytes/commit
- [ ] P5.3: Runtime goal record pilot (task vs. runtime goal vs. continuation)
- [ ] Exit gate: two provider adapters, isolated worktrees, cannot write outside scope
## Phase 6 — Observability and harness evaluation
- [ ] P6.1: Causal trace model (OTel spans, map.* namespace, no secrets)
- [ ] P6.2: Historical evaluation corpus
  - [ ] Duplicate claim / response-loss retry / self-review cases
  - [ ] Stale authority / writer collision / contradiction cases
  - [ ] Output-path violation / bad metadata / rotation drift cases
  - [ ] Partial release / context false-positive / premature-done cases
- [ ] P6.3: Scorecard (success, violations, retries, cost, recovery time)
- [ ] Exit gate: telemetry loss proven non-fatal to lifecycle correctness
## Phase 7 — Durable-execution decision
- [ ] P7.1: Compare deepened LangGraph vs. bounded Temporal POC
  - [ ] Frozen failure matrix (pause, restart, outage, budget, rollback)
  - [ ] Decision score (correctness, complexity, recovery, controllability)
- [ ] D3: dependency approval before any Temporal install
- [ ] Operator records deepen/adopt/defer decision
## Phase 8 — Mechanical authorization and budgets
- [ ] P8.1: Policy engine interface
  - [ ] Native deterministic rules (no self-review, path/workspace match)
  - [ ] Cedar/OPA comparison only if native rules become hard to audit
- [ ] P8.2: Budgets and circuit breakers
  - [ ] Attach budgets to runtime goals/flows, not task truth
  - [ ] Accounting-only first, before any blocking enforcement
- [ ] D4: approve blocking enforcement after accounting evidence
## Phase 9 — Context Builder, memory, portable snapshots
- [ ] P9.1: Production-candidate Context Builder
  - [ ] Retrieval order: exact -> FTS5 -> capsules -> semantic (optional)
  - [ ] Acceptance thresholds (recall, abstention, contradiction fails closed)
- [ ] P9.2: Typed noncanonical memory blocks, no auto-promotion
- [ ] P9.3: Portable MAP agent snapshot (extends STATE_SNAPSHOT)
- [ ] Exit gate: blinded orientation with lower context, no authority mistake
## Phase 10 — Supervised persistent runtime (conditional)
- [ ] Conditional on Phase 2/3/5/7/8/9 evidence clearing first
- [ ] Rollout sequence
  - [ ] Deterministic process under supervisor, then one disposable session
  - [ ] Detach/reconnect, crash/recovery with no task mutation
  - [ ] Bounded task attempt, helper lifecycle, cross-host recovery drill
  - [ ] Opt-in production pilot, default only after operator acceptance
- [ ] D5: approve persistent runtime + any listener/control endpoint
## Phase 11 — Controlled refinement, conditional interop
- [ ] P11.1: refine.propose enabled after evaluation corpus exists
- [ ] P11.2: MCP/A2A/Prime adapters — conditional
  - [ ] MCP: read-only first, mutations via same authority commands
  - [ ] A2A: capability advertisement, not trusted identity
  - [ ] Prime: one AgentRuntime adapter, never default control plane
- [ ] D6: adapters only for a concrete approved use case
## Phase 12 — Program cutover and closeout
- [ ] Cutover checklist
  - [ ] Freeze changes, verify clean source + Smalls backup
  - [ ] Deploy to Smalls, migration+smoke tests, rebuild projections
  - [ ] Sync Biggie, enable enforcement flags one at a time
- [ ] Closeout artifacts (decisions, schema ref, runbook, scorecard, register)
- [ ] D7: operator accepts final cutover or orders rollback
