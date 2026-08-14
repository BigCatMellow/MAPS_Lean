<!-- hpom: file: shared/decisions.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-15 -->
<!-- hpom: verified_against: DEC-028 proving-workflow direction (operator) -->
<!-- hpom: verified_against_prior: MAP_System audit 2026-06-29 -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Decisions

## DEC-001: Use File-Backed State First

Status: approved
Owner: command-center
Date: 2026-06-17
Applies-To: MAP system — data authority and state storage

Use JSON, Markdown, and JSONL files for the first collaboration layer. This keeps the system inspectable by both Codex and Claude Code before adding SQLite or a service runtime.

## DEC-002: LangGraph Is The Orchestrator

Status: approved
Owner: command-center
Date: 2026-06-17
Applies-To: MAP orchestration layer

LangGraph should route task states, review loops, and human pauses. It should not be the canonical database, artifact store, or full project memory.

## DEC-003: One Owner Per Active Task

Status: approved
Owner: command-center
Date: 2026-06-17
Applies-To: all active tasks

Each active task has one owner. Other agents may review, comment, or continue after a handoff, but should not silently edit the same owned output paths.

## DEC-004: Core Agents Plus Temporary Helpers

Status: approved — core agent list superseded by DEC-008
Owner: command-center
Date: 2026-06-17
Applies-To: agent coordination and helper policy

The command center keeps Codex and Claude as the two active core agents (see DEC-008). Core agents may request or start temporary helper agents for bounded work when parallelism is useful.

Temporary helpers are identified by a `helper-*` tag and documented in `MAP_System/inbox/helpers/`. Helper notes are durable project memory; the helper process itself may be opened, closed, forked, or replaced as needed.

Helper agents do not own final approval. A core agent remains accountable for task ownership, integration, review routing, and cleanup.

## DEC-005: Route Around Unavailable Agents

Status: approved
Owner: command-center
Date: 2026-06-17
Applies-To: agent routing and availability handling

When a core agent reaches a session limit or otherwise becomes unavailable, the system records that state in `MAP_System/agents/status.json`.

Available agents may continue ready work unless a task explicitly declares `required_agent` for the unavailable agent. Work owned by an unavailable agent should be handed off or queued in durable notes before another agent continues.

LangGraph should treat unavailable agents as routing constraints, not as a global stop condition.

## DEC-006: Visible Command-Center Agents

Status: approved
Owner: command-center
Date: 2026-06-17
Applies-To: all agent and helper launches

Command-center launches use an operator-reachable interface for core agents,
temporary helpers, and assistants. Visible terminal tabs are the default.
Headless `hcom` sessions are allowed only when the AI Command Center can
inspect the screen, send input, approve prompts, and stop the session. Hidden
background assistants are disallowed.

For routine in-scope work, agents may use session-level approval options when their tool offers them. This does not remove human approval requirements for destructive actions, external network calls, publication, final release, or changes outside the assigned scope.

## DEC-007: Manual Coordination For Gemini And Antigravity

Status: superseded by DEC-008
Owner: command-center
Date: 2026-06-17
Applies-To: Gemini and Antigravity coordination

Gemini remains in command-center planning state for work the operator chooses to assign manually. Antigravity also may require manual operator prompting until its command-center communication is reliable. Do not assume hcom alone can start or coordinate Gemini or Antigravity work; record ownership and status durably, and let the operator prompt those agents when needed.

## DEC-009: SQLite Is The Task Claiming Coordinator

Status: approved — 2026-06-19
Owner: command-center
Date: 2026-06-19
Applies-To: task claiming — TASK-014 onward

From TASK-014 onward, task claims are made atomically through `MAP_System/map.db` using `MAP_System/db/claims.py`. Agents must not manually edit task JSON files to claim work. The file-backed JSON files remain synchronized as a human-readable mirror of SQLite state, not as the authoritative claim source.

The claim protocol uses `UPDATE ... WHERE rowcount == 1` to guarantee that only one agent can successfully claim a task, even if multiple agents attempt simultaneously. Leases expire after 30 minutes of no heartbeat; `expire_leases()` returns them to READY.

## DEC-008: Codex And Claude Are The Two Active Agents

Status: approved — 2026-06-19
Owner: command-center
Date: 2026-06-19
Applies-To: all task planning and assignment
Supersedes: DEC-004, DEC-007

Gemini and Antigravity are not expected to be available for most of the project (confirmed by operator). Codex and Claude Code are the two active core agents going forward. All task planning, assignment, and workload splitting should assume only these two agents.

Codex handles implementation tasks. Claude handles review, architecture, synthesis, and planning tasks. Both may propose new tasks as work progresses. Temporary helpers remain available when parallelism is needed for a bounded scope.

## DEC-010: STATE_SNAPSHOT Handoff Format

Status: approved — 2026-06-19
Owner: command-center
Date: 2026-06-19
Applies-To: cross-session agent handoffs

Agents should use `STATE_SNAPSHOT` YAML handoff records for cross-session continuity when important context would otherwise live only in chat or a compacted transcript.

The canonical schema and worked example live in `MAP_System/workflow/templates/state_snapshot.yaml`. Snapshots belong in `MAP_System/handoffs/` and should point to durable files instead of copying large context.

Required snapshot coverage: `agent_id`, `session_id`, task context, active constraints, forward tasks, and project-local lexicon. Agents should emit a snapshot before session end when work is active, blocked, or pending review, and should read the latest relevant snapshot on resume before continuing the task.

## DEC-011: HPOM Is The Assignment Layer Over MAP

Status: approved — 2026-06-29
Owner: command-center
Date: 2026-06-29
Applies-To: MAP/HPOM integration and assignment discipline

HPOM means Human-Paced Orchestration Model for this MAP implementation.

MAP remains the durable task, memory, event, and state system. HPOM is the
assignment discipline layered over MAP. It decides whether work should go to
command-center, a core agent, a visible temporary helper, a local assistant, or
Aider based on:

- task clarity;
- authority required;
- model/tool fit;
- visibility and control;
- token and coordination cost.

HPOM does not replace MAP, HCOM, task ownership, review gates, or durable file
memory. It prevents wasteful assignment by requiring a worker-fit reason and a
stop condition before helpers or local assistants are used.

Current references:

- `shared/hpom.md`
- `shared/agent-capability-matrix.md`
- `notes/local-model-helper-guide.md`

Implementation order:

1. Enforce strict task promotion and claim-time metadata defense.
2. Add local assistant health checks.
3. Add local assistant wrappers only after health checks and visibility rules are
   proven.

## DEC-012: Canonical Repo Is Downloads/MultiAgentProject

