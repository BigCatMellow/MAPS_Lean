<!-- hpom: file: shared/current-state.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: scripts/render_active_state.py plus scripts/validate_shared_state_tasks.py against live map.db -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Current State

This file is the current operating snapshot, not a cumulative transcript.
Compacted history for the TASK-147–192 era lives in
`archive/compactions/compaction-2026-07-14-tasks-147-192.md`. The current
project purpose and authority model are summarized in `shared/project-brief.md`.

## Alignment Baseline - 2026-07-28

- Project direction: ship useful software through MAP's owned, reviewable,
  reversible delivery flow (DEC-028), not framework expansion for its own sake.
- Operator surface: the AI Command Center is for decisions, approvals,
  blockers, conflicts, and safety/scope attention. Routine progress remains
  visible through `hcom --intent inform` and durable MAP records.
- Authority: Codex and Claude are the active core agents. Pi is
  exploratory-only. Helpers and local models are bounded support capabilities,
  never alternate task/review/release authorities.
- Worker selection: HPOM means use the cheapest competent model at the right
  reasoning tier. Core agents remain accountable integrators, but should route
  bounded checks/drafts/reviews to visible Haiku, Sonnet, Opus, local-model, or
  Aider helpers when the task shape fits. Do not default every unit of work to
  the core session merely because it is already open.
- State authority: SQLite coordinates claims; task JSON and the graph are
  synchronized human-readable mirrors; decisions and shared state carry
  canonical meaning; hcom and UI views are communication surfaces.
