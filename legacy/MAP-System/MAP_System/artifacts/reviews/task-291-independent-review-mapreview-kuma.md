<!-- hpom: file: artifacts/reviews/task-291-independent-review-mapreview-kuma.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: TASK-291 independent review -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-291

## Header

```
task_id:      TASK-291
reviewer:     mapreview-kuma
review_date:  2026-07-28
task_owner:   mapfinish-rafa
```

Reviewer (mapreview-kuma) ≠ task owner (mapfinish-rafa). Independence check passes.

---

## Verdict

```
APPROVED
```

---

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | AGENTS.md Core Protocol documents running `validate_shared_state_tasks.py` (or `render_active_state.py --check`) as part of the standing startup habit, in the same place and style as rule 11 | PASS | Rule 12 appended immediately after rule 11 in the Core Protocol numbered list. Same template: "When you \<check\> (a standing startup habit), also \<action\>. If \<condition\>, \<remedy\> — see \<doc\>. ... \<N-day drift evidence\> ... treat this check as part of the routine, not optional follow-up." Not a bolted-on separate section — it reads as a natural continuation of rule 11's pattern. |
| 2 | The startup note names the concrete command and states what to do on drift (regenerate + fix stale annotations), not just report | PASS | `notes/command-center-lab-restart-startup.md` names `python3 MAP_System/scripts/validate_shared_state_tasks.py` (or `render_active_state.py --check`), then: "If it reports drift, regenerate the file with `python3 MAP_System/scripts/render_active_state.py` and fix any stale entries in `shared/active-lane-annotations.json` — do not just note the drift and move on." Explicit corrective action, not passive reporting. |
| 3 | Guidance explicitly does NOT introduce automatic rewriting of `current-state.md` during another agent's startup, and says why, in BOTH files | PASS | AGENTS.md rule 12: "Do not regenerate `current-state.md` silently as a side effect of another agent's startup: it is shared canonical state, and an unannounced rewrite while another agent is reading it would recreate the SYN-0001 pattern (one state, multiple readers, no declared authority) instead of fixing it — regenerate it as its own visible step." Startup note: "Do this as your own visible step, not silently while another agent's startup is reading the same file: regenerating `current-state.md` unannounced during someone else's orientation is a new instance of the SYN-0001 pattern (one state, multiple readers, no declared authority), not a fix for it." Same reasoning independently present and correctly stated in both files, not a reference-only mention in one. |
| 4 | No executable behavior changes; `run_tests.sh` still passes | PASS (with caveat) | Both edits are Markdown/prose only — no script or code touched by this task. Ran `bash MAP_System/scripts/run_tests.sh`: 76/80 pass. The 4 failures are pre-existing and unrelated to this diff (see Independent Verification Run below for the traced root cause of each); none originate from rule 12 or the startup-note addition. |

---

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Edits outside declared `output_paths` (`MAP_System/AGENTS.md`, `MAP_System/notes/command-center-lab-restart-startup.md`) | NOT BROKEN — `git diff` on these two files also shows other hunks (retrieval capsule, rule 11, `submit_task` doc update, helper-spawning wording, helper-note metadata contract, Verified Context Rotation section), but these are pre-existing uncommitted content from separately released tasks (TASK-269 RELEASED 2026-07-23; TASK-271 RELEASED 2026-07-28T16:53:40Z; rule 11 predates TASK-291 per its own task description). TASK-291 was created 12:27:09Z and submitted 12:34:22Z — a 7-minute window, consistent only with rule 12 + the matching startup-note bullet, not the much larger unrelated hunks. |
| Introducing auto-regeneration of shared canonical state | NOT BROKEN — explicitly and correctly disclaimed in both files (see criterion 3 above). |
| Executable/behavioral changes disguised as docs | NOT BROKEN — diff attributable to this task is prose-only. |

---

## Files Reviewed

- `MAP_System/AGENTS.md` (full diff via `git diff`, rule 12 hunk isolated by attribution reasoning above)
- `MAP_System/notes/command-center-lab-restart-startup.md` (full diff via `git diff`)
- `MAP_System/tasks/TASK-291.json` (acceptance criteria)
- `MAP_System/events/events.jsonl` (task/task-269/task-271 timeline cross-check)

## Independent Verification Run

```text
bash MAP_System/scripts/run_tests.sh: SUMMARY pass=76 fail=4 total=80
Failures, all confirmed pre-existing/unrelated to TASK-291:
  - validate_research_artifacts: stale fragment in
    artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md (unrelated file).
  - validate_shared_state_tasks: 6 drifted row(s) — live, in-flight drift from
    concurrent agent work (the condition TASK-291 adds a startup habit for;
    this task does not itself resolve live drift).
  - validate_events_no_new_warnings: new_warnings=1, traced via
    `python3 MAP_System/scripts/validate_events.py --fail-on-new` to
    events.jsonl line 2145, a TASK_SUBMITTED non-canonical event type from
    TASK-257 dated 2026-07-19 — 9 days before TASK-291 existed.
  - validate_layer1_test: cascades from the validate_events failure above.
```

## Notes

Scope note for future reviewers: `MAP_System/AGENTS.md` and
`notes/command-center-lab-restart-startup.md` currently carry multiple
tasks' uncommitted content in the same working tree. A plain `git diff`
against HEAD on these files will keep mixing unrelated tasks' hunks until
the next commit; attribute hunks via `events/events.jsonl`
timestamps/status rather than assuming the entire file diff belongs to the
task under review.
