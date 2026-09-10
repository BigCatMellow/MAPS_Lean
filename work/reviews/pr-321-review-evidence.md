reviewer: maps-lean-zaru
head_sha: e7ffd35e4db64698e76662da268debb416b12edd
independent: true
verdict: REQUEST-CHANGES
summary: Re-review of PR #321 after reko applied the round-1 REQUEST-CHANGES fix. Branch docs/wiki-full-reconciliation-2026-09-09, reviewed head e7ffd35 (tip: 4373a8d merge origin/main 378468c bringing in #319/#320/#324/#325 + wiki-status; e7ffd35 reko corrections). My prior evidence commit 5dc37a5 is superseded by this file. Independence unchanged: no prior involvement with this PR, its author, or the wiki beyond these two review rounds.

  ROUND-1 BLOCKING ITEMS — 4 of 5 resolved:
   - Emergence-Triage-and-Learning.md: section retitled "Established-mechanism supersession authority is current behavior", cites merge 69d6497 (2026-09-09). RESOLVED.
   - Capability-Status.md: removed "[PR #319] is not in main" exclusion bullet; 6.4 subsystem cell updated to "a first real BEFORE_DESTRUCTIVE_ACTION firing (PR #320, merged) ... the single exercise does not close the row". RESOLVED and accurate vs checklist line 113.
   - Development.md: #319 row -> "MERGED — current behavior"; "Operator decisions" -> "PR #319 — RESOLVED"; "Recently shipped" now lists #319/#320/#324/#325. RESOLVED.
   - Snapshot pointers: Capability-Status.md and Development.md bumped 18b064c / 2377bf8 -> 378468c. RESOLVED (378468c = current origin/main HEAD).
   - NOT fully resolved: see blocking finding below.

  CRITERION 1 (docs-only) — PASS. `git diff origin/main...HEAD --name-only` = the 12 docs/wiki/*.md files + work/reviews/pr-321-review-evidence.md. Nothing else. The merge commit 4373a8d pulls origin/main content but adds no non-wiki file to the branch delta vs origin/main.

  CRITERION 2 (no capability-status overclaim) — PASS. Re-checked the wiki "Canonical capability scoreboard" against work/roadmaps/CAPABILITY_CHECKLIST.md on origin/main 378468c: 19 DONE / 10 IN PROGRESS / 6 NOT STARTED (independent count of 35 rows: DONE=6.1,6.2,6.3,6.5,6.6,6.7,6.8,6.9,6.13,6.14,6.15,6.16,6.18,6.23,6.26,6.27,6.28,6.29,6.30; IN PROGRESS=6.4,6.10,6.11,6.19,6.20,6.21,6.22,6.24,6.33,6.35; NOT STARTED=6.12,6.17,6.25,6.31,6.32,6.34). Wiki scoreboard matches. 6.4 = IN PROGRESS on checklist line 113 (the 2026-09-09 #320 update explicitly keeps it IN PROGRESS: "Row stays IN PROGRESS: the write/credential/scope guards and the capability-declaration manifest are still unbuilt"). H4 = IN PROGRESS on checklist line 25 (the 2026-09-09 #324 update: "Status NOT changed"). No wiki DONE-ish claim exceeds its checklist row. reko's 6.4 cell edit is a correction toward accuracy, not an overclaim.

  CRITERION 3 (no new authority / rule invention) — PASS. All corrected text describes merged behavior (playbook/EMERGENCE.md on origin/main line 12 / line 124 now grants exactly the supersession-proposal authority the wiki now describes) and keeps "proposal authority distinct from execution/merge authority", which matches EMERGENCE.md. No sentence invents policy.

  CRITERION 4 (mechanism accuracy) — PASS (carried from round 1; no mechanism prose changed in e7ffd35 or the merge except the #319/#320/#324/#325 status text verified above).

  CRITERION 5 (internal consistency) — FAIL (one contradiction). docs/wiki/Development.md line 59, "Capability-area snapshot" table (merged in from origin/main, not corrected by reko):
    "| Learning & Evaluation | Active / review | Cross-root synthesis is shipped; supersession authority is proposed; competitor evidence is being routed through existing owners. |"
  "supersession authority is proposed" directly contradicts the same file's corrected lines 27 ("MERGED — current behavior"), 34 ("PR #319 — RESOLVED ... is merged"), and 41 ("SHIPPED"), and misstates current origin/main behavior. This is the exact stale-#319 class flagged in round 1, left in one overlooked cell.

  BLOCKING FINDING: Development.md:59 — replace "supersession authority is proposed" with a merged/current phrasing (e.g. "Emergence mechanism-supersession authority is merged (#319)"). Single-clause fix, same file, for a third agent (reko fine to reuse).

  NON-BLOCKING NOTES (no fix required to approve once the above lands):
   - Development.md:31 still lists PR #321 as "BLOCKED ... non-mergeable against newer canonical Wiki source"; this is the PR describing its own pre-reconciliation status. Defensible as a snapshot but will be stale on merge; a third agent may want to soften it.
   - Development.md:41 "Recently shipped" #319 bullet says "lets Emergence challenge/redesign/propose replacement" — consistent with EMERGENCE.md; fine.

  6.4 + H4 CONFIRMED IN PROGRESS on origin/main 378468c; scoreboard 19/10/6 unchanged. Criterion 1 PASS, 2 PASS, 3 PASS, 4 PASS, 5 FAIL (one cell).

  VERDICT: REQUEST-CHANGES — one remaining self-contradiction (Development.md:59 "supersession authority is proposed"). All five round-1 items are otherwise addressed and the merge is clean. A single-clause correction by a third agent clears it; I will re-review that delta only.
