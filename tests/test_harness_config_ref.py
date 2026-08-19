from __future__ import annotations

import unittest

from runtime.harness import (
    HarnessConfigRef,
    HarnessService,
    HookDirective,
    HookEvent,
    HookFailurePolicy,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
    OperationResult,
    harness_config_ref,
)


class DummyAdapter:
    def __init__(self, adapter_id: str) -> None:
        self.adapter_id = adapter_id

    def start(self, binding, launch_spec):
        return OperationResult.success("STARTED", "Started.")

    def attach(self, binding, session_ref):
        return OperationResult.success("ATTACHED", "Attached.")

    def send(self, binding, payload):
        return OperationResult.success("SENT", "Sent.")

    def inspect(self, session_ref):
        return OperationResult.success("INSPECTED", "Inspected.")

    def heartbeat(self, binding):
        return OperationResult.success("BEAT", "Beat.")

    def resume(self, binding):
        return OperationResult.success("RESUMED", "Resumed.")

    def stop(self, binding, reason):
        return OperationResult.success("STOPPED", "Stopped.")

    def collect(self, binding):
        return OperationResult.success("COLLECTED", "Collected.")


def _allow(context):
    return HookOutcome(HookDirective.ALLOW)


def _also_allow(context):
    return HookOutcome(HookDirective.ALLOW)


class HarnessConfigRefTests(unittest.TestCase):
    def _service(self, callback=_allow) -> HarnessService:
        hooks = HookRegistry()
        hooks.register(
            HookSpec(
                hook_id="guard-1",
                event=HookEvent.RUN_STARTING,
                callback=callback,
                priority=10,
                side_effect=HookSideEffect.READ_ONLY,
                failure_policy=HookFailurePolicy.FAIL_CLOSED,
            )
        )
        hooks.register(
            HookSpec(
                hook_id="guard-2",
                event=HookEvent.BEFORE_SEND,
                callback=callback,
                priority=50,
                side_effect=HookSideEffect.EVIDENCE_WRITE,
                failure_policy=HookFailurePolicy.CONTINUE,
            )
        )
        return HarnessService([DummyAdapter("hcom"), DummyAdapter("aider")], hooks=hooks)

    def test_deterministic_hash_for_same_configuration(self):
        first = harness_config_ref(self._service())
        second = harness_config_ref(self._service())

        self.assertIsInstance(first, HarnessConfigRef)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.adapter_ids, ("aider", "hcom"))
        self.assertEqual(len(first.hooks), 2)

    def test_different_adapter_set_changes_hash(self):
        baseline = harness_config_ref(self._service())

        hooks = HookRegistry()
        hooks.register(
            HookSpec(
                hook_id="guard-1",
                event=HookEvent.RUN_STARTING,
                callback=_allow,
                priority=10,
            )
        )
        hooks.register(
            HookSpec(
                hook_id="guard-2",
                event=HookEvent.BEFORE_SEND,
                callback=_allow,
                priority=50,
                side_effect=HookSideEffect.EVIDENCE_WRITE,
                failure_policy=HookFailurePolicy.CONTINUE,
            )
        )
        service = HarnessService([DummyAdapter("hcom")], hooks=hooks)
        changed = harness_config_ref(service)

        self.assertNotEqual(baseline.sha256, changed.sha256)

    def test_different_hook_set_changes_hash(self):
        baseline = harness_config_ref(self._service())

        hooks = HookRegistry()
        hooks.register(
            HookSpec(
                hook_id="guard-1",
                event=HookEvent.RUN_STARTING,
                callback=_allow,
                priority=10,
            )
        )
        service = HarnessService([DummyAdapter("hcom"), DummyAdapter("aider")], hooks=hooks)
        changed = harness_config_ref(service)

        self.assertNotEqual(baseline.sha256, changed.sha256)

    def test_hash_excludes_callback_identity(self):
        with_first_callback = harness_config_ref(self._service(callback=_allow))
        with_second_callback = harness_config_ref(self._service(callback=_also_allow))

        self.assertEqual(with_first_callback.sha256, with_second_callback.sha256)

    def test_hooks_are_covered_across_all_events_not_just_one(self):
        ref = harness_config_ref(self._service())
        events = {hook["event"] for hook in ref.hooks}
        self.assertEqual(
            events, {HookEvent.RUN_STARTING.value, HookEvent.BEFORE_SEND.value}
        )

    def test_to_dict_reflects_identity_fields(self):
        ref = harness_config_ref(self._service())
        payload = ref.to_dict()
        self.assertEqual(payload["adapter_ids"], ["aider", "hcom"])
        self.assertEqual(payload["sha256"], ref.sha256)
        self.assertEqual(len(payload["hooks"]), 2)


if __name__ == "__main__":
    unittest.main()
