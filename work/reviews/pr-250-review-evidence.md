# PR #250 review evidence — 6.9/S6 promotion gate step (decision: NO FLIP)

Independent verification review by maps-lean-luve (nava authored; luve reviewed
PR #246 which this consumes). Docs-only:
`work/notes/2026-09-02-6.9-s6-promotion-gate-step.md` (+168) +
`work/roadmaps/CAPABILITY_CHECKLIST.md` (6.9 / S6 / L4 rows, prose only).

## (i) Coverage / existence facts — CORRECT

Independent re-run at HEAD:

```
python3 -m unittest tests.test_exp_b_skill_routing  → 3/3 OK
  category_accuracy: {DIRECT 1.0, PARAPHRASE 1.0, MULTI_SKILL 1.0, NO_SKILL 1.0,
                      VOCABULARY_SHIFT 0.0, HARD_NEGATIVE 0.0, AMBIGUOUS 0.0}
  exact_rate 0.6 (15/25) · selection_precision 0.684 · selection_recall 0.765
  selection_f1 0.7222 · false_activation_cases 4 · missed_activation_cases 4
  ambiguity_misses 2 · corpus_sha256 2cff0e40…
```

Every figure in the note's §1 (metrics) and §2 (per-category table) matches this
run and matches the PR #246 review evidence. The corpus covers all six §6.9
categories with depth (5/4/4/4/4/4, "overlapping Skills" = MULTI_SKILL 2 +
AMBIGUOUS 2), runs the real `_select_skills` through the real
`evaluate_skill_selection` with no stubs, and `runtime/` is byte-unmodified (the
#250 diff touches only the note + checklist).

## (ii) NO-FLIP reasoning — SOUND, within reviewer scope

- **Reviewer-step framing is correct.** Scoping note #241 §1e (as corrected in
  its own review): §6.9 has no operator language and no task list; roadmap line
  1754's "review/operator promotion gate" is Wave 6, not §6.9; §17.3 lists
  "explicit operator decision" as an *available*, not required, DONE-evidence
  path. The note cites all of this correctly and does not overstep into an
  operator-authority call.
- **The DONE argument is legitimate, not over-cautious.** §6.9's "Promotion
  gate" sentence is immediately preceded by "Routing evaluation must include"
  listing the six categories (roadmap 699–708) — reading those as the
  acceptance surface is the natural reading. Three of six score 0.00.
  HARD_NEGATIVE 4/4 false-activation is not "a weak baseline" — it means
  `_select_skills` has no relevance judgement at all (any-token-overlap fires),
  so it is not yet a routing *decision*. Flipping 6.9/S6 to DONE because a
  measuring document now exists, while the measured capability fails half its
  own categories, is exactly the `ROADMAP_TRAJECTORY_CHECK.md` / §17.3
  anti-pattern the note names.
- **Not under-cautious.** §4 acknowledges the downstream containment (6.22 trust
  gate + SEC4 quarantine bound the *safety* blast radius, not routing
  correctness — a false activation is trust-gated evidence, not an execution).
  §5 records both DONE paths (a reviewed `_select_skills` quality PR re-run
  against EXP-B, or a §17.3 operator sign-off on the characterized behaviour).

## (iii) No status cell moved — VERIFIED

`git diff` of `CAPABILITY_CHECKLIST.md`, status column both sides:
- **6.9** — `IN PROGRESS` → `IN PROGRESS`
- **S6** — `IN PROGRESS` → `IN PROGRESS`
- **L4** — `IN PROGRESS` → `IN PROGRESS`

Only prose/evidence clauses added (the frozen eval exists + covers six
categories; the gate step returned NO FLIP; next step = selector work or
operator sign-off). Note §6 states "No status cell changes value" — confirmed.

Coordinator note: the rebase onto current main resolved a `CAPABILITY_CHECKLIST.md`
conflict on the 6.9 / 6.10 rows — 6.9 takes #250's NO-FLIP text, 6.10 keeps the
#245 (Half 3 slice 1) text. No status token changed on either side.

## Verdict: APPROVE

`python3 -m runtime.smoke` → exit 0.

reviewer: maps-lean-luve
head_sha: ba84756673d5ed101cd0b4ba7f501fa59f77f3e5
independent: true
summary: APPROVE — independent verification review of the docs-only 6.9/S6 promotion gate-step record; the coverage/existence facts are independently re-verified correct (EXP-B re-run: 4 of 7 category metrics at 1.0, 3 at 0.0, f1 0.7222, sha256 matches), the NO-FLIP decision is a sound and appropriately-scoped reviewer call grounded in §6.9's six-category acceptance surface + the HARD_NEGATIVE 4/4 false-activation (no relevance judgement) + the status-truth rule, and no checklist status cell moved (6.9/S6/L4 all stay IN PROGRESS, prose only).
