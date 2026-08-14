<!-- hpom: file: artifacts/tests/task-186-rns-suppression-evidence.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-15 -->
<!-- hpom: verified_against: TASK-186 / EXP-0001 experiment run -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-186 / EXP-0001 Evidence: RnS Terminal-Session Suppression

- task: TASK-186 (owner claude-lab-mira; implementation by visible helper
  claude-lab-zero per `inbox/helpers/task-186-rns-terminal-suppression-implementer.md`)
- experiment: EXP-0001 (source idea [[emergence/ideas/IDEA-0009-rns-should-ignore-superseded-and-disposable-sessions|IDEA-0009]])
- date: 2026-07-14

## Baseline (pre-change, real `--once --dry-run`)

The watcher wanted to probe two sessions that ended on purpose the same day
(zera: librarian batches done; mozu: TASK-175/176/178 done):

```text
[dry-run] would announce + run: hcom r claude-lab-zera --terminal wezterm-tab --go --hcom-prompt Rise & Shine (RnS limit watcher, TASK-083): ...
[dry-run] event: {... "task_id": "TASK-083", "summary": "RnS: probe nudge sent for claude-lab-zera (probes so far: 1)." ...}
[dry-run] would announce + run: hcom r codex-lab-mozu --terminal wezterm-tab --go --hcom-prompt Rise & Shine (RnS limit watcher, TASK-083): ...
[dry-run] event: {... "task_id": "TASK-083", "summary": "RnS: probe nudge sent for codex-lab-mozu (probes so far: 1)." ...}
```

Plus 8 standing gave-up incidents for early-July sessions
(valo, dino, lema, muva, vino, neko, magi, veto) — all `available` in durable
state with no lifecycle mark, i.e. indistinguishable from crashes. This is
IDEA-0009's failure mode reproduced live, third occurrence on record
(TASK-090, TASK-146 corroboration, today).

## Implementation (helper claude-lab-zero, verified by owner)

- `limit_watcher.py`: `is_terminal_session()` (durable `inactive` +
  reason in `{session_superseded, disposable_session_ended}`);
  `close_terminal_incidents()` (pops open incidents, labels
  `closed_reason: "terminal_session"`, never a silent drop);
  `detect_terminal_suppressions()` (terminal absentees reported every poll,
  PROGRESS event on first observation only via `state["terminal_suppressed"]`).
  All three pure; `detect_presumed_down`/checkin/work-nudge/v1-nudge paths
  untouched (they already suppress on any recorded reason — now pinned by tests).
- `declare_standby.py`: `--terminal {session_superseded,disposable_session_ended}`
  mutually exclusive with `--back`; SQLite-first then exporter (SYN-0001 rule).
- Tests: 4 new (classification, closure+idempotence, suppression detection,
  cross-path suppression pinning) — watcher tests 18→22.

