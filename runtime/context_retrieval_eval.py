from __future__ import annotations

from collections import Counter
import math
import re
from typing import Mapping, Sequence

from .context_evidence import EvidenceIntegrityError, evaluate_evidence_integrity


class RetrievalEvaluationError(ValueError):
    pass


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "does",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "under",
    "use",
    "what",
    "when",
    "which",
    "with",
}


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RetrievalEvaluationError(f"{field} must be non-empty text")
    return value.strip()


def _corpus_index(corpus: Mapping[str, object]):
    try:
        integrity = evaluate_evidence_integrity(
            corpus,
            [],
            label="stage2-retrieval-corpus-validation",
        )
    except EvidenceIntegrityError as exc:
        raise RetrievalEvaluationError(str(exc)) from exc

    raw_sources = corpus.get("sources")
    raw_cases = corpus.get("cases")
    if not isinstance(raw_sources, list) or not isinstance(raw_cases, list):
        raise RetrievalEvaluationError("corpus sources/cases must be lists")

    sources: dict[str, dict[str, object]] = {}
    for raw in raw_sources:
        if not isinstance(raw, Mapping):
            raise RetrievalEvaluationError("source must be a mapping")
        source_id = _text(raw.get("id"), "source.id")
        sources[source_id] = {
            "id": source_id,
            "path": _text(raw.get("path"), f"{source_id}.path"),
            "version": _text(raw.get("version"), f"{source_id}.version"),
            "content": str(raw.get("content", "")),
            "sha256": _text(raw.get("sha256"), f"{source_id}.sha256"),
        }

    cases: dict[str, dict[str, object]] = {}
    order: list[str] = []
    for raw in raw_cases:
        if not isinstance(raw, Mapping):
            raise RetrievalEvaluationError("case must be a mapping")
        case_id = _text(raw.get("id"), "case.id")
        accepted: list[str] = []
        for field in ("expected_cards", "acceptable_substitutes"):
            cards = raw.get(field, [])
            if not isinstance(cards, list):
                raise RetrievalEvaluationError(f"{case_id}.{field} must be a list")
            for card in cards:
                if not isinstance(card, Mapping):
                    raise RetrievalEvaluationError(f"{case_id}.{field} card is invalid")
                source_id = _text(card.get("source_id"), f"{case_id}.{field}.source_id")
                if source_id not in accepted:
                    accepted.append(source_id)
        forbidden: list[str] = []
        for item in raw.get("forbidden_credit", []):
            if not isinstance(item, Mapping):
                raise RetrievalEvaluationError(f"{case_id}.forbidden_credit is invalid")
            source_id = _text(item.get("source_id"), f"{case_id}.forbidden_source")
            if source_id not in forbidden:
                forbidden.append(source_id)
        drift = raw.get("drift")
        drift_ids: list[str] = []
        if drift is not None:
            if not isinstance(drift, Mapping):
                raise RetrievalEvaluationError(f"{case_id}.drift is invalid")
            for key in ("frozen_source_id", "current_source_id"):
                source_id = _text(drift.get(key), f"{case_id}.drift.{key}")
                if source_id not in drift_ids:
                    drift_ids.append(source_id)
        cases[case_id] = {
            "id": case_id,
            "category": _text(raw.get("category"), f"{case_id}.category"),
            "query": _text(raw.get("query"), f"{case_id}.query"),
            "expected_outcome": _text(
                raw.get("expected_outcome"), f"{case_id}.expected_outcome"
            ),
            "accepted_source_ids": tuple(accepted),
            "forbidden_source_ids": tuple(forbidden),
            "drift_source_ids": tuple(drift_ids),
        }
        order.append(case_id)
    return sources, cases, tuple(order), str(integrity["corpus_sha256"])


