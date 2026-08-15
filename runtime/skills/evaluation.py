from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping


class SkillSelectionEvalError(ValueError):
    pass


class SkillSelectionCategory(str, Enum):
    DIRECT = "DIRECT"
    PARAPHRASE = "PARAPHRASE"
    VOCABULARY_SHIFT = "VOCABULARY_SHIFT"
    NEAR_MISS = "NEAR_MISS"
    HARD_NEGATIVE = "HARD_NEGATIVE"
    NO_SKILL = "NO_SKILL"
    MULTI_SKILL = "MULTI_SKILL"
    AMBIGUOUS = "AMBIGUOUS"


class SkillSelectionOutcome(str, Enum):
    SELECT = "SELECT"
    ABSTAIN = "ABSTAIN"
    AMBIGUOUS = "AMBIGUOUS"


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SkillSelectionEvalError(f"{field_name} must be non-empty text")
    return value.strip()


def _skill_names(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise SkillSelectionEvalError(f"{field_name} must be a list of skill names")
    names = tuple(_required_text(item, field_name) for item in value)
    if len(set(names)) != len(names):
        raise SkillSelectionEvalError(f"{field_name} contains duplicate skill names")
    return tuple(sorted(names))


@dataclass(frozen=True, slots=True)
class SkillEvalCandidate:
    name: str
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text(self.name, "candidate.name"))
        object.__setattr__(
            self,
            "description",
            _required_text(self.description, "candidate.description"),
        )


@dataclass(frozen=True, slots=True)
class SkillSelectionCase:
    case_id: str
    category: SkillSelectionCategory
    task: str
    expected_outcome: SkillSelectionOutcome
    expected_skills: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _required_text(self.case_id, "case_id"))
        object.__setattr__(self, "task", _required_text(self.task, "task"))
        object.__setattr__(self, "expected_skills", tuple(sorted(self.expected_skills)))
        if self.expected_outcome == SkillSelectionOutcome.ABSTAIN and self.expected_skills:
            raise SkillSelectionEvalError("ABSTAIN cases cannot name expected skills")
        if self.expected_outcome in {
            SkillSelectionOutcome.SELECT,
            SkillSelectionOutcome.AMBIGUOUS,
        } and not self.expected_skills:
            raise SkillSelectionEvalError(
                f"{self.expected_outcome.value} cases require expected skills"
            )
        if self.category == SkillSelectionCategory.AMBIGUOUS:
            if self.expected_outcome != SkillSelectionOutcome.AMBIGUOUS:
                raise SkillSelectionEvalError(
                    "AMBIGUOUS category must expect AMBIGUOUS outcome"
                )
            if len(self.expected_skills) < 2:
                raise SkillSelectionEvalError(
                    "AMBIGUOUS cases must identify at least two implicated skills"
                )


@dataclass(frozen=True, slots=True)
class SkillSelectionCorpus:
    version: str
    candidates: tuple[SkillEvalCandidate, ...]
    cases: tuple[SkillSelectionCase, ...]
    sha256: str

    @property
    def candidate_names(self) -> tuple[str, ...]:
        return tuple(candidate.name for candidate in self.candidates)

    def case(self, case_id: str) -> SkillSelectionCase:
        target = _required_text(case_id, "case_id")
        for case in self.cases:
            if case.case_id == target:
                return case
        raise SkillSelectionEvalError(f"unknown case_id: {target}")


@dataclass(frozen=True, slots=True)
class SkillSelectionPrediction:
    case_id: str
    outcome: SkillSelectionOutcome
    selected_skills: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _required_text(self.case_id, "case_id"))
        object.__setattr__(self, "selected_skills", tuple(sorted(self.selected_skills)))
        if len(set(self.selected_skills)) != len(self.selected_skills):
            raise SkillSelectionEvalError("prediction contains duplicate skill names")
        if self.outcome == SkillSelectionOutcome.ABSTAIN and self.selected_skills:
            raise SkillSelectionEvalError("ABSTAIN prediction cannot select skills")
        if self.outcome in {
            SkillSelectionOutcome.SELECT,
            SkillSelectionOutcome.AMBIGUOUS,
        } and not self.selected_skills:
            raise SkillSelectionEvalError(
                f"{self.outcome.value} prediction requires selected skills"
            )


@dataclass(frozen=True, slots=True)
class SkillSelectionCaseResult:
    case_id: str
    category: SkillSelectionCategory
    expected_outcome: SkillSelectionOutcome
    predicted_outcome: SkillSelectionOutcome
    expected_skills: tuple[str, ...]
    predicted_skills: tuple[str, ...]
    exact: bool


