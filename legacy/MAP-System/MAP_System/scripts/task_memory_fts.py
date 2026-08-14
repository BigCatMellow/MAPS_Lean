#!/usr/bin/env python3
"""Disposable SQLite FTS5/RRF baseline for MAP durable-memory retrieval.

This experiment never becomes task authority. It indexes frozen task mirrors
and current registered sources into a rebuildable local database, keeps source
documents separate from task/source links, labels temporal attribution, and
returns bounded task/evidence candidates with explicit match provenance.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
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

from MAP_System.scripts import task_fingerprint_holdout as typed
from MAP_System.scripts import task_fingerprint_pilot as base
from MAP_System.scripts import task_fingerprint_source_holdout as source_base


DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-development-2026-07-19.json"
)
DEFAULT_SPECS = [
    (
        "TASK-257-known-development",
        ROOT / "artifacts" / "experiments" /
        "task-fingerprint-holdout-queries-2026-07-19.json",
    ),
    (
        "TASK-258-known-development",
        ROOT / "artifacts" / "experiments" /
        "task-fingerprint-source-holdout-queries-2026-07-19.json",
    ),
]
RRF_K = 60
TASK_LIMIT = 6
SOURCE_LIMIT = 2

TEMPORAL_WEIGHTS = {
    # Source-to-task propagation is a recall fallback, not a vote proportional
    # to how many outputs a task happened to register. Direct task fields stay
    # dominant; current shared text is deliberately weakest.
    "task_snapshot": 0.10,
    "current_unique": 0.25,
    "current_shared": 0.05,
    "unresolved": 0.0,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_path(raw: str, repo: Path = REPO) -> str:
    """Return a stable display key without pretending missing paths resolve."""
    path = Path(raw)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(repo.resolve()).as_posix()
        except (OSError, ValueError):
            return path.as_posix().rstrip("/")
    return path.as_posix().rstrip("/")


def resolve_path(raw: str, repo: Path = REPO) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else repo / path


def fts_query(text: str, *, trigram: bool = False) -> str:
    tokens = []
    for token in base.words(text):
        if trigram and len(token) < 3:
            continue
        if token not in tokens:
            tokens.append(token)
    return " OR ".join(f'"{token}"' for token in tokens)


def query_parts(query: str, *, limit: int = source_base.MAX_QUERY_PARTS) -> list[str]:
    """Split explicit compound clauses without free-form model expansion."""
    candidates = [query.strip()]
    keys = {" ".join(base.words(query))}
    connector_parts = re.split(
        r"\s+(?:or|versus|whereas|while)\s+|\s*;\s*|"
        r",\s+and\s+(?=(?:which|what|where|who|how|why)\b)|"
        r"\s+and\s+(?=(?:which|what|where|who|how|why)\b)",
        query,
        flags=re.IGNORECASE,
    )
    sentence_parts = re.split(r"(?<=[.!?])\s+", query)
    for part in [*connector_parts, *sentence_parts]:
        clean = part.strip(" ,.;:?!")
        key = " ".join(base.words(clean))
        raw_word_count = len(re.findall(r"[A-Za-z0-9]+", clean))
        if raw_word_count >= 3 and key not in keys:
            candidates.append(clean)
            keys.add(key)
        if len(candidates) >= limit:
            break
    return candidates


def rrf_fuse(
    rankings: dict[str, list[str]],
    *,
    weights: dict[str, float] | None = None,
    k: int = RRF_K,
) -> list[dict[str, Any]]:
    """Fuse rankings by rank only; raw BM25/trigram scales never mix."""
    weights = weights or {}
    scores: defaultdict[str, float] = defaultdict(float)
    provenance: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for channel in sorted(rankings):
        weight = weights.get(channel, 1.0)
        seen = set()
        for rank, item_id in enumerate(rankings[channel], 1):
            if item_id in seen:
                continue
            seen.add(item_id)
            contribution = weight / (k + rank)
            scores[item_id] += contribution
            provenance[item_id].append({
                "channel": channel,
                "rank": rank,
                "weight": weight,
                "contribution": round(contribution, 8),
            })
    return [
        {
            "id": item_id,
            "rrf_score": round(score, 8),
            "provenance": provenance[item_id],
        }
        for item_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    ]


def source_fields(path: Path, display: str, role: str) -> dict[str, str]:
    summary = source_base.source_description(path, role) if path.exists() else "unresolved registered source"
    title = source_base.identifier_text(Path(display).stem or Path(display).name)
    symbols = ""
    if path.is_file() and path.suffix.lower() == ".py":
        text = path.read_text(encoding="utf-8", errors="replace")[: source_base.MAX_SOURCE_BYTES]
        try:
            tree = ast.parse(text)
            names = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = source_base.identifier_text(node.name)
                    if name and name not in names:
                        names.append(name)
            symbols = base.truncate_words("; ".join(names), 120)
        except (SyntaxError, ValueError):
            symbols = ""
    return {
        "title": title,
        "summary": summary,
        "symbols": symbols,
        "path_terms": source_base.identifier_text(display),
        "role_text": f"{role} {typed.ROLE_PROOF.get(role, '')}",
    }


def temporal_mode(path: str, role: str, linked_task_count: int, exists: bool) -> str:
    if not exists:
        return "unresolved"
    if role == "task_scope" and path.startswith("MAP_System/tasks/TASK-"):
        return "task_snapshot"
    if linked_task_count > 1:
        return "current_shared"
    return "current_unique"


def task_payload(task: dict[str, Any]) -> dict[str, str]:
    outputs = task.get("output_paths", [])
    title = str(task.get("title", ""))
    description = str(task.get("description", ""))
    return {
        "task_id": task["task_id"],
        "title": title,
        "goal": description,
        "acceptance": " ".join(str(value) for value in task.get("acceptance_criteria", [])),
        "path_terms": " ".join(source_base.identifier_text(value) for value in outputs),
        "project": base.infer_project(outputs, title),
        "workstream": base.infer_workstream(title, description, outputs),
        "status": str(task.get("status", "UNKNOWN")),
    }


SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE task_documents (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    goal TEXT NOT NULL,
    acceptance TEXT NOT NULL,
    path_terms TEXT NOT NULL,
    project TEXT NOT NULL,
    workstream TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE source_documents (
    path TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    symbols TEXT NOT NULL,
    path_terms TEXT NOT NULL,
    role TEXT NOT NULL,
    role_text TEXT NOT NULL,
    exists_now INTEGER NOT NULL,
    sha256 TEXT,
    linked_task_count INTEGER NOT NULL,
    temporal_mode TEXT NOT NULL,
    historical_attribution INTEGER NOT NULL
);
CREATE TABLE task_source_links (
    task_id TEXT NOT NULL,
    path TEXT NOT NULL,
    link_kind TEXT NOT NULL,
    PRIMARY KEY (task_id, path),
    FOREIGN KEY (task_id) REFERENCES task_documents(task_id),
    FOREIGN KEY (path) REFERENCES source_documents(path)
);
CREATE VIRTUAL TABLE task_fts USING fts5(
    task_id UNINDEXED, title, goal, acceptance, path_terms, project, workstream,
    tokenize='porter unicode61'
);
CREATE VIRTUAL TABLE source_fts USING fts5(
    path UNINDEXED, title, summary, symbols, path_terms, role_text,
    tokenize='porter unicode61'
);
CREATE VIRTUAL TABLE path_fts USING fts5(
    path UNINDEXED, path_terms, tokenize='trigram'
);
"""


