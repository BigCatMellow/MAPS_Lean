# TASK-268 Lifecycle Authority Contract

- task_id: TASK-268
- author: codex-lab-zori
- status: implemented_pending_review
- scope: synchronized submission verb and review-claim identity contract
- related_repair: MAP_System/repairs/REPAIR-0008-task278-map-task-output-defer.md

## Submission authority

The sanctioned agent-facing submission path is:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/map_task.py submit TASK-NNN \
  --actor exact-agent-id
```

The command owns the complete synchronized transition:

1. Read the canonical SQLite row and require `IN_PROGRESS` with
   `claimed_by == actor`.
2. Call `MAP_System.db.claims.submit_task()` as the internal guarded SQLite
   primitive.
3. After the primitive commits, append one canonical `SUBMISSION` event whose
   sender and trace actor are the submitting agent.
4. Export SQLite state to the task JSON and task-graph mirrors.

`MAP_System.db.claims.submit_task()` remains a Boolean atomic transition
primitive. Direct use by an interactive agent is unsupported because it does
not own event emission or mirror synchronization. Internal automation that
still calls the primitive is compatibility code; TASK-274 is the sequenced
successor that moves canonical submission event emission into the low-level
API after TASK-268 and TASK-273 release.

When TASK-274 adds low-level event emission, it must update the CLI caller so a
successful submission still produces exactly one event, not one event in each
layer.

## Submission failure semantics

- Unknown task, wrong status, wrong claimant, or blank actor: fail before the
  transition and write no event.
- A race that removes the live claim between verification and transition:
  the guarded primitive returns `False`; the command fails and writes no event.
- Event append happens only after the SQLite status commit. A process failure
  cannot record a submission that never happened.
- Mirror export happens after the event. If append or export fails, the command
  exits nonzero and preserves the authoritative SQLite transition for explicit
  reconciliation; it does not invent or roll back task intent.
- Repeating the command after a successful submission fails its
  `IN_PROGRESS`/claimant check and does not duplicate the event.

## Review-claim identity authority

TASK-270 already implemented and independently released the declared identity
contract used by TASK-268:

- `claim_review()` accepts a valid reviewer that is not yet present in
  `agents`.
- Before inserting the review claim, it registers that exact reviewer through
  the same `INSERT OR IGNORE` contract used by `map_task.py ensure_agent()`.
- `False` is reserved for four expected outcomes: unknown task, task not
  `SUBMITTED`, reviewer equals the durable task owner, or another open review
  claim exists.
- An unexpected `sqlite3.IntegrityError` remains diagnosable and propagates.
  Only the observed invariant “an open claim now exists” classifies a race as
  occupied.

This task preserves that released implementation and verifies it in the same
end-to-end lifecycle that exercises the new submission verb. Re-keying
no-self-review enforcement from task owner to durable submission author is
outside this task and remains sequenced through TASK-274 then TASK-278.

## End-to-end evidence

`MAP_System/tests/test_task268_lifecycle.py` builds the real schema in an
isolated database and runs the real CLI and exporter. It proves:

- the current claimant can submit and a non-claimant cannot;
- SQLite becomes `SUBMITTED` and clears claim/lease/heartbeat fields;
- exactly one canonical `SUBMISSION` event is written to SQLite and JSONL with
  `trace_id`, actor, action, and target;
- task JSON and graph mirrors both become `SUBMITTED`;
- repeat submission creates no duplicate event;
- a previously unregistered reviewer can claim the submitted task;
- the reviewer agent row and open review-claim row agree.

Focused verification:

- `MAP_System/.venv/bin/python MAP_System/tests/test_task268_lifecycle.py`
  — 3/3 pass.
- `MAP_System/.venv/bin/python MAP_System/tests/test_review_claims.py`
  — 12/12 pass.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py`
  — pass after the approved REPAIR-0008 sequencing correction.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py`
  — pass.
- `MAP_System/.venv/bin/python MAP_System/tests/test_exporter_invariants.py`
  — 2/2 pass.

## Residual risk and rollback

- Until TASK-274 lands, internal callers of the low-level Boolean primitive do
  not automatically receive the CLI’s event guarantee.
- A crash after SQLite commit but before event/export remains visible as
  reconciliation debt, never as a false submission event.
- Rollback of this task is limited to removing the `submit` parser/function and
  restoring the prior AGENTS guidance. Existing canonical events are
  append-only and must not be deleted.
- REPAIR-0008 is reversible by re-registering `map_task.py` on TASK-278 through
  the sanctioned `add-output-path` verb only after predecessor ownership
  clears.