def _validate_overlay(
    corpus: Mapping[str, object], overlay: Mapping[str, object]
):
    sources, cases, order, corpus_sha = _corpus_index(corpus)
    if overlay.get("version") != "context-builder-retrieval-stage2-v1":
        raise RetrievalEvaluationError("unsupported Stage 2 overlay version")
    if overlay.get("base_corpus_version") != corpus.get("version"):
        raise RetrievalEvaluationError("Stage 2 overlay targets a different corpus version")
    raw_cases = overlay.get("cases")
    if not isinstance(raw_cases, list):
        raise RetrievalEvaluationError("overlay cases must be a list")

    explicit: dict[str, tuple[str, ...]] = {}
    for raw in raw_cases:
        if not isinstance(raw, Mapping) or set(raw) != {"case_id", "explicit_source_ids"}:
            raise RetrievalEvaluationError(
                "overlay case must contain exactly case_id/explicit_source_ids"
            )
        case_id = _text(raw.get("case_id"), "overlay.case_id")
        if case_id not in cases:
            raise RetrievalEvaluationError(f"overlay has unknown case: {case_id}")
        if case_id in explicit:
            raise RetrievalEvaluationError(f"overlay duplicates case: {case_id}")
        source_ids = raw.get("explicit_source_ids")
        if not isinstance(source_ids, list):
            raise RetrievalEvaluationError(
                f"{case_id}.explicit_source_ids must be a list"
            )
        normalized: list[str] = []
        for value in source_ids:
            source_id = _text(value, f"{case_id}.explicit_source_id")
            if source_id not in sources:
                raise RetrievalEvaluationError(
                    f"{case_id} references unknown explicit source: {source_id}"
                )
            if source_id in normalized:
                raise RetrievalEvaluationError(
                    f"{case_id} duplicates explicit source: {source_id}"
                )
            normalized.append(source_id)
        explicit[case_id] = tuple(normalized)

    if set(explicit) != set(order):
        missing = sorted(set(order) - set(explicit))
        extra = sorted(set(explicit) - set(order))
        raise RetrievalEvaluationError(
            f"overlay case coverage mismatch; missing={missing}, extra={extra}"
        )

    config = overlay.get("lexical_negative_control")
    if not isinstance(config, Mapping):
        raise RetrievalEvaluationError("lexical_negative_control must be an object")
    if set(config) != {
        "top_k",
        "minimum_shared_terms",
        "supplement_when",
        "promotion_candidate",
    }:
        raise RetrievalEvaluationError("lexical negative-control fields are invalid")
    top_k = config.get("top_k")
    minimum_shared_terms = config.get("minimum_shared_terms")
    if (
        isinstance(top_k, bool)
        or not isinstance(top_k, int)
        or top_k < 1
        or top_k > len(sources)
    ):
        raise RetrievalEvaluationError("lexical top_k is invalid")
    if (
        isinstance(minimum_shared_terms, bool)
        or not isinstance(minimum_shared_terms, int)
        or minimum_shared_terms < 1
    ):
        raise RetrievalEvaluationError("minimum_shared_terms is invalid")
    if config.get("supplement_when") != "EXPLICIT_SOURCE_SET_EMPTY":
        raise RetrievalEvaluationError(
            "v1 lexical negative control must supplement only when explicit sources are empty"
        )
    if config.get("promotion_candidate") is not False:
        raise RetrievalEvaluationError(
            "lexical negative control must not be marked as a promotion candidate"
        )

    return sources, cases, order, explicit, corpus_sha, {
        "top_k": top_k,
        "minimum_shared_terms": minimum_shared_terms,
    }


def _prediction(case_id: str, source_ids: Sequence[str]) -> dict[str, object]:
    return {"case_id": case_id, "source_ids": list(source_ids)}


def explicit_only_rankings(
    corpus: Mapping[str, object], overlay: Mapping[str, object]
) -> list[dict[str, object]]:
    _, _, order, explicit, _, _ = _validate_overlay(corpus, overlay)
    return [_prediction(case_id, explicit[case_id]) for case_id in order]


def same_path_drift_rankings(
    corpus: Mapping[str, object], overlay: Mapping[str, object]
) -> list[dict[str, object]]:
    sources, _, order, explicit, _, _ = _validate_overlay(corpus, overlay)
    output: list[dict[str, object]] = []
    for case_id in order:
        selected = list(explicit[case_id])
        for source_id in tuple(selected):
            source = sources[source_id]
            if str(source["version"]).lower() == "current":
                continue
            siblings = sorted(
                (
                    item
                    for item in sources.values()
                    if item["id"] != source_id
                    and item["path"] == source["path"]
                    and item["sha256"] != source["sha256"]
                ),
                key=lambda item: (
                    0 if str(item["version"]).lower() == "current" else 1,
                    str(item["id"]),
                ),
            )
            for sibling in siblings:
                sibling_id = str(sibling["id"])
                if sibling_id not in selected:
                    selected.append(sibling_id)
        output.append(_prediction(case_id, selected))
    return output


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(
        token
        for token in (match.group(0).lower() for match in _TOKEN_RE.finditer(value))
        if len(token) > 1 and token not in _STOPWORDS
    )


def _lexical_scores(
    sources: Mapping[str, Mapping[str, object]], query: str
) -> list[tuple[str, float, int]]:
    query_counts = Counter(_tokens(query))
    if not query_counts:
        return []

    documents: dict[str, Counter[str]] = {}
    document_frequency: Counter[str] = Counter()
    for source_id, source in sources.items():
        tokens = _tokens(f"{source['path']}\n{source['content']}")
        counts = Counter(tokens)
        documents[source_id] = counts
        document_frequency.update(counts.keys())

    total_documents = len(documents)
    scored: list[tuple[str, float, int]] = []
    for source_id, counts in documents.items():
        shared = set(query_counts) & set(counts)
        if not shared:
            continue
        score = 0.0
        shared_terms = 0
        for token in shared:
            shared_terms += 1
            idf = math.log((total_documents + 1) / (document_frequency[token] + 1)) + 1.0
            query_weight = 1.0 + math.log(query_counts[token])
            document_weight = 1.0 + math.log(counts[token])
            score += idf * query_weight * document_weight
        scored.append((source_id, score, shared_terms))
    return sorted(scored, key=lambda item: (-item[1], -item[2], item[0]))


