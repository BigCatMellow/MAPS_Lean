# MAP 2 Phase 0 Trustworthy Authority Baseline

- task_id: TASK-321
- status: implemented_pending_independent_review
- owner: rotation-replacement-miro-fela
- prepared_at: 2026-08-10T03:23:30Z
- authority_host: Smalls
- mirror_host: Biggie
- evidence_type: recovery_baseline

## Authority invariant

- Smalls is the sole writable MAP lifecycle authority.
- Biggie holds a read-only mirror and uses the allowlisted `map-authority`
  gateway for lifecycle changes.
- The fallback added here observes local Biggie process activity only. It does
  not write lifecycle state, weaken database permissions, or create a second
  authority path.

## Reproduction

### Biggie host probe

Command run outside the Codex sandbox:

```bash
systemctl --user is-active map-rns-watcher.service \
  map-command-center-maintenance.service \
  map-command-center-maintenance.timer
```

The host user bus is reachable. A sync attempted during a real overlapping
watcher-write window failed closed with:

```text
map-authority error: local writer services must be disabled before mirror sync: map-rns-watcher.service
```

After the 15-second collision window cleared, the normal notifier path
installed 316 files and recorded authority revision:

```text
sha256:a8eb7144c572909111a7be60c04c6dd06518bb748a9c936a588edfef72dda5e7
```

### Codex sandbox probe before the fix

```bash
systemctl --user is-active map-rns-watcher.service \
  map-command-center-maintenance.service \
  map-command-center-maintenance.timer
```

Result:

```text
Failed to connect to bus: No data available
```

That inability to query the host user bus was incorrectly represented as an
invalid topology even when no writer collision existed.

The same sandbox can read the unified cgroup record:

```bash
sed -n '1,20p' \
  /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice/map-rns-watcher.service/cgroup.events
```

Observed:

```text
populated 1
frozen 0
```

## Implementation

`MAP_System/scripts/map_authority.py` now:

1. Uses `systemctl --user` as the primary probe.
2. Invokes the cgroup-v2 fallback only for the narrow diagnostic
   `Failed to connect to bus`.
3. Reads `cgroup.events` for the two process-bearing writer services under the
   current user's systemd `app.slice`.
4. Treats malformed or unreadable cgroup evidence, a missing cgroup-v2 mount,
   or an absent current-UID user-service cgroup root as an error rather than a
   clean topology.
5. Continues treating a populated maintenance-service cgroup as an active
   writer.
6. Continues applying the 15-second mirrored-file quiet window to the
   always-on RnS watcher.
7. Reports `writer_service_probe_source` as `systemctl` or
   `cgroup_v2_fallback` so every clean writer decision remains auditable; a
   failed probe reports `unavailable` and still invalidates topology.

The maintenance timer is processless and is not inferred from cgroup absence;
its process-bearing oneshot target,
`map-command-center-maintenance.service`, remains explicitly checked. When the
user bus is available, the existing timer check is unchanged.

## Rotation and mirror reconciliation

- Frozen snapshot:
  `MAP_System/handoffs/STATE_SNAPSHOT-codex-lab-miro-20260810T030102Z.yaml`
- Verified SHA-256:
  `c2db1cffd66d7c1a93b857a16ca8cdb084515b3d849fc600fa799895b0696a11`
- Replacement identity:
  `rotation-replacement-miro-fela`
- Replacement session:
  `019fe99f-2219-7c60-b304-53c2dcfccfca`
- Finalized at: `2026-08-10T03:03:44Z`

Finalize correctly transferred the canonical Smalls owner and claim, but its
first exported task JSON and graph remained on `codex-lab-miro`. The mismatch
was repaired through a sanctioned same-owner `reassign-owner` lifecycle call,
which re-exported Smalls' canonical mirrors without changing accountability,
followed by a host-side `map-authority sync`. Direct task-file editing was not
used. `validate_task_mirrors.py` then passed.

## Verification

Focused tests:

```bash
MAP_System/.venv/bin/python -m unittest \
  MAP_System.tests.test_map_authority \
  MAP_System.tests.test_map_authority_notify
```

Result after security-review remediation: `Ran 59 tests ... OK`.

The added cases prove:

- a quiet populated RnS watcher does not create a false sandbox failure;
- a recent watcher write remains blocking;
- a populated maintenance writer remains blocking;
- malformed cgroup evidence fails closed; and
- a current-process UID that does not identify an existing user-service cgroup
  root fails closed instead of appearing writer-free; and
- unrelated `systemctl` errors cannot trigger the fallback; and
- both primary and fallback paths disclose their evidence source, including in
  authority status output.

Post-fix sandbox status after the collision window:

```text
freshness: FRESH
topology_valid: true
local_writer_services: []
writer_service_probe_source: "cgroup_v2_fallback"
writer_service_probe_error: ""
```

Post-fix sanctioned route after the collision window:

```text
next_route: review
authority.freshness: FRESH
authority.topology_valid: true
authority.local_writer_services: []
authority.writer_service_probe_source: "cgroup_v2_fallback"
```

Immediately after a mirrored-file replacement, the route continued to report
the watcher as active until the 15-second window cleared. That transient is
expected fail-closed behavior and demonstrates that the fallback did not turn
an overlapping write into a clean result.

## Review requirements

- Functional review must be performed by a core agent other than the task
  owner.
- A separate security-framed pass must examine cgroup path trust, malformed
  input behavior, writer/timer coverage, collision preservation, and whether
  any probe error can be misclassified as clean.
