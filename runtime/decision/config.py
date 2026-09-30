from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any, Mapping

DECISION_PROVIDERS = {"off", "jev"}
DECISION_MODES = {"off", "shadow", "active"}


@dataclass(frozen=True)
class DecisionConfig:
    """Runtime configuration for bounded semantic judgments.

    Enabling a provider is explicit because provider calls may transmit bounded
    task metadata and may incur external cost. Once enabled, callers do not need
    to remember to invoke the provider; MAPS decision points use the broker
    automatically.
    """

    provider: str = "off"
    mode: str = "off"
    model: str = "jev-latest"
    min_confidence: float = 0.80

    def validate(self) -> None:
        if self.provider not in DECISION_PROVIDERS:
            raise ValueError(f"unknown decision provider: {self.provider}")
        if self.mode not in DECISION_MODES:
            raise ValueError(f"unknown decision mode: {self.mode}")
        if self.provider == "off" and self.mode != "off":
            raise ValueError("decision provider off requires decision mode off")
        if not self.model.strip():
            raise ValueError("decision model cannot be empty")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("decision min_confidence must be between 0 and 1")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "DecisionConfig":
        raw = dict(value or {})
        provider = str(raw.get("provider", "off")).strip().lower() or "off"
        default_mode = "off" if provider == "off" else "shadow"
        config = cls(
            provider=provider,
            mode=str(raw.get("mode", default_mode)).strip().lower() or default_mode,
            model=str(raw.get("model", "jev-latest")).strip() or "jev-latest",
            min_confidence=float(raw.get("min_confidence", 0.80)),
        )
        config.validate()
        return config

    @classmethod
    def from_environment(cls) -> "DecisionConfig":
        provider = os.getenv("MAPS_DECISION_PROVIDER", "off").strip().lower() or "off"
        default_mode = "off" if provider == "off" else "shadow"
        return cls.from_mapping(
            {
                "provider": provider,
                "mode": os.getenv("MAPS_DECISION_MODE", default_mode),
                "model": os.getenv("MAPS_DECISION_MODEL", "jev-latest"),
                "min_confidence": os.getenv("MAPS_DECISION_MIN_CONFIDENCE", "0.80"),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
