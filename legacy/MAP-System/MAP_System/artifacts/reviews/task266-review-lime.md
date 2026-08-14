# Review: TASK-266

## Verdict

CHANGES_REQUESTED

## Reviewed Files

- `MAP_System/db/claims.py`
- `MAP_System/scripts/map_task.py`
- `MAP_System/tests/test_recover_orphan.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/tasks/TASK-186.json`
- `MAP_System/tasks/TASK-266.json`
- `MAP_System/workflow/task_graph.json`
- `MAP_System/events/events.jsonl`

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/db/claims.py` | `recover_orphan_task()` validates the written reason but does not validate `actor_id`. A blank/whitespace actor successfully changes an orphan from `IN_PROGRESS` to `READY` and reports whitespace as `recovered_by`. This violates the acceptance criterion that recovery requires an actor and makes direct sanctioned-function use unauditable. | Reject empty or whitespace-only `actor_id` before opening the transaction or changing task state. Add a focused test proving the task remains `IN_PROGRESS` when the actor is invalid. The CLI should also fail cleanly for `--actor ''`. |
| REQUIRED | `MAP_System/tasks/TASK-266.json` | The implementation added `MAP_System/tests/test_recover_orphan.py` and changed `MAP_System/scripts/run_tests.sh`, but neither path is registered in TASK-266 `output_paths`. This leaves task-owned work outside the durable ownership boundary and outside the task's declared review scope. | After rework, register both paths with the sanctioned `map_task.py add-output-path` verb before resubmission. |
| REQUIRED | `MAP_System/tasks/TASK-266.json` | SQLite says `SUBMITTED`, while the task mirror and graph still say `READY`; the task timeline also has no `SUBMISSION` event. The submission therefore did not satisfy the governing requirement to keep SQLite and file-backed state synchronized and record durable progress. | Resubmit using the normal synchronized workflow: update the task mirror and graph from SQLite and append a `SUBMISSION` event identifying the implementation and verification evidence. |

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_recover_orphan.py` - PASS (7 tests).
- Temporary-copy CLI probe using `map_task.py recover-orphan` - PASS: database and exported mirror moved to `READY`; event named actor, prior owner, and reason.
- Temporary isolated function probe with `actor_id='   '` - FAIL as expected for this review: function returned success and changed the task to `READY`.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` - FAIL during review because live TASK-186 had just been claimed by another agent while its mirror still showed `READY`; this is concurrent TASK-186 activity, not attributed to TASK-266.

## Notes

The core recovery predicate correctly refuses a set claimant, an unexpired lease, and non-`IN_PROGRESS` states in the focused suite. The real TASK-186 recovery event at `MAP_System/events/events.jsonl` names the actor, prior owner, and written reason. No TASK-266 source files were modified during review.

## Re-review - 2026-07-22

### Verdict

CHANGES_REQUESTED

The three original findings were addressed in substance: blank actors now fail
before mutation, all four implementation/test paths are registered, and the
resubmission synchronized SQLite/mirrors with a canonical `SUBMISSION` event.
One normalization defect remains in the CLI integration.

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/map_task.py` | `recover_orphan_task()` returns the stripped actor, but `recover_orphan()` continues using raw `args.actor` for `ensure_agent()`, `append_event()`, and the summary. A CLI call with `--actor ' review-probe '` recovers successfully as `review-probe` while creating agent/event identity `' review-probe '` and emitting a malformed double-spaced attribution. The function result, agent table, JSONL event, SQLite event, and summary therefore disagree about who acted. | After recovery succeeds, use `result['recovered_by']` consistently for agent registration, event sender/actor, and summary. Add a CLI-level regression test proving whitespace-padded input produces only the normalized identity and event attribution. |

### Re-verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_recover_orphan.py` - PASS (9 tests).
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` - PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_events.py --fail-on-new` - existing repository baseline still has one unrelated `TASK_SUBMITTED` warning at line 2145; TASK-266's new event is canonical `SUBMISSION`.
- Temporary-copy CLI normalization probe - FAIL: agent row, SQLite event sender, JSONL `sender`/`actor`, and summary retained whitespace while the command result reported the stripped actor.

## Final Re-review - 2026-07-22

### Verdict

APPROVED

The remaining CLI integration defect is fixed. `recover_orphan()` now assigns
`result["recovered_by"]` once and uses that normalized identity for agent
registration, SQLite and JSONL event attribution, and summary text. The new
CLI-level regression executes the real command and exporter against the
canonical schema, checks the printed result and every persisted identity
surface, rejects padded agent rows, and preserves the legitimate seeded prior
owner rather than weakening the assertion to demand an impossible one-row
agent table.

### Final Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_recover_orphan.py` - PASS,
  10/10.
- Temporary-copy mutation changing the fixed assignment back to
  `actor = args.actor` - regression test FAILS at the normalized-agent
  assertion, proving it detects the reported defect.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py` -
  PASS.
- `MAP_System/.venv/bin/python MAP_System/scripts/validate_task_graph.py` -
  PASS.
- `MAP_System/scripts/run_tests.sh` - 70 pass / 2 fail. Both failures are the
  established repository baseline caused by the pre-existing non-canonical
  `TASK_SUBMITTED` event at `events.jsonl:2145`; focused TASK-266 coverage and
  all adjacent claim/review/exporter/integration tests pass.
- SQLite, `tasks/TASK-266.json`, and `workflow/task_graph.json` all record
  `SUBMITTED` before approval. The latest JSONL `SUBMISSION` records the fix and
  verification evidence.

### Security and Authority Check

PASS. Recovery remains narrowly restricted to `IN_PROGRESS` rows with no
claimant and no live lease. Actor and reason are validated before mutation;
task identifiers are parameterized; the event and agent identity derive from
the normalized function result; and the CLI exports mirrors after the atomic
state transition. The change adds no shell construction, network access,
destructive operation, privilege escalation, or path supplied by the caller.
The existing transaction and conditional update prevent recovery from matching
a live claimed task. No `BLOCKER` or `REQUIRED` finding remains.
