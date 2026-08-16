from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping, Sequence


class EvidenceIntegrityError(ValueError):
    pass


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CARD_FIELDS = {
    "source_id",
    "source_sha256",
    "anchor",
    "proof_role",
    "polarity",
    "temporal_scope",
}
_ANCHOR_TYPES = {"MARKDOWN_SECTION", "CODE_SYMBOL", "DOCUMENT_STATUS"}
_POLARITIES = {"POSITIVE", "NEGATIVE_BOUNDARY"}
_RESULT_KEYS = {"case_id", "outcome", "cards", "drift"}
_DRIFT_KEYS = {
    "frozen_source_id",
    "frozen_sha256",
    "current_source_id",
    "current_sha256",
    "same_path",
    "hash_mismatch",
}


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceIntegrityError(f"{field} must be non-empty text")
    return value.strip()


def _hash(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def _anchor(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != {"type", "value"}:
        raise EvidenceIntegrityError("anchor must contain exactly type/value")
    kind = _text(value.get("type"), "anchor.type")
    label = _text(value.get("value"), "anchor.value")
    if kind not in _ANCHOR_TYPES:
        raise EvidenceIntegrityError(f"unsupported anchor type: {kind}")
    return {"type": kind, "value": label}


def _resolves(source: Mapping[str, object], anchor: Mapping[str, str]) -> bool:
    content = str(source["content"])
    kind, value = anchor["type"], anchor["value"]
    if kind == "MARKDOWN_SECTION":
        headings = {line.strip() for line in content.splitlines()}
        return any(f"{'#' * n} {value}" in headings for n in range(1, 7))
    if kind == "DOCUMENT_STATUS":
        return value in content
    if "." not in value:
        return False
    owner, symbol = value.rsplit(".", 1)
    return f"class {owner}" in content and f"def {symbol}" in content


def _source(raw: Mapping[str, object]) -> dict[str, object]:
    source_id = _text(raw.get("id"), "source.id")
    content = raw.get("content")
    sha = raw.get("sha256")
    if not isinstance(content, str):
        raise EvidenceIntegrityError(f"{source_id}.content must be text")
    if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
        raise EvidenceIntegrityError(f"{source_id}.sha256 is invalid")
    if hashlib.sha256(content.encode()).hexdigest() != sha:
        raise EvidenceIntegrityError(f"{source_id}.sha256 does not match content")
    return {
        "id": source_id,
        "path": _text(raw.get("path"), f"{source_id}.path"),
        "version": _text(raw.get("version"), f"{source_id}.version"),
        "content": content,
        "sha256": sha,
    }


def _card(raw: Mapping[str, object], *, truth: bool = False) -> dict[str, object]:
    allowed = _CARD_FIELDS | ({"credit_only_if_retrieved"} if truth else set())
    if not _CARD_FIELDS.issubset(raw) or set(raw) - allowed:
        raise EvidenceIntegrityError("evidence card fields are invalid")
    sha = raw.get("source_sha256")
    if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
        raise EvidenceIntegrityError("source_sha256 is invalid")
    polarity = _text(raw.get("polarity"), "polarity")
    if polarity not in _POLARITIES:
        raise EvidenceIntegrityError(f"unsupported polarity: {polarity}")
    return {
        "source_id": _text(raw.get("source_id"), "source_id"),
        "source_sha256": sha,
        "anchor": _anchor(raw.get("anchor")),
        "proof_role": _text(raw.get("proof_role"), "proof_role"),
        "polarity": polarity,
        "temporal_scope": _text(raw.get("temporal_scope"), "temporal_scope"),
    }


def project_evidence_card(
    source: Mapping[str, object],
    *,
    anchor: Mapping[str, str],
    proof_role: str,
    polarity: str,
    temporal_scope: str,
) -> dict[str, object]:
    """Verify and project one explicitly selected source/anchor; performs no retrieval."""

    src = _source(source)
    resolved_anchor = _anchor(anchor)
    if not _resolves(src, resolved_anchor):
        raise EvidenceIntegrityError(f"anchor does not resolve in {src['id']}")
    role = _text(proof_role, "proof_role")
    pol = _text(polarity, "polarity")
    if pol not in _POLARITIES:
        raise EvidenceIntegrityError(f"unsupported polarity: {pol}")
    return {
        "source_id": src["id"],
        "source_sha256": src["sha256"],
        "anchor": resolved_anchor,
        "proof_role": role,
        "polarity": pol,
        "temporal_scope": _text(temporal_scope, "temporal_scope"),
    }


def _validate_corpus(corpus: Mapping[str, object]):
    if corpus.get("version") != "context-builder-evidence-integrity-v1":
        raise EvidenceIntegrityError("unsupported evidence-integrity corpus version")
    contract = corpus.get("candidate_output_contract")
    metrics = corpus.get("metrics")
    raw_sources = corpus.get("sources")
    raw_cases = corpus.get("cases")
    if not isinstance(contract, Mapping) or not isinstance(contract.get("outcome"), list):
        raise EvidenceIntegrityError("candidate output contract is invalid")
    if not isinstance(metrics, list) or not all(isinstance(x, str) for x in metrics):
        raise EvidenceIntegrityError("metric list is invalid")
    if not isinstance(raw_sources, list) or not isinstance(raw_cases, list):
        raise EvidenceIntegrityError("sources/cases must be lists")

    outcomes = set(contract["outcome"])
    sources = {}
    for raw in raw_sources:
        if not isinstance(raw, Mapping):
            raise EvidenceIntegrityError("source must be a mapping")
        src = _source(raw)
        if src["id"] in sources:
            raise EvidenceIntegrityError(f"duplicate source: {src['id']}")
        sources[src["id"]] = src

    cases = []
    seen = set()
    for raw in raw_cases:
        if not isinstance(raw, Mapping):
            raise EvidenceIntegrityError("case must be a mapping")
        case_id = _text(raw.get("id"), "case.id")
        if case_id in seen:
            raise EvidenceIntegrityError(f"duplicate case: {case_id}")
        seen.add(case_id)
        outcome = _text(raw.get("expected_outcome"), f"{case_id}.expected_outcome")
        if outcome not in outcomes:
            raise EvidenceIntegrityError(f"{case_id}: unsupported expected outcome")
        expected = [_card(x, truth=True) for x in raw.get("expected_cards", [])]
        substitutes = [
            _card(x, truth=True) for x in raw.get("acceptable_substitutes", [])
        ]
        if outcome == "EVIDENCE" and len(expected) != 1:
            raise EvidenceIntegrityError(
                f"{case_id}: v1 requires one primary evidence card"
            )
        for card in expected + substitutes:
            src = sources.get(card["source_id"])
            if (
                src is None
                or card["source_sha256"] != src["sha256"]
                or not _resolves(src, card["anchor"])
            ):
                raise EvidenceIntegrityError(f"{case_id}: frozen card does not resolve")
        forbidden = []
        for item in raw.get("forbidden_credit", []):
            if not isinstance(item, Mapping):
                raise EvidenceIntegrityError(f"{case_id}: forbidden credit is invalid")
            source_id = _text(item.get("source_id"), "forbidden source")
            if source_id not in sources:
                raise EvidenceIntegrityError(f"{case_id}: forbidden source is unknown")
            forbidden.append(source_id)
        drift = raw.get("drift")
        if drift is not None:
            if not isinstance(drift, Mapping):
                raise EvidenceIntegrityError(f"{case_id}: drift is invalid")
            for key in ("frozen_source_id", "current_source_id"):
                if drift.get(key) not in sources:
                    raise EvidenceIntegrityError(f"{case_id}: drift source is unknown")
        cases.append(
            {
                "id": case_id,
                "category": _text(raw.get("category"), f"{case_id}.category"),
                "expected_outcome": outcome,
                "expected_cards": expected,
                "substitutes": substitutes,
                "forbidden": forbidden,
                "drift": drift,
            }
        )
    return sources, cases, outcomes, metrics


def _candidate(raw: Mapping[str, object], outcomes: set[str]) -> dict[str, object]:
    if set(raw) - _RESULT_KEYS:
        raise EvidenceIntegrityError("candidate result has unknown fields")
    case_id = _text(raw.get("case_id"), "case_id")
    outcome = _text(raw.get("outcome"), f"{case_id}.outcome")
    if outcome not in outcomes:
        raise EvidenceIntegrityError(f"{case_id}: unsupported outcome")
    raw_cards = raw.get("cards")
    if not isinstance(raw_cards, list):
        raise EvidenceIntegrityError(f"{case_id}.cards must be a list")
    cards = []
    for raw_card in raw_cards:
        if not isinstance(raw_card, Mapping):
            raise EvidenceIntegrityError(f"{case_id}: card must be a mapping")
        cards.append(_card(raw_card))

    drift = raw.get("drift")
    if drift is not None:
        if not isinstance(drift, Mapping) or set(drift) != _DRIFT_KEYS:
            raise EvidenceIntegrityError(f"{case_id}.drift fields are invalid")
        for key in ("frozen_sha256", "current_sha256"):
            value = drift.get(key)
            if not isinstance(value, str) or not _SHA256.fullmatch(value):
                raise EvidenceIntegrityError(f"{case_id}.{key} is invalid")
        drift = {
            "frozen_source_id": _text(
                drift.get("frozen_source_id"), "frozen_source_id"
            ),
            "frozen_sha256": drift["frozen_sha256"],
            "current_source_id": _text(
                drift.get("current_source_id"), "current_source_id"
            ),
            "current_sha256": drift["current_sha256"],
            "same_path": drift.get("same_path") is True,
            "hash_mismatch": drift.get("hash_mismatch") is True,
        }
    return {"case_id": case_id, "outcome": outcome, "cards": cards, "drift": drift}


def _key(card: Mapping[str, object]) -> str:
    return json.dumps(card, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _creditable(cards, accepted) -> bool:
    if not cards:
        return False
    accepted_keys = {_key(x) for x in accepted}
    candidate_keys = [_key(x) for x in cards]
    return (
        len(candidate_keys) == len(set(candidate_keys))
        and all(x in accepted_keys for x in candidate_keys)
    )


def _hashes_ok(cards, sources) -> bool:
    return bool(cards) and all(
        (src := sources.get(card["source_id"])) is not None
        and card["source_sha256"] == src["sha256"]
        for card in cards
    )


def _cards_resolve(cards, sources) -> bool:
    return _hashes_ok(cards, sources) and all(
        _resolves(sources[card["source_id"]], card["anchor"])
        for card in cards
    )


def _drift_ok(expected, reported, sources) -> bool:
    if not isinstance(expected, Mapping) or not isinstance(reported, Mapping):
        return False
    frozen = sources[expected["frozen_source_id"]]
    current = sources[expected["current_source_id"]]
    return reported == {
        "frozen_source_id": frozen["id"],
        "frozen_sha256": frozen["sha256"],
        "current_source_id": current["id"],
        "current_sha256": current["sha256"],
        "same_path": frozen["path"] == current["path"],
        "hash_mismatch": frozen["sha256"] != current["sha256"],
    }


def _field_ok(cards, accepted, field) -> bool:
    return bool(cards) and all(
        any(
            target["source_id"] == card["source_id"]
            and target[field] == card[field]
            for target in accepted
        )
        for card in cards
    )


def _state(applicable: bool, incomplete: bool, passed: bool) -> str:
    if not applicable:
        return "NOT_APPLICABLE"
    if incomplete:
        return "INCOMPLETE"
    return "PASS" if passed else "FAIL"


def _score(case, result, sources):
    expected_outcome = case["expected_outcome"]
    accepted = case["expected_cards"] + case["substitutes"]
    if result is None:
        cards, outcome, drift, incomplete = [], None, None, True
    else:
        cards, outcome, drift = result["cards"], result["outcome"], result["drift"]
        incomplete = outcome == "UNKNOWN" and expected_outcome != "UNKNOWN"

    outcome_ok = outcome == expected_outcome
    creditable = _creditable(cards, accepted)
    resolves = _cards_resolve(cards, sources)
    no_forbidden = not any(x["source_id"] in case["forbidden"] for x in cards)
    empty = not cards and drift is None
    drift_match = _drift_ok(case["drift"], drift, sources)

    if incomplete:
        status = "INCOMPLETE"
    elif expected_outcome == "EVIDENCE":
        status = (
            "PASS"
            if outcome_ok and creditable and resolves and no_forbidden and drift is None
            else "FAIL"
        )
    elif expected_outcome == "DRIFT_REPORTED":
        status = "PASS" if outcome_ok and not cards and drift_match else "FAIL"
    else:
        status = "PASS" if outcome_ok and empty else "FAIL"

    evidence = expected_outcome == "EVIDENCE"
    negative = evidence and any(x["polarity"] == "NEGATIVE_BOUNDARY" for x in accepted)
    temporal = case["category"] in {
        "TEMPORAL_CURRENT",
        "TEMPORAL_HISTORICAL",
        "AUTHORITY_STATUS",
    }
    substitute_sources = {x["source_id"] for x in case["substitutes"]}
    substitute_attempted = any(x["source_id"] in substitute_sources for x in cards)
    metrics = {
        "case_outcome_accuracy": _state(True, result is None or incomplete, outcome_ok),
        "exact_source_accuracy": _state(
            evidence, incomplete, _field_ok(cards, accepted, "source_id")
        ),
        "anchor_accuracy": _state(
            evidence,
            incomplete,
            _field_ok(cards, accepted, "anchor") and resolves,
        ),
        "source_hash_accuracy": _state(
            evidence, incomplete, _hashes_ok(cards, sources)
        ),
        "proof_role_accuracy": _state(
            evidence, incomplete, _field_ok(cards, accepted, "proof_role")
        ),
        "negative_boundary_accuracy": _state(
            negative,
            incomplete,
            _field_ok(cards, accepted, "polarity") and creditable,
        ),
        "negative_abstention_accuracy": _state(
            expected_outcome == "ABSTAIN", incomplete, status == "PASS"
        ),
        "temporal_version_accuracy": _state(
            temporal,
            incomplete,
            _field_ok(cards, accepted, "temporal_scope") and creditable,
        ),
        "source_drift_detection_accuracy": _state(
            expected_outcome == "DRIFT_REPORTED", incomplete, drift_match
        ),
        "acceptable_substitute_precision": _state(
            substitute_attempted, incomplete, creditable
        ),
        "vocabulary_shift_case_accuracy": _state(
            case["category"] == "VOCABULARY_SHIFT", incomplete, status == "PASS"
        ),
    }
    return {
        "case_id": case["id"],
        "category": case["category"],
        "status": status,
        "expected_outcome": expected_outcome,
        "reported_outcome": outcome,
        "returned_card_count": len(cards),
        "checks": {
            "outcome_correct": outcome_ok,
            "card_set_creditable": creditable,
            "cards_resolve": resolves,
            "no_forbidden_credit": no_forbidden,
            "drift_exact": drift_match,
            "empty_evidence": empty,
        },
        "metric_states": metrics,
    }


def evaluate_evidence_integrity(
    corpus: Mapping[str, object],
    results: Sequence[Mapping[str, object]],
    *,
    label: str,
) -> dict[str, object]:
    """Score externally supplied Stage-1 evidence outputs against frozen truth."""

    label = _text(label, "label")
    sources, cases, outcomes, metric_names = _validate_corpus(corpus)
    case_ids = {case["id"] for case in cases}
    indexed = {}
    for raw in results:
        if not isinstance(raw, Mapping):
            raise EvidenceIntegrityError("candidate result must be a mapping")
        item = _candidate(raw, outcomes)
        case_id = item["case_id"]
        if case_id not in case_ids:
            raise EvidenceIntegrityError(f"unknown case: {case_id}")
        if case_id in indexed:
            raise EvidenceIntegrityError(f"duplicate result: {case_id}")
        indexed[case_id] = item

    reports = [_score(case, indexed.get(case["id"]), sources) for case in cases]
    supported = set(reports[0]["metric_states"]) if reports else set()
    if set(metric_names) != supported:
        raise EvidenceIntegrityError("corpus metrics do not match scorer metrics")

    named = {
        name: {"pass": 0, "fail": 0, "incomplete": 0, "not_applicable": 0}
        for name in metric_names
    }
    for report in reports:
        for name, state in report["metric_states"].items():
            named[name][state.lower()] += 1

    return {
        "report_version": 1,
        "report_kind": "MAPS_CONTEXT_EVIDENCE_INTEGRITY_REPORT",
        "label": label,
        "corpus_version": corpus["version"],
        "corpus_sha256": _hash(corpus),
        "cases": reports,
        "metrics": {
            "cases": {
                "total": len(reports),
                "pass": sum(x["status"] == "PASS" for x in reports),
                "fail": sum(x["status"] == "FAIL" for x in reports),
                "incomplete": sum(x["status"] == "INCOMPLETE" for x in reports),
            },
            "named": named,
        },
        "promotion": {
            "automatic": False,
            "rule": (
                "passing evidence-integrity evaluation cannot authorize retrieval, "
                "routing, policy, or production changes"
            ),
        },
    }