def lexical_negative_control_rankings(
    corpus: Mapping[str, object], overlay: Mapping[str, object]
) -> list[dict[str, object]]:
    sources, cases, order, explicit, _, config = _validate_overlay(corpus, overlay)
    output: list[dict[str, object]] = []
    for case_id in order:
        selected = list(explicit[case_id])
        if not selected:
            ranked = _lexical_scores(sources, str(cases[case_id]["query"]))
            for source_id, _, shared_terms in ranked:
                if shared_terms < int(config["minimum_shared_terms"]):
                    continue
                selected.append(source_id)
                if len(selected) >= int(config["top_k"]):
                    break
        output.append(_prediction(case_id, selected))
    return output


def _validate_predictions(
    sources: Mapping[str, Mapping[str, object]],
    order: Sequence[str],
    predictions: Sequence[Mapping[str, object]],
) -> dict[str, tuple[str, ...]]:
    indexed: dict[str, tuple[str, ...]] = {}
    valid_cases = set(order)
    for raw in predictions:
        if not isinstance(raw, Mapping) or set(raw) != {"case_id", "source_ids"}:
            raise RetrievalEvaluationError(
                "prediction must contain exactly case_id/source_ids"
            )
        case_id = _text(raw.get("case_id"), "prediction.case_id")
        if case_id not in valid_cases:
            raise RetrievalEvaluationError(f"unknown prediction case: {case_id}")
        if case_id in indexed:
            raise RetrievalEvaluationError(f"duplicate prediction case: {case_id}")
        raw_ids = raw.get("source_ids")
        if not isinstance(raw_ids, list):
            raise RetrievalEvaluationError(f"{case_id}.source_ids must be a list")
        normalized: list[str] = []
        for value in raw_ids:
            source_id = _text(value, f"{case_id}.source_id")
            if source_id not in sources:
                raise RetrievalEvaluationError(
                    f"{case_id} selected unknown source: {source_id}"
                )
            if source_id in normalized:
                raise RetrievalEvaluationError(
                    f"{case_id} selected duplicate source: {source_id}"
                )
            normalized.append(source_id)
        indexed[case_id] = tuple(normalized)
    if set(indexed) != valid_cases:
        missing = sorted(valid_cases - set(indexed))
        raise RetrievalEvaluationError(f"predictions omit cases: {missing}")
    return indexed


