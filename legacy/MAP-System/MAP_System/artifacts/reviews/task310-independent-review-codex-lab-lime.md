# Review: TASK-310 Truthful MAP Authority State

task_id: TASK-310
reviewer: codex-lab-lime
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-310-codex-lab-lime-59db2f29
review_scope: Independent Biggie-local review of the unpublished task-owned implementation and delivery artifact under TASK-315's pre-publication topology correction.

## Verdict

CHANGES_REQUESTED

The core classification, snapshot-revision, rollback, and last-good behavior is
implemented coherently, and all 52 independently rerun tests pass. Two
fail-closed consumer/topology defects and one contract-level verification gap
remain. They prevent approval until corrected and independently rerun.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Every operator-facing state view names authority host, revision, last successful sync time, and freshness | FAIL | `map-authority status`, `map-authority route`, and the rendered-state integration expose the contract. Direct `MAP_System/.venv/bin/python MAP_System/graph/runner.py`, however, emits no `authority` object. This direct command is a standing startup invocation in `MAP_System/AGENTS.md` and the lab startup prompt, so it is an operator-facing state view. |
| Disconnecting or making Smalls unreachable produces `STALE` or `UNAVAILABLE`, never green/current | PARTIAL | The shared classifier and `map-authority route` gate pass the stale/unavailable fixtures and the live wrapper currently reports `STALE_AUTHORITY`. The direct runner simultaneously emits `next_route: review` and a dispatch recommendation with no freshness warning. |
| Biggie remains read-only and no second lifecycle authority, scheduler, or derived truth source is created | PARTIAL | `MAP_System/map.db` is mode `0444`, canonical claims use `map-authority`, and no second database writer was added. But `active_local_writer_services()` treats every nonzero `systemctl --user is-active` result as inactive. In this review environment `systemctl` reported `Failed to connect to bus`, while `map-authority status` returned `local_writer_services: []` and `topology_valid: true`; inability to inspect writer services is therefore presented as a proven-clean topology. |
| Focused tests cover fresh, stale, unavailable, clock-skew, rollback, and last-good behavior; independent core review | PARTIAL | The named cases and the full focused suite pass independently. The delivery contract's stricter verification matrix also requires explicit sync-age-expiry and writer-service-active classification coverage. Current tests exercise a synthetic stale gate and install refusal, but not those two `authority_status()` classification branches. |

## Files Reviewed

- `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md`
- `MAP_System/graph/runner.py`
- `MAP_System/scripts/map_authority.py`
- `MAP_System/scripts/map_authority_notify.py`
- `MAP_System/scripts/render_active_state.py`
- `MAP_System/tests/test_map_authority.py`
- `MAP_System/tests/test_map_authority_notify.py`
- `MAP_System/tests/test_render_active_state.py`
- `MAP_System/tests/test_command_center_authority_freshness.py`
- `MAP_System/tasks/TASK-310.json`
- `MAP_System/tasks/TASK-315.json`
- `MAP_System/shared/project-brief.md`
- `MAP_System/shared/requirements.md`
- `MAP_System/shared/decisions.md` (DEC-036 through DEC-041)

## Functional And Security Review

- Authority revisions are computed from SQLite online backups, carried in the
  snapshot response, and compared with the validated database before install.
- Snapshot installation stages all files, replaces `map.db` last, and restores
  prior mirrors/database sidecars on failure.
- The notifier retains the last successful time, revision, and observation
  time after a later failed sync.
- Mirror classification rejects a writable database, material future clock
  skew, and revision mismatch. Route wrapping preserves underlying task data
  while replacing non-fresh recommendations with `STALE_AUTHORITY`.
- Remote requests use a fixed argv with no shell. Snapshot validation retains
  its traversal, link, membership, size, and checksum checks.
- Biggie was correctly fail-closed through the wrapper before the authority
  hold was cleared: `map-authority status` reported database mode `0444`,
  `freshness: STALE`, and a 1,181-second last-good age against a 180-second
  threshold. After Zeno stopped the disabled-but-active watcher and forced a
  refresh, an independent 2026-08-01T17:43:52Z probe reported `FRESH`, age 41
  seconds, revision `sha256:ca99f87458cd7e6bc94b38c48948a40e840cd2c19567b1d6e4a4c5d96c560fd3`,
  database mode `0444`, no reported writers, and `topology_valid: true`.
