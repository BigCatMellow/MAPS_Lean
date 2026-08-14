# Cross-PC MAP And Command Center Convergence

- task_id: TASK-298
- status: implemented_pending_review
- operator_authority: KUDU `/home/mellow/Projects/MultiAgentProject` is the source snapshot for this convergence
- source_device: KUDU (`192.168.1.177`)
- destination_device: RUKI / MediaCenter (`192.168.1.153`)
- activated_destination: `/home/home/Projects/MultiAgentProject`
- activated_head: `c70282616a7cb7640a5b3b207fc83e91ff9987d3`

## Outcome

RUKI now runs the same MAP System and Command Center program snapshot as KUDU.
The prior RUKI repository was preserved by rename rather than deleted. The
installer regenerated RUKI's launchers, desktop entries, Command Center UI,
user services, and MAP virtual environment from the activated `Source/` tree.

This convergence establishes one program version at the recorded point in
time. It does not make two independently writable SQLite task databases safe.
Central task-state authority is the next architectural step; until then, agents
must not treat simultaneous claims in the two local database copies as atomic.

## RUKI Preservation Evidence

The pre-convergence repository remains intact at:

`/home/home/Projects/MultiAgentProject.pre-kudu-20260728T202400Z`

Additional recovery artifacts are at:

`/home/home/MAP-convergence-backups/20260728T201700Z`

The artifact set captured the prior Git history, tracked working-tree patch,
untracked files, MAP databases, branch, remotes, HEAD, and 30-path status
manifest.

| Artifact | SHA-256 |
|---|---|
| `repository-all-refs.bundle` | `a3b1f3de57d6ecb75516f20f2f8b8f1157a7314e06e91d43fd29c0038661e666` |
| `tracked-working-tree.patch` | `392ac6c312797c676c37e2dc7847f348677ac1b9b93681de49928cbc30ddaa1e` |
| `untracked-files.tar.gz` | `3770fc2b6e4e2a739bb86e1fe663bb5c8d3d3fc16006295796e07cb14ff15378` |
| `map-databases.tar.gz` | `c69d23eaf29471e6fe42dd586334f26c4ebf4bf219c787e8ea956f85f7af44c8` |

The activation script ran `sha256sum -c` successfully for all four artifacts
before renaming either repository.

## Transfer And Equality Evidence

- Transport: `rsync` over dedicated ED25519 key-only SSH.
- Staging path: `/home/home/Projects/MultiAgentProject.kudu-staging`.
- Initial transfer: 2,146 regular files; 171,521,039 bytes.
- Final reconciliation: 2,148 regular files; 171,521,560 bytes.
- Source and staged Git HEAD: `c70282616a7cb7640a5b3b207fc83e91ff9987d3`.
- Final checksum dry-run before activation: no itemized differences.
- Post-install checksum dry-run for non-host-local program files: no itemized
  differences.

Documented host-local exclusions:

- `.venv/`
- `.locks/`
- `logs/`
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- `map.db-shm`
- `map.db-wal`
- generated `MAP_System/runtime/*.json`
- `.git/index` during verification because `git status` refreshes it per host
- watcher-maintained agent availability/liveness files during post-install
  comparison

Tracked runtime documentation (`MAP_System/runtime/.gitignore` and
`MAP_System/runtime/README.md`) was included.

## Activation And Installation

All live RUKI agents were stopped or verified quiescent before activation.
Both MAP Rise & Shine watchers were paused for the final checksum pass.

Activation used two same-filesystem renames:

1. Existing RUKI repository to
   `/home/home/Projects/MultiAgentProject.pre-kudu-20260728T202400Z`.
2. Verified staging repository to
   `/home/home/Projects/MultiAgentProject`.

`Source/install-map-system.sh` was first run in dry-run mode, then applied with:

`--yes --skip-apt --skip-hcom --skip-wezterm`

Installer backups are at:

`/home/home/.local/state/map-install/backups/20260728-162342`

Validated launcher roots:

- `/home/home/.local/bin/ai-command-center-lab`
- `/home/home/.local/bin/ai-command-center-lab-codex`
- `/home/home/.config/wezterm/ai-command-center-lab.lua`

All resolve to:

`/home/home/Projects/MultiAgentProject/Source`

## Verification

- `hcom-relay.service`: active
- `map-rns-watcher.service`: active on both hosts after the sync window
- `map-command-center-maintenance.timer`: active on RUKI
- RUKI MAP runner: successful, loaded project `MAP-BOOTSTRAP-20260617`
- RUKI Command Center health:
  - Git: pass
  - Python: pass
  - hcom: pass
  - WezTerm: pass
  - Codex: pass
  - Claude: pass
  - Gemini: pass
  - Ollama: pass
  - MAP virtual environment: pass

## SSH Security

- Dedicated key:
  `SHA256:fRAp32AMtae88ymSzRj1jeNGX8qJy/jwjMR9vP+s4Oc`
- RUKI SSH service: enabled and active
- `PermitRootLogin no`
- `PasswordAuthentication no`
- `KbdInteractiveAuthentication no`
- `PubkeyAuthentication yes`
- `AllowUsers home@192.168.1.*`
- Non-key login test: rejected with `Permission denied (publickey)`.

A remote setup agent exposed the account's sudo password in an hcom-visible
command before being stopped. The credential is not reproduced here. The
operator was notified; the `home` account password must be rotated. Key-only
SSH reduces remote exposure but does not remove the need to rotate a password
that appeared in command/transcript history.

## Rollback

Do not remove either preserved path until functional and security reviews pass.

Rollback procedure on RUKI:

1. Stop Command Center agents and `map-rns-watcher.service`.
2. Rename the activated repository to a new failed-activation evidence path.
3. Rename
   `/home/home/Projects/MultiAgentProject.pre-kudu-20260728T202400Z`
   back to `/home/home/Projects/MultiAgentProject`.
4. Restore launcher/UI files from
   `/home/home/.local/state/map-install/backups/20260728-162342`, or rerun the
   restored repository's installer.
5. Restart the watcher and run the prior health checks.

No preserved repository or recovery artifact has been deleted.
