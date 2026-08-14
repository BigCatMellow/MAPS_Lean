<!-- hpom: file: artifacts/reviews/task289-independent-review-mapfinish2-zemi.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->

# Review Record: TASK-289

## Header

```
task_id:      TASK-289
reviewer:     mapfinish2-zemi
review_date:  2026-07-28
task_owner:   mapfinish-rafa
```

Reviewer (mapfinish2-zemi) ≠ task owner (mapfinish-rafa). Independence check passes.

---

## Verdict

```
APPROVED
```

---

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Doc matches live `tasks.task_tier` enum, or explicitly states the distinction with a rename recommendation | PASS | The diff adds a "task_tier naming collision" section stating the dispatch-packet `task_tier` (intake_request.py `classify()`) and `tasks.task_tier` (SQLite column) are distinct concepts, and recommends renaming the dispatch-packet field to `dispatch_tier`. Independently verified rafa's two-concept claim is correct (see Verification below), not just plausible-sounding — this is the acceptance-criteria-sanctioned alternative resolution, not a deviation from it. |
| 2 | grep for `task_tier` across `pre_dispatch_policy.py`, `map_task.py`, and a live `map.db` query confirm the doc matches reality | PASS | Reproduced independently, see Verification. All figures the diff cites (live enum values, DB query result, absence of local/helper/approval) match what I found directly. |

---

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Edits outside `MAP_System/ORCHESTRATION_ENTRYPOINT_SYSTEM.md` | NOT BROKEN — SUBMISSION event (events.jsonl:3241) lists only this file in `artifact_paths`; `git diff` for this task's change touches only this file. |

---

## Files Reviewed

- `MAP_System/ORCHESTRATION_ENTRYPOINT_SYSTEM.md` (diff)
- `MAP_System/scripts/pre_dispatch_policy.py` (grep)
- `MAP_System/scripts/map_task.py` (grep)
- `MAP_System/scripts/intake_request.py` (grep)
- `MAP_System/scripts/command_center_intake.py` (grep)
- `MAP_System/CHANGE_CONTROL_SYSTEM.md` (spot check of the claim that it documents `tasks.task_tier` correctly)
- `MAP_System/map.db` (live query)

---

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/ORCHESTRATION_ENTRYPOINT_SYSTEM.md` | YES — matches task's sole `output_paths` entry |

---

## Risk Identification

| Risk | Severity | Recommended action |
|---|---|---|
| None found | — | — |

---

## Findings

No BLOCKER or REQUIRED findings.

---

## Verification

Independently reproduced every factual claim in the diff rather than accepting rafa's framing at face value:

- `grep -n task_tier MAP_System/scripts/pre_dispatch_policy.py` — confirms enforcement against `"architecture"`, `{"mechanical", "bounded", ""}`, `"operator"` (lines 209-404).
- `grep -n task-tier MAP_System/scripts/map_task.py` — `create.add_argument("--task-tier", choices=["mechanical", "bounded", "architecture", "policy", "operator"])` (line 715). This is the authoritative live 5-value enum; matches the diff exactly.
- `sqlite3 MAP_System/map.db "SELECT DISTINCT task_tier FROM tasks WHERE task_tier IS NOT NULL;"` → `bounded`, `architecture`, `policy` — a subset of the 5-value enum, none outside it. Matches the diff's stated query result exactly.
- `grep -n task_tier MAP_System/scripts/intake_request.py` — `classify()` only ever sets `"task_tier": "core"` (3 call sites) or `"task_tier": "shaping"` (1 call site). No `local`, `helper`, or `approval` value anywhere in this file or in `command_center_intake.py` (confirmed via separate grep, zero matches).
- `grep -n task_tier MAP_System/CHANGE_CONTROL_SYSTEM.md` — documents the `tasks.task_tier` release-tier gating (`policy`/`operator`/`architecture` triggers High-risk tier), consistent with the live enum, supporting the diff's claim that this file already documents the column correctly.

Conclusion: rafa's two-concept claim is factually correct, not merely defensible — the dispatch-packet `task_tier` field and the `tasks.task_tier` SQLite column are genuinely different fields with different value sets and different producers/consumers, and `local`/`helper`/`approval` are unimplemented legacy values that exist nowhere in the code. The chosen resolution (document the distinction + recommend a rename) is the correct outcome given this evidence, not just an acceptable fallback.

---

## Notes

Diff is documentation-only, additive, and stays within the task's single declared output path. No scope creep, no unverified claims found. Approving.