- The documented review-topology correction is valid. This review examined the
  unpublished Biggie files in place and does not treat Smalls' older checkout
  as source evidence. Canonical approval must remain blocked until this exact
  artifact is transported and checksum-verified on Smalls.

## Findings

| Severity | Location | Finding | Required action |
|---|---|---|---|
| REQUIRED | `MAP_System/graph/runner.py`; `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md` Required Consumers | Direct runner output has no authority object or freshness gate. During this review it emitted `next_route: review` while `map-authority status/route` reported a stale mirror. The artifact's scope rationale calls the runner a consumer but leaves its direct result unqualified, contradicting its own Required Consumers rule and the actual mandated startup invocation. | Make the direct runner result embed the shared authority contract and fail closed, or remove every sanctioned/mandatory direct invocation and durably redefine the consumer boundary. Add a regression that compares direct and wrapped non-fresh behavior. |
| REQUIRED | `MAP_System/scripts/map_authority.py:641-656` | Writer-service discovery fails open. Missing `systemctl` or any nonzero/error probe is treated the same as an inactive service. The live command printed three bus-connection errors yet reported no active writers and `topology_valid: true`. This can classify a mirror as clean without proving the no-local-writer invariant. | Represent probe failure as unknown/invalid and make `authority_status()` fail closed unless writer inactivity was positively established. Preserve diagnostic text without exposing secrets. Add a service-manager-unavailable regression. |
| REQUIRED | `MAP_System/tests/test_map_authority.py`; delivery artifact Verification Matrix | No focused test drives a healthy last-success timestamp beyond `freshness_threshold_seconds` through `authority_status()`, and no test proves an active writer service makes the status `INVALID`. Synthetic gate input and install refusal do not test these classifier rows. | Add explicit classification tests for sync-age expiry and writer-service-active invalidity, then rerun the complete focused suite. |
| RECOMMENDED | `MAP_System/scripts/map_authority.py:48`; delivery artifact Time and Failure Rules | The 180-second default is hardcoded and displayed, but no code derives it from the configured mirror interval plus bounded grace as the contract states. A timer interval change can silently invalidate the threshold relationship. | Establish one durable/configured interval source and derive or validate the default threshold against it. |

## Independent Verification

- `map-authority task show TASK-310` — PASS; canonical state was `SUBMITTED`,
  owner `zeno`, attempt 5/5, with the reviewed output paths and criteria.
- `map-authority claim-review TASK-310 codex-lab-lime` — PASS; canonical claim
  `REV-TASK-310-codex-lab-lime-59db2f29` was created before substantive review.
- `MAP_System/.venv/bin/python -m unittest -v
  MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify
  MAP_System.tests.test_render_active_state
  MAP_System.tests.test_command_center_authority_freshness` — PASS; 52 tests.
- Named edge cases passed: fresh mirror, failure after last-good, unavailable
  before success, writable mirror, future clock, revision mismatch, online
  backup revision, failed database swap restoration, failed multi-file mirror
  rollback, active-writer install refusal, pre-install revision mismatch, and
  notification-state last-good preservation.
- `map-authority status` — fail-closed freshness PASS: it first reported
  `STALE`, then `FRESH` after the corrective sync, with database mode `0444`
  throughout; topology probe certainty FAIL as described above because this
  invocation printed bus-connection failures while returning an empty writer
  list.
- Direct `MAP_System/.venv/bin/python MAP_System/graph/runner.py` versus
  `map-authority route` — FAIL/PASS contrast reproduced: direct output omitted
  authority and recommended review; wrapped output returned `STALE_AUTHORITY`.

## Forbidden Changes Check

This review did not edit implementation files, tests, task records, shared
state, Git state, or the external CommandCenterUI. It did not synchronize the
mirror or approve/reject TASK-310. Its only workspace change is this review
artifact; the canonical review claim and its eventual release use the
sanctioned `map-authority` route.
