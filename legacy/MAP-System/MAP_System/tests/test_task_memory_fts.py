"""Focused tests for the TASK-259 disposable FTS5/RRF retriever."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from MAP_System.scripts import task_memory_fts as memory


class TaskMemoryFtsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "Source"
        self.root = self.repo / "MAP_System"
        self.tasks_dir = self.root / "tasks"
        self.tasks_dir.mkdir(parents=True)

        self._write(
            "MAP_System/shared/current-state.md",
            "# Current State\n\nLateonly shared phrase added after both tasks.\n",
        )
        self._write(
            "MAP_System/scripts/alpha_validator.py",
            '"""Validate alpha records against the canonical ledger."""\n\n'
            "def validate_alpha_record():\n    return True\n",
        )
        self._write(
            "MAP_System/tests/test_alpha_validator.py",
            '"""Regression proof for alpha validation."""\n\n'
            "def test_invalid_alpha_is_rejected():\n    assert True\n",
        )
        self._write(
            "MAP_System/artifacts/planning/recovery-plan.md",
            "# Quiet Agent Recovery\n\nOperator recovery proceeds from suspicion to nudge and reclaim.\n",
        )
        self._task(
            "TASK-001",
            "Add alpha record validation",
            "Reject invalid alpha records while preserving the canonical ledger.",
            [
                "MAP_System/shared/current-state.md",
                "MAP_System/scripts/alpha_validator.py",
                "MAP_System/tests/test_alpha_validator.py",
            ],
        )
        self._task(
            "TASK-002",
            "Specify quiet agent recovery",
            "Define operator suspicion, nudge, and reclaim behavior for a quiet agent.",
            [
                "MAP_System/shared/current-state.md",
                "MAP_System/artifacts/planning/recovery-plan.md",
            ],
        )
        self.db = Path(self.temp.name) / "memory.db"

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
        (self.tasks_dir / f"{task_id}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def _build(self) -> dict:
        return memory.build_database(
            self.db,
            ["TASK-001", "TASK-002"],
            tasks_dir=self.tasks_dir,
            repo=self.repo,
        )

    def test_unique_source_document_and_explicit_shared_links(self) -> None:
        stats = self._build()
        self.assertEqual(6, stats["source_document_count"])
        self.assertEqual(7, stats["task_source_link_count"])
        with sqlite3.connect(self.db) as conn:
            row = conn.execute(
                """
                SELECT linked_task_count,temporal_mode,historical_attribution
                FROM source_documents WHERE path='MAP_System/shared/current-state.md'
                """
            ).fetchone()
            links = conn.execute(
                "SELECT task_id FROM task_source_links "
                "WHERE path='MAP_System/shared/current-state.md' ORDER BY task_id"
            ).fetchall()
        self.assertEqual((2, "current_shared", 0), row)
        self.assertEqual([("TASK-001",), ("TASK-002",)], links)

    def test_current_shared_content_is_not_cloned_into_task_fts(self) -> None:
        self._build()
        with sqlite3.connect(self.db) as conn:
            task_hits = conn.execute(
                "SELECT task_id FROM task_fts WHERE task_fts MATCH 'lateonly'"
            ).fetchall()
            source_hits = conn.execute(
                "SELECT path FROM source_fts WHERE source_fts MATCH 'lateonly'"
            ).fetchall()
        self.assertEqual([], task_hits)
        self.assertEqual([("MAP_System/shared/current-state.md",)], source_hits)

    def test_unresolved_source_keeps_visible_path_health(self) -> None:
        task = json.loads((self.tasks_dir / "TASK-002.json").read_text())
        task["output_paths"].append("MAP_System/missing/never-created.md")
        (self.tasks_dir / "TASK-002.json").write_text(json.dumps(task), encoding="utf-8")
        stats = self._build()
        self.assertEqual(1, stats["unresolved_link_instances"])
        with sqlite3.connect(self.db) as conn:
            row = conn.execute(
                "SELECT exists_now,temporal_mode FROM source_documents "
                "WHERE path='MAP_System/missing/never-created.md'"
            ).fetchone()
        self.assertEqual((0, "unresolved"), row)

    def test_rrf_is_deterministic_and_does_not_mix_raw_scores(self) -> None:
        rankings = {"alpha": ["A", "B"], "beta": ["B", "C"]}
        first = memory.rrf_fuse(rankings, weights={"alpha": 1.0, "beta": 0.5}, k=10)
        second = memory.rrf_fuse(rankings, weights={"alpha": 1.0, "beta": 0.5}, k=10)
        self.assertEqual(first, second)
        self.assertEqual("B", first[0]["id"])
        self.assertEqual({"channel", "rank", "weight", "contribution"}, set(first[0]["provenance"][0]))

    def test_compound_parts_are_bounded_and_preserve_question_clauses(self) -> None:
        parts = memory.query_parts(
            "What shows the operator view, and how does recovery progress, "
            "and who may reclaim it; where is proof?"
        )
        self.assertLessEqual(len(parts), memory.source_base.MAX_QUERY_PARTS)
        self.assertTrue(any(part.startswith("how does recovery") for part in parts))
        self.assertTrue(any(part.startswith("who may reclaim") for part in parts))

    def test_query_retrieves_task_and_complementary_implementation_test(self) -> None:
        self._build()
        with sqlite3.connect(self.db) as conn:
            result = memory.search(
                conn,
                "What check rejects an invalid alpha record, and which regression proves it?",
            )
        self.assertEqual("TASK-001", result["candidates"][0]["task_id"])
        paths = {item["path"] for item in result["candidates"][0]["source_choices"]}
        self.assertEqual(
            {
                "MAP_System/scripts/alpha_validator.py",
                "MAP_System/tests/test_alpha_validator.py",
            },
            paths,
        )
        self.assertEqual("candidate_set", result["strength"]["recommendation"])

    def test_no_match_abstains(self) -> None:
        self._build()
        with sqlite3.connect(self.db) as conn:
            result = memory.search(conn, "Which task implemented zephyr quasar encryption?")
        self.assertEqual("no_strong_match", result["strength"]["recommendation"])
        self.assertEqual(0.0, result["strength"]["query_coverage"])

    def test_path_trigram_channel_finds_identifier_substring(self) -> None:
        self._build()
        with sqlite3.connect(self.db) as conn:
            hits = memory._rank_fts(conn, "path_fts", '"validat"', 10)
        self.assertIn("MAP_System/scripts/alpha_validator.py", hits)

    def test_rebuild_produces_same_query_order(self) -> None:
        self._build()
        with sqlite3.connect(self.db) as conn:
            first = [
                item["task_id"]
                for item in memory.search(conn, "quiet operator nudge reclaim")["candidates"]
            ]
        second_db = Path(self.temp.name) / "memory-second.db"
        memory.build_database(
            second_db,
            ["TASK-001", "TASK-002"],
            tasks_dir=self.tasks_dir,
            repo=self.repo,
        )
        with sqlite3.connect(second_db) as conn:
            second = [
                item["task_id"]
                for item in memory.search(conn, "quiet operator nudge reclaim")["candidates"]
            ]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