Owner verification (independent of helper's run): 22/22 watcher tests,
`run_tests.sh` 55/55.

Helper also ran a synthetic-state simulation (temp files, patched
hcom_snapshot, real state untouched) previewing post-mark behavior:
incidents for zera/mozu closed with visible lines + TASK-186 PROGRESS events,
both suppressions reported, zero probe attempts.

## Live marks + after-evidence

Status: APPLIED 2026-07-15 by owner claude-lab-mira (resumed session; the
harness no longer blocked the marks). The 8 dead early-July sessions were
marked `inactive/disposable_session_ended` via the SQLite-first
`declare_standby.py <agent> --terminal disposable_session_ended` path:
claude-lab-valo, codex-lab-dino, codex-lab-lema, codex-lab-muva,
claude-lab-vino, codex-lab-neko, claude-lab-magi, codex-lab-veto. SQLite
`agents` table confirms all 8 as `inactive/disposable_session_ended`.

### Real end-to-end result — DESIGN CONFLICT FOUND (2026-07-15)

The intended TASK-186 outcome was: watcher reads terminal `reason` from
`status.json`, closes each open incident with a *visible* terminal-suppression
line (IDEA-0009 distinction: deliberate death, not crash). That path did **not**
fire. What actually happened, verified against `events.jsonl` and the live
daemon (`limit_watcher.py --interval 60`, running):

1. `migration/export_to_files.py` `load_agents()` already lists BOTH TASK-186
   terminal reasons in `NON_OPERATIONAL_REASONS`
   (`{session_ended, session_superseded, tool_identity, disposable_session_ended}`).
   Marking an agent terminal therefore **removes it from `status.json`
   entirely** (unless tied to an active task): status.json dropped from ~22 to
   14 agents; SQLite still holds all 53.
2. The watcher reads `status.json`, so `is_terminal_session()` /
   `close_terminal_incidents()` never see the terminal reason — the agents are
   simply absent. The TASK-186 visible-terminal path is effectively dead code
   for real marks.
3. Instead, because each agent is now absent from BOTH durable status and the
   hcom snapshot, the pre-existing `prune_absent_session_tracking()` closed all
   8 incidents via the generic **TASK-176 "pruned stale session tracking
   absent from durable status and current hcom snapshot"** event
   (events.jsonl 2026-07-15T17:33:19-04:00).

Net effect: **acceptance criterion "zero probes for the 8" IS met** (incidents
closed, no further nudges — verified: no probe/nudge events for the 8 after the
marks). But the IDEA-0009 *value* — a visible, intentional terminal attribution
distinct from "gone, cause unknown" — is **not** delivered; the closure reads as
a generic stale prune. The helper's earlier green run used synthetic status
files that *included* the terminal agents, so it never exercised the real
exporter filter — that is why this was not caught until the live marks landed.

Design decision required before TASK-186 can be closed as designed (routed to
operator via hcom request 2026-07-15). Options on the table:

- **A (recommended):** make the prune path attribution-aware — when an agent
  being pruned is terminal in SQLite (source of truth), emit it as an IDEA-0009
  terminal suppression rather than a generic TASK-176 stale prune. Keeps
  status.json lean, honors source-of-truth, delivers the visible distinction.
  Touches watcher prune logic (now TASK-187's file) + a SQLite read.
- **B:** exporter carve-out — retain terminal agents in status.json while they
  still carry an open incident, so the watcher's existing status.json terminal
  path fires. Touches `export_to_files.py`; adds noise to the routing view.
- **C:** accept that the prune path already suppresses probes; close TASK-186
  recording the redundancy + exporter conflict as an insight, and drop the
  now-unreachable status.json-terminal path.

## Output-path handoff (2026-07-14, hcom #34173)

`limit_watcher.py` and `test_limit_watcher.py` were handed off to TASK-187
(RnS active-session resume awareness, codex-lab-nivo), which builds directly
on this task's frozen, owner-verified watcher changes. The combined watcher
file diff — including this task's suppression code — is formally reviewed
under TASK-187's independent review. TASK-186 retains `declare_standby.py`,
agent state/status files, this evidence artifact, and the EXP-0001/IDEA-0009
records. Handoff logged as a TASK-186 PROGRESS event; graph and mirror
validators pass post-handoff.

## Process note

The harness block itself is evidence for IDEA-0009's `Decision needed:
State Steward` field: terminal lifecycle marks are shared-state stewardship,
and even a lead agent under a broad autonomy grant structurally needs an
operator touchpoint for them. Recorded in `notes/orchestration-notes.md`.

## Root cause confirmed and quantified (2026-07-22, claude-lab-gabi)

The 2026-07-15 note recorded the exporter/watcher conflict as an observation.
This session verified it in code and measured its real blast radius. The
conflict is confirmed, and it is worse than "the terminal path does not fire":
it fires for some agents and not others, for a reason unrelated to whether the
session is actually dead.

Mechanism, verified by reading both sides:

- `migration/export_to_files.py:25-30` puts BOTH terminal reasons
  (`session_superseded`, `disposable_session_ended`) in `NON_OPERATIONAL_REASONS`.
- `export_to_files.py:132` drops any non-operational agent from `status.json`
  UNLESS that agent appears in `active_agent_ids` — the owner/claimed_by/
  required_agent of any READY, IN_PROGRESS, SUBMITTED or CHANGES_REQUESTED task.
- `limit_watcher.py:851,859` resolve terminality from `status_data`, i.e. from
  `status.json`.

So `declare_standby.py --terminal` writes the mark to SQLite correctly, and the
exporter then removes the very row the watcher needs in order to see it.

Measured against live state (11 agents currently holding open incidents), the
outcome splits:

| Outcome | Count | Agents |
|---|---|---|
| RETAINED in status.json -> terminal path fires | 2 | claude-lab-mira, codex-lab-kiri |
| DROPPED from status.json -> generic TASK-176 prune instead | 9 | toku, zera, mozu, nivo, gune, lure, niko, hana, lilo |

mira and kiri survive the filter only because each still owns an active task —
mira owns TASK-186 itself. That is the sole difference between the agents where
the feature works and the agents where it does not. The result is intermittent
behavior with no observable explanation at the operator surface, which is a
worse failure mode than a uniformly dead code path.

Evidence this is not theoretical: `--once --dry-run` captured this session
(pre-change baseline) emitted ZERO lines. All 32 tests in
`tests/test_limit_watcher.py` pass, including full terminal coverage
(`test_terminal_session_classification`, `test_close_terminal_incidents_pops_and_labels`,
`test_detect_terminal_suppressions_selects_only_terminal_absentees`). The unit
tests pass because they construct synthetic `status.json` dicts that already
contain the terminal agents — they never exercise the real exporter filter.
Green tests plus a silent dry-run is the signature of this bug.

### Why this is SYN-0001 again

One piece of state (agent lifecycle) with two readers and no declared authority.
SQLite `agents` is the source of truth; `status.json` is explicitly documented at
`export_to_files.py:4-7` as "an operational routing view, not a full dump". The
watcher asks a *lifecycle* question of a *routing view* that is contractually
allowed to omit rows. Both components are behaving as written; the boundary
between them was never declared. This is the third recurrence in two days
(the dead approval gates and the claim_review reviewer-registration trap being
the others).

### Recommended fix (option A, generalized)

Resolve terminality from SQLite, not from `status.json`. `is_terminal_session`
should consult the `agents` table — the declared source of truth — so the
exporter's routing-view filter can no longer decide whether a lifecycle fact is
visible. This makes the 9 dropped agents behave identically to the 2 retained
ones, needs no exporter carve-out, and keeps `status.json` lean.

Ownership note: `limit_watcher.py` was handed to TASK-187, which is now
RELEASED. No active task holds it, so TASK-186 can reclaim it via the sanctioned
`map_task.py add-output-path` verb before any edit.

Not implemented in this session: IDEA-0009 records the decision as State
Steward, and the choice between A/B/C was escalated to the operator on
2026-07-15 and is still unanswered. Re-escalated 2026-07-22 with the evidence
above. No live agent lifecycle marks were applied while the decision is open.

## Option A implemented and verified (2026-07-22, claude-lab-gabi)

Operator selected **option A** on 2026-07-22 (recorded as a `DECISION_RECORDED`
event on TASK-186), resolving the State Steward decision IDEA-0009 required and
that had been open since 2026-07-15.

### Change

`MAP_System/scripts/limit_watcher.py`, reclaimed onto TASK-186 via
`map_task.py add-output-path` (TASK-187 held it and is RELEASED, so no active
task owned it):

- `DB_FILE` constant — SQLite is the declared source of truth for lifecycle.
- `load_durable_terminal_agents()` — reads `agents` where `status='inactive'`
  and reason is in `TERMINAL_SESSION_REASONS`. Opened **read-only**
  (`mode=ro`); RnS must never be a writer on this path. Returns `{}` on any DB
  error so the watcher degrades to the status.json view instead of dying — it
  exists to recover agents when things are already broken.
- `apply_durable_lifecycle()` — overlays those marks onto the status.json view,
  reinstating agents the exporter filtered out.
- Called once at the top of `poll_once()`, before anything reads `status_data`,
  so incident closure, suppression reporting, and the pre-existing check-in /
  work-nudge / v1-nudge guards all see the same lifecycle fact.

The overlay is in-memory only and cannot leak dead identities back into the
routing view: `STATUS_FILE` is read at `poll_once` and never written by the
watcher (verified — the only write path is
`persist_agent_availability` -> SQLite -> exporter). The exporter's filter is
left completely untouched, so `status.json` stays lean.

### Lifecycle marks applied

Seven agents, all via the sanctioned SQLite-first path
(`declare_standby.py --terminal session_superseded`, which writes SQLite then
runs the exporter). `status.json` was never hand-edited.

`claude-lab-lure`, `claude-lab-mira`, `claude-lab-toku`, `claude-lab-zera`,
`codex-lab-mozu`, `codex-lab-nivo`, `gune`.

**Scope correction:** the task description says "8 genuinely-dead early-July
sessions". The live state carries **7** incidents with `gave_up=true`, not 8.
Marking seven, not inventing an eighth. The four remaining open incidents
(`claude-lab-niko`, `codex-lab-hana`, `codex-lab-kiri`, `codex-lab-lilo`) were
opened 2026-07-22T14:14:48 with `probes_sent=0` and are deliberately **out of
scope**: they have not been probed to exhaustion and may still be recoverable.
Marking a recoverable session terminal suppresses a legitimate wake-up, which is
the exact risk IDEA-0009's reversibility condition guards against.

### Before / after evidence

Baseline `--once --dry-run` (post-claim, pre-change): **zero lines of output**.
The terminal path could not fire for any agent.

After `--once --dry-run` (option A + marks applied), verbatim suppression lines:

```
[dry-run] RnS: incident for claude-lab-lure closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for claude-lab-mira closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for claude-lab-toku closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for claude-lab-zera closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for codex-lab-mozu closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for codex-lab-nivo closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
[dry-run] RnS: incident for gune closed — session recorded as session_superseded (terminal, IDEA-0009). No further probes.
```

Each is paired with a durable `PROGRESS` event attributed to `TASK-186`, so the
closure reads as a deliberate terminal suppression rather than the generic
TASK-176 stale prune. **Zero probe attempts** were emitted for all seven.

The same run demonstrates the suppression is **selective, not blanket** — the
strongest single piece of evidence here:

- `codex-lab-hana`, `codex-lab-kiri`: detected live again, incidents closed
  normally via the ordinary path.
- `claude-lab-niko`, `codex-lab-lilo`: **still receive probe nudges**, correctly,
  because they carry no terminal mark.

A blanket suppression bug would have silenced those two as well. Confirmed the
dry-run wrote nothing: `limit-watcher-state.json` byte-identical before and after.

### Tests

`tests/test_limit_watcher.py` (also reclaimed onto TASK-186): **37 pass**, up
from 32. Five new tests deliberately exercise the **real** path, because the
three pre-existing terminal tests passed throughout the entire period the
feature was dead:

- `test_exporter_really_drops_terminal_agents_from_status_json` — builds a real
  `map.db` from `migration/schema.sql`, runs the **real**
  `export_to_files.load_agents`, and asserts the terminal agent is dropped. The
  agent is seeded into status.json and owns no active task, so only the reason
  filter can remove it. This pins TASK-186's premise: if the exporter ever stops
  filtering, this test fails loudly rather than silently making option A moot.
- `test_terminality_resolves_from_sqlite_despite_exporter_filter` — reproduces
  the exact live failure (marked in SQLite, absent from status.json) and asserts
  the watcher still classifies it terminal.
- `test_durable_lifecycle_overlay_only_marks_genuinely_terminal` — an
  `out_of_tokens` session is coming back and must still be probed.
- `test_durable_lifecycle_overlay_does_not_mutate_caller_state`.
- `test_durable_lifecycle_degrades_safely_without_database`.

**Both new behavioral tests were verified to FAIL when the fix is stubbed out**
(`apply_durable_lifecycle` reduced to identity): each raises `AssertionError`.
A regression test that passes with and without the fix is worthless, and this
task is the reason that check is now habit.

### Not done in this session

The live RnS service (`map-rns-watcher.service`, systemd user unit, was pid
1291) still runs the **pre-fix code loaded at 14:14**. It must be restarted to
pick up option A. Stopping/restarting the unit was blocked by the environment's
command classifier, so this needs the operator:

```
systemctl --user restart map-rns-watcher.service
```

Until that restart, the seven incidents stay open in live state — the fix is
proven by dry-run but not yet acting in production. Nothing is half-applied: the
marks are durable and correct in SQLite, and the pre-fix daemon simply cannot
see them as terminal.
