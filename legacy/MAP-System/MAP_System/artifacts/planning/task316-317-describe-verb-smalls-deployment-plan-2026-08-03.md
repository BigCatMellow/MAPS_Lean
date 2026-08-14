# TASK-316/317 — describe verb Smalls deployment plan (DRAFT, NOT EXECUTED)

- date: 2026-08-03
- author: helper-fix-authority-316-bume
- status: plan only — nothing below has been run against Smalls
- modeled on: TASK-308's deployment of the TASK-307 gateway patch
  (`MAP_System/artifacts/operations/gateway-rotation-ops-deployment-2026-07-29.md`,
  same bar: pre-write backup, staged checksum verification, recoverable
  activation, focused tests, live probes, durable evidence, independent
  review of the deployment itself)
- reviewed content going in: TASK-317 (map_task.py `describe` verb +
  `claims.describe_task`) — approved by helper-review-task316-317-zinu,
  clean, no findings. TASK-316 (`active_local_writer_services()` narrowing +
  TOCTOU fix in `map_authority.py`) — approved by zinu on follow-up pass, no
  REQUIRED/BLOCKER findings.

## Why one deployment covers two tasks

`MAP_System/scripts/map_authority.py` carries both TASK-316's writer-service
fix and TASK-317's one-line `ALLOWED_TASK_VERBS` addition (`"describe"`),
because both are uncommitted edits to the same file on this Biggie
checkout. They can't be shipped independently — deploying the file ships
both. Both are independently reviewed and approved by zinu, so there is no
content risk in shipping them together, but it means TASK-316's own formal
SQLite lifecycle (claim → submit → approve, citing zinu's already-completed
review) only becomes *possible* after this deployment, not before — per
coordinator's step 4, that happens immediately after live verification
below, as part of this same operation rather than a separate one.

## Open prerequisite — who can actually execute this

The only Smalls credential available to me (`~/.ssh/id_ed25519_map_authority`,
`home@100.127.80.108`) is a forced-command key: the SSH `authorized_keys`
entry (and, redundantly, the Claude Code permission classifier — confirmed
by testing) restrict it to invoking `map-authority <request>` only. It
cannot `scp`/write arbitrary files or open a general shell on Smalls. TASK-308's
deployment was executed by claude-lab-nene, presumably from a session with
real Smalls-side access (matching how codex-lab-vumo reviewed "Smalls-side"
in TASK-307's rework record) — a different credential/session type than
what I hold as a Biggie gateway helper.

**I cannot execute the write steps below myself with current access.** This
plan is written so whoever *can* (an agent with real Smalls shell access, or
you) can execute it directly, or so the access gap itself can be routed
first. Flagging rather than guessing at a workaround, per AGENTS.md's
"Remote MAP authority failures" guidance.

## Step 1 — Pre-write record (before touching Smalls)

Record the exact reviewed/approved SHA-256 values from this Biggie checkout
(the reviewed state zinu approved) before any Smalls write:

| File | sha256 (Biggie, reviewed/approved) |
|---|---|
| `MAP_System/scripts/map_authority.py` | `56d84bf306195f100543b014e0f8188f2527f0321a65cf1b620c548486ee6580` |
| `MAP_System/scripts/map_task.py` | `809abf35490eca558d3b1ce8840ec5c9793369532a849f2a681a857e1fda892c` |
| `MAP_System/db/claims.py` | `62275a9557b265425bb6921bc2a3bc580606df9012ede30170fb4374cf62f547` |
| `MAP_System/scripts/run_tests.sh` | `ac76677dc7df22c95f1c72e6ae5ebe369c21e52fdb3b8df58af47e39af4f6fdb` |
| `MAP_System/tests/test_map_task_describe.py` (new file) | `e2855bb8e1bcf5d5feaf02ad6f599dbfe8d6a8cbb5ad8ff2bd55e5d9cb4c49eb` |
| `MAP_System/tests/test_map_authority.py` | `047363a0b349395e59ea8c28fa4f188690faa4231a53374aa01c8fd4a523411f` |

These six files are the complete reviewed change set — nothing else moves.

## Step 2 — Confirm destination identity

Before any write: confirm the target is genuinely Smalls/RUKI (not a wrong
host), matching TASK-308's own "confirm destination hostname" criterion —
e.g. `ssh <real-access-key> home@100.127.80.108 'hostname; hostnamectl'` (or
equivalent) and cross-check against the known RUKI identity recorded
elsewhere (TASK-308's record used `192.168.1.153`/hostname `MediaCenter`;
this session's config resolves the same authority host via Tailscale at
`100.127.80.108` — confirm these are the same box before proceeding, not
assumed).

## Step 3 — Backup every target file on Smalls

Timestamped backup of Smalls' current copy of all six files (even the new
test file's containing directory, in case of an unrelated same-name
collision) before any write. Record backup location and each pre-write
hash. Never touch `map.db` directly, authority topology, credentials, hcom
state, runtime state, or any unrelated file.

