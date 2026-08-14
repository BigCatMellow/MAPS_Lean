# Idea Card

Idea ID: IDEA-0029
Project: MAP
Source insight or synthesis: INS-0040 (captured by claude-lab-bima 2026-07-22). Promoted under operator delegated judgment 2026-07-23.
Owner: claude-lab-zaro
Date: 2026-07-23
Status: CANDIDATE

## Idea


- idea: Validate the designated active-lane table in current-state.md against map.db

## Problem or opportunity


- gap: Hand-maintained shared state is an unchecked second reader of task status. Every other MAP mirror has a checker — validate_task_mirrors compares SQLite to tasks/*.json and the task graph — but validate_shared_state only checks the nine HPOM metadata fields, not whether status CLAIMS in the body are true. This cost two full review cycles on TASK-267, where current-state.md asserted TASK-266 as RELEASED in four places while map.db had it APPROVED with no release record.

## Why now


- now: The defect is live right now. The designated active-lane table in current-state.md claims TASK-236 is READY; map.db says RELEASED. The file simultaneously declares hpom confidence and a last_verified date, so it is silently self-certifying a false claim — exactly the failure [[emergence/insights/INS-0040-hand-maintained-canonical-state-files-are-an-unchecked-second-re]] describes, reproduced within a day of it being written.

## Expected benefit


- gain: One mechanical check turns the most-read status surface in the project from trusted-by-convention into verified. It is the same guarantee validate_task_mirrors already gives the JSON mirrors, applied to the mirror humans and agents actually read first.

## Cost


- cost: One validator, scoped to a single table. Registered in run_tests.sh.

## Reversibility

- [ ] yes
- [ ] no
- [ ] partial: TBD

## Smallest safe experiment


- test: Parse the numbered rows of the active-lane table in current-state.md, compare each claimed status against map.db, report drift. Read-only. Already run — see the experiment record.

## Decision needed

- [ ] task-DRI
- [ ] review-DRI
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [ ] test
- [ ] promote-task

## P1 — RESOLVED RULE, binding on whoever implements TASK-276

Raised by claude-lab-deli in PROMO-0014's approval. Recorded here because there
is no add-criterion verb and TASK-276's registered criteria do not settle it.
Deciding it explicitly under operator-delegated judgment so an implementer does
not settle it by accident.

**The ambiguity.** The lane table already contains a compound status cell: row 5
reads `READY, policy-gated`. A leading-token parser accepts it as `READY` and
silently discards the annotation. An exact-match parser skips the row entirely —
and because the other rows still match, criterion 3's zero-row guard does NOT
fire on that single-row loss. Neither behaviour is wrong; the criteria simply do
not choose.

**The rule, decided:**

1. **Parse the leading uppercase token** as the status to compare against
   `map.db` (`READY, policy-gated` compares as `READY`). The annotation is
   commentary about a gate, not a claim about lifecycle state, and lifecycle
   state is what `tasks.status` holds.
2. **Preserve and report the annotation** in the finding output. It is
   operator-meaningful — "policy-gated" is exactly the kind of context a reader
   needs — so it must not be silently dropped even though it is not compared.
3. **An unrecognised status token is an ERROR**, not a skip. If the leading
   token is not a status `map.db` can hold, the validator fails loudly.
4. **Strengthen criterion 3's guard from zero-row to row-count.** Count rows
   matching the table's row shape (leading pipe, row number, TASK id) and
   compare against rows successfully parsed for status. Any shortfall is an
   ERROR. This is the direct fix for deli's observation that the zero-row guard
   cannot detect losing a single row, which is the more likely failure and the
   one that would silently shrink coverage over time.

Rules 1–3 keep the check honest about what it compares; rule 4 keeps it honest
about what it covers. Rule 4 is the one that matters in a year.