def evaluate_source_rankings(
    corpus: Mapping[str, object],
    overlay: Mapping[str, object],
    predictions: Sequence[Mapping[str, object]],
    *,
    label: str,
) -> dict[str, object]:
    """Evaluate source selection only; this does not score evidence-card correctness."""

    label = _text(label, "label")
    sources, cases, order, explicit, corpus_sha, _ = _validate_overlay(corpus, overlay)
    indexed = _validate_predictions(sources, order, predictions)

    reports: list[dict[str, object]] = []
    evidence_cases = 0
    evidence_hits = 0
    evidence_precision_numerator = 0
    evidence_precision_denominator = 0
    hard_negative_cases = 0
    hard_negative_abstained = 0
    forbidden_case_count = 0
    drift_cases = 0
    drift_pairs_complete = 0
    vocabulary_cases = 0
    vocabulary_hits = 0

    for case_id in order:
        case = cases[case_id]
        selected = indexed[case_id]
        accepted = set(case["accepted_source_ids"])
        forbidden = set(case["forbidden_source_ids"])
        drift_ids = set(case["drift_source_ids"])
        expected_outcome = str(case["expected_outcome"])
        selected_set = set(selected)

        forbidden_selected = tuple(x for x in selected if x in forbidden)
        accepted_selected = tuple(x for x in selected if x in accepted)
        hit = bool(accepted_selected)
        top1_hit = bool(selected) and selected[0] in accepted
        explicit_prefix_preserved = tuple(selected[: len(explicit[case_id])]) == explicit[case_id]

        if expected_outcome == "ABSTAIN":
            hard_negative_cases += 1
            passed = not selected
            if passed:
                hard_negative_abstained += 1
        elif expected_outcome == "DRIFT_REPORTED":
            drift_cases += 1
            passed = bool(drift_ids) and drift_ids.issubset(selected_set)
            if passed:
                drift_pairs_complete += 1
        else:
            evidence_cases += 1
            passed = hit and not forbidden_selected
            if hit:
                evidence_hits += 1
            evidence_precision_numerator += len(accepted_selected)
            evidence_precision_denominator += len(selected)
            if case["category"] == "VOCABULARY_SHIFT":
                vocabulary_cases += 1
                if hit:
                    vocabulary_hits += 1

        if forbidden_selected:
            forbidden_case_count += 1
            passed = False

        reports.append(
            {
                "case_id": case_id,
                "category": case["category"],
                "status": "PASS" if passed else "FAIL",
                "selected_source_ids": list(selected),
                "explicit_source_ids": list(explicit[case_id]),
                "checks": {
                    "accepted_source_retrieved": hit,
                    "top1_accepted": top1_hit,
                    "forbidden_source_selected": bool(forbidden_selected),
                    "forbidden_source_ids": list(forbidden_selected),
                    "drift_pair_complete": (
                        drift_ids.issubset(selected_set) if drift_ids else None
                    ),
                    "hard_negative_abstained": (
                        not selected if expected_outcome == "ABSTAIN" else None
                    ),
                    "explicit_prefix_preserved": explicit_prefix_preserved,
                },
            }
        )

    evidence_recall = evidence_hits / evidence_cases if evidence_cases else 1.0
    evidence_precision = (
        evidence_precision_numerator / evidence_precision_denominator
        if evidence_precision_denominator
        else 1.0
    )
    hard_negative_abstention = (
        hard_negative_abstained / hard_negative_cases if hard_negative_cases else 1.0
    )
    drift_pair_recall = drift_pairs_complete / drift_cases if drift_cases else 1.0
    vocabulary_recall = vocabulary_hits / vocabulary_cases if vocabulary_cases else 1.0
    average_candidates = sum(len(indexed[case_id]) for case_id in order) / len(order)

    safety_gates = {
        "hard_negative_abstention_perfect": hard_negative_abstention == 1.0,
        "no_forbidden_temporal_source": forbidden_case_count == 0,
        "drift_pairs_complete": drift_pair_recall == 1.0,
        "vocabulary_shift_recalled": vocabulary_recall == 1.0,
        "evidence_recall_perfect": evidence_recall == 1.0,
        "explicit_prefix_preserved": all(
            report["checks"]["explicit_prefix_preserved"] for report in reports
        ),
    }

    return {
        "report_version": 1,
        "report_kind": "MAPS_CONTEXT_RETRIEVAL_STAGE2_REPORT",
        "label": label,
        "corpus_version": corpus["version"],
        "corpus_sha256": corpus_sha,
        "overlay_version": overlay["version"],
        "cases": reports,
        "metrics": {
            "case_pass_rate": sum(x["status"] == "PASS" for x in reports) / len(reports),
            "evidence_source_recall": evidence_recall,
            "evidence_source_precision": evidence_precision,
            "hard_negative_abstention_accuracy": hard_negative_abstention,
            "forbidden_source_case_count": forbidden_case_count,
            "drift_pair_recall": drift_pair_recall,
            "vocabulary_shift_recall": vocabulary_recall,
            "average_candidate_count": average_candidates,
        },
        "candidate_gate": {
            "eligible_for_proposal": all(safety_gates.values()),
            "automatic_promotion": False,
            "gates": safety_gates,
            "rule": (
                "source-retrieval success is only candidate evidence; it cannot authorize "
                "production Context Builder routing or retrieval changes"
            ),
        },
    }


def run_stage2_controls(
    corpus: Mapping[str, object], overlay: Mapping[str, object]
) -> dict[str, object]:
    """Run deterministic controls; lexical output is deliberately a negative control."""

    explicit = evaluate_source_rankings(
        corpus,
        overlay,
        explicit_only_rankings(corpus, overlay),
        label="explicit-only-control",
    )
    drift = evaluate_source_rankings(
        corpus,
        overlay,
        same_path_drift_rankings(corpus, overlay),
        label="explicit-plus-same-path-drift-control",
    )
    lexical = evaluate_source_rankings(
        corpus,
        overlay,
        lexical_negative_control_rankings(corpus, overlay),
        label="lexical-overlap-negative-control",
    )
    lexical["candidate_gate"]["eligible_for_proposal"] = False
    lexical["candidate_gate"]["forced_non_candidate_reason"] = (
        "this method is retained only as a frozen negative control and is not a "
        "production retrieval proposal"
    )
    return {
        "report_version": 1,
        "report_kind": "MAPS_CONTEXT_RETRIEVAL_STAGE2_CONTROL_COMPARISON",
        "controls": {
            "explicit_only": explicit,
            "same_path_drift": drift,
            "lexical_negative_control": lexical,
        },
        "promotion": {
            "automatic": False,
            "next_step": (
                "future semantic/vector or other candidates submit source rankings to "
                "evaluate_source_rankings against the same frozen corpus/overlay"
            ),
        },
    }
