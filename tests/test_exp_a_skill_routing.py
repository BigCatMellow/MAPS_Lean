"""EXP-A: Skill-routing frozen-corpus benchmark.

Roadmap: `work/roadmaps/agent-harness-capabilities/05-learning-and-evaluation.md`
phase L4 ("Research experiments A-E"), task-backlog item 12 ("Build EXP-A
Skill-selection frozen eval corpus").

This module is evaluation-only: it does not modify
`runtime/context_builder.py`, `runtime/skills/evaluation.py`,
`runtime/skills/catalog.py`, or `runtime/skills/format.py`. It runs the real
production selector (`runtime.context_builder._select_skills`) against a
frozen corpus through the real eval harness
(`runtime.skills.evaluation.evaluate_skill_selection`), building a real
`SkillCatalog` from on-disk `SKILL.md` files (the same construction idiom
`tests/test_context_builder.py` uses) so nothing under test is a stub.

The frozen corpus at
`runtime/skills/eval_corpora/exp_a_skill_routing_v1.json` stores, per case,
both the `SkillSelectionCorpus` schema fields (`task`, `category`,
`expected_outcome`, `expected_skills`, ...) *and* the literal
`task_type`/`project_id`/`output_paths` fixture fields that
`_select_skills` actually reads. `load_skill_selection_corpus` ignores the
extra fixture fields (they are not part of its schema); this module reads
them directly from the raw JSON to build the task dict fed to
`_select_skills`.
"""

from __future__ import annotations

import json
import tempfile
import unittest
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
    / "exp_a_skill_routing_v1.json"
)


def _load_raw_fixtures() -> dict[str, dict[str, object]]:
    """Read the task_type/project_id/output_paths fixture fields per case_id.

    These fields drive the real `_select_skills` selector but are not part
    of the `SkillSelectionCorpus` schema, so they are read directly from the
    raw JSON rather than through `load_skill_selection_corpus`.
    """

    raw = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    fixtures: dict[str, dict[str, object]] = {}
    for item in raw["cases"]:
        fixtures[item["id"]] = {
            "task_type": item.get("task_type"),
            "project_id": item.get("project_id"),
            "output_paths": item.get("output_paths", []),
        }
    return fixtures


