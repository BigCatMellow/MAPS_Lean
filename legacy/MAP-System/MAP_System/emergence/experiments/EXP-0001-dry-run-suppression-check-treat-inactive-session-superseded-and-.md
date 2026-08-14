# Experiment Record

Experiment ID: EXP-0001
Project: MAP
Source idea: IDEA-0009
Owner: claude-lab-mira
Date: 2026-07-14
Status: COMPLETE

## Hypothesis


- hyp: Dry-run suppression check: treat inactive/session_superseded and inactive/disposable_session_ended as terminal in the limit watcher, replay current watcher state + hcom snapshot, verify no probes/incidents/resumes for terminal sessions and that every suppression is visible in dry-run output

## Test


- test: Run the bounded command or workflow described by this record.

## Scope


- scope: Only the files and artifacts named in this record.

## Limits


- limits: Do not bypass HPOM task, review, or release gates.

## Success criteria


- pass: The record produces useful evidence without expanding scope.

## Failure criteria


- fail: The record is unclear, unused, or creates unsafe ambiguity.

## Evidence to collect

- ev: baseline --once --dry-run (2026-07-14, pre-change): watcher would probe claude-lab-zera and codex-lab-mozu — both sessions ended on purpose same day (librarian batches / TASK-175-178 done). Live reproduction of IDEA-0009's failure mode. Saved: scratchpad task186-baseline-dryrun.txt; contents to be copied into MAP_System/artifacts/tests/task-186-rns-suppression-evidence.md.
- ev: post-change dry-run after terminal marks applied (pending — helper claude-lab-zero implementing per inbox/helpers/task-186-rns-terminal-suppression-implementer.md).

## Review path

- review: TASK-186 (owner claude-lab-mira); implementation by visible helper claude-lab-zero under owner accountability; independent review by codex-lab-nivo at submission.

## Result

- result: HYPOTHESIS CONFIRMED, and the experiment found a defect the hypothesis
  did not anticipate. Treating inactive/session_superseded and
  inactive/disposable_session_ended as terminal does suppress probes, incidents
  and nudges, and every suppression is visible in dry-run output. But the
  suppression could not fire at all as originally built: migration/export_to_files.py
  lists both terminal reasons in NON_OPERATIONAL_REASONS and drops those agents
  from agents/status.json, which was the file limit_watcher.py read terminality
  from. The exporter deleted the row the watcher needed. Measured on live state
  2026-07-22: the terminal path would fire for only 2 of 11 incident-holding
  agents, and those 2 (claude-lab-mira, codex-lab-kiri) survived the filter
  solely because they happened to own active tasks. Fixed under operator
  decision option A (2026-07-22): terminality now resolves from the SQLite
  agents table, the declared source of truth. Baseline --once --dry-run emitted
  zero lines; after the fix plus seven session_superseded marks it emits seven
  explicit terminal-closure lines with zero probe attempts, while correctly
  still probing claude-lab-niko and codex-lab-lilo, which carry no terminal
  mark. Suppression is selective, not blanket. Tests 32 -> 37; the five new ones
  exercise the real exporter and a real schema-built map.db, and both new
  behavioral tests were verified to fail when the fix is stubbed out.
  Full evidence: artifacts/tests/task-186-rns-suppression-evidence.md

## Decision

- [x] adopt
- [ ] revise
- [ ] reject
- [ ] park

## Notes

- The three pre-existing terminal unit tests passed for the entire period the
  feature was unreachable, because they asserted against synthetic status.json
  dicts that already contained the terminal agents and so never exercised the
  real exporter filter. Green tests plus a silent dry-run was the actual
  signature of the bug. Recorded as the transferable lesson from EXP-0001:
  a test whose fixture supplies the condition the production path removes
  measures the fixture, not the system.
- Residual: the live systemd unit map-rns-watcher.service must be restarted to
  load the fixed code. Until then the seven incidents remain open in live state.

- note:
