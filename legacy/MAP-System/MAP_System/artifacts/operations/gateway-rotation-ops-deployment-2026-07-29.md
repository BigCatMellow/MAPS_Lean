# Gateway Rotation-Ops Deployment Evidence (TASK-307)

- date: 2026-07-29
- owner: claude-lab-nene
- status: superseded by later events on this same date — see
  "Post-original-approval currency note" at the end of this file
  (claude-lab-sumi, 2026-08-10). Original status line below is stale: it
  predates two further rework rounds and the eventual 2026-07-29T18:33:52Z
  approval by codex-lab-vumo; left in place as historical record rather than
  silently rewritten.
- status (as originally written, now stale): security rework complete (see
  below); independent functional + security review of the REWORKED patch not
  yet performed; nothing deployed to Smalls

## Background

The register-agent/rotation-transfer/rotation-restore operations in
`MAP_System/scripts/map_authority.py` (plus their support in
`MAP_System/db/claims.py`, wiring in
`MAP_System/scripts/context_rotation.py`, and coverage in
`MAP_System/tests/test_context_rotation.py`) were written by an earlier
session (rotation-replacement-damo-nivo, 2026-07-29T04:51:57Z) to fix a real
bug: `acknowledge_rotation()`/`finalize_rotation()` did direct SQLite writes
against a read-only mirror on hosts running in `mode=mirror`, bypassing the
`guard_production_write`/single-writer convention every other write path
follows. The patch was left uncommitted, on Biggie only, pending independent
review — see
`MAP_System/handoffs/STATE_SNAPSHOT-rotation-replacement-damo-nivo-20260729T045157Z.yaml`
for the original session's full account.

This is action-plan step 1a
(`MAP_System/artifacts/planning/biggie-smalls-orchestration-action-plan-2026-07-29.md`):
that code exists only on Biggie and was never deployed to Smalls (RUKI), the
authority host these calls actually route to — so any call to
register-agent/rotation-transfer/rotation-restore against RUKI fails, not
because the logic is wrong, but because RUKI doesn't have it. Confirmed
blocking: claude-lab-nene's own context-rotation handoff hit exactly this
failure earlier the same day.

## Revalidation (2026-07-29, claude-lab-nene)

Confirms TASK-307's first acceptance criterion: the patch is unchanged since
damo-nivo's session and still applies cleanly against current main.

**Checksum drift check** — compared current working-tree file hashes
against the exact values recorded in damo-nivo's own STATE_SNAPSHOT
integrity block:

| File | sha256 (recorded 04:51:57Z and current — identical) | Match |
|---|---|---|
| `MAP_System/db/claims.py` | `0a6746031ded856c9c429999f4f90e75d87caf53742d5fbe6ff6809db350a40e` | Yes |
| `MAP_System/scripts/context_rotation.py` | `3c8af4be714d1eaea3cce49d6e126056c71613e8f4e583cf3b4c69d4ce5c3bec` | Yes |
| `MAP_System/scripts/map_authority.py` | `c01dc152f4ec12fbfa14902762439116b58b68c0bf5776015f56d26d60e9a454` | Yes |
| `MAP_System/tests/test_context_rotation.py` | `6515557329fb037b397dc8f7a05f2da272c14c1be1996f14e7d1e3ba2a50a8ba` | Yes |

All four byte-for-byte identical — zero drift since the patch was left
uncommitted. Recorded values are copied verbatim from
`STATE_SNAPSHOT-rotation-replacement-damo-nivo-20260729T045157Z.yaml`'s
`integrity.touched_paths` block; current values are from this session's own
`sha256sum` run today, both shown as a single column above since they match
exactly.

**Compile check**:
`MAP_System/.venv/bin/python -m py_compile MAP_System/db/claims.py
MAP_System/scripts/map_authority.py MAP_System/scripts/context_rotation.py
MAP_System/tests/test_context_rotation.py` — PASS.