def build_database(
    db_path: Path,
    corpus_task_ids: Iterable[str],
    *,
    tasks_dir: Path = ROOT / "tasks",
    repo: Path = REPO,
) -> dict[str, Any]:
    started = time.perf_counter()
    tasks = []
    missing_tasks = []
    links: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)

    for task_id in corpus_task_ids:
        task_path = tasks_dir / f"{task_id}.json"
        if not task_path.is_file():
            missing_tasks.append(task_id)
            continue
        task = base.load_json(task_path)
        tasks.append(task)
        task_ref = normalize_path(str(task_path), repo)
        links[task_ref].append((task_id, "task_record"))
        for raw in task.get("output_paths", []):
            links[normalize_path(raw, repo)].append((task_id, "registered_output"))

    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO metadata VALUES (?, ?)", ("projection_authority", "none"))
        conn.execute("INSERT INTO metadata VALUES (?, ?)", ("generated_at", utc_now()))

        for task in tasks:
            payload = task_payload(task)
            conn.execute(
                "INSERT INTO task_documents VALUES (?,?,?,?,?,?,?,?)",
                tuple(payload[key] for key in (
                    "task_id", "title", "goal", "acceptance", "path_terms",
                    "project", "workstream", "status",
                )),
            )
            conn.execute(
                "INSERT INTO task_fts VALUES (?,?,?,?,?,?,?)",
                tuple(payload[key] for key in (
                    "task_id", "title", "goal", "acceptance", "path_terms",
                    "project", "workstream",
                )),
            )

        unresolved_instances = 0
        temporal_counts: defaultdict[str, int] = defaultdict(int)
        for display in sorted(links):
            raw_path = resolve_path(display, repo)
            exists = raw_path.exists()
            if not exists:
                unresolved_instances += len(links[display])
            role = typed.evidence_role(display, repo)
            task_ids = sorted({task_id for task_id, _kind in links[display]})
            mode = temporal_mode(display, role, len(task_ids), exists)
            temporal_counts[mode] += 1
            fields = source_fields(raw_path, display, role)
            digest = base.sha256(raw_path) if raw_path.is_file() else None
            historical = int(mode == "task_snapshot")
            conn.execute(
                "INSERT INTO source_documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    display, fields["title"], fields["summary"], fields["symbols"],
                    fields["path_terms"], role, fields["role_text"], int(exists),
                    digest, len(task_ids), mode, historical,
                ),
            )
            conn.execute(
                "INSERT INTO source_fts VALUES (?,?,?,?,?,?)",
                (
                    display, fields["title"], fields["summary"], fields["symbols"],
                    fields["path_terms"], fields["role_text"],
                ),
            )
            conn.execute("INSERT INTO path_fts VALUES (?,?)", (display, fields["path_terms"]))
            for task_id in task_ids:
                kinds = {kind for linked_task, kind in links[display] if linked_task == task_id}
                link_kind = "task_record" if "task_record" in kinds else "registered_output"
                conn.execute(
                    "INSERT INTO task_source_links VALUES (?,?,?)",
                    (task_id, display, link_kind),
                )

    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "task_count": len(tasks),
        "missing_task_ids": missing_tasks,
        "source_document_count": len(links),
        "task_source_link_count": sum(
            len({task_id for task_id, _kind in values}) for values in links.values()
        ),
        "reused_source_count": sum(len({task for task, _kind in values}) > 1 for values in links.values()),
        "unresolved_link_instances": unresolved_instances,
        "temporal_mode_counts": dict(sorted(temporal_counts.items())),
        "build_ms": round(elapsed_ms, 3),
        "database_bytes": db_path.stat().st_size,
    }


