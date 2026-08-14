#!/usr/bin/env python3
"""Disposable claim-evidence retrieval pilot for TASK-263 / EXP-0006.

Builds one "claim card" per (originating task, exact anchor) pair from
completed MAP tasks' registered output paths, rather than attributing an
entire shared file to every task that ever touched it. Each card carries an
exact code-symbol or Markdown-heading anchor, a build-time source hash (drift
fingerprint only, never claimed as historical proof), and a release-event
time watermark. Retrieval is a from-scratch lexical/TF-IDF scorer over these
cards; it never reads the frozen holdout answers and never modifies the
frozen retriever/selector/capsule scripts it imports for shared utilities.

This is experiment evidence only (EXP-0006 / TASK-263). It confers no
production authority and must not be wired into startup, routing, or
canonical retrieval.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_holdout as typed  # noqa: E402
from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402

DEFAULT_HOLDOUT = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-claim-evidence-holdout-2026-07-19.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-claim-evidence-development-2026-07-19.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-claim-evidence-development-2026-07-19.md"
)
DEFAULT_EVENTS = ROOT / "events" / "events.jsonl"
TASKS_DIR = ROOT / "tasks"

HOLDOUT_EXPECTED_SHA256 = (
    "635aa5f0b41bdded414fac6b6a7cf82cb2841395751813ad6213619eb0f75e3f"
)

TASK_TAG_RE = re.compile(r"TASK-(\d{3,4})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

ENABLE_WORDS = {
    "allow", "allowed", "allows", "allowing", "enable", "enabled", "enables",
    "permit", "permitted", "permits", "can",
}
BLOCK_WORDS = {
    "prevent", "prevents", "prevented", "block", "blocks", "blocked",
    "forbid", "forbids", "reject", "rejects", "rejected", "disallow",
    "disallows", "prohibit", "prohibits", "stop", "stops", "stopped",
    "must not", "cannot",
}

SOURCE_BUDGET = 3
# Calibrated on general design reasoning (near-miss token overlap on 1-2
# common words should not clear this), never on the frozen holdout's own
# query/answer pairs.
MIN_TASK_SCORE = 6.0
# A near-miss (topically adjacent but capability-absent) match tends to share
# only a couple of common query words; a genuine match tends to share a
# larger fraction of the query's content words across the two channels.
MIN_COVERAGE_RATIO = 0.3


def load_json(path: Path) -> Any:
    return base.load_json(path)


def write_json(path: Path, payload: Any) -> None:
    base.write_json(path, payload)


def normalize_path(raw: str) -> str:
    resolved = base.resolve_path(raw, REPO)
    try:
        return str(resolved.relative_to(REPO))
    except ValueError:
        return raw


def read_events_watermarks(events_path: Path) -> dict[str, str]:
    """Earliest SUBMISSION/APPROVED event timestamp per task_id."""
    watermarks: dict[str, str] = {}
    if not events_path.is_file():
        return watermarks
    with events_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") not in {"SUBMISSION", "APPROVED"}:
                continue
            task_id = event.get("task_id")
            created_at = event.get("created_at")
            if not task_id or not created_at:
                continue
            existing = watermarks.get(task_id)
            if existing is None or created_at < existing:
                watermarks[task_id] = created_at
    return watermarks


def check_source_drift(
    holdout: dict[str, Any],
    *,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Compare every source file's current hash against its freeze-time hash.

    The holdout recorded a SHA-256 for each referenced source at freeze time.
    A file that has changed since does not invalidate the experiment, but it
    does mean the frozen anchor was verified against different bytes than the
    ones being retrieved now -- so drift must be reported, never silently
    absorbed. A current hash is a drift fingerprint only; it is never evidence
    of a file's historical content.
    """
    frozen = holdout.get("source_hashes_at_freeze", {}) or {}
    unchanged: list[str] = []
    drifted: list[dict[str, str]] = []
    missing: list[str] = []
    for display, frozen_hash in sorted(frozen.items()):
        resolved = base.resolve_path(display, repo)
        if not resolved.is_file():
            missing.append(display)
            continue
        actual = base.sha256(resolved)
        if actual == frozen_hash:
            unchanged.append(display)
        else:
            drifted.append({
                "path": display,
                "frozen_sha256": frozen_hash,
                "current_sha256": actual,
            })
    return {
        "checked": len(frozen),
        "unchanged": len(unchanged),
        "drifted": drifted,
        "missing": missing,
        "clean": not drifted and not missing,
        "note": (
            "Drift does not invalidate a retrieved anchor, but it does mean the "
            "anchor was frozen against different bytes than are being read now. "
            "Reported, never silently absorbed."
        ),
    }


