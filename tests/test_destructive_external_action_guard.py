"""Isolated tests for the SEC3 destructive/external action Hook guard.

The guard is deliberately unwired from every production call site (design note
`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`,
Non-goals), so it is exercised directly and through a bare `HookRegistry`.
"""

from pathlib import Path
import unittest

from runtime.harness import HookDirective, HookEvent, HookRegistry
from runtime.harness.hooks import HookEnforcement
from runtime.policy.destructive_action_guard import (
    DestructiveExternalActionGuard,
    register_destructive_external_action_guards,
)


ROOT = Path(__file__).resolve().parents[1]


class DestructiveExternalActionGuardTest(unittest.TestCase):
    def setUp(self):
        self.guard = DestructiveExternalActionGuard()

    def test_enum_member_exists(self):
        self.assertEqual(
            HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION.value,
            "DESTRUCTIVE_EXTERNAL_ACTION",
        )

    def test_missing_both_keys_fails_closed(self):
        outcome = self.guard({})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "CLASSIFICATION_REQUIRED")

    def test_missing_one_key_fails_closed(self):
        outcome = self.guard({"destructive": False})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "CLASSIFICATION_REQUIRED")
        outcome = self.guard({"external": False})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "CLASSIFICATION_REQUIRED")

    def test_non_boolean_classification_is_denied(self):
        for value in ("true", 1, None, [], {}):
            with self.subTest(value=value):
                outcome = self.guard({"destructive": value, "external": False})
                self.assertEqual(outcome.directive, HookDirective.DENY)
                self.assertEqual(
                    outcome.annotations["guard_code"], "CLASSIFICATION_INVALID"
                )

    def test_destructive_true_denies_with_no_authority_signal(self):
        outcome = self.guard({"destructive": True, "external": False})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "ACTION_AUTHORITY_ABSENT")
        self.assertEqual(outcome.annotations["action_classes"], "destructive")

    def test_external_true_denies_with_no_authority_signal(self):
        outcome = self.guard({"destructive": False, "external": True})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "ACTION_AUTHORITY_ABSENT")
        self.assertEqual(outcome.annotations["action_classes"], "external")

    def test_both_true_denies(self):
        outcome = self.guard({"destructive": True, "external": True})
        self.assertEqual(outcome.directive, HookDirective.DENY)
        self.assertEqual(outcome.annotations["guard_code"], "ACTION_AUTHORITY_ABSENT")
        self.assertEqual(outcome.annotations["action_classes"], "destructive,external")

    def test_never_requires_approval(self):
        """No operator-approval mechanism exists for this path yet."""

        for destructive in (True, False):
            for external in (True, False):
                outcome = self.guard(
                    {"destructive": destructive, "external": external}
                )
                self.assertNotEqual(outcome.directive, HookDirective.REQUIRE_APPROVAL)

    def test_both_explicitly_false_allows(self):
        outcome = self.guard({"destructive": False, "external": False})
        self.assertEqual(outcome.directive, HookDirective.ALLOW)
        self.assertEqual(outcome.annotations["guard_code"], "ACTION_NOT_CONSEQUENTIAL")

    def test_extra_context_keys_do_not_change_the_decision(self):
        outcome = self.guard(
            {"destructive": False, "external": False, "operation": "stop"}
        )
        self.assertEqual(outcome.directive, HookDirective.ALLOW)


class DestructiveExternalActionRegistrationTest(unittest.TestCase):
    def test_registration_records_enforcement_on_both_events(self):
        registry = HookRegistry()
        guard = DestructiveExternalActionGuard()
        self.assertFalse(
            registry.has_enforcement(
                HookEvent.BEFORE_DESTRUCTIVE_ACTION,
                HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION,
            )
        )
        register_destructive_external_action_guards(registry, guard)
        for event in (
            HookEvent.BEFORE_DESTRUCTIVE_ACTION,
            HookEvent.BEFORE_EXTERNAL_ACTION,
        ):
            self.assertTrue(
                registry.has_enforcement(
                    event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION
                )
            )
            self.assertFalse(
                registry.has_enforcement(event, HookEnforcement.CANONICAL_RUN)
            )

    def test_registration_rejects_a_foreign_guard(self):
        registry = HookRegistry()

        class Sneaky(DestructiveExternalActionGuard):
            pass

        with self.assertRaises(TypeError):
            register_destructive_external_action_guards(registry, Sneaky())

    def test_registry_run_blocks_an_undeclared_action(self):
        registry = HookRegistry()
        register_destructive_external_action_guards(
            registry, DestructiveExternalActionGuard()
        )
        result = registry.run(HookEvent.BEFORE_DESTRUCTIVE_ACTION, {})
        self.assertFalse(result.permitted)
        self.assertTrue(result.denied)

    def test_registry_run_blocks_a_declared_destructive_action(self):
        registry = HookRegistry()
        register_destructive_external_action_guards(
            registry, DestructiveExternalActionGuard()
        )
        result = registry.run(
            HookEvent.BEFORE_DESTRUCTIVE_ACTION,
            {"destructive": True, "external": False},
        )
        self.assertFalse(result.permitted)

    def test_registry_run_permits_a_non_consequential_action(self):
        registry = HookRegistry()
        register_destructive_external_action_guards(
            registry, DestructiveExternalActionGuard()
        )
        result = registry.run(
            HookEvent.BEFORE_EXTERNAL_ACTION,
            {"destructive": False, "external": False},
        )
        self.assertTrue(result.permitted)


class NoAccidentalProductionWiringTest(unittest.TestCase):
    """The guard and its enforcement member must stay unwired for now.

    Mirrors the "no accidental production wiring" caution used elsewhere in
    this repo: this task builds the guard only. Wiring a first real call site
    is a separate, bounded follow-up, and doing it by accident here would
    silently change live stop/kill behavior.
    """

    ALLOWED_FILES = {
        ROOT / "runtime" / "harness" / "hooks.py",
        ROOT / "runtime" / "policy" / "destructive_action_guard.py",
        ROOT / "runtime" / "policy" / "__init__.py",
    }

    def _runtime_sources(self):
        return sorted(ROOT.joinpath("runtime").rglob("*.py"))

    def test_enforcement_member_is_not_referenced_by_production_code(self):
        offenders = []
        for path in self._runtime_sources():
            if path in self.ALLOWED_FILES:
                continue
            if "DESTRUCTIVE_EXTERNAL_ACTION" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(
            offenders,
            [],
            "DESTRUCTIVE_EXTERNAL_ACTION must stay unwired from production call "
            f"sites until a bounded follow-up wires one: {offenders}",
        )

    def test_guard_is_not_constructed_or_registered_by_production_code(self):
        offenders = []
        for path in self._runtime_sources():
            if path in self.ALLOWED_FILES:
                continue
            text = path.read_text(encoding="utf-8")
            if (
                "DestructiveExternalActionGuard" in text
                or "register_destructive_external_action_guards" in text
            ):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"guard must stay unwired: {offenders}")

    def test_service_gating_helper_was_not_added(self):
        service = ROOT / "runtime" / "harness" / "service.py"
        text = service.read_text(encoding="utf-8")
        self.assertNotIn("DESTRUCTIVE", text)
        self.assertNotIn("destructive", text)


if __name__ == "__main__":
    unittest.main()
