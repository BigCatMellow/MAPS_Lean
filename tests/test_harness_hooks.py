import unittest

from runtime.harness.hooks import (
    HookDirective,
    HookEvent,
    HookFailurePolicy,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
)


class HookRegistryTests(unittest.TestCase):
    def test_hooks_run_in_priority_then_registration_order(self):
        calls = []
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "later",
                HookEvent.BEFORE_WRITE,
                lambda ctx: calls.append("later") or HookOutcome(HookDirective.ALLOW),
                priority=20,
            )
        )
        registry.register(
            HookSpec(
                "first",
                HookEvent.BEFORE_WRITE,
                lambda ctx: calls.append("first") or HookOutcome(HookDirective.ALLOW),
                priority=10,
            )
        )
        registry.register(
            HookSpec(
                "same-priority",
                HookEvent.BEFORE_WRITE,
                lambda ctx: calls.append("same-priority") or HookOutcome(HookDirective.ALLOW),
                priority=20,
            )
        )

        result = registry.run(HookEvent.BEFORE_WRITE, {"path": "x.py"})

        self.assertTrue(result.permitted)
        self.assertEqual(calls, ["first", "later", "same-priority"])

    def test_deny_and_require_approval_preserve_all_blocking_reasons(self):
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "scope",
                HookEvent.BEFORE_EXTERNAL_ACTION,
                lambda ctx: HookOutcome(HookDirective.DENY, "Outside task scope."),
            )
        )
        registry.register(
            HookSpec(
                "approval",
                HookEvent.BEFORE_EXTERNAL_ACTION,
                lambda ctx: HookOutcome(
                    HookDirective.REQUIRE_APPROVAL,
                    "Operator approval is required.",
                ),
            )
        )

        result = registry.run(HookEvent.BEFORE_EXTERNAL_ACTION)

        self.assertFalse(result.permitted)
        self.assertTrue(result.denied)
        self.assertTrue(result.requires_approval)
        self.assertEqual(
            result.blocking_reasons,
            ("Outside task scope.", "Operator approval is required."),
        )

    def test_hook_exception_fails_closed_by_default_without_raw_message(self):
        registry = HookRegistry()

        def boom(ctx):
            raise RuntimeError("secret-ish failure detail")

        registry.register(HookSpec("guard", HookEvent.BEFORE_TOOL, boom))
        result = registry.run(HookEvent.BEFORE_TOOL)

        self.assertTrue(result.denied)
        outcome = result.invocations[0].outcome
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertNotIn("secret-ish", outcome.reason)
        self.assertEqual(outcome.annotations["error_type"], "RuntimeError")

    def test_continue_failure_is_annotation_not_permission_grant(self):
        registry = HookRegistry()

        def boom(ctx):
            raise RuntimeError("details")

        registry.register(
            HookSpec(
                "telemetry",
                HookEvent.AFTER_TOOL,
                boom,
                failure_policy=HookFailurePolicy.CONTINUE,
            )
        )
        result = registry.run(HookEvent.AFTER_TOOL)

        self.assertTrue(result.permitted)
        self.assertEqual(
            result.invocations[0].outcome.directive,
            HookDirective.ANNOTATE,
        )

    def test_raise_policy_propagates(self):
        registry = HookRegistry()

        def boom(ctx):
            raise RuntimeError("expected")

        registry.register(
            HookSpec(
                "debug",
                HookEvent.AFTER_TOOL,
                boom,
                failure_policy=HookFailurePolicy.RAISE,
            )
        )
        with self.assertRaises(RuntimeError):
            registry.run(HookEvent.AFTER_TOOL)

    def test_duplicate_hook_ids_are_rejected(self):
        registry = HookRegistry()
        spec = HookSpec(
            "same",
            HookEvent.BEFORE_WRITE,
            lambda ctx: HookOutcome(HookDirective.ALLOW),
        )
        registry.register(spec)
        with self.assertRaises(ValueError):
            registry.register(spec)

    def test_blocking_directives_require_reason(self):
        with self.assertRaises(ValueError):
            HookOutcome(HookDirective.DENY)
        with self.assertRaises(ValueError):
            HookOutcome(HookDirective.REQUIRE_APPROVAL, " ")

    def test_hook_security_enums_are_validated_at_construction(self):
        callback = lambda ctx: HookOutcome(HookDirective.ALLOW)

        with self.assertRaises(TypeError):
            HookSpec("bad-event", "before_write", callback)
        with self.assertRaises(TypeError):
            HookSpec(
                "bad-side-effect",
                HookEvent.BEFORE_WRITE,
                callback,
                side_effect="READ_ONLY",
            )
        with self.assertRaises(TypeError):
            HookSpec(
                "bad-failure-policy",
                HookEvent.BEFORE_WRITE,
                callback,
                failure_policy="FAIL_CLOESD",
            )

    def test_registry_rejects_duck_typed_unvalidated_spec(self):
        class MalformedSpec:
            hook_id = "guard"
            event = HookEvent.BEFORE_TOOL
            callback = staticmethod(lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")))
            priority = 100
            side_effect = HookSideEffect.READ_ONLY
            failure_policy = "FAIL_CLOESD"

        registry = HookRegistry()

        with self.assertRaises(TypeError):
            registry.register(MalformedSpec())
        self.assertEqual(registry.list_for(HookEvent.BEFORE_TOOL), ())

    def test_invalid_callback_directive_fails_closed(self):
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "guard",
                HookEvent.BEFORE_TOOL,
                lambda ctx: HookOutcome("ALLOW"),
            )
        )

        result = registry.run(HookEvent.BEFORE_TOOL)

        self.assertTrue(result.denied)
        self.assertEqual(result.invocations[0].outcome.annotations["error_type"], "TypeError")

    def test_invalid_run_event_is_rejected(self):
        registry = HookRegistry()
        with self.assertRaises(TypeError):
            registry.run("before_tool")

    def test_hook_context_is_top_level_read_only(self):
        registry = HookRegistry()

        def mutate(ctx):
            ctx["new"] = "no"
            return HookOutcome(HookDirective.ALLOW)

        registry.register(HookSpec("readonly", HookEvent.BEFORE_TOOL, mutate))
        result = registry.run(HookEvent.BEFORE_TOOL, {"original": True})

        self.assertTrue(result.denied)
        self.assertEqual(result.invocations[0].outcome.annotations["error_type"], "TypeError")

    def test_hook_context_is_recursively_read_only_across_hooks(self):
        registry = HookRegistry()
        observed = []

        def attempted_mutation(ctx):
            try:
                ctx["binding"]["worker_id"] = "attacker"
            except TypeError:
                pass
            try:
                ctx["details"]["items"].append("injected")
            except AttributeError:
                pass
            return HookOutcome(HookDirective.ALLOW)

        def later_guard(ctx):
            observed.append(
                (
                    ctx["binding"]["worker_id"],
                    tuple(ctx["details"]["items"]),
                )
            )
            return HookOutcome(HookDirective.ALLOW)

        registry.register(
            HookSpec("mutator", HookEvent.BEFORE_SEND, attempted_mutation, priority=1)
        )
        registry.register(
            HookSpec("guard", HookEvent.BEFORE_SEND, later_guard, priority=2)
        )

        result = registry.run(
            HookEvent.BEFORE_SEND,
            {
                "binding": {"worker_id": "worker-1"},
                "details": {"items": ["original"]},
            },
        )

        self.assertTrue(result.permitted)
        self.assertEqual(observed, [("worker-1", ("original",))])

    def test_unsupported_mutable_hook_leaf_fails_closed_before_callbacks(self):
        class MutableLeaf:
            def __init__(self):
                self.values = ["original"]

        leaf = MutableLeaf()
        callback_calls = []
        registry = HookRegistry()

        def mutator(ctx):
            callback_calls.append("mutator")
            ctx["details"]["leaf"].values.append("injected")
            return HookOutcome(HookDirective.ALLOW)

        def later_guard(ctx):
            callback_calls.append("guard")
            return HookOutcome(HookDirective.ALLOW)

        registry.register(HookSpec("mutator", HookEvent.BEFORE_SEND, mutator, priority=1))
        registry.register(HookSpec("guard", HookEvent.BEFORE_SEND, later_guard, priority=2))

        result = registry.run(
            HookEvent.BEFORE_SEND,
            {"details": {"leaf": leaf}},
        )

        self.assertTrue(result.denied)
        self.assertEqual(result.invocations[0].hook_id, "__context_guard__")
        self.assertEqual(result.invocations[0].outcome.annotations["error_type"], "TypeError")
        self.assertEqual(callback_calls, [])
        self.assertEqual(leaf.values, ["original"])

    def test_hook_outcome_annotations_are_recursively_detached_and_read_only(self):
        source = {"nested": [{"value": 1}]}
        outcome = HookOutcome(HookDirective.ANNOTATE, annotations=source)

        source["nested"][0]["value"] = 2
        source["nested"].append({"value": 3})

        self.assertEqual(outcome.annotations["nested"][0]["value"], 1)
        self.assertEqual(len(outcome.annotations["nested"]), 1)
        with self.assertRaises(TypeError):
            outcome.annotations["nested"][0]["value"] = 4
        with self.assertRaises(AttributeError):
            outcome.annotations["nested"].append({"value": 5})


if __name__ == "__main__":
    unittest.main()
