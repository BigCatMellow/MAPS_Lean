# Control-Plane Setup: SQLite, LangGraph, hcom, and RnS

Use this guide to install and rebuild the retained MAPS control plane on a fresh
machine or clone.

This is an implementation guide, not an authority document. The responsibility
boundaries remain defined by [CONTROL_PLANE.md](../playbook/CONTROL_PLANE.md).

## Important migration rule

MAPS Lean now contains a curated copy of the proven legacy runtime under:

```text
migration/legacy-runtime-source/
```

That directory is **migration source, not active runtime**. Do not import from
it in production code. It exists so `legacy/` can be removed without losing the
implementation and tests needed to rebuild Lean correctly.

Before replacing a retained subsystem from scratch:

```text
inspect extracted source
→ identify the behavior/invariant it protected
→ implement the smallest Lean version
→ port the relevant test
→ verify against disposable state
```

See [Legacy Runtime Extraction](../migration/LEGACY_RUNTIME_EXTRACTION.md).

## Target layout

```text
MAPS_Lean/
├── runtime/
│   ├── state/
│   ├── routing/
│   ├── policy/
│   ├── communication/
│   ├── recovery/
│   └── helpers/
├── tests/
├── .maps/
│   └── state/
│       ├── maps.db
│       └── langgraph-checkpoints.db
└── .hcom/
```

Keep each mutable store separate:

- `.maps/state/maps.db` — MAPS task truth: tasks, ownership, claims, leases,
  submission authorship, reviews, release/approval records, and task events.
- `.maps/state/langgraph-checkpoints.db` — LangGraph execution/checkpoint memory.
- `.hcom/` — hcom message/session/hook/transport state.

**Do not combine these databases.** Legacy used LangGraph checkpoint tables in
`map.db`; Lean intentionally separates them. hcom's own SQLite state must never
become project/task authority.

## 1. Prerequisites

Recommended local setup:

- Git
- Python 3.10+
- Python virtual environments
- SQLite Python binding (`sqlite3`, normally included with CPython)
- Claude Code and/or Codex CLI if those workers will be launched through hcom
- optional Ollama/Aider when local helper lanes are wanted
- `uv` if available; ordinary `pip` also works

From the repository root:

```bash
mkdir -p .maps/state
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell use `.venv\Scripts\Activate.ps1`.

## 2. SQLite

### Install / verify

Python verification:

```bash
python - <<'PY'
import sqlite3
print("SQLite:", sqlite3.sqlite_version)
PY
```

The CLI is useful but not required by the Python runtime. On Debian/Ubuntu/Linux
Mint:

```bash
sudo apt update
sudo apt install sqlite3
sqlite3 --version
```

### Connection defaults

Each task-ledger connection should use:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
```

Keep the live DB on a local filesystem when relying on WAL for multi-process
coordination.

### Do not start from the old "minimal schema"

The legacy runtime already proved that several lifecycle facts matter:

- task dependencies and output paths;
- acceptance criteria;
- durable owner vs current claimant;
- claim lease + heartbeat + attempts;
- submission authorship independent from owner;
- independent review records/findings;
- release records;
- approval gates;
- agent lifecycle state;
- events.

The preserved source is:

```text
migration/legacy-runtime-source/migration/schema.sql
migration/legacy-runtime-source/db/claims.py
migration/legacy-runtime-source/db/review_authorship.py
migration/legacy-runtime-source/db/authority.py
```

Use that as the behavioral baseline. Simplify fields only when a ported test
shows the removed concept is no longer required.

### Lean-specific changes required

Do not copy the old state layer unchanged. Resolve these differences first:

1. Lean task lifecycle names currently use:

   ```text
   NEEDS_SHAPING → READY → ACTIVE → READY_FOR_REVIEW → DONE
                              ↘ BLOCKED
                        ↖ CHANGES_REQUESTED
   ```

   Legacy code uses states such as `IN_PROGRESS`, `SUBMITTED`, `APPROVED`, and
   `RELEASED`. Pick one runtime vocabulary and make every transition/test agree.

2. A consequential task MUST pass the AGI readiness gate before entering
   `READY`.

3. Submission authorship MUST remain separate from durable owner so owner
   reassignment cannot defeat no-self-review.

4. Output paths remain prospective write boundaries, not an after-the-fact
   report of changed files.

### Required state API

Put task-ledger access behind `runtime/state/`. Expose semantic operations, not
arbitrary SQL spread across the system. At minimum:

```text
create_task(...)
get_task(task_id)
validate_ready(task_id)
claim_task(task_id, worker_id)
heartbeat(task_id, worker_id)
submit_task(task_id, worker_id, evidence)
claim_review(task_id, reviewer_id)
record_review(task_id, reviewer_id, verdict)
request_changes(task_id, ...)
complete_task(task_id, ...)
release_or_approve(...)
recover_expired_claim(...)
append_event(...)
```

Every mutation must check expected state/authority and return explicit
success/failure.

### Atomic claim invariant