@dataclass(frozen=True, slots=True)
class SkillSelectionEvalReport:
    corpus_sha256: str
    total_cases: int
    exact_cases: int
    exact_rate: float
    selection_precision: float
    selection_recall: float
    selection_f1: float
    abstention_accuracy: float | None
    ambiguity_accuracy: float | None
    false_activation_cases: int
    missed_activation_cases: int
    ambiguity_misses: int
    category_accuracy: Mapping[str, float]
    case_results: tuple[SkillSelectionCaseResult, ...] = field(repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "category_accuracy",
            MappingProxyType(dict(self.category_accuracy)),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "corpus_sha256": self.corpus_sha256,
            "total_cases": self.total_cases,
            "exact_cases": self.exact_cases,
            "exact_rate": self.exact_rate,
            "selection_precision": self.selection_precision,
            "selection_recall": self.selection_recall,
            "selection_f1": self.selection_f1,
            "abstention_accuracy": self.abstention_accuracy,
            "ambiguity_accuracy": self.ambiguity_accuracy,
            "false_activation_cases": self.false_activation_cases,
            "missed_activation_cases": self.missed_activation_cases,
            "ambiguity_misses": self.ambiguity_misses,
            "category_accuracy": dict(self.category_accuracy),
            "cases": [
                {
                    "case_id": item.case_id,
                    "category": item.category.value,
                    "expected_outcome": item.expected_outcome.value,
                    "predicted_outcome": item.predicted_outcome.value,
                    "expected_skills": list(item.expected_skills),
                    "predicted_skills": list(item.predicted_skills),
                    "exact": item.exact,
                }
                for item in self.case_results
            ],
        }


