"""Focused tests for the TASK-263 / EXP-0006 disposable claim-evidence pilot."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_memory_claim_evidence_pilot as pilot  # noqa: E402


class AttributeSymbolTests(unittest.TestCase):
    def test_unique_link_needs_no_evidence(self) -> None:
        origin, method, confidence = pilot.attribute_symbol(
            linked_task_ids=["TASK-100"],
            local_context="",
            header_hints=[],
            symbol_tokens=set(),
            task_text_tokens={},
        )
        self.assertEqual("TASK-100", origin)
        self.assertEqual("unique_link", method)
        self.assertEqual(1.0, confidence)

    def test_prefers_inline_tag_over_fallback(self) -> None:
        origin, method, _ = pilot.attribute_symbol(
            linked_task_ids=["TASK-080", "TASK-083"],
            local_context="fixes the reset bug (TASK-083)",
            header_hints=[("TASK-080", "v1 (TASK-080): original behavior")],
            symbol_tokens={"reset", "bug"},
            task_text_tokens={
                "TASK-080": {"reset", "watcher"},
                "TASK-083": {"silent", "stop"},
            },
        )
        self.assertEqual("TASK-083", origin)
        self.assertEqual("inline_tag", method)

    def test_falls_back_to_version_header(self) -> None:
        origin, method, _ = pilot.attribute_symbol(
            linked_task_ids=["TASK-080", "TASK-083"],
            local_context="no tag here at all",
            header_hints=[
                ("TASK-080", "v1 (TASK-080): recorded-reset-only nudges"),
                ("TASK-083", "v2 (TASK-083): silent stop detection"),
            ],
            symbol_tokens={"silent", "stop", "detection"},
            task_text_tokens={
                "TASK-080": {"reset", "watcher"},
                "TASK-083": {"silent", "stop"},
            },
        )
        self.assertEqual("TASK-083", origin)
        self.assertEqual("version_header_match", method)

    def test_falls_back_to_acceptance_text_overlap(self) -> None:
        origin, method, _ = pilot.attribute_symbol(
            linked_task_ids=["TASK-001", "TASK-002"],
            local_context="",
            header_hints=[],
            symbol_tokens={"create", "artifact"},
            task_text_tokens={
                "TASK-001": {"unrelated", "topic"},
                "TASK-002": {"create", "artifact", "template"},
            },
        )
        self.assertEqual("TASK-002", origin)
        self.assertEqual("acceptance_criteria_match", method)

    def test_undifferentiated_fallback_is_deterministic(self) -> None:
        origin, method, confidence = pilot.attribute_symbol(
            linked_task_ids=["TASK-050", "TASK-010"],
            local_context="",
            header_hints=[],
            symbol_tokens={"zzz_no_overlap_anywhere"},
            task_text_tokens={"TASK-050": {"other"}, "TASK-010": {"words"}},
        )
        self.assertEqual("TASK-010", origin)  # lexicographically first, not insertion order
        self.assertEqual("undifferentiated_fallback", method)
        self.assertLess(confidence, 0.5)


class PolarityTests(unittest.TestCase):
    def test_detects_enable_and_block_and_neutral(self) -> None:
        self.assertEqual("enable", pilot.polarity_of({"allowed", "the", "action"}))
        self.assertEqual("block", pilot.polarity_of({"forbids", "the", "action"}))
        self.assertEqual("neutral", pilot.polarity_of({"the", "action"}))


class WatermarkTests(unittest.TestCase):
    def test_earliest_submission_or_approved_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                "\n".join([
                    json.dumps({"type": "PROGRESS", "task_id": "TASK-001", "created_at": "2026-07-01T00:00:00Z"}),
                    json.dumps({"type": "SUBMISSION", "task_id": "TASK-001", "created_at": "2026-07-02T00:00:00Z"}),
                    json.dumps({"type": "APPROVED", "task_id": "TASK-001", "created_at": "2026-07-01T12:00:00Z"}),
                    "not json, ignored",
                ]),
                encoding="utf-8",
            )
            watermarks = pilot.read_events_watermarks(events_path)
            self.assertEqual("2026-07-01T12:00:00Z", watermarks["TASK-001"])


def _write_task(tasks_dir: Path, task_id: str, *, title, description, acceptance, output_paths) -> None:
    (tasks_dir / f"{task_id}.json").write_text(json.dumps({
        "task_id": task_id, "title": title, "description": description,
        "acceptance_criteria": acceptance, "output_paths": output_paths,
    }), encoding="utf-8")


class EndToEndTests(unittest.TestCase):
    def test_positive_match_and_negative_abstention(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            tasks_dir = repo / "MAP_System" / "tasks"
            tasks_dir.mkdir(parents=True)
            scripts_dir = repo / "MAP_System" / "scripts"
            scripts_dir.mkdir(parents=True)

            source = scripts_dir / "widget.py"
            source.write_text(
                '"""Widget module (TASK-900)."""\n\n'
                "def spin_up_widget(name):\n"
                '    """Starts the named widget process."""\n'
                "    return name\n",
                encoding="utf-8",
            )
            _write_task(
                tasks_dir, "TASK-900",
                title="Add widget spin-up",
                description="Implement widget process start-up so operators can launch named widgets.",
                acceptance=["spin_up_widget starts a named widget process"],
                output_paths=["MAP_System/scripts/widget.py"],
            )

            cards, build_meta = pilot.build_claim_cards(["TASK-900"], tasks_dir=tasks_dir, repo=repo)
            self.assertEqual(1, build_meta["claim_card_count"])
            self.assertEqual("TASK-900", cards[0]["task_id"])
            self.assertEqual("spin_up_widget", cards[0]["anchor"])
            self.assertEqual("unique_link", cards[0]["attribution_method"])

            index = pilot.ClaimIndex(cards)
            # MIN_TASK_SCORE is IDF-scaled and calibrated for the ~1400-card real
            # corpus; a one-card synthetic index needs a proportionally lower
            # floor to exercise the matching logic itself, not the production
            # threshold value.
            positive = pilot.retrieve(
                index, "How does the widget process get started by name?", min_task_score=0.5,
            )
            self.assertEqual(["TASK-900"], positive["predicted_task_ids"])
            self.assertEqual("spin_up_widget", positive["predicted_sources"][0]["anchor"])

            negative = pilot.retrieve(
                index, "Which task added distributed consensus voting for cluster leadership?",
                min_task_score=0.5,
            )
            self.assertTrue(negative["abstained"])
            self.assertEqual([], negative["predicted_task_ids"])


class SourceHashDriftTests(unittest.TestCase):
    """Acceptance criterion 4: source-hash drift must be covered directly."""

    def _holdout(self, tmp: Path, rel: str, sha: str) -> dict:
        return {"source_hashes_at_freeze": {rel: sha}}

    def test_unchanged_file_reports_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "sample.py"
            target.write_text("x = 1\n", encoding="utf-8")
            frozen = pilot.base.sha256(target)
            result = pilot.check_source_drift(self._holdout(repo, "sample.py", frozen), repo=repo)
            self.assertTrue(result["clean"])
            self.assertEqual(1, result["unchanged"])
            self.assertEqual([], result["drifted"])

    def test_changed_file_is_reported_as_drifted_with_both_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "sample.py"
            target.write_text("x = 1\n", encoding="utf-8")
            frozen = pilot.base.sha256(target)
            target.write_text("x = 2  # changed after freeze\n", encoding="utf-8")

            result = pilot.check_source_drift(self._holdout(repo, "sample.py", frozen), repo=repo)
            self.assertFalse(result["clean"])
            self.assertEqual(0, result["unchanged"])
            self.assertEqual(1, len(result["drifted"]))
            entry = result["drifted"][0]
            self.assertEqual("sample.py", entry["path"])
            self.assertEqual(frozen, entry["frozen_sha256"])
            self.assertNotEqual(entry["frozen_sha256"], entry["current_sha256"])

    def test_deleted_file_is_reported_missing_not_silently_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = pilot.check_source_drift(
                self._holdout(repo, "gone.py", "0" * 64), repo=repo
            )
            self.assertFalse(result["clean"])
            self.assertEqual(["gone.py"], result["missing"])
            self.assertEqual([], result["drifted"])

    def test_live_holdout_drift_is_surfaced_not_absorbed(self) -> None:
        """The real frozen holdout has known drift; it must be reported."""
        holdout = pilot.load_json(pilot.DEFAULT_HOLDOUT)
        result = pilot.check_source_drift(holdout)
        self.assertEqual(29, result["checked"])
        # Every checked file is accounted for in exactly one bucket.
        self.assertEqual(
            result["checked"],
            result["unchanged"] + len(result["drifted"]) + len(result["missing"]),
        )
        for entry in result["drifted"]:
            self.assertNotEqual(entry["frozen_sha256"], entry["current_sha256"])


class AcceptableSubstituteTests(unittest.TestCase):
    """Acceptance criterion 4: acceptable evidence sets must be covered directly.

    A substitute is credited only when a legitimate alternate source is
    actually RETRIEVED. Regression guard for a real defect: an earlier version
    also credited a hit whenever a missed expected path merely equalled a
    substitute's path, which fired without anything being retrieved because
    several holdout substitutes live in the same file as their expected source.
    """

    def _run(self, query: dict) -> dict:
        holdout = {"queries": [query], "corpus_task_ids": []}
        index = pilot.ClaimIndex([])
        return pilot.evaluate(index, holdout)

    def test_no_substitute_credited_when_nothing_retrieved(self) -> None:
        metrics = self._run({
            "id": "S1",
            "kind": "positive",
            "question": "zzz totally unmatchable query text",
            "expected_task_ids": ["TASK-900"],
            "expected_source_paths": ["MAP_System/scripts/widget.py"],
            "expected_anchors": [],
            # Substitute shares the SAME path as the missed expected source --
            # the exact shape that used to produce a false credit.
            "acceptable_substitutes": [
                {"path": "MAP_System/scripts/widget.py", "anchor": "other_symbol", "why": "alt"}
            ],
        })
        self.assertEqual(0, metrics["acceptable_substitute_hits_on_missed_queries"])
        row = metrics["per_query"][0]
        self.assertFalse(row["substitute_hit"])
        self.assertEqual([], row["matched_substitutes"])
        self.assertEqual(["MAP_System/scripts/widget.py"], row["missed_expected_paths"])

    def test_substitute_credited_when_alternate_actually_retrieved(self) -> None:
        """Expected source is missed, but a declared substitute IS retrieved."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            tasks_dir = repo / "MAP_System" / "tasks"
            tasks_dir.mkdir(parents=True)
            scripts_dir = repo / "MAP_System" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "widget.py").write_text(
                "def read_lock_pid(path):\n"
                '    """Reads the recorded process identifier for staleness."""\n'
                "    return path\n",
                encoding="utf-8",
            )
            _write_task(
                tasks_dir, "TASK-900",
                title="Widget lock", description="Lock staleness handling for widgets.",
                acceptance=["read_lock_pid reads the recorded process identifier"],
                output_paths=["MAP_System/scripts/widget.py"],
            )
            cards, _ = pilot.build_claim_cards(["TASK-900"], tasks_dir=tasks_dir, repo=repo)
            index = pilot.ClaimIndex(cards)

            holdout = {
                "corpus_task_ids": ["TASK-900"],
                "queries": [{
                    "id": "S2",
                    "kind": "positive",
                    "question": "Which code reads the recorded process identifier for staleness?",
                    "expected_task_ids": ["TASK-900"],
                    # Expected source is a file that will NOT be retrieved.
                    "expected_source_paths": ["MAP_System/scripts/never_returned.py"],
                    "expected_anchors": [],
                    # The substitute is what retrieval will actually return.
                    "acceptable_substitutes": [{
                        "path": "MAP_System/scripts/widget.py",
                        "anchor": "read_lock_pid",
                        "why": "legitimate alternate source",
                    }],
                }],
            }
            # MIN_TASK_SCORE is IDF-scaled for the ~1400-card real corpus; a
            # one-card index needs a proportionally lower floor to exercise
            # crediting rather than the production threshold.
            with unittest.mock.patch.object(pilot, "MIN_TASK_SCORE", 0.5):
                metrics = pilot.evaluate(index, holdout)

            row = metrics["per_query"][0]
            self.assertTrue(row["substitute_hit"])
            self.assertEqual(1, metrics["acceptable_substitute_hits_on_missed_queries"])
            self.assertEqual(
                [("MAP_System/scripts/widget.py", "read_lock_pid")],
                [tuple(s) for s in row["matched_substitutes"]],
            )
            # The expected source genuinely was missed -- the credit is for the
            # substitute, not for accidentally satisfying the original.
            self.assertEqual(["MAP_System/scripts/never_returned.py"], row["missed_expected_paths"])
            self.assertEqual([], row["exact_source_hits"])


class HoldoutIntegrityTests(unittest.TestCase):
    def test_generate_refuses_when_holdout_hash_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "holdout.json"
            tampered.write_text(json.dumps({
                "corpus_task_ids": [], "queries": [], "scoring_contract": {"baselines_to_beat": {}},
            }), encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                pilot.generate(tampered, Path(tmp) / "out.json", Path(tmp) / "out.md")
            self.assertIn("hash mismatch", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
