# Verified Context Rotation Guide

## Purpose

Context rotation reduces future prompt size and restores reasoning headroom
without treating chat history as durable memory. It does not refund tokens
already spent. Prompt caching can reduce price, but it does not remove context
window pressure.

The safety rule is simple: **checkpoint, verify, resume, then supersede**.
Never clear first and reconstruct later.

## Authority Invariant

Context rotation is session continuity, not promotion or role assignment.
`shared/project-brief.md` → `Operating Model` remains authoritative:
`bigboss`/operator → one designated coordinator per run → accountable task
owners and conflict-separated independent reviewers → bounded support.

- `prepare` freezes evidence; it transfers no authority.
- `ack` proves that a live replacement understands the exact snapshot; it
  transfers no authority.
- `finalize` transfers only the snapshot's explicit claims and obligations.
  It may continue a coordinator designation only when the snapshot explicitly
  records that existing designation and the operator has not revoked it.
- Rotation never creates operator, policy, task-owner, reviewer, release, or
  routing authority. Provider, model, session ID, and terminal presence remain
  runtime facts rather than governance roles.

## Threshold Policy

- Default hard threshold: 150,000 current-context tokens.
- Soft checkpoint: 120,000 tokens, or 60% of a known context window—whichever
  arrives first.
- Rotation: 150,000 tokens, or 75% of a known context window—whichever arrives
  first.
- Emergency: at 90% or on a runtime compaction warning, stop starting new work
  and prepare the snapshot immediately.

Use:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py advise \
  --agent <current-hcom-name>
```

The installed `limit_watcher.py` evaluates this status on every poll and sends
an hcom `inform` once when a live session crosses the soft checkpoint and once
when it crosses the rotation boundary. Its durable marker in
`agents/limit-watcher-state.json` is atomically committed immediately after a
successful send, before unrelated recovery work can block the poll; a new
below-threshold context clears the marker. The watcher only advises—the agent
must complete the verified protocol below, and it never launches a hidden
replacement or clears a transcript.

Codex exposes a current context estimate and window. Claude transcript usage is
different: cumulative cache-read totals repeatedly count prior prompts. MAP
uses only the latest successful Claude response's prompt-input footprint as an
estimate and labels it honestly. If no current-context estimate exists, the
tool returns `unknown`; it never invents a percentage.

## Snapshot Draft

Copy `workflow/templates/state_snapshot.yaml` and use snapshot version 2. The
draft must be `status: handing_off` and include:

- every task currently claimed by the old agent, exactly as SQLite records it;
- pending reviews, recent decisions/events, touched paths, active constraints,
  blockers, failed approaches, resume commands, and validation already run;
- a `rotation` block with the trigger, current estimate, threshold, compact
  summary, and first next action.

Do not add `integrity`; `prepare` generates it.

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py prepare \
  --agent <old-agent> --draft /tmp/context-snapshot.yaml
```

Prepare refuses an incomplete claim inventory. It freezes an immutable file in
`handoffs/` and updates `shared/context-continuity.md`. The master text is a
generated human view with embedded machine-readable state. SQLite/tasks remain
canonical; the ledger records their digest so disagreement is visible.

Multi-file atomicity is implemented as a commit-pointer protocol under
`.locks/context-rotation.lock`: the immutable snapshot is written first and the
master ledger last. A crash can leave an unreferenced snapshot, which is safe
raw evidence; it cannot make the ledger point at a missing snapshot.

## Replacement ACK

Start a fresh visible Codex or Claude session with a prompt naming the snapshot
path and SHA-256 printed by `prepare`. The replacement must read the snapshot,
the task record, and current runner state before acknowledging:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py ack \
  --old-agent <old-agent> \
  --replacement-agent <new-live-hcom-name> \
  --replacement-session <new-session-id> \
  --snapshot-sha256 <sha256-from-prepare>
```

ACK refuses the same identity, a non-live replacement, a replacement session
ID that does not match the live hcom roster, a wrong hash, snapshot tampering,
master-text edits, canonical task drift, or touched-path drift.

## Finalize

After the replacement reports that it understands the next action:

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py finalize \
  --old-agent <old-agent>
```

Finalize transfers exactly the snapshot's live claims to the replacement,
updates owner only when the old agent itself was owner, refreshes leases,
exports task and agent mirrors, marks the old identity
`inactive/session_superseded`, and commits the master ledger. If export or the
final master-ledger commit fails, SQLite and exported mirrors are restored and
the ledger remains at `acknowledged`, so retry or manual recovery is possible.
Immediately before mutation, finalize rechecks that the exact acknowledged
replacement identity and session are still live.

Only this successful finalization makes the replacement the continuity holder.
It does not broaden the authority or obligations named in the frozen snapshot.

Only after finalize succeeds should the old terminal/session be stopped.

## Drift Check

```bash
MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py validate
```

Before ACK, task or touched-path changes are blocking drift. After ACK/finalize,
the snapshot remains immutable history; later task progress is expected and is
not a permanent blocker. Snapshot hash or master-render drift always fails.
The generated master ledger itself is recorded as protocol-generated evidence,
not content-hashed into its own commit; its revision and deterministic render
are the integrity check, avoiding a self-referential false drift.

## Failure Recovery

- Prepare fails: fix the draft; keep working in the old session.
- Replacement cannot start: leave phase `prepared`; old session remains owner.
- ACK fails: reconcile the named drift. If the draft is stale, preserve and
  abandon the unacknowledged attempt, then prepare a new snapshot:

  ```bash
  MAP_System/.venv/bin/python MAP_System/scripts/context_rotation.py abandon \
    --old-agent <old-agent> --reason "<why this attempt is stale>"
  ```

  The old immutable snapshot moves into ledger history; it is not deleted.
- Finalize/export/master-commit fails: the command restores task/agent state
  and re-exports the restored view; retry after the underlying problem is fixed.
- Old session dies after prepare but before ACK: the snapshot and master ledger
  still preserve recovery context; an operator can start the replacement, but
  finalize remains checksum-gated.
