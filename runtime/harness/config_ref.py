from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .hooks import HookEvent, HookRegistry


def _canonical_hash(value: object) -> str:
    """Return a stable sha256 hex digest over a JSON-like structure.

    Mirrors ``runtime/run_record.py``'s ``_canonical_hash`` and
    ``runtime/evaluation/regression_case.py``'s ``_canonical_hash``: canonical
    JSON, sorted keys, compact separators, so the same logical configuration
    always produces the same digest regardless of construction order.
    """

    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hook_descriptor(spec: Any) -> dict[str, object]:
    """Project one registered Hook to its declared, hashable identity.

    Deliberately excludes ``spec.callback`` -- Python callables are not
    stable/hashable across processes or even across two equivalent
    definitions of the same function, so the callback itself is never part
    of harness configuration identity. Only the declared metadata that
    governs how the callback participates (event, ordering, effect class,
    failure handling) is included.
    """

    return {
        "hook_id": spec.hook_id,
        "event": spec.event.value,
        "priority": spec.priority,
        "side_effect": spec.side_effect.value,
        "failure_policy": spec.failure_policy.value,
    }


@dataclass(frozen=True, slots=True)
class HarnessConfigRef:
    """Deterministic, versioned identity for one registered harness configuration.

    Represents the set of adapters and Hooks a ``HarnessService`` was
    constructed with -- not any single run's evidence, and not canonical
    persisted state. This is the identity primitive; binding it onto a real
    run manifest at run-start time is separate, future work (see
    ``work/tasks/harness-config-identity-wave10.md``).
    """

    adapter_ids: tuple[str, ...]
    hooks: tuple[dict[str, object], ...]
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter_ids": list(self.adapter_ids),
            "hooks": [dict(hook) for hook in self.hooks],
            "sha256": self.sha256,
        }


def harness_config_ref(service: Any) -> HarnessConfigRef:
    """Build a ``HarnessConfigRef`` from a live ``HarnessService`` instance.

    Reads ``service.adapter_ids`` (already sorted) and, for Hooks, calls
    ``service.hooks.list_for(event)`` for every ``HookEvent`` member so every
    registered Hook is covered, not just one event's worth.
    """

    adapter_ids = tuple(service.adapter_ids)
    registry: HookRegistry = service.hooks

    hook_descriptors: list[dict[str, object]] = []
    for event in HookEvent:
        for spec in registry.list_for(event):
            hook_descriptors.append(_hook_descriptor(spec))

    hook_descriptors.sort(
        key=lambda item: (item["event"], item["hook_id"], item["priority"])
    )
    hooks = tuple(hook_descriptors)

    payload = {
        "adapter_ids": list(adapter_ids),
        "hooks": [dict(hook) for hook in hooks],
    }
    digest = _canonical_hash(payload)

    return HarnessConfigRef(
        adapter_ids=adapter_ids,
        hooks=hooks,
        sha256=digest,
    )
