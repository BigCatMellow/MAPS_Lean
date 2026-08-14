<!-- hpom: file: artifacts/reviews/task186-review-lime.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-lime -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: TASK-186 independent functional and security-framed review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-186

```text
task_id:      TASK-186
reviewer:     codex-lab-lime
review_date:  2026-07-22
task_owner:   claude-lab-mira
implementer:  claude-lab-gabi (option A completion)
```

Reviewer is independent of the task owner and option-A implementer. The review
claim was acquired atomically before substantive review.

## Verdict

```text
APPROVED
```

No `BLOCKER` or `REQUIRED` implementation findings remain. Production release
must wait for the operator-requested restart of `map-rns-watcher.service`, then
capture one live poll proving the seven incidents close through the new path.

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Both terminal reasons are classified; terminal sessions receive no probes, incidents, check-ins, or work nudges. | PASS | `load_durable_terminal_agents()` reads only `inactive` rows and allowlists the two reasons; `apply_durable_lifecycle()` runs before all decision paths. Existing cross-path suppression tests plus the new real-DB overlay tests pass. Live dry-run closed seven terminal incidents while a non-terminal live session (`codex-lab-lilo`) followed the ordinary live-again path. |
| 2 | Existing terminal incidents close with explicit reason and visible dry-run suppression. | PASS | Independent `--once --dry-run` emitted seven named `terminal, IDEA-0009` closure lines and matching dry-run events. `close_terminal_incidents()` sets `closed_reason=terminal_session` before removing each incident. |
| 3 | Lifecycle marks use SQLite-first persistence; `status.json` is not hand-edited or written by the watcher. | PASS | SQLite contains seven new `inactive/session_superseded` rows. In `limit_watcher.py`, `STATUS_FILE` has one `read_text()` use and no write/open-for-write use; availability writes go through SQLite then the exporter. The overlay copies dictionaries and is memory-only. |
| 4 | Before/after evidence shows zero probes for the dead population and visible suppressions. | PASS WITH CORRECTED LIVE CARDINALITY | The fixed task text says eight, but the current state had seven `gave_up=true` incidents. Seven were marked and visibly suppressed; the four fresh incidents were deliberately preserved as recoverable. Inventing an eighth terminal mark would create the exact false-suppression risk this task prevents. The stale cardinality is documented in the evidence and IDEA closeout rather than hidden. |
| 5 | Focused tests cover behavior; full suite stays green. | PASS WITH PRE-EXISTING BASELINE EXCEPTION | Focused watcher suite independently passes 37/37. With `apply_durable_lifecycle` replaced by identity, both key behavioral tests fail (`KeyError` / `AssertionError`), proving they measure the fix. The implementer's complete suite result is 70 pass / 2 fail versus baseline 69 / 2; both failures trace to the pre-existing non-canonical `TASK_SUBMITTED` event at `events.jsonl:2145`. This reviewer reproduced the same two failures before the local suite process was killed later in `pre_dispatch_gate_inputs`; no TASK-186 check failed. Rewriting the append-only event log is not an acceptable remedy. |
| 6 | EXP-0001 and IDEA-0009 are closed out. | PASS | `map_emergence.py validate` passes 85 records. EXP-0001 is `COMPLETE` with adopt selected and real-path evidence; IDEA-0009 is `ADOPTED` with the State Steward decision, scope correction, and SYN-0001 lesson recorded. |

## Forbidden Changes Check

| Forbidden / risk boundary | Status |
|---|---|
| Reintroduce terminal identities into exported routing state | NOT BROKEN — overlay is in-memory; exporter remains unchanged. |
| Suppress recoverable/non-terminal agents | NOT BROKEN — SQLite query requires `inactive` plus one of two terminal reasons; `out_of_tokens` fixture remains absent from the overlay. Fresh incidents were not marked terminal. |
| Let RnS become a lifecycle writer through the new path | NOT BROKEN — new SQLite connection is `mode=ro`; errors return `{}`. Existing explicit availability persistence remains SQLite-first and unchanged. |
| Hide suppression or mutate state during dry-run | NOT BROKEN — independent pre/post SHA-256 of `limit-watcher-state.json` was identical; all seven closures were printed. |
| Hand-edit `status.json` or bypass the exporter | NOT BROKEN — lifecycle marks were made with `declare_standby.py --terminal`; current DB/mirror evidence agrees. |