class ExpASkillRoutingBenchmarkTests(unittest.TestCase):
    """Runs the real S6 selector through the real S4 eval harness."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_skill_selection_corpus(CORPUS_PATH)
        cls.fixtures = _load_raw_fixtures()

    def _build_catalog(self):
        """Construct a real SkillCatalog with one on-disk SKILL.md per candidate.

        Mirrors the `_write_skill`/`build_skill_catalog` idiom in
        `tests/test_context_builder.py`: real files discovered by
        `discover_skills`, not hand-built descriptor stubs.
        """

        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        skills_root = Path(tmp_dir.name) / "skills-src"
        skills_root.mkdir()
        for candidate in self.corpus.candidates:
            skill_dir = skills_root / candidate.name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {candidate.name}\ndescription: {candidate.description}\n---\n"
                "Procedure body (not read by selection; selection only ever "
                "reads descriptor name/description).\n",
                encoding="utf-8",
            )
        source = SkillCatalogSource(
            source_id="exp-a-corpus",
            root=skills_root,
            kind=SkillSourceKind.LOCAL,
        )
        return build_skill_catalog([source])

    def _run_predictions(self) -> list[SkillSelectionPrediction]:
        catalog = self._build_catalog()
        predictions: list[SkillSelectionPrediction] = []
        for case in self.corpus.cases:
            fixture = self.fixtures[case.case_id]
            task = {
                "task_type": fixture["task_type"],
                "project_id": fixture["project_id"],
                "output_paths": fixture["output_paths"],
            }
            selected = _select_skills(catalog, task)
            selected_names = tuple(item["name"] for item in selected)
            if not selected_names:
                outcome = SkillSelectionOutcome.ABSTAIN
            else:
                # `_select_skills` has no ambiguity concept of its own (S6 does
                # not implement an AMBIGUOUS outcome); any non-empty result is
                # a SELECT for the purposes of this eval, consistent with
                # `evaluate_skill_selection`'s SELECT/ABSTAIN/AMBIGUOUS model
                # where AMBIGUOUS is reserved for corpus cases that expect it.
                outcome = SkillSelectionOutcome.SELECT
            predictions.append(
                SkillSelectionPrediction(
                    case_id=case.case_id,
                    outcome=outcome,
                    selected_skills=selected_names,
                )
            )
        return predictions

    def test_corpus_composition(self) -> None:
        self.assertEqual(self.corpus.version, "exp-a-skill-routing-v1")
        self.assertEqual(len(self.corpus.candidates), 5)
        self.assertEqual(len(self.corpus.cases), 12)
        categories = {case.category.value for case in self.corpus.cases}
        self.assertEqual(
            categories,
            {
                "DIRECT",
                "PARAPHRASE",
                "VOCABULARY_SHIFT",
                "HARD_NEGATIVE",
                "NO_SKILL",
                "MULTI_SKILL",
            },
        )

    def test_real_selector_through_real_eval_harness(self) -> None:
        """Runs `_select_skills` through `evaluate_skill_selection` and prints the report.

        This is the EXP-A experiment itself. The report is printed (not just
        asserted) so `python3 -m unittest tests.test_exp_a_skill_routing -v`
        produces the numbers reported in
        `work/notes/2026-08-19-exp-a-skill-routing-benchmark.md`.

        Assertions below encode the *known, documented* outcome of this
        specific frozen corpus against the current production selector: two
        designed-clean DIRECT/PARAPHRASE/MULTI_SKILL/HARD_NEGATIVE-2/NO_SKILL
        cases pass exactly, one VOCABULARY_SHIFT case is a genuine missed
        activation (literal-token-only matching cannot see a pure synonym
        shift), and one HARD_NEGATIVE case is a genuine false activation
        (the selector's any-token-overlap rule fires on the shared word
        "writing"). If a future change to `_select_skills` alters this
        balance, that is exactly the kind of regression this frozen corpus
        exists to catch -- update the assertions only alongside a deliberate,
        reviewed change to the selector, not to make a run pass.
        """

        predictions = self._run_predictions()
        report = evaluate_skill_selection(self.corpus, predictions)

        print("\n--- EXP-A Skill-routing benchmark report ---")
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))

        self.assertEqual(report.total_cases, 12)
        self.assertEqual(report.corpus_sha256, self.corpus.sha256)

        # Documented, expected imperfections of the real selector on this
        # corpus (see corpus notes on EXPA-007 and EXPA-008):
        self.assertEqual(report.missed_activation_cases, 1)
        self.assertEqual(report.false_activation_cases, 1)
        self.assertEqual(report.exact_cases, 10)
        self.assertEqual(report.exact_rate, 10 / 12)

        by_case = {result.case_id: result for result in report.case_results}
        self.assertEqual(
            by_case["EXPA-007"].predicted_outcome, SkillSelectionOutcome.ABSTAIN
        )
        self.assertFalse(by_case["EXPA-007"].exact)
        self.assertEqual(
            by_case["EXPA-008"].predicted_outcome, SkillSelectionOutcome.SELECT
        )
        self.assertEqual(
            by_case["EXPA-008"].predicted_skills, ("changelog-authoring",)
        )
        self.assertFalse(by_case["EXPA-008"].exact)

        # Every other case is exact.
        for case_id, result in by_case.items():
            if case_id in {"EXPA-007", "EXPA-008"}:
                continue
            self.assertTrue(result.exact, f"{case_id} expected to be exact: {result}")

        self.assertGreater(report.selection_precision, 0.0)
        self.assertLess(report.selection_precision, 1.0)
        self.assertGreater(report.selection_recall, 0.0)
        self.assertLess(report.selection_recall, 1.0)


if __name__ == "__main__":
    unittest.main()
