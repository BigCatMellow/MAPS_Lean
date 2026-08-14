# Agent Operating Rules

These rules apply to Codex, Claude Code, and any future worker agent in this workspace.

## Canonical Authority Hierarchy

`shared/project-brief.md` → `Operating Model` is the canonical authority view.
Every prompt, runtime surface, and task must preserve this order:

1. `bigboss` / operator / Command Center owns intent, priority, policy and
   scope decisions, high-authority approvals, veto, and stop control.
2. One operator-designated coordinator may integrate and route a run. Codex
   and Claude are the eligible peer core agents (DEC-008); fixed-roster
   visibility or provider/model identity does not designate the coordinator.
3. Each active task has one accountable owner and a different independent
   reviewer. These are parallel, conflict-separated lifecycle roles, not
   permanent ranks, and SQLite claims/review records bind them.
4. Pi, Librarian, visible helpers, and local assistants provide bounded support
   under a named accountable owner. They gain no task, review, release,
   routing, policy, or operator authority.

RUKI SQLite stores canonical lifecycle state, LangGraph recommends routes,
hcom communicates, and Command Center presents operator controls. Control
systems and open terminals do not become authorities merely by storing,
moving, or displaying state. A context replacement continues a designated
coordinator role only after checksum-bound finalization and only when the
frozen snapshot explicitly preserves that existing designation; rotation
never creates or elevates authority.

## Retrieval capsule

- Purpose: Defines the canonical operating rules for MAP task ownership, durable coordination, helper visibility, review separation, authority boundaries, and safe multi-agent work inside this repository.
- Proves: The required behavior for claiming tasks, preserving durable evidence, communicating through hcom, counting helper capacity, routing independent review, and avoiding silent output collisions.
- Applies to: Core agents and visible model-backed helpers performing reusable MAP system work under `MAP_System/`.
- Does not provide: Project-specific requirements, permission to bypass SQLite task state, operator approvals, destructive-action safeguards, independent review, or release gates.
- Evidence type: governing_rule
- Status: current

## Core Protocol

1. Work only on an assigned or explicitly claimed task from `tasks/`.
2. Read `shared/project-brief.md`, `shared/requirements.md`, `shared/decisions.md`, and the task file before editing.
3. Keep one accountable owner per active task.
4. Do not silently modify another active task's owned output paths.
5. Record important assumptions in `shared/unresolved-questions.md` or `shared/decisions.md`.
6. Put durable work in `artifacts/`, `shared/`, `workflow/`, `tasks/`, or source files, not only in chat.
7. Use `events/events.jsonl` for short append-only activity records.
8. Use `handoffs/` for work that another agent should review or continue.
9. Do not approve your own substantive deliverable.
10. Stop when the task acceptance criteria are met.
11. When you check `graph/runner.py`'s output (a standing startup habit), also
    read its `emergence_sentinel` field. If `pending_candidates > 0` or
    `scan_stale` is true, run `scripts/emergence_sentinel.py list` and curate
    what you can before moving on — see `SELF_REPAIR_SYSTEM.md`. This queue
    sat uncurated for 9 days (2026-07-18 to 2026-07-27, 12 candidates) before
    anyone looked at it; it has no cadence of its own, so treat this check as
    part of the routine, not optional follow-up.
12. When you orient off `shared/current-state.md` (also a standing startup
    habit), also run `scripts/validate_shared_state_tasks.py` (or
    `scripts/render_active_state.py --check`). If it reports drift,
    regenerate the file with `scripts/render_active_state.py` and fix any
    stale entries in `shared/active-lane-annotations.json` before treating
    the file as orientation truth — see `notes/command-center-lab-restart-startup.md`.
    Do not regenerate `current-state.md` silently as a side effect of another
    agent's startup: it is shared canonical state, and an unannounced rewrite
    while another agent is reading it would recreate the SYN-0001 pattern
    (one state, multiple readers, no declared authority) instead of fixing
    it — regenerate it as its own visible step. This table drifted from
    `map.db` for 6 days (TASK-263/265/274/276 rows, found 2026-07-28) before
    anyone looked at it; the check already exists and runs in
    `scripts/run_tests.sh`, but nothing ran it at startup, so treat this as
    part of the routine, not optional follow-up.
