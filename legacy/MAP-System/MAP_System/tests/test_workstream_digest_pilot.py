#!/usr/bin/env python3
"""Focused deterministic tests for TASK-285's workstream digest pilot."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.scripts import workstream_digest_pilot as pilot


def fixture(tmp: Path) -> tuple[Path, Path, Path, Path, Path]:
    repo = tmp / "repo"
    tasks_dir = repo / "MAP_System" / "tasks"
    reviews = repo / "MAP_System" / "artifacts" / "reviews"
    workflow = repo / "MAP_System" / "workflow"
    events_dir = repo / "MAP_System" / "events"
    for path in (tasks_dir, reviews, workflow, events_dir):
        path.mkdir(parents=True, exist_ok=True)

    by_task_anchors: dict[str, list[str]] = {}
    for spec in pilot.CLAIM_SPECS:
        if "TASK-" in spec["path"]:
            task_id = Path(spec["path"]).stem
            by_task_anchors.setdefault(task_id, []).append(spec["anchor"])

    graph_rows = []
    events = []
    for task_id in pilot.RELATED_TASK_IDS:
        primary = f"MAP_System/source/{task_id.lower()}.txt"
        source = repo / primary
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(("canonical evidence " + task_id + "\n") * 80)
        task = {
            "task_id": task_id,
            "title": f"Lifecycle capability {task_id}",
            "description": " ".join(by_task_anchors.get(task_id, [])),
            "status": "RELEASED",
            "output_paths": [primary],
        }
        (tasks_dir / f"{task_id}.json").write_text(json.dumps(task))
        (reviews / f"{task_id.lower()}-review.md").write_text("APPROVED")
        graph_rows.append({"task_id": task_id, "status": "RELEASED"})
        events.append(
            {
                "type": "SUBMISSION",
                "task_id": task_id,
                "summary": ("verified submission evidence " + task_id + " ") * 30,
            }
        )

    risk = {
        "task_id": pilot.OPEN_RISK_TASK_ID,
        "title": "Submission authorship",
        "description": "open risk",
        "status": "IN_PROGRESS",
        "output_paths": [],
    }
    (tasks_dir / f"{pilot.OPEN_RISK_TASK_ID}.json").write_text(json.dumps(risk))
    graph_rows.append({"task_id": pilot.OPEN_RISK_TASK_ID, "status": "IN_PROGRESS"})
    graph = workflow / "task_graph.json"
    graph.write_text(json.dumps({"tasks": graph_rows}))
    events_path = events_dir / "events.jsonl"
    events_path.write_text("\n".join(json.dumps(row) for row in events) + "\n")

    decisions = repo / "MAP_System" / "shared" / "decisions.md"
    decisions.parent.mkdir(parents=True)
    decisions.write_text(
        "## DEC-003: One Owner Per Active Task\n"
        "## DEC-009: SQLite Is The Task Claiming Coordinator\n"
    )
    for raw in pilot.KEY_FILE_PATHS:
        path = repo / raw
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(("key implementation evidence\n") * 80)

    db = repo / "MAP_System" / "map.db"
    with sqlite3.connect(db) as connection:
        connection.execute(
            "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO tasks VALUES (?, ?)",
            [
                *((task_id, "RELEASED") for task_id in pilot.RELATED_TASK_IDS),
                (pilot.OPEN_RISK_TASK_ID, "IN_PROGRESS"),
            ],
        )
    return repo, tasks_dir, db, graph, events_path


def build(paths: tuple[Path, Path, Path, Path, Path]) -> dict:
    repo, tasks, db, graph, events = paths
    return pilot.build_digest(
        repo=repo,
        tasks_dir=tasks,
        db_path=db,
        graph_path=graph,
        events_path=events,
    )


def test_threshold_and_required_evidence_are_preserved() -> None:
    with tempfile.TemporaryDirectory() as raw:
        row = build(fixture(Path(raw)))
        assert row["eligibility"] == {
            "minimum_related_released_tasks": 5,
            "declared_related_tasks": list(pilot.RELATED_TASK_IDS),
            "verified_released_tasks": 5,
            "eligible": True,
        }
        assert len(row["decisions"]) == 2
        assert len(row["repeated_failures"]) == 5
        assert row["open_risks"][0]["id"] == "risk-submission-authorship"
        assert all(task["backlinks"] for task in row["tasks"])


def test_contradictory_lifecycle_fails_eligibility_and_is_visible() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        graph = paths[3]
        data = json.loads(graph.read_text())
        data["tasks"][0]["status"] = "APPROVED"
        graph.write_text(json.dumps(data))
        row = build(paths)
        assert row["eligibility"]["eligible"] is False
        issue = next(
            issue
            for issue in row["evidence_issues"]
            if issue["kind"] == "lifecycle_not_released"
        )
        assert issue["detail"]["contradictory"] is True


def test_missing_and_stale_evidence_are_not_synthesized_away() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        repo = paths[0]
        missing = repo / pilot.KEY_FILE_PATHS[0]
        missing.unlink()
        row = build(paths)
        assert any(
            issue["kind"] == "missing"
            and issue["path"] == pilot.KEY_FILE_PATHS[0]
            for issue in row["evidence_issues"]
        )
        assert pilot.detect_probe(
            {"expected_sha256": "old", "actual_sha256": "new"}
        ) == "stale"


def test_directory_evidence_uses_deterministic_manifest_classification() -> None:
    with tempfile.TemporaryDirectory() as raw:
        repo = Path(raw) / "repo"
        evidence_dir = repo / "MAP_System" / "tasks"
        nested = evidence_dir / "nested"
        nested.mkdir(parents=True)
        (evidence_dir / "TASK-001.json").write_text('{"status":"RELEASED"}')
        (nested / "TASK-002.json").write_text('{"status":"RELEASED"}')

        first = pilot.source_ref(
            "MAP_System/tasks", "primary", repo
        )
        second = pilot.source_ref(
            "MAP_System/tasks", "primary", repo
        )
        assert first["state"] == "available"
        assert first["source_type"] == "directory_manifest"
        assert first["sha256"] == second["sha256"]

        (nested / "TASK-002.json").write_text('{"status":"APPROVED"}')
        changed = pilot.source_ref(
            "MAP_System/tasks",
            "primary",
            repo,
            expected_sha256=first["sha256"],
        )
        assert changed["state"] == "stale"
        assert changed["source_type"] == "directory_manifest"


def test_frozen_evaluation_and_noncanonical_rules() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        row = build(paths)
        metrics = pilot.evaluate(row, paths[0])
        assert metrics["required_fact_retention"] == 1.0
        assert metrics["source_traceability"] == 1.0
        assert metrics["stale_detection_accuracy"] == 1.0
        assert metrics["context_byte_reduction"] > 0.0
        assert row["canonical"] is False
        assert row["production_routing_enabled"] is False
        assert row["raw_evidence_required"] is True


def test_refresh_detects_stale_claim_source_and_withholds_it() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        first = build(paths)
        assert any(row["id"] == "decision-one-owner" for row in first["decisions"])
        # A plain rebuild with no prior manifest cannot see the mutation --
        # it only proves the current content is internally consistent.
        prior_manifest = pilot.extract_manifest(first)

        repo, tasks_dir, db, graph, events = paths
        decisions_path = repo / "MAP_System" / "shared" / "decisions.md"
        decisions_path.write_text(decisions_path.read_text() + "\nmutated after first build\n")

        second = pilot.build_digest(
            repo=repo, tasks_dir=tasks_dir, db_path=db, graph_path=graph,
            events_path=events, prior_manifest=prior_manifest,
        )
        # The mutated claim must be withheld, not reported as still available.
        assert not any(row["id"] == "decision-one-owner" for row in second["decisions"])
        withheld = next(
            row for row in second["withheld_claims"] if row["id"] == "decision-one-owner"
        )
        assert withheld["backlinks"][0]["state"] == "stale"
        assert any(
            issue["kind"] == "stale" for issue in second["evidence_issues"]
        )

        # A rebuild against the same (still-mutated) content and the same
        # prior manifest is stable -- the mutation is detected, not the
        # rebuild itself.
        third = pilot.build_digest(
            repo=repo, tasks_dir=tasks_dir, db_path=db, graph_path=graph,
            events_path=events, prior_manifest=prior_manifest,
        )
        assert not any(row["id"] == "decision-one-owner" for row in third["decisions"])

        # Without a prior manifest, the same mutated content is reported
        # available -- this is the exact gap the review flagged: a plain
        # rebuild cannot detect staleness on its own.
        no_baseline = pilot.build_digest(
            repo=repo, tasks_dir=tasks_dir, db_path=db, graph_path=graph, events_path=events,
        )
        assert any(row["id"] == "decision-one-owner" for row in no_baseline["decisions"])


def test_token_metrics_are_computed_and_reduce_context() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        row = build(paths)
        metrics = pilot.evaluate(row, paths[0])
        assert metrics["context_tokens_raw"] > 0
        assert metrics["context_tokens_digest"] > 0
        assert metrics["context_tokens_digest"] < metrics["context_tokens_raw"]
        assert 0.0 < metrics["context_token_reduction"] < 1.0
        # Token and byte reductions are independent measurements, not aliases.
        assert metrics["context_tokens_raw"] != metrics["context_bytes_raw"]


def test_estimate_tokens_is_deterministic_and_word_symbol_bounded() -> None:
    assert pilot.estimate_tokens("hello world") == 2
    assert pilot.estimate_tokens("a,b") == 3  # "a", ",", "b"
    assert pilot.estimate_tokens("") == 0
    assert pilot.estimate_tokens("hello world") == pilot.estimate_tokens("hello world")


def test_extract_manifest_only_keeps_hashed_backlinks() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        row = build(paths)
        manifest = pilot.extract_manifest(row)
        assert manifest
        assert all(isinstance(value, str) and len(value) == 64 for value in manifest.values())
        # Every manifest entry must correspond to a real backlink with a hash.
        all_backlinks = [
            ref
            for task in row["tasks"]
            for ref in task["backlinks"]
        ] + [
            ref
            for section in ("decisions", "repeated_failures", "open_risks", "withheld_claims")
            for claim in row[section]
            for ref in claim["backlinks"]
        ] + list(row["key_files"]["backlinks"])
        hashed_paths = {ref["path"] for ref in all_backlinks if ref.get("sha256")}
        assert set(manifest) <= hashed_paths


def test_render_roundtrip_supports_prior_report_refresh() -> None:
    with tempfile.TemporaryDirectory() as raw:
        paths = fixture(Path(raw))
        first_row = build(paths)
        first_metrics = pilot.evaluate(first_row, paths[0])
        rendered = pilot.render(first_row, first_metrics)
        report_path = Path(raw) / "report.md"
        report_path.write_text(rendered, encoding="utf-8")

        loaded = pilot.load_prior_digest(report_path)
        assert loaded == first_row
        manifest = pilot.extract_manifest(loaded)
        assert manifest

        missing_report = Path(raw) / "does-not-exist.md"
        assert pilot.load_prior_digest(missing_report) is None


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} TASK-285 tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
