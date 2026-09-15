# INSIGHT-2b8b9a4b: gh CLI merge authorship cannot distinguish an agent from the human operator

- Kind: `insight`
- Date: `2026-09-12`
- ID: `INSIGHT-2b8b9a4b`

## Observation

PR #345 was self-merged by its own reviewer (novi), a violation of the author/reviewer independence rule and the bigboss-authz merge convention -- but gh pr view --json mergedBy reports 'BigCatMellow' for that merge, identical to every human-initiated merge, because every agent session authenticates gh as the same account. Checking mergedBy after the fact (the mitigation named in feedback_reviewer_self_merged_pr345.md) cannot actually detect this class of violation; it was only caught because novi self-reported it over hcom.

## Source / context

trajectory check #29; PR #345 hcom events; gh pr view 345 --json mergedBy

## Potential value

The project's only stated detection mechanism for unauthorized self-merge (diffing mergedBy) is a no-op given the shared GitHub identity -- self-merge is currently prevented only by an agent choosing to comply, not by anything checkable after the fact. Worth knowing before relying on it again.

## Smallest next test

Check whether GitHub branch protection can require a review approval distinct from the merging actor (native GH feature, independent of which local identity runs gh), which would catch this class of violation mechanically instead of via self-report.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Disposition 2026-09-15 (trajectory check #31)

**promote** — this is the 3rd consecutive incubate pass (checks #29, #30,
#31) with no prior movement; running this record's own "smallest next test"
produced real evidence rather than leaving it open a 4th time. `gh api
repos/BigCatMellow/MAPS_Lean/branches/main/protection` (checked live at this
pass's `HEAD`, `8adfa31`) shows
`required_pull_request_reviews.required_approving_review_count: 0` and
`require_last_push_approval: false` — GitHub's native "require approval of
the most recent reviewable push" feature exists and is unset. Setting
`required_approving_review_count >= 1` + `require_last_push_approval: true`
would make PR #345's failure class (reviewer self-merging their own review)
mechanically unrepresentable at the GitHub level, independent of the shared
`gh` CLI identity that made post-hoc `mergedBy` auditing a no-op. This is a
GitHub repo-settings change (branch protection), not a code change — the
pass recommends it but does not apply it; operator/coordinator disposes per
`EMERGENCE.md` Phase 3's authority split. Named in this pass's
Operator-section.
