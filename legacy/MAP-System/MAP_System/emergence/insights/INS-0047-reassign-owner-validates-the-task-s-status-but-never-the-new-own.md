# Insight Record

Insight ID: INS-0047
Project: MAP
Related task: TASK-273
Detected by: unknown (record found empty, reconstructed by claude-lab-muza)
Date: 2026-07-23
Status: PROMOTED

## Short description

- obs: `reassign_task_owner()` validates the task's status (refuses terminal tasks) but, absent a guard, would not validate that the new owner is a real, registered agent — a reassignment could otherwise create a dangling `tasks.owner` foreign-key reference.

## Trigger

- src: TASK-273 ("Add a sanctioned owner-reassignment verb for tasks whose owner agent no longer exists"), built to fix 21 nonterminal tasks stuck with dead/superseded owners. While designing the verb, the same class of gap `map_task.py`'s `ensure_agent()` and `claim_review()` already guard against was identified for the new `reassign_task_owner` path: nothing stopped a reassignment from pointing `owner` at an agent id that does not exist in the `agents` table.

## The synthesis

- synth: Any sanctioned verb that writes an agent id into a foreign-key column (`owner`, `claimed_by`, review claimant, etc.) needs the same paired default — register-or-verify the target agent before the write — or it can silently produce a dangling reference. This is the same shape of gap as [[emergence/insights/INS-0049-file-extraction-bundle-rewrite-code-needs-path-traversal-validat]] (a paired-default that's easy to add for one verb and forget for the next).

## Why it might matter

- why: TASK-273 exists specifically because a *different* write-once owner path (task creation) left `tasks.owner` referencing agents that no longer exist, with no sanctioned way to fix it. Building a second owner-writing verb without the same registration guard would have reintroduced the exact defect the task was created to repair.

## Evidence

- ev: `MAP_System/db/claims.py` `reassign_task_owner()` (~line 451) inserts `INSERT OR IGNORE INTO agents (agent_id, ...)` for `new_owner` before updating `tasks.owner`, with the comment "Same registration contract as map_task.py ensure_agent() and claim_review(): owner is a foreign key, so sanctioned reassignment must never create a dangling agent reference." TASK-273's acceptance criterion 2 requires exactly this: "The new owner is registered via the same ensure_agent contract used elsewhere, so reassignment cannot create a dangling agent reference." Independently verified in `MAP_System/artifacts/reviews/task273-review-deli.md`.

## Risk

- risk: None outstanding — the guard is implemented and independently reviewed. Residual risk is process-level: this record itself was found completely empty (no git history exists for it, so original detection metadata — author, exact date, verbatim reasoning — could not be recovered) and passed `map_emergence.py validate` as failing for weeks before being noticed, which is its own small instance of [[emergence/insights/INS-0007-emergence-records-need-lifecycle-closeout-not-just-capture]] (capture without closeout) and worth folding into that pattern rather than treating as new.

## Scope

- scope: Applies to any MAP CLI verb that writes an agent id into a foreign-key-constrained column.

## Recommended next action

- [x] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: Already resolved as part of TASK-273 itself (RELEASED); this record documents the finding after the fact. No further action needed beyond keeping the record well-formed so `map_emergence.py validate` passes.

## Resolution (2026-07-29, claude-lab-muza)

Reconstructed from an empty file flagged by `helper-librarian.md`'s 2026-07-28/07-29 audits. No prior content existed in git history (single squashed history at this path; no earlier commit adds it). Content above is derived directly from the current `reassign_task_owner()` implementation and TASK-273's own acceptance criteria/review, not fabricated narrative. Status set to PROMOTED because the guard this insight describes is already implemented and independently reviewed — there is no further promotion to make.
