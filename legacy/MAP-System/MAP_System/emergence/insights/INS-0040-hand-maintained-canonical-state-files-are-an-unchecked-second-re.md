# Insight Record

Insight ID: INS-0040
Project: MAP
Related task: TASK-267
Detected by: claude-lab-bima
Date: 2026-07-22
Status: RAW

## Short description


- obs: Hand-maintained canonical state files are an unchecked second reader of task state, and no validator compares their status claims to map.db

## Trigger


- src: TASK-267 was rejected twice by two independent reviewers on the same defect shape. Kiri's REQUIRED finding 1 was current-state.md publishing TASK-186 as blocked after the operator had resolved it. My REQUIRED finding was current-state.md and the realignment memo publishing TASK-266 as RELEASED in four places while map.db had it APPROVED with no task_release_records row and no RELEASED event. Different tasks, different reviewers, identical shape.

## The synthesis


- synth: [[shared/current-state]] and the planning memos are a second reader of task state that agents are told to trust, but nothing mechanically compares their task-status claims against map.db, the authoritative writer. Every other MAP mirror has a checker: validate_task_mirrors.py compares SQLite to tasks/*.json and workflow/task_graph.json. Shared-state prose has validate_shared_state.py, but it checks the nine HPOM metadata fields, not the truth of status claims in the body. So the one canonical file agents read first for the operating picture is the one mirror with no agreement check.

## Why it might matter


- why: This is [[emergence/synthesis/SYN-0001-two-readers-one-truth]] (one state, multiple readers, no declared authority) recurring inside the very document that diagnoses [[emergence/synthesis/SYN-0001-two-readers-one-truth]]. It cost two full review cycles on TASK-267 alone, and both escapes were caught only because a human-directed independent reviewer happened to re-query map.db by hand. The failure mode is silent and self-confirming: the file declares hpom confidence HIGH and last_verified today, so a reader has no signal that a specific status line is stale. In the TASK-266 case it also erased a real outstanding release step, and it contradicted the release gate documented at line 164 of the same file.

## Evidence


- ev: 1) map.db at review time: TASK-266 status=APPROVED, latest event APPROVED by codex-lab-lime 2026-07-22T19:11:43Z, no row in task_release_records; TASK-186 status=RELEASED with a release record by claude-lab-gabi 2026-07-22T21:48:52Z. 2) Four false RELEASED claims: current-state.md lines 46 and 54-55, memo TASK-268 row and post-table sentence. 3) Prior identical-shape escape: [[artifacts/reviews/task267-review-kiri]] REQUIRED finding 1. 4) validate_shared_state.py passed 23/23 across both submissions and cannot catch this by design -- it validates HPOM metadata fields, not body claims. 5) validate_task_mirrors.py exists and passes, proving MAP already accepts mirror-agreement checking as a pattern; it simply does not cover shared-state prose. 6) The runner's DEPENDENCY_SATISFIED_STATUSES = {DONE, APPROVED, RELEASED} meant the downstream conclusion happened to survive, which is why the error was easy to miss.

## Risk


- risk: A naive validator that regexes every TASK-NNN mention in shared/ and demands a matching live status would produce constant false positives: these files legitimately discuss historical states, released work, decision-era context, and explicitly timestamped snapshots. Any real implementation needs a narrow opt-in marker for lines that assert current status, or must scope itself to a designated lane table, so that timestamped historical prose stays legal. Getting this wrong would make the validator noisy and it would be disabled, which is worse than not having it.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:

## Corroboration (added 2026-07-23 by claude-lab-zaro)

[[INS-0019]] is independent corroboration of this insight's central argument,
from a different project and predating it by nineteen days: a ~100-line domain
validator written at the start of a generative batch immediately caught legality
bugs in already-released artifacts that two agents' manual cross-review had
approved. The mechanism it names — encoding rules as a script forces enumerating
them, and the enumeration itself surfaces the gap — is why the fix promoted from
this insight is a validator rather than a review checklist.

Promoted via IDEA-0029 / EXP-0010 / PROMO-0014 into TASK-276, scoped to the
designated active-lane table only, per the false-positive risk recorded above.
EXP-0010 found real drift on its first run: the table claimed TASK-236 READY
while map.db said RELEASED.

