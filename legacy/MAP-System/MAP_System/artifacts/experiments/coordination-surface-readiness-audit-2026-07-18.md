# Coordination-Surface Readiness Audit

**Date:** 2026-07-18  
**Scope:** Evidence and task-shape recommendation only. This audit changes no Command Center source, task record, agent status, or policy.

## Conclusion

The existing Command Center has the needed source systems, but no per-agent coordination read model. A future task is ready only if it reads SQLite directly for claims, preserves live-versus-durable disagreement, and labels every attention reason with its source. It must not merge these signals into a single inferred agent status.

## Field authority and conflict contract

| Proposed field | Observation | Evidence | Implication / freshness and conflict behavior |
|---|---|---|---|
| Durable agent status | `agents/status.json` records the durable board; live hcom is explicitly a separate authority. | `MAP_System/agents/README.md:8-10,38-49`; `MAP_System/templates/install/command-center-ui/app/server.py:72,1947-1951`; current board entries in `MAP_System/agents/status.json`. | **Authoritative only for the durable field.** Show `status`, `reason`, and `resume_after` verbatim plus the file-level read/capture age. The entry has no per-agent update timestamp, so its per-agent freshness is unknown. If hcom presence disagrees, show both values and `conflict/unknown`; do not infer capacity, availability, or a replacement durable value. |
| Active claim | Claims are atomically written to the canonical SQLite `tasks` table with `claimed_by`, `lease_expires_at`, and `heartbeat_at`. | `MAP_System/migration/schema.sql:17-35`; `MAP_System/db/claims.py:122-155,173-194`; `MAP_System/db/README.md:11-15`; `MAP_System/notes/orchestration-notes.md:80-84`. | **`MAP_System/map.db`, read-only, is authoritative.** A claim is active only when task status is `IN_PROGRESS`, `claimed_by` is set, and the lease is not expired at read time. Task JSON/graph mirrors are content mirrors, not claim liveness. An expired or malformed lease is an attention reason, not an active claim. SQLite read time and lease expiry are the freshness evidence. |
| Latest meaningful action | The plan defines this field as the latest event line for the sender; the current backend reads the append-only event log in file order without an agent-level synthesis. | `MAP_System/notes/system-improvement-implementation-plan.md:67-76`; `MAP_System/templates/install/command-center-ui/app/server.py:233-244`; event examples with interleaved timestamps at `MAP_System/events/events.jsonl:1901-1907`. | **The latest valid, action-bearing MAP event for that sender is the source, with its `created_at` and line/order retained.** It is not proof that the agent is live, still owns a claim, or that the action completed. A parse error, missing timestamp, or ambiguous action is `unknown`, not silently replaced by hcom chat activity. File order alone is not chronological evidence because current rows can be interleaved by timestamp. |
| Needs attention | The existing UI already separately derives unanswered operator requests, pending approval gates, and fresh blocked terminals; stale claims and reviewable submissions are available from SQLite but are not in that UI inbox. | `MAP_System/templates/install/command-center-ui/app/server.py:906-951,1705-1744`; `MAP_System/templates/install/command-center-ui/src/chat.js:1366-1450`; `MAP_System/scripts/limit_watcher.py:494-519,524-549`; `MAP_System/tasks/TASK-227.json:6-8`. | **No single source is authoritative.** Render a source-labelled set of reasons: unanswered live agent request (hcom), pending approval gate (SQLite), fresh blocked terminal (hcom), expired claim (SQLite), and pending review (`SUBMITTED` task in SQLite). A historical `BLOCKED` event alone is not an unresolved blocker because the event log has no closure relation; it may be displayed as history, never as a current attention fact without current-state evidence. |

## What the present Command Center shows

### Observation

The main active UI is `src/chat.html`, not the older `src/app.html` dashboard (`README.md:45-53`). It shows a hcom-derived “In the room” presence list, task-queue aggregate counts, recent conversation, and a “Needs you” inbox for requests, approvals, and blocked terminals.

### Evidence

- Presence comes from `/api/presence`; the backend prefers process-bound `hcom list --json` and falls back to hcom's SQLite only when the command is unavailable (`app/server.py:734-760,1282-1367`). The UI polls it every eight seconds (`src/chat.js:641-652,1693-1706`) and renders name, live status, model, tag, and a terminal-view action (`src/chat.js:831-885`).
- The task block shows only queue counts from `workflow/task_graph.json`, not claim-level data (`app/server.py:254-266`; `src/chat.js:909-932`).
- The current attention inbox is limited to unanswered live-agent requests, pending approval gates, and fresh blocked terminals (`app/server.py:906-951,1705-1744`; `src/chat.js:1414-1450`).

