from __future__ import annotations

from typing import Any, Mapping

from .provider import ChoiceDecision


class JevDecisionProvider:
    """Optional TypeSafe Jev adapter.

    The SDK is imported lazily so MAPS_L core installs remain provider-neutral.
    Install runtime/requirements-jev.txt and set TYPESAFE_API_KEY before using
    this provider. The adapter only returns semantic recommendations; MAPS
    policy remains the authority boundary.
    """

    provider_name = "jev"

    def __init__(self, *, model: str = "jev-latest") -> None:
        self.model = model

    def choose(
        self,
        *,
        state: Mapping[str, Any],
        question: str,
        choices: Mapping[str, str | None],
    ) -> ChoiceDecision:
        try:
            from typesafe_sdk import Choice, TypeSafeClient
        except ImportError as exc:
            raise RuntimeError(
                "Jev adapter requires: python -m pip install "
                "-r runtime/requirements-jev.txt"
            ) from exc

        with TypeSafeClient(model=self.model) as client:
            response = client.system_one(
                state=dict(state),
                questions={
                    "decision": Choice(
                        instructions=question,
                        criteria=dict(choices),
                    )
                },
            )

        answer = response.answers["decision"]
        return ChoiceDecision(
            choice=str(answer.choice),
            confidence=float(answer.confidence),
            probabilities={
                str(key): float(value) for key, value in answer.probabilities.items()
            },
            provider=self.provider_name,
            model=str(response.model),
        )
