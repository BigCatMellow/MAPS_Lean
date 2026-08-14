#!/usr/bin/env python3
"""TASK-258 source-level retrieval and compound-query holdout.

This remains a disposable, non-authoritative projection. It derives bounded
source descriptions from registered task outputs, retrieves with deterministic
lexical/fuzzy matching, and sends only compact packets to evaluators.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import html
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_holdout as typed  # noqa: E402
from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402


DEFAULT_SPEC = ROOT / "artifacts" / "experiments" / "task-fingerprint-source-holdout-queries-2026-07-19.json"
DEFAULT_INDEX = ROOT / "artifacts" / "experiments" / "task-fingerprint-source-holdout-2026-07-19.json"
DEFAULT_PACKET = ROOT / "artifacts" / "experiments" / "task-fingerprint-source-holdout-helper-packet-2026-07-19.md"
DEFAULT_PACKET_DIR = ROOT / "artifacts" / "experiments" / "task-fingerprint-source-holdout-packets-2026-07-19"
REGRESSION_SPEC = ROOT / "artifacts" / "experiments" / "task-fingerprint-holdout-queries-2026-07-19.json"
DEFAULT_REGRESSION = ROOT / "artifacts" / "experiments" / "task-fingerprint-source-regression-2026-07-19.json"

MAX_SOURCE_BYTES = 200_000
MAX_SOURCE_WORDS = 36
MAX_QUERY_PARTS = 4
ABSTAIN_MIN_SCORE = 24
ABSTAIN_MIN_COVERAGE = 0.20

TAG_RE = re.compile(r"<[^>]+>")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+?)\s*$")
HTML_TEXT_RE = re.compile(
    r"<(?:title|h[1-3]|button|label)[^>]*>(.*?)</(?:title|h[1-3]|button|label)>",
    re.IGNORECASE | re.DOTALL,
)
JS_NAME_RE = re.compile(
    r"\b(?:function|class)\s+([A-Za-z_$][\w$]*)|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=",
)


def identifier_text(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return re.sub(r"[_./:-]+", " ", value).strip()


def first_sentence(value: str) -> str:
    clean = " ".join(value.strip().split())
    if not clean:
        return ""
    match = re.search(r"(?<=[.!?])\s+", clean)
    return clean[: match.start()].strip() if match else clean


def bounded_text(parts: list[str], limit: int = MAX_SOURCE_WORDS) -> str:
    clean = " ".join(part.strip() for part in parts if part and part.strip())
    return base.truncate_words(" ".join(clean.split()), limit)


def markdown_description(text: str) -> str:
    headings: list[str] = []
    prose = ""
    in_fence = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line or line.startswith("<!--"):
            continue
        match = HEADING_RE.match(line)
        if match and len(headings) < 4:
            headings.append(match.group(1))
            continue
        if (
            not prose
            and not line.startswith(("- ", "* ", "|", ">"))
            and not re.match(r"^[a-z_ -]+:\s*", line, re.IGNORECASE)
        ):
            prose = first_sentence(line)
    return bounded_text(["; ".join(headings), prose])


def python_description(text: str) -> str:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return ""
    doc = first_sentence(ast.get_docstring(tree) or "")
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            rendered = identifier_text(node.name)
            if rendered and rendered not in names:
                names.append(rendered)
        if len(names) >= 18:
            break
    label = "symbols " + "; ".join(names) if names else ""
    return bounded_text([doc, label])


def json_description(text: str) -> str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return bounded_text([f"JSON {type(payload).__name__}"])
    parts = [
        str(payload.get("title") or payload.get("name") or ""),
        first_sentence(str(payload.get("description") or payload.get("summary") or "")),
    ]
    criteria = payload.get("acceptance_criteria")
    if isinstance(criteria, list):
        parts.append("; ".join(str(item) for item in criteria[:3]))
    parts.append("fields " + "; ".join(str(key) for key in list(payload)[:12]))
    return bounded_text(parts)


def html_description(text: str) -> str:
    values = []
    for raw in HTML_TEXT_RE.findall(text):
        clean = html.unescape(TAG_RE.sub(" ", raw))
        clean = " ".join(clean.split())
        if clean and clean not in values:
            values.append(clean)
        if len(values) >= 10:
            break
    return bounded_text(values)


def code_description(text: str) -> str:
    comments = [
        first_sentence(match.group(1))
        for match in re.finditer(r"(?:/\*+|//|#)\s*([^\n*]+)", text)
        if match.group(1).strip()
    ][:2]
    names = []
    for match in JS_NAME_RE.finditer(text):
        name = match.group(1) or match.group(2)
        rendered = identifier_text(name)
        if rendered and rendered not in names:
            names.append(rendered)
        if len(names) >= 14:
            break
    return bounded_text([*comments, "symbols " + "; ".join(names) if names else ""])


def structured_description(text: str) -> str:
    comments = [line.lstrip("# ").strip() for line in text.splitlines() if line.strip().startswith("#")]
    keys = []
    for line in text.splitlines():
        match = re.match(r"\s*[-]?\s*([A-Za-z0-9_.-]+):", line)
        if match and match.group(1) not in keys:
            keys.append(match.group(1))
        if len(keys) >= 16:
            break
    return bounded_text([*comments[:2], "fields " + "; ".join(keys) if keys else ""])


def source_description(path: Path, role: str) -> str:
    if path.is_dir():
        names = sorted(child.name for child in path.iterdir())[:16]
        return bounded_text([f"bundle {path.name}", "; ".join(identifier_text(name) for name in names)])
    if not path.is_file():
        return "unresolved registered source"
    text = path.read_text(encoding="utf-8", errors="replace")[:MAX_SOURCE_BYTES]
    suffix = path.suffix.lower()
    if suffix == ".py":
        description = python_description(text)
    elif suffix in {".md", ".rst", ".txt"}:
        description = markdown_description(text)
    elif suffix == ".json":
        description = json_description(text)
    elif suffix in {".html", ".htm"}:
        description = html_description(text)
    elif suffix in {".yaml", ".yml", ".toml"}:
        description = structured_description(text)
    elif suffix in {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".sh", ".lua"}:
        description = code_description(text)
    else:
        description = ""
    return description or bounded_text([role, identifier_text(path.name)])


def source_fingerprint(raw: str, repo: Path = REPO) -> dict[str, Any]:
    path = base.resolve_path(raw, repo)
    role = typed.evidence_role(raw, repo)
    exists = path.exists()
    return {
        "path": raw,
        "role": role,
        "description": source_description(path, role) if exists else "unresolved registered source",
        "exists": exists,
        "sha256": base.sha256(path) if path.is_file() else None,
        "derivation": "bounded_content_extract",
    }


def build_source_index(
    spec: dict[str, Any],
    tasks_dir: Path = ROOT / "tasks",
    repo: Path = REPO,
) -> dict[str, Any]:
    index = base.build_index(spec, tasks_dir, repo)
    for fingerprint in index["fingerprints"]:
        sources = [source_fingerprint(raw, repo) for raw in fingerprint["source_refs"]]
        fingerprint["source_fingerprints"] = sources
        fingerprint["source_digest"] = base.truncate_words(
            " ".join(source["description"] for source in sources),
            120,
        )
        fingerprint["curation"] = "deterministic_task_and_registered_source_extract"
    index.update({
        "schema_version": 2,
        "experiment": spec.get("experiment", "TASK-258"),
        "source_fingerprint_mode": "bounded deterministic extract; no owner semantic fields",
        "query_decomposition": "full query plus at most three connector/sentence parts",
    })
    return index


def edit_distance_at_most_one(left: str, right: str) -> bool:
    if left == right:
        return True
    if abs(len(left) - len(right)) > 1:
        return False
    if len(left) > len(right):
        left, right = right, left
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right)) <= 1
    index_left = index_right = differences = 0
    while index_left < len(left) and index_right < len(right):
        if left[index_left] == right[index_right]:
            index_left += 1
            index_right += 1
            continue
        differences += 1
        index_right += 1
        if differences > 1:
            return False
    return True


def lexical_matches(query: str, text: str) -> tuple[list[str], list[str]]:
    query_tokens = set(base.words(query))
    text_tokens = set(base.words(text))
    exact = sorted(query_tokens.intersection(text_tokens))
    unmatched_query = query_tokens.difference(exact)
    unmatched_text = text_tokens.difference(exact)
    fuzzy = []
    for query_token in sorted(unmatched_query):
        if len(query_token) < 4 or query_token.isdigit():
            continue
        for text_token in unmatched_text:
            if len(text_token) >= 4 and edit_distance_at_most_one(query_token, text_token):
                fuzzy.append(f"{query_token}~{text_token}")
                break
    return exact, fuzzy


def query_parts(query: str) -> list[str]:
    candidates = [query.strip()]
    candidate_keys = {" ".join(base.words(query))}
    sentence_parts = re.split(r"(?<=[.!?;])\s+", query)
    connector_parts = re.split(r"\s+(?:or|versus|whereas|while)\s+|\s*;\s*", query, flags=re.IGNORECASE)
    # Connector splits carry the two sides of a compound question. Preserve
    # them before generic sentence fragments consume the bounded part budget.
    for part in [*connector_parts, *sentence_parts]:
        clean = part.strip(" ,.;:?!")
        key = " ".join(base.words(clean))
        if len(base.words(clean)) >= 3 and key not in candidate_keys:
            candidates.append(clean)
            candidate_keys.add(key)
        if len(candidates) >= MAX_QUERY_PARTS:
            break
    return candidates


def source_match_score(query: str, source: dict[str, Any]) -> tuple[int, dict[str, list[str]]]:
    description_exact, description_fuzzy = lexical_matches(query, source["description"])
    path_exact, path_fuzzy = lexical_matches(query, identifier_text(source["path"]))
    role_bonus = typed.query_role_weights(query).get(source["role"], 0)
    score = (
        len(description_exact) * 7
        + len(description_fuzzy) * 2
        + len(path_exact) * 5
        + len(path_fuzzy)
        + typed.ROLE_BASE.get(source["role"], 0)
        + max(0, role_bonus // 2)
    )
    matched = {}
    if description_exact:
        matched["description"] = description_exact
    if description_fuzzy:
        matched["fuzzy"] = description_fuzzy
    if path_exact:
        matched["path"] = path_exact
    return score, matched


def score_task_part(query: str, fingerprint: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    task_score, task_matched = base.score_fingerprint(query, fingerprint)
    source_scores = []
    for source in fingerprint["source_fingerprints"]:
        score, matched = source_match_score(query, source)
        if score:
            source_scores.append((score, source["path"], matched))
    source_scores.sort(key=lambda item: (-item[0], item[1]))
    top_source_scores = [item[0] for item in source_scores[:3]]
    combined = task_score + sum(top_source_scores)
    return combined, {
        "task": task_matched,
        "sources": [
            {"path": path, "score": score, "matched": matched}
            for score, path, matched in source_scores[:3]
        ],
    }


def score_task(query: str, fingerprint: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    parts = query_parts(query)
    scored = []
    for part in parts:
        score, matched = score_task_part(part, fingerprint)
        scored.append((score, part, matched))
    scored.sort(key=lambda item: -item[0])
    aggregate = scored[0][0] if scored else 0
    aggregate += math.floor(sum(item[0] for item in scored[1:]) * 0.35)
    return aggregate, {
        "parts": [
            {"query": part, "score": score, "matched": matched}
            for score, part, matched in scored
            if score > 0
        ],
    }


ROLE_GROUP = {
    "task_scope": "scope",
    "decision": "scope",
    "current_state": "scope",
    "implementation": "implementation",
    "guide": "implementation",
    "test": "verification",
    "review": "verification",
    "release": "verification",
    "outcome": "verification",
    "research": "verification",
    "artifact": "verification",
    "bundle": "other",
}


def diverse_sources(fingerprint: dict[str, Any], query: str, limit: int = 2) -> list[dict[str, Any]]:
    ranked = []
    for source in fingerprint["source_fingerprints"]:
        score, matched = source_match_score(query, source)
        ranked.append((score, source["path"], source, matched))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    query_tokens = set(base.words(query))
    explicit_task_scope = bool(re.search(
        r"\b(?:which|what)\s+(?:task\s+)?record\b|\bwho\s+owns\b|"
        r"\btask\s+status\b|\bdeclared\s+scope\b",
        query,
        re.IGNORECASE,
    ))
    policy_scope = bool(
        query_tokens.intersection({"authority", "decision", "policy", "posture"})
        or re.search(r"\bcurrent\s+(?:state|posture|policy|configuration)\b", query, re.IGNORECASE)
    )
    wants_guide = bool(query_tokens.intersection({"guide", "procedure", "protocol", "runbook"}))
    if explicit_task_scope:
        group_order = ["scope", "implementation", "verification"]
    elif policy_scope:
        group_order = ["scope", "verification", "implementation"]
    else:
        # The candidate heading already tells the evaluator which task it is.
        # Behavioral questions benefit more from executable and verifying
        # evidence than from repeating the task record in a scarce source slot.
        group_order = ["implementation", "verification", "scope"]

    selected = []
    groups = set()
    for wanted_group in group_order:
        choices = [item for item in ranked if ROLE_GROUP[item[2]["role"]] == wanted_group]
        if wanted_group == "implementation" and not wants_guide:
            executable = [item for item in choices if item[2]["role"] == "implementation"]
            choices = executable or choices
        if policy_scope and wanted_group == "scope" and not explicit_task_scope:
            non_task_scope = [item for item in choices if item[2]["role"] != "task_scope"]
            choices = non_task_scope or choices
        if not choices:
            continue
        score, _path, source, matched = choices[0]
        selected.append({
            **source,
            "score": score,
            "matched": matched,
            "proof": typed.ROLE_PROOF[source["role"]],
        })
        groups.add(wanted_group)
        if len(selected) == limit:
            break
    if len(selected) < limit:
        selected_paths = {source["path"] for source in selected}
        for score, _path, source, matched in ranked:
            if source["path"] in selected_paths:
                continue
            selected.append({
                **source,
                "score": score,
                "matched": matched,
                "proof": typed.ROLE_PROOF[source["role"]],
            })
            if len(selected) == limit:
                break
    return selected


def matched_query_tokens(query: str, matched: dict[str, Any]) -> set[str]:
    tokens = set()
    for part in matched.get("parts", []):
        for values in part["matched"]["task"].values():
            tokens.update(values)
        for source in part["matched"]["sources"]:
            tokens.update(source["matched"].get("description", []))
            tokens.update(source["matched"].get("path", []))
    return tokens.intersection(base.words(query))


def assess_strength(query: str, score: int, matched: dict[str, Any]) -> dict[str, Any]:
    query_tokens = set(base.words(query))
    hit_tokens = matched_query_tokens(query, matched)
    coverage = len(hit_tokens) / len(query_tokens) if query_tokens else 0
    strong = score >= ABSTAIN_MIN_SCORE and coverage >= ABSTAIN_MIN_COVERAGE
    return {
        "recommendation": "candidate_set" if strong else "no_strong_match",
        "top_score": score,
        "query_coverage": round(coverage, 4),
        "threshold": {"min_score": ABSTAIN_MIN_SCORE, "min_coverage": ABSTAIN_MIN_COVERAGE},
    }


def search_index(
    index: dict[str, Any],
    query: str,
    *,
    task_limit: int = 6,
    source_limit: int = 2,
) -> dict[str, Any]:
    ranked = []
    for fingerprint in index["fingerprints"]:
        score, matched = score_task(query, fingerprint)
        if score > 0:
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
            "summary": base.truncate_words(fingerprint["goal"], 24),
            "matched": matched,
            "source_choices": diverse_sources(fingerprint, query, source_limit),
            "source_warning": bool(fingerprint.get("broken_output_refs")),
        })
    strength = assess_strength(query, results[0]["task_score"], results[0]["matched"]) if results else {
        "recommendation": "no_strong_match",
        "top_score": 0,
        "query_coverage": 0,
        "threshold": {"min_score": ABSTAIN_MIN_SCORE, "min_coverage": ABSTAIN_MIN_COVERAGE},
    }
    return {"query_parts": query_parts(query), "strength": strength, "candidates": results}


def validate_spec(
    spec: dict[str, Any],
    tasks_dir: Path = ROOT / "tasks",
    repo: Path = REPO,
) -> list[str]:
    findings = []
    corpus = set(spec.get("corpus_task_ids", []))
    queries = spec.get("queries", [])
    if len(queries) < 8:
        findings.append(f"expected at least 8 queries, found {len(queries)}")
    if not any(not query.get("expected_task_ids") for query in queries):
        findings.append("holdout must include at least one no-match query")
    for query in queries:
        expected_tasks = query.get("expected_task_ids", [])
        expected_sources = query.get("expected_source_paths", [])
        if not expected_tasks and expected_sources:
            findings.append(f"{query.get('id')}: no-match query cannot have expected sources")
        registered = set()
        for task_id in expected_tasks:
            if task_id not in corpus:
                findings.append(f"{query.get('id')}: expected task outside corpus: {task_id}")
                continue
            task_path = tasks_dir / f"{task_id}.json"
            if not task_path.exists():
                findings.append(f"{query.get('id')}: missing task file: {task_id}")
                continue
            task = base.load_json(task_path)
            registered.add(f"MAP_System/tasks/{task_id}.json")
            registered.update(task.get("output_paths", []))
        for raw in expected_sources:
            if raw not in registered:
                findings.append(f"{query.get('id')}: source not registered by expected task: {raw}")
            if not base.resolve_path(raw, repo).exists():
                findings.append(f"{query.get('id')}: missing source path: {raw}")
    return findings


def algorithm_metrics(spec: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    task_hits = task_total = source_hits = source_total = 0
    abstention_hits = 0
    per_query = []
    contract = spec.get("retrieval_contract", {})
    task_limit = contract.get("max_candidates_per_query", 6)
    source_limit = contract.get("max_sources_per_candidate", 2)
    for query in spec["queries"]:
        search = search_index(index, query["question"], task_limit=task_limit, source_limit=source_limit)
        returned_tasks = [item["task_id"] for item in search["candidates"]]
        expected_tasks = query.get("expected_task_ids", [])
        found_tasks = [task_id for task_id in expected_tasks if task_id in returned_tasks]
        expected_sources = query.get("expected_source_paths", [])
        source_map = {item["task_id"]: item["source_choices"] for item in search["candidates"]}
        visible = {
            source["path"]
            for task_id in expected_tasks
            for source in source_map.get(task_id, [])
        }
        found_sources = [path for path in expected_sources if path in visible]
        expected_abstention = not expected_tasks
        actual_abstention = search["strength"]["recommendation"] == "no_strong_match"
        abstention_hits += int(expected_abstention == actual_abstention)
        task_hits += len(found_tasks)
        task_total += len(expected_tasks)
        source_hits += len(found_sources)
        source_total += len(expected_sources)
        per_query.append({
            "id": query["id"],
            "expected_tasks": expected_tasks,
            "returned_tasks": returned_tasks,
            "missing_tasks": [task_id for task_id in expected_tasks if task_id not in returned_tasks],
            "expected_sources": expected_sources,
            "visible_expected_sources": found_sources,
            "hidden_expected_sources": [path for path in expected_sources if path not in visible],
            "expected_abstention": expected_abstention,
            "algorithm_recommendation": search["strength"]["recommendation"],
            "top_score": search["strength"]["top_score"],
            "query_coverage": search["strength"]["query_coverage"],
            "query_parts": search["query_parts"],
        })
    return {
        "task_recall_at_6": round(task_hits / task_total, 4) if task_total else None,
        "task_hits": task_hits,
        "total_expected_tasks": task_total,
        "critical_task_misses": task_total - task_hits,
        "expected_source_visibility": round(source_hits / source_total, 4) if source_total else None,
        "visible_expected_sources": source_hits,
        "total_expected_sources": source_total,
        "abstention_accuracy": round(abstention_hits / len(spec["queries"]), 4),
        "abstention_hits": abstention_hits,
        "total_queries": len(spec["queries"]),
        "per_query": per_query,
    }


def render_query_packet(
    query: dict[str, Any],
    search: dict[str, Any],
    *,
    corpus_count: int,
    ceiling: int,
    watermark: str,
) -> tuple[str, int]:
    strength = search["strength"]
    lines = [
        f"# TASK-258 Holdout Packet — {query['id']}",
        "",
        "Generated retrieval aid; not authority. Use only this packet.",
        f"- corpus: {corpus_count} deterministic task/source fingerprints",
        f"- decomposed into: {' | '.join(search['query_parts'])}",
        f"- algorithm signal: {strength['recommendation']} "
        f"(score {strength['top_score']}, coverage {strength['query_coverage']:.0%})",
        f"- watermark: {watermark}",
        "- truth: withheld; no strong match is a valid answer",
        "",
        "## Query",
        "",
        query["question"],
        "",
        "## Candidates",
        "",
    ]
    for position, result in enumerate(search["candidates"], 1):
        lines.extend([
            f"### {position}. {result['task_id']} — {result['title']}",
            f"- {result['project']} / {result['workstream']} / {result['status']}; score {result['task_score']}",
            f"- scope: {result['summary']}",
            f"- path warning: {'registered output gap' if result['source_warning'] else 'none'}",
            "- diverse evidence:",
        ])
        for source in result["source_choices"]:
            lines.append(
                f"  - `{source['path']}` [{source['role']}] — "
                f"{base.truncate_words(source['description'], 18)}"
            )
        lines.append("")
    lines.extend([
        "## Required response",
        "",
        "Return: `query ID | selected TASK IDs or NO STRONG MATCH | up to two",
        "source paths | confidence high/medium/low | concise rationale`.",
        "State ambiguity and whether anything outside this packet was accessed.",
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
) -> tuple[str, dict[str, int]]:
    contract = spec["retrieval_contract"]
    packet_dir.mkdir(parents=True, exist_ok=True)
    sections = [
        "# TASK-258 Combined Holdout Packets",
        "",
        "Audit copy only. Evaluator receives one packet at a time.",
        "",
    ]
    estimates = {}
    for query in spec["queries"]:
        search = search_index(
            index,
            query["question"],
            task_limit=contract["max_candidates_per_query"],
            source_limit=contract["max_sources_per_candidate"],
        )
        packet, estimate = render_query_packet(
            query,
            search,
            corpus_count=index["corpus_count"],
            ceiling=contract["discovery_packet_max_estimated_tokens"],
            watermark=index["generated_at"],
        )
        (packet_dir / f"{query['id']}.md").write_text(packet, encoding="utf-8")
        estimates[query["id"]] = estimate
        sections.extend([packet.rstrip(), "", "---", ""])
    return "\n".join(sections).rstrip() + "\n", estimates


def run_regression(args: argparse.Namespace) -> int:
    spec = base.load_json(args.spec)
    index = build_source_index(spec, args.tasks_dir, args.repo)
    payload = {
        "experiment": "TASK-258-development-regression",
        "truth_provenance": "known TASK-257 truth; not holdout evidence",
        "implementation_frozen_before_new_truth": True,
        "source_spec": base.display_path(args.spec, str(args.spec), args.repo),
        "metrics": algorithm_metrics(spec, index),
        "corpus_count": index["corpus_count"],
        "source_fingerprint_count": sum(len(item["source_fingerprints"]) for item in index["fingerprints"]),
    }
    base.write_json(args.output, payload)
    print(json.dumps(payload, indent=2))
    return 0


def generate(args: argparse.Namespace) -> int:
    spec = base.load_json(args.spec)
    findings = validate_spec(spec, args.tasks_dir, args.repo)
    if findings:
        raise SystemExit("invalid holdout spec:\n- " + "\n- ".join(findings))
    index = build_source_index(spec, args.tasks_dir, args.repo)
    index["source_spec"] = base.display_path(args.spec, str(args.spec), args.repo)
    combined, estimates = render_packets(spec, index, args.packet_dir)
    index["metrics_before_helper"] = algorithm_metrics(spec, index)
    index["query_packet_estimated_tokens"] = estimates
    index["combined_packet_estimated_tokens"] = base.estimate_tokens(combined)
    index["source_fingerprint_count"] = sum(
        len(item["source_fingerprints"]) for item in index["fingerprints"]
    )
    base.write_json(args.index, index)
    args.packet.parent.mkdir(parents=True, exist_ok=True)
    args.packet.write_text(combined, encoding="utf-8")
    print(json.dumps({
        "index": str(args.index),
        "packet": str(args.packet),
        "packet_dir": str(args.packet_dir),
        "corpus_count": index["corpus_count"],
        "source_fingerprint_count": index["source_fingerprint_count"],
        "metrics": index["metrics_before_helper"],
        "packet_estimates": estimates,
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    regression = sub.add_parser("regression")
    regression.add_argument("--spec", type=Path, default=REGRESSION_SPEC)
    regression.add_argument("--output", type=Path, default=DEFAULT_REGRESSION)
    regression.add_argument("--tasks-dir", type=Path, default=ROOT / "tasks")
    regression.add_argument("--repo", type=Path, default=REPO)
    regression.set_defaults(func=run_regression)

    generate_cmd = sub.add_parser("generate")
    generate_cmd.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    generate_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    generate_cmd.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    generate_cmd.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    generate_cmd.add_argument("--tasks-dir", type=Path, default=ROOT / "tasks")
    generate_cmd.add_argument("--repo", type=Path, default=REPO)
    generate_cmd.set_defaults(func=generate)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