**Test check** (all three suites the original session validated against):
- `MAP_System/.venv/bin/python MAP_System/tests/test_context_rotation.py` —
  PASS, 20/20. (Damo-nivo's session recorded 19/19 with one pre-existing,
  unrelated failure in `test_installed_prompts_name_rotation_policy_and_recovery`
  — that test now passes too; something else fixed the underlying installer-
  template gap in the interim. Not investigated further here, out of
  TASK-307's scope.)
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_map_authority` —
  PASS, 17/17.
- `MAP_System/.venv/bin/python -m MAP_System.tests.test_map_authority_notify` —
  PASS, 6/6.

## Security rework (2026-07-29, after Smalls-side codex-lab-vumo's
## independent security review — CHANGES_REQUESTED)

vumo's required finding: `rotation-restore` accepted caller-supplied
`old_row`/`replacement_row`/`task_rows` JSON and restored them verbatim,
with no binding to a prior authority-generated transfer snapshot, nonce, or
ledger/session state. Any caller able to reach the gateway (over the
forced-command SSH key every core agent on Biggie shares) could craft
arbitrary row data and mutate agents/tasks unrelated to any real rotation
that ever happened — `transfer_rotation_claims()` returned the pre-transfer
snapshot straight to the caller, and `restore_rotation_claims()` trusted
whatever came back without ever recording what it had actually done.

**Fix**: bind restore to server-side recorded transfer state, exactly as
required.

- New table `rotation_transfers` (added to `MAP_System/migration/schema.sql`,
  plus an idempotent `CREATE TABLE IF NOT EXISTS` inside
  `transfer_rotation_claims`/`restore_rotation_claims` themselves so an
  already-provisioned database — Smalls' live `map.db` — self-heals on first
  use rather than needing a separate migration step before this code can
  run) stores `transfer_id` (a random `uuid.uuid4().hex`), `old_agent`,
  `replacement_agent`, the full pre-transfer `snapshot_json`, `created_at`,
  and `restored_at`.
- `transfer_rotation_claims()` now inserts that row in the same transaction
  as the actual claim transfer, and returns only `{"transfer_id": ...}` — it
  no longer hands the caller row data to carry around and echo back.
- `restore_rotation_claims(transfer_id)` looks up the recorded snapshot by
  id. Unknown id → `ValueError("unknown rotation transfer_id: ...")`.
  Already-restored id → `ValueError("... already restored, refusing
  replay: ...")` (closes a replay angle too — a captured legitimate
  transfer_id can't be reused to re-apply the same restore twice). Only on
  success does it apply the *server's* recorded rows and mark
  `restored_at`.
- `map_authority.py`'s `rotation-restore` gateway operation now takes
  exactly one argument (`TRANSFER-ID`), enforced both by the CLI's
  `argument_bounds` (`(1, 1)`, was `(3, 3)`) and by a defense-in-depth check
  inside `dispatch_authority()` itself. The old three-JSON-argument shape
  — literally what an attacker crafting a malicious payload would have sent
  — is rejected before any database is touched.
- `context_rotation.py`'s `_transfer_claims`/`_restore_claims`/
  `finalize_rotation` simplified to pass the opaque `transfer_id` through
  instead of three row dicts — smaller surface, and the caller genuinely
  can no longer shape what gets restored even if it wanted to.

**New tests** (`MAP_System/tests/test_context_rotation.py`), each seeding an
UNRELATED agent/task alongside the real old/replacement pair and asserting
the unrelated rows are byte-identical before and after:
- `test_restore_rotation_claims_undoes_exactly_the_transferred_rows` —
  positive case, a real transfer_id restores correctly.
- `test_restore_rotation_claims_rejects_unknown_transfer_id_and_mutates_nothing`
  — the core guarantee vumo asked for: a fabricated/never-issued transfer_id
  is refused and **zero rows change**, related or unrelated.
- `test_restore_rotation_claims_refuses_replay_after_first_restore` — a
  transfer_id can only restore once.
- `test_rotation_restore_gateway_operation_rejects_the_old_row_json_shape`
  — the old 3-argument row-JSON shape is rejected at the gateway's argument
  boundary, before touching any database.

**Re-verification after rework** — all independently rerun:
- `py_compile` on all five touched files — PASS.
- `test_context_rotation.py` — PASS, 24/24 (20 previous + 4 new).
- `test_map_authority.py` — PASS, 17/17.
- `test_map_authority_notify.py` — PASS, 6/6.
- `map-git diff --check` — PASS, clean.

**Updated file set and checksums** (supersedes the "unchanged since
damo-nivo" table above — the patch has now genuinely changed and needs a
fresh review, not a re-verification of the original):

| File | sha256 (post-rework) |
|---|---|
| `MAP_System/db/claims.py` | `25de53578a3395cee288271acb3fbb0899f6de9d3694b37b0fdc9e53baf47c92` |
| `MAP_System/scripts/context_rotation.py` | `09329b18fc23b8a95158bed8cf5609d567e18538a547af2099ec353f60785f85` |
| `MAP_System/scripts/map_authority.py` | `6c8e71c585254d22c373f936267c61c4f8169f23cc4b0941ab9ef40f9d5acf5e` |
| `MAP_System/tests/test_context_rotation.py` | `e987c0881eec7d1e0729c6f51bb4007d4a862b50035fa4cdc8633409d038e91e` |
| `MAP_System/migration/schema.sql` | `4d6f8ee5d9a2af9bc99d2cd4cd3af5e29f58ee6dc24b4dba1f123df5f9b9b3f4` (new — added the `rotation_transfers` table) |

## Transaction-boundary rework (2026-07-29, attempt 3, after Smalls-side
## codex-lab-vumo's fresh rereview — CHANGES_REQUESTED)

The arbitrary-row-restore flaw was confirmed fixed. One new REQUIRED
finding, precise and narrow: `transfer_rotation_claims()` still read the
pre-transfer snapshot rows (`old_row`, `replacement_row`, each `task_row`)
*before* `BEGIN IMMEDIATE`. A concurrent authority-side writer could change
one of those rows between the SELECT and the lock; if this finalize later
rolled back, `restore_rotation_claims()` would restore the stale, pre-lock
snapshot and silently overwrite that intervening legitimate write. This
does not reopen the arbitrary-JSON hole (the transfer_id binding still
holds) — it's a separate atomicity gap in what gets recorded as the
rollback snapshot in the first place.

**Fix**: moved `conn.execute("BEGIN IMMEDIATE")` to immediately after
`_ensure_rotation_transfers_table(conn)` and before any of the
agents/tasks SELECTs. The snapshot is now read under the same write lock
as the transfer itself, so no writer can interleave between "what we'll
restore to" and "what we actually transferred." (The idempotent
`CREATE TABLE IF NOT EXISTS` schema-self-heal call stays outside the
transaction, per vumo's own alternative — DDL and an explicit `BEGIN
IMMEDIATE` transaction don't mix cleanly in SQLite, and table creation
doesn't participate in the agents/tasks race being closed.)

**New test**: `test_transfer_rotation_claims_locks_before_reading_snapshot_rows`
— traces the actual sequence of SQL statements sqlite3 executes (via a
tracing `sqlite3.Connection` subclass installed as the connect factory) and
asserts every agents/tasks snapshot `SELECT` occurs after `BEGIN
IMMEDIATE` in call order. This proves the statement ordering directly
rather than simulating real thread timing — under SQLite's locking
semantics, correct ordering *is* the atomicity guarantee, and this test
would have failed against the pre-fix code (its SELECTs really did run
before BEGIN IMMEDIATE).

**Re-verification after this rework** — all independently rerun:
- `py_compile` on both touched files — PASS.
- `test_context_rotation.py` — PASS, 25/25 (24 previous + 1 new).
- `test_map_authority.py` — PASS, 17/17.
- `test_map_authority_notify.py` — PASS, 6/6.
- `map-git diff --check` — PASS, clean.

**Updated checksums** (only the two files this attempt touched changed):

| File | sha256 (post attempt-3 rework) |
|---|---|
| `MAP_System/db/claims.py` | `71a2627eaff2f7a2c160f3c89b09947ea012c628e13ca775a126eb4bb5bab839` |
| `MAP_System/tests/test_context_rotation.py` | `19bb1d2092ff3c2cbbb5a306bbf414b10d3872a95caeedf1e551f400e338cfad` |

(`context_rotation.py`, `map_authority.py`, and `schema.sql` are unchanged
from the attempt-2 hashes recorded above — this rework was kept narrow, per
instruction.)

## What has not happened yet

Per TASK-307's remaining acceptance criteria, none of the following are
done: independent functional review, independent security-framed review,
checksum-staged deployment to Smalls, or post-deployment verification that
register-agent/rotation-transfer/rotation-restore actually succeed against
live RUKI. This task explicitly excludes fixing the separate `task
approve`/review-artifact-availability problem (1b), any manual TASK-305/306
transition, and any direct SQL against `map.db`. No deployment happens
before both reviews approve.

## Post-original-approval currency note (2026-08-10, claude-lab-sumi)

Found while writing TASK-307's release checklist: this file's own header
said review was "not yet performed" and "nothing deployed," which appeared
to contradict TASK-307's `APPROVED` status. Checked `events.jsonl`'s full
TASK-307 history rather than trusting either the stale header or the bare
status field: two further rework rounds occurred after this file's header
was written (security findings from `codex-lab-vumo`'s pre-deploy and
re-review passes — unbound `rotation-restore` row state, then a
non-atomic snapshot-before-lock ordering bug), each fixed and resubmitted,
with final `APPROVED` recorded 2026-07-29T18:33:52Z. The header text just
never got updated after that - a currency gap, not a false approval.

Independently confirmed the underlying code is genuinely sound, not just
approved on paper: `MAP_System/tests/test_context_rotation.py` (25/25
passing this session) specifically covers the exact findings from both
rework rounds, including `test_transfer_rotation_claims_locks_before_reading_snapshot_rows`
(round 3's atomicity fix) and `test_restore_rotation_claims_rejects_unknown_transfer_id_and_mutates_nothing`
/ `test_rotation_restore_gateway_operation_rejects_the_old_row_json_shape`
(round 1's binding fix). Live evidence from this session also directly
exercised the deployed gateway successfully: `shared/context-continuity.md`
records 30 finalized context-rotations as of 2026-08-10, 5 of them in the
last hour, each requiring a working `register-agent`/`rotation-transfer`
round-trip against the live Smalls authority host.