def python_symbols(text: str) -> list[tuple[str, int, str]]:
    """Return (name, lineno, docstring_first_line) for def/class nodes."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    results = []
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in seen or node.name.startswith("_"):
                if node.name in seen:
                    continue
            seen.add(node.name)
            doc = ast.get_docstring(node) or ""
            first_line = doc.splitlines()[0] if doc else ""
            results.append((node.name, node.lineno, first_line))
    return results


def local_tag_context(lines: list[str], lineno: int, window: int = 6) -> str:
    """Text near a symbol definition: preceding comments plus own docstring line."""
    start = max(0, lineno - 1 - window)
    end = min(len(lines), lineno - 1 + 3)
    return " ".join(lines[start:end])


def module_header_hints(lines: list[str], limit: int = 40) -> list[tuple[str, str]]:
    """(task_id, description) pairs from 'vN (TASK-XXX): description'-style header lines."""
    hints = []
    for line in lines[:limit]:
        match = TASK_TAG_RE.search(line)
        if match:
            hints.append((f"TASK-{match.group(1)}", line))
    return hints


def best_text_match(text_tokens: set[str], candidates: dict[str, set[str]]) -> tuple[str | None, float]:
    best_id, best_score = None, 0.0
    for task_id, tokens in sorted(candidates.items()):
        score = len(text_tokens.intersection(tokens))
        if score > best_score:
            best_id, best_score = task_id, float(score)
    return best_id, best_score


def attribute_symbol(
    *,
    linked_task_ids: list[str],
    local_context: str,
    header_hints: list[tuple[str, str]],
    symbol_tokens: set[str],
    task_text_tokens: dict[str, set[str]],
) -> tuple[str, str, float]:
    """Return (origin_task_id, attribution_method, confidence)."""
    if len(linked_task_ids) == 1:
        return linked_task_ids[0], "unique_link", 1.0

    linked_set = set(linked_task_ids)
    tag_matches = {f"TASK-{m}" for m in TASK_TAG_RE.findall(local_context)}
    tag_matches &= linked_set
    if len(tag_matches) == 1:
        return next(iter(tag_matches)), "inline_tag", 0.95

    header_best_id, header_best_score = None, 0.0
    for task_id, header_line in header_hints:
        if task_id not in linked_set:
            continue
        header_tokens = set(base.words(header_line))
        score = len(symbol_tokens.intersection(header_tokens))
        if score > header_best_score:
            header_best_id, header_best_score = task_id, score
    if header_best_id and header_best_score >= 1:
        return header_best_id, "version_header_match", 0.75

    candidates = {tid: task_text_tokens[tid] for tid in linked_task_ids if tid in task_text_tokens}
    fallback_id, fallback_score = best_text_match(symbol_tokens, candidates)
    if fallback_id and fallback_score > 0:
        return fallback_id, "acceptance_criteria_match", 0.5
    return sorted(linked_task_ids)[0], "undifferentiated_fallback", 0.2


def build_claim_cards(
    corpus_task_ids: list[str],
    *,
    tasks_dir: Path = TASKS_DIR,
    repo: Path = REPO,
    watermarks: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    watermarks = watermarks or {}
    tasks: dict[str, dict[str, Any]] = {}
    missing_tasks = []
    path_tasks: defaultdict[str, list[str]] = defaultdict(list)
    task_text_tokens: dict[str, set[str]] = {}

    for task_id in corpus_task_ids:
        task_path = tasks_dir / f"{task_id}.json"
        if not task_path.is_file():
            missing_tasks.append(task_id)
            continue
        task = load_json(task_path)
        tasks[task_id] = task
        text = " ".join([
            str(task.get("title", "")),
            str(task.get("description", "")),
            " ".join(str(v) for v in task.get("acceptance_criteria", [])),
        ])
        task_text_tokens[task_id] = set(base.words(text))
        for raw in task.get("output_paths", []):
            path_tasks[normalize_path(raw)].append(task_id)

    cards: list[dict[str, Any]] = []
    skipped_paths = []
    for path, linked in sorted(path_tasks.items()):
        linked = list(dict.fromkeys(linked))
        resolved = base.resolve_path(path, repo)
        if not resolved.is_file():
            skipped_paths.append({"path": path, "reason": "not_found"})
            continue
        current_sha256 = base.sha256(resolved)
        role = typed.evidence_role(path, repo)
        suffix = resolved.suffix.lower()

        if suffix == ".py":
            text = resolved.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            header_hints = module_header_hints(lines)
            for name, lineno, doc_first_line in python_symbols(text):
                local_context = local_tag_context(lines, lineno)
                symbol_tokens = set(base.words(f"{name} {doc_first_line}"))
                origin, method, confidence = attribute_symbol(
                    linked_task_ids=linked,
                    local_context=local_context,
                    header_hints=header_hints,
                    symbol_tokens=symbol_tokens,
                    task_text_tokens=task_text_tokens,
                )
                cards.append({
                    "task_id": origin,
                    "path": path,
                    "anchor_type": "code_symbol",
                    "anchor": name,
                    "role": role,
                    "attribution_method": method,
                    "attribution_confidence": confidence,
                    "linked_task_ids": linked,
                    "context_text": f"{name} {name} {doc_first_line} {local_context}".strip(),
                    "task_context_text": " ".join(task_text_tokens.get(origin, set())),
                    "current_sha256": current_sha256,
                    "watermark_utc": watermarks.get(origin),
                })
        elif suffix in {".md", ".markdown"}:
            text = resolved.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            header_hints = module_header_hints(lines, limit=len(lines))
            for line in lines:
                match = HEADING_RE.match(line.strip())
                if not match:
                    continue
                heading_text = match.group(2).strip()
                if not heading_text:
                    continue
                symbol_tokens = set(base.words(heading_text))
                local_context = heading_text
                origin, method, confidence = attribute_symbol(
                    linked_task_ids=linked,
                    local_context=local_context,
                    header_hints=header_hints,
                    symbol_tokens=symbol_tokens,
                    task_text_tokens=task_text_tokens,
                )
                cards.append({
                    "task_id": origin,
                    "path": path,
                    "anchor_type": "markdown_heading",
                    "anchor": heading_text,
                    "role": role,
                    "attribution_method": method,
                    "attribution_confidence": confidence,
                    "linked_task_ids": linked,
                    "context_text": f"{heading_text} {heading_text}",
                    "task_context_text": " ".join(task_text_tokens.get(origin, set())),
                    "current_sha256": current_sha256,
                    "watermark_utc": watermarks.get(origin),
                })
        else:
            skipped_paths.append({"path": path, "reason": f"unsupported_suffix:{suffix}"})

    build_meta = {
        "corpus_tasks_requested": len(corpus_task_ids),
        "corpus_tasks_loaded": len(tasks),
        "missing_tasks": missing_tasks,
        "linked_paths": len(path_tasks),
        "skipped_paths": skipped_paths,
        "claim_card_count": len(cards),
    }
    return cards, build_meta


TASK_CONTEXT_WEIGHT = 0.4


class ClaimIndex:
    """From-scratch TF-IDF-style lexical index over claim cards. No frozen
    retriever code is reused or modified here.

    Each card is scored on two channels: its own local anchor context (full
    weight -- symbol name, docstring, nearby comments, or heading text) and
    its origin task's title/description/acceptance-criteria text (lower
    weight -- most holdout questions are phrased at this level, not at the
    raw-identifier level, but an exact anchor match must still outrank a
    generic task-level match).
    """

    def __init__(self, cards: list[dict[str, Any]]):
        self.cards = cards
        self.local_tokens: list[set[str]] = []
        self.task_tokens: list[set[str]] = []
        df: defaultdict[str, int] = defaultdict(int)
        for card in cards:
            local = set(base.words(card["context_text"]))
            task_ctx = set(base.words(card.get("task_context_text", "")))
            self.local_tokens.append(local)
            self.task_tokens.append(task_ctx)
            for token in local.union(task_ctx):
                df[token] += 1
        n = max(1, len(cards))
        self.idf = {token: math.log((n + 1) / (count + 1)) + 1.0 for token, count in df.items()}

    def default_idf(self) -> float:
        return math.log(len(self.cards) + 1) + 1.0 if self.cards else 1.0

    def coverage_ratio(self, card_index: int, query_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        matched = query_tokens.intersection(
            self.local_tokens[card_index].union(self.task_tokens[card_index])
        )
        return len(matched) / len(query_tokens)

    def score_card(self, card_index: int, query_tokens: set[str]) -> float:
        local_overlap = query_tokens.intersection(self.local_tokens[card_index])
        task_overlap = query_tokens.intersection(self.task_tokens[card_index])
        local_score = sum(self.idf.get(token, self.default_idf()) for token in local_overlap)
        task_score = sum(self.idf.get(token, self.default_idf()) for token in task_overlap)
        return local_score + TASK_CONTEXT_WEIGHT * task_score

    def rank(self, query: str) -> list[dict[str, Any]]:
        query_tokens = set(base.words(query))
        scored = []
        for index, card in enumerate(self.cards):
            score = self.score_card(index, query_tokens)
            if score <= 0:
                continue
            scored.append({
                **card,
                "score": round(score, 4),
                "card_index": index,
                "coverage_ratio": round(self.coverage_ratio(index, query_tokens), 4),
            })
        scored.sort(key=lambda item: (-item["score"], item["path"], item["anchor"]))
        return scored


def polarity_of(tokens: set[str]) -> str:
    enable = len(tokens.intersection(ENABLE_WORDS))
    block = len(tokens.intersection(BLOCK_WORDS))
    if enable and enable > block:
        return "enable"
    if block and block > enable:
        return "block"
    return "neutral"


def retrieve(
    index: ClaimIndex,
    query: str,
    *,
    budget: int = SOURCE_BUDGET,
    min_task_score: float = MIN_TASK_SCORE,
    min_coverage_ratio: float = MIN_COVERAGE_RATIO,
) -> dict[str, Any]:
    ranked = index.rank(query)
    if not ranked:
        return {"predicted_task_ids": [], "predicted_sources": [], "abstained": True, "reason": "no_lexical_match"}

    by_task: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in ranked:
        by_task[card["task_id"]].append(card)

    task_totals = {}
    for task_id, task_cards in by_task.items():
        top = sorted((c["score"] for c in task_cards), reverse=True)
        task_totals[task_id] = top[0] + (0.5 * top[1] if len(top) > 1 else 0.0)

    best_task = max(task_totals, key=lambda tid: task_totals[tid])
    best_score = task_totals[best_task]

    if best_score < min_task_score:
        return {
            "predicted_task_ids": [], "predicted_sources": [], "abstained": True,
            "reason": f"below_threshold:{best_score:.2f}<{min_task_score}",
        }

    if by_task[best_task][0]["coverage_ratio"] < min_coverage_ratio:
        return {
            "predicted_task_ids": [], "predicted_sources": [], "abstained": True,
            "reason": f"low_coverage:{by_task[best_task][0]['coverage_ratio']:.2f}<{min_coverage_ratio}",
        }

    query_polarity = polarity_of(set(base.words(query)))
    if query_polarity == "enable":
        evidence_text = " ".join(
            c["context_text"] + " " + c.get("task_context_text", "")
            for c in by_task[best_task][:budget]
        )
        evidence_tokens = set(base.words(evidence_text))
        enable_count = len(evidence_tokens.intersection(ENABLE_WORDS))
        block_count = len(evidence_tokens.intersection(BLOCK_WORDS))
        if block_count > enable_count:
            return {
                "predicted_task_ids": [], "predicted_sources": [], "abstained": True,
                "reason": "polarity_mismatch:enable_query_block_evidence",
            }

    selected = []
    seen_anchor = set()
    for card in by_task[best_task]:
        key = (card["path"], card["anchor"])
        if key in seen_anchor:
            continue
        seen_anchor.add(key)
        selected.append(card)
        if len(selected) >= budget:
            break

    return {
        "predicted_task_ids": [best_task],
        "predicted_sources": [
            {"path": c["path"], "anchor_type": c["anchor_type"], "anchor": c["anchor"]}
            for c in selected
        ],
        "abstained": False,
        "task_score": round(best_score, 4),
        "attribution_methods": sorted({c["attribution_method"] for c in selected}),
    }


def evaluate(index: ClaimIndex, holdout: dict[str, Any]) -> dict[str, Any]:
    per_query = []
    task_recall_hits = task_recall_total = 0
    exact_source_hits = exact_source_total = 0
    anchor_hits = anchor_total = 0
    substitute_hits = 0
    abstention_correct = abstention_total = 0
    abstention_false_positive = 0
    historical_correct = historical_total = 0
    times = []

    for query in holdout["queries"]:
        kind = query["kind"]
        started = time.perf_counter()
        result = retrieve(index, query["question"])
        times.append((time.perf_counter() - started) * 1000)

        expected_task_ids = query.get("expected_task_ids", [])
        expected_sources = [normalize_path(p) for p in query.get("expected_source_paths", [])]
        expected_anchors = [
            (normalize_path(a["path"]), a["anchor"]) for a in query.get("expected_anchors", [])
        ]
        substitutes = {
            (normalize_path(s["path"]), s["anchor"]) for s in query.get("acceptable_substitutes", [])
        }
        predicted_sources = result["predicted_sources"]
        predicted_paths = [s["path"] for s in predicted_sources]
        predicted_anchor_pairs = {(s["path"], s["anchor"]) for s in predicted_sources}

        row: dict[str, Any] = {"id": query["id"], "kind": kind, "predicted": result}

        if kind in {"positive", "historical"}:
            task_recall_total += 1
            task_hit = bool(set(expected_task_ids).intersection(result["predicted_task_ids"]))
            task_recall_hits += int(task_hit)
            row["task_recall_hit"] = task_hit

            source_hits = [p for p in expected_sources if p in predicted_paths]
            exact_source_hits += len(source_hits)
            exact_source_total += len(expected_sources)
            row["exact_source_hits"] = source_hits
            row["exact_source_misses"] = [p for p in expected_sources if p not in predicted_paths]

            anchor_pair_hits = [pair for pair in expected_anchors if pair in predicted_anchor_pairs]
            anchor_hits += len(anchor_pair_hits)
            anchor_total += len(expected_anchors)
            row["anchor_hits"] = len(anchor_pair_hits)
            row["anchor_total"] = len(expected_anchors)

            missed_paths = [p for p in expected_sources if p not in predicted_paths]
            # A substitute hit means we actually RETRIEVED a legitimate
            # alternate source, so it can only be credited against what was
            # predicted. An earlier version also credited a hit whenever a
            # missed expected path merely equalled a substitute's path, which
            # over-reported badly: several holdout substitutes live in the
            # same file as their expected source (P01's read_lock_pid sits in
            # agent_loop.py alongside the expected acquire_loop_lock), so that
            # clause fired without anything having been retrieved at all.
            matched_substitutes = sorted(substitutes.intersection(predicted_anchor_pairs))
            sub_hit = bool(matched_substitutes)
            if sub_hit:
                substitute_hits += 1
            row["substitute_hit"] = sub_hit
            row["matched_substitutes"] = matched_substitutes
            row["missed_expected_paths"] = missed_paths

            if kind == "historical":
                historical_total += 1
                trap_task_ids = set(TASK_TAG_RE.findall(query.get("temporal_trap", "")))
                trap_task_ids = {f"TASK-{t}" for t in trap_task_ids} - set(expected_task_ids)
                wrong = bool(trap_task_ids.intersection(result["predicted_task_ids"]))
                correct = task_hit and not wrong
                historical_correct += int(correct)
                row["historical_correct"] = correct
                row["historical_trap_hit"] = wrong

        elif kind == "negative":
            abstention_total += 1
            correct = result["abstained"]
            abstention_correct += int(correct)
            abstention_false_positive += int(not correct)
            row["abstained_correctly"] = correct

        per_query.append(row)

    sorted_times = sorted(times)
    median_ms = sorted_times[len(sorted_times) // 2] if sorted_times else 0.0

    return {
        "task_recall": f"{task_recall_hits}/{task_recall_total}",
        "task_recall_ratio": round(task_recall_hits / task_recall_total, 4) if task_recall_total else None,
        "exact_source_accuracy": f"{exact_source_hits}/{exact_source_total}",
        "exact_source_ratio": round(exact_source_hits / exact_source_total, 4) if exact_source_total else None,
        "anchored_evidence_accuracy": f"{anchor_hits}/{anchor_total}",
        "anchored_evidence_ratio": round(anchor_hits / anchor_total, 4) if anchor_total else None,
        "acceptable_substitute_hits_on_missed_queries": substitute_hits,
        "abstention_precision_recall": f"{abstention_correct}/{abstention_total}",
        "abstention_false_positives": abstention_false_positive,
        "historical_version_correctness": f"{historical_correct}/{historical_total}",
        "median_selection_ms": round(median_ms, 4),
        "per_query": per_query,
    }


def generate(holdout_path: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    actual_sha = base.sha256(holdout_path)
    if actual_sha != HOLDOUT_EXPECTED_SHA256:
        raise SystemExit(
            f"frozen holdout hash mismatch: expected {HOLDOUT_EXPECTED_SHA256}, got {actual_sha}. "
            "Refusing to evaluate against a possibly-modified holdout."
        )
    holdout = load_json(holdout_path)
    source_drift = check_source_drift(holdout)
    watermarks = read_events_watermarks(DEFAULT_EVENTS)
    cards, build_meta = build_claim_cards(holdout["corpus_task_ids"], watermarks=watermarks)
    index = ClaimIndex(cards)
    metrics = evaluate(index, holdout)

    anchor_types = defaultdict(int)
    method_counts = defaultdict(int)
    suffix_counts = defaultdict(int)
    for card in cards:
        anchor_types[card["anchor_type"]] += 1
        method_counts[card["attribution_method"]] += 1
        suffix_counts[Path(card["path"]).suffix.lower() or "(none)"] += 1
    authoring_cost = {
        "claim_cards_total": len(cards),
        "cards_by_anchor_type": dict(anchor_types),
        "cards_by_attribution_method": dict(method_counts),
        "authoring_effort": (
            "zero manual authoring per card; all cards are mechanically derived "
            "from existing task JSON, source files, and events.jsonl at build time"
        ),
    }
    parser_coverage = {
        "linked_paths": build_meta["linked_paths"],
        "cards_by_source_suffix": dict(suffix_counts),
        "skipped_paths": build_meta["skipped_paths"],
        "note": (
            "Only .py (code_symbol via ast) and .md/.markdown (markdown_heading via "
            "'#' line scan) are parsed; other linked suffixes are skipped and listed "
            "in skipped_paths, so parser coverage is partial by design."
        ),
    }
    median_packet_words = 0
    if metrics["per_query"]:
        word_counts = sorted(
            len(base.words(" ".join(
                f"{s['path']} {s['anchor']}" for s in row["predicted"]["predicted_sources"]
            )))
            for row in metrics["per_query"]
        )
        median_packet_words = word_counts[len(word_counts) // 2]

    payload = {
        "experiment": "EXP-0006 / TASK-263",
        "authority": (
            "none; disposable experiment evidence only. Does not change production "
            "retrieval, startup, routing, or canonical policy."
        ),
        "treatment_author": "claude-lab-lili",
        "holdout_source": str(holdout_path.relative_to(REPO)),
        "holdout_sha256_verified": actual_sha,
        "source_hash_drift": source_drift,
        "min_task_score_threshold": MIN_TASK_SCORE,
        "source_budget": SOURCE_BUDGET,
        "build": build_meta,
        "metrics": metrics,
        "authoring_cost": authoring_cost,
        "parser_coverage": parser_coverage,
        "median_packet_words_per_query": median_packet_words,
        "baselines_to_beat": holdout["scoring_contract"]["baselines_to_beat"],
        "blind_evaluation_disclosure": (
            "This run was scored by the treatment implementer (claude-lab-lili), not "
            "by a separate blind evaluator. `soba` was reserved as blind evaluator in "
            "prior TASK-263 handoffs but is not a currently-registered agent. No second "
            "agent scored blinded output this session. The scorer itself is fully "
            "mechanical (exact string/path comparison against the frozen holdout's "
            "recorded fields) with no subjective judgment calls, but this does not "
            "substitute for independent execution. The independent TASK-263 reviewer "
            "should re-run this script (deterministic, reproducible) and treat these "
            "numbers as implementer-reported pending that re-run."
        ),
    }
    write_json(output_json, payload)

    md_lines = [
        "# TASK-263 Claim-Evidence Retrieval Pilot — Development Report",
        "",
        "Experiment evidence only (EXP-0006 / TASK-263). No production authority.",
        "",
        f"- Holdout: `{payload['holdout_source']}` (sha256 verified: {actual_sha[:16]}...)",
        f"- Claim cards built: {build_meta['claim_card_count']} over "
        f"{build_meta['corpus_tasks_loaded']} corpus tasks, {build_meta['linked_paths']} linked paths",
        f"- Task recall: {metrics['task_recall']} ({metrics['task_recall_ratio']})",
        f"- Exact-source accuracy: {metrics['exact_source_accuracy']} ({metrics['exact_source_ratio']})",
        f"- Anchored-evidence accuracy: {metrics['anchored_evidence_accuracy']} "
        f"({metrics['anchored_evidence_ratio']})",
        f"- Acceptable-substitute hits (a legitimate alternate source was actually "
        f"retrieved): {metrics['acceptable_substitute_hits_on_missed_queries']}",
        f"- Source-hash drift since freeze: {len(source_drift['drifted'])} drifted, "
        f"{len(source_drift['missing'])} missing, of {source_drift['checked']} checked"
        + ("" if source_drift["clean"] else "  <-- anchors were frozen against different bytes"),
        f"- Abstention (negatives correctly abstained): {metrics['abstention_precision_recall']}, "
        f"false positives: {metrics['abstention_false_positives']}",
        f"- Historical-version correctness: {metrics['historical_version_correctness']}",
        f"- Median selection time: {metrics['median_selection_ms']} ms",
        "",
        f"Baselines to beat (recorded in the frozen holdout): "
        f"exact-source {payload['baselines_to_beat']['capsule_exact_source']}, "
        f"task recall {payload['baselines_to_beat']['task_recall']}.",
        "",
    ]
    output_md.write_text("\n".join(md_lines), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout", type=Path, default=DEFAULT_HOLDOUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()
    payload = generate(args.holdout, args.output_json, args.output_md)
    print(json.dumps({
        "task_recall": payload["metrics"]["task_recall"],
        "exact_source_accuracy": payload["metrics"]["exact_source_accuracy"],
        "anchored_evidence_accuracy": payload["metrics"]["anchored_evidence_accuracy"],
        "abstention": payload["metrics"]["abstention_precision_recall"],
        "historical_version_correctness": payload["metrics"]["historical_version_correctness"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