def _rank_fts(conn: sqlite3.Connection, table: str, query: str, limit: int) -> list[str]:
    if not query:
        return []
    if table == "task_fts":
        id_column = "task_id"
        bm25 = "bm25(task_fts,0.0,8.0,4.0,3.0,2.0,1.0,1.0)"
    elif table == "source_fts":
        id_column = "path"
        bm25 = "bm25(source_fts,0.0,8.0,8.0,5.0,4.0,1.0)"
    else:
        id_column = "path"
        bm25 = "bm25(path_fts,0.0,1.0)"
    sql = (
        f"SELECT {id_column} FROM {table} WHERE {table} MATCH ? "
        f"ORDER BY {bm25}, {id_column} LIMIT ?"
    )
    return [row[0] for row in conn.execute(sql, (query, limit))]


def retrieval_channels(
    conn: sqlite3.Connection,
    query: str,
    *,
    per_channel_limit: int = 40,
) -> tuple[list[str], dict[str, list[str]], dict[str, list[str]]]:
    parts = query_parts(query)
    task_rankings = {}
    source_rankings = {}
    for index, part in enumerate(parts):
        lexical = fts_query(part)
        trigram = fts_query(part, trigram=True)
        task_rankings[f"task:{index}"] = _rank_fts(conn, "task_fts", lexical, per_channel_limit)
        source_rankings[f"source:{index}"] = _rank_fts(conn, "source_fts", lexical, per_channel_limit)
        source_rankings[f"path:{index}"] = _rank_fts(conn, "path_fts", trigram, per_channel_limit)
    return parts, task_rankings, source_rankings