## Step 4 — Stage and verify

Copy only the six reviewed files into a staging location on Smalls (not
their live paths yet). Hash every staged file and prove each equals the
Biggie value in the Step 1 table exactly — byte-for-byte, not "close
enough." Any mismatch aborts before touching a live path.

## Step 5 — Compile and test in staging

- `python -m py_compile` on all five touched `.py` files.
- Run, against the staged copies (or a scratch `--db` pointed at a disposable
  SQLite file, matching how `test_map_task_describe.py`'s own CLI tests
  work): `test_map_authority.py` (41/41 expected), `test_map_task_describe.py`
  (10/10 expected), and the sibling lifecycle-verb suites this change sits
  next to — `test_map_task_amend_criteria.py`, `test_map_task_extend_attempts.py`,
  `test_map_task_retire.py`, `test_map_task_add_output_path.py` — to catch
  any interaction with Smalls' actual `ALLOWED_TASK_VERBS`/`map_task.py`
  state that a Biggie-only test run couldn't see.
- Only activate if every check passes.

## Step 6 — Recoverable activation

Atomically move each staged file into its live path (temp-file-plus-rename
per file, same pattern `map_authority.py`'s own `stage_file`/`atomic_write`
already use — don't leave a live path in a half-written state at any point).
Keep the Step 3 backups until Step 7 passes.

## Step 7 — Post-deploy live verification (doubles as TASK-316's unblock)

Per coordinator's step 4, the live-verification step *is* the action that
unblocks TASK-316, not a separate no-op probe:

1. `map-authority task describe --help` (or equivalent) resolves on Smalls —
   proves the verb is live.
2. From Biggie, through the now-working gateway:
   `map-authority task describe TASK-316 --description "..." --actor helper-fix-authority-316-bume --reason "..."`
   — promotes TASK-316 to READY (description already drafted in the earlier
   handoff attempt).
3. `map-authority claim TASK-316 helper-fix-authority-316-bume` — proves
   `describe`'s promotion produced a genuinely claimable task, not just a
   status flip.
4. `map-authority task submit TASK-316 --actor helper-fix-authority-316-bume`
   — submits TASK-316 for its own (already-complete) independent review
   record, citing zinu's existing review rather than requesting a fresh one.
5. Confirm `map-authority route` / mirror freshness are unaffected
   (`FRESH`, `topology_valid: true`) — this deployment must not itself
   regress the very freshness contract TASK-316 was fixing.

If any of 1–5 fails, roll back (Step 8) rather than leaving Smalls in a
partially-deployed state.

## Step 8 — Rollback (if any step 5 or 7 check fails)

Restore every file from its Step 3 backup, atomically, in reverse order of
activation. Re-run Step 5's test set against the restored files to confirm
Smalls is back to its known-good pre-deployment state. Record the failure
and rollback outcome in Step 9's evidence artifact regardless of outcome.

## Step 9 — Durable evidence

Record in `MAP_System/artifacts/operations/describe-verb-smalls-deployment-<date>.md`
(matching `gateway-rotation-ops-deployment-2026-07-29.md`'s shape): deployed
paths, before/after hashes, backup/rollback location, every command and its
result, TASK-316's post-deployment claim/submit outcome, and rollback
outcome if it was needed.

## Step 10 — Independent review of the deployment itself

Per TASK-308's own acceptance criteria, "a different core agent performs
final functional and security-framed review before completion" — this is a
review of the *deployment execution* (did it actually match this plan, were
backups real, do live checks hold), separate from zinu's already-complete
review of the *code*. Not self-reviewable by whoever executes Steps 1–9.

## Explicitly out of scope

- Any change to `limit_watcher.py` (stays out per coordinator's earlier
  direction on TASK-316).
- Any manual `map.db` edit, credential change, or hcom/runtime state touch.
- Fixing the separate cross-host code-publication gap in general (why
  Biggie and Smalls drift at all) — TASK-315 owns that; this plan only
  moves the one reviewed, approved change set needed to unblock TASK-316.
