# Control-Plane Setup: SQLite, LangGraph, and hcom

Use this guide to install and wire the retained MAPS control-plane components on
a fresh machine or clone.

This is an implementation guide, not an authority document. The responsibility
boundaries remain defined by [CONTROL_PLANE.md](../playbook/CONTROL_PLANE.md).

## Target layout

Keep each system's mutable state separate:

```text
MAPS_Lean/
├── runtime/
│   ├── state/
│   │   └── sqlite_store.py
│   ├── routing/
│   │   └── langgraph_router.py
│   └── communication/
│       └── hcom_adapter.py
├── .maps/
│   └── state/
│       ├── maps.db
│       └── langgraph-checkpoints.db
└── .hcom/
```

The three stores have different jobs:

- `.maps/state/maps.db` — MAPS task truth: task state, claims, leases,
  submissions, reviews, and task events.
- `.maps/state/langgraph-checkpoints.db` — LangGraph execution/checkpoint state.
- `.hcom/` — hcom communication, session, hook, and transport state.

**Do not combine these databases.** MAPS must not query hcom's internal database
as project authority, and LangGraph checkpoint tables must not become the task
ledger.

## 1. Prerequisites

Recommended local setup:

- Git
- Python 3.10+
- a Python virtual environment
- Claude Code and/or Codex CLI if those workers will be launched through hcom
- `uv` if available; ordinary `pip` also works for the Python packages

Create local state and a Python environment from the repository root:

```bash
mkdir -p .maps/state
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell, activate the environment with the corresponding
`.venv\Scripts\Activate.ps1` command.

## 2. SQLite: install and verify

### What MAPS uses SQLite for

SQLite is the canonical mutable task ledger. Markdown remains the readable
project brief, roadmap, decisions, handoffs, and evidence.

Python already includes the `sqlite3` module in normal CPython builds, so MAPS
does not need a separate Python database package just to use SQLite.

Verify the Python binding:

```bash
python - <<'PY'
import sqlite3
print("SQLite:", sqlite3.sqlite_version)
PY
```

The `sqlite3` command-line program is useful for manual inspection but is not
required by the Python runtime. On Debian/Ubuntu/Linux Mint it is normally
installed with:

```bash
sudo apt update
sudo apt install sqlite3
sqlite3 --version
```

SQLite also publishes prebuilt CLI binaries on its official download page.

### Connection defaults for MAPS

For each MAPS task-ledger connection:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
```

Why:

- `foreign_keys=ON` makes declared relationships actually enforceable on that
  connection.
- WAL allows readers and a writer to make progress concurrently on a local
  filesystem.
- `busy_timeout` gives short lock conflicts a chance to clear instead of
  immediately failing.

Do not put the SQLite database on a network filesystem when relying on WAL for
multi-process coordination. Keep it on the same host as the MAPS runtime.

### Minimal starter schema

The first runtime version should stay small. A sufficient starting point is:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN (
        'NEEDS_SHAPING',
        'READY',
        'ACTIVE',
        'READY_FOR_REVIEW',
        'CHANGES_REQUESTED',
        'BLOCKED',
        'DONE'
    )),
    risk TEXT NOT NULL CHECK (risk IN ('LOW', 'MEDIUM', 'HIGH')),
    owner TEXT,
    lease_until TEXT,
    submitted_by TEXT,
    reviewer TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    event_type TEXT NOT NULL,
    actor TEXT,
    detail TEXT,
    created_at TEXT NOT NULL
);
```

Add tables only when a real lifecycle rule needs them. Do not rebuild the whole
historical MAP schema before the lean runtime proves the smaller contract.

### Atomic claim pattern

Task claiming must be a guarded database operation, not a read-then-write race.
A simple pattern is:

```sql
BEGIN IMMEDIATE;

UPDATE tasks
SET status = 'ACTIVE',
    owner = :agent_id,
    lease_until = :lease_until,
    updated_at = :now
WHERE id = :task_id
  AND status = 'READY'
  AND owner IS NULL;

