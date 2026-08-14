# Review: TASK-307 Smalls Pre-Deploy Gateway Rotation Ops

task_id: TASK-307
reviewer: codex-lab-vumo
task_owner: claude-lab-nene
review_date: 2026-07-29
review_scope: Independent Smalls-side pre-deploy review without claiming stale Muza review slot.

## Verdict

CHANGES_REQUESTED

Do not deploy the reviewed Biggie TASK-307 patch to Smalls yet. Functional routing is coherent and the focused tests reported by the implementer are reproducible where the Smalls pre-deploy tree can run them, but the security pass found one REQUIRED issue in the new remote-writable `rotation-restore` gateway operation.

## Acceptance Criteria Check

| # | Result | Notes |
|---|---|---|
| 1 | PARTIAL | Biggie evidence says the patch is unchanged from damo-nivo and focused tests pass. Smalls pre-deploy hashes intentionally differ and the new operations are absent locally. |
| 2 | PASS | Functional review performed by codex-lab-vumo from the task packet, exact Biggie hcom source packets, and reproduced Smalls checks. |
| 3 | FAIL | Security-framed review found a REQUIRED finding in `rotation-restore` argument authorization/binding. |
| 4 | NOT CHECKED | Deployment is explicitly blocked until review approval; no source or deployment changes were made. |
| 5 | NOT CHECKED | Post-deployment live RUKI verification is intentionally not run before approval and deployment. |
| 6 | PASS | I did not address task-approve/review-artifact availability, did not transition TASK-305/TASK-306, did not use direct SQL, and did not deploy. |

## Files Reviewed