def source_rows(conn: sqlite3.Connection, paths: Iterable[str]) -> dict[str, dict[str, Any]]:
    result = {}
    for path in paths:
        row = conn.execute(
            """
            SELECT path,title,summary,symbols,path_terms,role,exists_now,sha256,
                   linked_task_count,temporal_mode,historical_attribution
            FROM source_documents WHERE path=?
            """,
            (path,),
        ).fetchone()
        if row:
            result[path] = dict(zip(
                (
                    "path", "title", "summary", "symbols", "path_terms", "role",
                    "exists_now", "sha256", "linked_task_count", "temporal_mode",
                    "historical_attribution",
                ),
                row,
            ))
    return result


def task_rankings_from_sources(
    conn: sqlite3.Connection,
    source_rankings: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, float]]:
    rankings: dict[str, list[str]] = {}
    weights: dict[str, float] = {}
    for channel, paths in source_rankings.items():
        by_mode: defaultdict[str, list[str]] = defaultdict(list)
        seen: defaultdict[str, set[str]] = defaultdict(set)
        for path in paths:
            row = conn.execute(
                "SELECT temporal_mode FROM source_documents WHERE path=?",
                (path,),
            ).fetchone()
            if not row:
                continue
            mode = row[0]
            for (task_id,) in conn.execute(
                "SELECT task_id FROM task_source_links WHERE path=? ORDER BY task_id",
                (path,),
            ):
                if task_id not in seen[mode]:
                    by_mode[mode].append(task_id)
                    seen[mode].add(task_id)
        for mode, task_ids in by_mode.items():
            name = f"{channel}:{mode}"
            rankings[name] = task_ids
            weights[name] = TEMPORAL_WEIGHTS[mode]
    return rankings, weights