- Delivery posture: the operational recovery queue is nearly discharged. The
  remaining framework debt is the release backlog below, not new subsystems.
  The next substantive move is an operator direction call: select another real
  software slice (DEC-028's proving workflow) rather than extending MAP
  infrastructure by default.
- Release backlog (2026-07-28): 29 tasks sit APPROVED with no release
  checklist, some since 2026-07-17. Independent review passed on all of them;
  only the release ceremony is outstanding. This is the single largest gap
  between MAP's stated completion condition ("real software moves through
  intake, claim, implementation, verification, independent review, and
  release") and live state. Treat it as real work: the release gate's checks
  assert verified facts, so the backlog is discharged by verifying each task,
  not by ticking boxes in bulk.

<!-- BEGIN GENERATED ACTIVE LANES -->
## Active Execution Lanes — generated

Lifecycle fields below are generated from read-only `map.db`. Lane selection,
ordering, rationale, and gate text come from
`shared/active-lane-annotations.json`; the renderer never parses surrounding
prose as lifecycle truth.

Authority freshness: `AUTHORITATIVE` — mode=`authority` host=`self` revision=`sha256:529f87d476e61c714a8c01bb2375907060774660f5a38a97a85c77c22b0c7590` last_sync=`never`

| Order | Task | State | Durable owner | `claimed_by` / current worker | Why now / gate |
|---|---|---|---|---|---|
| 1 | TASK-263 | CHANGES_REQUESTED | `codex-lab-kiri` | none | Frozen claim-evidence retrieval experiment (EXP-0006); the last unreviewed submission in the queue. Submitted by claude-lab-lili at attempt 3/3 while codex was offline. Under independent review; implementer and freeze author are both disqualified from reviewing. Implementer self-scored because no blind evaluator was live -- disclosed, not hidden, and explicitly referred to the reviewer for judgment. |

Projection diagnostics:

- none
<!-- END GENERATED ACTIVE LANES -->

The generated projection replaces the former hand-maintained lifecycle table.
`validate_shared_state_tasks.py` remains the independent consistency check
during migration. `claimed_by` records the SQLite claimant; it is not a
substitute for durable ownership, decision authority, model fit, or a current
heartbeat. Historical lifecycle narrative elsewhere in this file is prose, not
an input to the renderer.

### Worker / Model Fit For The Recovery Queue

| Work | Accountable owner | Support tier |
|---|---|---|
| TASK-263 independent review | Core reviewer, not the implementer | Sonnet fits the evidence-boundary judgment. Implementer (claude-lab-lili) and freeze author (claude-lab-gabi) are both disqualified. |
| TASK-254 reconciliation | Core owner after rework | Sonnet fits the cross-file scope/authority reasoning that produced both prior rejections. |
| TASK-289 enum doc drift | Any core agent | Sonnet or Haiku; the fix is mechanical once the live enum is confirmed by grep plus a map.db query. |
| Release backlog (29 tasks) | Core owner per task | Sonnet per batch. Each checklist asserts verified facts, so this is verification work, not clerical work; do not batch-tick. |

The current helper/local inventory is not a mandate to use every model. A
helper is opened only with a bounded purpose, durable note, visible terminal,
stop condition, and core integration owner.

## Live Capabilities

- Normal root Git is available for Aider and standard Git tooling.
- GitHub remote `origin` points to
  `https://github.com/BigCatMellow/MultiAgentProject.git`.
- SQLite-backed task claiming exists in `db/claims.py` and `map.db`.
- The LangGraph runner lives in `graph/runner.py`.
- `requirements.txt` constrains LangGraph dependencies to the stable 1.x line
  (`langgraph>=1.0,<2.0`, `langchain-core>=1.0,<2.0`) based on the TASK-145
  Research Summary.
- The autonomous claim loop lives in `scripts/agent_loop.py`.
- File-backed task mirrors live in `tasks/` and `workflow/task_graph.json`.
- Agent availability lives in `agents/status.json`.
- Integration and multi-gate regression tests are wired into `scripts/run_tests.sh`.
- The limit watcher (`scripts/limit_watcher.py`, TASK-080, APPROVED) runs in the
  background and auto-resumes agents after usage-limit resets: the default poll
  interval is 90 minutes (`5400s`), chosen against the 5-hour agent refresh
  window. It polls `agents/status.json` for `out_of_tokens` + ISO-8601
  `resume_after`, resumes via visible `hcom r <name> --terminal wezterm-tab`
  (one nudge per window), and reports silent stops. Start/stop:
  `scripts/start-limit-watcher.sh` /
  `kill $(cat .locks/limit-watcher.pid)`. Protocol: `notes/limit-exhaustion-protocol.md`.
- `map_task.py rework` returns a CHANGES_REQUESTED task to a claimable state
  (TASK-081; closes the rework dead-end found during TASK-080's rejection).
- `scripts/validate_task_mirrors.py` compares canonical SQLite task state with
  `tasks/TASK-*.json` and `workflow/task_graph.json`. `map_task.py approve`,
  `release_task.py`, and `scripts/run_tests.sh` run this gate so stale file
  mirrors fail before approval/release instead of relying on agent memory.
- A release-path smoke checklist for user-facing packages lives in
  `notes/release-path-checklist.md` (PROMO-0005). A security second-pass rule
  for network-facing/write-capable outputs is in `AGENTS.md` Review Standard
  (PROMO-0004).
- Task graph validation currently passes.
- `scripts/map_task.py create --task-id auto` allocates the next task ID under
  a SQLite write lock so concurrent agents do not manually collide on task IDs.
- Local Ollama helper runner lives in `scripts/local_runner.py` (TASK-048, APPROVED).
- Supervised Aider setup wrapper lives in `scripts/aider_wrapper.py` (TASK-049, APPROVED).
- Emergence capture tooling lives in `scripts/map_emergence.py`. It can create
  insight, synthesis, idea, experiment, and promotion records from templates,
  rebuild `emergence/INDEX.md`, print the registry, validate artifact files,
  and report stale/placeholder lifecycle issues with `map_emergence.py stale`.
- Emergence records are compact-by-default and wikilinked (TASK-180/181/183,
  2026-07-14): new templates use terse `- label:` bullets, the generated
  INDEX wikilinks resolvable references, and `map_emergence.py compact`
  (dry-run default, `--apply`, idempotent) converts historical prose records
  without touching closed statuses. All active records are converted. Local
  models were trialed for the rewrites and rejected as not yet reliable
  (TASK-181 report: `artifacts/planning/emergence-local-librarian-report.md`).
- External CommandCenterUI is current with the MAP runtime (TASK-182,
  2026-07-14): read-only `GET /api/map/health` + a sidebar "MAP runtime" card
  showing runner route, librarian wikilink validation, session-replay index
  health, and RnS watcher state (ok/warn/error per source, 20s cache,
  per-source error isolation). Record:
  `artifacts/command-center-ui/task-182-map-health-cards.md`.
- Event log shape reporting lives in `scripts/validate_events.py`; default mode
  reports legacy aliases and missing optional canonical fields, while
  `--fail-on-new` uses `events/warning_baseline.json` to fail only warnings
  added after the accepted historical baseline.
- Git operation coordination lock tooling lives in `scripts/git_operation_lock.py`.
- Agent status reconciliation reporting lives in `scripts/reconcile_agents.py`.
- Operator request intake recommendation helper lives in `scripts/intake_request.py`.
- Canonical local repo status is recorded in `shared/canonical-repo.md`.
- Approval calibration rules are recorded in `shared/approval-calibration.md`.
- The eleven governance systems (DEC-015..026, TASK-103–126) are all built and
  cross-linked; each system doc is its own canonical reference:

| System | DEC | Doc |
|---|---|---|
| Research | DEC-015 | `RESEARCH_SYSTEM.md` + `templates/research/` |
| Self-Repair | DEC-016 | `SELF_REPAIR_SYSTEM.md` + `repairs/` |
| Context | DEC-017 | `CONTEXT_SYSTEM.md` |
| Decision/Authority | DEC-018 | `DECISION_AUTHORITY_SYSTEM.md`, `DECISION_CLASSES.md` |
| Human Interface | DEC-019 | `HUMAN_INTERFACE_SYSTEM.md` |
| Risk | DEC-020 | `RISK_SYSTEM.md` |
| Security/Permissions | DEC-021 | `SECURITY_PERMISSIONS_SYSTEM.md`, `AGENT_PERMISSION_LEVELS.md`, `DESTRUCTIVE_ACTION_POLICY.md` |
| Change Control | DEC-022 | `CHANGE_CONTROL_SYSTEM.md` |
| Project Bootstrapping | DEC-023 | `PROJECT_BOOTSTRAPPING_SYSTEM.md`, `NEW_PROJECT_WIZARD.md` |
| Archive/Retention | DEC-024 | `ARCHIVE_RETENTION_SYSTEM.md` |
| Retrospective | DEC-025 | `RETROSPECTIVE_SYSTEM.md` + `retros/` |
| Emergence capture mandatory | DEC-026 | `emergence/README.md`; release gate enforces "Emergence capture considered" |

- Systems-use posture (TASK-140/143): don't force every system into every
  task. Emergence is actively used and enforced; Research is invoked when a
  task needs sourced, current, external, or disputed facts.

### HPOM Gates (all active as of 2026-06-29)

| Gate | Script | Status |
|---|---|---|
| READY promotion | `scripts/promote_task.py` | ACTIVE — blocks CONFLICT tasks, requires 8 HPOM fields |
| No-self-review (claim) | `db/claims.py` `claim_block_reason()` | ACTIVE — claim fails if agent == task owner on review tasks |
| Review gate | `scripts/validate_review.py` + `map_task.py approve --review-record` | ACTIVE — APPROVED requires valid review record |
| Release gate | `scripts/release_task.py` + `map_task.py release --checklist` | ACTIVE — RELEASED requires completed checklist + record |
| Conflict freeze | `scripts/flag_conflict.py` | ACTIVE — CONFLICT status blocks promotion |
| Shared-state metadata | `scripts/validate_shared_state.py` | ACTIVE — 9 HPOM fields required per shared file |
| Decision log | `scripts/validate_decisions.py` | ACTIVE — required fields checked, index auto-generated |
| Metrics dashboard | `scripts/map_metrics.py` | ACTIVE — read-only health report (text + JSON) |
| Task ID allocation | `scripts/map_task.py create --task-id auto` | ACTIVE — reserves next TASK-NNN inside SQLite write transaction |
| Event log report | `scripts/validate_events.py` | ACTIVE — reports legacy schema/type aliases and fails new warnings with `--fail-on-new` |
| Emergence stale report | `scripts/map_emergence.py stale` | ACTIVE — reports stale, placeholder, and dangling emergence records |
| Git operation lock | `scripts/git_operation_lock.py` | ACTIVE — non-destructive lock for repo-global operations |
| Task mirror reconciliation | `scripts/validate_task_mirrors.py` | ACTIVE — blocks approval/release when SQLite, task JSON, or task graph mirrors drift |

## Active Agents

- Codex and Claude Code are the active core agents.
- Gemini is standby/manual unless the operator explicitly activates it. Antigravity is retired from active Command Center routing under TASK-320; preserve historical/generic provider records only.
- Temporary helpers are allowed when task-scoped and recorded in `inbox/helpers/`.
- Local Ollama models and Aider are helper capabilities, not registered core agents; see `notes/local-model-helper-guide.md`.
- Pi is **exploratory-only** (operator decision 2026-07-21, superseding the
  2026-07-18 blanket pause). Pi may be used for capability probes, drafts, and
  bounded experiments whenever useful, because it is token-free and costs
  nothing to try. It must run as a visible instance.
  **Authority limit unchanged and still binding:** do not route tasks, reviews,
  handoffs, releases, routing, or capacity plans through Pi. The 2026-07-18
  Trial C using `ollama/qwen2.5-coder:7b-16k --offline` failed its no-write
  communication drill — no required hcom acknowledgement was observed and
  terminal text made a malformed delivery claim — and that capability finding
  stands. Exploratory use no longer needs per-run authorization; operational
  authority still does not exist. Record exploratory runs durably so the
  TASK-261 gap (a Pi run with no authorization record) does not recur. See
  `notes/pi-agent-communication-guide.md`,
  `artifacts/experiments/pi-local-capability-trial-2026-07-18.md`, and the
  DECISION_RECORDED event for TASK-261 (2026-07-21).
- Local assistants should take scoped support load off paid/core agents through
  summaries, checks, drafts, recommendations, and diff suggestions.
- HPOM is now defined as the Human-Paced Orchestration Model: a routing and
  assignment discipline for deciding when to use humans, core agents, helpers,
  local models, or Aider. See `shared/hpom.md` and
  `shared/agent-capability-matrix.md`.

## Known Health Issues

- All shared files are CURRENT (`validate_shared_state.py`: 23/23 on 2026-07-22).
- Some historical artifacts still mention the old `langgraph/` directory. The live code path is `graph/`.
- Canonical repo for this live environment is
  `/home/mellow/Projects/MultiAgentProject` with the shared workspace rooted at
  `Source/`; see `shared/canonical-repo.md`. DEC-014's durable rule remains the
  Projects checkout, not the retired Downloads checkout.
- `validate_events.py` reports 33 accepted legacy warnings; `--fail-on-new`
  with `events/warning_baseline.json` blocks new ones.
- TASK-186 is RELEASED on operator-selected option A. Its checklist preserves
  the evidence limitation: no post-restart live terminal-attribution transition
  was available, and no live session was falsely marked terminal to manufacture
  one. The next natural terminal transition is follow-up confirmation, not a
  release blocker.
- SYN-0001 (one state, multiple readers, no declared authority) remains the
  highest-leverage unresolved system pattern. It has recurred in approval-gate
  inputs, reviewer registration, and exporter/watcher terminal state. The next
  shaping task must declare the authoritative writer/reader contract and add
  end-to-end reachability evidence for each live instance.
- Open follow-up items are tracked in `shared/improvement-backlog.md`.
- Deferred command-center items are tracked in `notes/command-center-later.md`.
- Command Center Lab emergence integration is active through
  `scripts/map_emergence.py`; use capture when real insights, ideas,
  experiments, synthesis, or promotions appear, and skip ceremony when no
  candidate exists.

## Safety Notes

- Normal root Git is available. `scripts/map-git` remains as a compatibility
  wrapper.
- Before using Aider for more than narrow helper edits, review and commit the
  current MAP cleanup/restructure so rollback points are clear.
- Treat `artifacts/` as historical unless a current task points to a specific artifact.
- Treat `archive/` as historical compacted memory unless a current task points to a specific archived file.
- Do not silently fill missing task acceptance criteria or output paths without understanding task intent.
- Handler commands passed to `scripts/agent_loop.py` are trusted operator configuration and should not be built from untrusted input.
- Run brain compaction periodically so active memory stays lean; see `notes/brain-compaction-guide.md`.
- Push back on changes that hide ownership, erase history, over-automate ambiguous work, or make active memory noisier.
