"""Assemble a ``HarnessService.send()`` payload from a Context Builder plan.

Roadmap 6.22 / ``work/notes/2026-09-06-harness-send-callsite-design.md`` §2c.

This is the *single* component that decides which memory-derived text is
embedded into the outbound message body, so the ``embedded`` flag it writes on
each provenance entry is true by construction (the guard slice-1 residual, §2c;
same shape as SEC3's caller-declared ``destructive: bool``).

Embedding rule (§2c): the renderer only ever embeds ``LOAD``-classed guidance
claims and ``LOAD``-classed Skill bodies into ``message``. Every
``WITHHOLD``/``DENY`` item contributes at most an id/name reference line and is
marked ``embedded=False`` (items dropped from the plan entirely by the trust
gate need no entry at all). Under that rule a correctly-assembled payload is
never denied by the BEFORE_SEND memory-provenance guard -- that guard's deny
path exists to catch an assembler bug or a future looser renderer.

Pure function, no I/O, no store. On any rendering error it raises
``ContextDeliveryRenderError`` so the caller emits **no** payload rather than a
partial one (a partial render could embed a withheld item without its
provenance entry).
"""

from __future__ import annotations

from typing import Any, Mapping

from runtime.policy.memory_provenance_guard import (
    MEMORY_CONTENT_MARKER,
    PROVENANCE_KEY,
)
from runtime.policy.memory_trust_gate import MemoryAdmission, admit_memory_evidence

#: hcom ``send`` intent for a context-delivery message (never a request/ack).
RENDER_INTENT = "inform"


class ContextDeliveryRenderError(ValueError):
    """Raised on any rendering failure; the caller must emit no payload."""


def _advisory_admission(trust_class: Any, *, stale: bool) -> str:
    """Advisory label only -- the guard re-derives and ignores this field."""
    try:
        decision = admit_memory_evidence(
            trust_class, stale=stale, unknown_admission=MemoryAdmission.DENY
        )
        return decision.admission.value
    except Exception:  # noqa: BLE001 - advisory only, never blocks assembly
        return "UNKNOWN"


