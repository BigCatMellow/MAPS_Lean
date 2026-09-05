reviewer: pr297-review-velu
head_sha: 888d558cfed0d567a176abcca23f489818a4e88c
independent: true
summary: Independent adversarial review of the zero-diff revalidation acceptance path added to scripts/check_review_evidence.py. Verdict APPROVE.
verdict: APPROVE

## detail

Scope: additive acceptance path in `check()` (scripts/check_review_evidence.py)
letting a stale `head_sha` pass if (a) it is an ancestor of the resolved
reviewed-code head via `git merge-base --is-ancestor`, and (b) `git diff
--name-only <old> <new>` between them is empty. Paired playbook section in
playbook/MODEL_CAPABILITY_ROUTING.md.

Adversarial checks performed (fresh clone, /tmp/pr297rev-15688, independent
of author nafe and coordinator):

1. Does `git diff --name-only` under-report real changes it should catch?
   Built a throwaway repo, made a mode-only change (chmod +x, no content
   change). `git diff --name-only` DID list the file (git diff is a
   tree-object comparison, not a content-only comparison — mode is part of
   the tree entry). No hole here.

2. Direction/wiring check: read `check()` end to end. `reviewed_head =
   _reviewed_code_head(repo_root, actual_head)` is computed first (existing
   walk-back, unchanged); the new ancestor+diff check is applied as
   `_is_ancestor(claimed_head, reviewed_head)` and diff between the same two
   — i.e. against the post-walkback reviewed head, not the raw current HEAD.
   Correct wiring, matches the PR's own description.

3. `_reviewed_code_head` (the evidence-only-commit walk-back) is byte-for-
   byte untouched by this diff — confirmed via `git diff main...pr297 --
   scripts/check_review_evidence.py`, the function body has zero changed
   lines.

4. Adversarial test I wrote (not in the PR's own test file): two divergent
   branches from a common base, each making a change and then reverting the
   file back to the base content, producing two commits with IDENTICAL final
   tree content but NO ancestor relationship to each other. Wrote evidence
   claiming `head_sha` = branch A's tip while actual code sits at branch B's
   tip (same tree, unrelated history). Result: `_is_ancestor` correctly
   returned False (branch A tip is not an ancestor of branch B tip), so the
   check fell through to the strict "does not match" failure, NOT the
   revalidation pass. Confirms the ancestor requirement is load-bearing and
   isn't satisfiable by tree-equality alone — an attacker can't pick an
   unrelated commit with matching final content to forge a pass.

5. Authority-of-head_sha question (does this let an attacker point at code
   that was never actually reviewed by anyone?): No new hole. The checker
   has never verified that head_sha's contents were legitimately reviewed —
   only that head_sha matches the code state now on the branch. This PR
   extends "matches" from bit-equality to tree-equality-via-ancestor+
   empty-diff, which by construction means the code at head_sha and the code
   now are the same bytes. The invariant ("evidence's claimed reviewed state
   must equal the actual current code, or the check refuses to pass") is
   preserved exactly, just widened to cover a rebase/merge that changes
   nothing.

6. `_is_ancestor` omits `check=True` (unlike `_diff_is_empty`, which has it)
   — reviewed for a fail-open risk: if `_is_ancestor` returns a non-zero
   exit for a bad/unreachable SHA it returns False, which routes to the
   strict-fail branch (fail-closed). `_diff_is_empty` (which would raise on
   an invalid object) is only reached via Python's `and` short-circuit after
   `_is_ancestor` already returned True, i.e. after git has already resolved
   both objects as valid and related — so the `check=True` path never sees
   an object git couldn't resolve. No crash/bypass in practice.

7. Ran the full existing suite plus the two new tests added by this PR:
   `python3 -m unittest tests.test_check_review_evidence -v` → 12/12 pass,
   including `test_stale_ancestor_head_sha_with_zero_diff_passes_via_revalidation`
   and `test_stale_ancestor_head_sha_with_any_diff_still_fails`.

8. Playbook wording (playbook/MODEL_CAPABILITY_ROUTING.md, "Revalidation
   review tier (zero-diff re-review)" section) diffed line-for-line against
   the operator-approved text supplied in the dispatch brief — exact match,
   no drift.

No findings raised in Phase 1 (see hcom to mizo). Environment: fresh clone
at /tmp/pr297rev-15688, never touched ~/Projects/MAPS_Lean or
.claude/worktrees/.
