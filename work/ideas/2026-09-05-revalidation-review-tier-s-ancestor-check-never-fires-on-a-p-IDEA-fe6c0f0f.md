# IDEA-fe6c0f0f: revalidation review tier's ancestor check never fires on a plain git rebase

- Kind: `idea`
- Date: `2026-09-05`
- ID: `IDEA-fe6c0f0f`

## Observation

PR #297's check_review_evidence.py revalidation path accepts a stale head_sha only if `git merge-base --is-ancestor` holds between old and new head. A `git rebase origin/main` (this repo's actual coordinator convention, not `git merge`) replays commits as new objects, so is-ancestor is false even when the diff is byte-identical — confirmed live on PR #298 on 2026-09-05.

## Source / context

playbook/MODEL_CAPABILITY_ROUTING.md "Revalidation review tier" section + scripts/check_review_evidence.py (PR #297); observed during PR #298 merge-prep (coordinator mizo, session 32).

## Potential value

the revalidation shortcut currently can't help with this repo's real rebase-based merge-prep workflow — every rebase-for-freshness still needs a manual zero-diff confirmation + evidence rebind (smaller savings than intended, but still skips full re-review).

## Smallest next test

instead of is-ancestor, compare the PR's pre-rebase diff (old_head vs old_head's merge-base with new main) against the same diff computed relative to the new head — if identical, that's rebase-safe evidence without requiring literal ancestry. Try this next time a PR needs a freshness rebase under strict branch protection.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

- 2026-09-12 disposition (trajectory check #29, `vuna`): **promoted — implemented.** `scripts/check_review_evidence.py`'s revalidation tier now accepts on empty tree diff alone (PR #345, `_is_ancestor` removed), independently reviewed (`novi`, APPROVE, 13/13 `tests/test_check_review_evidence.py` passing) and independently re-verified this pass. Resolved one arc before the N=3 escalation bound named at check #28. Observation preserved as history.
