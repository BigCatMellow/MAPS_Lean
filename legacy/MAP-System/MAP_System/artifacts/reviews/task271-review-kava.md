# Review: TASK-271

task_id: TASK-271
reviewer: codex-lab-kava
task_owner: codex-lab-veto
review_date: 2026-07-22

## Verdict

APPROVED

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Current-context estimate, configurable 150000 default, and honest metric semantics. | PASS | Boundary tests pass; Codex uses latest request context and Claude uses latest prompt footprint rather than cumulative transcript traffic. |
| 2 | Validated immutable STATE_SNAPSHOT v2, canonical/touched digests, and locked atomic master update. | PASS | Prepare, claim-inventory, redaction, locking, self-reference, and commit-pointer tests pass; live ledger validates. |
| 3 | Detect snapshot/master/canonical drift before ACK while preserving raw history. | PASS | Independent master tamper was refused without byte changes; snapshot/task/path drift tests pass; abandoned and finalized snapshots remain in ledger history. |
| 4 | Checksum- and live-session-bound ACK before recoverable finalize. | PASS | Independent fabricated-session and vanished-replacement probes refused; finalize stayed `acknowledged` without superseding the old session. Rollback tests pass. |
| 5 | Focused coverage and test registration. | PASS | Context 15/15, token 2/2, watcher 39/39; all are registered in `run_tests.sh`. Full baseline is 72 pass / 2 established unrelated failures. |
| 6 | AGENTS, template, guide, and installed launcher guidance. | PASS | Guidance covers 150k, 60%/75%, ledger, visible replacement, ACK/finalize, abandon/recovery, and never-clear ordering; both launchers pass shell syntax and content coverage. |

## Forbidden Changes Check

| Boundary | Status |
|---|---|
| Raw transcript/history must never be deleted. | NOT BROKEN — implementation has no transcript/history deletion path; abandoned snapshots remain preserved. |
| Watcher remains advisory and must not launch hidden replacements or supersede sessions. | NOT BROKEN — it sends transition-based `inform` notices and persists fingerprints only. |
| SQLite/task state remains canonical; ledger must not silently override drift. | NOT BROKEN — ledger is a checked commit pointer; task/path drift blocks pre-ACK continuation. |
| Old session must remain recoverable until verified ACK/finalize. | NOT BROKEN — missing/mismatched/vanished replacement and export/master failures refuse or roll back without superseding the old session. |

## Files Reviewed

- `MAP_System/AGENTS.md`
- `MAP_System/artifacts/reviews/task271-security-selfcheck-lime.md`
- `MAP_System/notes/context-rotation-guide.md`
- `MAP_System/scripts/agent_token_status.py`
- `MAP_System/scripts/context_rotation.py`
- `MAP_System/scripts/limit_watcher.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/shared/context-continuity.md`
- `MAP_System/templates/install/bin/ai-command-center-lab-claude`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex`
- `MAP_System/tests/test_agent_token_status.py`
- `MAP_System/tests/test_context_rotation.py`
- `MAP_System/tests/test_limit_watcher.py`
- `MAP_System/workflow/templates/state_snapshot.yaml`

## Findings

No open findings remain.

| Prior Severity | File | Re-review Resolution |
|---|---|---|
| REQUIRED — RESOLVED | `MAP_System/scripts/context_rotation.py` | ACK now checks deterministic master rendering under the rotation lock. Independent tamper reproduction was refused with `master_render_drift`, and the tampered bytes remained unchanged. |
| REQUIRED — RESOLVED | `MAP_System/scripts/context_rotation.py` | The live roster now retains agent-to-session bindings. ACK refuses a supplied session mismatch, and finalize refuses when the acknowledged identity/session is absent. Independent reproduction left the ledger safely at `acknowledged`. |
| REQUIRED — RESOLVED | `MAP_System/scripts/limit_watcher.py` | State writes are atomic, and a successful notice fingerprint is committed before event append or later recovery work. The new later-poll-failure regression passes; live service state independently showed both expected fingerprints immediately after restart. |
| REQUIRED — RESOLVED | `MAP_System/templates/install/bin/ai-command-center-lab-claude`, `MAP_System/templates/install/bin/ai-command-center-lab-codex` | Both prompts explicitly state the 150k default, `min(120k, 60%)` soft checkpoint, `min(150k, 75%)` hard rotation, visible replacement, recoverable old session, abandon/reprepare route, and never-clear-before-finalize rule. Shell syntax and focused prompt coverage pass. |

## Verification

- Atomic re-review claim: `claim_review("TASK-271", "codex-lab-kava")` returned `True` before substantive re-review.
- `MAP_System/.venv/bin/python MAP_System/tests/test_context_rotation.py` - 15/15 passed, including the master-render refusal/evidence-preservation, session mismatch, vanished-after-ACK, prompt-policy, threshold, self-reference, history, drift, locking, ACK/finalize, and rollback cases.
- `MAP_System/.venv/bin/python MAP_System/tests/test_agent_token_status.py` - 2/2 passed; Claude latest prompt input is separated from cumulative transcript traffic.
- `python3 MAP_System/tests/test_limit_watcher.py` - 39/39 passed; successful notice persistence survives a synthetic later-poll exception and prevents a duplicate send.
- Independent temporary-root adversarial reproduction - master tamper made ACK refuse with `master_render_drift` while preserving exact bytes; fabricated replacement session made ACK refuse; replacement disappearance made finalize refuse while retaining ledger phase `acknowledged`.
- `MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py validate` - returned `ok: true`, revision 5; finalized/history snapshots retained valid hashes. Expected post-finalize task/path changes were reported as drift booleans but not blocking issues.
- `sh -n` on both installed launcher scripts - passed.
- `python3 MAP_System/scripts/validate_task_mirrors.py` - passed.
- `systemctl --user status map-rns-watcher.service --no-pager` - supervised unit was loaded/enabled and active since 2026-07-22 16:09:49 EDT with PID 143411 running the expected source path at a 300-second interval.
- Live watcher evidence - `agents/limit-watcher-state.json` was atomically updated at 16:09:50 and contained `rotation_due:120000:150000` fingerprints for both `claude-lab-gabi` and `codex-lab-veto`; event line 2345 records Veto's matching notice at the same second.
- `MAP_System/scripts/run_tests.sh` - reproduced the submission baseline exactly: `pass=72 fail=2 total=74`. Both failures derive from the established new `TASK_SUBMITTED` warning at `events/events.jsonl:2145` (`validate_events_no_new_warnings` and aggregate `validate_layer1_test`), not TASK-271 behavior.

## Notes

- The 150,000-token default and proportional `min(default, 75% window)` rotation boundary are correctly implemented; the soft boundary is 120,000 or 60% of a known window. Codex uses `last_token_usage`; Claude uses the latest successful prompt footprint, not cumulative cache/read traffic.
- Prepare uses a locked commit-pointer design: immutable snapshot first, atomically replaced ledger second. Generated-master self-reference is explicitly classified, and abandoned attempts remain hash-validated history.
- Snapshot tamper, master-render drift, canonical task drift, touched-path drift, claim inventory mismatch, wrong hash/session, replacement disappearance, export failure, and ledger-write failure now have focused coverage and independently reproduced safe refusal behavior.
- The live dogfood ledger preserves both the abandoned first attempt and finalized second attempt. The old `codex-lab-lime` hcom process was still process-bound during review; that does not undo SQLite finalize, but it means the operational evidence demonstrates safe ordering rather than completed terminal shutdown.