13. If work touches the MAP Bedrock program (the map-2 research-adoption
    plan, `artifacts/planning/map-2-research-adoption-implementation-program-2026-08-09.md`),
    read `artifacts/planning/map-bedrock-phase-checklist-2026-08-10.md`
    first for current phase/status/next-action — it is the tracked
    execution state, kept current as work lands; the plan document is the
    design and does not update itself. A "MAP Bedrock" project in
    `Projects/ProjectUpdater/app/index.html` mirrors the same checklist as
    a human-facing dashboard (imported from the file, not independently
    authoritative) — the operator may check that instead of asking in
    chat, so keep it re-imported (`Projects/ProjectUpdater/scripts/project_updater_command.py
    update "MAP Bedrock" --steps-file <this file>`) whenever the checklist
    file changes.

## Remote MAP authority failures

On a mirror host, a sanctioned `map-authority` CLI verb is the required route
to RUKI, but the verb is not a classifier exemption. The remote SSH boundary
and the requested lifecycle mutation are still subject to policy controls and
version compatibility.

If a sanctioned call is denied or fails, preserve the exact command, exit
status, stdout/stderr, local and authority versions when available, and the
task state observed before and after. Report that evidence to the accountable
owner. Do not blindly retry, invent an alternate transport, bypass the
classifier, or treat a policy denial as permission to mutate the read-only
mirror. Retry only after the blocking condition is identified and the normal
authority path is explicitly cleared.

## Documentation Style

All MAP Markdown and template files should be agent-readable first. Prefer
structured fields, stable IDs, explicit statuses, file paths, task IDs, and
bullets over prose narrative.

Use complete sentences when explaining risk, tradeoff, exception, conflict, or
decision reasoning. For normal state, use compact structure.

See `notes/documentation-style-guide.md`.

## Pushback Standard

Agents should push back when a request or proposed design would make MAP more
fragile, ambiguous, expensive to read, or unsafe.

Push back especially on:

- over-design before current validation failures are fixed;
- adding new files that do not change agent behavior;
- database triggers before script-level gates are proven;
- self-healing flows that silently invent task intent;
- helper communication that bypasses ownership;
- compaction that deletes raw history instead of summarizing forward;
- changes that hide task ownership, status, output paths, or acceptance criteria.

When pushing back:

- name the concrete risk;
- propose the safer alternative;
- keep the user's goal as the anchor;
- continue with the safe portion when possible.

## Task Claiming (SQLite)

As of TASK-014, task claims are coordinated through `MAP_System/map.db` using the atomic claim module at `MAP_System/db/claims.py`. Do not edit task JSON files directly to claim work.

**Claiming a task:**

```python
from MAP_System.db.claims import claim_task, heartbeat, submit_task, expire_leases

success = claim_task("TASK-NNN", "your-agent-id")   # returns False if already claimed
```

**While working** (renew every ~15 minutes to avoid lease expiration):

```python
heartbeat("TASK-NNN", "your-agent-id")
```

**When done:**

```bash
MAP_System/.venv/bin/python MAP_System/scripts/map_task.py submit TASK-NNN \
  --actor your-agent-id
```

This synchronized command verifies the current claimant, transitions SQLite to
`SUBMITTED`, appends the canonical `SUBMISSION` event, and exports the task and
graph mirrors. `MAP_System.db.claims.submit_task()` is the internal atomic
transition primitive; direct agent use is unsupported because it cannot
synchronize the event and file-backed state.

**Reconciliation** (run by the LangGraph runner or manually):

```python
expired = expire_leases()   # returns tasks back to READY when lease has passed
```

