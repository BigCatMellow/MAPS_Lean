"""Fail-closed Hook guard over the memory provenance of a `send()` payload.

Implements the first *action-level* seam of roadmap 6.22, per the design note
`work/notes/2026-08-31-memory-trust-tool-call-gate-design.md` (Q3 "Smallest
first seam"). Structural mirror of the SEC3 guard in
`runtime/policy/destructive_action_guard.py`: one callable guard, one
`register_*` composition helper, one enforcement role, registered on an
already-fired `HookEvent` (`BEFORE_SEND`) in
`build_canonical_harness_service` and nowhere else.

What this guard does
--------------------
`HarnessService.send(binding, session_ref, payload)` is the orchestrator
injecting a follow-up message/instruction into a running session -- the
runtime's own "tool call carrying memory-derived content". If that payload
embeds remembered guidance / lesson / Skill-instruction text whose
contributing item was `WITHHOLD`/`DENY`-classed by
`admit_memory_evidence()`, the `send()` is refused before `adapter.send()` is
reached.

The decision is a *projection of `MemoryAdmission` onto `HookDirective`*,
never a new admission table (design Q2):

* `LOAD`                          -> ALLOW
* `WITHHOLD`, item embedded       -> DENY  (its content text is in the payload body)
* `WITHHOLD`, item referenced only-> ALLOW (only an id/name is in the payload)
* `DENY`                          -> DENY
* payload carries a memory-content marker but no provenance annotation -> DENY
  (`MEMORY_PROVENANCE_UNVERIFIED`) -- unannotated memory content cannot be
  proven clean.
* no annotation and no memory-content marker -> ALLOW (`NO_MEMORY_CONTENT`);
  the guard is inert for payloads that never touch memory.

Contract on the payload assembler (design Q4)
---------------------------------------------
The assembler that turns a Context Builder plan into a `send()` payload is
required to attach ``payload["memory_provenance"]`` -- a list of
``{"item_id": str, "trust_class": str, "admission": str, "embedded": bool}``,
one entry per plan item whose text or identifier it copied into the payload.
The guard **re-derives** the admission from ``trust_class`` (+ ``stale``) via
`admit_memory_evidence()` and does *not* trust the assembler's stated
``admission`` field -- the annotation is an identifier + class claim, the
authoritative decision stays in the one pure function (rule 12).

Residual trusted in slice 1 (folded in per #198 non-blocking rec)
----------------------------------------------------------------
Slice 1 TRUSTS the assembler's ``embedded: bool`` flag on each provenance
entry. The guard re-derives the admission verdict via
`admit_memory_evidence()`, but it does **not** itself re-classify whether a
given item's content is embedded in the payload body vs merely referenced by
id/name -- it takes the assembler's word for that. This is the exact same
kind of residual as SEC3's caller-declared ``destructive: bool`` flag. Slice
1 does not attempt to close it; a later slice (with a real production
assembler to reason about) can.

Deliberately NOT in slice 1
---------------------------
* No `BEFORE_TOOL`/`AFTER_TOOL` firing site, no adapter tool-loop
  interception, no new `HookEvent` member (design Q6 MUST-NOT 1).
* No `_require_memory_provenance_enforcement()` fail-closed gate on `send()`
  itself -- that would break every `send()` without the guard, and there is
  no production `send()` caller yet to reason about (MUST-NOT 8).
* No schema change, migration, persisted store, or provenance graph -- the
  annotation lives only on the in-flight payload (MUST-NOT 2).
* DENY-only. `HookDirective.REQUIRE_APPROVAL` is never returned, matching the
  canonical-run guard and the SEC3 destructive-action guard (MUST-NOT 5).
* No inspection or regex-sniffing of the payload *text* -- the decision comes
  only from the annotation + `trust_class` mapping (MUST-NOT 6).
"""

from __future__ import annotations

from typing import Any, Mapping

from runtime.harness import (
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
)
from runtime.harness.hooks import HookEnforcement

from .memory_trust_gate import MemoryAdmission, admit_memory_evidence

# The payload key an assembler sets truthy to declare "this payload body
# contains memory-derived text". Its only role is to make the fail-closed
# `MEMORY_PROVENANCE_UNVERIFIED` branch reachable: a payload that carries
# memory content but forgot the provenance annotation must not pass as clean.
MEMORY_CONTENT_MARKER = "memory_content"

# The provenance annotation the assembler attaches (design Q4).
PROVENANCE_KEY = "memory_provenance"

GUARD_CODE_ALLOW_NO_MEMORY = "NO_MEMORY_CONTENT"
GUARD_CODE_ALLOW_ADMITTED = "MEMORY_PROVENANCE_ADMITTED"
GUARD_CODE_DENIED = "MEMORY_PROVENANCE_DENIED"
GUARD_CODE_UNVERIFIED = "MEMORY_PROVENANCE_UNVERIFIED"
GUARD_CODE_MALFORMED = "MEMORY_PROVENANCE_MALFORMED"


