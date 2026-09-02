"""EXP-B: expanded frozen Skill-selection evaluation (the 6.9 promotion gate).

Roadmap: `00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6.9 "Routing evaluation must
include" (direct matches / paraphrases / vocabulary shifts / overlapping Skills
/ hard negatives / no-Skill cases) + `work/notes/2026-09-01-6.9-frozen-selection-eval-scoping.md`
§4. EXP-A (`test_exp_a_skill_routing.py`, 12 cases) is the predecessor; EXP-B
expands it to a frozen corpus with ≥4 deliberate cases in every §6.9 category.

Evaluation-only. This module does not modify `runtime/context_builder.py`,
`runtime/skills/evaluation.py`, `runtime/skills/catalog.py`, or
`runtime/skills/format.py`. It runs the real production selector
(`runtime.context_builder._select_skills`) against the frozen corpus at
`runtime/skills/eval_corpora/exp_a_skill_routing_v2.json` through the real eval
harness (`runtime.skills.evaluation.evaluate_skill_selection`), building a real
`SkillCatalog` from on-disk `SKILL.md` files — nothing under test is a stub.

The assertions pin the *observed* behaviour of the selector on this frozen
corpus. Updated alongside the 6.9/S6 selector-quality change (design note
`work/notes/2026-09-02-6.9-s6-selector-quality-scoping.md`, results note
`work/notes/2026-09-02-6.9-s6-selector-quality-results.md`): `_select_skills`
now applies a match-strength gate instead of "any shared token selects", which
closed the HARD_NEGATIVE category:
  * HARD_NEGATIVE cases — an incidental single generic-word overlap no longer
    surfaces a Skill; every case now `ABSTAIN`s (`false_activation_cases` 4 → 0).
  * VOCABULARY_SHIFT cases — still `missed_activation_cases`. Literal-token
    matching cannot see a synonym shift, and V01's post-normalisation match
    (one distinctive token) is lexically indistinguishable from the
    hard-negatives the strength gate rejects — closing it needs the semantic
    work roadmap 6.33 gates, out of scope here.
  * AMBIGUOUS cases — still `ambiguity_misses`. S6 has no `AMBIGUOUS` outcome,
    and A01/A02 are not score-ties (the token evidence favours one candidate),
    so a confidence/margin rule cannot separate them from a genuine
    MULTI_SKILL tie without regressing that category.
If a future `_select_skills` change alters this balance, this frozen corpus is
what catches it — update the assertions only alongside a deliberate, reviewed
selector change.

The 6.9 promotion gate is a *coverage + existence* bar (roadmap 706–708): a
frozen selection evaluation must exist and cover the six categories. This module
establishes that. Whether to flip 6.9/S6 to DONE (optionally against the
proposed `work/notes/2026-09-01-exp-b-skill-selection-frozen-eval.md` §criterion)
is a separate reviewer gate step — this module and the corpus do not assert it.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from runtime.context_builder import _select_skills
from runtime.skills import (
    SkillCatalogSource,
    SkillSelectionOutcome,
    SkillSelectionPrediction,
    SkillSourceKind,
    build_skill_catalog,
    evaluate_skill_selection,
    load_skill_selection_corpus,
)


CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "skills"
    / "eval_corpora"
    / "exp_a_skill_routing_v2.json"
)

_NON_OVERLAPPING_CATEGORIES = {
    "DIRECT",
    "PARAPHRASE",
    "VOCABULARY_SHIFT",
    "HARD_NEGATIVE",
    "NO_SKILL",
}
# §6.9's sixth category, "overlapping Skills", is MULTI_SKILL + AMBIGUOUS
# together (design note §4a) — depth-checked as a combined count below.
_OVERLAPPING = {"MULTI_SKILL", "AMBIGUOUS"}


class ExpBSkillRoutingBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_skill_selection_corpus(CORPUS_PATH)
        raw = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
        cls.fixtures = {
            item["id"]: {
                "task_type": item.get("task_type"),
                "project_id": item.get("project_id"),
                "output_paths": item.get("output_paths", []),
            }
            for item in raw["cases"]
        }

    def _build_catalog(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        skills_root = Path(tmp_dir.name) / "skills-src"
        skills_root.mkdir()
        for candidate in self.corpus.candidates:
            skill_dir = skills_root / candidate.name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {candidate.name}\ndescription: {candidate.description}\n---\n"
                "Procedure body (not read by selection).\n",
                encoding="utf-8",
            )
        source = SkillCatalogSource(
            source_id="exp-b-corpus",
            root=skills_root,
            kind=SkillSourceKind.LOCAL,
        )
        return build_skill_catalog([source])

    def _run_predictions(self):
        catalog = self._build_catalog()
        predictions = []
        for case in self.corpus.cases:
            fixture = self.fixtures[case.case_id]
            selected, _ = _select_skills(
                catalog,
                {
                    "task_type": fixture["task_type"],
                    "project_id": fixture["project_id"],
                    "output_paths": fixture["output_paths"],
                },
            )
            names = tuple(item["name"] for item in selected)
            outcome = (
                SkillSelectionOutcome.SELECT if names else SkillSelectionOutcome.ABSTAIN
            )
            predictions.append(
                SkillSelectionPrediction(
                    case_id=case.case_id,
                    outcome=outcome,
                    selected_skills=names,
                )
            )
        return predictions

    def test_corpus_is_frozen(self) -> None:
        self.assertEqual(self.corpus.version, "exp-a-skill-routing-v2")
        # sha256 is a pure function of the canonical corpus content.
        self.assertEqual(
            self.corpus.sha256, "2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565"
        )

    def test_corpus_covers_every_6_9_category_with_depth(self) -> None:
        counts = Counter(case.category.value for case in self.corpus.cases)
        for category in _NON_OVERLAPPING_CATEGORIES:
            self.assertGreaterEqual(
                counts[category], 4, f"{category}: {counts[category]} (< 4)"
            )
        self.assertGreaterEqual(
            counts["MULTI_SKILL"] + counts["AMBIGUOUS"],
            4,
            f"overlapping Skills: {counts['MULTI_SKILL']}+{counts['AMBIGUOUS']} (< 4)",
        )
        self.assertEqual(
            set(counts) - _NON_OVERLAPPING_CATEGORIES - _OVERLAPPING,
            set(),
            "unexpected category present",
        )
        self.assertEqual(len(self.corpus.cases), 25)
        self.assertEqual(len(self.corpus.candidates), 7)

    def test_real_selector_through_real_eval_harness(self) -> None:
        predictions = self._run_predictions()
        report = evaluate_skill_selection(self.corpus, predictions)

        print("\n--- EXP-B expanded Skill-routing benchmark report ---")
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))

        self.assertEqual(report.total_cases, 25)
        self.assertEqual(report.corpus_sha256, self.corpus.sha256)

        by_case = {r.case_id: r for r in report.case_results}

        # Every AMBIGUOUS case is a documented ambiguity miss (S6 has no
        # AMBIGUOUS outcome).
        for case in self.corpus.cases:
            if case.category.value == "AMBIGUOUS":
                self.assertFalse(
                    by_case[case.case_id].exact,
                    f"{case.case_id}: S6 cannot produce AMBIGUOUS, so exact must be False",
                )

        # Every HARD_NEGATIVE case now ABSTAINs — the 6.9/S6 match-strength gate
        # rejects an incidental single generic-word overlap (was: every case
        # false-activated under "any shared token selects").
        for case in self.corpus.cases:
            if case.category.value == "HARD_NEGATIVE":
                self.assertEqual(
                    by_case[case.case_id].predicted_outcome,
                    SkillSelectionOutcome.ABSTAIN,
                    f"{case.case_id}: 6.9/S6 gate must reject the hard negative",
                )

        # Documented aggregate balance of the selector on this frozen corpus
        # after the 6.9/S6 selector-quality change (results note
        # work/notes/2026-09-02-6.9-s6-selector-quality-results.md): exact
        # 15 → 19, false activations 4 → 0, precision 0.68 → 1.0, recall
        # unchanged at 0.76. VOCABULARY_SHIFT (4 misses) and AMBIGUOUS (2
        # misses) are unchanged — documented §6.33-class residuals.
        self.assertEqual(report.exact_cases, 19)
        self.assertEqual(report.missed_activation_cases, 4)
        self.assertEqual(report.false_activation_cases, 0)
        self.assertEqual(report.ambiguity_misses, 2)
        self.assertEqual(report.selection_precision, 1.0)


if __name__ == "__main__":
    unittest.main()