Update `workflow/task_graph.json` and the task's individual JSON file to reflect the new status after claiming or submitting, so the file-backed state stays synchronized with SQLite.

## Elastic Helper Agents

The command center keeps Codex and Claude as the two active core agents (see DEC-008). Core agents may start temporary helper agents when a task benefits from parallel research, review, implementation, or focused analysis.

**Spawning helpers:** use a command-center-managed terminal surface. Every LLM
agent and model-backed helper must remain visible while working. Always launch
hcom agents with `--terminal wezterm-tab` unless the operator explicitly
selects another visible terminal. Never use `--headless`, a hidden background
process, or any surface the operator cannot directly inspect and stop.

Deterministic non-model automation may run without a dedicated terminal only
when it is not represented as an agent and its status, last run, outputs,
errors, and stop control are visible in the Command Center operator surface.
If a deterministic watcher invokes a model for judgment, that model invocation
is agent work and must move to a visible terminal/session.

```bash
hcom 1 claude --tag helper-review-01 --terminal wezterm-tab
```

```bash
# Deliberate override for narrowly-scoped, low-friction work:
hcom 1 claude --tag helper-scan-01 --terminal wezterm-tab --model haiku
```

Claude helpers default to Sonnet with auto permission mode (DEC-035,
2026-07-28), superseding TASK-194's original Haiku default at the operator's
explicit instruction to remove permission-prompt babysitting. This is a
resource/attention-management default, not a capability ceiling. Haiku
remains available and is still the right choice for narrowly-scoped,
low-friction work — it is now a deliberate per-spawn override (`--model
haiku`), not the default, and choosing it needs no escalation. If a helper
needs Opus, the owning agent must first write a short escalation request with
the helper scope, why Sonnet is insufficient, the requested tier, and the
expected bounded use. A different core agent reviews that request and chooses
the lowest tier that can reasonably handle the work. Review should be
generous when the reasoning is sound: do not spend Opus on tasks Sonnet can
reliably perform, and do not force Sonnet onto work Haiku already handles
well. See `notes/helper-agent-guide.md` for the tier rubric, the request
format, and why the original Haiku-default friction traced to a missing
`--permission-mode auto` flag rather than a Haiku-specific restriction.

Helper agents are not permanent identities. Each helper must have:

- a stable helper tag like `helper-research-01` or `helper-review-ui`;
- a specific task, question, or review scope;
- a durable note in `MAP_System/inbox/helpers/` describing what it is doing and what it has already learned;
- an owner among the core agents who is accountable for integrating or discarding the helper's output.

Helpers should be stopped when their assigned work is done, stale, duplicated by another helper, or no longer relevant. Do not keep helpers running merely to keep agents busy. Do not allow helpers to bypass task ownership, approval gates, or human approval requirements.

### Helper-note metadata contract

The graph counts helper capacity from the durable note, not from terminal
presence. A manually created helper note must begin with plain bullet metadata
in this shape; display-only labels such as `**Status:** ACTIVE` are not parsed.

```md
# Helper Assignment - <bounded purpose>

- status: active
- owner: codex-lab-<owner>
- provider: codex | claude | local
- model: haiku | sonnet | opus | local-<tag>
- created_at: YYYY-MM-DD
- scope: one bounded question or task
```

`model` is the **approved** tier, not the requested one. `provider` says which
system ran the helper; it does not say how much model was spent, so it cannot
answer whether the tier rubric was followed. When the approved tier is Opus
(above the Sonnet default, DEC-035), also record the approver and the lower
tier that was considered and skipped — `notes/helper-agent-guide.md` requires
both, and this is where they go.

The graph reports any **active** helper note with no `model` line
(`helpers_missing_model_tier` in the runner output). A finished note is
historical evidence and is not reopened to backfill.

Basis: the tier rubric in `notes/helper-agent-guide.md` has always required the
approved tier to be recorded, but this contract had nowhere to put it. Measured
2026-07-22: 6 of 82 helper notes carried any tier, and 2 named a model at all,
so the rubric could not be checked even in principle (TASK-269).

