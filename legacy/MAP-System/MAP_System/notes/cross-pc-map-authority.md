# Cross-PC MAP database authority

RUKI is the sole writable authority for the production
`MAP_System/map.db`. KUDU keeps a read-only, periodically refreshed mirror.
Agents on either PC therefore see one task board instead of creating divergent
claims and task histories.

## Modes

- `standalone` is the default when `~/.config/map-authority.json` is absent.
  Installation behavior remains the same as before this feature.
- `authority` owns the writable database and runs the existing watcher and
  maintenance services.
- `mirror` disables those local writers, refreshes from the authority through
  `map-authority-mirror.timer`, and sets the installed database mode to `0444`.

Example authority configuration:

```json
{"mode":"authority"}
```

Example mirror configuration:

```json
{
  "mode": "mirror",
  "authority_host": "192.168.1.153",
  "authority_user": "home",
  "authority_key": "/home/mellow/.ssh/id_ed25519_map_authority"
}
```

## Restricted SSH channel

The mirror uses a dedicated public key whose `authorized_keys` entry forces
`map-authority gateway` and applies OpenSSH's `restrict` option. The key does
not provide an interactive shell, port forwarding, agent forwarding, X11
forwarding, or arbitrary command execution. The gateway accepts a bounded,
versioned base64-encoded JSON request and dispatches only these operations:

`route`, `task`, `claim`, `heartbeat`, `claim-review`, `get-open-review`,
`release-review`, and `snapshot`.

`task` accepts only known `map_task.py` verbs and rejects every canonical-path
override. Commands are executed as argument arrays, never through a shell.

## Agent commands on KUDU

```sh
map-authority route
map-authority task show TASK-299
map-authority claim TASK-299 agent-name
map-authority heartbeat TASK-299 agent-name
map-authority claim-review TASK-299 reviewer-name
map-authority get-open-review TASK-299
map-authority release-review TASK-299 reviewer-name APPROVED
map-authority sync
map-authority status
```

The installed Codex lab prompt identifies a mirror host and directs the agent
to these commands. `ai route` also delegates to the authority automatically.

## Snapshot safety and failure behavior

The authority creates the database with SQLite's online backup API, bundles it
with canonical task/status/workflow mirrors, and attaches a size and SHA-256
manifest. KUDU rejects unknown archive members, links, traversal paths,
duplicates, oversize expansion, membership mismatches, and checksum failures.
It fully stages every mirror file before replacing anything, records the old
version of every target, and atomically replaces `map.db` last after moving old
SQLite sidecars out of the way. If any replacement fails, it rolls back every
changed mirror and restores the old database and sidecars. A failed connection
or validation leaves the last good mirror in place.
Sync refuses to proceed while local writer services are active.

The mirror timer begins 30 seconds after login/boot and refreshes once per
minute. User lingering must remain enabled for boot-time user services.

`map-authority-sync` wraps each timer refresh with a non-AI connection
watchdog. A failed connection, authority error, or rejected snapshot is
recorded in `~/.local/state/map-authority/health.json`. The watchdog retries
every minute and uses `notify-send` to show a critical desktop notification
once the graphical session is available. Repeated alerts are limited to once
per 30 minutes, and the first successful sync afterward sends one recovery
notification. It does not open the Command Center UI, start Codex, or invoke a
local LLM.

## Recovery

Before first activation, preserve each PC's database, WAL, and SHM files in a
timestamped backup directory. To return a host to standalone mode:

1. Stop and disable `map-authority-mirror.timer`.
2. Change its configuration to `{"mode":"standalone"}` or remove the file.
3. Restore a chosen database backup, make it owner-writable, and run
   `./install-map-system.sh --yes` to re-enable local services.

Do not promote both databases to writable authority. Choose one recovery
point, verify it, and keep the other host read-only until convergence is
confirmed.
