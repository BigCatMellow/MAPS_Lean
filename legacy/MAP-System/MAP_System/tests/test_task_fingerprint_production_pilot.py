#!/usr/bin/env python3
"""Focused deterministic tests for TASK-284's offline source-aware pilot."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.scripts import task_fingerprint_production_pilot as pilot


def fixture(tmp: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    repo = tmp / "repo"; repo.mkdir()
    tasks = repo / "MAP_System" / "tasks"; tasks.mkdir(parents=True)
    events = repo / "MAP_System" / "events"; events.mkdir(parents=True)
    reviews = repo / "MAP_System" / "artifacts" / "reviews"; reviews.mkdir(parents=True)
    workflow = repo / "MAP_System" / "workflow"; workflow.mkdir(parents=True)
    (repo / "MAP_System" / "shared").mkdir(parents=True)
    (repo / "MAP_System" / "scripts").mkdir(parents=True)
    (repo / "MAP_System" / "scripts" / "validator.py").write_text("def validate(): pass\n")
    (repo / "MAP_System" / "shared" / "decisions.md").write_text("TASK-X permits this check.\n")
    task = {"task_id":"TASK-X", "title":"Validate source mirrors", "description":"Test status mirror drift", "status":"RELEASED", "output_paths":["MAP_System/scripts/validator.py", "MAP_System/missing.py"]}
    (tasks / "TASK-X.json").write_text(json.dumps(task))
    (events / "events.jsonl").write_text(json.dumps({"task_id":"TASK-X", "type":"SUBMISSION"}) + "\n")
    (reviews / "task-x-review.md").write_text("review")
    graph = workflow / "task_graph.json"
    graph.write_text(json.dumps({"tasks": [{"task_id": "TASK-X", "status": "RELEASED"}]}))
    db = repo / "MAP_System" / "map.db"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT NOT NULL)")
        connection.execute("INSERT INTO tasks VALUES (?, ?)", ("TASK-X", "RELEASED"))
    return repo, tasks, events / "events.jsonl", repo / "MAP_System" / "shared" / "decisions.md", db, graph


def test_index_has_only_released_records_and_explicit_backlinks() -> None:
    with tempfile.TemporaryDirectory() as raw:
        repo, tasks, events, decisions, db, graph = fixture(Path(raw))
        index = pilot.build_index(tasks, repo, events, decisions, db, graph)
        assert [row["task_id"] for row in index["records"]] == ["TASK-X"]
        record = index["records"][0]
        assert any(row["kind"] == "submission" for row in record["sources"])
        assert any(row["kind"] == "review" for row in record["sources"])
        assert "MAP_System/missing.py" in record["missing_or_contradictory_sources"]
        assert record["release_state"]["statuses"] == {
            "task_json": "RELEASED",
            "sqlite": "RELEASED",
            "task_graph": "RELEASED",
        }


def test_contradictory_release_state_is_marked_and_excluded() -> None:
    with tempfile.TemporaryDirectory() as raw:
        repo, tasks, events, decisions, db, graph = fixture(Path(raw))
        graph.write_text(json.dumps({"tasks": [{"task_id": "TASK-X", "status": "CHANGES_REQUESTED"}]}))
        index = pilot.build_index(tasks, repo, events, decisions, db, graph)
        assert index["records"] == []
        assert len(index["excluded_records"]) == 1
        excluded = index["excluded_records"][0]
        assert excluded["task_id"] == "TASK-X"
        assert excluded["release_state"]["eligible"] is False
        assert excluded["release_state"]["contradictions"] == [{
            "kind": "release_status_mismatch",
            "source": "task_graph",
            "expected": "RELEASED",
            "actual": "CHANGES_REQUESTED",
        }]
        result = pilot.search(index, "validate source mirrors")
        assert result["abstained"] is True
        assert result["results"] == []

        graph.write_text(json.dumps({"tasks": [{"task_id": "TASK-X", "status": "RELEASED"}]}))
        with sqlite3.connect(db) as connection:
            connection.execute(
                "UPDATE tasks SET status = ? WHERE task_id = ?",
                ("CHANGES_REQUESTED", "TASK-X"),
            )
        index = pilot.build_index(tasks, repo, events, decisions, db, graph)
        assert index["records"] == []
        assert index["excluded_records"][0]["release_state"]["contradictions"] == [{
            "kind": "release_status_mismatch",
            "source": "sqlite",
            "expected": "RELEASED",
            "actual": "CHANGES_REQUESTED",
        }]

        with sqlite3.connect(db) as connection:
            connection.execute(
                "UPDATE tasks SET status = ? WHERE task_id = ?",
                ("RELEASED", "TASK-X"),
            )
        task_path = tasks / "TASK-X.json"
        task = json.loads(task_path.read_text())
        task["status"] = "CHANGES_REQUESTED"
        task_path.write_text(json.dumps(task))
        index = pilot.build_index(tasks, repo, events, decisions, db, graph)
        assert index["records"] == []
        assert index["excluded_records"][0]["release_state"]["contradictions"] == [{
            "kind": "release_status_mismatch",
            "source": "task_json",
            "expected": "RELEASED",
            "actual": "CHANGES_REQUESTED",
        }]
        result = pilot.search(index, "validate source mirrors")
        assert result["abstained"] is True
        assert result["results"] == []


def test_search_abstains_instead_of_returning_unlinked_guess() -> None:
    index = {"records": [{"task_id":"TASK-X", "title":"Validate source mirrors", "description":"Test status mirror drift", "sources": [], "missing_or_contradictory_sources": []}]}
    result = pilot.search(index, "automatic secret redaction scanner", minimum_score=3)
    assert result["abstained"] is True
    assert result["results"] == []


def test_evaluation_keeps_task_and_source_metrics_separate() -> None:
    index = {"records": [{"task_id":"TASK-X", "title":"Validate source mirrors", "description":"Test status mirror drift", "sources":[{"kind":"primary","path":"MAP_System/scripts/validator.py","exists":True,"sha256":"x","state":"available"}], "missing_or_contradictory_sources": []}]}
    holdout = ({"id":"one", "question":"validate source mirrors", "expected_task_ids":["TASK-X"], "expected_source_paths":["MAP_System/scripts/validator.py"]},)
    metrics = pilot.evaluate(index, holdout)
    assert metrics["task_recall"] == 1.0
    assert metrics["primary_source_recall"] == 1.0
    assert metrics["context_byte_reduction"] >= 0.0


def test_projection_never_enables_production_routing() -> None:
    with tempfile.TemporaryDirectory() as raw:
        repo, tasks, events, decisions, db, graph = fixture(Path(raw))
        index = pilot.build_index(tasks, repo, events, decisions, db, graph)
        assert index["mode"] == "offline_disposable_projection"
        assert index["production_routing_enabled"] is False


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test(); print(f"PASS {test.__name__}")
    print(f"{len(tests)} TASK-284 tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
