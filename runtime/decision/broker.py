from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping

from .config import DecisionConfig
from .provider import ChoiceDecision, DecisionProvider


@dataclass(frozen=True)
class BrokerDecision:
    selected: str
    evidence: Mapping[str, Any] | None = None


class DecisionBroker:
    """Automatic bounded-judgment broker.

    The broker can influence preference only among choices already supplied by
    deterministic MAPS code. It cannot create permission, eligibility, task
    state, verification evidence, or review approval.
    """

    def __init__(
        self,
        config: DecisionConfig | None = None,
        *,
        provider: DecisionProvider | None = None,
    ) -> None:
        self.config = config or DecisionConfig()
        self.config.validate()
        self.provider = provider or self._build_provider()
        self._cache: dict[str, ChoiceDecision] = {}

    @classmethod
    def from_environment(cls) -> "DecisionBroker":
        return cls(DecisionConfig.from_environment())

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "DecisionBroker":
        return cls(DecisionConfig.from_mapping(value))

    def _build_provider(self) -> DecisionProvider | None:
        if self.config.provider == "off" or self.config.mode == "off":
            return None
        if self.config.provider == "jev":
            from .jev import JevDecisionProvider

            return JevDecisionProvider(model=self.config.model)
        raise ValueError(f"unsupported decision provider: {self.config.provider}")

    @staticmethod
    def _cache_key(
        *,
        decision_type: str,
        state: Mapping[str, Any],
        question: str,
        choices: Mapping[str, str | None],
    ) -> str:
        encoded = json.dumps(
            {
                "decision_type": decision_type,
                "state": state,
                "question": question,
                "choices": choices,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _valid_decision(decision: ChoiceDecision, eligible_ids: set[str]) -> bool:
        if decision.choice not in eligible_ids:
            return False
        try:
            confidence = float(decision.confidence)
            probability_items = list(decision.probabilities.items())
        except (AttributeError, TypeError, ValueError):
            return False
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            return False
        probability_keys = {str(key) for key, _ in probability_items}
        if not probability_keys.issubset(eligible_ids):
            return False
        for _, value in probability_items:
            try:
                probability = float(value)
            except (TypeError, ValueError):
                return False
            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                return False
        return True

    def choose(
        self,
        *,
        decision_type: str,
        state: Mapping[str, Any],
        question: str,
        choices: Mapping[str, str | None],
        deterministic_choice: str,
    ) -> BrokerDecision:
        """Resolve one bounded semantic choice with deterministic fallback."""

        if deterministic_choice not in choices:
            raise ValueError("deterministic_choice must be one of choices")
        if len(choices) <= 1 or self.config.mode == "off" or self.provider is None:
            return BrokerDecision(deterministic_choice)

        provider_name = str(
            getattr(self.provider, "provider_name", self.provider.__class__.__name__)
        )
        cache_key = self._cache_key(
            decision_type=decision_type,
            state=state,
            question=question,
            choices=choices,
        )
        cache_hit = cache_key in self._cache

        try:
            decision = self._cache.get(cache_key)
            if decision is None:
                decision = self.provider.choose(
                    state=state,
                    question=question,
                    choices=choices,
                )
                self._cache[cache_key] = decision
        except Exception as exc:
            return BrokerDecision(
                deterministic_choice,
                {
                    "decision_type": decision_type,
                    "mode": self.config.mode,
                    "provider": provider_name,
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "selected": deterministic_choice,
                    "applied": False,
                    "escalation_recommended": True,
                },
            )

        eligible_ids = set(choices)
        if not self._valid_decision(decision, eligible_ids):
            return BrokerDecision(
                deterministic_choice,
                {
                    "decision_type": decision_type,
                    "mode": self.config.mode,
                    "provider": provider_name,
                    "status": "invalid",
                    "suggested": getattr(decision, "choice", None),
                    "selected": deterministic_choice,
                    "applied": False,
                    "escalation_recommended": True,
                    "cache_hit": cache_hit,
                },
            )

        confidence = float(decision.confidence)
        low_confidence = confidence < self.config.min_confidence
        selected = deterministic_choice
        applied = False
        status = "ok"

        if self.config.mode == "active":
            if low_confidence:
                status = "low_confidence"
            else:
                selected = decision.choice
                applied = True

        return BrokerDecision(
            selected,
            {
                "decision_type": decision_type,
                "mode": self.config.mode,
                "provider": decision.provider or provider_name,
                "model": decision.model,
                "status": status,
                "suggested": decision.choice,
                "selected": selected,
                "applied": applied,
                "confidence": confidence,
                "min_confidence": self.config.min_confidence,
                "probabilities": {
                    str(key): float(value)
                    for key, value in decision.probabilities.items()
                },
                "escalation_recommended": low_confidence,
                "cache_hit": cache_hit,
            },
        )
