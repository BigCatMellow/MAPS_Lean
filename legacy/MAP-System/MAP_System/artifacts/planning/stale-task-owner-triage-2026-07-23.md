# Triage: Tasks Owned By Agents That No Longer Exist

- author: claude-lab-bima
- date: 2026-07-23
- directive: operator, 2026-07-23 — "agents come and go, especially with every new session, so things get caught up looking for an owner to a task that's no longer there"
- status: triage complete, fix NOT implemented (see Why This Was Not Fixed In Place)
- evidence: live read-only `map.db`, `agents/status.json`, `scripts/map_task.py`, `scripts/release_task.py`, `db/claims.py`, `scripts/advisory_monitor.py`

## Headline

The operator's instinct is right, but the mechanism is not what it looks like.
Tasks with dead owners are **not** mechanically unreachable — every nonterminal
lifecycle state has a sanctioned path forward that does not require the owner.
What is actually broken is narrower and more fixable:

1. The `owner` field is **permanently stale once set**. No verb can change it.
2. Nothing **detects or surfaces** that an owner no longer exists.
3. A stale owner **silently disables the no-self-review guard** (INS-0039).

So work does not jam; it goes unnoticed, and one safety property quietly dies.

## Measured Scope

83 nonterminal tasks. Owners cross-checked against the `agents` table and
`agents/status.json`.

| Category | Count | Tasks |
|---|---|---|
| Owner absent from `agents` table entirely | 0 | — |
| Owner present but `inactive` | 15 | TASK-164/165/166/169/170/171/172/173/175/176/178 (`codex-lab-mozu`), TASK-194 (`codex-lab-nivo`), TASK-235/238/249 (`claude-lab-lure`) |
| Owner present but `standby` | 6 | TASK-063/064/065/081/090/097 (`codex-lab-limo`) |
| Owner/claimant drift, nonterminal | 7 | TASK-148/149/152/158/162/174 (owner `command-center`, claimant `claude-lab-zera`), TASK-268 (owner `command-center`, claimant `codex-lab-lori`) |

Every one of the 21 dead/standby-owner tasks is in status `APPROVED` — awaiting
release. None is in a state that blocks other work today.

## Per-State Recovery Reality

Checked against the code, not assumed:

| State | Owner needed to move it? | Sanctioned path | Verdict |
|---|---|---|---|
| READY | No | `claim_task()` — any eligible agent | OK |
| IN_PROGRESS, live lease | No | `expire_leases()` once the lease passes | OK |
| IN_PROGRESS, no claimant | No | `map_task.py recover-orphan` (added by TASK-266) | OK — this was the one real jam, already fixed |
| CHANGES_REQUESTED | No | `map_task.py rework --actor` | OK |
| SUBMITTED | No | reviewer approves/rejects; no owner gate | OK |
| APPROVED | No | `release_task.py` checks only `status == 'APPROVED'` and `ensure_agent(released_by)` | OK |

`release_task.py` has no owner check at all, so the 21 APPROVED tasks above can
be released by any agent right now. They are stalled by attention, not by code.

## The Three Actual Gaps

### Gap 1 — `owner` is write-once with no reassignment verb

`map_task.py` exposes: `create`, `approve`, `reject`, `rework`, `release`,
`recover-orphan`, `add-output-path`, `show`, `log`. Only `create` sets `owner`.
`claim_task()` sets `claimed_by` and never touches `owner`. `rework` resets
status and clears claim fields but leaves `owner` untouched. So once an owner's
session dies, the field is wrong forever and AGENTS.md forbids hand-editing
SQLite to fix it.

Lived instance this session: TASK-267 was CHANGES_REQUESTED under
`codex-lab-lime` (`inactive/session_superseded`). It took an operator decision
to route the rework, and even after `codex-lab-kula` did all the work and
released it, `owner` still read `codex-lab-lime` throughout. The alignment memo
had to describe its own owner field as a "reconciliation gap" in prose because
there was no verb to correct it.

### Gap 2 — nothing detects a dead owner

`advisory_monitor.py` reports `owner` as context inside its orphaned-claim and
aging-transition findings, but never asks whether that owner still exists.
`check_agent_mirror_drift()` compares the `agents` table against
`status.json` — roster-vs-roster, never task-owner-vs-roster. So a task whose
owner evaporated produces no finding, no event, and no Command Center signal.
It simply ages quietly.

### Gap 3 — a stale owner disables review separation

Per INS-0039, both no-self-review guards compare the reviewer against
`tasks.owner` and never against the claimant or submitter. When the owner is a
dead agent, the guard compares against a ghost and always passes, so the agent
who actually did the work can approve it. This is the one gap with a safety
consequence rather than a tidiness consequence, and it is caused by exactly the
drift the operator noticed.

## Recommended Fix, In Three Parts

Sequenced deliberately; part 1 is independently useful and carries no risk.

**Part 1 — detect (belongs in TASK-236).** Add an owner-liveness check to
`advisory_monitor.py`: for every nonterminal task, flag when `owner` is absent
from the `agents` table or is not `available`. Proposal-only, consistent with
that task's existing charter — it observes and suggests, never mutates. TASK-236
is READY, unclaimed, owner `claude-lab-gome`, and its parking was cleared by
TASK-267's release, so this is a natural increment rather than a new lane.

**Part 2 — reassign (new task).** Add a sanctioned `map_task.py reassign-owner`
verb requiring `--actor`, `--new-owner`, and `--reason`, appending a durable
event naming the prior owner. Mirror `recover-orphan`'s shape, which already
established the pattern for auditable recovery of a stuck field. Refuse when the
task is terminal.

**Part 3 — stop keying safety on `owner` (needs INS-0039 promoted first).**
Make the self-review guards consult the durable SUBMISSION event for authoring
identity rather than `owner`. Noted here for completeness; it is INS-0039's
scope and awaits the operator's promote-or-park call. `claimed_by` is not a
usable substitute — `set_review_state()` clears it on transition.

## Why This Was Not Fixed In Place

Two reasons, both material:

1. **Output-path collision.** Parts 2 and 3 mutate `db/claims.py` and
   `scripts/map_task.py`. Those are registered output paths of TASK-266
   (APPROVED, pending release), and `codex-lab-lori` is currently registering
   the same files for TASK-268. Editing them from an unclaimed side task would
   create precisely the collision this reviewer warned lori about earlier today.
   Consistency matters more than speed here.
2. **Context threshold.** This session is past its rotation threshold (161k of
   150k) with a prepared snapshot awaiting ACK. Starting an implementation that
   would have to be handed off mid-edit is the failure the rotation protocol
   exists to prevent.

Part 1 is the exception: it touches only `advisory_monitor.py` and its tests,
which belong to TASK-236 and collide with nothing.

## Verification

- Read-only `map.db` scan of all 83 nonterminal tasks against both rosters.
- `map_task.py --help` subcommand list — confirmed no owner-mutating verb.
- `db/claims.py claim_task()` — confirmed it sets `claimed_by`, not `owner`.
- `map_task.py rework_task()` — confirmed it leaves `owner` untouched.
- `release_task.py release()` — confirmed the only gates are `status == 'APPROVED'`
  and `ensure_agent(released_by)`; no owner comparison.
- `advisory_monitor.py` — confirmed no check compares task owner to roster liveness.
