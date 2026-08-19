# Worktree Isolation

Any dispatched agent/session that does writable repository work in a shared
clone (the operator's checkout, a coordinator's checkout — anything more than
one lane might touch) MUST work in its own `git worktree`, never mutate the
shared checkout's branch state, and remove its worktree when the work is
integrated or discarded.

This doc exists because the alternative was tried and failed: a fork/subagent
ran `git checkout`/`gh pr checkout` directly in the shared
`~/Projects/MAPS_Lean` clone and discarded another lane's uncommitted work —
twice, early in one session. The fix below fully stopped it for the rest of
that session and is now the standing convention, not a one-off workaround.

## The rule

- Never run `git checkout`, `git stash`, `git clean`, `git reset --hard`, or
  `gh pr checkout` in a shared checkout on behalf of dispatched work. Those
  commands mutate branch/working-tree state that another lane may depend on.
- Every dispatched agent/session doing writable repo work gets its own
  `git worktree`, on its own branch, at its own path under `/tmp/` (or another
  location outside the shared clone).
- All commits and pushes for that work happen from inside that worktree path,
  never from the shared checkout.
- The worktree is removed once its push/PR has succeeded — not before, and
  not left indefinitely after.

## The recipe

From the shared checkout (read-only for this step — `fetch` never mutates
branch state):

```bash
cd ~/Projects/MAPS_Lean
git fetch origin main
git worktree add /tmp/<descriptive-name> -b <branch-name> origin/main
```

Then do **all** work — edits, commits, pushes, `gh pr create` — from inside
`/tmp/<descriptive-name>`:

```bash
cd /tmp/<descriptive-name>
# ... edit, git add, git commit ...
git push -u origin <branch-name>
gh pr create --title "..." --body "..."
```

Once the push/PR has succeeded, clean up:

```bash
git worktree remove /tmp/<descriptive-name> --force
```

Do not remove the worktree before the push/PR succeeds — if something fails
partway, the worktree is the recovery surface (its working tree still has the
uncommitted or unpushed state to inspect), not something to discard early.

This doc is the recipe; it does not add a new authority layer. It integrates
with — and does not replace — existing task ownership, review independence,
and recovery/cleanup conventions (see `playbook/HELPERS_AND_COMMUNICATION.md`
and `playbook/TASK_LIFECYCLE.md`). A worktree gives a dispatched worker a safe
place to *do* the work; it does not give it authority to merge, and it does
not change who owns the task, who reviews it, or who integrates the result.

## Wrinkle: a branch falls behind `main` mid-PR

This came up close to a dozen times in one session: another PR merges to
`main` first, leaving an open PR's branch behind. Bringing it up to date with
`git merge origin/main` (inside the worktree, never the shared checkout)
creates a **merge commit** on the branch. That has a real consequence for
`scripts/check_review_evidence.py`: its `head_sha` walk-back explicitly never
walks past a merge commit (see that script's own docstring — this is a
deliberate safety property, not a bug: a merge commit could otherwise hide
non-evidence changes). So syncing with `main` always forces a new `head_sha`
for any review-evidence file already committed against the old head.

### Worked example

Say a PR's review-evidence file at `work/reviews/pr-118-review-evidence.md`
was bound to `head_sha: abc1234` (the commit the reviewer actually read), and
then `main` moves because another PR merges first:

```bash
cd /tmp/<descriptive-name>          # inside the worktree, not the shared clone
git fetch origin main
git merge origin/main               # creates a new merge commit, e.g. def5678
```

Before touching the evidence file, confirm the merge didn't silently change
anything the review actually covered — diff the *reviewed files* (not the
whole tree) between the old head and the new merge commit:

```bash
git diff abc1234 def5678 --stat -- <file1> <file2> ...
```

If that comes back empty (no changes to the reviewed files — only the
`main`-side changes from the other PR were pulled in), the review still
covers the same code. Update the evidence file's `head_sha` to the new merge
commit and record why, so a future reader doesn't mistake the rebind for a
new, unreviewed head:

```
head_sha: def5678
rebase_note: rebound from abc1234 after merging origin/main to pick up
  PR #117; git diff abc1234 def5678 --stat -- <reviewed files> confirmed
  no change to reviewed files
```

Commit that evidence-file update, then re-run the check locally before
pushing:

```bash
python3 scripts/check_review_evidence.py <PR-number>
```

If the diff on the reviewed files is *not* empty, the review no longer covers
the current code — do not just rebind `head_sha`; get the changed files
re-reviewed (or re-request review) before merging.

## Sharp edge: an empty commit permanently breaks the walk-back for that lineage

`check_review_evidence.py`'s walk-back only treats a trailing commit as
"evidence-only" (safe to walk past) when that commit's own diff is
non-empty and touches only `work/reviews/`. An **empty** commit — e.g. one
made with `git commit --allow-empty` to force a CI re-run — sitting on top
of an evidence-only commit breaks that condition: its diff is empty, so it
does not satisfy "every path it changes is under `work/reviews/`" in a way
the walk-back can use, and the walk stops there.

This happened once in this session (via an `--allow-empty` commit made to
retrigger CI). Do not create empty commits on a branch carrying committed
review evidence.

If it happens anyway, do not try to walk further back past the empty
commit — that is not what the script does and forcing it would defeat the
safety property. Instead, bind `head_sha` to the exact empty commit itself.
Its tree is usually still identical to the prior real code state (that's
what makes it "empty"), so the review still legitimately covers it; the fix
is just pointing `head_sha` at that commit, with a `rebase_note` explaining
why an empty commit is the bound head.

## Summary checklist

- [ ] `git fetch origin main` from the shared checkout (read-only).
- [ ] `git worktree add /tmp/<name> -b <branch> origin/main`.
- [ ] All edits/commits/pushes/`gh pr create` happen inside `/tmp/<name>`.
- [ ] Never `git checkout`/`stash`/`clean`/`reset --hard`/`gh pr checkout` in
      the shared checkout.
- [ ] If the branch falls behind `main`, merge inside the worktree, diff the
      reviewed files across the merge, and rebind `head_sha` with a
      `rebase_note` if they're unchanged.
- [ ] Never `git commit --allow-empty` on a branch with committed review
      evidence; if it happens, bind `head_sha` to that exact commit instead
      of trying to walk past it.
- [ ] `git worktree remove /tmp/<name> --force` only after push/PR succeeds.
