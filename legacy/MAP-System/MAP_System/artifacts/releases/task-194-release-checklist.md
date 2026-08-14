# Release Checklist: TASK-194

## Header

```
task_id:      TASK-194
released_by:  mapfinish2-zemi
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Documents Claude helper spawn defaults (auto permission mode + Haiku model
tier, visible `wezterm-tab` still mandatory), the escalation path for
higher tiers (written request, review by a different core agent, approve
generously when reasoning is sound), and a tier-capability rubric. Two
independent reviewers (`toku`, `zero`) both approved with no findings.

## Evidence Per Check

- **Shared-file updates complete** — All 3 declared output paths
  (`AGENTS.md`, `notes/helper-agent-guide.md`, `notes/orchestration-notes.md`)
  exist and re-verified today still carry the exact language both reviews
  cite: `AGENTS.md:141` "Claude helpers default to auto permission mode and
  Haiku"; `orchestration-notes.md:102-110` "Standing rules (operator-set)"
  section with the exact persisted-command language.
- **Decisions recorded** — the standing rule itself, with its rationale and
  the exact persisted command, is recorded in
  `orchestration-notes.md:102-110` ("Standing rules (operator-set)") — this
  *is* the decision record for an operator-set standing rule; no separate
  `DEC-NNN` was required or used for this class of rule elsewhere in the
  repo.
- **Follow-up tasks created** — none needed; the escalation path (written
  request + independent review) is itself the follow-up mechanism the task
  built, not a gap requiring its own task.
- **Event log entry prepared** — `events/events.jsonl` carries PROGRESS →
  SUBMISSION → APPROVED (`claude-lab-zero`, 2026-07-15T03:13:43Z),
  consistent with `map.db`'s pre-release `APPROVED` status.
- **Emergence capture considered** — Considered; both reviews already note
  the rubric explicitly guards against the two failure modes (blanket
  downgrade / needless escalation) rather than stating a naive rule, which
  is the substantive insight here and is already captured in the doc text
  itself rather than needing a separate artifact.

## Live-State Finding (flagged, not blocking)

Re-checking acceptance criterion 4 today (`hcom config claude_args`) found
it returns `--model sonnet --permission-mode auto`, not the documented
Haiku default. Both reviews independently verified `--model haiku` live at
review time (2026-07-14/15), so criterion 4 was genuinely true then.
Digging further: `~/.hcom/config.toml` has **no** `claude_args` key at all
today — the persisted TOML setting this task made is gone (host reorg or a
later reset, not something this checklist can date), and the current
`sonnet` value comes from an `HCOM_CLAUDE_ARGS` environment variable set for
this session's tag, not from a standing default. This is a live operational
drift from what the docs prescribe, not a defect in what TASK-194 shipped
or reviewed — the documentation is unchanged and correct, and the review
evidence was accurate at the time. Flagging to `claude-lab-lili` as a
possible small follow-up (re-persist `hcom config claude_args
'--permission-mode auto --model haiku'`) rather than holding this
documentation task's release on a runtime config value it does not itself
own going forward.

## Verification

- Independent reviews: `artifacts/reviews/task194-review-toku.md`,
  `task194-review-zero.md` — both APPROVED, all 4 acceptance criteria PASS,
  scope check confirms only the 3 declared output paths changed.
- Re-verified today: all 3 declared output paths exist with unchanged
  content; `python3 MAP_System/scripts/validate_task_mirrors.py` — pass.
