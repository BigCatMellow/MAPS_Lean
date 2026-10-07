from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class ChoiceDecision:
    """A provider-neutral bounded choice with confidence evidence."""

    choice: str
    confidence: float
    probabilities: Mapping[str, float]
    provider: str
    model: str | None = None


class DecisionProvider(Protocol):
    """Semantic judgment provider.

    Providers recommend among caller-supplied choices only. They do not grant
    authority, widen eligibility, mutate task state, or prove completion.
    """

    provider_name: str

    def choose(
        self,
        *,
        state: Mapping[str, Any],
        question: str,
        choices: Mapping[str, str | None],
    ) -> ChoiceDecision:
        ...
