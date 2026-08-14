#!/usr/bin/env python3
"""TASK-284 source-aware fingerprint pilot.

This is an offline, rebuildable evaluation projection.  It reads released task
records and canonical evidence references, but it never changes routing,
canonical task state, or source evidence.  A result is always accompanied by
the raw evidence backlinks needed to verify it.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
TASKS = ROOT / "tasks"
EVENTS = ROOT / "events" / "events.jsonl"
DECISIONS = ROOT / "shared" / "decisions.md"
DEFAULT_DB = ROOT / "map.db"
DEFAULT_TASK_GRAPH = ROOT / "workflow" / "task_graph.json"
DEFAULT_REPORT = ROOT / "artifacts" / "experiments" / "task284-source-aware-fingerprint-pilot.md"

# These rows are a fixed subset of the independently authored TASK-258 source
# holdout.  They are deliberately data, not tuned from this implementation.
FROZEN_HOLDOUT = (
    {
        "id": "S1",
        "question": "A completed research packet has template placeholders or lacks a mandatory section. What catches it and where are failures tested?",
        "expected_task_ids": ["TASK-104"],
        "expected_source_paths": [
            "MAP_System/scripts/validate_research_artifacts.py",
            "MAP_System/tests/test_validate_research_artifacts.py",
        ],
    },
    {
        "id": "S2",
        "question": "Why does a ready follow-up become dispatchable after its prerequisite is RELEASED, and which regression protects that rule?",
        "expected_task_ids": ["TASK-116"],
        "expected_source_paths": [
            "MAP_System/graph/runner.py",
            "MAP_System/tests/test_runner_task_classification.py",
        ],
    },
    {
        "id": "S5",
        "question": "What check exposes drift when SQLite disagrees with task JSON or workflow graph status and output paths?",
        "expected_task_ids": ["TASK-143"],
        "expected_source_paths": [
            "MAP_System/scripts/validate_task_mirrors.py",
            "MAP_System/tests/test_validate_task_mirrors.py",
        ],
    },
    {
        "id": "S9",
        "question": "Which historical task implemented automatic secret scanning and redaction for MAP event records before they are committed?",
        "expected_task_ids": [],
        "expected_source_paths": [],
    },
)

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
STOP_WORDS = {"a", "an", "and", "are", "as", "after", "before", "does", "for", "from", "how", "in", "is", "it", "its", "map", "of", "or", "that", "the", "this", "to", "what", "when", "where", "which", "with"}


def words(value: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(value.lower()) if token not in STOP_WORDS and len(token) > 2}


def digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def resolve(raw: str, repo: Path) -> Path:
    return (repo / raw).resolve() if not Path(raw).is_absolute() else Path(raw)


def event_refs(events: Path, task_id: str, repo: Path) -> list[dict[str, str]]:
    if not events.exists():
        return []
    found = []
    for line in events.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("task_id") == task_id and event.get("type") == "SUBMISSION":
            found.append({"kind": "submission", "path": display(events, repo), "event_type": "SUBMISSION", "exists": True, "sha256": digest(events), "state": "available", "summary": event.get("summary", "")})
    return found


def review_refs(reviews_dir: Path, task_id: str, repo: Path) -> list[dict[str, str]]:
    rows = []
    for path in sorted(reviews_dir.glob(f"*{task_id.lower()}*")):
        if path.is_file():
            rows.append({"kind": "review", "path": display(path, repo), "exists": True, "sha256": digest(path), "state": "available", "summary": " ".join(path.read_text(encoding="utf-8", errors="replace")[:4000].split()[:60])})
    return rows


def source_row(raw: str, kind: str, repo: Path) -> dict[str, Any]:
    path = resolve(raw, repo)
    summary = ""
    if path.is_file():
        summary = " ".join(path.read_text(encoding="utf-8", errors="replace")[:8000].split()[:80])
    return {
        "kind": kind,
        "path": raw,
        "exists": path.is_file(),
        "sha256": digest(path),
        "state": "available" if path.is_file() else "missing",
        "summary": summary,
    }


def canonical_statuses(db_path: Path) -> dict[str, str]:
    """Read task lifecycle status from SQLite without opening a write-capable handle."""
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        return {
            str(task_id): str(status)
            for task_id, status in connection.execute(
                "SELECT task_id, status FROM tasks ORDER BY task_id"
            )
        }


def graph_statuses(task_graph: Path) -> dict[str, str]:
    graph = json.loads(task_graph.read_text(encoding="utf-8"))
    return {
        str(row["task_id"]): str(row.get("status", ""))
        for row in graph.get("tasks", [])
        if isinstance(row, dict) and row.get("task_id")
    }


def release_state(
    task_id: str,
    task_status: str | None,
    db_statuses: dict[str, str],
    graph_states: dict[str, str],
) -> dict[str, Any]:
    statuses = {
        "task_json": task_status,
        "sqlite": db_statuses.get(task_id),
        "task_graph": graph_states.get(task_id),
    }
    contradictions = []
    for source, status in statuses.items():
        if status is None:
            contradictions.append(
                {
                    "kind": "missing_release_state",
                    "source": source,
                    "expected": "RELEASED",
                    "actual": None,
                }
            )
        elif status != "RELEASED":
            contradictions.append(
                {
                    "kind": "release_status_mismatch",
                    "source": source,
                    "expected": "RELEASED",
                    "actual": status,
                }
            )
    return {
        "eligible": not contradictions,
        "statuses": statuses,
        "contradictions": contradictions,
    }


def build_index(
    tasks_dir: Path = TASKS,
    repo: Path = REPO,
    events: Path = EVENTS,
    decisions: Path = DECISIONS,
    db_path: Path = DEFAULT_DB,
    task_graph: Path = DEFAULT_TASK_GRAPH,
) -> dict[str, Any]:
    """Build only from records whose three declared lifecycle sources agree."""
    records = []
    excluded_records = []
    db_states = canonical_statuses(db_path)
    graph_states = graph_statuses(task_graph)
    task_files = {}
    for task_path in sorted(tasks_dir.glob("TASK-*.json")):
        task = json.loads(task_path.read_text(encoding="utf-8"))
        task_files[str(task["task_id"])] = (task_path, task)

    candidate_ids = set(task_files).union(db_states, graph_states)
    for task_id in sorted(candidate_ids):
        task_entry = task_files.get(task_id)
        task_path = task_entry[0] if task_entry else tasks_dir / f"{task_id}.json"
        task = task_entry[1] if task_entry else {}
        observed_statuses = {
            task.get("status"),
            db_states.get(task_id),
            graph_states.get(task_id),
        }
        # A task that no authority source calls RELEASED is simply outside this
        # released-evidence index. If any source calls it RELEASED, compare all
        # three before deciding eligibility so disagreements cannot disappear.
        if "RELEASED" not in observed_statuses:
            continue
        state = release_state(
            task_id,
            task.get("status"),
            db_states,
            graph_states,
        )
        if not state["eligible"]:
            excluded_records.append(
                {
                    "task_id": task_id,
                    "reason": "contradictory_or_missing_release_state",
                    "release_state": state,
                }
            )
            continue
        sources = [source_row(display(task_path, repo), "released_task", repo)]
        sources += [source_row(raw, "primary", repo) for raw in task.get("output_paths", [])]
        sources += event_refs(events, task_id, repo)
        sources += review_refs(repo / "MAP_System" / "artifacts" / "reviews", task_id, repo)
        if decisions.exists() and task_id in decisions.read_text(encoding="utf-8", errors="replace"):
            sources.append(source_row(display(decisions, repo), "decision", repo))
        missing = [row["path"] for row in sources if row.get("state") == "missing"]
        records.append({
            "task_id": task_id,
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "status": "RELEASED",
            "sources": sources,
            "release_state": state,
            "missing_sources": missing,
            "contradictory_sources": [],
            "missing_or_contradictory_sources": missing,
            "projection": "derived; raw evidence remains authoritative",
        })
    return {
        "schema_version": 2,
        "mode": "offline_disposable_projection",
        "production_routing_enabled": False,
        "records": records,
        "excluded_records": excluded_records,
    }


def score(question: str, record: dict[str, Any]) -> tuple[int, set[str]]:
    query = words(question)
    haystack = " ".join([record["task_id"], record["title"], record["description"], *[row["path"] + " " + row.get("summary", "") for row in record["sources"]]])
    matched = query.intersection(words(haystack))
    # The title/description is a candidate locator only. Evidence is returned
    # separately, never blended into an untraceable semantic answer.
    return len(matched), matched


def search(index: dict[str, Any], question: str, limit: int = 3, minimum_score: int = 3) -> dict[str, Any]:
    ranked = []
    for record in index["records"]:
        value, matched = score(question, record)
        if value:
            ranked.append((value, record["task_id"], record, sorted(matched)))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    if not ranked or ranked[0][0] < minimum_score:
        return {"abstained": True, "reason": "no source-linked candidate exceeded the frozen minimum score", "results": []}
    results = []
    for value, _task_id, record, matched in ranked[:limit]:
        primary = [row for row in record["sources"] if row["kind"] == "primary"]
        primary.sort(key=lambda row: (-len(words(question).intersection(words(row["path"] + " " + row.get("summary", "")))), row["path"]))
        primary = primary[:3]
        results.append({
            "task_id": record["task_id"], "score": value, "matched_tokens": matched,
            "primary_sources": primary,
            "all_backlinks": record["sources"],
            "missing_or_contradictory_sources": record["missing_or_contradictory_sources"],
            "raw_evidence_required": True,
        })
    return {"abstained": False, "reason": "source-linked candidates available", "results": results}


def estimate_bytes(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def evaluate(index: dict[str, Any], holdout: tuple[dict[str, Any], ...] = FROZEN_HOLDOUT) -> dict[str, Any]:
    task_hits = source_hits = expected_tasks = expected_sources = 0
    negative_total = negative_correct = 0
    rows = []
    for query in holdout:
        result = search(index, query["question"])
        actual_tasks = {item["task_id"] for item in result["results"]}
        actual_sources = {source["path"] for item in result["results"] for source in item["primary_sources"]}
        wanted_tasks = set(query["expected_task_ids"])
        wanted_sources = set(query["expected_source_paths"])
        task_hits += len(wanted_tasks.intersection(actual_tasks)); expected_tasks += len(wanted_tasks)
        source_hits += len(wanted_sources.intersection(actual_sources)); expected_sources += len(wanted_sources)
        if not wanted_tasks:
            negative_total += 1
            negative_correct += int(result["abstained"])
        rows.append({"id": query["id"], "abstained": result["abstained"], "expected_tasks": sorted(wanted_tasks), "returned_tasks": sorted(actual_tasks), "expected_sources": sorted(wanted_sources), "returned_primary_sources": sorted(actual_sources)})
    # Compare the compact projection with the actual source bytes an agent
    # would otherwise need to open. Count each raw path once; backlinks may be
    # shared by several released tasks but source content should not be charged
    # repeatedly.
    raw_paths = {source["path"] for record in index["records"] for source in record["sources"] if source.get("exists")}
    raw_bytes = sum(resolve(path, REPO).stat().st_size for path in raw_paths if resolve(path, REPO).is_file())
    compact_bytes = sum(estimate_bytes({"task_id": row["task_id"], "title": row["title"], "sources": row["sources"]}) for row in index["records"])
    return {
        "holdout_id": "TASK-258-source-holdout-subset-frozen-2026-07-19",
        "frozen_holdout_sha256": hashlib.sha256(json.dumps(holdout, sort_keys=True).encode()).hexdigest(),
        "task_recall": task_hits / expected_tasks if expected_tasks else 1.0,
        "primary_source_recall": source_hits / expected_sources if expected_sources else 1.0,
        "negative_abstention_accuracy": negative_correct / negative_total if negative_total else 1.0,
        "context_bytes_raw": raw_bytes,
        "context_bytes_fingerprint": compact_bytes,
        "context_byte_reduction": (1 - compact_bytes / raw_bytes) if raw_bytes else 0.0,
        "rows": rows,
    }


def render(index: dict[str, Any], metrics: dict[str, Any]) -> str:
    return f"""# TASK-284 Source-Aware Fingerprint Pilot