Do not implement claim as `SELECT` followed by an unconditional `UPDATE`.
The claim mutation itself must be guarded, so concurrent workers cannot both
succeed.

The extracted `db/claims.py` contains the prior guarded-update behavior and
lease recovery logic. Port its invariant, then test a two-worker race.

Required result:

```text
exactly one claim succeeds
loser re-reads current task state
loser never force-overwrites ownership
```

## 3. LangGraph

### Install

Inside `.venv`:

```bash
python -m pip install -U langgraph langgraph-checkpoint-sqlite
```

Or:

```bash
uv pip install langgraph langgraph-checkpoint-sqlite
```

For current `langgraph-checkpoint-sqlite`, keep strict MessagePack loading unless
a reviewed compatibility reason requires otherwise:

```bash
export LANGGRAPH_STRICT_MSGPACK=true
```

### Smoke test

```bash
python - <<'PY'
from pathlib import Path
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

Path('.maps/state').mkdir(parents=True, exist_ok=True)

class State(TypedDict):
    route: str

def dispatch(state: State):
    return {"route": "wait_or_reconcile"}

builder = StateGraph(State)
builder.add_node("dispatch", dispatch)
builder.add_edge(START, "dispatch")
builder.add_edge("dispatch", END)

with SqliteSaver.from_conn_string('.maps/state/langgraph-checkpoints.db') as cp:
    graph = builder.compile(checkpointer=cp)
    result = graph.invoke(
        {"route": ""},
        {"configurable": {"thread_id": "maps-smoke-test"}},
    )
    print(result)
PY
```

Expected: `route == wait_or_reconcile` and a dedicated checkpoint DB exists.

### Migration source

Preserved routing source:

```text
migration/legacy-runtime-source/graph/runner.py
migration/legacy-runtime-source/graph/graph.py
migration/legacy-runtime-source/workflow/runtime_policy.yaml
migration/legacy-runtime-source/workflow/role_registry.yaml
migration/legacy-runtime-source/scripts/pre_dispatch_policy.py
migration/legacy-runtime-source/scripts/halt_state.py
```

The old runner grew large and accumulated fixed-role/context-history concerns.
Do not port it line-for-line. Preserve the useful route contract:

```text
review
wait_for_agent
propose_helper
claim_or_assign
policy_gate
wait_or_reconcile
```

Input should be a read-only snapshot of:

```text
task/dependency state
AGI readiness
risk/policy gates
worker capability/availability
review requirement
approval requirement
helper capacity
halt state
```

LangGraph recommends a route. A guarded MAPS operation performs any mutation.

### Checkpoint migration

Legacy `db/checkpointer.py` placed custom LangGraph checkpoint tables in the
same `map.db` as task truth. Keep it only as compatibility/reference evidence.
For Lean use the official SQLite saver against:

```text
.maps/state/langgraph-checkpoints.db
```

## 4. hcom

hcom is the cross-provider communication and session-control transport used by
the existing recovery design.

### Install

Preferred when `uv` is available:

```bash
uv tool install hcom
```

Python alternative:

```bash
python3 -m venv "$HOME/.local/share/hcom-venv"
"$HOME/.local/share/hcom-venv/bin/python" -m pip install -U hcom
mkdir -p "$HOME/.local/bin"
ln -sf "$HOME/.local/share/hcom-venv/bin/hcom" "$HOME/.local/bin/hcom"
```

The old installer used this separate user-local venv pattern. It avoids mixing
hcom with the project runtime environment.

Verify:

```bash
hcom --version
hcom status
```

### Isolate hcom per project

From the clone root:

```bash
export HCOM_DIR="$PWD/.hcom"
hcom status
```

Use the same `HCOM_DIR` for all hcom commands for this clone.

### Claude and Codex

With `HCOM_DIR` set:

```bash
hcom claude
```

In another terminal:

```bash
export HCOM_DIR="$PWD/.hcom"
hcom codex
```

Verify:

```bash
hcom list
```

### MAPS adapter boundary

Put hcom access behind:

```text
runtime/communication/hcom_adapter.py
```

Expected operations:

```text
send(...)
list_sessions()
session_status(...)
spawn(...)
resume(...)
stop(...)
read_bounded_events_or_transcript(...)
```

hcom may supply transport/session facts. It MUST NOT decide:

- MAPS task ownership;
- task completion;
- review verdict;
- scope changes;
- operator approval;
- destructive-action authority.

Legacy communication notes explicitly treated hcom message intent/history as
hcom-owned transport data, not MAP canonical state. Preserve that boundary.

## 5. RnS / recovery

Preserved recovery source:

```text
migration/legacy-runtime-source/scripts/limit_watcher.py
migration/legacy-runtime-source/scripts/liveness_reaper.py
migration/legacy-runtime-source/scripts/durable_execution.py
migration/legacy-runtime-source/scripts/resilience_controls.py
migration/legacy-runtime-source/scripts/dead_letter_queue.py
migration/legacy-runtime-source/scripts/agent_loop.py
```

