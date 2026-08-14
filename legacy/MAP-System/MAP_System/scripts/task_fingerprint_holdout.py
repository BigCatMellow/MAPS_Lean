#!/usr/bin/env python3
"""TASK-257 uncurated holdout with query-aware evidence-role ranking.

The task fingerprint remains a disposable projection. This experiment adds a
second ranking stage for sources: first retrieve likely tasks, then rank each
task's registered evidence by what the query needs to prove.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402


DEFAULT_SPEC = ROOT / "artifacts" / "experiments" / "task-fingerprint-holdout-queries-2026-07-19.json"
DEFAULT_INDEX = ROOT / "artifacts" / "experiments" / "task-fingerprint-holdout-2026-07-19.json"
DEFAULT_PACKET = ROOT / "artifacts" / "experiments" / "task-fingerprint-holdout-helper-packet-2026-07-19.md"
DEFAULT_PACKET_DIR = ROOT / "artifacts" / "experiments" / "task-fingerprint-holdout-packets-2026-07-19"


ROLE_PROOF = {
    "task_scope": "declared intent, scope, status, ownership, and registered outputs",
    "test": "executed checks, regression behavior, parity, or validation evidence",
    "review": "independent findings, verdict, and acceptance assessment",
    "release": "release closeout and shipped-state checklist",
    "decision": "approved decision, authority, or governing boundary",
    "current_state": "current project/system posture at its verification watermark",
    "outcome": "measured result, cost/yield, later use, or operational effect",
    "research": "sourced analysis or comparative evidence",
    "guide": "documented procedure, protocol, or operating convention",
    "implementation": "implementation behavior and executable mechanism",
    "artifact": "task-specific analysis, plan, audit, or experiment evidence",
    "bundle": "collection of implementation or evidence files; inspect a specific member",
}


def evidence_role(raw: str, repo: Path = REPO) -> str:
    lower = raw.lower()
    name = Path(raw).name.lower()
    resolved = base.resolve_path(raw, repo)
    if "/tasks/" in lower and name.startswith("task-") and name.endswith(".json"):
        return "task_scope"
    if "/notes/" in lower or "guide" in name or "protocol" in name:
        return "guide"
    if "/tests/" in lower or name.startswith("test_"):
        return "test"
    if "/artifacts/reviews/" in lower or "review" in name:
        return "review"
    if "/artifacts/releases/" in lower or "release-checklist" in name:
        return "release"
    if "decisions" in name or "/decisions/" in lower:
        return "decision"
    if "current-state" in name or name == "runtime_policy.yaml":
        return "current_state"
    if (
        "/scripts/" in lower
        or "/db/" in lower
        or "/app/" in lower
        or "/src/" in lower
        or resolved.suffix.lower() in {".py", ".js", ".mjs", ".ts", ".html", ".css", ".sh", ".lua"}
    ):
        return "implementation"
    if any(term in lower for term in ("outcome", "cost-yield", "cost_yield", "metrics")):
        return "outcome"
    if "/artifacts/research/" in lower or "research" in name or "summary-" in name:
        return "research"
    if (
        "/artifacts/tests/" in lower
        or "/tests/" in lower
        or name.startswith("test_")
        or any(term in name for term in ("parity", "regression", "smoke", "drill", "evidence", "verification"))
    ):
        return "test"
    if resolved.is_dir():
        return "bundle"
    if "/artifacts/" in lower or resolved.suffix.lower() in {".md", ".json", ".yaml", ".yml"}:
        return "artifact"
    return "artifact"


def query_role_weights(query: str) -> dict[str, int]:
    tokens = set(base.words(query))
    weights: dict[str, int] = defaultdict(int)

    def apply(trigger_words: set[str], role_weights: dict[str, int]) -> None:
        if tokens.intersection(trigger_words):
            for role, value in role_weights.items():
                weights[role] += value

    apply(
        {"prove", "proof", "verify", "verified", "evidence", "test", "tests", "regression", "parity", "validate", "validation", "check", "drill", "robustness"},
        {"test": 16, "review": 8, "artifact": 6, "task_scope": -2},
    )
    apply(
        {"review", "reviewer", "finding", "findings", "verdict", "acceptance", "rejected", "approved"},
        {"review": 16, "test": 5, "task_scope": 2},
    )
    apply(
        {"decision", "decide", "authority", "permission", "policy", "rule", "boundary", "govern", "conflict"},
        {"decision": 16, "guide": 10, "current_state": 6, "task_scope": 2},
    )
    apply(
        {"implement", "implementation", "code", "script", "function", "runtime", "mechanism", "fix", "behavior", "build"},
        {"implementation": 14, "test": 6, "artifact": 3},
    )
    apply(
        {"release", "released", "ship", "shipped", "closeout", "deployed"},
        {"release": 16, "test": 6, "review": 5},
    )
    apply(
        {"outcome", "result", "worked", "failed", "cost", "yield", "metric", "measured", "effect", "later"},
        {"outcome": 16, "artifact": 7, "research": 5, "test": 4},
    )
    apply(
        {"research", "compare", "comparison", "study", "source", "external"},
        {"research": 16, "artifact": 5},
    )
    apply(
        {"guide", "procedure", "protocol", "runbook", "how", "workflow"},
        {"guide": 16, "decision": 5},
    )
    apply(
        {"current", "now", "posture", "state", "remaining"},
        {"current_state": 14, "task_scope": 3},
    )
    apply(
        {"which", "record", "task", "scope", "owner", "status", "intended"},
        {"task_scope": 9},
    )
    return dict(weights)


ROLE_BASE = {
    "test": 8,
    "review": 7,
    "decision": 7,
    "outcome": 7,
    "release": 6,
    "research": 6,
    "current_state": 6,
    "guide": 5,
    "artifact": 5,
    "implementation": 4,
    "task_scope": 3,
    "bundle": 0,
}


def rank_sources(
    fingerprint: dict[str, Any],
    query: str,
    *,
    limit: int = 3,
    repo: Path = REPO,
) -> list[dict[str, Any]]:
    query_tokens = set(base.words(query))
    role_weights = query_role_weights(query)
    ranked = []
    for raw in fingerprint.get("source_refs", []):
        role = evidence_role(raw, repo)
        path_tokens = set(base.words(raw.replace("_", " ").replace("/", " ").replace("-", " ")))
        overlap = sorted(query_tokens.intersection(path_tokens))
        score = ROLE_BASE.get(role, 0) + role_weights.get(role, 0) + len(overlap) * 5
        ranked.append((score, -len(raw), raw, role, overlap))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [
        {
            "path": raw,
            "role": role,
            "proves": ROLE_PROOF[role],
            "score": score,
            "matched_path_terms": overlap,
        }
        for score, _negative_length, raw, role, overlap in ranked[:limit]
    ]


def search_index(
    index: dict[str, Any],
    query: str,
    *,
    task_limit: int = 6,
    source_limit: int = 3,
    repo: Path = REPO,
) -> list[dict[str, Any]]:
    ranked = []
    for fingerprint in index["fingerprints"]:
        score, matched = base.score_fingerprint(query, fingerprint)
        if score <= 0:
            continue
        ranked.append((score, fingerprint["task_id"], fingerprint, matched))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    results = []
    for score, _task_id, fingerprint, matched in ranked[:task_limit]:
        results.append({
            "task_id": fingerprint["task_id"],
            "title": fingerprint["title"],
            "status": fingerprint["status"],
            "project": fingerprint["project"],
            "workstream": fingerprint["workstream"],
            "task_score": score,
            "summary": base.candidate_summary(fingerprint, max_words=30),
            "matched_fields": matched,
            "source_choices": rank_sources(fingerprint, query, limit=source_limit, repo=repo),
            "source_warning": bool(fingerprint.get("broken_output_refs")),
        })
    return results


def validate_spec(spec: dict[str, Any], tasks_dir: Path = ROOT / "tasks", repo: Path = REPO) -> list[str]:
    findings = []
    corpus = set(spec.get("corpus_task_ids", []))
    queries = spec.get("queries", [])
    if len(queries) != 8:
        findings.append(f"expected 8 queries, found {len(queries)}")
    for query in queries:
        for task_id in query.get("expected_task_ids", []):
            if task_id not in corpus:
                findings.append(f"{query.get('id')}: expected task outside corpus: {task_id}")
        registered = set()
        for task_id in query.get("expected_task_ids", []):
            task_path = tasks_dir / f"{task_id}.json"
            if not task_path.exists():
                findings.append(f"{query.get('id')}: missing task file: {task_id}")
                continue
            task = base.load_json(task_path)
            registered.add(f"MAP_System/tasks/{task_id}.json")
            registered.update(task.get("output_paths", []))
        for raw in query.get("expected_source_paths", []):
            if not base.resolve_path(raw, repo).exists():
                findings.append(f"{query.get('id')}: missing source path: {raw}")
            if raw not in registered:
                findings.append(f"{query.get('id')}: source not registered by expected task: {raw}")
    return findings


def algorithm_metrics(spec: dict[str, Any], index: dict[str, Any], repo: Path = REPO) -> dict[str, Any]:
    total_tasks = task_hits = total_sources = source_hits = 0
    per_query = []
    for query in spec["queries"]:
        results = search_index(index, query["question"], repo=repo)
        returned_tasks = [result["task_id"] for result in results]
        expected_tasks = query["expected_task_ids"]
        found_tasks = [task_id for task_id in expected_tasks if task_id in returned_tasks]
        source_map = {result["task_id"]: result["source_choices"] for result in results}
        visible_sources = {
            choice["path"]
            for task_id in expected_tasks
            for choice in source_map.get(task_id, [])
        }
        expected_sources = query["expected_source_paths"]
        found_sources = [path for path in expected_sources if path in visible_sources]
        total_tasks += len(expected_tasks)
        task_hits += len(found_tasks)
        total_sources += len(expected_sources)
        source_hits += len(found_sources)
        per_query.append({
            "id": query["id"],
            "expected_tasks": expected_tasks,
            "returned_tasks": returned_tasks,
            "missing_tasks": [task_id for task_id in expected_tasks if task_id not in returned_tasks],
            "expected_sources": expected_sources,
            "visible_expected_sources": found_sources,
            "hidden_expected_sources": [path for path in expected_sources if path not in visible_sources],
        })
    return {
        "task_recall_at_6": round(task_hits / total_tasks, 4) if total_tasks else 0,
        "task_hits": task_hits,
        "total_expected_tasks": total_tasks,
        "critical_task_misses": total_tasks - task_hits,
        "expected_source_visibility": round(source_hits / total_sources, 4) if total_sources else 0,
        "visible_expected_sources": source_hits,
        "total_expected_sources": total_sources,
        "per_query": per_query,
    }


def render_query_packet(
    query: dict[str, Any],
    results: list[dict[str, Any]],
    *,
    corpus_count: int,
    ceiling: int,
    watermark: str,
) -> tuple[str, int]:
    lines = [
        f"# TASK-257 Holdout Packet — {query['id']}",
        "",
        "Generated retrieval projection; not authority.",
        "Use only this packet. Do not search or open named sources.",
        "",
        f"- corpus searched: {corpus_count} deterministic uncurated fingerprints",
        "- truth set: withheld",
        f"- discovery ceiling: {ceiling} estimated tokens",
        f"- watermark: {watermark}",
        "",
        "## Query",
        "",
        query["question"],
        "",
        "## Candidates",
        "",
    ]
    for position, result in enumerate(results, 1):
        matched = "; ".join(
            f"{field}={','.join(values)}" for field, values in result["matched_fields"].items()
        )
        lines.extend([
            f"### {position}. {result['task_id']} — {result['title']}",
            "",
            f"- scope: {result['project']} / {result['workstream']} / {result['status']}",
            f"- task score: {result['task_score']}",
            f"- summary: {result['summary']}",
            f"- match: {matched or 'weak lexical match'}",
            f"- source warning: {'registered output gap' if result['source_warning'] else 'none'}",
            "- ranked evidence choices:",
        ])
        for choice in result["source_choices"]:
            lines.append(
                f"  - `{choice['path']}` — {choice['role']}; can prove {choice['proves']}"
            )
        lines.append("")
    lines.extend([
        "## Required response",
        "",
        "Return: `query ID | selected TASK IDs | up to two selected source paths |",
        "confidence high/medium/low | concise rationale or no strong match`.",
        "Also state ambiguity and whether anything outside this packet was accessed.",
        "",
    ])
    text = "\n".join(lines)
    estimate = base.estimate_tokens(text)
    if estimate > ceiling:
        raise ValueError(f"{query['id']} packet estimate {estimate} exceeds ceiling {ceiling}")
    text += f"- estimated packet tokens: {estimate}\n"
    return text, estimate


def render_packets(
    spec: dict[str, Any],
    index: dict[str, Any],
    packet_dir: Path,
    repo: Path = REPO,
) -> tuple[str, dict[str, int]]:
    contract = spec["retrieval_contract"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    sections = [
        "# TASK-257 Combined Holdout Packets",
        "",
        "Audit copy only. The evaluator receives one query file at a time.",
        "",
    ]
    estimates = {}
    for query in spec["queries"]:
        results = search_index(
            index,
            query["question"],
            task_limit=contract["max_candidates_per_query"],
            source_limit=contract["max_sources_per_candidate"],
            repo=repo,
        )
        packet, estimate = render_query_packet(
            query,
            results,
            corpus_count=index["corpus_count"],
            ceiling=contract["discovery_packet_max_estimated_tokens"],
            watermark=index["generated_at"],
        )
        path = packet_dir / f"{query['id']}.md"
        path.write_text(packet, encoding="utf-8")
        estimates[query["id"]] = estimate
        sections.extend([packet.rstrip(), "", "---", ""])
    return "\n".join(sections).rstrip() + "\n", estimates


def generate(args: argparse.Namespace) -> int:
    spec = base.load_json(args.spec)
    findings = validate_spec(spec, args.tasks_dir, args.repo)
    if findings:
        raise SystemExit("invalid holdout spec:\n- " + "\n- ".join(findings))
    index = base.build_index(spec, args.tasks_dir, args.repo)
    index["source_spec"] = base.display_path(args.spec, str(args.spec), args.repo)
    index["fingerprint_mode"] = "deterministic_task_record_only; no semantic curation"
    if any(item["curation"] != "deterministic_task_record" for item in index["fingerprints"]):
        raise SystemExit("holdout contains curated fingerprints")
    combined, estimates = render_packets(spec, index, args.packet_dir, args.repo)
    index["pilot_metrics_before_helper"] = algorithm_metrics(spec, index, args.repo)
    index["query_packet_estimated_tokens"] = estimates
    index["combined_packet_estimated_tokens"] = base.estimate_tokens(combined)
    base.write_json(args.index, index)
    args.packet.parent.mkdir(parents=True, exist_ok=True)
    args.packet.write_text(combined, encoding="utf-8")
    print(json.dumps({
        "index": str(args.index),
        "packet": str(args.packet),
        "packet_dir": str(args.packet_dir),
        "corpus_count": index["corpus_count"],
        "missing_task_ids": index["missing_task_ids"],
        "metrics": index["pilot_metrics_before_helper"],
        "packet_estimates": estimates,
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("generate")
    command.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    command.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    command.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    command.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    command.add_argument("--tasks-dir", type=Path, default=ROOT / "tasks")
    command.add_argument("--repo", type=Path, default=REPO)
    command.set_defaults(func=generate)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
