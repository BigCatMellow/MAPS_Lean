# IDEA-20615e4d: isolated-worktree convention added to AGENTS.md

- Kind: `note`
- Date: `2026-09-13`
- Related: `IDEA-20615e4d`, `work/notes/2026-09-12-roadmap-trajectory-check-29.md`,
  `work/notes/2026-09-13-roadmap-trajectory-check-30.md`

## What changed

Checks #28/#29/#30 each found the same gap: every dispatch brief was
restating "use a fresh clone/worktree, never `~/Projects/MAPS_Lean`" by hand,
`playbook/WORKTREE_ISOLATION.md` already existed as the recipe, but
`AGENTS.md` never named the convention — `grep -n worktree AGENTS.md` found
nothing. Check #30 disposed `IDEA-20615e4d` as **promote**: codify existing,
unanimous practice with one line in the coordination section.

Added a bullet to `AGENTS.md`'s "MAPS_L orchestration operator invariant"
section (the operator MUST list) stating that dispatched implementer/
reviewer sessions default to an isolated worktree or fresh clone, linking to
`playbook/WORKTREE_ISOLATION.md` for the recipe. No new policy — documents
what dispatch briefs already do in practice.

## Not in scope of this change

`work/ideas/2026-08-19-...IDEA-20615e4d.md`'s own disposition history is not
updated here (out of this task's write boundary); a future trajectory pass
can close that record once it confirms this line landed on `main`.