SELECT changes();
COMMIT;
```

Interpret the result as:

- `changes() == 1` — claim succeeded;
- `changes() == 0` — claim failed; re-read current task state and do not force
  ownership.

`BEGIN IMMEDIATE` starts the write transaction up front. SQLite permits many
readers but only one simultaneous writer, so callers must handle `SQLITE_BUSY`
by using the configured timeout and then retrying/reconciling rather than
pretending the claim succeeded.

### Required SQLite wrapper

Put task-ledger access behind one module such as:

```text
runtime/state/sqlite_store.py
```

Expose semantic operations rather than arbitrary SQL throughout MAPS:

```text
get_task(task_id)
create_task(...)
claim_task(task_id, agent_id, lease_until)
renew_lease(task_id, agent_id, lease_until)
submit_task(task_id, agent_id, evidence_ref)
record_review(task_id, reviewer, verdict)
transition_task(task_id, expected_state, new_state, actor)
append_event(...)
```

Every state-changing operation must validate the expected current state and
return an explicit success/failure result.

## 3. LangGraph: install and verify

### Install

Inside `.venv`:

```bash
python -m pip install -U langgraph langgraph-checkpoint-sqlite
```

With `uv`:

```bash
uv pip install langgraph langgraph-checkpoint-sqlite
```

The SQLite checkpointer is a separate package; installing `langgraph` alone is
not enough for `from langgraph.checkpoint.sqlite import SqliteSaver`.

For current `langgraph-checkpoint-sqlite`, use strict MessagePack loading unless
there is a reviewed reason not to:

```bash
export LANGGRAPH_STRICT_MSGPACK=true
```

### Smoke test

This confirms that LangGraph and its SQLite checkpointer both work and that the
checkpoint database can be created:

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

Expected result: a dictionary whose `route` is `wait_or_reconcile`, plus a new
`.maps/state/langgraph-checkpoints.db` file.

The synchronous `SqliteSaver` is intended for lightweight synchronous use. If
MAPS later runs an async LangGraph path, use `AsyncSqliteSaver` rather than
calling async graph methods through the synchronous saver.

### How MAPS should use LangGraph

Put the router behind:

```text
runtime/routing/langgraph_router.py
```

Its input should be a read-only snapshot of project/task conditions such as:

```text
task state
dependencies
risk/policy gates
available workers
review requirement
approval requirement
helper capacity
```

Its output should be a bounded operational route, for example:

```text
review
wait_for_agent
propose_helper
claim_or_assign
policy_gate
wait_or_reconcile
```

LangGraph must not:

- invent product scope;
- change operator priorities;
- approve destructive or consequential actions;
- directly overwrite MAPS task truth as a side effect of merely choosing a
  route.

The graph recommends the next route. A MAPS operation then performs the guarded
SQLite transition.

## 4. hcom: install and verify

hcom is a standalone communication/session-control CLI. It supports Claude
Code, Codex, and other coding-agent CLIs. It has no required background service.

### Preferred install on this project

If `uv` is available:

```bash
uv tool install hcom
```

Official alternatives include:

```bash
# macOS/Linux/Termux/WSL installer
curl -fsSL https://github.com/aannoo/hcom/releases/latest/download/hcom-installer.sh | sh

# ordinary Python install
pip install hcom
```

On macOS with Homebrew:

```bash
brew install aannoo/hcom/hcom
```

On native Windows PowerShell, hcom publishes a release installer script. See
its official README before running the current command.

Verify:

```bash
hcom status
```

### Isolate hcom per MAPS project

Before the first project-local hcom launch:

```bash
export HCOM_DIR="$PWD/.hcom"
hcom status
```

Use the same `HCOM_DIR` for every hcom command for this clone. This prevents one
project's hcom sessions/hooks/state from becoming another project's transport
state.

### Launch Claude and Codex through hcom

From the repository root with `HCOM_DIR` set:

```bash
hcom claude
```

In another terminal:

```bash
export HCOM_DIR="$PWD/.hcom"
hcom codex
```

Then verify hcom can see them:

```bash
hcom list
```

Open the hcom dashboard with:

```bash
hcom
```

Basic direct messaging is available through `hcom send`; use `hcom <command>
--help` for current flags rather than hard-coding undocumented arguments into
MAPS.

### How MAPS should use hcom

Put hcom access behind:

```text
runtime/communication/hcom_adapter.py
```

Expose a small MAPS-facing contract such as:

```text
send(target, message)
list_sessions()
status(session)
spawn(worker_type, ...)
resume(session)
stop(session)
```

hcom may provide:

- cross-provider messages;
- agent/session identity;
- liveness/status information;
- resume/nudge operations used by RnS;
- bounded transcript/event access when needed for recovery.

hcom must not decide:

- who owns a MAPS task;
- whether a task is DONE;
- whether a review passes;
- whether scope may change;
- whether a destructive action is authorized.

Those remain MAPS/operator decisions backed by the task ledger and durable
records.

If remote-device relay features are later enabled, treat device enrollment as a
high-trust security boundary. Do not enable it merely to make local setup work.

## 5. Wire the components together

The intended call path is:

```text
Markdown project/task record
          │
          ▼
     MAPS runtime
          │
     reads task truth
          ▼
       SQLite
          │
          ▼
   LangGraph router
          │
    recommends route
          ▼
 MAPS guarded operation
     │            │
     │            └── updates SQLite only if valid
     ▼
   hcom adapter
     │
     └── message / spawn / resume the selected worker
