import unittest

from runtime.harness.hooks import (
    HookDirective,
    HookEvent,
    HookFailurePolicy,
    HookOutcome,
    HookRegistry,
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

    def test_hook_context_is_top_level_read_only(self):
        registry = HookRegistry()

        def mutate(ctx):
            ctx["new"] = "no"
            return HookOutcome(HookDirective.ALLOW)

        registry.register(HookSpec("readonly", HookEvent.BEFORE_TOOL, mutate))
        result = registry.run(HookEvent.BEFORE_TOOL, {"original": True})

        self.assertTrue(result.denied)
        self.assertEqual(result.invocations[0].outcome.annotations["error_type"], "TypeError")


if __name__ == "__main__":
    unittest.main()
