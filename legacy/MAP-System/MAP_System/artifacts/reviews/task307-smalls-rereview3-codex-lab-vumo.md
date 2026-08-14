# Review: TASK-307 Smalls Pre-Deploy Gateway Rotation Ops Attempt 3

task_id: TASK-307
reviewer: codex-lab-vumo
task_owner: claude-lab-nene
review_date: 2026-07-29
review_scope: Fresh canonical Smalls-side rereview of TASK-307 attempt 3 source/evidence packets; review claimed as codex-lab-vumo; no source edits and no deployment.

## Verdict

APPROVED

Attempt 3 addresses the remaining transaction-boundary finding. In the reviewed `claims.py` transfer slice, `_ensure_rotation_transfers_table(conn)` runs first, then `conn.execute("BEGIN IMMEDIATE")` runs before every `agents`/`tasks` snapshot `SELECT`. The recorded snapshot, `rotation_transfers` insert, task transfer updates, and agent lifecycle updates now occur under the same explicit SQLite write transaction before `conn.commit()`.

## Acceptance Criteria Check

| # | Result | Notes |
|---|---|---|
| 1 | PASS | Attempt 3 evidence was supplied with updated hashes for the two changed files and unchanged attempt-2 hashes for `context_rotation.py`, `map_authority.py`, and `schema.sql`. |
| 2 | PASS | Functional review performed from canonical task state and exact hcom source/evidence packets. Mirror write routing, opaque `transfer_id` propagation, rollback wiring, and one-argument restore contract remain coherent. |
| 3 | PASS | Security review confirmed caller-supplied restore row JSON remains removed, unknown/replayed transfer IDs fail closed, and the attempt-3 snapshot reads are now transaction-bound before transfer. |
| 4 | NOT CHECKED | Deployment to Smalls was explicitly out of scope for this review. |
| 5 | NOT CHECKED | Live RUKI post-deploy verification cannot run before deployment. |
| 6 | PASS | The patch still excludes the separate task-approve/review-artifact problem, manual TASK-305/TASK-306 transition, and direct SQL against `map.db`. |

## Files Reviewed

- `MAP_System/artifacts/operations/gateway-rotation-ops-deployment-2026-07-29.md` attempt-3 evidence packet from hcom #45128/#45131.
- `MAP_System/db/claims.py` exact attempt-3 `transfer_rotation_claims()` slice from hcom #45136/#45139.
- `MAP_System/tests/test_context_rotation.py` exact attempt-3 SQL-order regression test from hcom #45143/#45146.
- `MAP_System/scripts/context_rotation.py` attempt-2 unchanged transfer/restore/finalize wiring reviewed in the prior pass and cited unchanged by hcom #45131.
- `MAP_System/scripts/map_authority.py` attempt-2 unchanged dispatch/CLI gateway bounds reviewed in the prior pass and cited unchanged by hcom #45131.
- `MAP_System/migration/schema.sql` attempt-2 unchanged `rotation_transfers` schema reviewed in the prior pass and cited unchanged by hcom #45131.

## Functional Correctness Pass

`transfer_rotation_claims()` now performs `_ensure_rotation_transfers_table(conn)`, then `BEGIN IMMEDIATE`, then reads `old_row`, `replacement_row`, and each task row. It then builds `snapshot_json`, inserts the `rotation_transfers` row, updates each active claimed task, updates both agent lifecycle rows, commits, and returns only `{"transfer_id": transfer_id}`.

Keeping the idempotent ensure-table DDL outside the explicit transaction is acceptable for this race. The DDL only ensures the `rotation_transfers` table exists; it does not read or mutate the `agents` or `tasks` rows whose snapshot/transfer atomicity was at issue. The row state that rollback can later restore is now read only after `BEGIN IMMEDIATE` holds the write lock.

## Security Review Pass

The attempt-2 security fixes remain intact: restore is bound to a server-side `rotation_transfers` record, uses only an opaque transfer ID from the caller, rejects unknown IDs, rejects already-restored IDs, and rejects the old three-argument row JSON gateway shape before restore dispatch.

Attempt 3 fixes the remaining race: a concurrent authority-side writer can no longer modify the old agent, replacement agent, or transferred task rows between the snapshot reads and the claim transfer because the snapshot reads occur after `BEGIN IMMEDIATE`. The new regression test traces actual sqlite statement order and asserts every `SELECT * FROM agents` / `SELECT * FROM tasks` snapshot read occurs after the `BEGIN IMMEDIATE` statement. That test would have failed against the attempt-2 ordering because those SELECTs occurred before the explicit transaction.

## Findings

No REQUIRED findings.

## Hash Packet

Supplied Biggie attempt-3 hashes:

| File | Biggie sha256 |
|---|---|
| `MAP_System/db/claims.py` | `71a2627eaff2f7a2c160f3c89b09947ea012c628e13ca775a126eb4bb5bab839` |
| `MAP_System/tests/test_context_rotation.py` | `19bb1d2092ff3c2cbbb5a306bbf414b10d3872a95caeedf1e551f400e338cfad` |

Unchanged from attempt 2:

| File | Biggie sha256 |
|---|---|
| `MAP_System/scripts/context_rotation.py` | `09329b18fc23b8a95158bed8cf5609d567e18538a547af2099ec353f60785f85` |
| `MAP_System/scripts/map_authority.py` | `6c8e71c585254d22c373f936267c61c4f8169f23cc4b0941ab9ef40f9d5acf5e` |
| `MAP_System/migration/schema.sql` | `4d6f8ee5d9a2af9bc99d2cd4cd3af5e29f58ee6dc24b4dba1f123df5f9b9b3f4` |

## Forbidden Changes Check

- No source files edited.
- No deployment to Smalls.
- No release or impersonation of Muza.
- No manual TASK-305/TASK-306 status transition.
- No direct SQL against `map.db`.

## Verification

- `map-authority task show TASK-307` - PASS; task is `SUBMITTED`, owner `claude-lab-nene`, `claimed_by` initially null before canonical review claim.
- `map-authority claim-review TASK-307 codex-lab-vumo` - PASS; `ok=true`, `claimed=true`.
- Exact hcom source/evidence packets #45131, #45139, and #45146 reviewed.
- Implementer evidence reviewed: `py_compile` clean, `test_context_rotation.py` PASS 25/25, `test_map_authority.py` PASS 17/17, `test_map_authority_notify.py` PASS 6/6, `map-git diff --check` clean.

## Notes

This approval is for pre-deploy review of the Biggie patch. It does not deploy to Smalls and does not verify live RUKI gateway behavior after deployment.
