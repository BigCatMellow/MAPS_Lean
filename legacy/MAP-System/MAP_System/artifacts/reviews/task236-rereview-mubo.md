# Independent Re-review: TASK-236

task_id: TASK-236
reviewer: codex-lab-mubo
task_owner: claude-lab-gome
submitter: claude-lab-zaro
review_date: 2026-07-23

## Verdict

APPROVED

The three prior REQUIRED findings are closed. The focused suite passes 25/25,
the full suite reproduces the disclosed 71-pass/3-fail baseline, task mirrors
pass, and the monitor leaves its three declared read-only inputs byte-identical.
The added owner-liveness check now treats `available` and `busy` as live and
describes `standby` truthfully as parked rather than departed.

The submitter disclosed a post-submission delivery-note edit. I reloaded and
reviewed the current file, captured the reviewed hashes below, and found that
the edit weakens an overclaim by documenting a real limitation: this observer
detects recorded roster state, not actual process departure. That limitation is
acceptable here because the observer remains proposal-only and the note now
states that its result is a floor rather than a census. Liveness computation
belongs to `scripts/liveness_reaper.py`; duplicating hcom process inference in
this read-only observer would create a competing authority.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Read-only proposal-only monitor, structured findings, exit 1 iff findings. | PASS | Live execution returned findings and exit 1. SHA-256 values for `map.db`, `events.jsonl`, and `agents/status.json` were identical before and after. Source opens SQLite with `mode=ro` and contains no state mutation path. |
| 2 | Focused fixtures cover each check and clean state; suite registered. | PASS | `test_advisory_monitor.py` passes 25/25, including malformed claim shapes, mirror drift, event health, clean state, busy-owner silence, and truthful standby wording. `run_tests.sh` registration passes. |
| 3 | Standing deployment is a command-center decision request. | PASS | Delivery note leaves trigger, output surface, owner, grouping, and repeat suppression undecided; no service was deployed. |
| 4 | Recurrence/novelty emits candidates only; no automatic promotion or model control path. | PASS | Delivery note specifies core-agent promotion and keeps any model assistance outside the deterministic path. |
| 5 | Delivery-note evidence includes the TASK-186 worked example. | PASS | `task-advisory-monitor-delivery-note.md` uses the required evidence structure and records the first-run catch. |

## Added Scope Check

The owner-liveness increment is not one of the five registered criteria but was
added by the 2026-07-23 operator directive, so it was reviewed independently.

- `LIVE_OWNER_STATUSES = ("available", "busy")`; the focused busy fixture
  proves no stale-owner finding.
- `standby` yields `owner-parked` at MEDIUM with confirm-before-action language
  and no claim that the owner departed.
- The live run returned 21 owner findings: 15 `owner-inactive` and 6
  `owner-parked`, plus one expired lease and one event-log-health finding.
- The delivery note now discloses that stale `available` roster rows cause
  false negatives. This is a roster-maintenance/liveness-reaper gap, not a
  reason to add a second liveness authority to the observer.

## Findings

### RECOMMENDED — Freeze submitted outputs during review

The delivery note was edited after SUBMITTED and after the reviewer lane was
routed. The submitter disclosed the change and the reviewed version is safer
because it removes an overclaim, so this does not block approval. Future
post-submission corrections should return through a clearly frozen resubmission
or be coordinated before editing; otherwise the reviewer can unknowingly
approve a different file than the one inspected.

### RECOMMENDED — Correct the stale live-state task identifier

The delivery note's verification table says the current expired lease is
`TASK-268`; the independently reproduced live run identifies `TASK-263`.
TASK-268 was already returned to READY before this review. This is a
non-capability evidence typo in moving global state: the asserted count and
finding kind still reproduce, and the exact current subject is recorded here.
The submitter corrected this after approval by removing the volatile task ID
and retaining the stable finding-kind distribution. The reviewer inspected and
accepted that exact documentation-only delta before release.

## Forbidden Changes Check

| Boundary | Result |
|---|---|
| Monitor must not claim, edit, approve, or mutate MAP state. | PASS |
| No standing hidden process may be deployed unilaterally. | PASS |
| No model call may enter the deterministic control path. | PASS |
| `db/claims.py`, `scripts/map_task.py`, and no-self-review guards remain outside TASK-236. | PASS |

## Files Reviewed

- `MAP_System/scripts/advisory_monitor.py`
- `MAP_System/tests/test_advisory_monitor.py`
- `MAP_System/artifacts/tests/task-advisory-monitor-delivery-note.md`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/artifacts/reviews/task236-review-lilo.md`
- `MAP_System/artifacts/reviews/task236-rereview-lori.md`

## Verification

- Focused advisory-monitor tests: 25/25 pass.
- Task mirror validation: pass.
- Full suite: 71 pass, 3 fail, 74 total. Failures reproduce the disclosed
  research-summary validation issue, event warning at line 2145, and its
  layer-1 cascade.
- Scoped `map-git diff --check`: pass.
- Read-only input hashes were unchanged:
  - `map.db`: `fe93a9d98198d05a6f69b4d88a2479297d5ffc0ad931af984e405cb133ebc9af`
  - `events.jsonl`: `990de3a9a6bccaf4d99f8008ea23362a4f78bd7a0618621642cad24d0ef82a68`
  - `agents/status.json`: `da5c491e3aba1a654c292352f562451dcfc8e3b18435ed8bac7b3c10ce2e3e5f`
- Reviewed output hashes:
  - `advisory_monitor.py`: `a3ba481df82903066f079e4b51a423702a48e3ca5f1b00a2aa4e65a22d5baf86`
  - `test_advisory_monitor.py`: `5893c2ca072ef3ba294a0cbc14900ce0ec42e3838a14546b5ee4f237b7ad3810`
  - delivery note after the accepted stable-evidence correction:
    `46771b0b7f50e56448596f06d1cb979179f9cf90006e6ce777490c188b68d763`
  - `run_tests.sh`: `4347cad754f9cefb3d50317ae922f83bf5880cf7af1f87feb1add965acccaece`
