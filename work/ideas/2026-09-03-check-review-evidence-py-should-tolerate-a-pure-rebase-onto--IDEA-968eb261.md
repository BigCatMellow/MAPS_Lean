# IDEA-968eb261: check_review_evidence.py should tolerate a pure rebase-onto-main when reviewed paths are unchanged

- Kind: `idea`
- Date: `2026-09-03`
- ID: `IDEA-968eb261`

## Observation

PR #278 needed 2 review-evidence rebinds this session: Phase-1 head -> rebase onto #277 -> fcd2e0e. The reviewed content (2 doc files) was byte-identical across the rebase. check_review_evidence.py binds to an exact head_sha and its walk-back stops at merge commits (INSIGHT-29a10ad4), so any rebase invalidates evidence even when nothing the reviewer looked at changed. This tax scales with main's velocity and strict branch protection, and has recurred for months (#109, #278, others).

## Source / context

This session's #278 two-phase review; scripts/check_review_evidence.py head_sha logic; work/insights INSIGHT-29a10ad4; work/ideas IDEA-582cc671 (zero-diff re-review tier)

## Potential value

Removing a recurring multi-rebind tax on every PR that races main. Complements IDEA-582cc671 (a routing/effort-tier answer) with a checker-side answer: evidence stays valid if head_sha is an ancestor of HEAD AND the reviewed paths' tree objects are unchanged between that sha and HEAD.

## Smallest next test

Prototype a check_review_evidence.py mode: given head_sha not == HEAD, accept if git diff <head_sha>..HEAD -- <reviewed paths> is empty and head_sha is an ancestor of HEAD; emit a 'revalidated by tree-equality' line. Test against #278's rebase.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
