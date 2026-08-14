# Review: TASK-236 real-time advisory monitor

- task_id: TASK-236
- reviewer: codex-lab-lilo
- task_owner: claude-lab-gome
- risk_tier: medium
- review_claim: claimed by `codex-lab-lilo` before substantive review

## Verdict

CHANGES_REQUESTED

## Files Reviewed

- `MAP_System/tasks/TASK-236.json`
- `MAP_System/scripts/advisory_monitor.py`
- `MAP_System/tests/test_advisory_monitor.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/artifacts/tests/task-advisory-monitor-delivery-note.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/notes/review-guide.md`

## Forbidden Changes Check

PASS — the submitted monitor opens `map.db` with `mode=ro`, reads the event
and status sources, writes no MAP state, claims no task, and starts no standing
process. The delivery note routes standing deployment to command-center rather
than implementing it.

## Acceptance Criteria Check

| Criterion | Result | Evidence |
|---|---|---|
| Read-only, proposal-only findings with `1` iff findings | PARTIAL | The implementation is source-read-only and the live run correctly emits the TASK-186 advisory. Its malformed-claim handling misses a no-lease claim, so orphaned/expired-claim detection is incomplete. |
| Focused tests cover every check plus clean state, and are registered | FAIL | The registered six tests cover only claim/aging logic. They explicitly leave mirror drift and event-log health to a live run; the clean-board test likewise never exercises those two checks. |
| Standing deployment is a decision request, not an implementation | PASS | The delivery note states trigger, output surface, owner, and a proposal-only guardrail without starting a service. |
| E/I recurrence layer is specified and never auto-promotes | PASS | The delivery note specifies signature recurrence as a candidate for core-agent promotion and keeps model judgment out of the deterministic path. |
| Delivery note records the TASK-186 worked example | PASS | The first-run catch and authority-safe triage are documented. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/tests/test_advisory_monitor.py`; `MAP_System/artifacts/tests/task-advisory-monitor-delivery-note.md` | Task acceptance requires focused coverage for all four checks plus a clean-state no-findings case. The submitted tests cover orphaned/expired claims and aging transitions only; their module comment says mirror drift and event-log health are not tested. The delivery note nevertheless marks that criterion MET. A live repository run cannot deterministically prove either check or a globally clean monitor result. | Add isolated fixtures/assertions for agent-mirror drift and event-log-health, and make the clean-state case exercise all monitor checks (not only the two DB checks). Keep test isolation read-only. Update the delivery note to cite the expanded evidence accurately. |
| REQUIRED | `MAP_System/scripts/advisory_monitor.py`; `MAP_System/tests/test_advisory_monitor.py` | `check_orphaned_or_expired_claims` treats a record as orphaned only when both claimant and parsed lease are absent. An `IN_PROGRESS` record with `claimed_by='agent-z'`, no lease, and no heartbeat produces no finding, even though it has no live lease. Conversely, a heartbeat-only record is reported as having “no heartbeat,” which is factually wrong. This leaves malformed/non-live claims invisible and makes an advisory observation unreliable. | Define an active claim as a valid claimant plus a parseable, unexpired lease; emit a source-accurate attention finding for missing/malformed lease or inconsistent claimant/lease state, without inventing heartbeat facts. Add fixtures for claimant-without-lease, claimant-with-malformed-lease, no-claimant-with-lease, and heartbeat-only state; preserve the healthy live-claim no-finding case. |

## Verification

- `python3 MAP_System/tests/test_advisory_monitor.py` — PASS (6/6), but confirms only the incomplete submitted scope.
- `python3 MAP_System/scripts/advisory_monitor.py --json` — exit 1 with the expected proposal-only `TASK-186` orphaned-in-progress finding; no state mutation observed.
- `python3 MAP_System/scripts/validate_events.py --fail-on-new` — PASS (`errors=0`, `new_warnings=0`); validator is read-only by inspection.
- `sh MAP_System/scripts/run_tests.sh` — PASS (all registered checks, including `advisory_monitor_test`).
- Independent malformed-state reproduction: claimant-without-lease produced `[]`; heartbeat-only produced an observation stating “no heartbeat.”

## Notes

The monitor's design boundary is sound: deterministic, visible, proposal-only,
and no standing deployment was started. The two required corrections are narrow
and preserve that design. Once the monitor proves every advertised check and
reports malformed claim state accurately, this medium-risk review can approve.
