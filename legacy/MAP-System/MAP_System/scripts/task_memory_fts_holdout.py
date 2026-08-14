#!/usr/bin/env python3
"""Frozen-packet harness for TASK-260's fresh FTS5/RRF holdout.

The retrieval engine lives in task_memory_fts.py and is frozen independently.
This harness validates an independently authored truth set, builds a temporary
database, records full and task-only rankings, and renders one compact packet
per query. It never changes canonical MAP state.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sqlite3
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402
from MAP_System.scripts import task_memory_fts as memory  # noqa: E402


DEFAULT_SPEC = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-queries-2026-07-19.json"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-2026-07-19.json"
)
DEFAULT_PACKET = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-helper-packet-2026-07-19.md"
)
DEFAULT_PACKET_DIR = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-packets-2026-07-19"
)


def task_only_search(conn: sqlite3.Connection, query: str, limit: int = 6) -> list[str]:
    _parts, rankings, _source_rankings = memory.retrieval_channels(conn, query)
    weights = {
        channel: (1.15 if channel != "task:0" else 1.0)
        for channel in rankings
    }
    return [item["id"] for item in memory.rrf_fuse(rankings, weights=weights)[:limit]]


def validate_spec(
    spec: dict[str, Any],
    *,
    tasks_dir: Path = ROOT / "tasks",
    repo: Path = REPO,
) -> list[str]:
    findings = []
    corpus = set(spec.get("corpus_task_ids", []))
    queries = spec.get("queries", [])
    positives = [query for query in queries if query.get("expected_task_ids")]
    negatives = [query for query in queries if not query.get("expected_task_ids")]
    compounds = [query for query in positives if len(query.get("expected_task_ids", [])) > 1]
    work_areas = {query.get("work_area") for query in positives if query.get("work_area")}

    if len(positives) < 8:
        findings.append(f"need at least 8 positive queries; found {len(positives)}")
    if len(negatives) < 3:
        findings.append(f"need at least 3 no-match queries; found {len(negatives)}")
    if len(compounds) < 2:
        findings.append(f"need at least 2 compound task sets; found {len(compounds)}")
    if len(work_areas) < 5:
        findings.append(f"need at least 5 positive work areas; found {len(work_areas)}")

    seen_ids = set()
    for query in queries:
        query_id = str(query.get("id", ""))
        if not query_id or query_id in seen_ids:
            findings.append(f"missing or duplicate query id: {query_id!r}")
        seen_ids.add(query_id)
        expected_tasks = query.get("expected_task_ids", [])
        expected_sources = query.get("expected_source_paths", [])
        expected_roles = query.get("expected_source_roles", [])
        if len(expected_sources) != len(expected_roles):
            findings.append(f"{query_id}: source paths/roles length mismatch")
        if not expected_tasks:
            if expected_sources:
                findings.append(f"{query_id}: no-match query has expected sources")
            if not query.get("no_match_reason"):
                findings.append(f"{query_id}: no-match query lacks no_match_reason")
            continue
        if len(expected_tasks) > 2:
            findings.append(f"{query_id}: at most 2 expected tasks allowed")
        if not (1 <= len(expected_sources) <= 3):
            findings.append(f"{query_id}: positive query needs 1-3 expected sources")
        registered = set()
        for task_id in expected_tasks:
            if task_id not in corpus:
                findings.append(f"{query_id}: expected task outside corpus: {task_id}")
                continue
            task_path = tasks_dir / f"{task_id}.json"
            if not task_path.is_file():
                findings.append(f"{query_id}: missing task record: {task_id}")
                continue
            task = base.load_json(task_path)
            registered.add(f"MAP_System/tasks/{task_id}.json")
            registered.update(memory.normalize_path(path, repo) for path in task.get("output_paths", []))
        for path in expected_sources:
            normalized = memory.normalize_path(path, repo)
            if normalized not in registered:
                findings.append(f"{query_id}: source is not registered by expected tasks: {path}")
            if not memory.resolve_path(normalized, repo).exists():
                findings.append(f"{query_id}: expected source does not resolve: {path}")
    return findings


def algorithm_metrics(
    conn: sqlite3.Connection,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    task_hits = task_total = source_hits = source_total = 0
    task_only_hits = 0
    compound_complete = compound_total = 0
    abstention_hits = 0
    results = {}
    per_query = []
    for query in spec["queries"]:
        full = memory.search(conn, query["question"])
        results[query["id"]] = full
        task_only = task_only_search(conn, query["question"])
        returned_tasks = [item["task_id"] for item in full["candidates"]]
        expected_tasks = query.get("expected_task_ids", [])
        expected_sources = [memory.normalize_path(path) for path in query.get("expected_source_paths", [])]
        visible_sources = {
            source["path"]
            for candidate in full["candidates"]
            if candidate["task_id"] in expected_tasks
            for source in candidate["source_choices"]
        }
        found_tasks = [task_id for task_id in expected_tasks if task_id in returned_tasks]
        task_only_found = [task_id for task_id in expected_tasks if task_id in task_only]
        found_sources = [path for path in expected_sources if path in visible_sources]
        task_hits += len(found_tasks)
        task_only_hits += len(task_only_found)
        task_total += len(expected_tasks)
        source_hits += len(found_sources)
        source_total += len(expected_sources)
        expected_abstention = not expected_tasks
        actual_abstention = full["strength"]["recommendation"] == "no_strong_match"
        abstention_hits += int(expected_abstention == actual_abstention)
        if len(expected_tasks) > 1:
            compound_total += 1
            compound_complete += int(len(found_tasks) == len(expected_tasks))
        per_query.append({
            "id": query["id"],
            "expected_tasks": expected_tasks,
            "returned_tasks": returned_tasks,
            "task_only_returned_tasks": task_only,
            "missing_tasks": [task_id for task_id in expected_tasks if task_id not in returned_tasks],
            "task_only_missing_tasks": [task_id for task_id in expected_tasks if task_id not in task_only],
            "expected_sources": expected_sources,
            "visible_expected_sources": found_sources,
            "hidden_expected_sources": [path for path in expected_sources if path not in visible_sources],
            "expected_abstention": expected_abstention,
            "recommendation": full["strength"]["recommendation"],
            "query_coverage": full["strength"]["query_coverage"],
            "supporting_channels": full["strength"]["supporting_channels"],
            "query_parts": full["query_parts"],
            "query_ms": full["query_ms"],
        })
    return {
        "task_recall_at_6": round(task_hits / task_total, 4) if task_total else None,
        "task_hits": task_hits,
        "task_only_recall_at_6": round(task_only_hits / task_total, 4) if task_total else None,
        "task_only_hits": task_only_hits,
        "total_expected_tasks": task_total,
        "expected_source_visibility": round(source_hits / source_total, 4) if source_total else None,
        "source_hits": source_hits,
        "total_expected_sources": source_total,
        "compound_complete": compound_complete,
        "compound_total": compound_total,
        "abstention_accuracy": round(abstention_hits / len(spec["queries"]), 4),
        "abstention_hits": abstention_hits,
        "total_queries": len(spec["queries"]),
        "per_query": per_query,
    }, results


def render_packet(
    query: dict[str, Any],
    result: dict[str, Any],
    *,
    corpus_count: int,
    ceiling: int,
    watermark: str,
) -> tuple[str, int]:
    strength = result["strength"]
    lines = [
        f"# TASK-260 Fresh Holdout Packet — {query['id']}",
        "",
        "Generated retrieval aid; not authority. Use only this packet.",
        f"- corpus: {corpus_count} completed task records with linked source documents",
        f"- query parts: {' | '.join(result['query_parts'])}",
        f"- algorithm signal: {strength['recommendation']} "
        f"(coverage {strength['query_coverage']:.0%}; supporting channels {strength['supporting_channels']})",
        f"- watermark: {watermark}",
        "- no strong match is a valid answer",
        "",
        "## Query",
        "",
        query["question"],
        "",
        "## Candidates",
        "",
    ]
    for position, candidate in enumerate(result["candidates"], 1):
        lines.extend([
            f"### {position}. {candidate['task_id']} — {candidate['title']}",
            f"- {candidate['project']} / {candidate['workstream']} / {candidate['status']}",
            f"- scope: {base.truncate_words(candidate['goal'], 24)}",
            "- linked evidence:",
        ])
        for source in candidate["source_choices"]:
            health = "resolved" if source["exists_now"] else "unresolved"
            lines.append(
                f"  - `{source['path']}` [{source['role']}; {source['temporal_mode']}; {health}] — "
                f"{base.truncate_words(source['summary'], 16)}"
            )
        lines.append("")
    lines.extend([
        "## Required response",
        "",
        "Return one line: `query ID | up to two TASK IDs or NO MATCH | up to",
        "three source paths | confidence high/medium/low | concise reasoning`.",
        "State ambiguity and whether anything outside this packet was accessed.",
        "",
    ])
    text = "\n".join(lines)
    estimate = base.estimate_tokens(text)
    if estimate > ceiling:
        raise ValueError(f"{query['id']} packet estimate {estimate} exceeds ceiling {ceiling}")
    text += f"- estimated packet tokens: {estimate}\n"
    return text, estimate


def generate(
    spec_path: Path,
    output: Path,
    packet: Path,
    packet_dir: Path,
) -> dict[str, Any]:
    spec = base.load_json(spec_path)
    findings = validate_spec(spec)
    if findings:
        raise SystemExit("invalid holdout spec:\n- " + "\n- ".join(findings))
    with tempfile.TemporaryDirectory(prefix="map-task260-") as temp_dir:
        db_path = Path(temp_dir) / "holdout.db"
        build = memory.build_database(db_path, spec["corpus_task_ids"])
        with sqlite3.connect(db_path) as conn:
            metrics, results = algorithm_metrics(conn, spec)
    contract = spec["retrieval_contract"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    combined = [
        "# TASK-260 Combined Fresh Holdout Packets",
        "",
        "Audit copy only. Evaluator receives one packet at a time.",
        "",
    ]
    estimates = {}
    for query in spec["queries"]:
        text, estimate = render_packet(
            query,
            results[query["id"]],
            corpus_count=build["task_count"],
            ceiling=contract["discovery_packet_max_estimated_tokens"],
            watermark=spec["frozen_at"],
        )
        (packet_dir / f"{query['id']}.md").write_text(text, encoding="utf-8")
        estimates[query["id"]] = estimate
        combined.extend([text.rstrip(), "", "---", ""])
    combined_text = "\n".join(combined).rstrip() + "\n"
    packet.parent.mkdir(parents=True, exist_ok=True)
    packet.write_text(combined_text, encoding="utf-8")
    payload = {
        "experiment": "TASK-260-fresh-holdout",
        "generated_at": memory.utc_now(),
        "projection_authority": "none; frozen retriever evaluation only",
        "retriever_sha256": spec["retriever_sha256"],
        "harness_sha256": spec["harness_sha256"],
        "source_spec": memory.normalize_path(str(spec_path)),
        "build": build,
        "metrics_before_helper": metrics,
        "packet_estimated_tokens": estimates,
        "combined_packet_estimated_tokens": base.estimate_tokens(combined_text),
    }
    base.write_json(output, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = generate(args.spec, args.output, args.packet, args.packet_dir)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