`active`, `running`, and `in_progress` consume helper capacity. Set the first
field to a non-active final value such as `complete`, `stopped`, or `superseded`
when the assignment ends, while preserving the note as historical evidence.
The owner is responsible for this transition. Use the command-center helper
starter when available; when assigning an existing visible helper, copy this
block before sending the hcom assignment.

### Routine Reviewer Conflict Routing

If a submitted task needs review, the available reviewer has a no-self-review
conflict, and no clean core reviewer is immediately available, do not ask the
operator to solve the routing problem. Use the existing helper path:

1. Create a durable helper note in `MAP_System/inbox/helpers/`.
2. Spawn a visible temporary review helper with `--terminal wezterm-tab`.
3. Send a bounded review packet naming the task, output paths, conflict reason,
   and required review artifact.
4. Continue tracking the helper and integrate the result through the normal MAP
   review and release gates.

Escalate to the operator only if spawning a visible helper is blocked, the task
needs a human decision, or the review would cross a privacy, destructive-action,
security, or scope boundary.

## Broadcast Coordinator Convention

When an operator or command-center message goes to more than one core agent
at once (a broadcast, e.g. "what did the review find?" or "go fix these
findings"), duplicate ownership is a real risk: two agents can independently
audit the same thing, or both claim the same fix, without either being wrong
to try. This has worked so far only because agents happened to coordinate by
convention (TASK-140/141: claude-lab-vino and codex-lab-neko split a review
broadcast by announcing non-overlapping angles over hcom before starting).
That is not a gate, so it should not be assumed to keep working by luck.

Rule: the first core agent to start substantive work on a broadcast should,
before or immediately as it starts, send the other addressed agent(s) a short
hcom message naming the scope it is claiming (which findings, which files, or
which recommendation number) and inviting a swap if there is a conflict.
`--intent inform` is sufficient; do not block on a reply before starting, but
do stop and re-split if another agent objects or was already mid-work on the
same scope.

If the broadcast is large enough that a full split needs judgment (more than
a couple of independent pieces, or unclear boundaries), the first agent should
propose the split explicitly and wait briefly for the other(s) to confirm or
counter-propose, rather than each agent silently picking a lane. Record the
agreed split in the hcom thread; a durable task file or handoff note is only
required if the resulting work itself needs one under the normal Core
Protocol.

This is deliberately a convention, not new tooling: it targets exactly the
gap TASK-140 found (duplicate-owner risk on broadcasts) without adding a new
process file for something two agents can resolve by talking to each other
first.

## Broad Directive Intake Convention

Broad operator directives should enter MAP through the visible intake wrapper
before an agent decomposes them into tasks or lanes. Default path:

```bash
python3 MAP_System/scripts/command_center_intake.py \
  --hcom-inform-to @bigboss \
  --hcom-name <agent-hcom-name> \
  "operator directive text"
```

The wrapper classifies the directive, validates its own hcom-shaped summary,
optionally posts that summary as `hcom --intent inform`, records the intake
event, and prints the current runner route. This makes the dispatch packet
visible before decomposition without requiring a human approval step.

Urgent live-control messages are exempt: stop/pause/resume instructions,
approval prompts, safety/privacy/scope conflicts, and direct agent routing
messages may be handled immediately through hcom. If the urgent message later
turns into broad implementation work, run intake for the follow-on directive
before creating or splitting tasks.

## Autonomous Claim Loop

An autonomous task daemon is available at `MAP_System/scripts/agent_loop.py`. It claims, works, and submits tasks in a cyclic LangGraph loop without operator intervention for normal work. It pauses at `review` and `propose_helper` routes, requiring operator input before resuming.

```bash
MAP_System/.venv/bin/python MAP_System/scripts/agent_loop.py \
  --agent-id codex \
  --handler "python3 MAP_System/scripts/handle_task.py {task_id}" \
  --heartbeat-interval 300 \
  --lease-seconds 1800
```

Use `--once` for a single-cycle run. Use `--dry-run` to verify routing without claiming. The loop acquires a per-agent-id lockfile at startup and releases it on exit or SIGTERM.

## Agent Availability And Session Limits

Agent availability is durable project state. When an agent reaches a session limit, is waiting for approval, goes offline, or otherwise cannot work, record it in `MAP_System/agents/status.json`.

Other agents should continue with available work unless a task explicitly requires the unavailable agent. If work was owned by an unavailable agent, create a handoff or queue a note before another agent continues. Do not wait for an unavailable agent merely because it was previously participating.

Use `required_agent` in a task only when that exact agent is necessary. Otherwise, tasks should be transferable among available core agents or temporary helpers.

## Git Protocol

Normal root Git is available from the canonical repo:

```text
/home/home/Projects/MultiAgentProject
```

The canonical repo decision is recorded in `shared/canonical-repo.md` and
`shared/decisions.md` (DEC-014).

Remote:

```text
https://github.com/BigCatMellow/MultiAgentProject.git
```

Use normal Git or the compatibility wrapper:

```bash
git status
MAP_System/scripts/map-git status
```

The wrapper delegates to root Git and exists so older MAP instructions still
work.

See `notes/git-setup.md` for details.

## Communication

Be extremely concise. Sacrifice grammar for the sake of concision. Exception:
`## Documentation Style` above still requires complete sentences when
explaining risk, tradeoff, exception, conflict, or decision reasoning —
concision there must not come at the cost of ambiguity in reasoning other
agents act on.

Use MATOCP tokens for agent-to-agent messages (see `phatic-suppression.md`):

| Token | Meaning |
|---|---|
| `!ACK [id]` | Acknowledged, proceeding |
| `!LGTM` | Approved, no issues |
| `!ERR [code] reason="..."` | Failed, reason given |
| `!REQ key context="..."` | Need this before continuing |
| `!WARN [code] reason="..."` | Flag, not blocking |
| `!NOTE [text ≤200 chars]` | Anything that doesn't fit a token |

For longer structured events, prefer these types in `events/events.jsonl`:

- `PROGRESS`, `SUBMISSION`, `REVIEW_REQUESTED`, `CHANGES_REQUESTED`, `APPROVED`
- `QUESTION`, `ANSWER`, `BLOCKED`, `HANDOFF`
- `DECISION_PROPOSED`, `DECISION_RECORDED`

Use this compact event shape in `events/events.jsonl`:

```json
{"created_at":"2026-06-17T00:00:00-04:00","type":"PROGRESS","task_id":"TASK-001","sender":"codex","summary":"Short factual update","artifact_paths":[]}
```

## Handoff Format

Create a Markdown file in `handoffs/` named like:

```text
HANDOFF-TASK-001-codex-to-claude.md
```

Include:

- task ID
- sender
- intended recipient
- status
- files changed or created
- what needs review or continuation
- known limitations

## STATE_SNAPSHOT Resume Format

Use `STATE_SNAPSHOT` YAML when a session ends with active work, blocked work, or pending review state that the next agent should not re-derive from scratch. The schema and example live at `MAP_System/workflow/templates/state_snapshot.yaml`.

Emit snapshots in `MAP_System/handoffs/` with names like:

```text
STATE_SNAPSHOT-codex-20260619T104500.yaml
```

Before resuming a task, check `MAP_System/handoffs/` for the latest relevant `STATE_SNAPSHOT-*` file from the previous owner or reviewer. Load it as orientation only; SQLite task state, task files, decisions, and artifacts remain canonical.

### Verified Context Rotation

Do not wait for context exhaustion or clear a conversation without a verified
handoff. `scripts/context_rotation.py` implements the TASK-271 rotation gate.
The default rotation threshold is 150,000 current-context tokens; when a model
exposes its context window, the earlier proportional guard also applies:
checkpoint at 60% and rotate by 75%. Cumulative transcript traffic is not a
context estimate.

The local `scripts/limit_watcher.py` checks live-session context estimates on
each poll and sends transition-based `inform` notices at checkpoint and
rotation boundaries. It atomically records each successful notification before
unrelated recovery work can block the poll, preventing repeat spam. A notice
is advisory: it does not clear history, supersede an identity, or launch a
replacement.

At every AI Command Center Lab startup, continuity checks happen before task
routing. The agent must first determine its exact current hcom identity, then
run:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py validate
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py advise --agent <exact-current-hcom-identity>
```

The agent includes the continuity validation result and the exact
checkpoint/rotation recommendation in its single initial status/resume-plan
message to `@bigboss`; if there is no in-flight work, the same message requests
priorities. These startup commands only validate and advise. Startup must never
automatically clear history, prepare or finalize a rotation, supersede a
session, or use `advise --notify`.

Rotation order is mandatory:

1. Write a `STATE_SNAPSHOT` v2 draft with the exact live task claims, touched
   paths, decisions, failed approaches, blockers, summary, and next action.
2. Run `context_rotation.py prepare`. It freezes the snapshot and updates
   `shared/context-continuity.md` under a file lock with snapshot and canonical
   state hashes.
3. Start the replacement through a visible command-center terminal. Never use
   a headless replacement.
4. The replacement reads the exact snapshot and runs `context_rotation.py ack`
   with its SHA-256. ACK binds the supplied replacement session ID to the live
   hcom roster. Any snapshot, master-ledger, task, touched-path, identity, or
   session drift blocks acknowledgement.
5. Only after ACK may the old session run `context_rotation.py finalize`. That
   transfers its recorded live claims, exports mirrors, marks the old identity
   `inactive/session_superseded`, and commits the ledger. Export or final
   ledger-write failure rolls back the transfer so the old session remains
   recoverable. Finalize first rechecks the acknowledged replacement identity
   and session are still live.

Raw transcripts and snapshots are never deleted. A `/clear`, fresh session,
or old-session shutdown before the checksum-bound ACK is a protocol violation.
See `notes/context-rotation-guide.md`.

Replacement sessions spawned via `hcom ... --terminal wezterm-tab` inherit
`CLAUDE_CODE_CHILD_SESSION=1`, which by default excludes them from
`--resume`, `--continue`, up-arrow history, and the `claude agents` list, and
affects their transcript persistence. This is handled globally, not per
rotation: `~/.claude/settings.json` sets `CLAUDE_CODE_FORCE_SESSION_PERSISTENCE:
"1"` in its `env` block and `cleanupPeriodDays: 36500` at the top level, so
every session (including rotation replacements) persists its transcript from
the start. No manual step is needed at rotation time.

## File Ownership

Task files list `output_paths`. Treat those as owned by the task while it is active. If ownership needs to change, create a handoff and update the task status.

## Review Standard

Review findings should be concrete and actionable. Use severities:

- `BLOCKER`
- `REQUIRED`
- `RECOMMENDED`
- `OPTIONAL`

Only `BLOCKER` and `REQUIRED` findings should block approval.

### Security Second Pass

Any task whose outputs add a network-facing or write-capable component — a
server, listener, endpoint, or anything that can write into the agent bus,
filesystem beyond its own artifacts, or an external service — requires a
second, explicitly security-framed review pass before approval, separate
from the functional review.

The security pass checks trust boundaries specifically: authentication,
CSRF/drive-by exposure, injection, path traversal, identity attribution,
and failure modes on malformed input.

Skip it for purely static, read-only, or documentation work.

Basis: TASK-056's functional review approved a working, input-validated
backend but missed a real CSRF gap that a security-framed second pass then
caught (INS-0004 / IDEA-0004 / PROMO-0004, promoted by TASK-078).