Status: superseded by DEC-014
Owner: command-center (decision authority delegated to core agents via hcom #14454; recorded by claude-lab-rose, TASK-077)
Date: 2026-07-02
Applies-To: repo layout, git operations, cross-repo sync, Pathwell two-repo sync

`/home/home/Downloads/MultiAgentProject` (repo A) is the canonical working
repo. `/home/home/Projects/MultiAgentProject` (repo B) is frozen: no pushes,
no commits, no edits, no sync into or out of it until reconciled.

Basis: the TASK-063 repo-drift audit found B's git HEAD frozen at 2026-06-17
(4 commits behind A) while its working tree was manually overwritten with
newer uncommitted files — a hybrid state that would produce corrupt-looking
history if committed or pushed. All current validated work happened in A.

Reconciliation plan (in order, after TASK-065's git-operation lock exists):

1. Preserve B's `Projects/Pathwell/` and `Projects/Backups/` before anything
   else. These are gitignored private content and exist in B only as working
   files; a reclone or clean would delete them. They are stale relative to A
   but are the only copy of that private work outside A.
2. Single clean commit in A covering the audited/validated state (after the
   TASK-065 remediation batch lands and all validators pass).
3. Push A to `origin` — operator-visible step; announce via hcom first.
4. Reset or reclone B from the remote, then restore/refresh its private
   `Projects/Pathwell/` copy from A via file sync (not git).
5. Resume the Pathwell two-repo sync protocol only after steps 1-4 complete.

Until step 4 completes, a freeze marker should be placed in B
(deferred at codex-lab-limo's request until the git lock tooling exists).

Supersession note, 2026-07-02: TASK-079 completed the reconciliation sequence.
Later live lab sessions and authorized pushes moved to
`/home/home/Projects/MultiAgentProject`. DEC-014 supersedes DEC-012's
path-specific canonical repo rule.

## DEC-013: Synthesis And Experiment Record Types Stay Active, Not Mandatory

Status: approved
Owner: command-center (decision delegated via hcom #15008; recorded by claude-lab-rose, TASK-082)
Date: 2026-07-02
Applies-To: emergence system usage

Report Phase 2.4 asked whether the never-used synthesis and experiment
emergence types should be kept, tested, or marked advanced/optional.

Decision: both stay active and first-class, used only when genuinely
warranted — never as ceremony. A synthesis is warranted when multiple
insights turn out to share one deeper pattern (first real use: SYN-0001,
"two readers, one truth," drawn from six of this week's incidents). An
experiment is warranted when a claim is testable before being promoted
(none yet; the next candidate should use it rather than promoting untested).
`map_emergence.py stale` treats absence of SYN/EXP records as normal, not
as debt.

## DEC-014: Canonical Repo Is Projects/MultiAgentProject

Status: approved
Owner: command-center (operator confirmation via hcom #17759; recorded by codex-lab-limo, TASK-090)
Date: 2026-07-02
Applies-To: repo layout, git operations, command-center lab sessions, RnS watcher state
Supersedes: DEC-012

`/home/home/Projects/MultiAgentProject` is the canonical working repo for
current MAP work.

Basis:

- TASK-079 completed the DEC-012 reconciliation plan.
- The previous canonical path, `/home/home/Downloads/MultiAgentProject`, is no
  longer the live command-center working path.
- Current lab sessions, task state, CommandCenterUI work, RnS watcher runtime,
  and recent authorized pushes are operating from
  `/home/home/Projects/MultiAgentProject`.
- Operator hcom #17759 instructed agents to stop waiting and continue work when
  work remains; Zaro explicitly confirmed in hcom #17774 that TASK-090 should
  treat #17759 as canonical-repo confirmation, with operator veto available on
  review.

Effect:

- `MAP_System/shared/canonical-repo.md` now names
  `/home/home/Projects/MultiAgentProject` as canonical.
- The old Downloads path is retired/non-authoritative if it reappears.
- Normal task-scoped commits and pushes may proceed from the Projects repo when
  owned paths are staged, validators pass, and MAP review/release gates are
  followed.
- Repository-global operations still require the git operation lock.

## DEC-015: Adopt the MAP Research System

Status: approved
Owner: command-center (directed via hcom #19306; built by claude-lab-valo, TASK-103)
Date: 2026-07-03
Applies-To: knowledge acquisition, research artifacts, decisions fed by research

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified the Research System as
the highest-priority missing MAP system: MAP could move work safely and
capture ideas safely, but had no formal process for establishing that a
claim is true, current, and sourced before it became project truth.

Effect:

- `MAP_System/RESEARCH_SYSTEM.md` defines the research flow: Research
  Question → Research Brief → Source Map → Source Evaluation → Claim
  Evidence Matrix → Assumption Register → Research Summary → Decision or
  HPOM Task.
- `MAP_System/research/README.md` is the working quick-start.
- `MAP_System/templates/research/` holds the six research templates.
- Research conclusions that change project truth are still recorded as
  normal `DEC-NNN` entries here; the Research System does not bypass the
  decision log or HPOM review/release gates.
- Unsourced claims used in tasks or decisions must be logged in an
  Assumption Register, not silently absorbed into architecture.

## DEC-016: Adopt the MAP Self-Repair System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-105)
Date: 2026-07-03
Applies-To: repair behavior across MAP validators, reconciliation, and health checks

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Self-Repair as gap
#2: MAP already had repair behavior (validators, `reconcile_agents.py`,
`map_emergence.py stale`, `map_metrics.py`, `local_assistant_health.py`,
`test_exporter_invariants.py`) but no formal module tying it together.

Effect:

- `MAP_System/SELF_REPAIR_SYSTEM.md` defines repair severity levels
  (COSMETIC/DRIFT/BLOCKING/STRUCTURAL), automatic-repair permissions by
  HPOM tier, escalation rules, verification plans, and follow-up
  prevention.
- `MAP_System/repairs/README.md` is the working quick-start.
- `MAP_System/templates/repairs/` holds the Repair Record and Health Check
  Report templates.
- STRUCTURAL repairs still require command-center approval or a normal
  decision entry — Self-Repair does not grant agents new unilateral
  authority.
- Cross-linked to the Research System (DEC-015): stale/contradictory facts
  identified by research are DRIFT/BLOCKING repair targets here. Cross-
  linked to Emergence: recurring repairs should be captured as insights
  and promoted into permanent validator/template/decision fixes.

## DEC-017: Adopt the MAP Context System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-107)
Date: 2026-07-03
Applies-To: context assembly for tasks, reviews, research, and repairs

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified the Context System
as gap #3: `notes/context-routing-guide.md` and `shared/memory-map.md`
already define what to read and in what order, but context itself was not
formalized as a bounded packet with required/optional/forbidden content,
staleness handling, token-budget rules, and a local-summarizer boundary.

Effect:

- `MAP_System/CONTEXT_SYSTEM.md` defines the context packet format,
  required context by task type, forbidden context loading, stale-context
  handling (as a Self-Repair DRIFT target), token-budget rules, the
  local-summarizer role (Tier 3 per `shared/hpom.md`), and compression
  rules.
- `MAP_System/templates/CONTEXT_PACKET_TEMPLATE.md` is the packet template.
- Does not replace `notes/context-routing-guide.md`'s situational routing
  table — governs the packet that guide produces.
- Cross-linked to the Research System (DEC-015, packets carry Research
  Summaries not raw sourcing), Self-Repair System (DEC-016, stale context
  is a repair target), and Emergence (recurring context gaps become
  insights).

## DEC-018: Adopt the MAP Decision / Authority System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-108)
Date: 2026-07-03
Applies-To: who may decide what; Class: AUTHORITY

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified the Decision /
Authority System as gap #4: `shared/decisions.md` records decisions well
but does not formally define who is entitled to make them, what requires
command-center approval, or how proposals get promoted to binding
decisions.

Effect:

- `MAP_System/DECISION_AUTHORITY_SYSTEM.md` applies `shared/hpom.md`'s
  authority tiers specifically to decision rights, defines human-approval
  requirements, supersession rules, and proposal-to-decision promotion.
- `MAP_System/DECISION_CLASSES.md` defines five decision classes
  (ARCHITECTURE, OWNERSHIP, SCOPE, AUTHORITY, POLICY) with the minimum
  approval level each requires.
- Cross-linked to Self-Repair (STRUCTURAL repairs are proposals routed
  through this system) and Research (unresolved contradictions are
  proposals routed through this system).
- This decision is itself class AUTHORITY and required command-center
  direction to adopt, consistent with the rule it establishes.

## DEC-019: Adopt the MAP Human Interface System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-110)
Date: 2026-07-03
Applies-To: operator dashboard content contract; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified the Human Interface
System as gap #5: a CommandCenterUI prototype exists but there was no
formal definition of what an operator dashboard should surface without
requiring a full-repository read.

Effect:

- `MAP_System/HUMAN_INTERFACE_SYSTEM.md` defines the dashboard content
  contract: current status, pending decisions, blocked tasks, review
  queue, open repairs, open research questions, recent insights, agent
  availability, and next recommended actions, plus what counts as noise
  to exclude.
- Does not replace or require rebuilding the existing CommandCenterUI
  prototype (`artifacts/command-center-ui/`) — specifies what "done" looks
  like for its live hcom/MAP wiring.
- Cross-linked to Decision/Authority (DEC-018, pending decisions),
  Self-Repair (DEC-016, open repairs), Research (DEC-015, open questions),
  and Emergence (recent insights).

## DEC-020: Adopt the MAP Risk System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-111)
Date: 2026-07-03
Applies-To: risk classes, register, escalation, acceptance; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Risk as a secondary
gap: risk signals already exist (review severity, security second-pass,
current-state health issues, improvement backlog, constraints) but were
scattered without a register or escalation discipline.

Effect:

- `MAP_System/RISK_SYSTEM.md` defines risk classes (SECURITY, DATA,
  PROCESS, AVAILABILITY, KNOWLEDGE), reuses Self-Repair's four-level
  severity vocabulary, and defines register format, owners, review
  cadence, escalation, and acceptance.
- `MAP_System/templates/RISK_REGISTER_TEMPLATE.md` is the entry template.
- Risk acceptance is itself a decision routed through
  `DECISION_AUTHORITY_SYSTEM.md`, not a separate authority path.
- Cross-linked to Self-Repair (risk-bearing drift), Decision/Authority
  (acceptance routing), Human Interface (dashboard surfacing), and
  Research (unresolved contradictions as KNOWLEDGE-class risk).

## DEC-021: Adopt the MAP Security / Permissions System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-112)
Date: 2026-07-03
Applies-To: agent permission levels, destructive actions, trust boundaries; Class: AUTHORITY

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Security/Permissions
as a secondary gap: `AGENTS.md`'s Security Second Pass rule exists but
there was no formal permission-level model, destructive-action policy, or
trust boundary model underneath it.

Effect:

- `MAP_System/SECURITY_PERMISSIONS_SYSTEM.md` defines the trust boundary
  model (repo/machine/network), secret handling, and external-service
  policy; extends rather than replaces `AGENTS.md`'s Security Second Pass
  rule.
- `MAP_System/AGENT_PERMISSION_LEVELS.md` maps `shared/hpom.md` tiers to
  concrete read/write/shell/network permissions.
- `MAP_System/DESTRUCTIVE_ACTION_POLICY.md` defines what counts as
  destructive and the required confirmation/approval before a core agent
  acts.
- Cross-linked to Risk (SECURITY-class exposure), Decision/Authority
  (permission/scope changes require approval), and Self-Repair
  (STRUCTURAL security drift).
- This decision is itself class AUTHORITY and required command-center
  direction to adopt.

## DEC-022: Adopt the MAP Change Control System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-114)
Date: 2026-07-03
Applies-To: change requests, release records, rollback, changelog, retirement; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Change Control as a
secondary gap: Git tooling, the git operation lock, and the release-path
smoke checklist already exist, but change request format, release-record
requirements, rollback notes, changelog policy, migration notes, version
tags, and artifact retirement were not formalized.

Effect:

- `MAP_System/CHANGE_CONTROL_SYSTEM.md` formalizes the task file itself as
  the change request, names the existing Review Gate as the diff-review
  requirement, requires the `artifacts/releases/` checklist convention
  (already used by TASK-101 through TASK-112) for any task touching
  shared/template/canonical files, and defines rollback-notes,
  changelog, migration-notes, version-tag, and retirement rules.
- Declines to add a new version-tag scheme (TASK-NNN/DEC-NNN already serve
  that role) and a new MAP-system-level changelog file (decisions.md +
  events.jsonl already serve that role) — avoids duplicating existing
  identifiers per the documentation style guide's pushback rule.
- Cross-linked to Self-Repair (rollback-as-repair), Decision/Authority
  (AUTHORITY/POLICY-class changes), Risk (irreversible-change risk), and
  Human Interface (review-queue surfacing).

## DEC-023: Adopt the MAP Project Bootstrapping System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-115)
Date: 2026-07-03
Applies-To: new-project bootstrap workflow; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Project
Bootstrapping as a secondary gap: `notes/brain-organization-guide.md`
already defines a strong folder layout, but there was no formal workflow
requiring a new project to establish intent, assumptions, research needs,
quality standards, risks, and decision paths before its first task.

Effect:

- `MAP_System/PROJECT_BOOTSTRAPPING_SYSTEM.md` defines the six
  pre-first-task requirements and points to `RESEARCH_SYSTEM.md`,
  `RISK_SYSTEM.md`, and `DECISION_AUTHORITY_SYSTEM.md` as the source for
  three of them.
- `MAP_System/NEW_PROJECT_WIZARD.md` is the step-by-step checklist.
- Extends `notes/brain-organization-guide.md` rather than duplicating its
  folder layout; that guide now links back to this system.
- Skip conditions apply for trivial/throwaway projects per `shared/hpom.md`
  routing questions.

## DEC-024: Adopt the MAP Archive/Retention System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-117)
Date: 2026-07-03
Applies-To: archive statuses, retention rules, compaction cadence; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Archive/Retention
as a secondary gap: `notes/brain-compaction-guide.md` already defines
compaction mechanics, but archive statuses and the distinction between
archiving and artifact retirement were not formalized.

Effect:

- `MAP_System/ARCHIVE_RETENTION_SYSTEM.md` defines archive statuses
  (ACTIVE, COMPACTED, HISTORICAL), retention rules, and draws the line
  between retirement (`CHANGE_CONTROL_SYSTEM.md`, marking an artifact
  invalid in place) and archiving (moving genuinely inactive content out
  of the active-memory budget).
- Extends `notes/brain-compaction-guide.md` rather than duplicating its
  compaction trigger/cadence logic.
- Cross-linked to Self-Repair (stale-but-active content is a repair
  target, not an archiving target), Change Control (retirement vs.
  archiving distinction), and Context System (archive/historical content
  excluded from default context).

## DEC-025: Adopt the MAP Retrospective / Learning System

Status: approved
Owner: command-center (directed via hcom #19306/#19718; built by claude-lab-valo, TASK-118)
Date: 2026-07-03
Applies-To: end-of-cycle retrospective loop; Class: ARCHITECTURE

`MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md` identified Retrospective/Learning
as the last and weakest secondary gap: the improvement backlog and
Emergence capture individual findings, but no formal end-of-cycle loop
asked what worked, what failed, what caused rework, and what should become
permanent.

Effect:

- `MAP_System/RETROSPECTIVE_SYSTEM.md` defines the retrospective loop and
  its relationship to Self-Repair's incident-scale prevention (this system
  runs at cycle scale instead).
- `MAP_System/templates/RETROSPECTIVE_TEMPLATE.md` is the record template.
- Includes RETRO-0001, a worked retrospective of the TASK-103 through
  TASK-117 gap-review build sequence itself, which found a recurring
  output_paths-registration gap for cross-linked files and applied the fix
  directly to `notes/task-authoring-guide.md` (logged in
  `shared/improvement-backlog.md` as applied).
- Cross-linked to Self-Repair, Emergence, the improvement backlog, and
  Change Control.
- This completes the full build sequence identified in
  `MAP_System/artifacts/reports/MAP-repo-systems-gap-review.md`: all systems named as
  priority or secondary gaps (Research, Self-Repair, Context,
  Decision/Authority, Human Interface, Risk, Security/Permissions, Change
  Control, Project Bootstrapping, Archive/Retention, Retrospective) are
  now built.

## DEC-026: Make Emergence Capture Mandatory Per-Project, Enforced Through MAP

Status: approved
Owner: command-center (direct operator instruction; built by claude-lab-valo, TASK-126)
Date: 2026-07-03
Applies-To: every project's bootstrap and every task's release; Class: POLICY

The operator identified that the Emergence/Insight (E/I) system was
never used during the entire ProjectUpdater build (TASK-123 through
TASK-125) despite `emergence/README.md` already existing and defining
project-level insight/idea/experiment/synthesis folders, and real
insights surfacing during that build (a Playwright install workaround, a
risk-mitigation idea, a completeness-gap pattern) that went uncaptured
until asked about directly. Operator directive: backfill proper records
for ProjectUpdater now, and make Emergence capture mandatory for every
project going forward, enforced through MAP rather than left as a
documentation-only suggestion.

Effect:

- Backfilled `INS-0011`, `INS-0012`, `INS-0013`, and `IDEA-0015` for
  ProjectUpdater (tagged `Project: ProjectUpdater`), triaged (not left
  `RAW`), and rebuilt the emergence index.
- Created `Projects/ProjectUpdater/{insights,ideas,experiments,synthesis}/`
  retroactively, matching the new bootstrap requirement below.
- `PROJECT_BOOTSTRAPPING_SYSTEM.md` (amended): added a 7th
  pre-first-task requirement ("Emergence capacity") and a new "Ongoing
  Emergence capture" section clarifying this is not a one-time bootstrap
  checkbox like the other six.
- `NEW_PROJECT_WIZARD.md` (amended): added step 7 (create empty Emergence
  folders at bootstrap) and step 9 (consider Emergence capture at every
  task's submission).
- `CHANGE_CONTROL_SYSTEM.md` (amended) and `scripts/release_task.py`
  (amended): `REQUIRED_CHECKS` now includes a literal
  `- [x] Emergence capture considered` line, mechanically blocking
  `release_task.py` from marking any task `RELEASED` without it — same
  enforcement mechanism as the three existing required checklist items.
  A checklist may honestly say "considered, nothing worth capturing";
  the gate blocks only a missing line, not a "no" answer.
- `templates/release-checklist.md` and `tests/test_release_gate.py`
  updated to match; new focused test
  `test_missing_emergence_line_blocks_release` added and passing.
- This decision is itself class POLICY and was approved directly by
  command-center instruction, per `DECISION_AUTHORITY_SYSTEM.md`.

## DEC-027: Research System Stays Specification-Only Until A Real Research Question Exists

Status: approved
Owner: claude-lab-magi (TASK-142, follow-up to TASK-129/130/140/141)
Date: 2026-07-04
Applies-To: Research System use across all projects; Class: SCOPE (core
agent, propose-and-record; not AUTHORITY or POLICY because it does not
change who may decide or a cross-MAP rule, only what is currently in bounds
for Research System use)

TASK-129/130 found the Research System (`RESEARCH_SYSTEM.md`, six templates
in `templates/research/`, `validate_research_artifacts.py`) is fully built
and validator-backed but has zero real Research Brief / Source Map / Claim
Evidence Matrix / Assumption Register / Research Summary artifacts in
`artifacts/research/` beyond the README. ProjectUpdater's bootstrap
explicitly recorded that no external-dependency research brief was needed.
The operator asked directly (TASK-142 broadcast) whether E/I and Research
need improvement and whether all built systems are actually being used.

Answer for Research, recorded as a decision rather than left implicit:

- E/I (Emergence) does not need more building — it is genuinely used and
  mechanically enforced (DEC-026, `release_task.py`'s required
  `Emergence capture considered` line). No action needed there.
- Research is different in kind: it isn't under-enforced, it's
  under-*needed*. Every task so far has had its unknowns resolved by reading
  code, existing docs, or asking the operator directly — none has hit the
  shape Research is for (an external claim, a third-party library choice, a
  contested technical fact) that benefits from a structured brief/source
  map/evidence trail. Building fake research artifacts to make the system
  look used would be the box-ticking-ceremony failure mode DEC-026 already
  named as a risk for Emergence, applied to a different system.

Effect:

- Research System stays exactly as built (validator, templates, README) with
  no forced sample artifact.
- The next task that has a genuine external/contested-fact research need
  must use `templates/research/` for it — this decision does not lower the
  bar, it only declines to invent a need that does not exist yet.
- `artifacts/research/README.md` should link this decision so a future
  reader does not mistake the empty folder for an unbuilt or abandoned
  system.
- Revisit this decision (supersede or amend) the first time a task's
  unresolved-questions or review reveals a real unverified external claim
  that should have gone through a Research Brief but didn't.

## DEC-028: MAP Commits to Software Delivery as its First Standing Proving Workflow

Status: approved
Owner: bigboss (operator), selected 2026-07-15 from gune's working-backwards
brief (`artifacts/planning/working-backwards-proving-workflow-2026-07-15.md`)
Date: 2026-07-15
Applies-To: MAP proving-workflow direction; Class: DIRECTION/SCOPE (operator
authority — this is a project-direction choice, which DECISION_AUTHORITY_SYSTEM
reserves for the operator as decision owner; reversible)

Reason: MAP is architecturally ahead on durability + mechanical gates
(INS-0022) but every recent task (197–204) was internal infrastructure, with no
real deliverable flowing through the gates (INS-0023). Applying Amazon's
working-backwards method, the operator selected **software delivery** as MAP's
first standing proving workflow: MAP designs, implements, reviews, and releases
real software, with every change gated, owned, and reversible. Software was
chosen over the research-brief and Pathwell candidates because it has the most
objective acceptance gates — the strongest fit for MAP's mechanical-gate
differentiator.

- First slice (bounded, reversible): complete **IDEA-0015's deferred import
  half** — a JSON Import button in ProjectUpdater (export shipped in TASK-136;
  import was deferred). This mitigates the registered localStorage data-loss
  risk (`Projects/ProjectUpdater/risks/RISK_REGISTER.md`) with an objective
  acceptance test (export → import round-trip restores state).
- Standing workflow: real software features flow through normal MAP
  intake → claim → implement (Codex-led) → review (Claude/core, cross-review) →
  release-gate. The research-brief candidate remains available as a second track.
- This resolves the open `shared/unresolved-questions.md` item ("first real
  workflow target: writing / software / research / PM?").
- Revisit/amend if the first feature slices show the software cadence is a poor
  fit or the operator redirects to another track.

## DEC-029: Remote OLLAMA_HOST is Permitted Only as Explicit, UI-Visible Configuration

Status: approved
Owner: bigboss (operator), decided 2026-07-23; relayed via claude-lab-bima
(hcom #13380) and recorded by claude-lab-zaro
Date: 2026-07-23
Applies-To: TASK-265 (CommandCenterUI local-model lane); supersedes the open
question TASK-264 left unsettled; Class: POLICY/AUTHORITY (operator authority —
this is a trust-boundary direction, reserved for the operator as decision
owner; reversible)

Operator intent, verbatim: "I will eventually be using a second machine to work
alongside this one."

Decision: a remote `OLLAMA_HOST` is **permitted in principle**, but only
through explicit configuration whose target host is **visible in the Command
Center UI**. Silent inheritance of an ambient `OLLAMA_HOST` environment
variable remains **forbidden**. Loopback-only stays the default and the current
enforced behaviour. This settles policy direction; it does **not** authorise
implementation now.

Reason: the hazard being defended against is not remote access, it is
*invisible* remote access. Prompts carry agent transcripts, task records, and
file contents, so an environment variable that silently redirects them off-box
is the actual exposure. An explicitly configured, UI-visible host does not have
that property — the operator can see where their data is going. TASK-264's
hardening is **not** reverted by this decision; it is the mechanism that keeps
the default safe.

- **Near-term action (the whole of it):** live `server.py` carries three
  hardcoded loopback constants — line 100 `OLLAMA_URL =
  "http://127.0.0.1:11434"`, and lines 424 and 846 `env["OLLAMA_HOST"] =
  "127.0.0.1:11434"`. Route all three through **one configuration point** that
  defaults to loopback and refuses ambient env inheritance. No behaviour change
  today. The point is to make the eventual second-machine change a small,
  reviewable edit rather than an urgent one — every additional hardcode raises
  the odds someone reverts the hardening in a hurry to make remote work.
- **Do NOT implement remote support now.** The operator said "eventually."
- **When remote is eventually enabled it is a trust-boundary crossing.**
  `map_task.py create` exposes `--trust-boundary-crossing`; the eventual task
  must carry that flag and take the security second pass AGENTS.md requires for
  network-facing outputs.
- `server.py` lives in the external CommandCenterUI project, not this repo. Per
  `artifacts/planning/commandcenterui-boundary-decision.md`, work there needs
  explicit operator approval — so the consolidation above is recorded as
  direction, not started here.
- Revisit when the second machine actually arrives, or if the UI cannot in fact
  surface the configured host, which would invalidate the visibility premise
  this decision rests on.

## DEC-030: Live server.py is Authoritative for Features, the Template for Install; Merge Direction is Live to Template

Status: approved
Owner: bigboss (operator), decided 2026-07-23; relayed via claude-lab-bima
(hcom #13380) and recorded by claude-lab-zaro after independent verification
Date: 2026-07-23
Applies-To: TASK-265 (first half — which `server.py` copy is authoritative);
Class: ARCHITECTURE/OWNERSHIP (resolves a source-of-truth ambiguity that was
blocking TASK-265's policy gate; reversible)

Decision: the **live** copy at `~/Projects/CommandCenterUI/app/server.py` is
authoritative for **feature content**. The **in-repo template** at
`MAP_System/templates/install/command-center-ui/app/server.py` is authoritative
for **install content**. Merge direction is **live → template**. The template's
17 template-only lines are the security/visibility hardening and **must survive
any merge**.

Verified directly on 2026-07-23 rather than taken from the relay:

| Copy | Path | Lines | Modified |
|---|---|---|---|
| Live (features) | `~/Projects/CommandCenterUI/app/server.py` | 2396 | — |
| Template (install) | `MAP_System/templates/install/command-center-ui/app/server.py` | 2119 | 2026-07-21 |
| **Stale third copy** | `~/Documents/Projects/MultiAgentProject-main/Source/MAP_System/templates/install/command-center-ui/app/server.py` | 2049 | 2026-07-15 |

- The 17 template-only lines were confirmed by diff and include
  `VISIBLE_OLLAMA_MODELS`, the model-visibility hardening. Losing them in a
  live → template merge would silently revert the protection DEC-029 relies on
  for its "explicit and visible" premise.
- The **third checkout is real and is a trap.** It is a stale *template* copy,
  not a live one, and no task references it. `shared/canonical-repo.md` requires
  reconciling checkout identity before any repo-global operation; anyone doing a
  three-way merge without noticing it would silently regress the file by ~70
  lines to a 2026-07-15 state. It is recorded here so it is discovered by
  reading rather than by breaking something.
- This decision assigns authority only. It does not perform the merge, and no
  `server.py` was edited in recording it — that file lives in the external
  CommandCenterUI project, which per
  `artifacts/planning/commandcenterui-boundary-decision.md` requires explicit
  operator approval to modify.
- Revisit if the live copy is ever regenerated from the template, which would
  invert the merge direction.

## DEC-031: The Advisory Monitor Runs on a Visible Interval, Reports Only on Change, and Stays Proposal-Only

Status: approved
Owner: bigboss (operator) delegated judgment to claude-lab-zaro on 2026-07-23
("i approve of whatever you need to do and using your best judgement");
recorded by claude-lab-zaro
Date: 2026-07-23
Applies-To: TASK-236 acceptance criterion 3 (standing/real-time deployment of
`scripts/advisory_monitor.py`); Class: PROCESS/AUTHORITY (standing-process and
visibility choice; reversible)

TASK-236 built the monitor but deliberately did not deploy it, because making a
read-only observer into a standing process is a visibility and accountability
choice rather than an implementation detail. This settles the three questions
that criterion left open.

**Trigger — a visible interval, not event-triggered.** Reuse the proven
TASK-221 systemd-user pattern at a modest interval. Event-triggering on each
`events.jsonl` append is more responsive and more machinery; the findings this
monitor produces (stranded owners, aging reviews, log health) age in hours or
days, not seconds, so latency is not the binding constraint. Revisit if a
finding class appears where minutes matter.

**Output surface — the Command Center coordination panel, shared with
TASK-227 §1a.** These are the same surface and must not be built twice.

**Owner — the parent lane of the agent whose work a finding concerns**, per
IDEA-0028 if that is promoted; until then, command-center holds the triage
queue. Naming an accountable owner is not optional: a proposal queue nobody
drains is how the 21 stranded tasks accumulated in the first place, and a
detection system without a drainer reproduces the problem with better
documentation.

**Reporting — on change, not every cycle.** The owner-liveness check emits 21
findings on today's board, 11 of them for a single departed agent. A standing
run that republishes an unchanged backlog every interval will be muted within a
week, and a muted monitor is worse than none because it looks like coverage.
Report new findings, resolved findings, and changes in severity; keep the full
standing set queryable on demand.

- **Fixed regardless of any of the above: proposal-only, forever.** The monitor
  observes and suggests. It never claims, edits, approves, promotes, or
  releases. A core agent turns each finding into a fix, an E/I insight, or a
  dismissal. Nothing auto-acts. Any future change to this property is a new
  decision, not an implementation detail.
- **Not yet implemented.** This settles direction; deploying the timer is
  separate work and should carry its own task and review.
- Revisit if the findings queue is routinely ignored (the owner question was
  answered wrongly) or if a latency-sensitive finding class appears (the
  trigger question was answered wrongly).

## DEC-032: Core-Agent Authority to Reconcile the Release-Checklist/Risk-Tier Conflict (F5) and Clear the Resulting Backlog

Status: approved
Owner: bigboss (operator) delegated judgment to lili-replacement-nisa on
2026-07-28 ("i approve what you need to do"), in direct response to being
told TASK-288 and the APPROVED-backlog release both carry a
`REQUIRE_COMMAND_CENTER_DECISION` policy gate (`decision_class=POLICY`);
recorded by lili-replacement-nisa
Date: 2026-07-28
Applies-To: TASK-288 (reconcile `scripts/release_task.py`'s flat
REQUIRED_CHECKS gate with `notes/review-guide.md`'s risk-tiered release
policy and `CHANGE_CONTROL_SYSTEM.md`'s output-path-scoped rule — open
finding F5 in `notes/system-improvement-implementation-plan.md`) and the
consequent release of the 90-task APPROVED backlog (oldest since
2026-07-17) once the reconciled rule is implemented; Class: POLICY/PROCESS
(process-definition change; reversible via a follow-up decision)

This is the `command-center approval` evidence `pre_dispatch_policy.py`
requires before a core agent may claim or execute a POLICY-class task
(`REQUIRE_COMMAND_CENTER_DECISION` / `REQUIRE_SECURITY_STRUCTURAL_APPROVAL`).
It authorizes a core agent to design and implement the actual reconciled
rule (this record intentionally does not pre-decide the rule's content —
that is TASK-288's acceptance criteria to satisfy and a reviewer's to
verify) and, once TASK-288 lands, to release the existing APPROVED backlog
under that rule without a separate per-task approval round, provided each
released task is genuinely covered by the low-risk/non-canonical-path
exemption the reconciled rule defines. A task the implementing agent judges
high/medium risk under the new rule still needs its own standalone release
checklist — this decision authorizes process execution, not a blanket
release of everything currently APPROVED regardless of content.

- Not yet implemented. TASK-288 is the implementation; this record only
  clears the authority gate blocking it.
- Revisit if the reconciled rule turns out to require operator input on a
  specific judgment call (e.g., where the risk-tier line actually falls),
  rather than being mechanically derivable from the two existing documents.

## DEC-033: CommandCenterUI Local-Model Allowlist Stays a Single Named Model

Status: approved
Owner: bigboss (operator), decided 2026-07-28 directly in conversation with
task288-review-valo; recorded by task288-review-valo
Date: 2026-07-28
Applies-To: TASK-265 (CommandCenterUI live/template merge); confirms and
reaffirms DEC-029 and DEC-030 (both 2026-07-23, restated by the operator
today in materially identical terms) and closes the follow-up the
2026-07-21 untracked-edit audit
(`artifacts/audits/task254-untracked-edit-2026-07-21.md`) flagged to
@bigboss/@niko and left unresolved; Class: POLICY/AUTHORITY (operator
authority — trust-boundary direction on what local-model surface is
exposed; reversible)

Context: while preparing TASK-265's live/template merge, found that the
live `server.py`'s `local_agent_defs()` currently has **no allowlist gate**
at all — `VISIBLE_OLLAMA_MODELS` (template-only, one entry: `qwen3.5:4b`)
was dropped by the untracked 2026-07-21 edit and, unlike the loopback/
`SUMMARY_MODEL` hardening, was never restored by TASK-264 (TASK-264's own
description names only three items to restore; this allowlist gate is not
one of them). Right now, live exposes and makes launchable *every*
Ollama model actually installed on the machine (11 present via `ollama
list` as of 2026-07-28, including `deepseek-r1:8b`, `qwen3.5:9b`,
`qwen2.5-coder:7b`, and an embedding-only model, `nomic-embed-text`, that
is not suited for agent launching at all) — not just a reviewed, named
set. The live copy's `OLLAMA_MODEL_USES` dict (5 entries) is a plausible-
looking but non-gating description table only; three of its five named
models (`llama3.2:3b`, `qwen2.5-coder:3b`, `gemma3:4b`) are not even
currently installed, so it does not reflect real deliberate curation
either.

Decision: the local-model allowlist reverts to the original, narrower
scope — **`qwen3.5:4b` only** stays launchable through the Command Center
UI. `OLLAMA_MODEL_USES`'s broader 5-model list is not adopted as the new
allowlist. Any future expansion is a new, explicit operator decision,
not a default inherited from whichever copy last edited the file.

Reason: same hazard shape as DEC-029 — the risk is not that local models
exist, it is that a broader launchable surface accumulates by silent
inheritance rather than deliberate review. An allowlist that grows because
one edit happened to add entries is the model-exposure equivalent of the
ambient-`OLLAMA_HOST` problem DEC-029 already rejected for the network
case.

- **Execution is not authorized here.** Like DEC-029/030, this record
  settles policy only. `app/server.py` lives outside this repo
  (`~/Projects/CommandCenterUI`) and per
  `artifacts/planning/commandcenterui-boundary-decision.md` needs its own
  task with the external path as a named output before any agent edits it.
  TASK-265 is that task; its output_paths currently name only the in-repo
  template copy and will need the live path added before the live file
  itself can be corrected to restore the allowlist gate.
- **Helper-execution boundary hit while preparing this**:
  `task288-review-valo` (a helper) attempted to claim TASK-265 with the
  operator's general go-ahead already in hand, and was rejected by
  `pre_dispatch_policy.py` (`REJECT_HELPER_BROAD_ARCHITECTURE`) — a
  structural role boundary, not a missing-approval gate, and not waivable
  by operator permission given informally in chat. TASK-265 needs a core
  agent (e.g. `lili-replacement-nisa`).
- The 2026-07-21 audit's merge recipe
  (`artifacts/audits/task254-untracked-edit-2026-07-21.md`, "Repair (Part
  2)" section) already lists exactly what to keep from live (terminal-
  prompt feature, chat intent validation) versus what to restore
  (`OLLAMA_URL`/`SUMMARY_MODEL` hardcoding, the loopback pin, and the
  `VISIBLE_OLLAMA_MODELS` allowlist gate) — TASK-265 should follow that
  recipe rather than re-deriving it, with this decision settling the one
  question that recipe left open (which model(s) populate the allowlist).
- Revisit if the operator later wants to name additional approved models —
  that is a small, explicit follow-on decision, not a reason to reopen this
  one.

## DEC-034: CommandCenterUI Terminal-Message/Timestamp/Composer-Intent Frontend Feature Is Authorized as Shipped Behavior

Status: approved
Owner: bigboss (operator), decided 2026-07-28 directly in conversation when
asked to choose between authorizing the feature, reverting it, or
re-investigating its provenance; recorded by claude-lab-lili
Date: 2026-07-28
Applies-To: TASK-292 (authorize the untracked 2026-07-21 frontend feature)
and TASK-254 (CommandCenterUI serial-batch reconciliation), whose criterion
4 this decision supplies the missing authority for; closes the frontend half
of the 2026-07-21 untracked-edit audit
(`artifacts/audits/task254-untracked-edit-2026-07-21.md`), whose backend
half was already closed by DEC-029/DEC-030/DEC-033; Class: POLICY/AUTHORITY
(operator product authority over shipped UI behavior; reversible by a
follow-up decision plus a revert task)

Context: on 2026-07-21 the live CommandCenterUI `chat.html`/`chat.css`/
`chat.js` gained a terminal chat-message merge, message timestamps, and
composer intent handling through an edit with **no owning task**. An audit
investigated and could not attribute the cause. `audit-untracked-bozo`
then folded that feature into the template to restore live/template parity
as part of TASK-254's repair. Reviewer `codex-lab-lilo` rejected TASK-254
for blessing unauthorized behavior inside an administrative task, and
reviewer `mapfinish-kino` rejected the follow-up attempt because a prose
addendum reinterpreted TASK-254's acceptance criterion 4 ("no CommandCenterUI
source or behavior is changed by the administrative repair") rather than
amending it — while the audit itself records the fold as TASK-254's *own*
repair action, making that criterion factually false as written.

Decision: the feature is **authorized as intentional shipped behavior**.
Live/template byte parity holds, the backend half is settled, all 12 focused
`test_command_center_*` assertions pass, `node --check` passes both copies,
and no security finding attaches to the frontend change. The feature stays.

Reason: the feature has been live and working for a week, is covered by
focused tests, and carries no security exposure — unlike the *backend* half
of the same untracked edit, which did carry real exposure (a dropped
allowlist gate) and was therefore narrowed rather than accepted (DEC-033).
The two halves of one untracked edit legitimately get different answers
because their risk differs, not because the provenance differs.

- **Provenance remains unattributed and that is accepted as a known gap**,
  not resolved. This decision authorizes the *behavior*; it does not claim
  anyone established who wrote it. Re-investigation was explicitly
  considered and declined by the operator because the prior audit already
  attempted attribution and closed unattributed.
- This decision does **not** retroactively make TASK-254's criterion 4 true.
  Criterion 4 must still be formally amended through the task lifecycle
  citing this record as its authority, per `mapfinish-kino`'s required
  action (a) — reinterpreting the unchanged text in a side document was
  already rejected twice and remains rejected.
- Revisit if the feature later proves to conflict with a deliberate UI
  direction; reversal is a follow-up decision plus a revert task, not a
  silent edit.

## DEC-035: Spawned Claude Agents Default to Sonnet With Auto Permission Mode, Superseding TASK-194's Haiku Default

Status: approved
Owner: bigboss (operator), directed 2026-07-28 in conversation: "every new
agent is supposed to be opened in sonnet with auto mode on, so they can just
work, with haiku being used specific tasks. since I dont want to have to sit
here and approve things by hand"; recorded by claude-lab-lili
Date: 2026-07-28
Applies-To: supersedes the Haiku-default helper tier documented by TASK-194
(RELEASED, `notes/helper-agent-guide.md`) and the matching line in
`MAP_System/AGENTS.md` Elastic Helper Agents; Class: POLICY (resource and
operator-attention policy; reversible by a follow-up decision plus one
`hcom config` call)

Decision: `hcom config claude_args` is set to
`--model sonnet --permission-mode auto`, persisted in
`~/.hcom/config.toml` under `[launch.claude] args`, so every spawned Claude
agent starts on Sonnet in auto permission mode. Haiku remains available and
is still the right choice for narrowly-scoped, low-friction work, but it is
now an explicit per-spawn override (`--model haiku`) rather than the default.

Reason: the Haiku default was chosen as a resource-management measure, and
that tradeoff was real. What it cost in practice was operator attention:
every spawned agent blocked on manual permission prompts, and those prompts
fell to the operator. The operator's instruction is explicit that this is the
cost they are unwilling to keep paying. Sonnet plus auto mode removes the
prompt-babysitting without removing the ability to choose Haiku deliberately.

- **Root cause of the original friction was a missing flag, not the model
  tier.** `--permission-mode auto` had never actually been passed at spawn
  time, so *every* agent — Sonnet included — defaulted to manual approval.
  An earlier working note had concluded "Haiku sessions cannot be set to auto
  mode"; that conclusion is not supported by anything in `claude --help`, and
  was most likely drawn from the missing flag rather than a real model-tier
  restriction. Watch whether Haiku spawns still block under
  `--permission-mode auto`; if they do, the restriction is genuine and this
  note should be corrected again.
- **This decision creates a documentation debt that must be paid.** TASK-194
  is RELEASED and its guidance now describes behavior the system no longer
  has. Found by `mapfinish2-zemi` while release-verifying TASK-194 on
  2026-07-28, which is exactly the kind of doc-vs-reality drift MAP's
  completion condition forbids. `notes/helper-agent-guide.md` and the
  `AGENTS.md` Elastic Helper Agents paragraph both need updating to cite this
  record; that is tracked as a follow-up task, not silently left.
- The escalation-request process TASK-194 defined (write a scope/justification
  note, have a different core agent choose the tier) is **not** repealed. It
  still governs going *above* the default to Opus. Only the default itself
  moved.
- Auto mode is not blanket approval: the classifier still blocks unmediated
  mutations of canonical state, as it did to a raw-SQL `max_attempts` update
  on 2026-07-28 (REPAIR-0012), which is what prompted building the sanctioned
  verb in TASK-293 instead.

## DEC-036: Claude Takes Over MAP Recovery Coordination While Codex Is Unavailable

Status: approved
Owner: bigboss (operator), directed 2026-07-30 in conversation: "Codex is out
of use, so I need you to take over as orchestrator"; recorded by
claude-lab-mimi
Date: 2026-07-30
Applies-To: the "recovery coordinator" role held by codex-lab-risa under the
approved `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_KICKOFF.md`
plan (Section 11); Class: OPERATIONAL (provider-availability response,
reversible when Codex returns and the operator re-designates)

Decision: claude-lab-mimi is the operator-designated MAP recovery
coordinator/orchestrator effective 2026-07-30 while Codex is unavailable, per
the eligible-peer-core-agent designation rule in `MAP_System/AGENTS.md`'s
Canonical Authority Hierarchy (Codex and Claude are both eligible; provider
identity does not self-confer the role, only an explicit operator
designation does). New coordination decisions route through mimi, not
codex-lab-risa, until further notice.

At handoff: TASK-310 (WS-1 authority freshness, owner codex-lab-risa) had an
expired SQLite lease (`04:08:11` vs actual time `04:21:41`). TASK-313 (WS-1
path-ownership prerequisite, owner codex-lab-vumo) was still heartbeating
minutes earlier and is paused clean on its own initiative, awaiting a
separate operator APPROVE/HOLD on its "A1" disposition — not part of this
handoff. TASK-311 (owner rotation-replacement-kite-veni, a Claude identity)
was independently blocked ~3 hours before this decision and is unrelated to
the Codex outage.

- **The outage was not verified uniform across every codex-lab identity at
  the moment of the operator's statement.** codex-lab-vumo's last heartbeat
  (04:17 UTC) was 4 minutes before the operator's instruction reached mimi.
  Treat "Codex is out of use" as "stop routing new coordination/
  implementation work to codex-lab-*", not as license to assume every
  codex-owned task is already abandoned — check lease/heartbeat freshness
  per task before reclaiming.
- Reclaiming any codex-owned SQLite lease must go through sanctioned
  `map-authority` verbs on Smalls/RUKI; Biggie's local `MAP_System/db/claims`
  module refuses direct writes (`RemoteAuthorityRequired`), which is working
  as designed, not a bug to route around.

## DEC-037: Librarian Owns Standing Plan/Goal-Alignment Auditing

Status: approved
Owner: bigboss (operator), directed 2026-07-30 in conversation: "so lets
review where we are, and where the goals are so we dont get off track again
(something the librarian should be doing)"; recorded by claude-lab-mimi
Date: 2026-07-30
Applies-To: the librarian helper role (`helper-librarian-*` identities) for
the duration of the MAP recovery effort (`MAP_System_Recovery_2026-07-29/`)
and beyond; Class: OPERATIONAL (a standing responsibility, not a one-off
audit; reversible by a follow-up decision)

Decision: the librarian owns ongoing, independent auditing of live MAP state
against `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_KICKOFF.md`
— its stated purpose (Section 1), its Change Freeze (Section 8), and its
sequence (Section 10) — and reports drift to the recovery coordinator and
the operator. This explicitly includes checking the coordinator's own work,
not just other agents' — the point is an independent check, not a rubber
stamp of whoever is currently driving.

First pass requested same-day from `helper-librarian-tara`, covering: (1)
live task state vs. the Section 10 sequence position; (2) every substantive
change since kickoff-plan approval checked against the Section 8 Change
Freeze, including the coordinator's own actions; (3) a recommendation for
how this recurs (cadence/trigger) so it does not depend on someone
remembering to ask each time.

- **Why this is needed now specifically, not just in general.** The
  recovery's own diagnosis (kickoff plan Section 4) is that MAP had already
  drifted once into building/monitoring/repairing itself instead of proving
  itself on external product delivery. A recovery effort correcting that
  drift is not automatically immune to repeating it — reusing this
  session's own established discipline (independently re-verify rather than
  trust a report, per `INS-0058`) against the recovery's own trajectory, not
  only against individual task submissions.
- This does not make the librarian a decision authority — per
  `MAP_System/AGENTS.md`'s Canonical Authority Hierarchy, helpers "gain no
  task, review, release, routing, policy, or operator authority." It reports
  drift; the operator and coordinator decide what to do about it.

## DEC-038: Disposition Of DEC-037's First Audit Findings — Sequence Breach Stands As A Recorded Deviation, TASK-298/305 Freeze Held Going Forward

Status: approved
Owner: bigboss (operator, "do what you think is best" on the two open
questions, 2026-07-30) and claude-lab-mimi (made the calls under that
authorization)
Date: 2026-07-30
Applies-To: `MAP_RECOVERY_KICKOFF.md`'s WS-1→WS-2→WS-3 gate order and Section
8 Change Freeze, as cross-checked by `helper-librarian-tara`'s first DEC-037
audit (`MAP_System_Recovery_2026-07-29/00_control/reviews/plan-alignment-audit-2026-07-30.md`);
Class: OPERATIONAL (governs how existing state is treated, not new policy)

Decision:

1. **TASK-311 (WS-2) stays `APPROVED`; not reverted.** The audit correctly
   found it ran ahead of Sequence Amendment 1's own approved revised
   ordering (which put WS-2 after TASK-310 receives independent review, not
   parallel to it) — the coordinator's question to the operator authorizing
   it was framed around the raw SQLite dependency, not Amendment 1's fuller
   sequence, which is on the coordinator, not a misunderstanding by the
   operator. The underlying collision-resolution work itself was correct,
   independently re-verified twice (once by the reviewer, once by this
   audit), and reverting it would destroy real, correctly-executed value
   without fixing anything — the actual defect is sequencing discipline
   going forward, not this specific approval. Recorded as a deviation, per
   the audit's own recommendation to "not erase history."
2. **Going forward, the gate is restored, not waived.** No further WS-3/
   WS-4+ work proceeds past what's already claimed until TASK-310 (WS-1) is
   submitted and independently reviewed by an agent outside the
   claude-lab-mimi/rotation-replacement-mimi-koda lineage.
3. **TASK-298 and TASK-305 stay `APPROVED`; also not reverted** — same
   reasoning: the review work was sound (independently re-verified, not
   trusted from either submission), only the *timing* of the lifecycle
   advance is in question. **Their downstream actions are held**: no
   TASK-298 backup removal or further deployment, no further TASK-305-linked
   release-guidance/backlog ceremony, until WS-1 through WS-3 stabilization
   actually completes. This is the freeze exception the audit asked for,
   made explicit rather than left ambiguous.
4. TASK-295's use of the `retire` verb during WS-2 is affirmed as within the
   audit's own "defensible bounded exception" reading — active
   output-collision repair is an explicit Section 8 allowed exception. No
   further lifecycle-verb expansion is authorized by this decision.

- **Why not just revert TASK-311/298/305 to be safe.** Reverting correctly-
  reviewed, independently-verified work to "undo" a sequencing mistake would
  itself violate the freeze's own spirit (destructive backlog churn) for no
  real safety gain — nothing about the collision resolution or the two
  approvals was substantively wrong, only their timing relative to the plan.
  The freeze exists to prevent MAP from building/monitoring/repairing itself
  instead of shipping; unwinding real completed verification work to satisfy
  a sequencing technicality would be exactly that pattern in a different
  costume.
- See also DEC-039 (coordinator role separation), the direct structural fix
  for how this drift happened in the first place.

## DEC-039: Coordinator Role Is Split Out From Task Ownership And Review

Status: approved
Owner: bigboss (operator), directed 2026-07-30 in conversation: "I agree on
the you doing too many things at once. Lets take a snapshot, and then you
will set up another agent to be the new coordinator whose job is just that
... it should coordinate, not run tasks"; recorded by claude-lab-mimi
Date: 2026-07-30
Applies-To: the "MAP recovery coordinator" role established by DEC-036;
supersedes DEC-036's designation of `claude-lab-mimi` as coordinator; Class:
OPERATIONAL (direct structural response to DEC-037's first audit finding of
role concentration; reversible by a follow-up decision)

Decision: `map-coordinator-hobo` is the MAP recovery coordinator effective
2026-07-30, with a scope narrower than DEC-036's original designation by
design — coordination only (routing, task assignment, DEC-037 audit
response, blocker triage). It does not claim, own, or implement tasks, and
its own work is therefore not self-reviewed by construction. `claude-lab-mimi`
steps back from coordination entirely and continues only as TASK-310's
task-owner until that task is submitted and independently reviewed by
someone outside the mimi/`rotation-replacement-mimi-koda` lineage — mimi
does not resume routing, assigning, or auditing after this handoff.

Handoff mechanism: a fresh `STATE_SNAPSHOT` was prepared and hash-verified
(`MAP_System/handoffs/STATE_SNAPSHOT-claude-lab-mimi-20260730T214444Z.yaml`,
`sha256:5a377a...9f69`) before spawning the successor, matching this
session's DEC-036 precedent (operator statement + durable decision record +
hcom broadcast) rather than the technical `context_rotation.py` ack/finalize
pipeline, which remains structurally blocked on the undeployed TASK-307/308
gateway patch (unrelated to and unblocked by this decision).

- **Why split coordinator from owner/reviewer at all, rather than just
  reminding mimi to be careful.** DEC-037's first audit (mandated
  specifically to check the coordinator's own work, not exempt it) found
  concrete drift traceable to role concentration: an expired TASK-310 lease
  that went unnoticed because coordination attention was split across too
  many things at once, a stale TASK-309 ownership record documented in
  DEC-036 but never actually fixed, and a sequence-breach authorization
  where the coordinator's own question to the operator was incompletely
  framed. None of these were reviewer failures on any single task — they
  were coordination-attention failures. Splitting the role removes the
  structural cause rather than asking the same identity to simply try
  harder at all of it simultaneously.
- The new coordinator's job description ("coordinate, not run tasks") is the
  operator's own phrasing, kept verbatim as the scope boundary. If a future
  coordinator identity finds itself wanting to also own or implement a task,
  that is the signal to route it to someone else, not to expand its own
  scope back to where DEC-037 found the problem.

## DEC-040: TASK-306 Split (Operator-Authorized) And TASK-309 Coordinator-Epic Ownership Clarified

Status: approved
Owner: bigboss (operator), directed 2026-07-30 in conversation with
map-coordinator-hobo, deciding between options it presented after relaying
helper-librarian-tara's DEC-037-audit findings on both questions
Date: 2026-07-30
Applies-To: TASK-306 (cross-PC Command Center alignment) and TASK-309
(recovery coordination epic); Class: SCOPE/OPERATIONAL (task-lifecycle
disposition plus a coordinator-role interpretation)

Decision:

1. **TASK-306 split.** Per helper-librarian-tara's audit recommendation:
   retire TASK-306 preserving evidence (owner claude-lab-nene, twice
   CHANGES_REQUESTED, not currently live); create one minimal
   local/template-only WS-1 Command Center consumer task with no remote
   write, to unblock TASK-310's fourth Required Consumer; defer the
   broader Smalls cross-PC deployment/parity work to a separate WS-6 task,
   created when that workstream begins, gated by its own operator/security/
   rollback approval. Full TASK-306 execution as originally scoped is not
   authorized now; it stays frozen absent a future explicit operator
   exception.
2. **TASK-309 ownership clarified.** map-coordinator-hobo owning/claiming
   TASK-309 (the coordination-tracking epic itself, role: coordinator) does
   not violate DEC-039's "does not claim, own, or implement tasks"
   boundary. That boundary targets substantive delivery/review tasks (the
   role-concentration failure DEC-037's audit found); the coordinator's own
   tracking epic -- explicitly named as the coordinator's first action in
   the DEC-039 handoff snapshot -- is coordination bookkeeping, not
   delivery work, and creates no self-review conflict. Recorded here so
   future audits read this consistently rather than re-raising it as fresh
   drift each time.

- **Why split rather than force a full TASK-306 rescope now.** TASK-306
  already hit CHANGES_REQUESTED twice for narrowing its own recorded
  acceptance criteria informally. Informally waiving the Command Center
  consumer to unblock TASK-310 would repeat that exact mistake against a
  second task. A formal split -- not an informal narrowing, a real
  re-scope into two tasks with distinct risk profiles -- lets the low-risk
  local half proceed under the existing WS-1 gate while the genuinely
  frozen half (destructive, trust-boundary-crossing Smalls deployment)
  stays parked with WS-6, where Section 10's sequence already puts it.
- **Why TASK-309 is a bookkeeping exception, not scope creep.** DEC-039's
  own rationale names the specific failure it fixes: an expired TASK-310
  lease that went unnoticed, a stale TASK-309 ownership record, and role
  concentration across coordinator/owner/reviewer on delivery tasks.
  TASK-309 has no deliverable beyond `00_control/phase2-status.md` and no
  review step of its own that a self-claim could corrupt -- it is the
  coordination role's own accounting artifact. Tara's flag was the correct
  challenge to raise regardless (per DEC-037, the coordinator's own actions
  get checked, not assumed clean); this decision is the operator's answer
  to that challenge, not the coordinator asserting it unilaterally.

## DEC-041: Operator Approval To Edit Live CommandCenterUI For TASK-314's Freshness Display

Status: approved
Owner: bigboss (operator), directed 2026-07-30 in conversation with
map-coordinator-hobo
Date: 2026-07-30
Applies-To: TASK-314 (WS-1 Command Center authority-freshness display); the
external-edit approval checklist in
`MAP_System/artifacts/planning/commandcenterui-boundary-decision.md`, and
DEC-030's live-to-template merge direction; Class: SCOPE (named exception to
the CommandCenterUI boundary default, per that doc's own Option B path)

Decision: mimi is authorized to extend TASK-314 to also edit the live
CommandCenterUI application, satisfying the boundary doc's "Required Approval
Before External Edits" checklist:

- **External path named:** `/home/mellow/Projects/CommandCenterUI` (Biggie
  local; not Smalls, not cross-host -- distinct from TASK-306's frozen
  cross-PC deployment scope).
- **Output paths (exact files):**
  `/home/mellow/Projects/CommandCenterUI/app/server.py`,
  `/home/mellow/Projects/CommandCenterUI/src/orchestrator.html`,
  `/home/mellow/Projects/CommandCenterUI/src/orchestrator.css`,
  `/home/mellow/Projects/CommandCenterUI/src/orchestrator.js`, plus
  regenerating `MAP_System/templates/install/command-center-ui/version.json`'s
  checksum manifest so template and live match again per DEC-030.
- **Outside normal writable scope:** yes, per the boundary doc; recorded here
  as the explicit exception, not an implicit target.
- **Validation/restart plan:** back up the live files before editing; after
  editing, restart the live Command Center server process and run a smoke
  check confirming the existing UI still loads and the new freshness badge
  renders; then re-run `test_command_center_deployment_parity.py` to confirm
  template/live parity is restored.
- **Read-only vs write-capable:** this is read-only UI integration (a GET
  endpoint calling `map-authority status`, no MAP state mutation) -- not the
  write-capable approve/reject/replay control surface the boundary doc's
  Option C gates separately. That remains out of scope.

- **Why this doesn't reopen the TASK-306 freeze question.** TASK-306 was
  frozen because its Smalls half was destructive, cross-host, and
  trust-boundary-crossing. This is a local Biggie-only edit to a
  currently-running service, gated by a *different*, narrower boundary
  (`commandcenterui-boundary-decision.md`) that exists specifically to make
  external-CCUI edits deliberate rather than implicit -- and that gate is
  satisfied here by explicit named operator approval, per its own terms.
- **Why not leave it template-only.** DEC-030 already establishes live as
  authoritative for features with merge direction live-to-template; shipping
  a feature template-first inverts that and leaves the operator's actual
  running UI without the display TASK-314 exists to add, while also failing
  the existing deployment-parity test. Syncing live resolves both.

## DEC-042: Program Coordinator Designated For The MAP Bedrock Program (D0)

Status: approved
Owner: bigboss (operator), directed 2026-08-10 in conversation, choosing
"Me (claude-lab-sumi), this session" when asked to designate a Program
Coordinator for the MAP Bedrock run; recorded by claude-lab-sumi
Date: 2026-08-10
Applies-To: the "Program coordinator" role required by
`map-2-research-adoption-implementation-program-2026-08-09.md` §2 and
D0 ("The operator must explicitly designate the program coordinator
before Phase 1", line 175) for the MAP Bedrock program specifically.
Distinct from DEC-039's "MAP recovery coordinator" role, which was
scoped to the earlier MAP-BOOTSTRAP-20260617 recovery epic (TASK-309,
RELEASED 2026-08-10) — a different, now-closed effort. DEC-039 is not
reused or extended by this decision.
Class: OPERATIONAL (reversible by a follow-up decision; at most one
program coordinator per run, per the plan's own rule)

Decision: `claude-lab-sumi` is the MAP Bedrock program coordinator
effective 2026-08-10: maintains the dependency ledger and phase
checklist, routes tasks/reviews to helper agents, surfaces gates,
prevents collisions. Per the plan's own coordinator-scope rule, does
not own every implementation or approve its own deliverables — delivery
and review work continues to route to helper agents and independent
reviewers, as has been the pattern this session (e.g. TASK-323's
independent review by `helper-review-task323-fenn`, not self-approved).

## Notes

- **Why this needed a fresh decision rather than citing DEC-039.** DEC-039
  designated a coordinator for a different, narrower-scoped role (the
  original MAP recovery epic) that had already informally drifted through
  several undocumented handoffs (hobo -> an untracked handoff to
  claude-lab-luzo -> coordinator-replacement-rose, last active
  2026-08-03) with no DEC record for each step, and whose own tracking
  task (TASK-309) was released the same day as this decision. Citing it
  for the Bedrock program's D0 would have been exactly the "exception
  recorded only in prose" the Phase 0 combined-exit-gate language warns
  against applying loosely — the plan requires an explicit, current
  designation for this run.