Keep these behaviors:

- detect explicit provider-reset times when available;
- detect stale/stopped sessions when no final handoff turn occurs;
- capped retry/backoff rather than resume spam;
- durable incident/recovery state;
- terminal/superseded sessions are not resurrected;
- expired task claims recover without stealing live work;
- RnS does not invent, claim, or reassign tasks.

Remove the old hard dependency on:

```text
hcom r <name> --terminal wezterm-tab --go
```

Replace terminal choice with an adapter. The recovery contract is:

```text
session identified
→ recovery condition true
→ durable handoff/task state checked
→ adapter resume/nudge
→ verify liveness
→ backoff or close incident
```

WezTerm is presentation, not recovery authority.

## 6. Local model / Aider helpers

Legacy already contains useful bounded helper wrappers:

```text
migration/legacy-runtime-source/scripts/local_runner.py
migration/legacy-runtime-source/scripts/local_assistant_health.py
migration/legacy-runtime-source/scripts/aider_wrapper.py
```

Retain the ideas, adapt the task format:

- explicit model/tool;
- explicit task/scope;
- explicit output path(s);
- health check before local execution;
- Aider target files must fit declared write boundaries;
- dirty target files block automatic launch;
- helper result is recorded durably;
- helper never owns final completion/review/architecture decisions.

HPOM/model-capability routing should decide whether a specific local model is
fit for a task. Do not hard-code the old approved model list as eternal truth.

## 7. Installer design

Preserved source:

```text
migration/legacy-runtime-source/install/install-map-system.sh
migration/legacy-runtime-source/docs/fresh-install.md
```

Keep:

- dry-run as the safe/default preview path;
- user-local installation;
- backup before overwrite;
- dynamic repo path rather than hard-coded machine path;
- separate hcom environment;
- post-install command checks;
- no credential/API-key automation.

Do not carry forward as requirements:

- WezTerm installation;
- fixed startup roster;
- Agent Deck / terminal cockpit;
- bundled CommandCenterUI installation;
- mandatory desktop launchers.

A future Lean installer should install only selected runtime dependencies and
print missing optional workers/tools.

## 8. Fresh-clone implementation order

Use this order:

```text
1. Python environment
2. SQLite task store + migrations
3. port lifecycle tests
4. AGI READY gate
5. hcom install + project isolation
6. hcom adapter
7. LangGraph + dedicated checkpoint DB
8. routing/policy adapter
9. RnS recovery adapter
10. local helper adapters as needed
11. fresh-clone smoke suite
```

Do not wire automated dispatch before the SQLite state/gates pass their tests.

## 9. Required behavioral verification

Before calling the Lean control plane usable:

```text
[ ] SQLite opens with FK + WAL + busy timeout
[ ] concurrent claim race has exactly one winner
[ ] expired lease recovers without stealing live work
[ ] AGI FAIL cannot transition to READY
[ ] submission author cannot review own substantive work
[ ] output-path/write-boundary conflict is rejected
[ ] review/release gates require expected evidence
[ ] LangGraph uses separate checkpoint DB
[ ] router recommendation does not mutate task truth
[ ] hcom project state is isolated with HCOM_DIR
[ ] hcom session state never grants task authority
[ ] RnS resumes/nudges without mandatory WezTerm
[ ] RnS does not revive terminal/superseded sessions
[ ] local helper cannot widen scope or self-approve
[ ] Aider wrapper blocks out-of-scope target files
[ ] fresh install works without reading legacy/
```

The focused old tests preserved under
`migration/legacy-runtime-source/tests/` are migration evidence. Port them into
the active `tests/` suite as each subsystem is implemented.

## 10. Local-state ignore rules

Normally keep these out of Git:

```gitignore
/.venv/
/.maps/state/
/.hcom/
```

Tracked Markdown remains the durable human-readable project record.

## 11. Troubleshooting

### hcom

```bash
hcom status
hcom update
hcom list
```

Do not use an hcom reset as a repair for MAPS task truth.

### LangGraph

```bash
python - <<'PY'
import importlib.metadata as md
for pkg in ('langgraph', 'langgraph-checkpoint-sqlite'):
    print(pkg, md.version(pkg))
PY
```

### SQLite

```bash
sqlite3 .maps/state/maps.db '.tables'
sqlite3 .maps/state/maps.db 'PRAGMA journal_mode;'
sqlite3 .maps/state/maps.db 'PRAGMA foreign_keys;'
sqlite3 .maps/state/maps.db 'PRAGMA integrity_check;'
```

A failed claim may be correct contention behavior; re-read state before treating
it as a DB failure.

## 12. External source references

The public dependency commands in this guide were last checked on 2026-08-14.
Re-verify before changing installer pins or supported command syntax.

- hcom: `https://github.com/aannoo/hcom`
- LangGraph: `https://docs.langchain.com/oss/python/langgraph/overview`
- LangGraph persistence: `https://docs.langchain.com/oss/python/langgraph/persistence`
- SQLite: `https://www.sqlite.org/`
