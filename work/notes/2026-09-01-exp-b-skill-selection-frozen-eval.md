# EXP-B: expanded frozen Skill-selection evaluation — results

Status: `EVIDENCE — EXP-B RUN AND LABELED. 6.9/S6 promotion gate: coverage +
existence MET; the DONE flip is a separate reviewer gate step (see §6).`

Implements `work/notes/2026-09-01-6.9-frozen-selection-eval-scoping.md` §4.
EXP-A (`work/notes/2026-08-19-exp-a-skill-routing-benchmark.md`, 12 cases, 6 of
8 categories) is the predecessor; EXP-B expands the frozen corpus to **25
cases** with **≥ 4 deliberate cases in every one of §6.9's six required
categories**.

**Evaluation-only.** No production file changed behaviour:
`runtime/context_builder.py`, `runtime/skills/evaluation.py`,
`runtime/skills/catalog.py`, `runtime/skills/format.py` are byte-for-byte
unmodified. New files only:

- `runtime/skills/eval_corpora/exp_a_skill_routing_v2.json` — the frozen corpus
  (`version: "exp-a-skill-routing-v2"`, `sha256:
  2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565`).
- `tests/test_exp_b_skill_routing.py` — builds a real `SkillCatalog` from
  on-disk `SKILL.md`, runs the real `_select_skills` per case, calls the real
  `evaluate_skill_selection`, and pins the observed behaviour.

`exp_a_skill_routing_v1.json` and `test_exp_a_skill_routing.py` are untouched
(v1 stays a frozen historical artifact).

## What §6.9's gate actually requires (per scoping note §1)