def select_sources_for_task(
    conn: sqlite3.Connection,
    task_id: str,
    query: str,
    fused_sources: list[dict[str, Any]],
    *,
    limit: int = SOURCE_LIMIT,
) -> list[dict[str, Any]]:
    score_map = {item["id"]: item["rrf_score"] for item in fused_sources}
    rank_map = {item["id"]: rank for rank, item in enumerate(fused_sources, 1)}
    paths = [
        row[0]
        for row in conn.execute(
            "SELECT path FROM task_source_links WHERE task_id=? ORDER BY path",
            (task_id,),
        )
    ]
    rows = source_rows(conn, paths)
    query_tokens = set(base.words(query))
    task = task_row(conn, task_id) or {}
    task_context_tokens = set(base.words(" ".join([
        str(task.get("title", "")),
        base.truncate_words(str(task.get("goal", "")), 40),
    ])))
    explicit_task_scope = bool(re.search(
        r"\b(?:which|what)\s+(?:task\s+)?record\b|\bwho\s+owns\b|"
        r"\btask\s+status\b|\bdeclared\s+scope\b",
        query,
        re.IGNORECASE,
    ))
    candidates = []
    for path, row in rows.items():
        text = " ".join(
            str(row[key]) for key in ("title", "summary", "symbols", "path_terms", "role")
        )
        text_tokens = set(base.words(text))
        overlap = query_tokens.intersection(text_tokens)
        context_overlap = (task_context_tokens - query_tokens).intersection(text_tokens)
        role_signal = typed.query_role_weights(query).get(row["role"], 0) / 12.0
        relevance = (
            len(overlap) * 3.0
            + len(context_overlap) * 1.25
            + role_signal
            + score_map.get(path, 0) * 300
        )
        source_name = Path(path).name.lower()
        if (
            query_tokens.intersection({"check", "drift", "mismatch", "mismatches", "validate", "validation", "verify"})
            and source_name.startswith(("validate", "check"))
        ):
            relevance += 12.0
        if (
            query_tokens.intersection({"user", "button", "click", "action", "interface", "control"})
            and Path(path).suffix.lower() in {".html", ".htm"}
        ):
            relevance += 10.0
        if (
            query_tokens.intersection({"policy", "authority", "permission", "rule"})
            and ("policy" in source_name or row["role"] in {"decision", "current_state"})
        ):
            relevance += 5.0
        if row["role"] == "task_scope" and not explicit_task_scope:
            relevance -= 6.0
        candidates.append({
            **row,
            "rrf_score": score_map.get(path, 0),
            "global_source_rank": rank_map.get(path),
            "matched_terms": sorted(overlap),
            "task_context_terms": sorted(context_overlap),
            "selection_score": relevance,
        })

    resolved = [item for item in candidates if item["exists_now"]]
    if len(resolved) >= limit:
        candidates = resolved
    non_scope = [item for item in candidates if item["role"] != "task_scope"]
    if not explicit_task_scope and len(non_scope) >= limit:
        candidates = non_scope

    selected = []
    remaining = candidates[:]
    covered: set[str] = set()
    while remaining and len(selected) < limit:
        selected_roles = {item["role"] for item in selected}

        def marginal(item: dict[str, Any]) -> tuple[float, float, str]:
            terms = set(item["matched_terms"])
            new_terms = terms - covered
            redundancy = len(terms.intersection(covered)) / max(1, len(terms.union(covered)))
            complement = 0.0
            if (
                (item["role"] == "implementation" and selected_roles.intersection({"test", "review", "artifact"}))
                or (item["role"] in {"test", "review", "current_state", "outcome"} and "implementation" in selected_roles)
            ):
                complement = 7.0
            value = (
                item["selection_score"]
                + len(new_terms) * 4.0
                - redundancy * 2.0
                + complement
            )
            return value, item["rrf_score"], item["path"]

        preferred = remaining
        if selected and selected[0]["role"] in {"test", "review"}:
            complements = [
                item for item in remaining
                if item["role"] in {"implementation", "current_state", "decision"}
            ]
            preferred = complements or remaining
        best = max(preferred, key=marginal)
        remaining.remove(best)
        selected.append(best)
        covered.update(best["matched_terms"])
    return selected


def task_row(conn: sqlite3.Connection, task_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT task_id,title,goal,acceptance,project,workstream,status FROM task_documents WHERE task_id=?",
        (task_id,),
    ).fetchone()
    if not row:
        return None
    return dict(zip(
        ("task_id", "title", "goal", "acceptance", "project", "workstream", "status"),
        row,
    ))


