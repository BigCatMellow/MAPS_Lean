# Code-sync timer — both boxes fast-forward from origin

- date: 2026-08-03
- author: claude-lab-luzo (coordinator)
- motivation: TASK-316/317 sat fully reviewed and approved but undeployed
  because Biggie and Smalls are independent git checkouts with no sync
  between them -- a fully reviewed fix had to wait on someone finding it,
  understanding it, and manually shipping it. This does for the *code*
  what `map-authority-mirror.timer` already does for `map.db`: keep both
  checkouts converged automatically, conservatively (fast-forward only,
  never merges/rebases, always skips rather than risks clobbering local
  work).

## Biggie: done, live

- `/home/mellow/.local/bin/map-code-sync` (script, executable)
- `/home/mellow/.config/systemd/user/map-code-sync.service`
- `/home/mellow/.config/systemd/user/map-code-sync.timer` (`OnBootSec=45s`,
  `OnUnitActiveSec=300s`, enabled + started)

Behavior: skips (exit 0, no error) if the working tree has any local
changes, or if HEAD isn't on `agent/biggie-smalls-convergence`. Otherwise
fetches `origin` and fast-forwards only; if history has diverged (can't
fast-forward), it fails loudly (exit 1, visible in
`systemctl --user status map-code-sync.service` / journal) rather than
merging or rebasing automatically.

Verified: ran once at enable time, correctly skipped (Biggie's tree had
unrelated uncommitted files at that moment) rather than doing anything
risky.

## Smalls: not done — needs someone with real Smalls access

I only have the restricted `map-authority` gateway key from this seat, which
can't write files or open a shell on Smalls (same access gap TASK-316/317's
deployment hit). This needs to be applied by whoever has genuine Smalls
access. Adjust only the user/path (Smalls' repo lives at
`/home/home/Projects/MultiAgentProject` per `AGENTS.md`'s canonical-repo
note, user `home` not `mellow`) -- logic is identical.

**`/home/home/.local/bin/map-code-sync`** (chmod +x):

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO="/home/home/Projects/MultiAgentProject"
BRANCH="agent/biggie-smalls-convergence"

cd "$REPO"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "map-code-sync: skipped -- working tree has local changes, not touching it"
  exit 0
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$current_branch" != "$BRANCH" ]]; then
  echo "map-code-sync: skipped -- on branch '$current_branch', expected '$BRANCH'"
  exit 0
fi

git fetch origin "$BRANCH"

if git merge-base --is-ancestor HEAD "origin/$BRANCH"; then
  if [[ "$(git rev-parse HEAD)" == "$(git rev-parse "origin/$BRANCH")" ]]; then
    echo "map-code-sync: already up to date"
    exit 0
  fi
  git merge --ff-only "origin/$BRANCH"
  echo "map-code-sync: fast-forwarded to $(git rev-parse --short HEAD)"
else
  echo "map-code-sync: local branch has diverged from origin/$BRANCH -- not merging/rebasing automatically, needs manual resolution" >&2
  exit 1
fi
```

**`/home/home/.config/systemd/user/map-code-sync.service`**:

```ini
[Unit]
Description=Fast-forward the MultiAgentProject code checkout from origin
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/home/Projects/MultiAgentProject
Environment=PATH=/home/home/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/home/.local/bin/map-code-sync
```

**`/home/home/.config/systemd/user/map-code-sync.timer`**:

```ini
[Unit]
Description=Periodically fast-forward the MultiAgentProject code checkout

[Timer]
OnBootSec=45s
OnUnitActiveSec=300s
Persistent=true
Unit=map-code-sync.service

[Install]
WantedBy=timers.target
```

Install: `systemctl --user daemon-reload && systemctl --user enable --now map-code-sync.timer`.

## After Smalls has this running

TASK-316/317's fix (already committed and pushed to
`origin/agent/biggie-smalls-convergence`, commit `8699411`) will land on
Smalls automatically within 5 minutes of the timer being enabled. At that
point, follow the already-drafted
`task316-317-describe-verb-smalls-deployment-plan-2026-08-03.md` Step 7
onward to activate it (the `describe` verb still needs the existing
install/activation step for privileged code -- code-sync only keeps the git
checkout current, it does not itself deploy privileged binaries under
`~/.local/bin/`).