def _bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _guidance_lines_and_provenance(
    plan: Mapping[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    lines: list[str] = []
    provenance: list[dict[str, Any]] = []

    for item in plan.get("guidance") or ():
        if not isinstance(item, Mapping):
            raise ContextDeliveryRenderError("guidance item is not an object")
        lesson_id = str(item.get("lesson_id") or "").strip()
        claim = str(item.get("claim") or "").strip()
        if not lesson_id or not claim:
            raise ContextDeliveryRenderError(
                "LOAD guidance item missing lesson_id/claim"
            )
        stale = _bool(item.get("stale_trust_metadata"))
        lines.append(f"- [{lesson_id}] {claim}")
        provenance.append(
            {
                "item_id": lesson_id,
                "trust_class": str(item.get("trust_class") or ""),
                "admission": _advisory_admission(
                    item.get("trust_class"), stale=stale
                ),
                "embedded": True,
                "stale": stale,
            }
        )

    for item in plan.get("withheld_guidance") or ():
        if not isinstance(item, Mapping):
            raise ContextDeliveryRenderError("withheld_guidance item is not an object")
        lesson_id = str(item.get("lesson_id") or "").strip()
        if not lesson_id:
            raise ContextDeliveryRenderError("withheld guidance item missing lesson_id")
        reason = str(item.get("withheld_reason") or item.get("reason") or "WITHHELD")
        stale = _bool(item.get("stale_trust_metadata"))
        # Reference only -- never the (absent) claim text.
        lines.append(
            f"- [{lesson_id}] withheld ({reason}); pursue explicitly to load"
        )
        provenance.append(
            {
                "item_id": lesson_id,
                "trust_class": str(item.get("trust_class") or ""),
                "admission": _advisory_admission(
                    item.get("trust_class"), stale=stale
                ),
                "embedded": False,
                "stale": stale,
            }
        )

    return lines, provenance


def _skill_lines_and_provenance(
    plan: Mapping[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    lines: list[str] = []
    provenance: list[dict[str, Any]] = []

    for item in plan.get("skills") or ():
        if not isinstance(item, Mapping):
            raise ContextDeliveryRenderError("skills item is not an object")
        name = str(item.get("name") or "").strip()
        skill_id = str(item.get("skill_id") or "").strip()
        ref = skill_id or name
        if not ref:
            raise ContextDeliveryRenderError("Skill item missing name/skill_id")
        body = item.get("body")
        # A LOAD Skill has its hash-verified SKILL.md body attached; only then
        # is any Skill *text* embedded.
        embedded = isinstance(body, str) and bool(body.strip())
        trust_class = item.get("trust_class")
        if embedded:
            description = str(item.get("description") or "").strip()
            lines.append(f"## Skill: {name} ({skill_id})")
            if description:
                lines.append(description)
            lines.append(str(body).strip())
        else:
            reason = str(item.get("withheld_reason") or "not loaded")
            lines.append(f"- Skill {name} ({skill_id}) withheld ({reason})")
        provenance.append(
            {
                "item_id": ref,
                "trust_class": str(trust_class or ""),
                "admission": _advisory_admission(trust_class, stale=False),
                "embedded": embedded,
                "stale": False,
            }
        )

    return lines, provenance


def _reference_lines(plan: Mapping[str, Any]) -> list[str]:
    """Non-memory, deterministic scaffolding: authority / required / deps /
    boundaries. These carry no memory trust class and contribute no
    provenance entries."""
    lines: list[str] = []

    authority = plan.get("authority") or ()
    if authority:
        lines.append("Authority:")
        for item in authority:
            if isinstance(item, Mapping):
                lines.append(f"- {item.get('path') or item.get('value') or item}")

    required = plan.get("required") or ()
    if required:
        lines.append("Required inputs:")
        for item in required:
            if isinstance(item, Mapping):
                lines.append(
                    f"- {item.get('value')} [{item.get('status')}]"
                )

    dependencies = plan.get("dependencies") or ()
    if dependencies:
        lines.append("Dependencies:")
        for item in dependencies:
            if isinstance(item, Mapping):
                lines.append(
                    f"- {item.get('task_id')} [{item.get('status')}]"
                )

    boundaries = plan.get("boundaries")
    if isinstance(boundaries, Mapping) and boundaries:
        lines.append("Boundaries:")
        for key in sorted(boundaries):
            lines.append(f"- {key}: {boundaries[key]}")

    return lines


def render_context_send_payload(
    context_plan: Mapping[str, Any], *, from_name: str
) -> dict[str, Any]:
    """Turn a ``build_context_plan`` result into a guarded ``send()`` payload.

    Returns the §2c shape:

    * ``message`` -- deterministic text; never embeds WITHHOLD/DENY item text.
    * ``intent`` -- always ``"inform"``.
    * ``from_name`` -- passed through.
    * ``memory_content`` -- ``True`` when the plan carried any memory-like item
      (guidance / withheld_guidance / skills), so the guard's fail-closed
      unverified-provenance branch stays reachable if the annotation is ever
      dropped.
    * ``memory_provenance`` -- one entry ``{item_id, trust_class, admission,
      embedded, stale}`` per plan item whose text or identifier was copied.
    """
    if not isinstance(context_plan, Mapping):
        raise ContextDeliveryRenderError("context_plan must be a mapping")
    from_name = str(from_name or "").strip()
    if not from_name:
        raise ContextDeliveryRenderError("from_name is required")

    task_id = str(context_plan.get("task_id") or "").strip()
    task_revision = str(context_plan.get("task_revision") or "").strip()
    if not task_id:
        raise ContextDeliveryRenderError("context_plan is missing task_id")

    guidance_lines, guidance_prov = _guidance_lines_and_provenance(context_plan)
    skill_lines, skill_prov = _skill_lines_and_provenance(context_plan)
    provenance = [*guidance_prov, *skill_prov]

    body_lines: list[str] = [
        f"MAPS context for task {task_id} (revision {task_revision or 'unknown'})",
    ]
    body_lines.extend(_reference_lines(context_plan))
    if guidance_lines:
        body_lines.append("Guidance:")
        body_lines.extend(guidance_lines)
    if skill_lines:
        body_lines.append("Skills:")
        body_lines.extend(skill_lines)

    message = "\n".join(line for line in body_lines if line is not None).strip()
    if not message:
        raise ContextDeliveryRenderError("rendered an empty message body")

    has_memory = bool(
        (context_plan.get("guidance") or ())
        or (context_plan.get("withheld_guidance") or ())
        or (context_plan.get("skills") or ())
    )

    payload: dict[str, Any] = {
        "message": message,
        "intent": RENDER_INTENT,
        "from_name": from_name,
        PROVENANCE_KEY: provenance,
    }
    if has_memory:
        payload[MEMORY_CONTENT_MARKER] = True
    return payload