def search(
    conn: sqlite3.Connection,
    query: str,
    *,
    task_limit: int = TASK_LIMIT,
    source_limit: int = SOURCE_LIMIT,
) -> dict[str, Any]:
    started = time.perf_counter()
    parts, direct_task_rankings, source_rankings = retrieval_channels(conn, query)
    linked_task_rankings, source_task_weights = task_rankings_from_sources(conn, source_rankings)
    all_task_rankings = {**direct_task_rankings, **linked_task_rankings}
    task_weights = {channel: 1.0 for channel in direct_task_rankings}
    task_weights.update(source_task_weights)
    fused_tasks = rrf_fuse(all_task_rankings, weights=task_weights)

    source_weights = {
        channel: (0.70 if channel.startswith("path:") else 1.0)
        for channel in source_rankings
    }
    fused_sources = rrf_fuse(source_rankings, weights=source_weights)
    candidates = []
    for fused in fused_tasks[:task_limit]:
        row = task_row(conn, fused["id"])
        if not row:
            continue
        choices = select_sources_for_task(
            conn, fused["id"], query, fused_sources, limit=source_limit
        )
        candidates.append({
            **row,
            "rrf_score": fused["rrf_score"],
            "match_provenance": fused["provenance"],
            "source_choices": choices,
        })

    query_tokens = set(base.words(query))
    if candidates:
        top = candidates[0]
        evidence_text = " ".join(
            " ".join(str(source.get(key, "")) for key in ("title", "summary", "symbols", "path_terms"))
            for source in top["source_choices"]
        )
        top_text = " ".join([top["title"], top["goal"], top["acceptance"], evidence_text])
        matched = query_tokens.intersection(base.words(top_text))
        coverage = len(matched) / len(query_tokens) if query_tokens else 0.0
        supporting_channels = len({
            item["channel"]
            for item in top["match_provenance"]
            if item["rank"] <= 10 and item["weight"] > 0
        })
        strong = coverage >= 0.20 and supporting_channels >= 2
    else:
        matched = set()
        coverage = 0.0
        supporting_channels = 0
        strong = False

    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "query": query,
        "query_parts": parts,
        "strength": {
            "recommendation": "candidate_set" if strong else "no_strong_match",
            "query_coverage": round(coverage, 4),
            "supporting_channels": supporting_channels,
            "matched_terms": sorted(matched),
            "threshold": {"min_coverage": 0.20, "min_supporting_channels": 2},
        },
        "candidates": candidates,
        "source_ranking": fused_sources,
        "query_ms": round(elapsed_ms, 3),
    }


def reciprocal_rank(expected: Iterable[str], returned: list[str]) -> float:
    ranks = {item: index for index, item in enumerate(returned, 1)}
    values = [1.0 / ranks[item] if item in ranks else 0.0 for item in expected]
    return sum(values) / len(values) if values else 0.0


