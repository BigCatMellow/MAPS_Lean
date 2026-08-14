#!/usr/bin/env python3
"""Disposable query-global evidence selector for MAP task-memory packets.

This layer deliberately sits after task selection.  It does not change the
frozen TASK-259 retriever, declare task authority, or decide whether a task is
the answer.  Given a query and an already selected task set, it greedily
allocates a small, query-wide evidence budget using lexical clause coverage,
proof-role demand, task linkage, path health, temporal attribution, and
non-redundancy.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_holdout as typed  # noqa: E402
from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402
from MAP_System.scripts import task_memory_fts as memory  # noqa: E402


DEFAULT_SPEC = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-queries-2026-07-19.json"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-evidence-verifier-development-2026-07-19.json"
)
DEFAULT_PACKET_DIR = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-query-global-packets-2026-07-19"
)
SOURCE_LIMIT = 3
MAX_CANDIDATE_SOURCE_BYTES = 64 * 1024

FROZEN_INPUTS = {
    "retriever": (
        ROOT / "scripts" / "task_memory_fts.py",
        "edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27",
    ),
    "retriever_tests": (
        ROOT / "tests" / "test_task_memory_fts.py",
        "58df22f41258c3cea27d48ddbf413bf1b0c9c63eead9016b58008718a677949f",
    ),
    "holdout_harness": (
        ROOT / "scripts" / "task_memory_fts_holdout.py",
        "65219824dc3c2d5f62b77923a0bd9cd3f6c21d3222ee9db9f3e5bcff723a83ff",
    ),
    "holdout_harness_tests": (
        ROOT / "tests" / "test_task_memory_fts_holdout.py",
        "3d97e70c1624a714ae2620993959f7c23abf39cbc4cdca5a45aec149f2dacd0c",
    ),
}

# Observed visible run, 2026-07-19 22:36-22:39 UTC.  The helper received
# exactly the frozen packet named by input_event_id.  Responses were visible
# in its terminal transcript but were not returned through hcom as requested.
PI_VERIFIER_OBSERVATION = {
    "helper": "helper-index-local-verifier-bero",
    "model_display": "qwen2.5-coder:7b-16k",
    "delivery": "one frozen TASK-260 packet per hcom message",
    "repository_command_events": 0,
    "repository_file_events": 0,
    "self_reported_outside_context": False,
    "hcom_responses_returned": 0,
    "context_compactions_observed": 2,
    "final_terminal_token_display": {"cumulative_input_approx": 114000, "output_approx": 696},
    "task_metrics": {
        "expected_positive_task_ids": 12,
        "correct_positive_task_ids": 8,
        "returned_positive_task_ids": 13,
        "task_recall": 0.6667,
        "task_precision": 0.6154,
        "exact_positive_task_sets": 1,
        "positive_queries": 8,
        "negative_rejections": 3,
        "negative_queries": 3,
        "mixed_task_and_no_match_responses": 4,
        "over_budget_task_responses": 1,
    },
    "source_metrics": {
        "exact_expected_source_hits": 9,
        "expected_sources": 20,
        "exact_source_visibility": 0.45,
        "returned_source_paths": 14,
        "exact_source_precision": 0.6429,
    },
    "latency_seconds": {
        "values": [9, 3, 3, 2, 3, 3, 13, 8, 3, 12, 9],
        "median": 3,
        "total": 68,
    },
    "per_query": [
        {"id": "F1", "input_event_id": 7963, "task_ids": ["TASK-214", "TASK-215"], "sources": ["Projects/ClearFront/app/js/combat.js", "Projects/ClearFront/app/js/state.js"], "confidence": "medium", "latency_seconds": 9},
        {"id": "F2", "input_event_id": 7978, "task_ids": ["TASK-213", "TASK-214"], "sources": ["Projects/ClearFront/app/index.html", "Projects/ClearFront/app/js/combat.js"], "confidence": "high", "latency_seconds": 3},
        {"id": "F3", "input_event_id": 7988, "task_ids": ["TASK-223", "TASK-224", "TASK-221"], "sources": ["MAP_System/scripts/limit_watcher.py", "MAP_System/scripts/emergence_sentinel.py", "MAP_System/tests/test_limit_watcher.py"], "confidence": "medium", "latency_seconds": 3},
        {"id": "F4", "input_event_id": 7998, "task_ids": ["TASK-232"], "also_said_no_match": True, "sources": ["MAP_System/scripts/local_runner.py"], "confidence": "low", "latency_seconds": 2},
        {"id": "F5", "input_event_id": 8006, "task_ids": ["TASK-231"], "also_said_no_match": True, "sources": ["MAP_System/tests/test_runner_helper_notes.py"], "confidence": "low", "latency_seconds": 3},
        {"id": "F6", "input_event_id": 8014, "task_ids": ["TASK-237", "TASK-240"], "sources": ["MAP_System/artifacts/tests/task237-attention-popup.md", "MAP_System/templates/install/command-center-ui/src/chat.js"], "confidence": "medium", "latency_seconds": 3},
        {"id": "F7", "input_event_id": 8024, "task_ids": ["TASK-249"], "also_said_no_match": True, "sources": ["MAP_System/scripts/pre_dispatch_policy.py", "/home/mellow/Projects/MultiAgentProject/MAP_System/tests/test_pre_dispatch_policy.py"], "confidence": "low", "latency_seconds": 13},
        {"id": "F8", "input_event_id": 8038, "task_ids": ["TASK-233"], "also_said_no_match": True, "sources": ["MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md"], "confidence": "low", "latency_seconds": 8},
        {"id": "N1", "input_event_id": 8053, "no_match": True, "sources": [], "confidence": "low", "latency_seconds": 3},
        {"id": "N2", "input_event_id": 8063, "no_match": True, "sources": [], "confidence": "low", "latency_seconds": 12},
        {"id": "N3", "input_event_id": 8073, "no_match": True, "sources": [], "confidence": "low", "latency_seconds": 9},
    ],
    "verdict": "not viable as a task/source capability verifier in this packet format",
}

# These are quality priors, not historical claims.  Current shared files are
# usable but weaker because their present text cannot be attributed precisely
# to every linked historical task.
TEMPORAL_BONUS = {
    "current_unique": 5.0,
    "task_snapshot": 2.0,
    "current_shared": -3.0,
    "unresolved": -50.0,
}


def atomic_clauses(query: str) -> list[str]:
    """Return bounded semantic clauses without model-based query expansion."""
    pieces = re.split(
        r"(?<=[?.;])\s+|\s+(?:while|whereas)\s+|"
        r",\s+(?:and\s+)?(?=(?:how|what|which|where|who|why)\b)|"
        r"\s+and\s+(?=(?:how|what|which|where|who|why)\b)",
        query,
        flags=re.IGNORECASE,
    )
    clauses: list[str] = []
    seen: set[tuple[str, ...]] = set()
    for piece in pieces:
        clean = piece.strip(" ,.;:?!")
        tokens = tuple(base.words(clean))
        if len(tokens) < 2 or tokens in seen:
            continue
        clauses.append(clean)
        seen.add(tokens)
    return clauses[:4] or [query]


def requested_roles(query: str) -> dict[str, float]:
    """Convert explicit proof language into bounded, soft role demand."""
    weights = {
        role: max(0.0, value / 16.0)
        for role, value in typed.query_role_weights(query).items()
        if value > 0
    }
    tokens = set(base.words(query))
    lower = query.lower()

    # Questions about a mechanism generally need the executable mechanism.
    if re.search(r"\b(?:how|what prevents|which .* (?:implements|detects))\b", lower):
        weights["implementation"] = max(weights.get("implementation", 0.0), 0.75)
    # Evidence/coverage language asks for validation, but this remains a bonus;
    # two complementary implementation files or tests may still both win.
    if tokens.intersection({
        "evidence", "covered", "coverage", "prove", "proves", "tested",
        "regression", "reliable", "preserved", "preserve", "behavior",
        "prevents", "prevent", "reject", "rejected", "kept",
    }):
        weights["test"] = max(weights.get("test", 0.0), 0.85)
    if tokens.intersection({
        "measured", "result", "results", "reveal", "revealed", "worked",
        "deployed", "verification",
    }):
        weights["outcome"] = max(weights.get("outcome", 0.0), 0.65)
    return weights


def _fused_sources(conn: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    _parts, _tasks, source_rankings = memory.retrieval_channels(conn, query)
    weights = {
        channel: (0.70 if channel.startswith("path:") else 1.0)
        for channel in source_rankings
    }
    return memory.rrf_fuse(source_rankings, weights=weights)


def bounded_source_tokens(path: str) -> set[str]:
    """Read a bounded candidate prefix for selection, never for task authority."""
    resolved = memory.resolve_path(path)
    if not resolved.is_file() or resolved.suffix.lower() not in {
        ".py", ".js", ".mjs", ".ts", ".html", ".css", ".sh", ".lua",
    }:
        return set()
    try:
        with resolved.open("r", encoding="utf-8", errors="replace") as handle:
            return set(base.words(handle.read(MAX_CANDIDATE_SOURCE_BYTES)))
    except OSError:
        return set()


def evidence_candidates(
    conn: sqlite3.Connection,
    query: str,
    task_ids: Iterable[str],
) -> list[dict[str, Any]]:
    """Score every source linked to the selected tasks; do not allocate yet."""
    ordered_tasks = list(dict.fromkeys(task_ids))
    source_ranking = _fused_sources(conn, query)
    rank_map = {item["id"]: rank for rank, item in enumerate(source_ranking, 1)}
    rrf_map = {item["id"]: item["rrf_score"] for item in source_ranking}
    clauses = [set(base.words(clause)) for clause in atomic_clauses(query)]
    query_tokens = set().union(*clauses) if clauses else set(base.words(query))
    role_demand = requested_roles(query)
    explicit_task_scope = bool(re.search(
        r"\b(?:task\s+record|recorded\s+task|declared\s+scope|task\s+status|"
        r"task\s+owner|who\s+owns)\b",
        query,
        re.IGNORECASE,
    ))

    path_tasks: defaultdict[str, set[str]] = defaultdict(set)
    task_context: dict[str, set[str]] = {}
    for task_id in ordered_tasks:
        task = memory.task_row(conn, task_id)
        if not task:
            continue
        task_context[task_id] = set(base.words(" ".join([
            str(task.get("title", "")),
            base.truncate_words(str(task.get("goal", "")), 48),
        ])))
        for (path,) in conn.execute(
            "SELECT path FROM task_source_links WHERE task_id=? ORDER BY path",
            (task_id,),
        ):
            path_tasks[path].add(task_id)

    rows = memory.source_rows(conn, sorted(path_tasks))
    candidates = []
    for path in sorted(rows):
        row = rows[path]
        if row["role"] == "task_scope" and not explicit_task_scope:
            continue
        text = " ".join(str(row.get(key, "")) for key in (
            "title", "summary", "symbols", "path_terms", "role",
        ))
        text_tokens = set(base.words(text))
        body_tokens = bounded_source_tokens(path)
        matched_terms = query_tokens.intersection(text_tokens)
        body_matched_terms = query_tokens.intersection(body_tokens)
        linked_tasks = sorted(path_tasks[path])
        context_terms = set().union(*(task_context.get(task_id, set()) for task_id in linked_tasks))
        context_overlap = (context_terms - query_tokens).intersection(text_tokens)
        clause_matches = [
            index for index, clause_tokens in enumerate(clauses)
            if clause_tokens.intersection(text_tokens)
        ]
        role_fit = role_demand.get(row["role"], 0.0)
        global_rank = rank_map.get(path)
        retrieval_signal = rrf_map.get(path, 0.0) * 260.0
        base_score = (
            len(matched_terms) * 3.0
            + len(context_overlap) * 0.65
            + len(clause_matches) * 2.0
            + role_fit * 7.0
            + retrieval_signal
            + TEMPORAL_BONUS.get(row["temporal_mode"], 0.0)
            + min(4, len(body_matched_terms)) * 0.75
        )
        if row["role"] == "release" and not query_tokens.intersection({
            "release", "released", "ship", "shipped", "closeout", "deployed",
        }):
            base_score -= 4.0
        if not row["exists_now"]:
            base_score -= 50.0
        candidates.append({
            **row,
            "linked_selected_tasks": linked_tasks,
            "matched_terms": sorted(matched_terms),
            "task_context_terms": sorted(context_overlap),
            "bounded_body_matched_terms": sorted(body_matched_terms),
            "clause_matches": clause_matches,
            "role_fit": round(role_fit, 4),
            "global_source_rank": global_rank,
            "rrf_score": rrf_map.get(path, 0.0),
            "base_score": round(base_score, 6),
        })
    return candidates


def allocate_evidence(
    candidates: Iterable[dict[str, Any]],
    *,
    limit: int = SOURCE_LIMIT,
) -> list[dict[str, Any]]:
    """Greedily allocate one global budget with deterministic tie-breaking."""
    remaining = [dict(item) for item in candidates]
    if any(item.get("exists_now") for item in remaining):
        remaining = [item for item in remaining if item.get("exists_now")]
    selected: list[dict[str, Any]] = []
    covered_terms: set[str] = set()
    covered_clauses: set[int] = set()
    covered_tasks: set[str] = set()
    covered_roles: set[str] = set()
    covered_hashes: set[str] = set()

    while remaining and len(selected) < limit:
        def marginal(item: dict[str, Any]) -> tuple[float, float, float, str]:
            terms = set(item.get("matched_terms", []))
            clauses = set(item.get("clause_matches", []))
            tasks = set(item.get("linked_selected_tasks", []))
            union = terms.union(covered_terms)
            redundancy = len(terms.intersection(covered_terms)) / max(1, len(union))
            new_role = item.get("role") not in covered_roles
            duplicate_content = bool(item.get("sha256") and item.get("sha256") in covered_hashes)
            value = (
                float(item.get("base_score", 0.0))
                + len(terms - covered_terms) * 2.5
                + len(clauses - covered_clauses) * 5.0
                + len(tasks - covered_tasks) * 5.0
                + (float(item.get("role_fit", 0.0)) * 10.0 if new_role else 0.0)
                - redundancy * 4.0
                - (50.0 if duplicate_content else 0.0)
            )
            # max() is used below; the inverted rank makes a better global rank
            # win before the stable path tie-breaker.
            rank = item.get("global_source_rank")
            rank_tie = -float(rank) if rank is not None else float("-inf")
            return value, float(item.get("rrf_score", 0.0)), rank_tie, item["path"]

        best = max(remaining, key=marginal)
        remaining.remove(best)
        value = marginal(best)[0]
        best["marginal_score"] = round(value, 6)
        best["selection_position"] = len(selected) + 1
        selected.append(best)
        covered_terms.update(best.get("matched_terms", []))
        covered_clauses.update(best.get("clause_matches", []))
        covered_tasks.update(best.get("linked_selected_tasks", []))
        covered_roles.add(str(best.get("role", "")))
        if best.get("sha256"):
            covered_hashes.add(str(best["sha256"]))
    return selected


def select_evidence(
    conn: sqlite3.Connection,
    query: str,
    task_ids: Iterable[str],
    *,
    limit: int = SOURCE_LIMIT,
) -> dict[str, Any]:
    started = time.perf_counter()
    ordered_tasks = list(dict.fromkeys(task_ids))
    candidates = evidence_candidates(conn, query, ordered_tasks)
    selected = allocate_evidence(candidates, limit=limit)
    return {
        "query": query,
        "selected_task_ids": ordered_tasks,
        "clauses": atomic_clauses(query),
        "requested_roles": requested_roles(query),
        "budget": limit,
        "sources": selected,
        "candidate_source_count": len(candidates),
        "selection_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def render_packet(query_id: str, selection: dict[str, Any]) -> str:
    lines = [
        f"# TASK-261 Query-Global Evidence Packet — {query_id}",
        "",
        "Development projection; not authority. Task selection is supplied by the prior evaluator.",
        f"- selected tasks: {', '.join(selection['selected_task_ids']) or 'none'}",
        f"- global source budget: {selection['budget']}",
        f"- clauses: {' | '.join(selection['clauses'])}",
        "",
        "## Query",
        "",
        selection["query"],
        "",
        "## Query-global evidence",
        "",
    ]
    for source in selection["sources"]:
        tasks = ", ".join(source["linked_selected_tasks"])
        lines.append(
            f"- `{source['path']}` [{source['role']}; {source['temporal_mode']}; "
            f"linked {tasks}] — {base.truncate_words(source['summary'], 22)}"
        )
    lines.extend([
        "",
        "The selected sources are leads only. Verify against canonical task state and the files themselves.",
        "",
    ])
    return "\n".join(lines)


def evaluate_development(
    conn: sqlite3.Connection,
    spec: dict[str, Any],
    packet_dir: Path,
) -> dict[str, Any]:
    """Use known TASK-260 labels only after its evaluator selected the tasks."""
    packet_dir.mkdir(parents=True, exist_ok=True)
    fixed_hits = global_hits = total = 0
    per_query = []
    selection_times = []
    for query in spec["queries"]:
        task_ids = query.get("expected_task_ids", [])
        if not task_ids:
            continue
        fixed = memory.search(conn, query["question"])
        fixed_visible = {
            source["path"]
            for candidate in fixed["candidates"]
            if candidate["task_id"] in task_ids
            for source in candidate["source_choices"]
        }
        selection = select_evidence(conn, query["question"], task_ids)
        global_visible = {source["path"] for source in selection["sources"]}
        expected = [memory.normalize_path(path) for path in query["expected_source_paths"]]
        fixed_found = [path for path in expected if path in fixed_visible]
        global_found = [path for path in expected if path in global_visible]
        fixed_hits += len(fixed_found)
        global_hits += len(global_found)
        total += len(expected)
        selection_times.append(selection["selection_ms"])
        packet_text = render_packet(query["id"], selection)
        packet_path = packet_dir / f"{query['id']}.md"
        packet_path.write_text(packet_text, encoding="utf-8")
        per_query.append({
            "id": query["id"],
            "selected_task_ids": task_ids,
            "expected_sources": expected,
            "fixed_visible_expected_sources": fixed_found,
            "query_global_visible_expected_sources": global_found,
            "fixed_hidden_expected_sources": [path for path in expected if path not in fixed_visible],
            "query_global_hidden_expected_sources": [path for path in expected if path not in global_visible],
            "query_global_sources": [source["path"] for source in selection["sources"]],
            "selection_ms": selection["selection_ms"],
            "packet_estimated_tokens": base.estimate_tokens(packet_text),
        })
    sorted_times = sorted(selection_times)
    median = sorted_times[len(sorted_times) // 2] if sorted_times else 0.0
    return {
        "evaluation_mode": "known TASK-260 development; task-conditioned after evaluator task selection",
        "positive_queries": len(per_query),
        "expected_sources": total,
        "fixed_selector_hits": fixed_hits,
        "fixed_selector_visibility": round(fixed_hits / total, 4) if total else None,
        "query_global_hits": global_hits,
        "query_global_visibility": round(global_hits / total, 4) if total else None,
        "source_budget_per_query": SOURCE_LIMIT,
        "median_selection_ms": median,
        "per_query": per_query,
    }


def generate(spec_path: Path, output: Path, packet_dir: Path) -> dict[str, Any]:
    spec = base.load_json(spec_path)
    with tempfile.TemporaryDirectory(prefix="map-task261-") as temp_dir:
        db_path = Path(temp_dir) / "development.db"
        build = memory.build_database(db_path, spec["corpus_task_ids"])
        with sqlite3.connect(db_path) as conn:
            metrics = evaluate_development(conn, spec, packet_dir)
    payload = {
        "experiment": "TASK-261",
        "authority": "none; disposable development projection",
        "development_source": str(spec_path.relative_to(REPO)),
        "task_selection_condition": (
            "TASK-260 blinded evaluator selected every expected task with no extras; "
            "known labels are supplied here solely to isolate evidence allocation"
        ),
        "build": build,
        "metrics": metrics,
        "frozen_input_hashes": {
            name: {
                "path": str(path.relative_to(REPO)),
                "expected": expected,
                "actual": base.sha256(path),
                "unchanged": base.sha256(path) == expected,
            }
            for name, (path, expected) in FROZEN_INPUTS.items()
        },
        "local_pi_verifier": PI_VERIFIER_OBSERVATION,
    }
    base.write_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    args = parser.parse_args()
    payload = generate(args.spec, args.output, args.packet_dir)
    metrics = payload["metrics"]
    print(json.dumps({
        "fixed": metrics["fixed_selector_visibility"],
        "query_global": metrics["query_global_visibility"],
        "source_hits": metrics["query_global_hits"],
        "source_total": metrics["expected_sources"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
