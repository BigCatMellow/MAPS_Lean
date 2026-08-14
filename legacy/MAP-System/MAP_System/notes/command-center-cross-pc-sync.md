# CommandCenterUI Cross-PC Sync Protocol (Biggie → Smalls)

TASK-306. This note defines the protocol for aligning Smalls' installed
CommandCenterUI with Biggie's live-tested, template-versioned bundle. It is a
**protocol document only** — no Smalls-side execution has happened under
this task. Executing it against Smalls is deferred to a follow-up task that
first confirms Smalls' exact host/device identity and runs a dry-run.

## Scope and what this is not

This protocol moves the CommandCenterUI **program bundle** (the managed
files listed in `MAP_System/scripts/command_center_version.py`'s
`MANAGED_FILES`) from Biggie to Smalls. It is unrelated to, and must never be
confused with, MAP task/database authority:

- RUKI remains the sole writable `map.db` authority (see
  `MAP_System/notes/cross-pc-map-authority.md`). This protocol never writes
  to `map.db`, never calls `map_authority.py`'s task/claim/review verbs, and
  never changes which host is the MAP authority.
- It never touches host credentials, SSH keys, hcom runtime state, or
  anything under `runtime/` (see `command_center_version.py`'s
  `EXCLUDED_RUNTIME_PATTERNS`).
- Direction is locked: **Biggie is always the source, Smalls is always the
  destination.** Nothing in this protocol reads Smalls' CommandCenterUI as
  authoritative or pulls changes from Smalls back to Biggie or the repo.

## Preconditions (all required before any write to Smalls)

1. **Exact destination identity confirmed.** The target host, SSH user, and
   absolute install path (expected: `home@<Smalls-IP>:~/Projects/CommandCenterUI`,
   per `MAP_System/artifacts/operations/cross-pc-convergence-2026-07-28.md`'s
   recorded identity) must be explicitly confirmed for that run, not assumed
   from a prior session's notes. Never target a host discovered by scanning
   or inferred from a hostname guess.
2. **Clean-or-preserved destination state.** Before writing, run
   `command_center_version.py verify --bundle-root <Smalls path> --manifest
   <Smalls' last-known manifest>` over SSH (read-only) to determine whether
   Smalls has any local drift from its last known-good state. If it does,
   stop and require an explicit operator decision: overwrite (with the
   backup below as the safety net) or preserve (copy Smalls' drifted files
   aside before proceeding). Never silently overwrite undeclared local
   changes.
3. **Pre-write backup.** Copy Smalls' entire current CommandCenterUI managed
   bundle (not just the files about to change) to a timestamped backup
   location on Smalls before any write. Record the backup path in the
   deployment's evidence artifact. No backup, no write.
4. **Dry-run review.** Compute the exact set of files that would change
   (`command_center_version.py verify` against Biggie's current manifest
   shows exactly this: missing/changed/extra) and have that plan reviewed —
   by the operator directly, or by an independent reviewer if run
   unattended — before touching Smalls. The dry-run output is evidence, not
   a formality: paste it into the deployment record.

## Execution (only after all four preconditions are met)

5. **Staged transfer.** Copy the managed bundle files to a staging directory
   on Smalls (not directly into the live install path) over the existing
   restricted, forced-command SSH channel — the same security posture
   already established for `map-authority` (see
   `MAP_System/notes/cross-pc-map-authority.md`), not a new general-purpose
   transfer mechanism. Do not invent a new open SSH path or listener for
   this.
6. **Staged checksum verification.** Run `command_center_version.py verify
   --bundle-root <staging dir> --manifest <Biggie's manifest>` against the
   staged copy before activating anything. A staged copy that fails
   verification is discarded, not activated, and does not touch the live
   install path.
7. **Atomic, recoverable activation.** Swap the verified staged directory
   into the live install path as a single atomic operation (rename-based
   swap, not an in-place file-by-file overwrite), so a failure mid-activation
   cannot leave a half-updated bundle. Keep the pre-write backup available
   for immediate rollback; do not delete it as part of activation.
8. **Post-deploy smoke and parity check.** After activation, run
   `command_center_version.py verify --bundle-root <Smalls live path>
   --manifest <Biggie's manifest>` again against the now-live install (proves
   parity), and start the app (`run-command-center-app.sh --server-only` or
   equivalent) to confirm it actually serves `orchestrator.html` and responds
   on its expected port (proves the deployment works, not just that the
   files match). Record both results in the deployment evidence artifact.

## Rollback

If verification, smoke check, or anything else fails after activation:
restore the pre-write backup from step 3 as a single atomic swap back into
the live install path, then re-run the post-deploy parity check against the
restored backup to confirm the rollback itself succeeded. A rollback that
cannot be verified is treated as a new incident, not a completed rollback.

## Evidence

Every real execution of this protocol produces a dated artifact under
`MAP_System/artifacts/operations/` recording: the confirmed destination
identity, the pre-write drift check result, the backup location, the
dry-run plan, the staged verification result, the activation method, the
post-deploy verify + smoke result, and (if used) the rollback verification.
`MAP_System/artifacts/operations/command-center-cross-pc-alignment-2026-07-29.md`
is TASK-306's own evidence record for the Biggie-side (template-import) half
of this work; it explicitly does not claim any Smalls-side step above has
been executed.
