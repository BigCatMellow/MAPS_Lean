"""Focused tests for the TASK-260 frozen holdout harness."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from MAP_System.scripts import task_memory_fts as memory
from MAP_System.scripts import task_memory_fts_holdout as holdout


class TaskMemoryFtsHoldoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "Source"
        self.tasks = self.repo / "MAP_System" / "tasks"
        self.tasks.mkdir(parents=True)
        self._write(
            "MAP_System/scripts/alpha.py",
            '"""Validate alpha records."""\ndef validate_alpha():\n    return True\n',
        )
        self._write(
            "MAP_System/tests/test_alpha.py",
            '"""Test alpha validation."""\ndef test_alpha():\n    assert True\n',
        )
        self._write(
            "MAP_System/artifacts/recovery.md",
            "# Agent Recovery\n\nNudge and reclaim a quiet agent.\n",
        )
        self._task(
            "TASK-001",
            "Validate alpha records",
            "Reject invalid alpha records.",
            ["MAP_System/scripts/alpha.py", "MAP_System/tests/test_alpha.py"],
        )
        self._task(
            "TASK-002",
            "Specify agent recovery",
            "Nudge and reclaim a quiet agent.",
            ["MAP_System/artifacts/recovery.md"],
        )
        self.db = Path(self.temp.name) / "holdout.db"
        memory.build_database(
            self.db,
            ["TASK-001", "TASK-002"],
            tasks_dir=self.tasks,
            repo=self.repo,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write(self, relative: str, text: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _task(self, task_id: str, title: str, description: str, outputs: list[str]) -> None:
        payload = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "status": "RELEASED",
            "output_paths": outputs,
            "acceptance_criteria": [description],
        }
        (self.tasks / f"{task_id}.json").write_text(json.dumps(payload), encoding="utf-8")

    def _valid_spec(self) -> dict:
        queries = []
        for index in range(8):
            compound = index < 2
            queries.append({
                "id": f"F{index + 1}",
                "question": "What validates alpha records and how is recovery handled?" if compound else "What validates alpha records?",
                "work_area": f"area-{index % 5}",
                "expected_task_ids": ["TASK-001", "TASK-002"] if compound else ["TASK-001"],
                "expected_source_paths": ["MAP_System/scripts/alpha.py"],
                "expected_source_roles": ["implementation"],
                "source_justifications": ["Executable validation mechanism."],
            })
        for index in range(3):
            queries.append({
                "id": f"N{index + 1}",
                "question": f"Which task implemented absent capability {index}?",
                "work_area": "negative",
                "expected_task_ids": [],
                "expected_source_paths": [],
                "expected_source_roles": [],
                "source_justifications": [],
                "no_match_reason": "Both corpus task records were checked.",
            })
        return {
            "corpus_task_ids": ["TASK-001", "TASK-002"],
            "queries": queries,
        }

    def test_valid_spec_contract_passes(self) -> None:
        findings = holdout.validate_spec(
            self._valid_spec(), tasks_dir=self.tasks, repo=self.repo
        )
        self.assertEqual([], findings)

    def test_contract_rejects_too_few_negatives_and_compounds(self) -> None:
        spec = self._valid_spec()
        spec["queries"] = [query for query in spec["queries"] if not query["id"].startswith("N")]
        spec["queries"][1]["expected_task_ids"] = ["TASK-001"]
        findings = holdout.validate_spec(spec, tasks_dir=self.tasks, repo=self.repo)
        self.assertTrue(any("no-match" in finding for finding in findings))
        self.assertTrue(any("compound" in finding for finding in findings))

    def test_task_only_ablation_returns_direct_task_candidates(self) -> None:
        with sqlite3.connect(self.db) as conn:
            tasks = holdout.task_only_search(conn, "invalid alpha validation")
        self.assertEqual("TASK-001", tasks[0])

    def test_algorithm_metrics_records_full_and_task_only_rankings(self) -> None:
        spec = {
            "queries": [{
                "id": "X1",
                "question": "What validates invalid alpha records?",
                "expected_task_ids": ["TASK-001"],
                "expected_source_paths": ["MAP_System/scripts/alpha.py"],
            }]
        }
        with sqlite3.connect(self.db) as conn:
            metrics, results = holdout.algorithm_metrics(conn, spec)
        self.assertEqual(1.0, metrics["task_recall_at_6"])
        self.assertEqual(1.0, metrics["task_only_recall_at_6"])
        self.assertIn("X1", results)
        self.assertIn("task_only_returned_tasks", metrics["per_query"][0])

    def test_packet_is_bounded_and_shows_temporal_mode(self) -> None:
        query = {"id": "X1", "question": "What validates invalid alpha records?"}
        with sqlite3.connect(self.db) as conn:
            result = memory.search(conn, query["question"])
        packet, estimate = holdout.render_packet(
            query,
            result,
            corpus_count=2,
            ceiling=1800,
            watermark="frozen",
        )
        self.assertLessEqual(estimate, 1800)
        self.assertIn("current_unique", packet)
        self.assertIn("no strong match is a valid answer", packet)


if __name__ == "__main__":
    unittest.main()
