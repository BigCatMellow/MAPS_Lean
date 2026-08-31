"""Tests for the 6.22 slice-1 memory-provenance Hook guard.

Covers the design note
`work/notes/2026-08-31-memory-trust-tool-call-gate-design.md` (Q3 "Smallest
first seam"): `MemoryProvenanceGuard` on the already-fired
`HookEvent.BEFORE_SEND`, projecting `admit_memory_evidence()`'s
`MemoryAdmission` onto a `HookDirective` over a `send()` payload's
`memory_provenance` annotation.

The guard TRUSTS the assembler's `embedded: bool` flag per entry (it
re-derives the admission verdict, not the embedded/referenced split) -- the
same residual as SEC3's `destructive: bool`. Tested here as a documented
contract, not closed.
"""

from pathlib import Path
import tempfile
import unittest

from runtime.harness import (
    ExecutionBinding,
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
    OperationResult,
    SessionRef,
)
from runtime.harness.hooks import HookEnforcement
from runtime.harness.service import HarnessService
from runtime.policy.memory_provenance_guard import (
    MemoryProvenanceGuard,
    register_memory_provenance_guards,
)

ROOT = Path(__file__).resolve().parents[1]


def _ctx(payload):
    return {"operation": "send", "adapter_id": "hcom", "details": {"payload": payload}}


def _entry(trust_class, *, embedded, item_id="item-1", admission="LOAD", stale=False):
    return {
        "item_id": item_id,
        "trust_class": trust_class,
        "admission": admission,
        "embedded": embedded,
        "stale": stale,
    }