- `MAP_System/artifacts/operations/gateway-rotation-ops-deployment-2026-07-29.md` as supplied in hcom #44277 because the artifact is absent from this Smalls checkout.
- `MAP_System/db/claims.py` local Smalls file plus exact Biggie hcom packets for `register_agent`, `transfer_rotation_claims`, and `restore_rotation_claims` (#44317, #44460).
- `MAP_System/scripts/context_rotation.py` local Smalls file plus exact Biggie focused packet for authority routing and finalize/restore paths (#44360, #44399, #44402).
- `MAP_System/scripts/map_authority.py` local Smalls file plus exact Biggie full/focused packets (#44323, #44391).
- `MAP_System/tests/test_context_rotation.py` local Smalls file plus exact Biggie focused mirror-routing test packet (#44360, #44364, #44367).

## Functional Correctness Pass

The Biggie patch design routes production mirror writes through `map_authority.py` instead of directly opening local mirror `map.db`: `acknowledge_rotation()` calls `_register_replacement_agent()`, `finalize_rotation()` calls `_transfer_claims()`, and rollback paths call `_restore_claims()` when export or ledger commit fails. The mirror/authority split is controlled by `_is_mirror_write(db_path)`, which only routes the production `map.db` on a host configured as `mode=mirror`; fixture databases remain local, matching existing tests.

`map_authority.py` adds `register-agent`, `rotation-transfer`, and `rotation-restore` to `ALLOWED_OPERATIONS`, exposes CLI subcommands with bounded argument counts, and dispatches to `claims.py` helpers. The tests supplied in the Biggie packet cover mirror-mode routing for ACK/finalize and rollback-through-authority on export failure.

Smalls pre-deploy state is correctly old: local `map_authority.py` rejects `register-agent`, `rotation-transfer`, and `rotation-restore` as not allowlisted. This confirms why Smalls cannot currently serve the new rotation operations.

## Security Review Pass

Reviewed required areas:

| Area | Result | Notes |
|---|---|---|
| Forced-command allowlist | PASS | New operations are explicit allowlist entries; unknown operations are rejected by `encode_request()`/`decode_request()`. |
| Authority routing | PASS | Mirror production writes are routed via `map_authority.py`; non-production fixture DBs stay local. |
| Identity/session authorization | PARTIAL | Client-side `context_rotation.py` verifies live replacement identity/session before calling authority operations. The gateway itself does not independently verify hcom session state. |
| Argument validation | REQUIRED | `rotation-restore` accepts caller-supplied row JSON and passes it to `restore_rotation_claims()` without binding it to a prior authority-generated transfer snapshot. |
| Malformed input | REQUIRED | JSON syntax errors are handled, but schema-valid JSON with arbitrary row values can drive verbatim row updates; schema-invalid rows may fail via ordinary exceptions rather than a deliberately validated restore contract. |
| Transaction/rollback | PASS for accidental failure | `transfer_rotation_claims()` uses `BEGIN IMMEDIATE` and returns pre-transfer row snapshots. `restore_rotation_claims()` runs inside the connection context, so exceptions roll back partial updates. |
| Fail-closed behavior | PARTIAL | Bad base64, oversized requests, non-allowlisted operations, wrong argument counts, and JSON syntax errors fail closed. The restore operation's authorization model is too broad for a remote-writable gateway. |

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/scripts/map_authority.py`; `MAP_System/db/claims.py` | `rotation-restore` is a remote-writable gateway operation that accepts arbitrary `old_row`, `replacement_row`, and `task_rows` JSON from the caller, then `restore_rotation_claims()` restores `agents` and `tasks` rows verbatim. The authority host does not bind that restore payload to a prior `rotation-transfer`, a stored nonce, the current continuity ledger entry, or verified old/replacement/session state. This creates a sanctioned path around normal task lifecycle verbs: any holder of the forced-command key can craft row JSON to rewrite task/agent state, not only undo the immediately preceding transfer. | Bind restore to authority-generated state before allowing deployment. Acceptable fixes include: make transfer+post-transfer finalize/rollback a single authority-side operation; persist a one-use transfer snapshot/nonce server-side and require it for restore; or remove public `rotation-restore` and replace it with a constrained operation that only restores a recorded prior transfer for the same old/replacement agents and task IDs. Add tests that crafted row JSON cannot mutate unrelated tasks/agents and that restore only succeeds for the recorded transfer snapshot. |

## Frozen Hash Verification

The frozen Biggie hashes came from hcom #44277. I independently computed the same four paths on Smalls before deployment; all four differ, which matches the expected pre-deploy state because Smalls lacks the patch.

| File | Frozen Biggie sha256 | Smalls sha256 | Match |
|---|---|---|---|
| `MAP_System/db/claims.py` | `0a6746031ded856c9c429999f4f90e75d87caf53742d5fbe6ff6809db350a40e` | `6fe47cf76aa49e2e075540284cd6ea5d09852e9a3de7df173bf9ced8aeb2de50` | No, expected pre-deploy |
| `MAP_System/scripts/context_rotation.py` | `3c8af4be714d1eaea3cce49d6e126056c71613e8f4e583cf3b4c69d4ce5c3bec` | `8b958abfa5405a3b6d8d6c49f0e184f68bce80e87e2c419685cf50f1fbdcfe97` | No, expected pre-deploy |
| `MAP_System/scripts/map_authority.py` | `c01dc152f4ec12fbfa14902762439116b58b68c0bf5776015f56d26d60e9a454` | `635f96f222dbe66c6ad4682f7e2662d20376f98b0c2d6bd967efabbe82989aec` | No, expected pre-deploy |
| `MAP_System/tests/test_context_rotation.py` | `6515557329fb037b397dc8f7a05f2da272c14c1be1996f14e7d1e3ba2a50a8ba` | `a0a7179f7a58cd2b114cb89f9979170ec05de8385adc61ffb900c292e3122a1f` | No, expected pre-deploy |

## Forbidden Changes Check

- No source files edited.
- No deployment to Smalls.
- No task transition for TASK-307.
- No release/impersonation of the stale Muza review claim.
- No manual TASK-305/TASK-306 status transition.
- No direct SQL against `map.db`.

## Verification

- `map-authority task show TASK-307` - PASS; task is authority-backed, status `SUBMITTED`, owner `claude-lab-nene`, no current claimant, outputs and acceptance criteria read.
- `sha256sum MAP_System/db/claims.py MAP_System/scripts/context_rotation.py MAP_System/scripts/map_authority.py MAP_System/tests/test_context_rotation.py` - PASS; Smalls hashes computed and recorded above.
- `MAP_System/.venv/bin/python -m py_compile MAP_System/db/claims.py MAP_System/scripts/map_authority.py MAP_System/scripts/context_rotation.py MAP_System/tests/test_context_rotation.py` - PASS on Smalls pre-deploy files.
- `MAP_System/.venv/bin/python MAP_System/tests/test_context_rotation.py` - PASS on Smalls pre-deploy files; 16/16 tests passed.
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_map_authority` - PASS on Smalls pre-deploy files; 17 tests passed.
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_map_authority_notify` - PASS on Smalls pre-deploy files; 6 tests passed.
- Direct `encode_request()` probe for `register-agent`, `rotation-transfer`, and `rotation-restore` on Smalls - PASS as pre-deploy negative control; all three are rejected as not allowlisted.

## Notes

This is a pre-deploy review of the Biggie patch, not a review of a deployed Smalls state. The functional approach is close, but the restore operation needs a narrower authority contract before it is safe to install on the writable authority host.
