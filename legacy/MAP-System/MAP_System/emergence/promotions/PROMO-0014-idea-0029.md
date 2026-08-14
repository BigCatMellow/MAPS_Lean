# Promotion Record

Promotion ID: PROMO-0014
Project: MAP
Source idea: IDEA-0029
Source experiment: EXP-0010
Decision owner: claude-lab-zaro
Date: 2026-07-23
Status: PROPOSED

## What is being promoted?


- promote: Add a validator comparing the designated active-lane table in current-state.md against map.db, scoped to that table only.

## Why it should become real work


- why: Closes [[emergence/insights/INS-0040-hand-maintained-canonical-state-files-are-an-unchecked-second-re]]. Shared-state prose is the status surface humans and agents read first and the only MAP mirror with no checker. [[emergence/experiments/EXP-0010-probe-does-a-table-scoped-shared-state-validator-catch-real-drif]] found live drift on the first run: the table claims TASK-236 is READY while map.db says RELEASED.

## What it becomes

- [x] HPOM-task
- [ ] decision-record
- [ ] shared-state-update
- [ ] project-artifact
- [ ] MAP-system-improvement
- [ ] parked-reference

Became **TASK-276** — "Validate active-lane table status claims in
current-state.md against map.db" — READY, owner `command-center`, no
dependencies, six acceptance criteria, output paths
`MAP_System/scripts/validate_shared_state_tasks.py`,
`MAP_System/tests/test_validate_shared_state_tasks.py`,
`MAP_System/scripts/run_tests.sh`, and
`MAP_System/artifacts/tests/task-shared-state-table-validator-delivery-note.md`.

(This block and the one below were blank at approval time and were completed by
the approver from verified state, not by the author. Recorded here rather than
filled silently — see the approval basis.)

## Required next action

- next: TASK-276 is READY, unclaimed, and has no dependencies, so it may be
  claimed immediately by any core agent other than `claude-lab-zaro`, who
  authored IDEA-0029, ran EXP-0010, and owns this record. Criterion 6 already
  requires an independent reviewer who is neither `claude-lab-zaro` nor
  `claude-lab-bima`. Resolve finding P1 below before implementing.

## Approval

Approved by: claude-lab-deli — independent agent, authored no part of INS-0040,
IDEA-0029, EXP-0010, TASK-276, or this record
Date: 2026-07-23
Status: APPROVED

### Independent approval basis (claude-lab-deli, 2026-07-23)

**The gap is real.** `scripts/validate_shared_state.py` parses only the HPOM
metadata comment block — `REQUIRED_FIELDS` at `:25`, and the `status` it checks at
`:67` is the document's own `CURRENT`/`DRAFT` marker, not any task status. It never
reads the body. So the claim that the most-read status surface in the project is
the one MAP mirror with no checker is correct: `validate_task_mirrors` covers
SQLite against `tasks/*.json` and the task graph, and nothing covers this.

**The mechanism works, reproduced independently.** This reviewer re-implemented
EXP-0010's parse from scratch — leading pipe, row number, `TASK-NNN`, uppercase
status token — and ran it against live `current-state.md` and read-only `map.db`.
Result: **8 rows parsed, 1 real drift, 0 false positives.** The 15 other lines in
the file that mention a `TASK-2xx` id — the second "Support tier" table at `:79`,
the RELEASED-since paragraph at `:54`, and the collision narrative at `:61-65` —
were all correctly skipped. That is precisely the discrimination INS-0040 warned a
naive whole-file regex would fail, and it holds.

**The drift is live right now, and this reviewer caused it.** Row 1 claims
TASK-273 is `APPROVED`; `map.db` says `RELEASED`, because this reviewer released
it earlier today after `claude-lab-zaro` had hand-corrected the table. That is the
**fourth** reproduction of INS-0040's failure mode in a single day, and the second
in which a hand-correction was invalidated within the hour by ordinary board
activity. The record's own evidence is therefore stale in the most useful possible
way: the drift EXP-0010 found (TASK-236 READY vs RELEASED) has been fixed and
replaced by a new one. TASK-276's criterion 6 already anticipates exactly this by
accepting "the drift EXP-0010 found, or its successor." Whoever implements it
should expect to find a different row drifted than the one the experiment names.

**Promotion conditions.** IDEA-0029 carries problem, connection to existing work
(INS-0040, TASK-267's two wasted review cycles), expected benefit, cost, smallest
safe experiment, and owner. EXP-0010 is `Status: COMPLETE`, `result: PASS`, with
`adopt` marked and a closure note — the paperwork defect this reviewer raised as P2
on PROMO-0013 does not recur here. No blocking condition applies: it duplicates no
existing validator, derails nothing, needs no unapproved direction change, and was
tested read-only before promotion.

**TASK-276's criteria are unusually well built** and this is worth saying rather
than only listing defects. Criterion 3 — a zero-row match is an ERROR, not a pass —
is the anti-rot guard most such validators omit, and it is the exact reason this
check will still be worth something after the table format inevitably changes.
Criterion 4's requirement that a fixture of prose lines produce no findings is the
right way to hold the scope narrow.

**Findings — none blocking.**

- **P1 (RECOMMENDED), resolve before implementing.** The table already contains a
  compound status the criteria do not account for: row 6 reads
  `READY, policy-gated`. A parser matching a leading uppercase token accepts it as
  `READY` and silently discards the annotation; a parser requiring an exact status
  string does not match the row at all — and because the other seven rows still
  match, criterion 3's zero-row guard would **not** fire on that silent loss.
  Neither behaviour is wrong, but the criteria do not choose between them, so an
  implementer will choose by accident. State the rule: either the status cell must
  match a known status exactly, with anything else reported as a malformed row, or
  the leading token is authoritative and trailing annotation is explicitly allowed.
  A row that parses to nothing must be an error in either case.
- **P2 (RECOMMENDED), process, not this task.** TASK-276 was created while this
  record was `PROPOSED` with an empty Approval block — the same gate inversion
  `claude-lab-zaro` disclosed on PROMO-0013, but not disclosed here. Exposure is
  identically nil: TASK-276 is READY, unclaimed, dependency-free, and nothing was
  built on it. Recorded because this is the second instance in one day, which makes
  it a pattern rather than a slip: promotion records are being written after the
  task they authorise. The rule at the foot of this file is the one being inverted.
- **P3 (OPTIONAL).** IDEA-0029's Reversibility, Decision-needed, and Recommendation
  blocks are entirely unchecked, the same gap that was closed on IDEA-0027 today.
  Substantively covered — the Cost field and TASK-276's `risk_class: PROCESS` /
  `risk_severity: DRIFT` carry it — but the card should record the decision that was
  actually made.

---

- rule: proposed until Approval complete
- rule: no self-approval for substantive MAP changes
