# Cross-PC MAP authority activation — 2026-07-28

## Outcome

- RUKI (`home@192.168.1.153`, hostname `MediaCenter`) is the only writable
  production MAP SQLite authority.
- KUDU (`mellow@192.168.1.177`) is a read-only mirror refreshed once per
  minute through `map-authority-mirror.timer`.
- KUDU lifecycle and routing commands use a dedicated Ed25519 key restricted
  by an OpenSSH forced command to the allowlisted `map-authority gateway`.
- The separate administrative SSH key remains functional for deliberate
  source maintenance.

## Preserved recovery points

- KUDU:
  `/home/mellow/MAP-convergence-backups/20260728T205100Z-pre-authority-kudu`
- RUKI:
  `/home/home/MAP-convergence-backups/20260728T205100Z-pre-authority-ruki`
- RUKI authorized-keys backup:
  `/home/home/.ssh/authorized_keys.pre-map-authority-20260728T205100Z`

No convergence or activation backup was removed.

## Review and test evidence

The visible independent reviewer
`task299-security-review-todo:RUKI` found and caused correction of:

1. WAL/SHM rollback on a failed final database swap.
2. Full canonical-mirror rollback on any intermediate swap failure.
3. Installer fail-open behavior for unsupported authority mode strings.

The reviewer returned PASS on the corrected revision after:

- 17/17 focused `test_map_authority` tests passed.
- Direct database-swap and mirror-swap fault-injection tests passed.
- The installer unsupported-mode integration test passed.
- Shell syntax checks passed.

Additional compatibility checks for map-task lifecycle and review claims
passed before activation.

## Live verification

- RUKI status: `mode=authority`, database writable, watcher active and
  enabled, maintenance timer active and enabled, mirror timer disabled.
- KUDU status: `mode=mirror`, database not writable, watcher and maintenance
  disabled/inactive, mirror timer active and enabled.
- User lingering is enabled on both PCs, so the user services start without
  requiring a terminal to remain open.
- First and subsequent snapshots installed 294 validated files.
- KUDU `MAP_System/map.db` is mode `0444`; WAL/SHM sidecars are absent after
  sync.
- A guarded production connection raises `RemoteAuthorityRequired` on KUDU.
- A raw SQLite update fails with `attempt to write a readonly database`.
- A remote `heartbeat TASK-299 codex-live` succeeded and was visible after
  the next mirror sync.
- The authority key returned `invalid forced command` for an attempted
  arbitrary `id` command.
- The timer-triggered sync completed with `Result=success`,
  `ExecMainStatus=0`, and scheduled its next one-minute run.

## Dedicated key fingerprint

`SHA256:0XrQcJlJFoEgNs79smu/sU0dogqAVboJ/yxLvdZcQPQ`

Only the fingerprint is recorded here; no private key or shared secret is
included.
