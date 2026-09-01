# PR #241 review evidence — 6.9/S6 frozen Skill-selection eval scoping note

Independent verification-only review by maps-lean-nava (gela authored). Design
only, 1 file (`work/notes/2026-09-01-6.9-frozen-selection-eval-scoping.md`).
Reviewed in two rounds: claims 1–5 + the flagged call at the initial commit
(REQUEST_CHANGES on a repeated citation misattribution), then a delta re-check
of the fix commit (APPROVE). `head_sha` below is the rebased branch tip
carrying both commits.

## Round 1 — claims 1–5 (all substantively verified against merged code + roadmap)

1. **6.9 promotion gate is COVERAGE+EXISTENCE, not a numeric threshold.**
   VERIFIED. `00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6.9 `### Promotion gate`
   (lines 706–708) is exactly *"Do not rely on fuzzy Skill selection without a
   frozen selection evaluation,"* preceded by the six `### Routing evaluation
   must include` categories (699–704). No number. `/usr/bin/grep` for
   `>= 0.` / `threshold` across `runtime/skills/` + the eval tests → nothing.
   `test_exp_a_skill_routing.py` pins the current numbers as a regression
   detector ("update only alongside a deliberate reviewed selector change"),
   not a criterion.
2. **"Meaningful improvement over baseline" (roadmap L1383/L1961) is the
   semantic-retrieval gate, not 6.9's.** VERIFIED. L1383 is under `## 6.33
   Semantic retrieval` and L1961 under `## 13.4 Evidence gate`.
   `_select_skills` is `signals & skill_tokens` — exact set intersection, no
   fuzzy/semantic step. It *is* the explicit baseline; a "beat baseline by X"
   bar has no referent.
3. **EXP-A already is a frozen selection eval of the real selector through the
   real harness (~0.889 p/r); gap = thin category coverage + no criterion +
   not recorded as a gate decision.** VERIFIED. `exp_a_skill_routing_v1.json` =
   12 cases (`DIRECT 5, HARD_NEGATIVE 2, NO_SKILL 2, PARAPHRASE 1,
   VOCABULARY_SHIFT 1, MULTI_SKILL 1` — 3 of 6 roadmap categories have a single
   case). `test_exp_a_skill_routing.py` runs the real `_select_skills` (real
   `SkillCatalog` from on-disk `SKILL.md`, no stubs) through the real
   `evaluate_skill_selection`.
4. **Not blocked on an operator precondition / retrieval experiment / selector
   work.** VERIFIED. Semantic retrieval is §6.33/§13.4 (separate item); 6.9's
   gate is the explicit selector existing + being frozen-evaluated (S4 + S6
   both DONE). 6.9 is P2, no `build_canonical_harness_service` / ask-#1
   dependency. Only downstream dependency is the promotion *determination*.
5. **Smallest slice (~26-case v2 corpus + a `test_exp_b` module reusing EXP-A's
   shape + record) is executable as a one-shot dispatch.** VERIFIED. §4 spec:
   new `exp_a_skill_routing_v2.json` (≥4 deliberate cases per §6.9 category,
   ~6–8 candidate Skills, frozen `version`+`sha256`+pinned-composition test), a
   parallel `tests/test_exp_b_skill_routing.py` mirroring `test_exp_a`'s
   no-stubs shape, a results note, one checklist evidence clause, no status
   flip, MUST-NOT touch selector/harness. Paste-ready Resume prompt.

### Round 1 finding (REQUEST_CHANGES, since fixed)

The note attributed a "review/operator promotion gate" to §6.9 by citing
roadmap line 1754 (3×) — but line 1754 is item 7 of the `## Build` list under
`# Wave 6 — Controlled operational learning and harness refinement`
(6.30/6.31 lesson + harness-config promotion), not §6.9. The flagged-call
reasoning (§1e/§5) was built on that misattribution. On the merits the note's
conclusion (defer the criterion; a reviewer may set optional floors on a P2
quality capability unless the operator claims it) did NOT hide an operator-only
call — the misattribution pushed toward over-escalation, the safe direction —
but the citations needed correcting.

## Round 2 — delta re-check (8c25de5, +104/-73, 1 file)

| Required fix | Result |
|---|---|
| (a) 3 line-1754 misattributions gone | DONE — kept only as explicit disavowals that locate line 1754 in Wave 6 (inoculates future readers). |
| (b) §1e/§5 re-grounded on §6.9 lines 706–708 + §17.3 sibling-evidence framing | DONE — §1e leads with the coverage+existence bar / "no operator language"; §17.3's "explicit operator decision" and "measured promotion gate" framed as sibling status-flip evidence kinds, not a §6.9 requirement. |
| (c) §1d floors reframed as optional additional rigor | DONE — header now "Optional additional rigor — a numeric criterion §6.9 does NOT mandate"; §2b/§4c/§4d/§6/Resume prompt made consistent. |
| (d) enum note fixed | DONE — full 8-member list; "overlapping Skills" = MULTI_SKILL + AMBIGUOUS. |
| (e) claims 1–5 + §4 slice + READY-TO-DISPATCH verdict unchanged in substance | CONFIRMED — only "review/operator" → "reviewer" phrasing swapped. |
| bonus | §1a's own stale self-citation "lines ~2185–2215" for §6.9 corrected to "~697–708". |

The flagged call now reads correctly: verifying §6.9's gate is a reviewer task
(§6.9 has no operator language); the operator MAY opt in under §17.3 but is not
required; mis-selections are contained downstream by the 6.22 trust gate + SEC4
quarantine. No operator-only call hidden as reviewer judgment (rule 9/11).

## Sanity

`python3 -m runtime.smoke` → exit 0. Diff = 1 file, docs-only.

reviewer: maps-lean-nava
head_sha: 9c77baacf4d504f9d054c2db173d67f31010fd3e
independent: true
summary: APPROVE — verification-only review of a design-only scoping note; claims 1-5 (6.9 gate is coverage+existence not numeric; the "beat baseline" language is the §6.33/§13.4 retrieval gate; EXP-A is already a real frozen selection eval; not blocked on an operator precondition; the §4 corpus slice is a clean one-shot) all verified against merged code and the roadmap; an initial REQUEST_CHANGES on a repeated line-1754/§6.9 citation misattribution was fixed in commit 8c25de5, which cleanly re-grounds §1e/§5 on §6.9 lines 706-708 + §17.3 as sibling status-flip evidence and reframes the numeric floors as optional rigor; the READY-TO-DISPATCH verdict and the flagged-call treatment (reviewer task, operator may opt in but is not required) are sound.
