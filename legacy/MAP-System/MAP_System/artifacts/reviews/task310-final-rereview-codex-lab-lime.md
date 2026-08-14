# Final Rereview: TASK-310 Truthful MAP Authority State

task_id: TASK-310
reviewer: codex-lab-lime
task_owner: zeno
review_date: 2026-08-01
review_claim: REV-TASK-310-codex-lab-lime-2736770f
prior_review: MAP_System/artifacts/reviews/task310-rereview-codex-lab-lime.md
review_scope: Final independent Biggie-local rereview of attempt 7/7, limited to the explicit nonproduction `--db` integration correction and retention of production fail-closed behavior.

## Verdict

APPROVED

The bounded correction fixes the scratch-database integration regression
without weakening production authority enforcement. Production database paths
still use the configured mirror contract and fail closed; explicitly different
fixture paths are classified locally through the same authority schema. The
focused suite passes 56/56, integration passes 11/11, and the complete release
suite passes 84/84. Canonical task approval remains intentionally deferred
until Zeno confirms checksum-verified transport of this exact artifact to
Smalls.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Every operator-facing state view names authority host, revision, last successful sync time, and freshness | PASS | Normal direct summaries call `runner_authority_status()` through `summarize_with_authority()`. Interrupted and re-interrupted gate responses pass `Path(args.db)` to `output_with_authority()`. Production output retains the mirror object; isolated fixture output retains the same schema and explicit local revision. |
| Disconnecting or making Smalls unreachable produces `STALE` or `UNAVAILABLE`, never green/current | PASS | The canonical `MAP_DB_PATH` branch still calls `authority_status(load_authority_config())`. In this review process, inability to reach the user service manager produced `INVALID`, `topology_valid: false`, and `STALE_AUTHORITY`; the fixture exception did not affect that path. |
| Biggie remains read-only and no second lifecycle authority, scheduler, or derived truth source is created | PASS | Production `MAP_System/map.db` remains mode `0444` and is selected by resolved-path equality, including alternate spellings/symlinks that resolve to the same file. Only an explicitly different database is treated as the authority for its isolated invocation. No production writer, scheduler, or canonical mutation path was added. |
| Focused tests cover fresh, stale, unavailable, clock-skew, rollback, and last-good behavior; independent core review | PASS | The 56 focused tests remain green. The 11-step agent-loop integration now completes against a temporary `--db`, and the full 84-check release suite passes with task/schema/mirror, policy, resilience, authority, Command Center, and integration coverage. |

## Bounded Delta Review

- `runner_authority_status(db_path)` compares resolved paths. The canonical
  production database always uses the configured authority mode and shared
  mirror health; it cannot enter the fixture branch through a relative path or
  symlink alias.
- An explicitly different database calls `authority_status({"mode":
  "authority"}, db_path=..., writer_services=[], database_writable=...)`.
  Missing, non-file, unreadable, or read-only fixtures therefore remain
  non-green; a valid writable isolated SQLite database receives an online-
  backup revision and `AUTHORITATIVE` for that isolated graph.
- `summarize_with_authority()` takes the effective `db_path` from graph state.
  Both interrupt call sites pass `Path(args.db)` explicitly to
  `output_with_authority()`, preventing gate-pause output from accidentally
  falling back to production mirror health during fixture runs.
- Production behavior is retained rather than bypassed. A direct probe of
  `runner_authority_status(MAP_DB_PATH)` returned mirror mode and fail-closed
  `INVALID` when service-manager status could not be proven. The same probe
  against a temporary writable SQLite database returned local
  `AUTHORITATIVE`, `topology_valid: true`, and a `sha256:` revision.
- The end-to-end integration test exercised the actual `agent_loop.py --db
  <temporary database>` path, including claim, handler execution, submission,
  lease cleanup, and isolated export.

## Files Reviewed

- `MAP_System/artifacts/recovery/ws1-truthful-authority-state.md`
- `MAP_System/artifacts/reviews/task310-rereview-codex-lab-lime.md`
- `MAP_System/graph/runner.py`
- `MAP_System/scripts/map_authority.py`
- `MAP_System/scripts/integration_test.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/tests/test_map_authority.py`
- `MAP_System/tests/test_map_authority_notify.py`
- `MAP_System/tests/test_render_active_state.py`
- `MAP_System/tests/test_command_center_authority_freshness.py`
- `MAP_System/tasks/TASK-310.json`
- `MAP_System/tasks/TASK-315.json`

## Findings

| Severity | Location | Finding | Action |
|---|---|---|---|
| RECOMMENDED | `MAP_System/scripts/map_authority.py:48`; delivery artifact Time and Failure Rules | The shared 180-second threshold remains hardcoded rather than mechanically derived or validated against the configured one-minute mirror timer plus grace. This predates and is unaffected by the fixture correction. | In a future maintenance task, establish one durable interval source and derive or validate the threshold. |
| OPTIONAL | `MAP_System/graph/runner.py:889`; focused tests | The production/fixture selection is exercised by the full integration test and direct reviewer probes, but there is no small unit test dedicated to resolved-path equality, read-only fixture rejection, and gate-pause propagation of `args.db`. | Add focused boundary tests when this runner surface is next maintained. |

No BLOCKER or REQUIRED findings remain.

## Independent Verification

- `map-authority task show TASK-310` — PASS; canonical state `SUBMITTED`,
  owner `zeno`, attempt 7/7.
- `map-authority claim-review TASK-310 codex-lab-lime` — PASS; claim
  `REV-TASK-310-codex-lab-lime-2736770f` opened before substantive rereview.
- `MAP_System/.venv/bin/python -m unittest -v
  MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify
  MAP_System.tests.test_render_active_state
  MAP_System.tests.test_command_center_authority_freshness` — PASS; 56/56.
- `MAP_System/.venv/bin/python MAP_System/scripts/integration_test.py` — PASS;
  11/11.
- `MAP_System/scripts/run_tests.sh` — PASS; summary
  `pass=84 fail=0 total=84`.
- `MAP_System/scripts/map-git diff --check -- <TASK-310 code/test paths>` — PASS.
- Direct production-versus-fixture classifier probe — PASS: production stayed
  mirror/fail-closed; temporary writable SQLite fixture was local
  `AUTHORITATIVE` with a consistent revision.

## Forbidden Changes Check

This final rereview did not edit implementation files, tests, task records,
shared state, Git state, external CommandCenterUI, or Smalls source. It did not
synchronize the mirror or canonically approve TASK-310. Its only workspace
change is this review artifact; canonical review claim/release operations use
the sanctioned `map-authority` route.