Roadmap `00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6.9 "Promotion gate" (lines
706–708): *"Do not rely on fuzzy Skill selection without a frozen selection
evaluation"*, preceded by "Routing evaluation must include" (lines 699–704):
`direct matches; paraphrases; vocabulary shifts; overlapping Skills; hard
negatives; no-Skill cases`. It is a **coverage + existence** bar — **no numeric
threshold**. The "meaningful improvement over baseline" language elsewhere in
the roadmap (L1383/L1961/L796) is the L4/EXP-B *semantic-retrieval* gate, not
this one; `_select_skills` is already explicit-first token intersection — it
*is* the baseline.

## Corpus composition — all six §6.9 categories with depth

| §6.9 category | `SkillSelectionCategory` | Cases | Case IDs |
|---|---|---|---|
| direct matches | `DIRECT` | 5 | EXPB-D01..D05 |
| paraphrases | `PARAPHRASE` | 4 | EXPB-P01..P04 |
| vocabulary shifts | `VOCABULARY_SHIFT` | 4 | EXPB-V01..V04 |
| overlapping Skills | `MULTI_SKILL` + `AMBIGUOUS` | 2 + 2 | EXPB-M01..M02, EXPB-A01..A02 |
| hard negatives | `HARD_NEGATIVE` | 4 | EXPB-H01..H04 |
| no-Skill cases | `NO_SKILL` | 4 | EXPB-N01..N04 |

7 candidate Skills (`incident-response-playbook`, `secrets-rotation`,
`api-contract-review`, `load-test-planning`, `changelog-authoring`,
`data-migration-runbook`, `dependency-upgrade-review`), with deliberately
concept-word-controlled descriptions so every token overlap is intentional.
`NEAR_MISS` is not included — §6.9 does not list it, and it is hard to author
cleanly against a pure token selector without collapsing into `HARD_NEGATIVE`.

The 5 `DIRECT` cases cover 5 of the 7 candidate Skills; `changelog-authoring`
and `dependency-upgrade-review` have no `DIRECT` case (they appear only in
`PARAPHRASE` / `MULTI_SKILL` / `HARD_NEGATIVE` cases). §6.9 requires ≥ 4 direct
matches, not one per Skill, so this is within the bar — noted for a reviewer
weighing per-Skill `DIRECT` confidence.

### Authoring discipline

- **PARAPHRASE** cases reword the intent in prose; the deciding overlap is
  carried by the structured fixture fields (`task_type` / `project_id` /
  output-path stems), and the authoring constraint applied was **the overlap
  must not rest *solely* on tokens shared with the Skill name** — tokens that a
  Skill-name synonym alone would supply (`steps`, `upgrade`, `impact`, …) were
  deliberately stripped from the fixtures. Two of the four (EXPB-P01
  `migration` via the output path; EXPB-P03 `dependency` via `task_type`) do
  contain one token that also appears in the target Skill's *name*, but in both
  the selection is additionally carried by description-unique concept words
  (P01: `schema` / `backfill` / `cutover` / `database`; P03: `transitive` /
  `advisory` / `lockfile` / `bump`) — so PARAPHRASE = 1.00 is a partial floor
  for those two, not a pure name-token match. The four VOCABULARY_SHIFT cases
  are the ones that avoid *every* name and description token (→ ABSTAIN).
- **VOCABULARY_SHIFT** cases use genuine synonyms the exact-token selector
  cannot see (`credential`≠`credentials`, `renew`≠`rotation`, `brownout`≠`outage`).
  `expected_outcome` is `SELECT` — recording what a robust selector *should* do;
  the selector's actual `ABSTAIN` is the documented recall gap.
- **AMBIGUOUS** cases expect an `AMBIGUOUS` outcome S6 never produces, so they
  are always non-exact — they document that S6 has no disambiguation, and the
  harness reports `ambiguity_misses` rather than failing.
- **HARD_NEGATIVE** cases share one *accidental* token with a Skill (`load` in
  a frontend-fixture task, `rotation` in logrotate) and correctly want `ABSTAIN`;
  the any-token-overlap selector false-activates, which is the point.

## Result — the real selector on the frozen corpus

`python3 -m unittest tests.test_exp_b_skill_routing -v` prints the full report.
At `origin/main` `891045e`:

| Metric | Value |
|---|---|
| `total_cases` | 25 |
| `exact_cases` / `exact_rate` | 15 / 0.60 |
| `selection_precision` | 0.684 |
| `selection_recall` | 0.765 |
| `selection_f1` | 0.722 |
| `missed_activation_cases` | 4 (all `VOCABULARY_SHIFT`) |
| `false_activation_cases` | 4 (all `HARD_NEGATIVE`) |
| `ambiguity_misses` | 2 (both `AMBIGUOUS`) |

**Per-category accuracy (exact rate):**

| Category | Accuracy | Reading |
|---|---|---|
| DIRECT | **1.00** | token selector is reliable when the task vocabulary matches the Skill's |
| PARAPHRASE | **1.00** | reliable when a reworded task still shares ≥1 unique concept token |
| MULTI_SKILL | **1.00** | correctly surfaces both Skills when both genuinely apply |
| NO_SKILL | **1.00** | correctly abstains when nothing overlaps |
| VOCABULARY_SHIFT | **0.00** | **blind to synonym shifts** — literal-token matching only |
| HARD_NEGATIVE | **0.00** | **false-activates on any accidental shared token** — no relevance judgement |
| AMBIGUOUS | **0.00** | **no disambiguation** — always returns a flat SELECT list |

## Interpretation

The current `_select_skills` is a **precise but brittle** literal-token matcher:

- **Strong** where the task's declared signals (`task_type` / `project_id` /
  output-path stems) share vocabulary with the Skill — direct, paraphrase, and
  multi-Skill cases are all exact.
- **Blind** to (a) the same intent expressed in different words
  (`VOCABULARY_SHIFT` — 0/4), (b) an irrelevant task that happens to share one
  token (`HARD_NEGATIVE` — 4/4 false activations), and (c) genuine ambiguity
  (`AMBIGUOUS` — no confidence signal).

These are exactly the failure classes §6.9's "Routing evaluation must include"
list names. They are **recorded, not tuned away**: the frozen test pins them,
and a future selector change that shifts the balance fails the test (update the
assertions only alongside a deliberate, reviewed selector change).

The 6.22 memory trust gate and SEC4 quarantine sit **downstream** of selection,
so a false activation surfaces a Skill as *evidence* that is then trust-gated —
it does not silently execute. A missed activation costs recall, not safety.

## §criterion — optional additional rigor (NOT required by §6.9, for the reviewer)

§6.9 mandates only coverage + existence. A reviewer running the promotion gate
*may* additionally apply a numeric bar. Proposed shape (values are the
reviewer's call, not set here — scoping note §1d/§1e):

1. **Coverage** — ≥ 4 cases in each of the six categories. **MET** (5/4/4/4/4/4).
2. **Precise-vocabulary categories hold** — DIRECT + PARAPHRASE + MULTI_SKILL +
   NO_SKILL exact rate ≥ `<floor>`. **Observed: 1.00** across all four.
3. **Hard-negative / no-Skill safety** — `false_activation_cases` among
   `HARD_NEGATIVE` ∪ `NO_SKILL` ≤ `<cap>`. **Observed: 4** (all in
   `HARD_NEGATIVE`; `NO_SKILL` clean). Whether 4/4 hard-negative false
   activations clears the bar for a `P2` capability with a downstream trust gate
   is the reviewer's judgement.
4. **Aggregate** — `selection_f1 ≥ <bar>`. **Observed: 0.722.**

## §6 — the promotion decision (reviewer gate step, NOT this slice)

This slice establishes: **a frozen selection evaluation exists and covers §6.9's
six categories** — the coverage + existence bar is **MET**.

Flipping `6.9` / `S6` to `DONE` is a separate **reviewer** step (scoping note
§1e — no operator decision required by §6.9; the operator *may* weigh in under
§17.3 but it is not required). That step: (a) confirm coverage + existence
against this corpus, (b) optionally set and apply the §criterion floors above,
(c) decide whether the characterized behaviour — perfect on precise vocabulary,
blind on synonym / hard-negative / ambiguity — is acceptable to promote a `P2`
routing capability, or whether the missed classes motivate selector work first
(a *separate, reviewed* PR — do not tune the selector to a number).

**This PR does not flip the status.** The `CAPABILITY_CHECKLIST.md` clause it
adds records only that the expanded frozen eval exists.

## Resume prompt — the 6.9 promotion gate step

You are running the **6.9 / S6 promotion gate** for MAPS_Lean. Source: this
note + `work/notes/2026-09-01-6.9-frozen-selection-eval-scoping.md` §1e/§5 +
roadmap §6.9 lines 699–708.

The frozen selection evaluation now exists (`runtime/skills/eval_corpora/exp_a_skill_routing_v2.json`
+ `tests/test_exp_b_skill_routing.py`, 25 cases, ≥4 per §6.9 category, real
`_select_skills` through real `evaluate_skill_selection`, sha256 pinned). Run
`python3 -m unittest tests.test_exp_b_skill_routing -v` and read the report.

Decide, as a reviewer (no operator decision is required by §6.9): does the
coverage + existence bar plus the characterized behaviour (§Interpretation —
1.00 on DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL, 0.00 on VOCABULARY_SHIFT/
HARD_NEGATIVE/AMBIGUOUS) clear 6.9's "do not rely on fuzzy Skill selection
without a frozen selection evaluation"? Optionally set the §criterion floors.

- **If yes:** flip `6.9` and `S6` to `DONE` in `CAPABILITY_CHECKLIST.md` with
  this note + the test module as evidence (§17.3). Note in the row that the
  selector is a literal-token matcher with documented VOCABULARY_SHIFT /
  HARD_NEGATIVE / AMBIGUOUS gaps that the frozen test pins.
- **If no:** record which category(ies) fall short of the bar you set; the
  next 6.9 slice is selector work (add near-synonym / stopword handling, a
  relevance threshold, or a confidence signal for AMBIGUOUS) as a separate
  reviewed PR — the frozen corpus then re-runs as the acceptance test.

Do not modify the selector or the corpus to make the gate pass.
