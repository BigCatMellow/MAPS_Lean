# IDEA-a134ad7c: Exclude .claude/worktrees/ from check_spiderweb.py by default

- Kind: `idea`
- Date: `2026-09-03`
- ID: `IDEA-a134ad7c`

## Observation

check_spiderweb.py already excludes legacy/, migration/legacy-*, archive/, work/context/ as raw/non-canonical surfaces. It does NOT exclude .claude/worktrees/*, so an in-place run against a checkout with active worktrees reports ~12000 orphan candidates / 186 broken links / 131 duplicate-stable-IDs, almost all from worktree copies of legacy/. A clean clone reports 430 / 11 / 0. The scanner is effectively unusable in the coordinator checkout.

## Source / context

scripts/check_spiderweb.py exclude list; run comparison this session (in-place vs /tmp/rev278-686802 clean clone), 2026-09-03

## Potential value

One line in the exclude list makes the default scan usable where it is actually run (the working checkout), instead of requiring a throwaway clone every time. Worktrees are copies, not canonical artifacts - exactly the class the other exclusions target.

## Smallest next test

Add '.claude/worktrees/' to the DEFAULT_EXCLUDES in check_spiderweb.py; re-run in-place and confirm counts match a clean clone (~430 orphans, ~11 broken).

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

- 2026-09-03: promoted → PR "coordination tooling fixes" (branch `fix/coordination-tooling`), bundled from the 2026-09-03 E/I Emergence pass. Append-only disposition; the "Not promoted." line above is the original capture state.
