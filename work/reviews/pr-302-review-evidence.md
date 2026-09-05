reviewer: nezu (independent reviewer, dispatched by coordinator viva; author-independent of BigCatMellow / the PR author)
head_sha: c00b9181305ba13cb771e367c0a510fffe415f2e
independent: true
summary: CHANGES-REQUESTED. Reviewed from `gh pr diff 302` + fresh clone of emergence/cross-root-synthesis-20260905 at head c00b918.

  VERIFIED LITERALLY (not from PR body):
  - `git diff --stat origin/main...HEAD` => playbook/EMERGENCE.md, 1 file, +75 / -2.
  - `git rev-list --left-right --count origin/main...HEAD` => 0 behind, 4 ahead (4 commits: a545b6b, 9c9b118, 0d5afd2, c00b918).
  - `gh pr checks 302`: `test` pass; `review-evidence` fail (expected — no evidence file committed yet).

  PR body claims "+43 lines, no deletions", "one commit ahead of current main, zero behind". Actual is +75/-2 across 4 commits. The diff is NOT what the description claims.

  STOP CONDITION HIT — scope creep into Capture/Promote authority. The PR "Boundary" section states "This does not change Capture/Promote authority." The diff contradicts that:
  - Phase 3 — Promote: adds "Promotion may also authorize work whose purpose is to replace or supersede an existing mechanism. Preserve lineage and the reason for replacement; do not keep an inferior process solely for continuity." and weakens "only a promoted item may expand implementation scope." to "...under the current operating model."
  - Phase 2 — Capture: adds "A candidate may explicitly target an existing MAPS_L process for adaptation or supersession; current process does not receive immunity from evaluation."
  - New top-of-doc clause: the lifecycle "may challenge, compare, redesign, or propose replacement of any established mechanism — including this emergence lifecycle itself".
  - Final Rule line rewritten to add "challenge precedent ... supersede when earned".
  These edits expand the charter of emergence into promotion/supersession authority framing — beyond the dispatched GOAL, which is a bounded Phase-1 (Imagine) cross-root synthesis pass that explicitly does NOT change Capture/Promote authority. 3 of the 4 commits ("Let emergence challenge established mechanisms", "Clarify current process is baseline, not ceiling", "Preserve final emergence wording") carry this undisclosed scope.

  PROCESS: material change to a canonical playbook method (playbook/EMERGENCE.md), opened directly with no companion design note and no playbook/INDEX.md "Adding or changing a method" justification. The in-repo E/I reframe (work/notes/2026-09-03-emergence-imagination-reframe-design.md) was explicitly routed as "a normal design -> impl PR pair" and "Not to be authored/merged by the reviewer lane"; this PR bypasses that pattern. The reframe itself is already merged into base main (Phase 1/2/3 structure present at origin/main), so no direct content conflict with unimplemented queued work — but the governance pattern is being skipped.

  WHAT IS SOUND (would likely approve if scoped down to just the Phase-1 synthesis pass): the "### Cross-root synthesis" subsection's Capture gate is concrete — requires source A + source B, connection type / linking mechanism, new implication not restating either source, why it may matter, current baseline, smallest discriminating test/falsifier — and explicitly rejects "Shared vocabulary, theme, superficial analogy, or incumbency". The `NO MATERIAL CROSS-ROOT SYNTHESIS FOUND` outcome is present. The connection taxonomy (shared mechanism, transfer, contradiction, composition, latent dependency, unused capability, alternative frame) matches the dispatch. The compact-summaries-first / bounded-distant-comparison / no-durable-links-without-value guidance is reasonable.

  REQUIRED CHANGES: (1) drop the Phase 2/Phase 3/top-of-doc/Rule-line edits that expand into supersession & promotion authority, OR split them into a separate design -> impl PR pair routed through the coordinator with an INDEX.md justification; (2) reduce to the bounded Phase-1 Imagine cross-root synthesis pass as dispatched; (3) fix the PR body to state the real diff size and commit count. A separate third agent handles the fix per dispatch boundary; nezu edits only this evidence file.
verdict: CHANGES-REQUESTED
