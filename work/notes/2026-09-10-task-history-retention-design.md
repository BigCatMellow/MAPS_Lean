# Canonical task/history retention — Stage-0 design

Date: 2026-09-10
Status: `DESIGN READY FOR INDEPENDENT REVIEW — NO RUNTIME CHANGE`
Owner task: [`../tasks/task-history-retention-design.md`](../tasks/task-history-retention-design.md)
Source finding: [`2026-09-09-competitor-borrow-integration-log.md`](2026-09-09-competitor-borrow-integration-log.md), Slice 09

## Question

What does MAPS_L mean when it says canonical semantic task history is append-only?

The current system leaves two distinct questions partially implicit:

1. may an already committed `task_events` row be edited/deleted directly?
2. may the owning canonical task itself be hard-deleted, taking history with it?

Those must be answered together before adding immutability triggers.

## Accepted-main evidence

### Normal write path is append-only

`runtime/state/base.py::BaseStore._append_event()` only inserts rows into `task_events`. Task creation calls it in the same explicit transaction as the canonical task insert. Other lifecycle operations likewise append semantic events alongside state mutations.

PR #330 separately froze the local transaction invariant by fault injection: when event persistence fails during claim, canonical task mutation rolls back too. That proves local atomicity, not retention.

### Database does not enforce event immutability

Current `runtime/state/schema.sql` defines:

```sql
CREATE TABLE IF NOT EXISTS task_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    actor TEXT,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

No `BEFORE UPDATE` or `BEFORE DELETE` trigger exists for `task_events`.

Therefore:

```text
normal application code appends only
!=
database-enforced immutable history
```

A direct SQLite writer can currently alter or remove an event row.

### The rest of the schema has moved toward stronger immutable evidence

Newer evidence/lineage records such as run manifests, run context/worktree bindings, submission-run links, run/session links, helper/recovery lineage, review subjects, release checks, and several lifecycle decision records use explicit UPDATE/DELETE guards.

That makes `task_events` an outlier despite being the oldest semantic-history surface.

### Parent deletion is not a coherent supported runtime feature today

The event FK uses `ON DELETE CASCADE`, as do many task-owned tables. But no public `delete_task()` operation was found in accepted runtime code. The CLI/runtime expose task creation/shaping/lifecycle/review operations, not canonical task hard deletion.

Moreover, several newer task-owned child tables have their own no-delete triggers. SQLite cascades invoke child deletion behavior, so the schema has evolved away from a simple assumption that every task can always be cascaded away cleanly.

Conclusion: `ON DELETE CASCADE` is real referential behavior, but there is no evidence it represents an accepted user-facing/runtime hard-delete contract.

## Options

### A. Immutable event rows, but task hard-delete may cascade them

Pros:
- preserves current FK shape;
- easy to explain mechanically.

Problem:
- one parent delete can erase all supposedly immutable audit history;
- no current runtime delete feature requires this flexibility;
- it creates a broad destructive bypass around event immutability.

Disposition: reject as default core contract.

### B. Delete task but preserve events through tombstone/archive identity

Pros:
- clean separation of active task state from permanent history;
- supports eventual archival products.

Problem:
- requires new durable identity/lifecycle/archive semantics;
- likely requires FK/schema migration and new read models;
- no demonstrated current need.

Disposition: defer until a real archive/privacy/storage requirement exists.

### C. Forbid canonical task hard deletion once semantic history exists

Pros:
- strongest and simplest audit semantics;
- aligns with existing immutable evidence direction;
- requires no new task state or archival subsystem;
- every ordinary task already gets `TASK_CREATED` atomically, so the rule is deterministic.

Tradeoff:
- future legal/privacy/storage deletion cannot be expressed through normal task deletion and must be deliberately designed.

Disposition: **recommended and selected for review**.

### D. Keep application-only append behavior

Pros:
- zero schema work.

Problem:
- direct SQL can rewrite the historical record;
- weaker than the database guarantees already used for downstream evidence tables;
- undercuts the value of task events as audit evidence.

Disposition: reject.

## Proposed Lean contract

```text
canonical task creation
→ task row + TASK_CREATED commit atomically
→ task row is not normally hard-deletable
→ task_events may only gain later rows
→ historical event rows are never UPDATEd or DELETEd
→ correction = later semantic event, not history rewrite
```

No `ARCHIVED` task state is added. Terminal work remains `DONE` or `BLOCKED`. User interfaces/read models may filter terminal work without changing canonical retention.

This is **not** a claim that MAPS must retain all data forever under every legal/privacy/storage condition. It is only the default runtime integrity contract. If a real data-disposal need appears, design an explicit privileged path that states what is deleted/redacted/exported, why, under what authority, and what audit residue is appropriate.

## Why explicit task-delete rejection is preferable to relying on child triggers

If only `task_events` received a `no_delete` trigger, an attempted parent delete would incidentally fail because cascade reaches an immutable event. That would implement the same practical outcome but encode the rule in the wrong owner and produce misleading errors.

A future implementation should therefore make both invariants explicit:

- event rows are immutable;
- canonical task rows cannot be hard-deleted through ordinary SQL/runtime operation.

The task-level guard owns the retention policy; event-level guards own history integrity.

## Why not rewrite all `ON DELETE CASCADE` clauses now

Changing existing SQLite foreign keys generally requires broader table reconstruction/migration. It is unnecessary to prove the selected common-case contract because an explicit task delete guard stops parent deletion before normal cascades become relevant.

The cascade declarations can remain latent referential cleanup mechanics until/unless a separately authorized retention migration has a reason to revisit them. This avoids a large schema churn for a narrow invariant.

## First implementation tranche after independent approval

Smallest expected delta:

1. `runtime/state/schema.sql`
   - add `trg_task_events_no_update`;
   - add `trg_task_events_no_delete`;
   - add explicit `trg_tasks_no_delete`.
2. one focused regression file (or smallest existing state-test owner) proving direct-SQL rejection and ordinary event appends still work.
3. implementation task evidence.

Required behavior proof:

```text
create task
→ TASK_CREATED present
→ UPDATE task_events ... rejected
→ DELETE task_events ... rejected
→ DELETE tasks ... rejected
→ claim/submit/review lifecycle still appends new semantic events
```

No archive state, no retention scheduler, no event-sourcing framework, no export service, and no data migration.

## Edge cases intentionally deferred

- GDPR/CCPA or other legal erasure policy;
- operator-requested project purge;
- database compaction/long-term storage limits;
- redaction of secrets accidentally placed in event summaries;
- export/archive transfer to another store;
- correction-event taxonomy/reference fields;
- deletion of disposable test databases/files themselves.

Those are materially different problems. This design must not pre-solve them by weakening the canonical audit contract or by building an archive subsystem without need.

## Review challenge

Independent review should try to falsify, in particular:

1. that no accepted public task-delete operation exists;
2. that task creation always establishes semantic history in the common runtime path;
3. that event immutability is currently only application-level;
4. that existing immutable child tables make unrestricted cascade deletion an unreliable implied contract;
5. that option C is materially simpler than archive/tombstone semantics while still leaving future explicit data-disposal authority possible;
6. that leaving FK cascades unchanged behind an explicit parent-delete guard is technically coherent and does not hide an active supported behavior.

If any accepted runtime owner actually depends on hard-deleting task rows, this design should be returned for correction rather than forcing the new rule through.