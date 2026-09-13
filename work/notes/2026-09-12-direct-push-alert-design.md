# Direct-to-main push alert — design

2nd occurrence of `feedback_no_direct_main_push` (commit `ce198ae`, see
`work/notes/2026-09-12-roadmap-trajectory-check-29.md` §2). Per rule 20
(CLAUDE.md), a 2nd occurrence of the same pattern gets a mechanical
countermeasure, not another prose reminder.

## Why this can't be a merge gate

Branch protection on `main` has already been silently bypassed twice by an
admin identity (both prior occurrences). A required-status-check merge gate
assumes the actor pushing respects branch protection in the first place —
that assumption is exactly what failed. So this is a **post-hoc, loud
alert**, not prevention: it cannot undo a push or block it retroactively,
it can only make it immediately visible instead of relying on an agent
self-reporting (how the 1st occurrence was caught) or a human finding it at
the next roadmap trajectory check (how the 2nd was caught).

## Mechanism

`.github/workflows/direct-push-alert.yml` triggers on `push` to `main`.
`scripts/check_direct_push.py <before> <after> --repo <owner/repo>` walks
every commit newly reachable in that range, skips true git merge commits
(2+ parents — always PR-covered already, since `review-evidence.yml` gates
every PR merge), and for each remaining commit calls GitHub's "list pull
requests associated with a commit" API
(`GET /repos/{owner}/{repo}/commits/{sha}/pulls`). A commit with zero
associated **merged** pull requests is a violation: the script prints its
sha/author/subject and exits 1, failing the workflow run loudly on `main`.

This API was chosen over a text/issue search because it has no indexing
lag and is the primitive GitHub itself uses to answer "which PR does this
commit belong to" — it works correctly for this repo's squash-merge
tooling (`scripts/opcmd_merge.py`), which never produces a 2-parent merge
commit. Verified empirically against real history: PR #347's squash
commit `5d6d567` returns `{"number": 347, "merged_at": "..."}`; the
`ce198ae` direct push returns an empty list.

## What this does not do

* Does not block, revert, or auto-remediate the push.
* Does not distinguish "author is a legitimate admin doing something the
  process explicitly allows" from "process violation" — every direct
  commit is flagged; a human decides what (if anything) to do about it.
* Does not run on `pull_request` — that trigger and its own gating are
  entirely `review-evidence.yml`'s job, unchanged.

## Verification

`tests/test_check_direct_push.py` (11 cases) exercises the pure git-plumbing
helpers (`_pushed_commits`, `_parent_count`) against real scratch
repositories and the violation-detection logic (`find_violations`) with
`_has_merged_pr` mocked (no network calls in unit tests). Additionally
hand-run against this repo's own real history during development: passes
cleanly on PR-only ranges (e.g. `92fa162..bdf7f37`, PR #345 alone) and
correctly flags `ce198ae` by exact sha/author/subject when it is in range —
not a synthetic-only validation.
