# MAP Research Adoption Implementation Program

- status: reviewed_ready_for_operator_decision
- date: 2026-08-09
- plan_owner: codex-lab-duma
- requested_by: operator
- independent_reviewer: claude-lab-lote on Smalls (review complete 2026-08-09; exact historical remote identity retained in hcom #17904)
- authority_effect: none until work packages are promoted, claimed, reviewed, and approved through MAP
- host_names: Biggie is this read-only mirror PC; Smalls is the writable authority PC
- implementation_authority: Smalls through sanctioned `map-authority` operations only
- source_documents:
  - `/home/mellow/Documents/Projects/MultiAgentProject-main/Web_research_MAP.md`
  - `/home/mellow/Documents/Projects/MultiAgentProject-main/MAP_Prime_Agent_Adoption_Brief.md`
  - `/home/mellow/Documents/Projects/MultiAgentProject-main/deep-research-report.md`
- existing_plans_reconciled:
  - `MAP_System/notes/system-improvement-implementation-plan.md`
  - `MAP_System/artifacts/planning/map-613-master-implementation-plan.md`
  - `MAP_System/artifacts/planning/map-runtime-migration-inventory.md`
  - `MAP_System/artifacts/planning/map-runtime-migration-plan.md`
  - `MAP_System/artifacts/planning/biggie-smalls-orchestration-action-plan-2026-07-29.md`
  - `MAP_System/artifacts/planning/kudu-ruki-orchestration-plan-2026-07-28.md` (legacy filename; its hosts are Biggie and Smalls)

## 1. Executive decision

MAP should adopt the research as an incremental infrastructure program, not a
framework replacement or a greenfield “MAP 2.0” rewrite.

The critical path is:

```text
recover a trustworthy cross-host baseline
  -> one transactional authority command seam
  -> generated lifecycle projections
  -> deterministic workflows and repository skills
  -> isolated task execution and provider-neutral runtime contract
  -> behavioral telemetry and historical evaluations
  -> measured durable-execution and authorization experiments
  -> context builder and portable noncanonical runtime state
  -> persistent supervised runtime only if the evidence justifies it
  -> controlled refinement and interoperability last
```

The first production proof is intentionally small:

> Commit one task claim and one canonical event in one authority transaction,
> kill the command handler before it replies, retry with the same idempotency
> key, and prove one transition, one event, the same result, and a rebuildable
> projection.

This program extends the existing `map-authority`/Smalls design. It must not add
a second writable `mapd`, make Biggie's mirror writable, or make JSONL/session
memory canonical.

The three source documents are research inputs, not MAP authority. Their
recommendations become actionable only when reconciled with current code,
released/active tasks, operator policy, independent review, and live Smalls
state. Broken sandbox links, absent companion files, and unsupported claims in
those documents must not be copied into acceptance criteria as if verified.

## 2. Program outcome and success conditions

### 2.1 Outcome

One operator can direct a small number of visible agents through long-running,
cross-host work while trusting that:

- exactly one authority accepts lifecycle mutations;
- a retried command cannot apply twice;
- every state transition has authenticated authorship and one transactional
  causal event;
- task JSON, task graph, current-state Markdown, and JSONL are rebuildable
  projections rather than competing writers;
- routine procedures run deterministically without repeated LLM planning;
- implementation work is isolated and scope-checked;
- runtime persistence never creates authority or hidden agents;
- context and memory improve retrieval without becoming project truth;
- changes to the harness are evaluated before promotion;
- operator approvals bind to the exact action/payload they authorize.

### 2.2 Program-level exit criteria

The program is complete only when all applicable criteria pass:

1. Every production lifecycle mutation uses the sanctioned authority command
   layer; direct production SQLite writers are either removed or explicitly
   allowlisted as internal authority modules.
2. The crash-after-commit/before-reply test produces exactly one transition,
   one canonical event, and one stable replay result across 100 deterministic
   repetitions.
3. All lifecycle projections rebuild from authority state and canonical events
   with stable content hashes; no projection is accepted as an independent
   mutation source.
4. Cross-host freshness remains truthful during authority loss, mirror delay,
   local writer collision, source-version mismatch, and recovery.
5. A representative release/review workflow resumes after process failure
   without repeating irreversible effects.
6. Task worktree validation detects every out-of-scope changed path in the
   test matrix and never discards pre-existing user changes.
7. Historical harness evaluations cover at minimum duplicate claim, self
   review, stale authority, projection drift, output-path violation, helper
   authority attempt, rotation failure, and partial release.
8. No model-backed worker runs outside an operator-inspectable/interruptible
   surface.
9. No helper, runtime session, imported snapshot, MCP client, or A2A peer can
   grant itself task, review, release, policy, or operator authority.
10. Every production cutover has a tested rollback that preserves user work
    and the one-writer invariant.

## 3. Non-negotiable invariants

These rules bind every work package:

- Operator intent, policy, high-authority approval, veto, and stop control
  remain with `bigboss`/Command Center.
- A run has at most one operator-designated coordinator. Startup presence or
  model/provider identity does not designate that role.
- One accountable task owner and a different independent reviewer are required
  for substantive deliverables.
- Smalls remains the sole writable production lifecycle authority.
- Biggie never mutates local `MAP_System/map.db`; it uses `map-authority`.
- Git source authority and SQLite runtime authority remain distinct.
- `map_events` may become canonical audit history only when it is written in
  the same transaction as the state change. Existing `events.jsonl` remains
  historical/projection input and must not be silently rewritten.
- Projections, workflow checkpoints, OTel telemetry, helper notes, agent
  memory, and session snapshots are never canonical task state.
- Runtime capability never implies MAP authority.
- All model-backed helpers use visible `wezterm-tab` surfaces unless Command
  Center provides equivalent inspect/send/approve/stop controls.
- Network-facing or write-capable components receive separate functional and
  security-framed review passes.
- The program never broad-resets, cleans, or overwrites a dirty worktree.
- A negative experiment is a valid result. It does not authorize production
  integration.

## 4. Current baseline: reuse, extend, or defer

| Research capability | Current MAP evidence | Program treatment |
|---|---|---|
| Single authority | Smalls authority gateway, Biggie mirror, TASK-299/310 | Extend existing seam; do not create a peer authority |
| Atomic claims/review separation | `db/claims.py`, TASK-268/274/278 | Preserve and route through transactional commands |
| Generated state | TASK-279 active-state projection | Generalize to all runtime lifecycle projections |
| Idempotency/checkpoints | TASK-155/161 JSONL helpers | Reuse concepts/tests; move enforcement into authority transaction |
| Scope/retry budgets | TASK-283 preflight/post-run detection | Integrate into runtime/worktree contract; do not overclaim OS enforcement |
| Context rotation | TASK-271 checksum-bound continuity | Preserve; repair remote transfer/finalize reliability before expanding |
| Retrieval/context | TASK-259-263, 284-285 experiments | Keep offline; production adoption only after fresh thresholds pass |
| Helper governance | durable notes/model tiers/visibility/capacity | Keep bounded; persistent profile may be standby, not permanent authority |
| Authority freshness | TASK-310/314/316 | Phase 0 blocker: current real-load collision proves more work is needed |
| Cross-host source convergence | TASK-307/308/315 and code-sync plan | Use as deployment foundation; verify actual Smalls revision before migration |
| Event history | `events.jsonl`, event validation, session replay | Quarantine corruption; migrate forward without fabricating history |
| Agent skills | procedural docs/scripts, no repository skill set found | Adopt standard `.agents/skills` progressively after command contracts stabilize |
| Deterministic flows | many scripts but no unified resumable flow contract | Build a thin native flow first; compare Lobster only after requirements freeze |
| Runtime adapters/worktrees | partial plans and ad hoc worktree use | Build contract and task-worktree pilot before persistent supervisor |
| OTel/evals | metrics and tests, no unified causal telemetry/eval corpus | Start minimal spans with first new command; mature before refinement |
| Policy as code | pre-dispatch checker and prose policy | Define engine interface first; compare simple native rules with Cedar/OPA |
| Prime/MCP/A2A | no production need proven | Conditional boundary adapters only; never control-plane replacements |

## 5. Program governance and role map

### 5.1 Human and core roles

| Role | Recommended worker | Responsibility | Cannot do |
|---|---|---|---|
| Operator | `bigboss` | Designate coordinator, approve scope/policy/destructive/external/dependency decisions, accept cutovers | Delegate operator authority by implication |
| Program coordinator | One operator-designated current Claude or Codex core identity | Maintain dependency ledger, route tasks/reviews, surface gates, prevent collisions | Own every implementation or approve own deliverables |
| Implementation lead | Current Codex core identity | Precise code/schema/tests, worktree/runtime/authority implementation | Self-review or bypass Smalls |
| Architecture/evaluation lead | Current Claude core identity | Architecture packets, threat models, evaluation design, independent review of Codex work | Treat design authorship as automatic implementation approval |
| Deterministic verifier | Current Pi fixed-roster identity, bounded support | Frozen test matrices, reproducibility runs, measurement packets | Final judgment or canonical mutation |
| Librarian | Current Librarian fixed-roster identity, bounded read-only support | Source maps, duplication checks, backlink/citation/evidence integrity | Promote research or mutate core truth directly |

Command Center UI work remains core-owned: Codex implements under a claimed
task, Claude independently reviews, and the operator performs visual/workflow
acceptance. No standing UI model is required.

The operator must explicitly designate the program coordinator before Phase 1.
Recommendation: use a Claude core identity as coordinator/architecture lead and
Codex as implementation lead, but only after continuity and authority routing
are healthy. If Claude owns a phase's substantive design artifact, Codex should
review that artifact; Claude may later review separately owned Codex code only
when the review criteria come from an operator-approved decision rather than
Claude's unreviewed personal design.

### 5.2 Helper policy for this program

Helpers are created only against a claimed task or a formally routed review.
Each gets a visible terminal, durable note, bounded packet, owner, model tier,
outputs, and stop condition.

| Helper profile | When used | Default tier | Output | Stop condition |
|---|---|---|---|---|
| Standing review packet helper | Routine submitted task with clean conflict separation | Sonnet default; Haiku for explicit checklist | Draft Review Standard packet; no formal approval | Packet delivered and owner/reviewer integrates it |
| Authority/security reviewer | `map-authority`, authz, approval, network/write surfaces | Sonnet; Opus only after separate escalation | Threat model/adversarial findings | Security pass delivered and helper retired/standby |
| Fault-injection verifier | Crash, retry, concurrency, rollback matrices | Haiku for scripted execution; Sonnet if diagnosis needed | Machine-readable results plus discrepancies | Frozen matrix completed |
| Source/inventory helper | Large bounded file maps or external primary-source checks | Haiku or Librarian lane | Source register with freshness/canonicality | Register complete |
| Temporal/Lobster/Cedar POC specialist | Only after dependency approval and frozen comparison | Sonnet | Isolated POC evidence, not adoption decision | Scorecard complete; environment removed or archived |
| Retrieval evaluator | Blinded context-builder holdout | Separate helper from corpus author | Frozen judgments and uncertainty | All packets scored; no treatment access |

Capacity rule:

- Four is a policy ceiling for concurrently active helper notes, not a target.
- Standing profiles should be `standby` when unassigned and activated only for
  a packet. Do not consume active capacity merely to keep a model session open.
- Sequential authority work remains with one owner; do not parallelize tightly
  coupled state code.

### 5.3 Review separation matrix

| Deliverable | Owner | Required reviewer |
|---|---|---|
| Program architecture decision | Program coordinator or Codex planner | Other core agent + operator approval |
| Authority command/schema implementation | Codex | Claude functional review + separate security-framed pass |
| Projection implementation | Codex | Claude |
| Repository skills authored by Claude | Claude | Codex |
| Deterministic flow implementation | Codex | Claude |
| Worktree/runtime implementation | Codex | Claude + security pass |
| Evaluation corpus curated by Librarian/Pi | Accountable core owner | Other core checks provenance/blinding |
| Temporal/LangGraph comparison | One core owns experiment | Other core reviews frozen method and result |
| Policy model/decision | Claude or coordinator | Codex technical challenge + operator approval |
| Command Center UI | Codex | Claude + operator visual/workflow acceptance |
| Final program closeout | Program coordinator | Other core + operator acceptance |

## 6. Workstream topology

The program uses one critical path and four bounded supporting tracks:

```text
Critical A: P0 recovery -> P1 decision -> P2 transaction -> P3 projections
                                      |-> P4 flows/skills
                                      |-> P5 worktrees/runtime contract

Evidence B: P0 baseline -> telemetry in P2 -> P6 evaluation corpus
                                                |-> P7 executor POCs
                                                |-> P8 policy POCs

Context C: P6 evaluation foundation -> P9 context builder/memory

Runtime D: P3 + P5 + P7 decision -> P10 supervised persistent runtime

Evolution E: P6 + stable P8/P10 -> P11 refinement; interoperability conditional
```

No phase number authorizes its tasks. Every work package must still be promoted
and claimed through Smalls after authoritative collision checks.

### 6.1 Relative delivery map

These are planning sizes, not calendar promises. A phase may contain multiple
independently reviewed MAP tasks; no phase should be claimed as one oversized
task.

| Phase | Relative effort | Critical dependency | Primary owner class | Helper demand | Operator touch |
|---|---:|---|---|---|---|
| 0. Trustworthy baseline | M-L | None; current blocker | Existing task owners/new routed successors | Scripted verifier + Librarian, sequentially | Only for unresolved authority/rotation choices |
| 1. Architecture contract | M | Phase 0 | Claude design / Codex schema, cross-reviewed | Source inventory; security challenge | D0 and D1 |
| 2. Transactional claim slice | M | Approved Phase 1 contract | Codex | Fault-injection verifier | D2 before production pilot |
| 3. Lifecycle/projection migration | L | Phase 2 proof | Codex | Projection/rebuild verifier | Cutover windows as needed |
| 4. Flows and skills | M | Stable command contracts | Codex/Claude by artifact | Checklist verifier | None for the native flow; D3 before Lobster, containers, or another dependency |
| 5. Runtime/worktree isolation | M-L | Stable lifecycle seam | Codex | Adversarial scope verifier | Approval only for new sandbox/dependency |
| 6. Telemetry/evaluations | L, incremental | Starts in Phase 2; matures after 3/5 | Claude method / Codex instrumentation | Librarian + Pi + blinded evaluator | Approve material success criteria |
| 7. Durable executor decision | M POC | Phase 6 baseline | One core experiment owner | One isolated POC specialist | D3 |
| 8. Authorization/budgets | M-L | Stable commands + Phase 6 evidence | Claude policy / Codex adapter | Security/adversarial helper | D3 and D4 |
| 9. Context/memory/snapshots | L | Phase 6 corpus | Codex owner / Claude reviewer for P9.1; separately assigned owners for P9.2-P9.3 | Retrieval evaluator + Librarian | Only if new service/dependency |
| 10. Persistent runtime | L, conditional | Phases 3, 5, and 7 decision | Codex | Failure/recovery verifier + security pass | D5 |
| 11. Refinement/interoperability | M-L, conditional | Stable eval/policy/runtime | Split by proposal/adapter | Blinded evaluator or protocol specialist | D6 |
| 12. Cutover/closeout | M | All adopted gates | Coordinator | Independent closeout verifier | D7 |

The critical-path implementation begins with Phase 0 and ends at Phase 6 for a
safe, observable core. Phases 7-11 are decision branches, not assumed scope:
MAP can close successfully without Temporal, a dedicated policy engine,
persistent model workers, semantic memory, MCP, A2A, or Prime if their measured
benefit does not clear the frozen adoption thresholds.

## 7. Phase 0 — Recover a trustworthy baseline

### Purpose

Stop planning on top of a system whose mirror routing, rotation transfer, event
history, release backlinks, helper count, and authority-host program revision
currently disagree or fail under load.

### Work packages

#### P0.1 Resolve current authority and rotation incidents

- Preserve the exact TASK-316 real-load failure: watcher stopped, first sync
  reported installation but freshness metadata stayed stale, second sync
  detected another local `events.jsonl` writer and failed closed.
- Identify every Biggie process that writes a mirrored path.
- Confirm Smalls deployed versions of `map_authority.py`, `map_task.py`,
  `claims.py`, and `context_rotation.py` against reviewed commits.
- Diagnose the current remote `rotation-transfer` exit 1/empty-stderr failure
  on Smalls. Do not blind-retry or invent another transport.
- Create a successor task to TASK-316 if the approved quiet-window design is
  insufficient under real load; do not reopen or silently edit released work.

Owner: existing recovery/authority owner designated through TASK-309 or a new
operator-routed successor. Reviewer: other core, with security framing.
Helper: Librarian for writer/version inventory; no model helper edits.

Exit gate:

- three consecutive scheduled sync cycles succeed under the normal fixed
  roster and watcher load;
- `map-authority status` and `route` agree on freshness and revision;
- one verified context rotation completes prepare -> ACK -> remote transfer ->
  finalize without direct DB access;
- watcher/service states are restored and recorded.

#### P0.2 Repair durable validation debt

- Quarantine and repair the NUL corruption at `events.jsonl` line 18,785 by a
  reviewed append-only-preserving procedure; retain original bytes/hash as
  evidence rather than silently rewriting history.
- Correct TASK-315's stale `/home/home/...` release backlink through authority
  or a provenance repair record, not local SQL.
- Triage wikilink findings into scanner false positives, resolvable shorthand,
  ambiguous `AGENTS`, and genuinely missing memory evidence.
- Reconcile active helper notes; complete/stale helpers stop consuming capacity.
- Re-run task, event, shared-state, review, release, authority, and full test
  validators from the exact source revision intended for deployment.

Owner: Codex for mechanical repair implementation; Claude review. Librarian
provides the already-written audit and confirms post-fix backlink integrity.

Exit gate:

- one reproducible green baseline report records source revision, authority
  revision, commands, expected exceptions, and hashes; and
- runner output reports `helper_capacity.active <= helper_capacity.maximum`
  and `helper_capacity.maximum == 4`. A renamed or replacement metric must be
  mapped explicitly; hiding active notes by changing labels does not pass.

#### P0.3 Close or explicitly carry existing lifecycle backlog

- Complete independent review/disposition of TASK-309.
- Inventory APPROVED tasks 295/297/299-303/305/307-308/311/313/316-317 and
  record which are released, deliberately deferred, superseded, or blocked.
- Do not make the research program own unrelated TASK-318 creative work.
- Confirm no nonterminal task owns proposed Phase 1-3 output paths.

Exit gate: no hidden collision or ambiguous predecessor remains on the first
authority-slice paths.

### Combined Phase 0 exit gate

Phase 1 cannot start until P0.1, P0.2, and P0.3 all pass in the same baseline
packet from the intended source and authority revisions. A two-of-three pass,
an earlier green packet from another revision, or an exception recorded only
in prose does not satisfy this roll-up gate.

### Rollback

Phase 0 contains repairs and diagnostics only. Every repair preserves original
evidence and can restore the last valid source/authority snapshot. No local
mirror database mutation is permitted.

## 8. Phase 1 — Freeze the architecture contract

### Purpose

Decide the boundary before building a daemon or installing dependencies.

### P1.1 Architecture decision packet

The packet must decide:

- existing `map-authority` command layer is the sole production mutation seam;
- in-process command modules precede any Unix socket/daemon transport;
- current-state rows plus transactional canonical events form the authority;
- task JSON, graph, current-state Markdown, and JSONL are projections;
- workflow checkpoints and OTel are noncanonical;
- authenticated server context supplies actor identity; clients cannot assert
  `bigboss` or another agent identity;
- optimistic `expected_version` and business `idempotency_key` semantics;
- operator approval object semantics: proposal hash, scope, expiry,
  consumption/single-use, approver identity;
- compatibility and rollback periods;
- per-project namespace decision before new runtime budgets/telemetry spread.

Recommended owner: Claude architecture lead. Reviewer: Codex. Operator gate:
AUTHORITY/SCOPE approval tied to the exact decision artifact hash.

### P1.2 Schema and command contract

Proposed additive authority tables/columns, subject to schema review:

```text
tasks.runtime_version
map_events
command_dedup
projection_cursors
operator_approvals
executions (reference only; not workflow checkpoints)
```

Every mutation command accepts or derives:

```text
authenticated actor/session/runtime/workspace
operation + resource
expected_version
idempotency_key
correlation_id + trace_id
caused_by
request payload hash
```

The schema design must specify concurrency, `SQLITE_BUSY`, dedup expiry,
payload privacy, event retention, projection cursor recovery, migrations, and
rollback. Do not fabricate canonical events for legacy history; legacy JSONL
is imported only as explicitly historical/nontransactional evidence if useful.

Owner: Codex. Reviewer: Claude plus security pass. Librarian checks conflict
with existing schema/plans.

### Exit gate

- operator-approved decision;
- independently approved schema/command specification;
- threat model covers identity spoofing, stale version, duplicate retries,
  post-commit response loss, partial projection, cross-host replay, malformed
  request, and approval substitution;
- no production code change yet depends on an unapproved external component.

## 9. Phase 2 — Transactional authority slice

### Purpose

Prove the smallest end-to-end invariant on `task.claim` before migrating other
verbs.

### P2.1 In-process command layer

Implement modules beneath existing `map-authority`, for example:

```text
commands / queries / lifecycle / authz / events / idempotency / projections
```

The first command transaction:

1. authenticate/construct request context outside model-controlled payload;
2. begin SQLite write transaction on Smalls;
3. check idempotency key and payload hash;
4. check expected task runtime version;
5. authorize actor/action/resource/context;
6. validate lifecycle transition and lease rules;
7. update current task state/version;
8. append one canonical event;
9. store stable command result/dedup record;
10. commit;
11. return result;
12. asynchronously or explicitly rebuild projections.

Owner: Codex. Reviewer: Claude functional review and separate security pass.
Pi runs the frozen fault matrix; a security helper may draft adversarial cases.

### P2.2 Fault-injection matrix

Required cases:

- two concurrent claims;
- process death before transaction;
- death after state update but before event append (transaction rolls back);
- death after commit but before response;
- identical retry returns same result;
- same key/different payload conflicts;
- stale expected version conflicts;
- authority disconnect before/after request;
- duplicate SSH delivery;
- invalid client actor assertion;
- projection failure after commit;
- `SQLITE_BUSY` bounded retry behavior;
- malformed/oversized payload and bounded error text.

No chaos test targets production `map.db` or the real event log. Use disposable
authority fixtures and a staged Smalls deployment drill.

### P2.3 Minimal telemetry

Emit noncanonical OTel-compatible spans for command receipt, authz, transaction,
event append, projection, and response. Redact content/secrets. Losing telemetry
must not change command correctness.

### Cutover and rollback

- Shadow-read the new query output against existing claim logic first.
- Enable new `task.claim` behind a reversible feature/config gate on Smalls.
- Never dual-write through old and new command paths. During compatibility,
  old clients call the new internal command implementation.
- Rollback routes clients to the prior implementation while retaining additive
  tables; no destructive down-migration during the observation window.

### Exit gate

The program-level crash-after-commit proof passes, command/event counts match,
and one staged cross-host claim is visible in authority state and projections.

## 10. Phase 3 — Migrate lifecycle verbs and make projections one-way

### P3.1 Verb migration order

Migrate one bounded verb at a time:

1. heartbeat/release expired lease;
2. submit plus durable submission authorship;
3. review claim/release;
4. reject/changes requested;
5. approve;
6. release;
7. create/describe/amend/add-output/retire;
8. agent registration and rotation transfer/restore;
9. operator approvals and halt operations.

Each verb repeats P2's concurrency/retry/security matrix appropriate to its
effects. Approval/release retain independent-review and risk-tier gates.

### P3.2 Projection contract

Build deterministic projectors for:

- `tasks/TASK-*.json` runtime fields;
- `workflow/task_graph.json` runtime fields;
- generated sections of `shared/current-state.md`;
- `events/events.jsonl` forward projection;
- Command Center read models.

Immutable task definition fields may remain Git-authored, but runtime fields
come only from authority state. Define a clear merge boundary so a projector
cannot erase task specification prose.

Required projector properties:

- deterministic ordering and bytes;
- atomic temp-write/replace;
- revision watermark and cursor;
- replay after interruption;
- stale/newer projection refusal;
- no parsing of free prose as lifecycle truth;
- explicit contradiction if an old client writes a projection directly.

Owner: Codex. Reviewer: Claude. Pi runs rebuild/idempotence matrices. Librarian
checks backlinks and human readability.

### P3.3 Direct-writer retirement

Inventory all code that writes task state, events, mirrors, status, review, or
release records. Classify each as:

- internal authority module;
- projection writer;
- noncanonical telemetry/runtime state;
- prohibited legacy writer to remove;
- explicitly separate project truth writer.

Add a validator/static allowlist that fails when a new production lifecycle
writer bypasses the command seam.

### Exit gate

- all lifecycle verbs use the command seam;
- projection rebuild matches live generated files;
- old direct lifecycle writes fail closed;
- Smalls/Biggie source and authority revisions are proven during cutover;
- rollback drill restores the last approved command implementation and
  rebuilds projections without losing committed state.

## 11. Phase 4 — Deterministic flows and Agent Skills

These two tracks start only after stable command contracts exist.

### P4.1 Thin MAP-native deterministic flow

Start with one release-verification flow because its steps are known and its
judgment points are explicit:

```text
load authoritative task/review
  -> validate task/projections/review
  -> run declared verification
  -> request operator approval only if policy requires
  -> invoke authority release command
  -> rebuild/validate projections
  -> emit result
```

Flow requirements:

- typed step inputs/outputs;
- per-step timeout/retry policy;
- retry only transient failures;
- durable step state separate from canonical task state;
- explicit human interrupt/approval;
- idempotent authority calls;
- resume and cancel;
- no shell-string interpolation for untrusted data;
- visible status and stop control.

After native behavior is frozen, compare Lobster against the same fixture and
score correctness, dependencies, recovery, security surface, maintenance, and
token savings. Adoption requires an operator-approved dependency decision.

Owner: Codex. Reviewer: Claude. Pi executes the frozen comparison. No helper
reasoning is needed for the mechanical happy path.

### P4.2 Repository Agent Skills

Create standard `.agents/skills/` packages progressively:

```text
map-task
map-review
map-release
map-context
map-handoff
map-repair
map-research
```

Each skill wraps sanctioned commands and points to canonical policy; it does
not reproduce authority rules or expand permissions. Begin with `map-review`
and `map-task`, measure context/token reduction and gate recall, then continue.

Recommended owner: Claude for skill instructions. Reviewer: Codex. Librarian
checks canonical links/freshness. A fresh bounded helper runs blinded skill vs.
baseline cases.

Skill promotion target:

- at least 20% lower procedural context on the pilot corpus;
- no reduction in required-gate recall;
- no new authority/scope violation;
- complete fallback when a skill loader is unavailable.

### Exit gate

One deterministic flow completes and resumes safely; two skills show measured
benefit before the remaining skills are authored.

## 12. Phase 5 — Isolated work and provider-neutral runtime contract

### P5.1 `AgentRuntime` contract

Define a provider-neutral interface without starting a persistent daemon:

```text
start / resume / send / steer / pause / cancel
snapshot / health / capabilities / usage / artifacts
```

The contract includes runtime identity, MAP agent identity, session ID,
workspace ID, task/goal reference, budgets, visibility/control endpoint,
children, and last checkpoint. Runtime identity is not lifecycle authority.

Owner: Codex. Reviewer: Claude. The operator accepts the inspect/send/approve/
stop semantics through a concrete Command Center workflow check.

### P5.2 Per-task Git worktree pilot

Lifecycle:

1. verify task claim and output paths;
2. record clean/dirty base without altering user work;
3. create a task branch/worktree from an approved base revision;
4. run worker with scoped workspace metadata;
5. compare changed/untracked paths against normalized `output_paths`;
6. run tests and create patch/commit evidence;
7. independent review of exact bytes/commit;
8. integrate through approved Git flow;
9. retire worktree only after evidence is preserved.

Start at L1 worktrees. Containers are a later security enhancement, not a
prerequisite. Any rootless container POC must never mount the Docker/Podman
socket or broad credentials and requires operator dependency/security approval.

Owner: Codex. Reviewer: Claude + security pass. Pi runs path/symlink/untracked
fixtures. Librarian checks task-output provenance.

### P5.3 Runtime goal record pilot

Keep three distinct objects:

- MAP task: desired outcome and canonical lifecycle;
- runtime goal: one session's bounded attempt;
- continuation policy: when the supervised runtime continues, stops, or asks.

Runtime goal records are noncanonical and reference exact task/version,
verification gate, token/turn/time/tool/helper budgets, and stop reason.
An agent saying “done” cannot satisfy the MAP task; it only ends its attempt
after configured verification or records why it stopped.

### Exit gate

Two different provider adapters complete the same disposable task fixture in
isolated worktrees, produce equivalent artifacts, obey visibility/stop rules,
and cannot write outside scope through sanctioned tooling.

## 13. Phase 6 — Observability and harness evaluation

Minimal telemetry began in P2; this phase makes it useful for decisions.

### P6.1 Causal trace model

Trace one task across intake, route, runtime attempt, tool calls, tests,
submission, review, rework, approval, release, and projection. Use standard
OpenTelemetry GenAI attributes where stable and a versioned `map.*` namespace
for MAP identity. Do not record prompts, secrets, sensitive file contents, or
raw credentials by default.

`map_events` remains canonical audit history. OTel remains disposable
behavioral telemetry.

### P6.2 Historical evaluation corpus

Convert real MAP failures into frozen cases:

- duplicate claim and response-loss retry;
- self-review and submission-authorship conflict;
- stale/invalid authority;
- writer collision during mirror install;
- task JSON/graph/SQLite contradiction;
- output-path violation;
- bad/blank task metadata;
- helper without note/model/owner;
- helper authority attempt;
- rotation snapshot/path/task drift;
- remote rotation-transfer rejection;
- partial release/projection failure;
- context retrieval false positive/abstention;
- premature “done” before verification.

Each case records inputs, expected decision, prohibited outcomes, observable
metrics, and whether it is deterministic, fault-injection, or model-evaluated.

Owner: Claude for evaluation method; reviewer: Codex. Librarian curates source
evidence; Pi runs deterministic cases. A fresh helper may score agentic cases
only after labels are frozen by a different worker.

### P6.3 Scorecard

Track:

- task/flow success;
- policy and scope violations;
- duplicate effects;
- retries and repeated identical failures;
- operator interruptions/approval load;
- tokens, turns, tool calls, wall time, known cost;
- context bytes and retrieval accuracy;
- reviewer findings/rework cycles;
- recovery time and lost-work indicators;
- helper utilization and discarded output.

### Exit gate

Every subsequent POC/change can run against a versioned baseline corpus, and
telemetry loss has been proven non-fatal to lifecycle correctness.

## 14. Phase 7 — Durable-execution decision

### P7.1 Compare deeper LangGraph persistence and Temporal

Use the same representative workflow and failure matrix:

- long operator pause;
- worker/orchestrator restart;
- provider outage;
- duplicate signal;
- claim/review/rework loop;
- budget exhaustion;
- authority unavailable;
- cancel/rollback;
- checkpoint schema upgrade.

Option A deepens existing LangGraph and separates framework checkpoint blobs
from canonical `map.db`. Option B runs a bounded Temporal POC in an isolated
environment. No production Temporal service is installed without operator
approval for dependency, service, storage, network, and maintenance burden.

Owner split:

- Codex owns LangGraph/native implementation.
- A visible Sonnet specialist may build the bounded Temporal POC under a core
  owner after dependency approval.
- Claude owns the frozen comparison method or synthesis, but whichever core
  did not own the synthesis performs the formal review.

Decision score:

- correctness under failure;
- exactly-once effects via idempotent authority calls;
- operational and cognitive complexity;
- local/cross-host recovery;
- observability;
- upgrade/backup burden;
- resource use and operator maintenance;
- ability to stay visible and controllable.

### Exit gate

Operator records one of: deepen LangGraph, adopt Temporal for selected flows,
or defer. A negative/defer result keeps the native flow and is not failure.

## 15. Phase 8 — Mechanical authorization and budgets

### P8.1 Policy engine interface

Freeze a small interface:

```text
authorize(principal, action, resource, request_context)
  -> ALLOW | DENY | APPROVAL_REQUIRED + bounded reason/policy version
```

Server-derived identity and exact operator approvals are prerequisites.
Begin with native deterministic rules for:

- no self-review;
- helper cannot approve/release/change policy;
- task owner/output-path/workspace match;
- Biggie cannot mutate local production DB;
- authority/policy/destructive/external actions require the right approval;
- stale authority cannot dispatch/mutate from mirror assumptions.

Then compare Cedar and OPA/Casbin only if native rules become difficult to
audit or express. Cedar examples are conceptual until validated by its real
toolchain.

Owner: Codex implementation, Claude policy/threat-model owner, separate core
review, security helper packet, operator approval for production enforcement.

### P8.2 Budgets and circuit breakers

Attach budgets to runtime goals/flows, not to task truth:

- tokens/turns/time/tool calls/retries;
- helper count/depth/concurrency;
- disk/network/known cost;
- per-step and per-run limits.

Classify errors before retry. Policy rejection, stale version, scope violation,
missing approval, and destructive confirmation are not transient. Budget
exhaustion returns evidence and a bounded extension request; it never silently
grants more.

Run accounting-only first. Blocking enforcement requires measured false
positive/negative evidence, independent review, operator approval, and a clear
rollback/override path.

### Exit gate

Adversarial tests prove clients cannot forge identity/approval/scope, and
budget/circuit-breaker decisions match the frozen corpus before enforcement.

## 16. Phase 9 — Context Builder, search, memory, and portable snapshots

### P9.1 Production-candidate Context Builder

Build on released FTS5/capsule/fingerprint/digest experiments; do not bypass
their negative results or CHANGES_REQUESTED history.

Retrieval order:

```text
exact task/decision/path/symbol
  -> FTS5/BM25
  -> structured retrieval capsules/fingerprints where validated
  -> optional semantic retrieval experiment
  -> canonicality/freshness/project/risk ranking
  -> bounded context packet
```

Every context item declares Required/Optional/Excluded, inclusion reason,
source, canonicality class, freshness, scope, and expansion route.
Canonicality outranks semantic similarity. Noncanonical memory cannot satisfy
a requirement for canonical evidence.

Acceptance thresholds, carried from prior pilots unless a reviewed experiment
changes them:

- task recall >= 0.90;
- exact/source recall >= 0.80;
- legitimate no-match abstention = 1.00;
- contradiction detection fails closed;
- source/path/time watermarks visible;
- measurable context reduction without gate-recall loss.

Accountable owner: Codex. Independent reviewer: Claude. Librarian builds the
source/canonicality registry. Separate helpers freeze truth and conduct blinded
evaluation; neither helper owns the adoption decision.

### P9.2 Typed noncanonical memory

Memory blocks may store obligations, working hypotheses, learned conventions,
recent failures, and specialist notes. Each carries:

```text
authority=NONCANONICAL
source / last_verified / scope / expires / sensitivity
```

No automatic promotion to task, decision, policy, or shared truth.

### P9.3 Portable MAP agent snapshot

Extend, do not replace, STATE_SNAPSHOT continuity. A portable runtime package
may include identity reference, runtime adapter, skill versions, current
task/version, runtime goal/checkpoint reference, memory references, context
summary, workspace manifest, budgets, child registry, and capabilities.

It never includes secrets or authority by implication. Import validates hashes,
paths, task state, source revision, live roster identity, and capabilities.

### Exit gate

A fresh agent completes blinded orientation/review fixtures with lower context
and no authority mistake; a cross-provider snapshot resumes in a disposable
task without transferring claims/review rights automatically.

## 17. Phase 10 — Supervised persistent runtime

This phase is conditional on P2/P3/P5/P7/P8/P9 evidence. Persistence before
authority, visibility, isolation, and recovery are proven would create a more
durable failure mode.

### Capabilities

- agent/session registry;
- detach/reconnect;
- crash detection and bounded restart;
- queued messages;
- runtime goals/budgets;
- child/helper registry;
- checkpoint/snapshot references;
- health/usage/artifacts;
- operator inspect/send/approve/stop surface.

The terminal may become a client rather than the process owner only when the
operator retains equivalent visibility and stop control. Closing a terminal
must not create an unreachable hidden worker.

Persistent helper identity means a resumable dormant profile, not perpetual
task/review/release rights. Idle profiles are `standby`; active capacity is
consumed only while a bounded assignment is running.

Owner: Codex runtime and Command Center implementation; Claude reviews
architecture/recovery; the operator performs UI/workflow acceptance; a
separate security pass covers any listener, credential, filesystem, or control
endpoint.

### Rollout

1. one deterministic/no-model process under supervisor;
2. one disposable visible model session;
3. detach/reconnect;
4. crash/recovery with no task mutation;
5. bounded task attempt through existing authority API;
6. helper lifecycle;
7. cross-host recovery drill;
8. opt-in production pilot;
9. default only after operator acceptance.

### Exit gate

Operator can inspect and stop every runtime, restarts cannot duplicate effects,
and loss of supervisor state cannot alter canonical task truth.

## 18. Phase 11 — Controlled refinement and conditional interoperability

### P11.1 `refine.propose`

Enable only after the evaluation corpus exists. Every proposal contains:

- observation and source trajectories;
- explicit hypothesis and metric target;
- exact skill/middleware/context/prompt/runtime change;
- scope and authority class;
- evaluation method and baseline;
- independent review;
- operator approval when policy/security/authority changes;
- version, rollback, retain/revert result.

The system may propose changes. It may not silently rewrite its governing
authority, permissions, review, release, or destructive-action rules.

### P11.2 MCP/A2A/Prime adapters — conditional

Build only for a concrete use case:

- MCP: read-only MAP queries/tools first. Mutations call the same authority
  commands and policy checks. MCP Tasks are external tool-job handles, not MAP
  tasks.
- A2A: external agent discovery/message/artifact adapter. Agent Cards advertise
  capability, not trusted identity or authority.
- Prime Agent: one `AgentRuntime` adapter and bounded comparison; never the MAP
  coordinator/control plane by default.

Every network/write surface receives functional and security reviews,
authentication, scoped credentials, malformed-input/path/injection testing,
rate/resource limits, and operator-approved deployment.

### Exit gate

At least one refinement proposal is evaluated and either retained or reverted
based on evidence. Interoperability may remain deferred with no program failure.

## 19. Phase 12 — Program cutover and closeout

### Cutover checklist

- freeze new lifecycle changes briefly at an operator-announced window;
- verify clean source revision and Smalls authority backup;
- verify Biggie dirty work is preserved in task worktrees/snapshots;
- deploy reviewed source to Smalls first;
- run schema migration and authority smoke/fault tests;
- rebuild projections and compare hashes;
- sync Biggie mirror and verify `FRESH`/matching authority revision;
- run Command Center, rotation, helper, release, and recovery scenarios;
- enable enforcement flags one at a time;
- observe through the approved window;
- record operator acceptance or rollback.

### Rollback checklist

- stop new command intake without mutating committed state;
- revert to last approved command implementation/config;
- retain additive schema/data and canonical events;
- rebuild projections from last accepted authority revision;
- restore service states and source revision through reviewed Git flow;
- confirm Smalls remains sole writer and Biggie mirror remains read-only;
- open a repair record for any divergence; never hand-edit mirrors as the fix.

### Closeout artifacts

- final architecture/decision records;
- schema and command reference;
- threat model and security reviews;
- migration/rollback runbook;
- evaluation corpus and before/after scorecard;
- operator guide and Command Center controls;
- source/authority revision manifest;
- residual-risk and deferred-adoption register;
- supersession annotations on prior plans, without deleting them.

## 20. Operator decision gates

| Gate | Decision | Earliest point |
|---|---|---|
| D0 | Designate one program coordinator | Before Phase 1 |
| D1 | Approve authority/scope architecture artifact by exact hash | End Phase 1 |
| D2 | Approve additive production schema migration/cutover window | Before Phase 2 production pilot |
| D3 | Approve new dependencies/services for Lobster, Temporal, Cedar/OPA, containers, or OTel backend | Before each isolated POC/install |
| D4 | Approve blocking authorization/budget enforcement after accounting-only evidence | End Phase 8 |
| D5 | Approve persistent runtime and any listener/control endpoint | Before Phase 10 production pilot |
| D6 | Approve network interoperability deployment | Before Phase 11 adapter production use |
| D7 | Accept final cutover or order rollback | Phase 12 |

Routine task progress, bounded helper routing, tests, documentation, and
noncanonical experiments do not require operator messages unless they hit a
blocker, conflict, privacy/scope/security risk, destructive action, external
publication/dependency, or the gates above.

## 21. Task promotion strategy

Do not create every task up front. Promote only the next independently
reviewable slice when its dependencies are proven.

Recommended first slate after Phase 0:

1. Architecture decision packet.
2. Schema/command/threat-model specification.
3. Transactional `task.claim` implementation and fault tests.
4. Independent functional review.
5. Separate security-framed review.
6. Smalls staged deployment/live verification.
7. Projection pilot.

Each task must declare exact output paths, risk fields, acceptance criteria,
forbidden changes, owner, reviewer class, source/authority revision, test
commands, rollback, and whether operator approval is already satisfied.

## 22. Stop conditions and anti-overdesign rules

Pause the program when:

- authority is stale/invalid or Smalls revision is unknown;
- an existing task owns an output path;
- a validator or independent review finds a state-authority contradiction;
- the next phase depends on an unreviewed proposal;
- a POC fails its frozen adoption threshold;
- helper capacity/visibility/ownership cannot be satisfied;
- a dependency, network, security, privacy, destructive, or publication
  decision lacks operator approval;
- source deployment would overwrite dirty user work;
- the program starts producing process documents that do not change behavior
  or measurable outcomes.

Explicitly avoid:

- a big-bang daemon rewrite;
- multiple lifecycle writers during “migration”;
- pure event replay for every current-state query;
- making current corrupted JSONL the canonical event store;
- installing Temporal/Cedar/vector databases because research called them
  promising;
- permanent active helpers without assignments;
- more agents by default;
- semantic retrieval before exact/canonical retrieval passes;
- self-improvement before evaluation;
- MCP/A2A as lifecycle authority;
- hidden persistent model workers;
- autonomous policy or scope expansion.

## 23. Plan review questions for Claude

The independent reviewer should answer explicitly:

1. Does any phase create a second authority or dual-write interval?
2. Does the plan duplicate released or active tasks/plans?
3. Is the ordering safe, especially API-before-supervisor and
   evaluation-before-refinement?
4. Are owner/reviewer assignments genuinely conflict-separated?
5. Are helper roles bounded, visible, and capacity-aware?
6. Are functional and security reviews separate where required?
7. Can every production cutover roll back without data/user-work loss?
8. Does the plan treat current cross-host/rotation/event corruption as a
   prerequisite rather than hiding it inside future architecture?
9. Are acceptance thresholds measurable and resistant to gaming?
10. Which work packages should be removed, merged, reordered, or made
    conditional?

## 24. Current review status

- Codex self-check: complete; `git diff --check` passed. Repository-wide
  Librarian validation still reports 22 pre-existing findings outside this
  artifact, so those are tracked baseline debt rather than suppressed here.
- Claude independent review: complete with `claude-lab-lote` on Smalls (hcom
  #17904; exact historical remote identity remains in that record). Disposition:
  `reviewed-ready-for-operator-decision`; no blockers.
- Required finding R1 resolved: P0.2 now requires runner-reported active helper
  capacity at or below the configured ceiling of four.
- Required finding R2 resolved: P9.1 now names Codex as the single accountable
  owner and Claude as independent reviewer in both the delivery map and work
  package.
- Recommended clarification Rc1 resolved: the Phase 4 native flow needs no
  routine operator touch, while Lobster/containers/dependencies still require
  D3.
- Recommended clarification Rc2 resolved: one combined Phase 0 gate requires
  P0.1, P0.2, and P0.3 to pass together on the intended revisions.
- Operational recommendation Rc3 accepted: the repeated rotation-transfer
  failure is evidence for log inspection, not authorization for a third blind
  retry.
- Operator approval: pending decision; this reviewed proposal still does not
  authorize implementation or lifecycle mutation.