def evaluate_spec(conn: sqlite3.Connection, spec: dict[str, Any]) -> dict[str, Any]:
    task_hits = task_total = source_hits = source_total = 0
    abstention_hits = 0
    task_rr_values = []
    source_rr_values = []
    compound_complete = compound_total = 0
    query_times = []
    per_query = []
    for query in spec["queries"]:
        result = search(conn, query["question"])
        query_times.append(result["query_ms"])
        returned_tasks = [item["task_id"] for item in result["candidates"]]
        expected_tasks = query.get("expected_task_ids", [])
        expected_sources = query.get("expected_source_paths", [])
        visible_sources = {
            source["path"]
            for candidate in result["candidates"]
            if candidate["task_id"] in expected_tasks
            for source in candidate["source_choices"]
        }
        found_tasks = [task_id for task_id in expected_tasks if task_id in returned_tasks]
        found_sources = [path for path in expected_sources if normalize_path(path) in visible_sources]
        normalized_expected_sources = [normalize_path(path) for path in expected_sources]
        source_returned = [item["id"] for item in result["source_ranking"]]

        task_hits += len(found_tasks)
        task_total += len(expected_tasks)
        source_hits += len(found_sources)
        source_total += len(expected_sources)
        if expected_tasks:
            task_rr_values.append(reciprocal_rank(expected_tasks, returned_tasks))
        if expected_sources:
            source_rr_values.append(reciprocal_rank(normalized_expected_sources, source_returned))
        expected_abstention = not expected_tasks
        actual_abstention = result["strength"]["recommendation"] == "no_strong_match"
        abstention_hits += int(expected_abstention == actual_abstention)
        if len(expected_tasks) > 1:
            compound_total += 1
            compound_complete += int(len(found_tasks) == len(expected_tasks))

        per_query.append({
            "id": query["id"],
            "expected_tasks": expected_tasks,
            "returned_tasks": returned_tasks,
            "missing_tasks": [item for item in expected_tasks if item not in returned_tasks],
            "expected_sources": expected_sources,
            "visible_expected_sources": found_sources,
            "hidden_expected_sources": [item for item in expected_sources if normalize_path(item) not in visible_sources],
            "recommendation": result["strength"]["recommendation"],
            "expected_abstention": expected_abstention,
            "query_coverage": result["strength"]["query_coverage"],
            "supporting_channels": result["strength"]["supporting_channels"],
            "query_parts": result["query_parts"],
            "query_ms": result["query_ms"],
        })

    query_times_sorted = sorted(query_times)
    median_ms = query_times_sorted[len(query_times_sorted) // 2] if query_times_sorted else 0.0
    return {
        "task_recall_at_6": round(task_hits / task_total, 4) if task_total else None,
        "task_hits": task_hits,
        "total_expected_tasks": task_total,
        "task_mrr": round(sum(task_rr_values) / len(task_rr_values), 4) if task_rr_values else None,
        "expected_source_visibility": round(source_hits / source_total, 4) if source_total else None,
        "source_hits": source_hits,
        "total_expected_sources": source_total,
        "source_mrr": round(sum(source_rr_values) / len(source_rr_values), 4) if source_rr_values else None,
        "abstention_accuracy": round(abstention_hits / len(spec["queries"]), 4),
        "abstention_hits": abstention_hits,
        "total_queries": len(spec["queries"]),
        "compound_complete": compound_complete,
        "compound_total": compound_total,
        "query_latency_ms": {
            "min": round(min(query_times), 3) if query_times else 0.0,
            "median": round(median_ms, 3),
            "max": round(max(query_times), 3) if query_times else 0.0,
        },
        "per_query": per_query,
    }


def benchmark(specs: list[tuple[str, Path]], output: Path) -> dict[str, Any]:
    payload = {
        "experiment": "TASK-259-development-regression",
        "generated_at": utc_now(),
        "projection_authority": "none; disposable local retrieval benchmark",
        "truth_provenance": "known TASK-257 and TASK-258 truth; not fresh holdout evidence",
        "architecture": {
            "engine": "SQLite FTS5 weighted BM25",
            "channels": ["task Porter", "source Porter", "path trigram"],
            "fusion": f"reciprocal rank fusion k={RRF_K}",
            "temporal_model": "unique source_documents + task_source_links; current shared content downweighted and never cloned into task text",
        },
        "benchmarks": [],
    }
    with tempfile.TemporaryDirectory(prefix="map-task259-") as temp_dir:
        for label, spec_path in specs:
            spec = base.load_json(spec_path)
            db_path = Path(temp_dir) / f"{label}.db"
            build = build_database(db_path, spec["corpus_task_ids"])
            with sqlite3.connect(db_path) as conn:
                metrics = evaluate_spec(conn, spec)
            payload["benchmarks"].append({
                "label": label,
                "source_spec": normalize_path(str(spec_path)),
                "build": build,
                "metrics": metrics,
            })
    base.write_json(output, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    bench = subparsers.add_parser("benchmark")
    bench.add_argument(
        "--spec",
        action="append",
        nargs=2,
        metavar=("LABEL", "PATH"),
        help="Known development truth set; repeat for multiple corpora.",
    )
    bench.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)

    query = subparsers.add_parser("query")
    query.add_argument("--spec", type=Path, required=True)
    query.add_argument("--query", required=True)
    query.add_argument("--db", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "benchmark":
        specs = (
            [(label, Path(path)) for label, path in args.spec]
            if args.spec else DEFAULT_SPECS
        )
        result = benchmark(specs, args.output)
        print(json.dumps(result, indent=2))
        return 0
    spec = base.load_json(args.spec)
    build = build_database(args.db, spec["corpus_task_ids"])
    with sqlite3.connect(args.db) as conn:
        result = search(conn, args.query)
    print(json.dumps({"build": build, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
