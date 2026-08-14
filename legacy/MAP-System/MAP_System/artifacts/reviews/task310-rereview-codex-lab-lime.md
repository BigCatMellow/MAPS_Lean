# Rereview: TASK-310 Truthful MAP Authority State

task_id: TASK-310
reviewer: codex-lab-lime
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-310-codex-lab-lime-33c8df82
prior_review: MAP_System/artifacts/reviews/task310-independent-review-codex-lab-lime.md
review_scope: Independent Biggie-local rereview of attempt 6/6 against every prior REQUIRED finding; unpublished source reviewed in place under TASK-315's topology correction.

## Verdict

APPROVED

All prior REQUIRED findings are resolved. The shared authority contract now
covers direct runner summaries and gate-pause responses, writer-service probe
uncertainty fails closed, and the missing classification regressions are
present. The independently rerun focused suite passes 56/56. Canonical task
approval remains intentionally deferred until Zeno confirms that this exact
artifact was transported unchanged to Smalls.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Every operator-facing state view names authority host, revision, last successful sync time, and freshness | PASS | `graph/runner.py` now routes normal summaries through `summarize_with_authority()` and interrupted/resumed gate responses through `output_with_authority()` or the same summary path. Both call the shared `authority_status()` and `apply_freshness_gate()` functions used by `map-authority route`. Status and rendered-state consumers remain covered. |
| Disconnecting or making Smalls unreachable produces `STALE` or `UNAVAILABLE`, never green/current | PASS | Stale, unavailable, invalid, age-expired, and failed-sync fixtures pass. In this review process the user service manager is unreachable; both direct runner and wrapped route independently returned `INVALID`, `topology_valid: false`, and `next_route: STALE_AUTHORITY`, preserving but not presenting the underlying review recommendation as current. |
| Biggie remains read-only and no second lifecycle authority, scheduler, or derived truth source is created | PASS | `MAP_System/map.db` remains mode `0444`; canonical review operations use `map-authority`. Writer discovery now raises on missing `systemctl` or unexpected probe errors. `authority_status()` converts that uncertainty to `INVALID`; `install_snapshot()` propagates it and refuses synchronization. No writer or scheduler was added. |
| Focused tests cover fresh, stale, unavailable, clock-skew, rollback, and last-good behavior; independent core review | PASS | The 56-test suite passes independently. Added tests explicitly exercise 181-second age expiry, active-writer invalidity, unavailable service-manager invalidity, and direct-versus-wrapped non-fresh equivalence, closing the prior matrix gaps. Existing rollback, sidecar restoration, revision mismatch, future-clock, last-good, and notification-state cases remain green. |

## Prior Required Findings Resolution

| Prior finding | Result | Rereview evidence |
|---|---|---|
| Direct runner omitted authority/freshness | RESOLVED | `summarize_with_authority()` is used for ordinary and resumed output; `output_with_authority()` covers interrupted gate output. The actual direct command emits the authority object and gates non-fresh recommendations. |
| Writer-service probe errors failed open | RESOLVED | `active_local_writer_services()` now distinguishes inactive/unknown units (return codes 3/4) from probe failure, raises bounded `AuthorityError` diagnostics for failures, and treats missing `systemctl` as failure. `authority_status()` exposes `writer_service_probe_error`, sets `topology_valid: false`, and returns `INVALID`. |
| Age-expiry and active-writer classifier rows lacked tests | RESOLVED | `test_sync_age_beyond_threshold_is_stale`, `test_active_writer_service_invalidates_mirror_topology`, and `test_unavailable_service_manager_invalidates_mirror_topology` exercise the actual classifier. `test_direct_runner_and_wrapped_route_share_non_fresh_gate` checks shared routing behavior. |

## Files Reviewed

- `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md`
- `MAP_System/artifacts/reviews/task310-independent-review-codex-lab-lime.md`
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

## Functional And Security Rereview

- Direct and wrapped paths import one classifier and one gate rather than
  duplicating freshness logic.
- Fail-closed output retains the underlying route only under explicitly stale
  inspection fields; it replaces the actionable route with
  `STALE_AUTHORITY`.
- Service-manager stderr/stdout is captured, whitespace-normalized by the
  command boundary, and bounded before exposure through the authority payload.
  No shell, request envelope, key content, or transcript is introduced.
- Active-writer detection still blocks snapshot installation. Probe
  uncertainty now blocks it as well rather than becoming an empty writer list.
- Snapshot path, checksum, online-backup revision, staged replacement,
  database-last activation, sidecar restoration, and multi-file rollback
  controls are unchanged and pass their regression tests.
- A transient database revision mismatch observed between two sequential live
  probes was attributable to the periodic mirror refresh after the rereview
  claim. Repeating against a stable mirror produced identical direct/wrapped
  revision `sha256:ca4b0af8c18dfd50d239a75ef16882ee3d5e6633c278bd8da93b4be5fa2330db`
  and identical fail-closed output.
- The task owner's host-side `FRESH` report is consistent with the code and
  fixtures, but approval does not depend on trusting it: this reviewer
  independently reproduced the harder service-manager-unavailable failure
  mode and observed both consumer paths fail closed identically.

## Findings

| Severity | Location | Finding | Action |
|---|---|---|---|
| RECOMMENDED | `MAP_System/scripts/map_authority.py:48`; delivery artifact Time and Failure Rules | `DEFAULT_FRESHNESS_SECONDS = 180` remains a displayed hardcoded value rather than being mechanically derived or validated against the configured one-minute mirror timer plus grace. This does not invalidate current classification because the deployed interval is one minute and the declared threshold is consistently shared. | In a future maintenance task, establish one durable interval source and derive or validate the threshold so a timer change cannot silently desynchronize the contract. |

No BLOCKER or REQUIRED findings remain.

## Independent Verification

- `map-authority task show TASK-310` — PASS; canonical state `SUBMITTED`,
  owner `zeno`, attempt 6/6.
- `map-authority claim-review TASK-310 codex-lab-lime` — PASS; claim
  `REV-TASK-310-codex-lab-lime-33c8df82` opened before substantive rereview.
- `MAP_System/.venv/bin/python -m unittest -v
  MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify
  MAP_System.tests.test_render_active_state
  MAP_System.tests.test_command_center_authority_freshness` — PASS; 56 tests.
- `MAP_System/scripts/map-git diff --check -- <TASK-310 code/test paths>` — PASS.
- Live direct-versus-wrapped comparison with unavailable user service manager
  — PASS: both `INVALID`, `topology_valid: false`, `STALE_AUTHORITY`, no active
  writers asserted, identical local revision after mirror stabilization.
- `sha256sum MAP_System/map.db` before and after a status probe — unchanged;
  database remained read-only.

## Forbidden Changes Check

This rereview did not edit implementation files, tests, task records, shared
state, Git state, the external CommandCenterUI, or Smalls source. It did not
synchronize the mirror or canonically approve TASK-310. Its only workspace
change is this rereview artifact; canonical review claim/release operations use
the sanctioned `map-authority` route.
