# TASK-258 Combined Holdout Packets

Audit copy only. Evaluator receives one packet at a time.

# TASK-258 Holdout Packet — S1

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: A completed research packet still contains template placeholders or is missing a mandatory section. What mechanism should catch it, and which failure cases prove that behavior? | A completed research packet still contains template placeholders | is missing a mandatory section. What mechanism should catch it, and which failure cases prove that behavior | A completed research packet still contains template placeholders or is missing a mandatory section
- algorithm signal: candidate_set (score 238, coverage 31%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

A completed research packet still contains template placeholders or is missing a mandatory section. What mechanism should catch it, and which failure cases prove that behavior?

## Candidates

### 1. TASK-104 — Add Research System validation tooling
- MAP / map-runtime / RELEASED; score 238
- scope: Follow-on to TASK-103 from Guidelines/MAP_repo_systems_gap_review.md: once the Research System docs/templates exist, add a focused validator and tests that check required research templates/metadata enough to…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_research_artifacts.py` [implementation] — Validate MAP Research System templates and completed research artifacts. symbols Issue; read text; check required fragments; check templates…
  - `MAP_System/tests/test_validate_research_artifacts.py` [test] — Focused tests for validate_research_artifacts.py. symbols copy templates; run validator; test research validator accepts templates and no artifacts; test…

### 2. TASK-103 — Build MAP Research System (docs, templates, folder scaffold)
- MAP / emergence-and-learning / RELEASED; score 205
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #1: MAP has no formal Research System. Build MAP_System/RESEARCH_SYSTEM.md defining the research flow (Research Question -> Research Brief -> Source Map…
- path warning: none
- diverse evidence:
  - `MAP_System/templates/research` [research] — bundle research ASSUMPTION REGISTER TEMPLATE md; CLAIM EVIDENCE MATRIX TEMPLATE md; RESEARCH BRIEF TEMPLATE md; RESEARCH SUMMARY TEMPLATE…
  - `MAP_System/tasks/TASK-103.json` [task_scope] — Build MAP Research System (docs, templates, folder scaffold) Per Guidelines/MAP_repo_systems_gap_review.md priority #1: MAP has no formal Research System…

### 3. TASK-145 — Research: LangGraph current external practice vs MAP's graph/runner.py and agent_loop.py usage
- MAP / map-runtime / RELEASED; score 181
- scope: Operator asked (hcom broadcast, TASK-144 sibling) to research whether MAP's LangGraph orchestration is aligned with current external practice, since agent training knowledge can be…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/research` [research] — bundle research ASSUMPTIONS 0001 langgraph current practice md; BRIEF 0001 langgraph current practice md; BRIEF 0002 map library…
  - `MAP_System/tasks/TASK-145.json` [task_scope] — Research: LangGraph current external practice vs MAP's graph/runner.py and agent_loop.py usage Operator asked (hcom broadcast, TASK-144 sibling) to…

### 4. TASK-142 — Broadcast-coordinator convention + Research System decision + event-warning baseline cleanup
- MAP / map-runtime / RELEASED; score 176
- scope: Follow-up to TASK-140/141: (1) add a durable broadcast-coordinator convention to AGENTS.md/helper-agent-guide so multi-agent hcom broadcasts declare owner/scope instead of relying on ad-hoc good behavior…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_events.py` [implementation] — Validate and summarize MAP JSONL event logs. symbols summary object; outcome payload; validate choice; validate outcome event; load…
  - `MAP_System/RESEARCH_SYSTEM.md` [research] — MAP Research System; What this is; Core principle; Why this exists The Research System is the knowledge-acquisition layer…

### 5. TASK-109 — Add Context System validation tooling
- MAP / map-runtime / RELEASED; score 175
- scope: Follow-on to TASK-107 from Guidelines/MAP_repo_systems_gap_review.md: after the Context System docs/template exist and current validator run_tests changes are approved, add focused validation tooling and tests…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_context_packets.py` [implementation] — Validate MAP Context Packet template and packet artifacts. symbols Issue; read text; check required fragments; check template; is…
  - `MAP_System/tests/test_validate_context_packets.py` [test] — Focused tests for validate_context_packets.py. symbols copy template; run validator; test context validator accepts template and no packets; test…

### 6. TASK-154 — MAP 6.13: Design outcome feedback and Library-layer research path
- MAP / map-runtime / APPROVED; score 170
- scope: Wave 6 from MAP 6.13 plan. Define outcome events, validator blind-spot metrics, Library layer viability measurement, and Research System pass over external repo candidates…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/research/BRIEF-0002-map-library-tool-candidates.md` [research] — Research Brief; Research question; Why this matters; What would count as an answer Which external Library/memory/collaboration/tooling candidates are…
  - `MAP_System/tasks/TASK-154.json` [task_scope] — MAP 6.13: Design outcome feedback and Library-layer research path Wave 6 from MAP 6.13 plan. Outcome feedback spec…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1466

---

# TASK-258 Holdout Packet — S2

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: Why does a ready follow-up become dispatchable after its prerequisite reaches RELEASED, and where is that rule protected against regression?
- algorithm signal: candidate_set (score 128, coverage 36%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

Why does a ready follow-up become dispatchable after its prerequisite reaches RELEASED, and where is that rule protected against regression?

## Candidates

### 1. TASK-116 — Fix runner dependency satisfaction for RELEASED tasks
- MAP / map-runtime / RELEASED; score 128
- scope: Self-Repair follow-up for REPAIR-0001: graph/runner.py treats DONE/APPROVED as dependency-satisfying but omits RELEASED, while validate_task_graph.py treats RELEASED as terminal. Align runner classification with validator terminal…
- path warning: none
- diverse evidence:
  - `MAP_System/graph/runner.py` [implementation] — Executable LangGraph runner for the file-backed MAP workflow. symbols Map State; project relative; load task graph; load tasks…
  - `MAP_System/tests/test_runner_task_classification.py` [test] — Regression tests for MAP runner task classification. symbols test paid halt suppresses paid ready task but keeps review…

### 2. TASK-125 — Add ProjectUpdater app regression validation tooling
- ProjectUpdater / map-runtime / RELEASED; score 103
- scope: Follow-up validator/tooling slice delegated by claude-lab-valo after TASK-123 and TASK-124 release. Add reusable regression checks for the standalone ProjectUpdater app so future edits can…
- path warning: none
- diverse evidence:
  - `Projects/ProjectUpdater/scripts/validate_project_updater.py` [implementation] — Browser regression checks for the standalone ProjectUpdater app. symbols iso days ago; date days from now; seed data…
  - `Projects/ProjectUpdater/artifacts/tests/task-125-project-updater-validator.md` [test] — TASK-125 ProjectUpdater Validator Evidence; Scope; Checks Covered; Verification Added a reusable browser regression validator for the standalone ProjectUpdater

### 3. TASK-121 — Clean up and optimize MAP_System folder structure after gap-review build
- MAP / map-runtime / RELEASED; score 95
- scope: Operator requested continuation after gap fill: take a fresh MAP_System backup, then clean up/optimize the MAP_System folder structure. Apply safe non-destructive cleanup directly; route…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/tests/README.md` [test] — Test Artifacts Use this folder for focused validation notes, test evidence, and command-output
  - `MAP_System/tasks/TASK-121.json` [task_scope] — Clean up and optimize MAP_System folder structure after gap-review build Operator requested continuation after gap fill: take a…

### 4. TASK-146 — E/I backlog triage: promote/park CANDIDATE ideas 0009-0014, add operator-friction closeout habit (IDEA-0010)
- MAP / command-center-ui / RELEASED; score 95
- scope: Operator asked to keep an eye on E/I as part of the full MAP renewal cycle (hcom #25059). 5 CANDIDATE ideas (IDEA-0009, 0010, 0011…
- path warning: none
- diverse evidence:
  - `MAP_System/notes/task-authoring-guide.md` [guide] — Task Authoring Guide; Required Fields; Acceptance Criteria; Output Paths Every task should be useful to a future agent…
  - `MAP_System/emergence/ideas/IDEA-0014-after-gap-review-implementation-run-a-backed-up-full-folder-file.md` [review] — Idea Card; Idea; Problem or opportunity; Why now After gap-review implementation, run a backed-up full folder/file-structure audit using…

### 5. TASK-119 — Harden RnS stale-claim owner nudges
- MAP / agent-liveness-and-helpers / RELEASED; score 89
- scope: Operator-requested follow-up after TASK-117 stalled: RnS recovered agents but did not get work moving because a stale IN_PROGRESS claim made the runner show no…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/limit_watcher.py` [implementation] — Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits. symbols parse resume after; decide nudges; clear…
  - `MAP_System/tests/test_limit_watcher.py` [test] — Tests for limit_watcher decision logic (TASK-080). symbols status; entry; test parse resume after; test fresh live transcript limit…

### 6. TASK-126 — Backfill ProjectUpdater E/I records and make Emergence capture mandatory per-project
- ProjectUpdater / emergence-and-learning / RELEASED; score 85
- scope: Operator identified a real gap: the Emergence/Insight (E/I) system was never used during the ProjectUpdater build (TASK-123/124/125) despite emergence/README.md existing and defining project-level insights/ideas/experiments/synthesis…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/release_task.py` [implementation] — Release APPROVED MAP tasks after a completed HPOM checklist. symbols Release Error; connect; ensure schema; ensure agent; validate…
  - `MAP_System/templates/release-checklist.md` [release] — Release Checklist: [TASK-NNN]; Header; Checklist; Summary [What changed in active project state and why this task is ready…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1362

---

# TASK-258 Holdout Packet — S3

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: After the first MAP system-building wave, which subsystems had real operating evidence and which still existed mostly as specifications or templates? | After the first MAP system-building wave, which subsystems had real operating evidence and which still existed mostly as specifications
- algorithm signal: candidate_set (score 251, coverage 27%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

After the first MAP system-building wave, which subsystems had real operating evidence and which still existed mostly as specifications or templates?

## Candidates

### 1. TASK-130 — Gather MAP systems real-usage evidence for TASK-129
- MAP / map-runtime / RELEASED; score 251
- scope: Dependent findings-only slice for TASK-129. Gather grep-backed real-usage evidence for the MAP systems built in TASK-103 through TASK-126, distinguishing operational use from documentation-only existence…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/audits/task-130-map-systems-real-usage-evidence.md` [test] — TASK-130 MAP Systems Real-Usage Evidence; Scope; Evidence Commands; Summary Matrix This note gathers evidence for actual use of…
  - `MAP_System/tasks/TASK-130.json` [task_scope] — Gather MAP systems real-usage evidence for TASK-129 Dependent findings-only slice for TASK-129. Evidence note covers each newly built…

### 2. TASK-103 — Build MAP Research System (docs, templates, folder scaffold)
- MAP / emergence-and-learning / RELEASED; score 246
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #1: MAP has no formal Research System. Build MAP_System/RESEARCH_SYSTEM.md defining the research flow (Research Question -> Research Brief -> Source Map…
- path warning: none
- diverse evidence:
  - `MAP_System/templates/README.md` [artifact] — Templates; Files Reusable templates for MAP-style project memory and coordination.
  - `MAP_System/tasks/TASK-103.json` [task_scope] — Build MAP Research System (docs, templates, folder scaffold) Per Guidelines/MAP_repo_systems_gap_review.md priority #1: MAP has no formal Research System…

### 3. TASK-105 — Build MAP Self-Repair System (docs, templates, folder scaffold)
- MAP / emergence-and-learning / RELEASED; score 242
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #2: MAP has real repair behavior scattered across validate_shared_state.py, validate_decisions.py, validate_task_graph.py, validate_events.py, reconcile_agents.py, map_emergence.py stale, map_metrics.py, and local_assistant_health.py, but no formal…
- path warning: none
- diverse evidence:
  - `MAP_System/templates/README.md` [artifact] — Templates; Files Reusable templates for MAP-style project memory and coordination.
  - `MAP_System/tasks/TASK-105.json` [task_scope] — Build MAP Self-Repair System (docs, templates, folder scaffold) Per Guidelines/MAP_repo_systems_gap_review.md priority #2: MAP has real repair behavior scattered…

### 4. TASK-149 — MAP 6.13: Add trace schema, calibration, and robustness grading plan
- MAP / map-runtime / APPROVED; score 224
- scope: Wave 2 from MAP 6.13 plan. Define traceable visibility, event append/reconstruction behavior, real-parameter measurement, sensitivity/robustness grading, and two simulation-test-drive acceptance probes. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md, MAP_System/events/README.md…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_events.py` [implementation] — Validate and summarize MAP JSONL event logs. symbols summary object; outcome payload; validate choice; validate outcome event; load…
  - `MAP_System/artifacts/audits/map-real-parameter-calibration.md` [artifact] — MAP Real-Parameter Calibration Plan (TASK-149, Wave 2); Purpose; The Four (Now Seven) Parameters To Measure; 1. Compression ratio…

### 5. TASK-121 — Clean up and optimize MAP_System folder structure after gap-review build
- MAP / map-runtime / RELEASED; score 218
- scope: Operator requested continuation after gap fill: take a fresh MAP_System backup, then clean up/optimize the MAP_System folder structure. Apply safe non-destructive cleanup directly; route…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/tests/README.md` [test] — Test Artifacts Use this folder for focused validation notes, test evidence, and command-output
  - `MAP_System/tasks/TASK-121.json` [task_scope] — Clean up and optimize MAP_System folder structure after gap-review build Operator requested continuation after gap fill: take a…

### 6. TASK-107 — Build MAP Context System (formalize context packets, budgets, compression)
- MAP / emergence-and-learning / RELEASED; score 217
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #3: promote notes/context-routing-guide.md and shared/memory-map.md into a formal Context System defining context packet format, required/optional context by task type, forbidden context…
- path warning: none
- diverse evidence:
  - `MAP_System/notes/context-routing-guide.md` [guide] — Context Routing Guide; Default Context Stack; File Relationships; Common Situations Use this guide to decide which MAP files…
  - `MAP_System/templates/CONTEXT_PACKET_TEMPLATE.md` [artifact] — Context Packet; Required; Optional (trigger-gated); Excluded See `MAP_System/CONTEXT_SYSTEM.md` for the rules this packet follows.

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1441

---

# TASK-258 Holdout Packet — S4

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: How can CommandCenterUI receive a ProjectUpdater status snapshot without taking ownership of browser-local data, and what user action produces that snapshot?
- algorithm signal: candidate_set (score 170, coverage 57%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

How can CommandCenterUI receive a ProjectUpdater status snapshot without taking ownership of browser-local data, and what user action produces that snapshot?

## Candidates

### 1. TASK-136 — Add ProjectUpdater status export for CommandCenterUI integration
- ProjectUpdater / command-center-ui / APPROVED; score 170
- scope: Companion to TASK-135 (CommandCenterUI integration, codex-lab-dino). ProjectUpdater is pure browser localStorage with no file-system or server access, so the only honest data bridge to…
- path warning: none
- diverse evidence:
  - `Projects/ProjectUpdater/scripts/validate_project_updater.py` [implementation] — Browser regression checks for the standalone ProjectUpdater app. symbols iso days ago; date days from now; seed data…
  - `MAP_System/emergence/ideas/IDEA-0015-add-an-export-import-json-button-to-projectupdater-to-mitigate-i.md` [artifact] — Idea Card; Idea; Problem or opportunity; Why now Add an Export/Import JSON button to ProjectUpdater to mitigate its…

### 2. TASK-135 — Integrate ProjectUpdater into CommandCenterUI
- ProjectUpdater / command-center-ui / RELEASED; score 131
- scope: Operator asked to integrate ProjectUpdater and CommandCenterUI. Add a small CommandCenterUI integration surface that shows ProjectUpdater status from the local ProjectUpdater app/storage files where…
- path warning: registered output gap
- diverse evidence:
  - `MAP_System/artifacts/planning/task-135-projectupdater-commandcenterui-integration-plan.md` [artifact] — TASK-135 ProjectUpdater + CommandCenterUI Integration Plan; Current State; Proposed First Integration; Intended CommandCenterUI Edits localhost Python backend and…
  - `MAP_System/tasks/TASK-135.json` [task_scope] — Integrate ProjectUpdater into CommandCenterUI Operator asked to integrate ProjectUpdater and CommandCenterUI. CommandCenterUI exposes a ProjectUpdater panel or sidebar…

### 3. TASK-139 — Fix CommandCenterUI ProjectUpdater open/status runtime
- ProjectUpdater / command-center-ui / RELEASED; score 119
- scope: Operator reported that CommandCenterUI's ProjectUpdater card says offline and clicking Open ProjectUpdater does nothing. Fix the released TASK-135 integration so the live app can…
- path warning: registered output gap
- diverse evidence:
  - `MAP_System/tasks/TASK-139.json` [task_scope] — Fix CommandCenterUI ProjectUpdater open/status runtime Operator reported that CommandCenterUI's ProjectUpdater card says offline and clicking Open ProjectUpdater does…
  - `MAP_System/tasks` [bundle] — bundle tasks README md; TASK 001 json; TASK 002 json; TASK 003 json; TASK 004 json; TASK 005…

### 4. TASK-125 — Add ProjectUpdater app regression validation tooling
- ProjectUpdater / map-runtime / RELEASED; score 92
- scope: Follow-up validator/tooling slice delegated by claude-lab-valo after TASK-123 and TASK-124 release. Add reusable regression checks for the standalone ProjectUpdater app so future edits can…
- path warning: none
- diverse evidence:
  - `Projects/ProjectUpdater/scripts/validate_project_updater.py` [implementation] — Browser regression checks for the standalone ProjectUpdater app. symbols iso days ago; date days from now; seed data…
  - `Projects/ProjectUpdater/artifacts/tests/task-125-project-updater-validator.md` [test] — TASK-125 ProjectUpdater Validator Evidence; Scope; Checks Covered; Verification Added a reusable browser regression validator for the standalone ProjectUpdater

### 5. TASK-133 — ProjectUpdater editing, goals, references, and open-folder actions
- ProjectUpdater / map-runtime / RELEASED; score 84
- scope: Operator reported ProjectUpdater cannot edit/delete projects, change/add goals, store a folder/reference for visiting the project, or open the project folder. Implement these project-management operations…
- path warning: none
- diverse evidence:
  - `Projects/ProjectUpdater/scripts/validate_project_updater.py` [implementation] — Browser regression checks for the standalone ProjectUpdater app. symbols iso days ago; date days from now; seed data…
  - `Projects/ProjectUpdater/shared/requirements.md` [artifact] — Requirements — ProjectUpdater; Functional; Non-functional; Quality bar list (stale projects sorted by days idle), and a recent-notes feed.

### 6. TASK-137 — Remove ProjectUpdater Areas sidebar section
- ProjectUpdater / map-runtime / RELEASED; score 79
- scope: Operator requested removing the visible Areas section from the ProjectUpdater sidebar. Keep project area data and existing project cards/forms intact; remove only the sidebar…
- path warning: none
- diverse evidence:
  - `Projects/ProjectUpdater/scripts/validate_project_updater.py` [implementation] — Browser regression checks for the standalone ProjectUpdater app. symbols iso days ago; date days from now; seed data…
  - `MAP_System/tasks/TASK-137.json` [task_scope] — Remove ProjectUpdater Areas sidebar section Operator requested removing the visible Areas section from the ProjectUpdater sidebar. ProjectUpdater sidebar…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1423

---

# TASK-258 Holdout Packet — S5

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: What check exposes drift when SQLite disagrees with either a task JSON record or the workflow graph, including status and output-path mismatches? | What check exposes drift when SQLite disagrees with either a task JSON record | the workflow graph, including status and output-path mismatches
- algorithm signal: candidate_set (score 206, coverage 53%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

What check exposes drift when SQLite disagrees with either a task JSON record or the workflow graph, including status and output-path mismatches?

## Candidates

### 1. TASK-101 — Add source/mirror invariant tests for MAP exports
- MAP / map-runtime / RELEASED; score 206
- scope: Effectiveness review item: source-of-truth drift recurred across map.db, task JSON, workflow graph, and agents/status.json. Add focused regression tests so exporter/seeder changes must preserve DB-to-file…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_task_graph.py` [implementation] — Validate the file-backed MAP task graph. symbols is shared output; load graph; detect cycle; validate; main; visit
  - `MAP_System/tests/test_exporter_invariants.py` [test] — Regression tests for SQLite-to-file export invariants. symbols init db; write existing files; run export; test task statuses match…

### 2. TASK-143 — Add task-state mirror reconciliation gate
- MAP / emergence-and-learning / RELEASED; score 176
- scope: Implement a focused MAP gate that compares canonical SQLite task state with file mirrors in MAP_System/tasks/TASK-*.json and MAP_System/workflow/task_graph.json before review/release, addressing TASK-140/TASK-141 findings about…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_task_mirrors.py` [implementation] — Validate that SQLite task state matches the JSON file mirrors. symbols load json; list values; load db tasks…
  - `MAP_System/tests/test_validate_task_mirrors.py` [test] — Tests for SQLite/file task mirror validation. symbols init db; mirror payload; write mirrors; test matching mirrors pass; test…

### 3. TASK-102 — Prevent canonical repo path drift in MAP docs
- MAP / map-runtime / RELEASED; score 154
- scope: Operator #18530 asked agents to fix process flaws. Concrete flaw: after DEC-014 moved the canonical repo to /home/home/Projects/MultiAgentProject, primary MAP operating docs still referenced…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_canonical_repo_paths.py` [implementation] — Fail when primary operating docs reintroduce the legacy repo path. symbols main
  - `MAP_System/AGENTS.md` [artifact] — Agent Operating Rules; Core Protocol; Documentation Style; Pushback Standard These rules apply to Codex, Claude Code, and any…

### 4. TASK-148 — MAP 6.13: Plan cold-start migration for runtime changes
- MAP / command-center-ui / APPROVED; score 152
- scope: Wave 1.5 from MAP 6.13 plan. Inventory current MAP state and write a migration rollout plan before shipping new runtime layers, so the project…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/tests/map-runtime-migration-smoke.md` [test] — MAP Runtime Migration Smoke Check (TASK-148); Canonical Path; Task Mirrors (SQLite / task JSON / task graph); Event…
  - `MAP_System/tasks/TASK-148.json` [task_scope] — MAP 6.13: Plan cold-start migration for runtime changes Wave 1.5 from MAP 6.13 plan. Inventory names current canonical…

### 5. TASK-116 — Fix runner dependency satisfaction for RELEASED tasks
- MAP / map-runtime / RELEASED; score 142
- scope: Self-Repair follow-up for REPAIR-0001: graph/runner.py treats DONE/APPROVED as dependency-satisfying but omits RELEASED, while validate_task_graph.py treats RELEASED as terminal. Align runner classification with validator terminal…
- path warning: none
- diverse evidence:
  - `MAP_System/graph/runner.py` [implementation] — Executable LangGraph runner for the file-backed MAP workflow. symbols Map State; project relative; load task graph; load tasks…
  - `MAP_System/repairs/REPAIR-0001-runner-released-dependency-drift.md` [artifact] — Repair Record; What was found; Surfaced by; Severity rationale `MAP_System/graph/runner.py` classifies dependency satisfaction using only

### 6. TASK-140 — Audit MAP process use in Command Center Lab
- MAP / command-center-ui / RELEASED; score 142
- scope: Review whether the Command Center Lab is using available MAP processes correctly and consistently, with emphasis on recent operating-loop friction, helper routing, hcom/Monitor use…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/reconcile_agents.py` [implementation] — Compare durable MAP agent status with live hcom agent JSON. symbols load durable; load hcom; reconcile; main
  - `MAP_System/workflow/task_graph.json` [artifact] — artifact task graph json

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1314

---

# TASK-258 Holdout Packet — S6

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: What should operators see when an agent goes quiet, and how should recovery progress from suspicion to nudge or reclaim without turning the dashboard into another state store? | What should operators see when an agent goes quiet, and how should recovery progress from suspicion to nudge | reclaim without turning the dashboard into another state store
- algorithm signal: candidate_set (score 130, coverage 25%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

What should operators see when an agent goes quiet, and how should recovery progress from suspicion to nudge or reclaim without turning the dashboard into another state store?

## Candidates

### 1. TASK-110 — Build MAP Human Interface System (operator dashboard definition)
- MAP / command-center-ui / RELEASED; score 130
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #5: a CommandCenterUI prototype exists (MAP_System/artifacts/command-center-ui/) but live hcom/MAP state wiring is still open, and there is no formal definition of…
- path warning: none
- diverse evidence:
  - `MAP_System/HUMAN_INTERFACE_SYSTEM.md` [artifact] — MAP Human Interface System; What this is; Core principle; Dashboard surface MAP already produces everything an operator needs…
  - `MAP_System/shared/current-state.md` [current_state] — Current State; Live Capabilities; HPOM Gates (all active as of 2026-06-29); Active Agents Last reviewed during TASK-193 (first…

### 2. TASK-112 — Build MAP Security/Permissions System (agent permission levels, destructive-action policy)
- MAP / map-runtime / RELEASED; score 125
- scope: Per Guidelines/MAP_repo_systems_gap_review.md secondary gap: AGENTS.md already has a Security Second Pass rule for network-facing/write-capable outputs, but there is no formal agent permission level model…
- path warning: none
- diverse evidence:
  - `MAP_System/AGENT_PERMISSION_LEVELS.md` [artifact] — MAP Agent Permission Levels; Reading this table; Related files Companion to `SECURITY_PERMISSIONS_SYSTEM.md`.
  - `MAP_System/shared/current-state.md` [current_state] — Current State; Live Capabilities; HPOM Gates (all active as of 2026-06-29); Active Agents Last reviewed during TASK-193 (first…

### 3. TASK-143 — Add task-state mirror reconciliation gate
- MAP / emergence-and-learning / RELEASED; score 120
- scope: Implement a focused MAP gate that compares canonical SQLite task state with file mirrors in MAP_System/tasks/TASK-*.json and MAP_System/workflow/task_graph.json before review/release, addressing TASK-140/TASK-141 findings about…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/map_task.py` [implementation] — Manage MAP tasks in SQLite and sync file mirrors. symbols Usage Error; connect; project id; ensure agent; task…
  - `MAP_System/tests/test_release_gate.py` [test] — Regression tests for HPOM-006 release gate enforcement. symbols init db; run release task; run map task release; export…

### 4. TASK-119 — Harden RnS stale-claim owner nudges
- MAP / agent-liveness-and-helpers / RELEASED; score 109
- scope: Operator-requested follow-up after TASK-117 stalled: RnS recovered agents but did not get work moving because a stale IN_PROGRESS claim made the runner show no…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/limit_watcher.py` [implementation] — Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits. symbols parse resume after; decide nudges; clear…
  - `MAP_System/artifacts/tests/task-119-rns-stale-claim-owner-nudge.md` [test] — TASK-119 RnS Stale-Claim Owner Nudge; Scope; Files; Change Hardened Rise & Shine so a recovered agent does not…

### 5. TASK-158 — MAP 6.13: Implement liveness reaper (real code from TASK-150 spec)
- MAP / agent-liveness-and-helpers / APPROVED; score 96
- scope: Build the actual liveness/reaper code from map-liveness-reaper-spec.md: a script that derives per-agent liveness state (last_seen, active_task, lane, state, state_since, stale_after, evidence) from agents/status.json, hcom…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/liveness_reaper.py` [implementation] — Liveness/reaper implementation for MAP 6.13 Wave 2.5 (TASK-150 spec, TASK-158 build). symbols Liveness Record; now iso; classify state…
  - `MAP_System/shared/liveness-state.md` [artifact] — MAP Liveness State Generated 2026-07-19T18:40:02Z by `scripts/liveness_reaper.py`.

### 6. TASK-126 — Backfill ProjectUpdater E/I records and make Emergence capture mandatory per-project
- ProjectUpdater / emergence-and-learning / RELEASED; score 88
- scope: Operator identified a real gap: the Emergence/Insight (E/I) system was never used during the ProjectUpdater build (TASK-123/124/125) despite emergence/README.md existing and defining project-level insights/ideas/experiments/synthesis…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/release_task.py` [implementation] — Release APPROVED MAP tasks after a completed HPOM checklist. symbols Release Error; connect; ensure schema; ensure agent; validate…
  - `MAP_System/tests/test_release_gate.py` [test] — Regression tests for HPOM-006 release gate enforcement. symbols init db; run release task; run map task release; export…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1409

---

# TASK-258 Holdout Packet — S7

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: How should MAP react to runaway paid-model spend, how is that different from an execution-failure breaker, and who may clear a broad emergency halt?
- algorithm signal: candidate_set (score 181, coverage 62%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

How should MAP react to runaway paid-model spend, how is that different from an execution-failure breaker, and who may clear a broad emergency halt?

## Candidates

### 1. TASK-151 — MAP 6.13: Add cost-governance and kill-switch design
- MAP / map-runtime / APPROVED; score 181
- scope: Wave 3 from MAP 6.13 plan. Design cost fields, per-task/day budgets, spend-rate circuit breaker, and operator kill-switch before broader runtime autonomy. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md, MAP_System/events/README.md…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/planning/map-kill-switch-spec.md` [artifact] — MAP Kill Switch Spec (TASK-151, Wave 3); Purpose; Halt Storage; Who May Set Or Clear The kill switch…
  - `MAP_System/tasks/TASK-151.json` [task_scope] — MAP 6.13: Add cost-governance and kill-switch design Wave 3 from MAP 6.13 plan. Cost spec defines tokens_in, tokens_out…

### 2. TASK-159 — MAP 6.13: Implement cost governance and kill-switch halt enforcement
- MAP / map-runtime / APPROVED; score 172
- scope: Implementation task for approved TASK-151 specs. Build the cost-governance helpers and kill-switch halt store/enforcement path described by MAP_System/artifacts/planning/map-cost-governance-spec.md and map-kill-switch-spec.md. Coordinate with TASK-152 validator…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/cost_governance.py` [implementation] — MAP cost accounting and spend-breaker helpers. symbols Cost Governance Error; utc now; empty cost state; load cost state…
  - `MAP_System/tests/test_halt_state.py` [test] — Tests for durable halt state and dispatch claim gates. symbols init db; test paid halt blocks paid lane…

### 3. TASK-152 — MAP 6.13: Specify protocol and semantic validators with halt authority
- MAP / map-runtime / APPROVED; score 138
- scope: Wave 4 from MAP 6.13 plan. Split hcom/MATOCP protocol compliance from semantic output-correctness validation, specify Layer 1 deterministic checks vs Layer 2 fuzzy judge…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/planning/map-protocol-validator-spec.md` [guide] — MAP Protocol Validator Spec (TASK-152, Wave 4); Purpose; Scope; Known Spec Discrepancy (found during this task, must be…
  - `MAP_System/artifacts/tests/map-validator-halt-probe.md` [test] — MAP Validator Halt Probe (TASK-152, Wave 4); Purpose; What This Probe Can Demonstrate Today (structural halt, already built)…

### 4. TASK-156 — MAP 6.13: Build governance pre-dispatch and threat-model plan
- MAP / map-runtime / APPROVED; score 130
- scope: Wave 8 from MAP 6.13 plan. Design pre-dispatch policy checking, destructive-action gates, capability whitelist tests, and threat model. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md, MAP_System/AGENT_PERMISSION_LEVELS.md, MAP_System/DESTRUCTIVE_ACTION_POLICY.md, MAP_System/DECISION_CLASSES.md, MAP_System/SECURITY_PERMISSIONS_SYSTEM.md…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/audits/map-threat-model.md` [artifact] — MAP Threat Model (TASK-156, Wave 8); Purpose; Assets; Actors This threat model identifies the control surfaces where MAP…
  - `MAP_System/tasks/TASK-156.json` [task_scope] — MAP 6.13: Build governance pre-dispatch and threat-model plan Wave 8 from MAP 6.13 plan. Policy-checker spec emits allow…

### 5. TASK-155 — MAP 6.13: Design resilience controls and chaos tests
- MAP / map-runtime / APPROVED; score 124
- scope: Wave 7 from MAP 6.13 plan. Design idempotency registry, dead-letter queue, durable/resumable execution, circuit breakers, chaos tests, degradation policy, and dependency DAG support. Read…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/planning/map-durable-execution-spec.md` [artifact] — MAP Durable Execution Spec (TASK-155, Wave 7); Purpose; Scope; Checkpoint Model `scripts/agent_loop.py` already has a LangGraph checkpointer, task…
  - `MAP_System/tasks/TASK-155.json` [task_scope] — MAP 6.13: Design resilience controls and chaos tests Wave 7 from MAP 6.13 plan. Resilience spec defines idempotency…

### 6. TASK-157 — MAP 6.13: Verify formal invariants, multi-project fit, roster, and assumptions
- MAP / map-runtime / APPROVED; score 112
- scope: Wave 9 from MAP 6.13 plan. Run the verification and audit pass: narrow formal invariant spike, MAST-style failure coverage, multi-project readiness, roster composition, and…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/audits/map-failure-taxonomy-coverage.md` [artifact] — MAP Failure Taxonomy Coverage (TASK-157, Wave 9); Purpose; Coverage Matrix; Existing Strong Areas This audit maps known MAP…
  - `MAP_System/tasks/TASK-157.json` [task_scope] — MAP 6.13: Verify formal invariants, multi-project fit, roster, and assumptions Wave 9 from MAP 6.13 plan. Formal invariant…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1390

---

# TASK-258 Holdout Packet — S8

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: Which narrow jobs may a local helper draft, and which dispatch fields determine whether work stays in a local lane or escalates to core or operator authority? | Which narrow jobs may a local helper draft, and which dispatch fields determine whether work stays in a local lane
- algorithm signal: candidate_set (score 199, coverage 44%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

Which narrow jobs may a local helper draft, and which dispatch fields determine whether work stays in a local lane or escalates to core or operator authority?

## Candidates

### 1. TASK-153 — MAP 6.13: Add gap scoring, task tiers, and local-helper lanes
- MAP / emergence-and-learning / APPROVED; score 199
- scope: Wave 5 from MAP 6.13 plan. Define gap scoring, task_tier, local_lane, escalation_reason, emergence preflight suggestions, local-helper lane wrappers, and bounded learning guard. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md…
- path warning: none
- diverse evidence:
  - `MAP_System/tasks/TASK-153.json` [task_scope] — MAP 6.13: Add gap scoring, task tiers, and local-helper lanes Wave 5 from MAP 6.13 plan. Task-tiering spec…
  - `MAP_System/artifacts/planning/map-local-helper-lanes-spec.md` [artifact] — MAP Local Helper Lanes Spec (TASK-153, Wave 5); Purpose; Lane Contract; Allowed Lanes Local helpers reduce paid-model load…

### 2. TASK-138 — Document auto-helper routing for reviewer conflicts
- MAP / emergence-and-learning / RELEASED; score 129
- scope: Operator identified that routine no-self-review reviewer conflicts should not be escalated back to the operator when existing MAP helper policy can solve them. Document…
- path warning: none
- diverse evidence:
  - `MAP_System/tasks/TASK-138.json` [task_scope] — Document auto-helper routing for reviewer conflicts Operator identified that routine no-self-review reviewer conflicts should not be escalated back…
  - `MAP_System/emergence/insights/INS-0015-a-routine-no-self-review-reviewer-conflict-should-trigger-the-ex.md` [review] — Insight Record; Short description; Trigger; The synthesis A routine no-self-review reviewer conflict should trigger the existing visible-helper path…

### 3. TASK-159 — MAP 6.13: Implement cost governance and kill-switch halt enforcement
- MAP / map-runtime / APPROVED; score 119
- scope: Implementation task for approved TASK-151 specs. Build the cost-governance helpers and kill-switch halt store/enforcement path described by MAP_System/artifacts/planning/map-cost-governance-spec.md and map-kill-switch-spec.md. Coordinate with TASK-152 validator…
- path warning: none
- diverse evidence:
  - `MAP_System/tasks/TASK-159.json` [task_scope] — MAP 6.13: Implement cost governance and kill-switch halt enforcement Implementation task for approved TASK-151 specs. Implements a durable…
  - `MAP_System/tests/test_halt_state.py` [test] — Tests for durable halt state and dispatch claim gates. symbols init db; test paid halt blocks paid lane…

### 4. TASK-156 — MAP 6.13: Build governance pre-dispatch and threat-model plan
- MAP / map-runtime / APPROVED; score 108
- scope: Wave 8 from MAP 6.13 plan. Design pre-dispatch policy checking, destructive-action gates, capability whitelist tests, and threat model. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md, MAP_System/AGENT_PERMISSION_LEVELS.md, MAP_System/DESTRUCTIVE_ACTION_POLICY.md, MAP_System/DECISION_CLASSES.md, MAP_System/SECURITY_PERMISSIONS_SYSTEM.md…
- path warning: none
- diverse evidence:
  - `MAP_System/tasks/TASK-156.json` [task_scope] — MAP 6.13: Build governance pre-dispatch and threat-model plan Wave 8 from MAP 6.13 plan. Policy-checker spec emits allow…
  - `MAP_System/artifacts/planning/map-pre-dispatch-policy-checker-spec.md` [artifact] — MAP Pre-Dispatch Policy Checker Spec (TASK-156, Wave 8); Purpose; Inputs; Outputs The pre-dispatch policy checker decides whether a…

### 5. TASK-147 — MAP 6.13: Build orchestration entrypoint and decomposer contract
- MAP / map-runtime / APPROVED; score 98
- scope: Wave 1 from MAP_System/artifacts/planning/map-613-master-implementation-plan.md. Define the single command-center entrypoint and decomposer contract for turning raw operator intent into protocol-shaped dispatch packets with subtasks, dependencies…
- path warning: none
- diverse evidence:
  - `MAP_System/tasks/TASK-147.json` [task_scope] — MAP 6.13: Build orchestration entrypoint and decomposer contract Wave 1 from MAP_System/artifacts/planning/map-613-master-implementation-plan.md. Defines one operator-intent entrypoint and when…
  - `MAP_System/tests/test_intake_request.py` [test] — Tests for MAP operator intake dispatch packets. symbols test build request emits decomposer fields; test publish request requires…

### 6. TASK-108 — Build MAP Decision/Authority System (decision classes, authority hierarchy)
- MAP / agent-liveness-and-helpers / RELEASED; score 96
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #4: shared/decisions.md records decisions well but does not formally define who can decide what, what requires human approval, what a core…
- path warning: none
- diverse evidence:
  - `MAP_System/shared/decisions.md` [decision] — Decisions; DEC-001: Use File-Backed State First; DEC-002: LangGraph Is The Orchestrator; DEC-003: One Owner Per Active Task Use…
  - `MAP_System/DECISION_AUTHORITY_SYSTEM.md` [artifact] — MAP Decision / Authority System; What this is; Core principle; Authority tiers, applied to decisions `shared/decisions.md` already records…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1494

---

# TASK-258 Holdout Packet — S9

Generated retrieval aid; not authority. Use only this packet.
- corpus: 60 deterministic task/source fingerprints
- decomposed into: Which historical task implemented automatic secret scanning and redaction for MAP event records before they are committed?
- algorithm signal: no_strong_match (score 116, coverage 18%)
- watermark: 2026-07-19T18:43:47Z
- truth: withheld; no strong match is a valid answer

## Query

Which historical task implemented automatic secret scanning and redaction for MAP event records before they are committed?

## Candidates

### 1. TASK-149 — MAP 6.13: Add trace schema, calibration, and robustness grading plan
- MAP / map-runtime / APPROVED; score 116
- scope: Wave 2 from MAP 6.13 plan. Define traceable visibility, event append/reconstruction behavior, real-parameter measurement, sensitivity/robustness grading, and two simulation-test-drive acceptance probes. Read MAP_System/artifacts/planning/map-613-master-implementation-plan.md, MAP_System/events/README.md…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_events.py` [implementation] — Validate and summarize MAP JSONL event logs. symbols summary object; outcome payload; validate choice; validate outcome event; load…
  - `MAP_System/artifacts/planning/map-event-trace-schema.md` [artifact] — MAP Event Trace Schema (TASK-149, Wave 2); Purpose; Fields; Why Not Required Yet Closes the 6.13 Requirements gap…

### 2. TASK-114 — Build MAP Change Control System (change requests, release records, rollback)
- MAP / map-runtime / RELEASED; score 108
- scope: Per Guidelines/MAP_repo_systems_gap_review.md secondary gap: normal Git, map-git wrapper, git operation lock, canonical repo decisions, and the release-path smoke checklist already exist, but change request…
- path warning: none
- diverse evidence:
  - `MAP_System/DECISION_AUTHORITY_SYSTEM.md` [artifact] — MAP Decision / Authority System; What this is; Core principle; Authority tiers, applied to decisions `shared/decisions.md` already records…
  - `MAP_System/tasks/TASK-114.json` [task_scope] — Build MAP Change Control System (change requests, release records, rollback) Per Guidelines/MAP_repo_systems_gap_review.md secondary gap: normal Git, map-git wrapper…

### 3. TASK-142 — Broadcast-coordinator convention + Research System decision + event-warning baseline cleanup
- MAP / map-runtime / RELEASED; score 98
- scope: Follow-up to TASK-140/141: (1) add a durable broadcast-coordinator convention to AGENTS.md/helper-agent-guide so multi-agent hcom broadcasts declare owner/scope instead of relying on ad-hoc good behavior…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/validate_events.py` [implementation] — Validate and summarize MAP JSONL event logs. symbols summary object; outcome payload; validate choice; validate outcome event; load…
  - `MAP_System/tests/test_validate_events.py` [test] — Tests for MAP event-log validation. symbols test validate events warns on legacy shape; test fail on new ignores…

### 4. TASK-159 — MAP 6.13: Implement cost governance and kill-switch halt enforcement
- MAP / map-runtime / APPROVED; score 96
- scope: Implementation task for approved TASK-151 specs. Build the cost-governance helpers and kill-switch halt store/enforcement path described by MAP_System/artifacts/planning/map-cost-governance-spec.md and map-kill-switch-spec.md. Coordinate with TASK-152 validator…
- path warning: none
- diverse evidence:
  - `MAP_System/scripts/halt_state.py` [implementation] — Durable MAP dispatch halt state helpers. symbols Halt State Error; current halt path; utc now; parse iso datetime…
  - `MAP_System/tests/test_cost_governance.py` [test] — Tests for MAP cost governance helpers. symbols test cost counter records known paid cost; test paid unknown cost…

### 5. TASK-108 — Build MAP Decision/Authority System (decision classes, authority hierarchy)
- MAP / agent-liveness-and-helpers / RELEASED; score 93
- scope: Per Guidelines/MAP_repo_systems_gap_review.md priority #4: shared/decisions.md records decisions well but does not formally define who can decide what, what requires human approval, what a core…
- path warning: none
- diverse evidence:
  - `MAP_System/DECISION_AUTHORITY_SYSTEM.md` [artifact] — MAP Decision / Authority System; What this is; Core principle; Authority tiers, applied to decisions `shared/decisions.md` already records…
  - `MAP_System/tasks/TASK-108.json` [task_scope] — Build MAP Decision/Authority System (decision classes, authority hierarchy) Per Guidelines/MAP_repo_systems_gap_review.md priority #4: shared/decisions.md records decisions well but does…

### 6. TASK-148 — MAP 6.13: Plan cold-start migration for runtime changes
- MAP / command-center-ui / APPROVED; score 93
- scope: Wave 1.5 from MAP 6.13 plan. Inventory current MAP state and write a migration rollout plan before shipping new runtime layers, so the project…
- path warning: none
- diverse evidence:
  - `MAP_System/artifacts/tests/map-runtime-migration-smoke.md` [test] — MAP Runtime Migration Smoke Check (TASK-148); Canonical Path; Task Mirrors (SQLite / task JSON / task graph); Event…
  - `MAP_System/tasks/TASK-148.json` [task_scope] — MAP 6.13: Plan cold-start migration for runtime changes Wave 1.5 from MAP 6.13 plan. Inventory names current canonical…

## Required response

Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two
source paths | confidence high/medium/low | concise rationale`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1393

---
