<!-- hpom: file: artifacts/releases/task-186-release-checklist.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: HPOM-006 release gate -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Release Checklist: TASK-186

## Header

```
task_id:      TASK-186
released_by:  claude-lab-gabi
release_date: 2026-07-22
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

RnS terminal-session suppression (IDEA-0009 / EXP-0001) is released under
operator decision **option A**: agent terminality resolves from the SQLite
`agents` table, the declared source of truth, instead of from
`agents/status.json`, which `migration/export_to_files.py` documents as an
operational routing view that may omit rows.

**Why this was needed.** The feature was structurally unreachable, not merely
buggy. `export_to_files.py:25-30` lists both terminal reasons in
`NON_OPERATIONAL_REASONS` and line 132 drops those agents from `status.json`,
while `limit_watcher.py:851,859` resolved terminality *from* `status.json`. The
exporter deleted the row the watcher needed. Measured against live state on
2026-07-22, the terminal path would fire for 2 of 11 incident-holding agents,
and those 2 survived the filter only because they happened to own active tasks.

**What changed.** `load_durable_terminal_agents()` (read-only SQLite, returns
`{}` on any DB error so RnS degrades rather than dies) and
`apply_durable_lifecycle()`, called once at the top of `poll_once()` so incident
closure, suppression reporting, and the pre-existing check-in / work-nudge /
v1-nudge guards all see the same lifecycle fact. The overlay is in-memory and
cannot leak dead identities into the routing view: the watcher never writes
`status.json`. The exporter filter is untouched.

**Lifecycle marks.** Seven genuinely-dead sessions marked
`inactive/session_superseded` via `declare_standby.py --terminal` (SQLite-first,
then exported; `status.json` never hand-edited): `claude-lab-lure`,
`claude-lab-mira`, `claude-lab-toku`, `claude-lab-zera`, `codex-lab-mozu`,
`codex-lab-nivo`, `gune`.

### Scope variance, accepted by the reviewer

The task text asserts 8 dead sessions; live state carried 7 with
`gave_up=true`. Seven were marked and an eighth was not invented. The four
incidents opened 2026-07-22T14:14:48 with `probes_sent=0` were deliberately
left unmarked as potentially recoverable.

This was subsequently **confirmed rather than merely defended**:
`claude-lab-niko` and `codex-lab-hana` both returned to live activity, and niko
went on to rework TASK-266. Marking the literal 8 would have suppressed RnS
wake-ups for an agent that was alive and mid-task, which is exactly the failure
IDEA-0009's reversibility condition exists to prevent.

### Evidence limitation — recorded explicitly, not glossed

Post-restart **live terminal-attribution evidence is unavailable**, and this
release proceeds without it under reviewer decision A
(`codex-lab-lime`, hcom #11804).

The fixed daemon is live (pid 143411, started 16:09, replacing the pre-fix pid
1291 from 14:14). However, `terminal_suppressed` is empty and zero
`limit_watcher` events are attributed to TASK-186. The seven incidents were
closed by the generic TASK-176 stale-prune path under the **pre-fix** daemon, in
the window between the marks being applied (~14:5x) and the restart. By the time
the fixed code was running, no terminal agent still held an incident, so the
terminal path had nothing to act on.

Cause: the marks had to be applied while the pre-fix daemon was still polling
every 300 s, because the environment command classifier blocks `systemctl` from
an agent session and the daemon could not be stopped first. The generic prune
won the race.

What this means precisely:

- **Achieved and verified:** all seven remain durably `inactive/session_superseded`
  in SQLite, their incidents are closed, and they receive zero further probes.
- **Not demonstrated on live state:** the visible intentional terminal
  attribution that distinguishes "dead on purpose" from "gone, cause unknown" —
  the actual value IDEA-0009 sought.

The code path itself is proven by the pre-restart `--once --dry-run` capture
(seven explicit terminal-closure lines, zero probe attempts, while still
correctly probing `claude-lab-niko` and `codex-lab-lilo`, which carry no
terminal mark) and by 37 passing tests including a real-exporter regression.

A terminal transition was **not** manufactured to produce the missing evidence.
Marking a live session dead to generate a log line is the precise failure
IDEA-0009's reversibility condition guards against. Per the reviewer, the next
naturally-occurring terminal session is follow-up operational confirmation, not
a release blocker.

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_limit_watcher.py` — 37 pass
  (was 32). Five new tests exercise the real exporter and a real schema-built
  `map.db`; both new behavioral tests were confirmed to FAIL when
  `apply_durable_lifecycle` is stubbed to identity.
- `bash MAP_System/scripts/run_tests.sh` — pass=70 fail=2. The two failures are
  the pre-existing non-canonical `TASK_SUBMITTED` event at
  `events/events.jsonl:2145` and are unrelated. Not "fixed" by rewriting the
  append-only log.
- `validate_task_mirrors.py`, `validate_events.py` (errors=0),
  `map_emergence.py validate` (86 artifacts) — all pass.
- Independent review: `artifacts/reviews/task186-review-lime.md` (functional plus
  security-framed), APPROVED.

## Related records

- Evidence: `artifacts/tests/task-186-rns-suppression-evidence.md`
- Experiment: EXP-0001 (COMPLETE / adopt)
- Idea: IDEA-0009 (ADOPTED, with lifecycle closeout)
- Follow-up captured: INS-0038 — `claim_task` writes SQLite but never syncs file
  mirrors. Same SYN-0001 shape; blocked two agent approvals and produced a false
  suite regression during this same session.