## Security-Framed Pass

The changed trust boundary is SQLite lifecycle data entering a component that
can send hcom nudges and write availability state. The new query accepts no
external parameters, opens the canonical database read-only, filters status and
reason through exact constants, and converts rows only into copied in-memory
entries. A malformed, missing, or inaccessible database degrades to `{}` and
does not crash the watcher or broaden suppression. A forged terminal mark would
require prior write access to MAP's canonical SQLite state; this task does not
add that authority. No path traversal, command construction, network endpoint,
or new write route is introduced.

Result: PASS. No security `BLOCKER` or `REQUIRED` finding.

## Files Reviewed

- `MAP_System/tasks/TASK-186.json`
- `MAP_System/scripts/limit_watcher.py`
- `MAP_System/tests/test_limit_watcher.py`
- `MAP_System/scripts/declare_standby.py`
- `MAP_System/migration/export_to_files.py`
- `MAP_System/agents/status.json`
- `MAP_System/agents/limit-watcher-state.json`
- `MAP_System/artifacts/tests/task-186-rns-suppression-evidence.md`
- `MAP_System/emergence/experiments/EXP-0001-dry-run-suppression-check-treat-inactive-session-superseded-and-.md`
- `MAP_System/emergence/ideas/IDEA-0009-rns-should-ignore-superseded-and-disposable-sessions.md`

## Verification

- `MAP_System/.venv/bin/python MAP_System/tests/test_limit_watcher.py` - PASS, 37/37.
- Mutation probe replacing `apply_durable_lifecycle` with identity - both key behavioral tests fail as required.
- `MAP_System/.venv/bin/python MAP_System/scripts/limit_watcher.py --once --dry-run` - seven explicit terminal closures; ordinary live-again handling retained for a non-terminal session.
- State-file hash around dry-run - unchanged (`70750df...31aa`).
- `MAP_System/.venv/bin/python MAP_System/scripts/map_emergence.py validate` - PASS, 85 records.
- Task mirror and task graph validators - PASS.
- Full-suite attempt - same two known event-baseline failures appeared; no TASK-186 failure appeared before later process termination.

## Release Condition

The installed systemd watcher still holds the pre-fix Python process image.
Before `TASK-186` is marked `RELEASED`, the operator should restart
`map-rns-watcher.service` and record one live poll showing the seven incidents
closed with TASK-186 terminal attribution. This is deployment activation, not a
code-review defect; it remains visible and unwaived.

### Post-approval operational confirmation

After approval, `claude-lab-gabi` reported that two of the four deliberately
unmarked fresh incidents proved recoverable: `claude-lab-niko` resumed active
TASK-266 rework, and `codex-lab-hana` returned live and had its incident closed
through the ordinary watcher path. This confirms that the seven-versus-eight
scope correction was safety-critical, not merely a stale-count variance.
Marking an eighth identity terminal would have risked suppressing wake-ups for
a live agent, violating IDEA-0009's reversibility condition. The canonical
SQLite agent rows for Niko and Hana remain `available` as of this confirmation.

This confirmation does not modify the approved implementation verdict or
waive the deployment gate. Release still requires an operator restart of
`map-rns-watcher.service` and one live post-restart poll.

## Findings

No `BLOCKER` or `REQUIRED` findings.

- `RECOMMENDED`: after the systemd restart, capture the live incident-state and
  event evidence in the TASK-186 artifact before release.
- `RECOMMENDED`: future task authoring should avoid fixed population counts for
  mutable live-state cleanup, or define a timestamped frozen population.