- task_id: TASK-284
- status: completed_offline_pilot
- generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}
- holdout: {metrics['holdout_id']}
- frozen_holdout_sha256: `{metrics['frozen_holdout_sha256']}`

## Boundary

This is a rebuildable retrieval projection, not canonical MAP truth. Every
returned task has raw source backlinks and `raw_evidence_required: true`.
Missing source state is preserved rather than inferred away. Release eligibility
is checked against task JSON, read-only canonical SQLite, and the task-graph
mirror. When any source identifies a release candidate, missing or
non-`RELEASED` status in any other source is recorded as a structured
contradiction and excluded from searchable candidates. The pilot does not
modify startup, runner routing, Command Center behavior, or task authority.

## Predeclared thresholds

- Promotion is prohibited in this task regardless of score.
- A future proposal requires task recall >= 0.90, primary-source recall >= 0.80,
  negative abstention accuracy == 1.00, and a separate independent review.
- Failure of any threshold, a missing/contradictory primary source, or inability
  to preserve backlinks means retain the projection as an experiment only.

## Frozen Evaluation

| Metric | Result |
|---|---:|
| released task records indexed | {len(index['records'])} |
| contradictory release records excluded | {len(index['excluded_records'])} |
| task recall | {metrics['task_recall']:.2%} |
| primary-source recall | {metrics['primary_source_recall']:.2%} |
| negative abstention accuracy | {metrics['negative_abstention_accuracy']:.2%} |
| raw context bytes | {metrics['context_bytes_raw']} |
| fingerprint context bytes | {metrics['context_bytes_fingerprint']} |
| context-byte reduction | {metrics['context_byte_reduction']:.2%} |

Only the holdout queries and expectations are frozen. The evidence corpus and
both byte counts are point-in-time measurements from this report generation;
they may change as canonical source files evolve while the holdout hash remains
stable.

## Results by Frozen Query

```json
{json.dumps(metrics['rows'], indent=2, sort_keys=True)}
```

## TASK-256 Comparison

TASK-256 reported 100% task recall@6 but 68.75% primary-source recall on its
curated 16-source experiment. This stricter source-aware pilot reports task
and primary-source recall separately, includes a genuine negative query that
exposed a false positive (zero abstention accuracy), and returns primary-source
backlinks rather than treating a task hit as proof. Its scores are not
comparable as a production claim because the frozen holdout and corpus differ.

## Decision

Do not promote or enable default production routing. Treat this report and the
script as an offline measurement harness until repeated independent holdouts
meet the thresholds and a separate task authorizes integration.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    index = build_index()
    metrics = evaluate(index)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render(index, metrics), encoding="utf-8")
    print(json.dumps(metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