def load_skill_selection_corpus(path: str | Path) -> SkillSelectionCorpus:
    corpus_path = Path(path)
    try:
        raw = json.loads(corpus_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillSelectionEvalError(f"cannot load selection corpus: {exc}") from exc
    if not isinstance(raw, dict):
        raise SkillSelectionEvalError("selection corpus root must be an object")

    version = _required_text(raw.get("version"), "version")
    raw_candidates = raw.get("candidates")
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise SkillSelectionEvalError("candidates must be a non-empty list")
    candidates: list[SkillEvalCandidate] = []
    for index, item in enumerate(raw_candidates):
        if not isinstance(item, dict):
            raise SkillSelectionEvalError(f"candidate {index} must be an object")
        candidates.append(
            SkillEvalCandidate(
                name=_required_text(item.get("name"), f"candidate[{index}].name"),
                description=_required_text(
                    item.get("description"), f"candidate[{index}].description"
                ),
            )
        )
    candidate_names = [candidate.name for candidate in candidates]
    if len(set(candidate_names)) != len(candidate_names):
        raise SkillSelectionEvalError("candidate names must be unique")
    known = set(candidate_names)

    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise SkillSelectionEvalError("cases must be a non-empty list")
    cases: list[SkillSelectionCase] = []
    seen_case_ids: set[str] = set()
    for index, item in enumerate(raw_cases):
        if not isinstance(item, dict):
            raise SkillSelectionEvalError(f"case {index} must be an object")
        case_id = _required_text(item.get("id"), f"case[{index}].id")
        if case_id in seen_case_ids:
            raise SkillSelectionEvalError(f"duplicate case id: {case_id}")
        seen_case_ids.add(case_id)
        try:
            category = SkillSelectionCategory(
                _required_text(item.get("category"), f"case[{index}].category")
            )
            outcome = SkillSelectionOutcome(
                _required_text(
                    item.get("expected_outcome"),
                    f"case[{index}].expected_outcome",
                )
            )
        except ValueError as exc:
            raise SkillSelectionEvalError(str(exc)) from exc
        expected_skills = _skill_names(
            item.get("expected_skills", []),
            f"case[{index}].expected_skills",
        )
        unknown = sorted(set(expected_skills) - known)
        if unknown:
            raise SkillSelectionEvalError(
                f"case {case_id} references unknown skills: {', '.join(unknown)}"
            )
        note = item.get("note", "")
        if not isinstance(note, str):
            raise SkillSelectionEvalError(f"case[{index}].note must be text")
        cases.append(
            SkillSelectionCase(
                case_id=case_id,
                category=category,
                task=_required_text(item.get("task"), f"case[{index}].task"),
                expected_outcome=outcome,
                expected_skills=expected_skills,
                note=note.strip(),
            )
        )

    canonical = json.dumps(
        raw,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return SkillSelectionCorpus(
        version=version,
        candidates=tuple(candidates),
        cases=tuple(cases),
        sha256=hashlib.sha256(canonical).hexdigest(),
    )


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate_skill_selection(
    corpus: SkillSelectionCorpus,
    predictions: Iterable[SkillSelectionPrediction],
) -> SkillSelectionEvalReport:
    by_case: dict[str, SkillSelectionPrediction] = {}
    known_skills = set(corpus.candidate_names)
    for prediction in predictions:
        if prediction.case_id in by_case:
            raise SkillSelectionEvalError(
                f"duplicate prediction for case: {prediction.case_id}"
            )
        try:
            corpus.case(prediction.case_id)
        except SkillSelectionEvalError as exc:
            raise SkillSelectionEvalError(
                f"prediction references {prediction.case_id!r}, which is not in corpus"
            ) from exc
        unknown = sorted(set(prediction.selected_skills) - known_skills)
        if unknown:
            raise SkillSelectionEvalError(
                "prediction selects unknown skills: " + ", ".join(unknown)
            )
        by_case[prediction.case_id] = prediction

    missing = [case.case_id for case in corpus.cases if case.case_id not in by_case]
    if missing:
        raise SkillSelectionEvalError(
            "missing predictions for cases: " + ", ".join(missing)
        )

    results: list[SkillSelectionCaseResult] = []
    true_positive = false_positive = false_negative = 0
    false_activation_cases = 0
    missed_activation_cases = 0
    ambiguity_misses = 0
    abstain_total = abstain_correct = 0
    ambiguous_total = ambiguous_correct = 0
    category_totals: dict[str, int] = {}
    category_correct: dict[str, int] = {}

    for case in corpus.cases:
        prediction = by_case[case.case_id]
        expected = set(case.expected_skills)
        predicted = set(prediction.selected_skills)
        exact = (
            prediction.outcome == case.expected_outcome
            and predicted == expected
        )
        results.append(
            SkillSelectionCaseResult(
                case_id=case.case_id,
                category=case.category,
                expected_outcome=case.expected_outcome,
                predicted_outcome=prediction.outcome,
                expected_skills=case.expected_skills,
                predicted_skills=prediction.selected_skills,
                exact=exact,
            )
        )

        category_totals[case.category.value] = (
            category_totals.get(case.category.value, 0) + 1
        )
        if exact:
            category_correct[case.category.value] = (
                category_correct.get(case.category.value, 0) + 1
            )

        if case.expected_outcome == SkillSelectionOutcome.SELECT:
            true_positive += len(expected & predicted)
            false_positive += len(predicted - expected)
            false_negative += len(expected - predicted)
            if prediction.outcome != SkillSelectionOutcome.SELECT or not predicted:
                missed_activation_cases += 1
        elif case.expected_outcome == SkillSelectionOutcome.ABSTAIN:
            abstain_total += 1
            if prediction.outcome == SkillSelectionOutcome.ABSTAIN and not predicted:
                abstain_correct += 1
            if prediction.outcome == SkillSelectionOutcome.SELECT and predicted:
                false_activation_cases += 1
        else:
            ambiguous_total += 1
            if exact:
                ambiguous_correct += 1
            else:
                ambiguity_misses += 1

    precision = _ratio(true_positive, true_positive + false_positive)
    recall = _ratio(true_positive, true_positive + false_negative)
    f1 = _ratio(2 * precision * recall, precision + recall) if precision + recall else 0.0
    exact_cases = sum(1 for result in results if result.exact)

    return SkillSelectionEvalReport(
        corpus_sha256=corpus.sha256,
        total_cases=len(results),
        exact_cases=exact_cases,
        exact_rate=_ratio(exact_cases, len(results)),
        selection_precision=precision,
        selection_recall=recall,
        selection_f1=f1,
        abstention_accuracy=(
            _ratio(abstain_correct, abstain_total) if abstain_total else None
        ),
        ambiguity_accuracy=(
            _ratio(ambiguous_correct, ambiguous_total) if ambiguous_total else None
        ),
        false_activation_cases=false_activation_cases,
        missed_activation_cases=missed_activation_cases,
        ambiguity_misses=ambiguity_misses,
        category_accuracy={
            category: _ratio(category_correct.get(category, 0), total)
            for category, total in sorted(category_totals.items())
        },
        case_results=tuple(results),
    )