### Implication

The unanswered operator question is: **for each live core agent or live helper, what durable state, owned work, latest durable action, and actionable exception should the operator trust now—and which of those answers conflict?** Today the operator must join multiple panels, raw hcom, event history, and SQLite/file state manually. A green/listening presence dot cannot answer that question.

## Required staged mixed-state fixtures

These are deterministic read-model fixtures, not changes to production state. Each assertion must retain source labels and timestamps/ages in the rendered data; a screenshot alone is insufficient.

1. **Stale durable status — essential.** Fixture one agent as hcom `listening`/process-bound while its durable board entry is `standby`/`out_of_tokens` with an already-passed `resume_after`. Expect both fields and their sources, a visible `conflict/unknown` result, and no claim that provider capacity is known. This is grounded in the documented live/durable distinction (`agents/README.md:8-10`).
2. **Live action newer than durable state — essential.** Provide a durable board snapshot file mtime of `T0`, then a valid sender event at `T1 > T0` plus a live hcom presence snapshot. Expect the last action to show its event timestamp and the durable status to show only whole-file age; the card must state that per-agent durable freshness is unknown. This verifies that a newer action does not overwrite or “freshen” a durable field.
3. **Expired claim — essential.** Fixture an `IN_PROGRESS` task with `claimed_by` set and `lease_expires_at < read time`. Expect `no active claim` plus an `expired claim` attention reason identifying the task and claimant. It must not report the lease as owned in-progress work. This is the same predicate used by the existing watcher (`scripts/limit_watcher.py:537-547`). A follow-on fixture for a `SUBMITTED` task may verify the separate pending-review reason.

## Smallest independently implementable task shape

**Scope:** One medium-risk, read-only coordination card for live core agents and currently running helpers, plus the `status.json` reader/writer contract that keeps the card's durable field honest. It adds no state store, no claim mutation, no status mutation, and no authority/policy change. This keeps the TASK-227 plan's 1a/1b shape (`system-improvement-implementation-plan.md:67-80`) while satisfying review finding C1 (`task227-review-lilo.md:45`).

**Exact output paths:**

- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/templates/install/command-center-ui/src/chat.html`
- `MAP_System/templates/install/command-center-ui/src/chat.js`
- `MAP_System/templates/install/command-center-ui/src/chat.css`
- `MAP_System/agents/README.md`
- `MAP_System/tests/test_coordination_surface.py`
- `MAP_System/scripts/run_tests.sh` (the suite invokes named tests explicitly; see lines 10-20 and 28-94).

### Concise acceptance checks

1. A read-only endpoint/card emits, per in-scope agent, source-labelled durable status, active-claim result, latest action, and zero or more attention reasons; each result includes the evidence time/age available from its source.
2. Claims come directly from `MAP_System/map.db` in read-only mode; the task graph/task JSON never decides claim liveness.
3. All three staged fixtures above pass as deterministic tests, and the first fixture visibly renders disagreement rather than a synthesized status.
4. A manual screenshot of the staged mixed state demonstrates that an operator can distinguish live presence, durable state, owned work, and attention without opening repository files.
5. `agents/README.md` states durable-board authority, live-hcom authority, file-level versus per-agent freshness limits, and the conflict/unknown rendering rule. It does not add a new governance rule.

## Recommendation classification

- **Essential:** the field contract, direct read-only SQLite claim query, source-labelled multi-reason attention, all three fixtures, and the `status.json` contract text. Without them the surface repeats the exact stale-state risk identified in the TASK-227 review.
- **Likely:** use `agents/status.json` file mtime as a clearly labelled, coarse durable-board freshness indicator. It uses existing metadata but must never be presented as an individual agent update time.
- **Optional:** terminal-link affordances and per-card visual polish. Existing presence cards already provide a terminal-view action; neither is needed to establish source authority.
- **Investigate:** whether future durable entries need per-agent `updated_at`. The current schema/documented board does not provide it. Do not add it in this task or infer it from unrelated activity; first measure whether the coarse file-level age prevents recovery decisions in practice.

## Established facts vs. unverified assumptions

**Established:** `map.db` is canonical for live claim/lease questions; hcom is the live-presence authority; `status.json` is the durable board; the event log is append-only and current UI source reads preserve its file order; and the current attention UI does not include expired claims or pending reviews.

**Unverified:** whether every meaningful action is emitted to `events/events.jsonl`; whether an event's `created_at` is always a trustworthy wall-clock order under concurrent writes; whether a file-level durable-board age is useful enough for operators; and the exact installed CommandCenterUI checkout's parity with this installer template. The proposed task should test the read model against fixtures, not assume these properties.