class MemoryProvenanceGuard:
    """Read-only Hook guard: deny a `send()` whose payload embeds untrusted memory.

    Deterministic, no policy engine, no rules DSL, no store. `__call__` reads
    ``context["details"]["payload"]`` and returns exactly one `HookOutcome`.
    Never returns `ALLOW` for a `DENY`-classed contributing item; never returns
    `REQUIRE_APPROVAL`.
    """

    @staticmethod
    def _deny(code: str, reason: str, *, evidence_refs: tuple[str, ...] = ()) -> HookOutcome:
        return HookOutcome(
            HookDirective.DENY,
            reason,
            evidence_refs=evidence_refs,
            annotations={"guard_code": code},
        )

    @staticmethod
    def _payload(context: Mapping[str, Any]) -> Mapping[str, Any] | None:
        details = context.get("details")
        if not isinstance(details, Mapping):
            return None
        payload = details.get("payload")
        return payload if isinstance(payload, Mapping) else None

    def __call__(self, context: Mapping[str, Any]) -> HookOutcome:
        payload = self._payload(context)
        if payload is None:
            # No payload visible at all -> nothing memory-bearing to gate.
            return HookOutcome(
                HookDirective.ALLOW,
                reason="No send payload present to inspect for memory provenance.",
                annotations={"guard_code": GUARD_CODE_ALLOW_NO_MEMORY},
            )

        provenance = payload.get(PROVENANCE_KEY)
        has_marker = bool(payload.get(MEMORY_CONTENT_MARKER))

        if provenance is None:
            if has_marker:
                return self._deny(
                    GUARD_CODE_UNVERIFIED,
                    "Payload declares memory-derived content but carries no "
                    f"'{PROVENANCE_KEY}' annotation; unannotated memory content "
                    "cannot be proven clean.",
                )
            return HookOutcome(
                HookDirective.ALLOW,
                reason="Payload carries no memory-derived content.",
                annotations={"guard_code": GUARD_CODE_ALLOW_NO_MEMORY},
            )

        if not isinstance(provenance, (list, tuple)):
            return self._deny(
                GUARD_CODE_MALFORMED,
                f"'{PROVENANCE_KEY}' must be a list of provenance entries.",
            )

        denied: list[str] = []
        for index, entry in enumerate(provenance):
            if not isinstance(entry, Mapping):
                return self._deny(
                    GUARD_CODE_MALFORMED,
                    f"'{PROVENANCE_KEY}'[{index}] is not a provenance entry object.",
                )

            item_id = entry.get("item_id")
            item_ref = item_id if isinstance(item_id, str) and item_id.strip() else f"#{index}"

            # Fail-closed re-derivation: never trust the entry's stated
            # `admission`. The one authoritative decision procedure is
            # `admit_memory_evidence()`. `unknown_admission=DENY` makes an
            # unresolved/blank/unknown trust class deny outright.
            decision = admit_memory_evidence(
                entry.get("trust_class"),
                stale=entry.get("stale", False),
                unknown_admission=MemoryAdmission.DENY,
            )

            if decision.admission is MemoryAdmission.LOAD:
                continue

            if decision.admission is MemoryAdmission.DENY:
                denied.append(f"{item_ref}:{decision.code}")
                continue

            # WITHHOLD: allowed only if the item is referenced, not embedded.
            # A missing / non-bool `embedded` is itself unproven -> treat as
            # embedded (fail closed).
            embedded = entry.get("embedded")
            if embedded is not True:
                if isinstance(embedded, bool):
                    continue  # explicitly referenced-only
                denied.append(f"{item_ref}:WITHHOLD_EMBEDDING_UNDECLARED")
                continue
            denied.append(f"{item_ref}:WITHHOLD_EMBEDDED")

        if denied:
            return self._deny(
                GUARD_CODE_DENIED,
                "send() payload embeds memory-derived content from item(s) that "
                "are not admissible into an action: "
                + ", ".join(denied)
                + ".",
                evidence_refs=tuple(f"memory_item:{ref}" for ref in denied),
            )

        return HookOutcome(
            HookDirective.ALLOW,
            reason="Every memory-provenance entry on the payload is admissible.",
            annotations={"guard_code": GUARD_CODE_ALLOW_ADMITTED},
        )


def register_memory_provenance_guards(
    registry: HookRegistry,
    guard: MemoryProvenanceGuard,
    *,
    priority: int = 10,
) -> None:
    """Register the fail-closed memory-provenance guard on `BEFORE_SEND`.

    Mirrors the SEC3 destructive-guard registration helper.
    `build_canonical_harness_service` (`runtime/recovery/production.py`) is the
    one production caller. `HarnessService.send()` already fires
    `HookEvent.BEFORE_SEND`; composing this guard changes no live behavior
    because `HarnessService.send()` has no production caller yet (design
    Q1c / §7). (The stale-caller CI check is suppressed on the closing line:
    the bare name `send` also matches unrelated adapter/backend `.send`
    methods, which are not callers of *this* method.)
    """  # noqa: stale-caller-check

    if type(guard) is not MemoryProvenanceGuard:
        raise TypeError("guard must be an exact MemoryProvenanceGuard")

    registry._register_enforcement(
        HookSpec(
            hook_id=f"memory-provenance:{HookEvent.BEFORE_SEND.value}",
            event=HookEvent.BEFORE_SEND,
            callback=guard,
            priority=priority,
            side_effect=HookSideEffect.READ_ONLY,
        ),
        HookEnforcement.MEMORY_PROVENANCE,
    )