```

For example, assigning a READY task should look conceptually like:

```text
1. Read task + AGI readiness.
2. Read current SQLite state.
3. Ask router for next operational route.
4. If route is claim_or_assign, atomically claim in SQLite.
5. Only after claim succeeds, send/launch the owner through hcom.
6. Worker executes the durable task contract.
7. Submission updates SQLite.
8. Router sees READY_FOR_REVIEW and selects review.
9. Independent reviewer verifies evidence.
10. Guarded review transition marks DONE only after required proof passes.
```

Do not send a worker an implementation assignment first and try to repair task
ownership afterward.

## 6. Local-state ignore rules

These paths are machine/runtime state and should normally stay out of Git:

```gitignore
/.venv/
/.maps/state/
/.hcom/
```

Tracked Markdown remains the durable human-readable project record.

## 7. Fresh-clone verification checklist

A fresh machine is ready for control-plane implementation only when all of these
pass:

```text
[ ] python can import sqlite3
[ ] MAPS can create/open .maps/state/maps.db
[ ] a guarded claim race has exactly one winner
[ ] langgraph imports successfully
[ ] langgraph-checkpoint-sqlite imports successfully
[ ] LangGraph smoke test creates/resumes a checkpoint thread
[ ] hcom status succeeds
[ ] HCOM_DIR is isolated to this repository
[ ] hcom can launch or attach to the intended Claude/Codex sessions
[ ] hcom list sees active sessions
[ ] MAPS task truth never depends on hcom's internal DB
[ ] LangGraph checkpoint state is separate from maps.db
```

Before calling the control plane complete, also run the behavioral simulations
specified by the active project roadmap: atomic claim race, independent-review
separation, restart persistence, and RnS recovery without a mandatory WezTerm
cockpit.

## 8. Updates and troubleshooting

### hcom

```bash
hcom status
hcom update
```

Use `hcom reset all` only when intentionally clearing/archiving hcom local state;
it is not a routine repair command for MAPS task state.

### LangGraph

Record package versions when debugging:

```bash
python - <<'PY'
import importlib.metadata as md
for pkg in ('langgraph', 'langgraph-checkpoint-sqlite'):
    print(pkg, md.version(pkg))
PY
```

If async graph calls fail through `SqliteSaver`, use the documented
`AsyncSqliteSaver` path instead of bypassing the checkpointer abstraction.

### SQLite

For manual inspection:

```bash
sqlite3 .maps/state/maps.db '.tables'
sqlite3 .maps/state/maps.db 'PRAGMA journal_mode;'
sqlite3 .maps/state/maps.db 'PRAGMA integrity_check;'
```

A failed claim is not automatically a database error. It may correctly mean
another worker claimed the task first.

## 9. Official sources

Checked 2026-08-14. Re-verify commands before changing installers or dependency
versions.

- hcom official repository/README:
  https://github.com/aannoo/hcom
- LangGraph overview/install:
  https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph persistence/checkpointers:
  https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph SQLite checkpointer package/source:
  https://pypi.org/project/langgraph-checkpoint-sqlite/
  https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-sqlite
- SQLite quickstart/download:
  https://www.sqlite.org/quickstart.html
  https://www.sqlite.org/download.html
- SQLite transactions/WAL/PRAGMA behavior:
  https://www.sqlite.org/lang_transaction.html
  https://www.sqlite.org/wal.html
  https://www.sqlite.org/pragma.html