class ProjectionMatrixTest(unittest.TestCase):
    def setUp(self):
        self.guard = MemoryProvenanceGuard()

    def test_load_class_item_allows(self):
        outcome = self.guard(_ctx({"memory_provenance": [_entry("REVIEWED_GUIDANCE", embedded=True)]}))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_ADMITTED")

    def test_embedded_withhold_item_denies(self):
        outcome = self.guard(_ctx({"memory_provenance": [_entry("OBSERVATION", embedded=True)]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_DENIED")

    def test_referenced_only_withhold_item_allows(self):
        outcome = self.guard(_ctx({"memory_provenance": [_entry("OBSERVATION", embedded=False)]}))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_ADMITTED")

    def test_deny_class_item_denies_even_when_only_referenced(self):
        outcome = self.guard(_ctx({"memory_provenance": [_entry("QUARANTINED", embedded=False)]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_DENIED")

    def test_decision_is_re_derived_not_trusted_from_the_annotation(self):
        # Annotation lies: it claims admission=LOAD for a QUARANTINED item.
        entry = _entry("QUARANTINED", embedded=True, admission="LOAD")
        outcome = self.guard(_ctx({"memory_provenance": [entry]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertIn("item-1", " ".join(outcome.evidence_refs))

    def test_stale_demotes_load_to_withhold_then_embedded_denies(self):
        entry = _entry("REVIEWED_GUIDANCE", embedded=True, stale=True)
        outcome = self.guard(_ctx({"memory_provenance": [entry]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)

    def test_unknown_trust_class_denies_fail_closed(self):
        entry = _entry("not-a-real-class", embedded=False)
        outcome = self.guard(_ctx({"memory_provenance": [entry]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)

    def test_missing_embedded_flag_on_withhold_denies_fail_closed(self):
        entry = {"item_id": "x", "trust_class": "OBSERVATION"}
        outcome = self.guard(_ctx({"memory_provenance": [entry]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)

    def test_never_returns_require_approval(self):
        for tc in ("QUARANTINED", "OBSERVATION", "REVIEWED_GUIDANCE", "bogus"):
            for emb in (True, False):
                outcome = self.guard(_ctx({"memory_provenance": [_entry(tc, embedded=emb)]}))
                self.assertNotEqual(outcome.directive, HookDirective.REQUIRE_APPROVAL)


class AnnotationPresenceTest(unittest.TestCase):
    def setUp(self):
        self.guard = MemoryProvenanceGuard()

    def test_memory_bearing_payload_with_no_annotation_is_unverified(self):
        outcome = self.guard(_ctx({"memory_content": True, "body": "remembered: ..."}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_UNVERIFIED")

    def test_non_memory_payload_allows_inert(self):
        outcome = self.guard(_ctx({"body": "plain instruction"}))
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(outcome.annotations["guard_code"], "NO_MEMORY_CONTENT")

    def test_no_payload_at_all_allows(self):
        outcome = self.guard({"operation": "send", "adapter_id": "hcom"})
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(outcome.annotations["guard_code"], "NO_MEMORY_CONTENT")

    def test_malformed_provenance_container_denies(self):
        outcome = self.guard(_ctx({"memory_provenance": "OBSERVATION"}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_MALFORMED")

    def test_malformed_provenance_entry_denies(self):
        outcome = self.guard(_ctx({"memory_provenance": ["OBSERVATION"]}))
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "MEMORY_PROVENANCE_MALFORMED")


class RegistrationTest(unittest.TestCase):
    def test_enum_member_exists(self):
        self.assertEqual(HookEnforcement.MEMORY_PROVENANCE.value, "MEMORY_PROVENANCE")

    def test_register_requires_exact_type(self):
        registry = HookRegistry()
        with self.assertRaises(TypeError):
            register_memory_provenance_guards(registry, object())

        class _Sub(MemoryProvenanceGuard):
            pass

        with self.assertRaises(TypeError):
            register_memory_provenance_guards(registry, _Sub())

    def test_register_binds_the_enforcement_role_on_before_send(self):
        registry = HookRegistry()
        register_memory_provenance_guards(registry, MemoryProvenanceGuard())
        self.assertTrue(
            registry.has_enforcement(
                HookEvent.BEFORE_SEND, HookEnforcement.MEMORY_PROVENANCE
            )
        )


class GuardNameIsolationTest(unittest.TestCase):
    """`MemoryProvenanceGuard` / `register_memory_provenance_guards` must stay
    confined to their module + `__init__` + the one composition root, exactly
    like the SEC3 guard's isolation test."""

    def _runtime_sources(self):
        return sorted(ROOT.joinpath("runtime").rglob("*.py"))

    def test_names_appear_in_no_other_runtime_source(self):
        allowed = {
            ROOT / "runtime" / "policy" / "memory_provenance_guard.py",
            ROOT / "runtime" / "policy" / "__init__.py",
            ROOT / "runtime" / "recovery" / "production.py",
        }
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path not in allowed
            and (
                "MemoryProvenanceGuard" in path.read_text(encoding="utf-8")
                or "register_memory_provenance_guards" in path.read_text(encoding="utf-8")
            )
        ]
        self.assertEqual(offenders, [])

    def test_enforcement_member_confined(self):
        allowed = {
            ROOT / "runtime" / "harness" / "hooks.py",
            ROOT / "runtime" / "policy" / "memory_provenance_guard.py",
        }
        offenders = [
            str(path.relative_to(ROOT))
            for path in self._runtime_sources()
            if path not in allowed
            and "MEMORY_PROVENANCE" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])


class _RecordingAdapter:
    adapter_id = "hcom"

    def __init__(self):
        self.sends = []

    def send(self, binding, payload):
        self.sends.append((binding.run_id, dict(payload)))
        return OperationResult.success("SENT", "Sent.", mutated=True)


class ComposedServiceSendTest(unittest.TestCase):
    """A composed `HarnessService.send()` gates on the memory-provenance guard.

    A permissive canonical-run enforcement shim is registered only to satisfy
    `_require_canonical_enforcement(BEFORE_SEND)`; the memory-provenance guard
    is the one that decides here.
    """

    def _registry(self):
        registry = HookRegistry()
        registry._register_enforcement(
            HookSpec(
                hook_id="test-canonical-shim",
                event=HookEvent.BEFORE_SEND,
                callback=lambda ctx: HookOutcome(HookDirective.ALLOW, "shim"),
                priority=1,
                side_effect=HookSideEffect.READ_ONLY,
            ),
            HookEnforcement.CANONICAL_RUN,
        )
        register_memory_provenance_guards(registry, MemoryProvenanceGuard())
        return registry

    def _binding(self):
        return ExecutionBinding(
            task_id="TASK-1",
            run_id="RUN-1",
            worker_id="worker-1",
            task_revision="rev-1",
            project_id="proj-1",
            session_id="sess-1",
        )

    def _ref(self):
        return SessionRef(
            session_id="sess-1",
            worker_id="worker-1",
            adapter="hcom",
            project_id="proj-1",
            remote_ref="s-1",
        )

    def test_synthetic_deny_classed_embedded_item_blocks_the_send(self):
        adapter = _RecordingAdapter()
        service = HarnessService([adapter], hooks=self._registry())
        payload = {
            "memory_content": True,
            "memory_provenance": [_entry("QUARANTINED", embedded=True, item_id="lesson-9")],
        }
        result = service.send(self._binding(), self._ref(), payload)
        self.assertEqual(result.code, "HOOK_DENIED")
        self.assertIn("lesson-9", " ".join(result.data["blocking_reasons"]))
        self.assertEqual(adapter.sends, [])

    def test_clean_payload_reaches_the_adapter(self):
        adapter = _RecordingAdapter()
        service = HarnessService([adapter], hooks=self._registry())
        payload = {"memory_provenance": [_entry("REVIEWED_GUIDANCE", embedded=True)]}
        result = service.send(self._binding(), self._ref(), payload)
        self.assertTrue(result.ok, result.code)
        self.assertEqual(len(adapter.sends), 1)


if __name__ == "__main__":
    unittest.main()
