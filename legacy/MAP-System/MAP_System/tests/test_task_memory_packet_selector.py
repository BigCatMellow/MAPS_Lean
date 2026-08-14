from __future__ import annotations

import sqlite3
import json
from pathlib import Path
import tempfile
import unittest

from MAP_System.scripts import task_memory_fts as memory
from MAP_System.scripts import task_memory_packet_selector as selector


def candidate(
    path: str,
    role: str,
    *,
    terms: tuple[str, ...] = (),
    clauses: tuple[int, ...] = (),
    tasks: tuple[str, ...] = ("TASK-001",),
    base_score: float = 10.0,
    role_fit: float = 1.0,
    exists: bool = True,
    temporal_mode: str = "current_unique",
    rank: int = 1,
) -> dict:
    return {
        "path": path,
        "role": role,
        "matched_terms": list(terms),
        "clause_matches": list(clauses),
        "linked_selected_tasks": list(tasks),
        "base_score": base_score,
        "role_fit": role_fit,
        "exists_now": int(exists),
        "temporal_mode": temporal_mode,
        "rrf_score": 1.0 / (60 + rank),
        "global_source_rank": rank,
    }


class AllocationTests(unittest.TestCase):
    def test_three_role_single_task_uses_three_source_budget(self) -> None:
        candidates = [
            candidate("impl.py", "implementation", terms=("quota",), clauses=(0,), rank=1),
            candidate("test_impl.py", "test", terms=("stale",), clauses=(1,), rank=2),
            candidate("outcome.md", "outcome", terms=("wake",), clauses=(2,), rank=3),
            candidate("scope.json", "task_scope", base_score=1, role_fit=0, rank=4),
        ]
        selected = selector.allocate_evidence(candidates)
        self.assertEqual(["impl.py", "test_impl.py", "outcome.md"], [item["path"] for item in selected])

    def test_compound_query_rewards_uncovered_task_and_clause(self) -> None:
        candidates = [
            candidate("state.js", "implementation", terms=("state",), clauses=(0,), tasks=("TASK-001",), base_score=14, rank=1),
            candidate("state-review.md", "review", terms=("state",), clauses=(0,), tasks=("TASK-001",), base_score=13, rank=2),
            candidate("combat.js", "implementation", terms=("combat",), clauses=(1,), tasks=("TASK-002",), base_score=10, rank=3),
        ]
        selected = selector.allocate_evidence(candidates, limit=2)
        self.assertEqual(["state.js", "combat.js"], [item["path"] for item in selected])

    def test_complementary_same_role_is_not_forced_out(self) -> None:
        candidates = [
            candidate("undo-browser.md", "test", terms=("replacement",), clauses=(0,), tasks=("TASK-001",), base_score=14, rank=1),
            candidate("rules.cases.mjs", "test", terms=("snapshot",), clauses=(1,), tasks=("TASK-002",), base_score=12, rank=2),
            candidate("generic-guide.md", "guide", terms=("undo",), clauses=(0,), base_score=8, rank=3),
        ]
        selected = selector.allocate_evidence(candidates, limit=2)
        self.assertEqual(["test", "test"], [item["role"] for item in selected])

    def test_unresolved_source_is_excluded_when_resolved_source_exists(self) -> None:
        candidates = [
            candidate("missing.py", "implementation", base_score=100, exists=False),
            candidate("present.py", "implementation", base_score=1, rank=2),
        ]
        self.assertEqual("present.py", selector.allocate_evidence(candidates, limit=1)[0]["path"])

    def test_deterministic_path_tie_break(self) -> None:
        candidates = [
            candidate("a.py", "implementation"),
            candidate("b.py", "implementation"),
        ]
        first = selector.allocate_evidence(candidates, limit=2)
        second = selector.allocate_evidence(reversed(candidates), limit=2)
        self.assertEqual([item["path"] for item in first], [item["path"] for item in second])


class DatabaseScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.repo = root / "repo"
        self.tasks = self.repo / "MAP_System" / "tasks"
        self.tasks.mkdir(parents=True)
        (self.repo / "src").mkdir()
        (self.repo / "src" / "unique.py").write_text("def quota_wake(): pass\n", encoding="utf-8")
        (self.repo / "src" / "shared.py").write_text("def quota_wake(): pass\n", encoding="utf-8")
        for task_id, outputs in {
            "TASK-001": ["src/unique.py", "src/shared.py", "src/missing.py"],
            "TASK-002": ["src/shared.py"],
        }.items():
            (self.tasks / f"{task_id}.json").write_text(
                json.dumps({
                    "task_id": task_id,
                    "title": "quota wake helper",
                    "description": "detect quota and wake agent",
                    "acceptance_criteria": [],
                    "output_paths": outputs,
                    "status": "COMPLETED",
                }) + "\n",
                encoding="utf-8",
            )
        self.db = root / "index.db"
        memory.build_database(
            self.db,
            ["TASK-001", "TASK-002"],
            tasks_dir=self.tasks,
            repo=self.repo,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_current_shared_and_unresolved_are_penalized(self) -> None:
        with sqlite3.connect(self.db) as conn:
            candidates = selector.evidence_candidates(conn, "quota wake", ["TASK-001"])
        scores = {item["path"]: item["base_score"] for item in candidates}
        self.assertGreater(scores["src/unique.py"], scores["src/shared.py"])
        self.assertGreater(scores["src/shared.py"], scores["src/missing.py"])

    def test_fixed_selector_comparison_has_global_limit(self) -> None:
        with sqlite3.connect(self.db) as conn:
            fixed = memory.search(conn, "quota wake", task_limit=2, source_limit=2)
            selected = selector.select_evidence(conn, "quota wake", ["TASK-001", "TASK-002"])
        fixed_count = sum(len(item["source_choices"]) for item in fixed["candidates"])
        self.assertGreaterEqual(fixed_count, len(selected["sources"]))
        self.assertLessEqual(len(selected["sources"]), 3)


if __name__ == "__main__":
    unittest.main()
