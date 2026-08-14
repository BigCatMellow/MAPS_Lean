#!/usr/bin/env python3
"""Build and query the bounded TASK-256 task-fingerprint pilot index.

This is an experiment, not MAP authority. It reads frozen task mirrors and a
pilot spec, emits a disposable JSON projection, and renders compact top-k
retrieval packets. It never changes task state or primary evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DEFAULT_SPEC = ROOT / "artifacts" / "experiments" / "task-fingerprint-index-pilot-queries-2026-07-19.json"
DEFAULT_INDEX = ROOT / "artifacts" / "experiments" / "task-fingerprint-index-pilot-2026-07-19.json"
DEFAULT_PACKET = ROOT / "artifacts" / "experiments" / "task-fingerprint-index-helper-packet-2026-07-19.md"

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "but", "by",
    "can", "do", "does", "for", "from", "had", "has", "have", "how", "i",
    "in", "into", "is", "it", "its", "me", "no", "not", "of", "on", "or",
    "our", "should", "that", "the", "their", "this", "to", "was", "we",
    "what", "when", "where", "which", "while", "with", "work", "task",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def words(text: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS and len(token) > 1]


def truncate_words(text: str, limit: int) -> str:
    values = text.split()
    if len(values) <= limit:
        return text.strip()
    return " ".join(values[:limit]).rstrip(".,;:") + "…"


def estimate_tokens(text: str) -> int:
    """Explicit approximation used by the frozen experiment contract."""
    return math.ceil(len(text) / 4)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(raw: str, repo: Path = REPO) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else repo / path


def display_path(path: Path, raw: str, repo: Path = REPO) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return raw


def infer_project(output_paths: list[str], title: str) -> str:
    if any("Projects/ClearFront/" in path for path in output_paths) or "clearfront" in title.lower():
        return "ClearFront"
    if "ProjectUpdater" in " ".join(output_paths) or "projectupdater" in title.lower():
        return "ProjectUpdater"
    return "MAP"


def infer_workstream(title: str, description: str, output_paths: list[str]) -> str:
    text = " ".join([title, description, *output_paths]).lower()
    if "clearfront" in text:
        if any(term in text for term in ("render", "card art", "prototype", "side-rail", "side rail", "glyph")):
            return "clearfront-ui"
        if any(term in text for term in ("combat", "engine", "rules", "undo", "state.js", "input.js")):
            return "clearfront-engine"
        return "clearfront-delivery"
    if "command center" in text or "commandcenter" in text:
        return "command-center-ui"
    if any(term in text for term in ("pi ", "local ollama", "local model", "limit_watcher", "rns")):
        return "agent-liveness-and-helpers"
    if any(term in text for term in ("e/i", "emergence", "discovery agent", "operational learning")):
        return "emergence-and-learning"
    if any(term in text for term in ("practice scenario", "system-improvement", "system improvement")):
        return "map-improvement"
    return "map-runtime"


def automatic_concepts(task: dict[str, Any], limit: int = 8) -> list[str]:
    title = task.get("title", "")
    description = task.get("description", "")
    paths = " ".join(task.get("output_paths", []))
    weighted = words(title) * 4 + words(description) + words(paths)
    counts = Counter(weighted)
    return [token for token, _count in counts.most_common(limit)]


def primary_sources(task: dict[str, Any], task_path: Path, repo: Path = REPO) -> tuple[list[str], list[str]]:
    valid = [display_path(task_path, str(task_path), repo)]
    broken: list[str] = []
    for raw in task.get("output_paths", []):
        path = resolve_path(raw, repo)
        if path.exists():
            rendered = display_path(path, raw, repo)
            if rendered not in valid:
                valid.append(rendered)
        else:
            broken.append(raw)
    return valid, broken


def source_hashes(refs: list[str], repo: Path = REPO) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for ref in refs:
        path = resolve_path(ref, repo)
        if path.is_file():
            hashes[ref] = sha256(path)
    return hashes


def fingerprint_for_task(
    task: dict[str, Any],
    task_path: Path,
    curation: dict[str, Any] | None = None,
    repo: Path = REPO,
) -> dict[str, Any]:
    curation = curation or {}
    refs, broken = primary_sources(task, task_path, repo)
    concepts = curation.get("concepts") or automatic_concepts(task)
    goal = truncate_words(task.get("description", "") or task.get("title", ""), 55)
    result = curation.get("result") or f"{task.get('status', 'UNKNOWN')}: {task.get('title', '')}."
    unexpected = curation.get("unexpected", "")
    friction = curation.get("friction", "")
    project = infer_project(task.get("output_paths", []), task.get("title", ""))
    workstream = infer_workstream(task.get("title", ""), task.get("description", ""), task.get("output_paths", []))
    semantic_text = " ".join([goal, result, unexpected, friction, *concepts])
    return {
        "task_id": task["task_id"],
        "project": project,
        "workstream": workstream,
        "status": task.get("status", "UNKNOWN"),
        "title": task.get("title", ""),
        "goal": goal,
        "result": truncate_words(result, 45),
        "changed_paths": task.get("output_paths", [])[:12],
        "concepts": concepts[:8],
        "unexpected": truncate_words(unexpected, 35),
        "friction": truncate_words(friction, 35),
        "outcome": "unknown",
        "source_refs": refs,
        "source_hashes": source_hashes(refs, repo),
        "broken_output_refs": broken,
        "semantic_word_count": len(semantic_text.split()),
        "curation": "frozen_owner_curation" if curation else "deterministic_task_record",
    }


def build_index(spec: dict[str, Any], tasks_dir: Path = ROOT / "tasks", repo: Path = REPO) -> dict[str, Any]:
    fingerprints = []
    missing_tasks = []
    curation = spec.get("curation", {})
    for task_id in spec["corpus_task_ids"]:
        task_path = tasks_dir / f"{task_id}.json"
        if not task_path.exists():
            missing_tasks.append(task_id)
            continue
        task = load_json(task_path)
        fingerprints.append(fingerprint_for_task(task, task_path, curation.get(task_id), repo))
    return {
        "schema_version": 1,
        "experiment": spec.get("experiment", "TASK-256"),
        "projection_authority": "none; generated retrieval aid only",
        "generated_at": spec.get("frozen_at") or utc_now(),
        "source_spec": display_path(DEFAULT_SPEC, str(DEFAULT_SPEC), repo),
        "corpus_count": len(fingerprints),
        "missing_task_ids": missing_tasks,
        "fingerprints": fingerprints,
    }


FIELD_WEIGHTS = {
    "title": 8,
    "concepts": 7,
    "result": 5,
    "unexpected": 5,
    "friction": 5,
    "changed_paths": 3,
    "workstream": 3,
    "project": 2,
    "goal": 2,
}


def text_for_field(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value or "")


def score_fingerprint(query: str, fingerprint: dict[str, Any]) -> tuple[int, dict[str, list[str]]]:
    query_tokens = set(words(query))
    matched: dict[str, list[str]] = {}
    score = 0
    for field, weight in FIELD_WEIGHTS.items():
        field_text = text_for_field(fingerprint.get(field, ""))
        overlap = sorted(query_tokens.intersection(words(field_text)))
        if overlap:
            matched[field] = overlap
            score += len(overlap) * weight
    normalized_query = " ".join(words(query))
    for concept in fingerprint.get("concepts", []):
        normalized_concept = " ".join(words(concept))
        if " " in normalized_concept and normalized_concept in normalized_query:
            score += 10
            matched.setdefault("concept_phrases", []).append(concept)
    return score, matched


def candidate_summary(fingerprint: dict[str, Any], max_words: int = 80) -> str:
    parts = [fingerprint["result"]]
    if fingerprint.get("unexpected"):
        parts.append(f"Discovery: {fingerprint['unexpected']}")
    elif fingerprint.get("friction"):
        parts.append(f"Friction: {fingerprint['friction']}")
    return truncate_words(" ".join(parts), max_words)


def search_index(index: dict[str, Any], query: str, limit: int = 6) -> list[dict[str, Any]]:
    ranked = []
    for fingerprint in index["fingerprints"]:
        score, matched = score_fingerprint(query, fingerprint)
        if score <= 0:
            continue
        ranked.append((score, fingerprint["task_id"], fingerprint, matched))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    results = []
    for score, _task_id, fingerprint, matched in ranked[:limit]:
        results.append({
            "task_id": fingerprint["task_id"],
            "title": fingerprint["title"],
            "project": fingerprint["project"],
            "workstream": fingerprint["workstream"],
            "status": fingerprint["status"],
            "score": score,
            "summary": candidate_summary(fingerprint),
            "matched_fields": matched,
            "source_refs": fingerprint["source_refs"][:3],
            "stale_or_broken": bool(fingerprint.get("broken_output_refs")),
        })
    return results


def render_query_section(query: dict[str, Any], results: list[dict[str, Any]]) -> tuple[str, int]:
    lines = [f"## {query['id']}", "", query["question"], ""]
    if not results:
        lines.extend(["No positive lexical match.", ""])
    for position, result in enumerate(results, 1):
        matched = "; ".join(
            f"{field}={','.join(values)}" for field, values in result["matched_fields"].items()
        )
        lines.extend([
            f"### {position}. {result['task_id']} — {result['title']}",
            "",
            f"- scope: {result['project']} / {result['workstream']} / {result['status']}",
            f"- lexical score: {result['score']}",
            f"- summary: {result['summary']}",
            f"- why matched: {matched or 'weak match'}",
            f"- source warning: {'some registered outputs are unresolved' if result['stale_or_broken'] else 'none'}",
            "- primary-source choices:",
            *[f"  - `{path}`" for path in result["source_refs"]],
            "",
        ])
    provisional = "\n".join(lines).rstrip() + "\n"
    estimated = estimate_tokens(provisional)
    lines.extend([f"- estimated discovery tokens for {query['id']}: {estimated}", ""])
    return "\n".join(lines).rstrip() + "\n", estimated


def render_helper_packet(spec: dict[str, Any], index: dict[str, Any]) -> tuple[str, dict[str, int]]:
    contract = spec["retrieval_contract"]
    lines = [
        "# TASK-256 Frozen Helper Retrieval Packet",
        "",
        "This packet is a generated, non-authoritative retrieval projection.",
        "Use only the candidates shown here. Do not search or inspect the repository.",
        "For each query, choose the most useful task fingerprint(s), then name no",
        f"more than {contract['max_primary_source_expansions']} primary sources you would open.",
        "Report confidence and ambiguity; `no strong match` is allowed.",
        "",
        f"- corpus fingerprints searched: {index['corpus_count']}",
        f"- maximum candidates per query: {contract['max_candidates_per_query']}",
        f"- per-query discovery ceiling: {contract['discovery_packet_max_estimated_tokens']} estimated tokens",
        f"- index watermark: {index['generated_at']}",
        "- truth set: withheld from helper",
        "",
    ]
    estimates: dict[str, int] = {}
    for query in spec["queries"]:
        results = search_index(index, query["question"], contract["max_candidates_per_query"])
        section, estimated = render_query_section(query, results)
        if estimated > contract["discovery_packet_max_estimated_tokens"]:
            raise ValueError(
                f"{query['id']} packet estimate {estimated} exceeds ceiling "
                f"{contract['discovery_packet_max_estimated_tokens']}"
            )
        estimates[query["id"]] = estimated
        lines.append(section.rstrip())
        lines.append("")
    lines.extend([
        "## Required response shape",
        "",
        "For each query: `Q# | selected TASK IDs | up to two source paths | confidence",
        "high/medium/low | concise rationale or no-strong-match`.",
        "Then report total queries answered, any ambiguity, and whether you used",
        "anything outside this packet.",
        "",
    ])
    return "\n".join(lines), estimates


def algorithm_metrics(spec: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    limit = spec["retrieval_contract"]["max_candidates_per_query"]
    total_expected = 0
    hits = 0
    per_query = []
    for query in spec["queries"]:
        results = search_index(index, query["question"], limit)
        returned = [item["task_id"] for item in results]
        expected = query["expected_task_ids"]
        found = [task_id for task_id in expected if task_id in returned]
        missing = [task_id for task_id in expected if task_id not in returned]
        total_expected += len(expected)
        hits += len(found)
        per_query.append({
            "id": query["id"],
            "expected": expected,
            "returned": returned,
            "found": found,
            "missing": missing,
        })
    return {
        "recall_at_6": round(hits / total_expected, 4) if total_expected else 0,
        "hits": hits,
        "total_expected": total_expected,
        "critical_miss_count": total_expected - hits,
        "per_query": per_query,
    }


def validate_expected_sources(spec: dict[str, Any], repo: Path = REPO) -> list[str]:
    broken = []
    for query in spec["queries"]:
        for raw in query["expected_source_paths"]:
            if not resolve_path(raw, repo).exists():
                broken.append(f"{query['id']}:{raw}")
    return broken


def generate(args: argparse.Namespace) -> int:
    spec = load_json(args.spec)
    broken_expected = validate_expected_sources(spec)
    if broken_expected:
        raise SystemExit(f"broken expected source paths: {broken_expected}")
    index = build_index(spec, args.tasks_dir, args.repo)
    packet, estimates = render_helper_packet(spec, index)
    index["pilot_metrics_before_helper"] = algorithm_metrics(spec, index)
    index["query_packet_estimated_tokens"] = estimates
    index["full_packet_estimated_tokens"] = estimate_tokens(packet)
    write_json(args.index, index)
    args.packet.parent.mkdir(parents=True, exist_ok=True)
    args.packet.write_text(packet, encoding="utf-8")
    print(json.dumps({
        "index": str(args.index),
        "packet": str(args.packet),
        "corpus_count": index["corpus_count"],
        "missing_task_ids": index["missing_task_ids"],
        "algorithm": index["pilot_metrics_before_helper"],
        "query_packet_estimated_tokens": estimates,
        "full_packet_estimated_tokens": index["full_packet_estimated_tokens"],
    }, indent=2))
    return 0


def search(args: argparse.Namespace) -> int:
    index = load_json(args.index)
    print(json.dumps(search_index(index, args.query, args.limit), indent=2))
    return 0


def score(args: argparse.Namespace) -> int:
    print(json.dumps(algorithm_metrics(load_json(args.spec), load_json(args.index)), indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    generate_cmd = sub.add_parser("generate")
    generate_cmd.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    generate_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    generate_cmd.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    generate_cmd.add_argument("--tasks-dir", type=Path, default=ROOT / "tasks")
    generate_cmd.add_argument("--repo", type=Path, default=REPO)
    generate_cmd.set_defaults(func=generate)

    search_cmd = sub.add_parser("search")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    search_cmd.add_argument("--limit", type=int, default=6)
    search_cmd.set_defaults(func=search)

    score_cmd = sub.add_parser("score")
    score_cmd.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    score_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    score_cmd.set_defaults(func=score)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
