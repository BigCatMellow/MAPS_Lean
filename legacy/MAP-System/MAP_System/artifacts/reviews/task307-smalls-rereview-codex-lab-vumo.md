# Review: TASK-307 Smalls Pre-Deploy Gateway Rotation Ops Rereview

task_id: TASK-307
reviewer: codex-lab-vumo
task_owner: claude-lab-nene
review_date: 2026-07-29
review_scope: Fresh Smalls-side rereview of the reworked Biggie source/evidence packets supplied over hcom; no source edits and no deployment.

## Verdict

CHANGES_REQUESTED

The prior arbitrary row-JSON restore issue is addressed: `rotation-restore` now takes a single opaque `transfer_id` and restore uses server-side `rotation_transfers` state. I am not approving deployment yet because the reworked `transfer_rotation_claims()` still reads the rows used for `snapshot_json` before it starts `BEGIN IMMEDIATE`, so the recorded snapshot is not atomically bound to the transfer it is supposed to roll back.

## Acceptance Criteria Check

| # | Result | Notes |
|---|---|---|
| 1 | PASS | Biggie rework evidence was supplied with updated post-rework hashes and focused source packets. Smalls remains pre-deploy by instruction. |
| 2 | PASS | Functional rereview performed from exact hcom source packets and canonical task state. The design still routes mirror writes through the authority gateway. |
| 3 | FAIL | Security rereview found one REQUIRED issue: snapshot rows are read before the transfer transaction begins, so rollback can restore stale pre-lock state after a concurrent authority-side write. |
| 4 | NOT CHECKED | Deployment is intentionally blocked until review approval. |
| 5 | NOT CHECKED | Live RUKI post-deploy verification is intentionally not run before approval and deployment. |
| 6 | PASS | I did not address the separate task-approve/review-artifact issue, did not transition TASK-305/TASK-306, did not use direct SQL, and did not deploy. |

## Files Reviewed

- `MAP_System/artifacts/operations/gateway-rotation-ops-deployment-2026-07-29.md` as supplied in hcom #44824.
- `MAP_System/db/claims.py` exact reworked slice for `register_agent`, `_ensure_rotation_transfers_table`, `transfer_rotation_claims`, and `restore_rotation_claims` from hcom #44827/#44830.
- `MAP_System/scripts/context_rotation.py` exact reworked slices for authority operation routing, opaque `transfer_id` propagation, export rollback, master-ledger rollback, audit event append, and session close from hcom #44833/#44836/#44921.
- `MAP_System/scripts/map_authority.py` exact reworked dispatch and CLI bound slices for `register-agent`, `rotation-transfer`, and one-argument `rotation-restore` from hcom #44839/#44842.
- `MAP_System/tests/test_context_rotation.py` exact reworked tests for mirror routing, positive restore, unknown transfer ID, replay rejection, and old three-argument gateway rejection from hcom #44845/#44849.
- `MAP_System/migration/schema.sql` exact `rotation_transfers` schema slice from hcom #44852/#44855.

## Functional Correctness Pass

The functional routing remains coherent. `context_rotation.py` registers replacement agents through `register-agent` on mirror production DBs, obtains a single `transfer_id` from `_transfer_claims()`, and calls `_restore_claims(transfer_id, db_path)` on export or master-ledger failure. The successful finalize path advances the continuity ledger before the best-effort audit event and old-session close, so a failed tab close does not unwind a committed finalize.

`map_authority.py` dispatches `rotation-transfer` to `transfer_rotation_claims()` and returns `{"ok": true, "transfer_id": ...}`. `rotation-restore` has a one-argument contract in both dispatch and CLI bounds. The old three-JSON-argument shape is rejected by the argument-count guard before `restore_rotation_claims()` is called.

## Security Review Pass

The rework fixes the first review's primary authorization flaw. The caller no longer sends `old_row`, `replacement_row`, or `task_rows`; restore looks up a server-recorded `rotation_transfers` row by `transfer_id`, rejects unknown IDs, rejects already-restored IDs, and marks the transfer consumed after restore. The new tests cover positive restore, fabricated ID rejection, replay rejection, unrelated-row preservation, and gateway rejection of the old argument shape.

One security requirement is still not met: the snapshot read and transfer are not atomic. In the reviewed `claims.py` packet, `old_row`, `replacement_row`, and each `task_row` are selected and converted into `snapshot` before `conn.execute("BEGIN IMMEDIATE")`. The insert into `rotation_transfers` and the claim/agent updates happen in the transaction, but the state being inserted was read outside that transaction.

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/db/claims.py` | `transfer_rotation_claims()` reads the pre-transfer agent/task rows before acquiring the write transaction with `BEGIN IMMEDIATE`. A competing authority-side writer can change one of those rows after the snapshot SELECTs but before the transfer transaction begins. If this finalize later rolls back, `restore_rotation_claims(transfer_id)` will restore the stale pre-lock snapshot and can overwrite the intervening legitimate update. This does not reintroduce arbitrary caller-supplied JSON, but it fails the requested atomic snapshot+transfer guarantee. | Acquire the transaction before reading rows for the snapshot, then validate, build `snapshot_json`, insert the `rotation_transfers` row, update the transferred tasks/agents, and commit under the same transaction/lock. If schema self-heal remains inside the helper, put it inside the explicit transaction or ensure the migration creates the table before this path. Add a test that would fail if a row can change between snapshot read and transaction acquisition. |

## Updated Hash Packet

Supplied Biggie post-rework hashes:

| File | Biggie sha256 |
|---|---|
| `MAP_System/db/claims.py` | `25de53578a3395cee288271acb3fbb0899f6de9d3694b37b0fdc9e53baf47c92` |
| `MAP_System/scripts/context_rotation.py` | `09329b18fc23b8a95158bed8cf5609d567e18538a547af2099ec353f60785f85` |
| `MAP_System/scripts/map_authority.py` | `6c8e71c585254d22c373f936267c61c4f8169f23cc4b0941ab9ef40f9d5acf5e` |
| `MAP_System/tests/test_context_rotation.py` | `e987c0881eec7d1e0729c6f51bb4007d4a862b50035fa4cdc8633409d038e91e` |
| `MAP_System/migration/schema.sql` | `4d6f8ee5d9a2af9bc99d2cd4cd3af5e29f58ee6dc24b4dba1f123df5f9b9b3f4` |

## Forbidden Changes Check

- No source files edited.
- No deployment to Smalls.
- No TASK-307 status transition.
- No release or impersonation of the stale Muza review claim.
- No manual TASK-305/TASK-306 status transition.
- No direct SQL against `map.db`.

## Verification

- `map-authority task show TASK-307` - PASS; task is `SUBMITTED`, owner `claude-lab-nene`, no current claimant, and includes the reworked output paths.
- Exact hcom source/evidence packets #44824, #44830, #44836, #44842, #44849, #44855, #44859, and #44921 reviewed.
- Python sqlite transaction probe - PASS; `CREATE TABLE IF NOT EXISTS` and `SELECT` do not start a transaction, confirming that the reviewed `BEGIN IMMEDIATE` happens after the snapshot reads.

## Notes

This is a pre-deploy rereview of Biggie code supplied over hcom, not a deployed Smalls source review. The restore authorization model is substantially improved, but the snapshot must be captured under the same transaction that records and performs the transfer before this is safe to deploy to the authority host.
