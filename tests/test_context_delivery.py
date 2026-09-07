"""Roadmap 6.22: the context-delivery assembler + `maps run send-context`.

Covers `runtime/context_delivery.py::render_context_send_payload` (the §2c
payload shape + the LOAD-only embedding rule) and the CLI call site
`runtime/cli.py::_dispatch_send_context` (default-off byte-identity, the
opt-in flag guard, and the four fail-closed paths from
`work/notes/2026-09-06-harness-send-callsite-design.md` §2f).

`HarnessService.send()` itself, `MemoryProvenanceGuard`, and the shared
`resolve_harness_binding` helper are exercised, never modified.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from runtime.context_delivery import (
    ContextDeliveryRenderError,
    render_context_send_payload,
)
from runtime.harness.binding_resolution import resolve_harness_binding
from runtime.harness.types import OperationResult
from runtime.policy.memory_provenance_guard import (
    GUARD_CODE_ALLOW_ADMITTED,
    GUARD_CODE_DENIED,
    MemoryProvenanceGuard,
)

from tests.test_cli_run import _RunCliMixin


def _plan(**overrides):
    plan = {
        "task_id": "T-1",
        "task_revision": "rev-abc",
        "authority": [],
        "required": [],
        "guidance": [],
        "withheld_guidance": [],
        "skills": [],
        "dependencies": [],
        "boundaries": {},
        "unresolved": [],
        "coverage": {},
    }
    plan.update(overrides)
    return plan


# --------------------------------------------------------------------------
# A. Assembler unit tests -- render_context_send_payload
# --------------------------------------------------------------------------
class RenderContextSendPayloadTests(unittest.TestCase):
    def test_minimal_shape_no_memory(self):
        payload = render_context_send_payload(_plan(), from_name="tester")
        self.assertEqual(payload["intent"], "inform")
        self.assertEqual(payload["from_name"], "tester")
        self.assertIsInstance(payload["message"], str)
        self.assertTrue(payload["message"])
        self.assertEqual(payload["memory_provenance"], [])
        # No memory-like item -> no marker (guard stays inert-ish / ADMITTED).
        self.assertNotIn("memory_content", payload)

    def test_load_guidance_is_embedded_with_provenance(self):
        payload = render_context_send_payload(
            _plan(
                guidance=[
                    {
                        "lesson_id": "L-load",
                        "claim": "always rebase before merge",
                        "trust_class": "REVIEWED_GUIDANCE",
                    }
                ]
            ),
            from_name="tester",
        )
        self.assertIn("always rebase before merge", payload["message"])
        self.assertTrue(payload["memory_content"])
        (entry,) = payload["memory_provenance"]
        self.assertEqual(entry["item_id"], "L-load")
        self.assertEqual(entry["trust_class"], "REVIEWED_GUIDANCE")
        self.assertIs(entry["embedded"], True)
        self.assertIs(entry["stale"], False)
        self.assertEqual(entry["admission"], "LOAD")

    def test_withheld_guidance_is_referenced_not_embedded(self):
        secret = "this candidate lesson text must never appear"
        payload = render_context_send_payload(
            _plan(
                withheld_guidance=[
                    {
                        "lesson_id": "L-withheld",
                        "reason": "CANDIDATE_NOT_PROMOTED",
                        "withheld_reason": "CANDIDATE_NOT_PROMOTED",
                        "trust_class": "CANDIDATE_LESSON",
                        # a hostile/nonstandard field carrying text -- must be ignored
                        "claim": secret,
                    }
                ]
            ),
            from_name="tester",
        )
        self.assertNotIn(secret, payload["message"])
        self.assertIn("L-withheld", payload["message"])
        (entry,) = payload["memory_provenance"]
        self.assertIs(entry["embedded"], False)
        self.assertEqual(entry["trust_class"], "CANDIDATE_LESSON")

    def test_load_skill_body_embedded_withheld_skill_referenced(self):
        payload = render_context_send_payload(
            _plan(
                skills=[
                    {
                        "skill_id": "S-load",
                        "name": "deploy",
                        "description": "how to deploy",
                        "body": "STEP 1 do the thing",
                        "trust_class": "APPROVED_SKILL",
                    },
                    {
                        "skill_id": "S-wh",
                        "name": "secret-skill",
                        "trust_class": "OBSERVATION",
                        "withheld_reason": "WITHHOLD",
                    },
                ]
            ),
            from_name="tester",
        )
        self.assertIn("STEP 1 do the thing", payload["message"])
        by_id = {e["item_id"]: e for e in payload["memory_provenance"]}
        self.assertIs(by_id["S-load"]["embedded"], True)
        self.assertIs(by_id["S-wh"]["embedded"], False)

    def test_rendering_error_raises_and_yields_no_payload(self):
        with self.assertRaises(ContextDeliveryRenderError):
            render_context_send_payload(
                _plan(guidance=[{"lesson_id": "L-x"}]),  # missing claim
                from_name="tester",
            )
        with self.assertRaises(ContextDeliveryRenderError):
            render_context_send_payload(_plan(), from_name="")


# --------------------------------------------------------------------------
# B. Guard interaction -- a correctly-assembled payload always passes;
#    a deliberately mis-assembled one is denied.
# --------------------------------------------------------------------------
class AssembledPayloadAgainstGuardTests(unittest.TestCase):
    @staticmethod
    def _guard_verdict(payload):
        outcome = MemoryProvenanceGuard()({"details": {"payload": dict(payload)}})
        return outcome.annotations.get("guard_code")

    def test_payload_with_withheld_item_passes_guard(self):
        payload = render_context_send_payload(
            _plan(
                guidance=[
                    {
                        "lesson_id": "L-load",
                        "claim": "keep changes minimal",
                        "trust_class": "REVIEWED_GUIDANCE",
                    }
                ],
                withheld_guidance=[
                    {
                        "lesson_id": "L-withheld",
                        "reason": "CANDIDATE_NOT_PROMOTED",
                        "trust_class": "CANDIDATE_LESSON",
                    }
                ],
            ),
            from_name="tester",
        )
        self.assertEqual(self._guard_verdict(payload), GUARD_CODE_ALLOW_ADMITTED)

    def test_mis_assembled_payload_embedding_denied_skill_is_denied(self):
        # Simulate a looser/buggy renderer that embedded a DENY-classed Skill.
        payload = render_context_send_payload(_plan(), from_name="tester")
        payload["memory_content"] = True
        payload["memory_provenance"] = [
            {
                "item_id": "S-bad",
                "trust_class": "QUARANTINED",
                "admission": "LOAD",  # advisory lie -- guard re-derives
                "embedded": True,
                "stale": False,
            }
        ]
        self.assertEqual(self._guard_verdict(payload), GUARD_CODE_DENIED)


# --------------------------------------------------------------------------
# C. Fake harness for the CLI call-site tests
# --------------------------------------------------------------------------
class _FakeHarnessService:
    def __init__(self, *, result=None, raises=False):
        self._result = result or OperationResult.success(
            "SENT", "message delivered", mutated=True
        )
        self._raises = raises
        self.send_calls = []

    def send(self, binding, session_ref, payload):
        self.send_calls.append((binding, session_ref, payload))
        if self._raises:
            raise RuntimeError("simulated harness failure")
        return self._result


# --------------------------------------------------------------------------
# D. CLI call site -- maps run send-context
# --------------------------------------------------------------------------
class SendContextCliTests(_RunCliMixin):
    def _seed_bound(self):
        task_id, run_id = self.seed_active_run()
        self.assertEqual(self.bind(run_id)[0], 0)
        return task_id, run_id

    def test_default_off_assembles_no_send_no_service(self):
        _task_id, run_id = self._seed_bound()
        with patch(
            "runtime.cli.build_canonical_harness_service",
            side_effect=AssertionError("must not build a HarnessService when off"),
        ) as builder:
            code, payload = self.run_maps(
                "run", "send-context", run_id, "--repo-root", str(self.repo)
            )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["code"], "CONTEXT_PAYLOAD_ASSEMBLED")
        self.assertFalse(payload["delivered"])
        self.assertEqual(payload["payload"]["intent"], "inform")
        builder.assert_not_called()

    def test_deliver_context_requires_enforcement_flags(self):
        _task_id, run_id = self._seed_bound()
        with self.assertRaises(SystemExit) as ctx:
            self.run_maps("run", "send-context", run_id, "--deliver-context")
        self.assertEqual(ctx.exception.code, 2)

    def test_deliver_context_happy_path_exactly_one_send(self):
        _task_id, run_id = self._seed_bound()
        fake = _FakeHarnessService()
        with patch(
            "runtime.cli.build_canonical_harness_service", return_value=fake
        ):
            code, payload = self.run_maps(
                "run", "send-context", run_id,
                "--repo-root", str(self.repo),
                "--deliver-context",
                "--enforce-canonical-run",
                "--harness-project-id", "proj-1",
            )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["code"], "CONTEXT_DELIVERED")
        self.assertTrue(payload["context_delivery"]["ok"])
        self.assertEqual(len(fake.send_calls), 1)
        _binding, _session_ref, sent = fake.send_calls[0]
        self.assertIsInstance(sent["memory_provenance"], list)
        self.assertEqual(sent["intent"], "inform")

    def test_fail_closed_binding_unresolved(self):
        # Active run + manifest, but no bind-session -> lineage not EXPLICIT.
        _task_id, run_id = self.seed_active_run()
        fake = _FakeHarnessService()
        with patch(
            "runtime.cli.build_canonical_harness_service", return_value=fake
        ):
            code, payload = self.run_maps(
                "run", "send-context", run_id,
                "--repo-root", str(self.repo),
                "--deliver-context",
                "--enforce-canonical-run",
                "--harness-project-id", "proj-1",
            )
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "CONTEXT_DELIVERY_FAILED")
        self.assertFalse(payload["context_delivery"]["attempted"])
        self.assertEqual(
            payload["context_delivery"]["reason"], "session_not_durably_bound"
        )
        self.assertEqual(fake.send_calls, [])

    def test_fail_closed_send_denied_no_retry(self):
        _task_id, run_id = self._seed_bound()
        fake = _FakeHarnessService(
            result=OperationResult.failure(
                "HOOK_DENIED", "MEMORY_PROVENANCE_DENIED: withheld item embedded"
            )
        )
        with patch(
            "runtime.cli.build_canonical_harness_service", return_value=fake
        ):
            code, payload = self.run_maps(
                "run", "send-context", run_id,
                "--repo-root", str(self.repo),
                "--deliver-context",
                "--enforce-canonical-run",
                "--harness-project-id", "proj-1",
            )
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "CONTEXT_DELIVERY_FAILED")
        self.assertFalse(payload["context_delivery"]["ok"])
        self.assertEqual(payload["context_delivery"]["code"], "HOOK_DENIED")
        self.assertEqual(len(fake.send_calls), 1)  # no retry

    def test_fail_closed_send_raising_is_caught(self):
        _task_id, run_id = self._seed_bound()
        fake = _FakeHarnessService(raises=True)
        with patch(
            "runtime.cli.build_canonical_harness_service", return_value=fake
        ):
            code, payload = self.run_maps(
                "run", "send-context", run_id,
                "--repo-root", str(self.repo),
                "--deliver-context",
                "--enforce-canonical-run",
                "--harness-project-id", "proj-1",
            )
        self.assertEqual(code, 2)
        self.assertEqual(
            payload["context_delivery"]["code"], "HARNESS_CALL_ERROR"
        )

    def test_run_not_found(self):
        code, payload = self.run_maps("run", "send-context", "run-nope")
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "RUN_NOT_FOUND")


# --------------------------------------------------------------------------
# E. Shared helper factor -- one lineage-resolution path, used by both sites
# --------------------------------------------------------------------------
class ResolveHarnessBindingSharedHelperTests(_RunCliMixin):
    def test_resolves_after_bind_session(self):
        task_id, run_id = self.seed_active_run()
        self.assertEqual(self.bind(run_id)[0], 0)
        binding, session_ref, reason = resolve_harness_binding(
            self.store,
            {"run_id": run_id, "task_id": task_id, "worker_id": "worker-1"},
            "sess-1",
        )
        self.assertEqual(reason, "")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.session_id, "sess-1")
        self.assertEqual(session_ref.session_id, "sess-1")
        self.assertEqual(session_ref.adapter, "hcom")

    def test_unbound_run_returns_reason(self):
        task_id, run_id = self.seed_active_run()
        binding, session_ref, reason = resolve_harness_binding(
            self.store,
            {"run_id": run_id, "task_id": task_id, "worker_id": "worker-1"},
            run_id,
        )
        self.assertIsNone(binding)
        self.assertIsNone(session_ref)
        self.assertEqual(reason, "session_not_durably_bound")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
