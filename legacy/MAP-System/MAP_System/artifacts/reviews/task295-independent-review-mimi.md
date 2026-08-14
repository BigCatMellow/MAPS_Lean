# Review Record: TASK-295

## Header

```
task_id:      TASK-295
reviewer:     claude-lab-mimi
review_date:  2026-07-30
task_owner:   command-center
```

Reviewer (claude-lab-mimi) ≠ task owner (command-center). Independence check passes.

---

## Verdict

```
APPROVED (rereview)
```

Original verdict below was `CHANGES_REQUESTED` for one undeclared-scope gap.
Fix applied exactly as required, independently reconfirmed live via
`map-authority task show TASK-295`: `output_paths` now includes
`MAP_System/db/claims.py` alongside the four originally-registered paths. No
code changed — this was always a pure bookkeeping gap, and the four literal
acceptance criteria and 8/8 focused tests already passed at the original
review. `git status`/collision state otherwise unchanged since. No further
findings on rereview.

---

## Original review (CHANGES_REQUESTED) — superseded above, kept for record

```
CHANGES_REQUESTED
```

---

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `map_task.py` gains a `retire` verb (`task_id --actor --reason`) that transactionally moves a task to RETIRED, appends a durable event, and re-exports mirrors, matching existing verb shape | PASS | Independently confirmed `retire_task` in `db/claims.py` and the `retire` subcommand in `scripts/map_task.py`. Live-exercised repeatedly this session on TASK-304 (unrelated coordination work) — transactional, evented, mirror-synced behavior matches exactly. |
| 2 | Refuses a task already terminal (RELEASED/RETIRED/DONE); refuses empty reason | PASS | `test_map_task_retire.py::test_refuses_terminal_statuses` and `::test_requires_a_reason`/`::test_requires_an_actor` — independently re-ran, all pass. |
| 3 | Focused tests cover success, refusal-per-terminal-status, refusal-on-empty-reason, mirror re-export; wired into `run_tests.sh` | PASS | Independently re-ran `python MAP_System/tests/test_map_task_retire.py`: 8/8 pass, matching the delivery note's claim exactly. `run_tests.sh` line 47 confirms `map_task_retire_test` is wired in. |
| 4 | Task record enumerates every tasks-table lifecycle transition, states which now have a sanctioned verb, and explicitly names any that still don't | PASS | Delivery note's enumeration table and "still verb-less" list are thorough and specific (names TASK-254 as a live, currently-blocked instance of gap #1, not a hypothetical) — exactly what the criterion asks for. |

All four literal criteria pass. The `CHANGES_REQUESTED` verdict below is for an
undeclared-scope gap the criteria don't explicitly cover but the task's own
Scope/Forbidden-Changes discipline requires.

---

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Editing `output_paths` retroactively to hide what was touched | NOT BROKEN — nothing was hidden; the omission is an honest gap, not a cover-up (the delivery note itself openly describes adding `retire_task` to `db/claims.py`). |
| Unregistered edit to a file outside the task's declared scope | **VIOLATED** — see REQUIRED finding below. |

---

## Files Reviewed

- `MAP_System/db/claims.py` (`retire_task`, lines 618+)
- `MAP_System/scripts/map_task.py` (`retire` subcommand)
- `MAP_System/tests/test_map_task_retire.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/artifacts/tests/task295-retire-verb-delivery-note.md`
- Live: `map-authority task show TASK-295`, `MAP_System/tasks/TASK-295.json`

---

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/scripts/map_task.py` | YES — registered output path. |
| `MAP_System/tests/test_map_task_retire.py` | YES — registered output path. |
| `MAP_System/scripts/run_tests.sh` | YES — registered output path. |
| `MAP_System/artifacts/tests/task295-retire-verb-delivery-note.md` | YES — registered output path. |
| `MAP_System/db/claims.py` | **NO** — modified (delivery note's own "What was built" section names `retire_task` as new code here) but never registered via `add-output-path`. Attempted to register it myself as a mechanical fix; `map_task.py`'s `add-output-path` only accepts `{NEEDS_SHAPING, READY, IN_PROGRESS, CHANGES_REQUESTED}` and TASK-295 is `SUBMITTED`, so this cannot be fixed without returning the task to an editable state — hence `CHANGES_REQUESTED` rather than a reviewer-side patch. |

---

## Risk Identification

| Risk | Severity | Recommended action |
|---|---|---|
| `db/claims.py` is the single most shared, most sensitive file in the lifecycle system (touched by nearly every other task this session). Confirmed no *live* collision right now — every other task referencing it (TASK-035/044/199/270/266/274/278/273/293) is RELEASED, and TASK-299/307 are APPROVED — but an undeclared touch means a *future* collision check on this file would not find TASK-295 in the list of prior touchers. | MEDIUM | Register `MAP_System/db/claims.py` via `add-output-path` once the task returns to an editable state (see Required Action), before resubmission. No code change needed — the implementation itself is correct. |

---

## Findings

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| REQUIRED | `MAP_System/db/claims.py` | `retire_task` (new) | Task modified this file (added `retire_task`) without ever registering it via `add-output-path`, so `TASK-295` does not appear as a prior toucher of one of the system's most shared files for future collision checks, even though no collision exists today. | `map_task.py rework TASK-295 --actor <owner> --reason "register db/claims.py output path"`, then `add-output-path TASK-295 --path MAP_System/db/claims.py --actor <owner>` (now legal — `CHANGES_REQUESTED` is in `add-output-path`'s editable-states set), then reclaim and resubmit. No other change needed; all four acceptance criteria already pass and all 8 focused tests already pass. |

No BLOCKER findings.

---

## Notes

This is otherwise strong, disciplined work — the "still verb-less" enumeration
in the delivery note is unusually thorough and names a real, currently-stuck
task (TASK-254) rather than a hypothetical gap. The single finding here is a
bookkeeping completeness issue, not a functional or design defect, and the fix
is mechanical (one `add-output-path` call, no code change). Independently
re-ran every test claim in the delivery note rather than trusting it: 8/8
`test_map_task_retire.py`, and (separately, via background full-suite run)
cross-checked the broader `run_tests.sh` failure count is unrelated to this
task's files.
