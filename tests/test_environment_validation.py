from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.environment import (
    CommandOutcome,
    ValidationTierError,
    load_environment_spec,
    make_validation_hook,
    run_validation_tier,
)
from runtime.harness.hooks import HookDirective, HookEvent, HookRegistry, HookSpec

SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "environment"
    / "specs"
    / "maps-runtime-ci.json"
)


def _passing_executor(command: str, repo_root: Path) -> CommandOutcome:
    return CommandOutcome(command=command, found=True, returncode=0, output="ok")


def _failing_executor(fail_on: str):
    def _executor(command: str, repo_root: Path) -> CommandOutcome:
        if command == fail_on:
            return CommandOutcome(
                command=command, found=True, returncode=1, output="secret=sk-live-abcdef1234567890"
            )
        return CommandOutcome(command=command, found=True, returncode=0, output="ok")

    return _executor


class RunValidationTierTests(unittest.TestCase):
    def setUp(self):
        self.spec = load_environment_spec(SPEC_PATH)
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_unknown_tier_is_rejected(self):
        with self.assertRaises(ValidationTierError):
            run_validation_tier(self.spec, "extreme", repo_root=self.tmp.name)

    def test_all_commands_passing_reports_passed(self):
        result = run_validation_tier(
            self.spec, "quick", repo_root=self.tmp.name, executor=_passing_executor
        )
        self.assertTrue(result.passed)
        self.assertEqual(len(result.ran), len(self.spec.validation.quick))
        self.assertEqual(result.skipped, ())
        self.assertEqual(result.environment_spec_hash, self.spec.sha256)

    def test_stops_at_first_failing_command_and_records_skipped(self):
        first_command = self.spec.validation.quick[0]
        result = run_validation_tier(
            self.spec,
            "quick",
            repo_root=self.tmp.name,
            executor=_failing_executor(first_command),
        )
        self.assertFalse(result.passed)
        self.assertEqual(len(result.ran), 1)
        self.assertEqual(result.skipped, self.spec.validation.quick[1:])

    def test_failing_command_output_is_redacted_before_being_kept_as_evidence(self):
        first_command = self.spec.validation.quick[0]
        result = run_validation_tier(
            self.spec,
            "quick",
            repo_root=self.tmp.name,
            executor=_failing_executor(first_command),
        )
        self.assertNotIn("sk-live-abcdef1234567890", result.ran[0].output)
        self.assertIn("REDACTED", result.ran[0].output)

    def test_operation_result_reflects_pass_and_fail(self):
        passing = run_validation_tier(
            self.spec, "quick", repo_root=self.tmp.name, executor=_passing_executor
        )
        self.assertTrue(passing.to_operation_result().ok)

        first_command = self.spec.validation.quick[0]
        failing = run_validation_tier(
            self.spec,
            "quick",
            repo_root=self.tmp.name,
            executor=_failing_executor(first_command),
        )
        failure_result = failing.to_operation_result()
        self.assertFalse(failure_result.ok)
        self.assertEqual(failure_result.code, "VALIDATION_FAILED")


class ValidationHookTests(unittest.TestCase):
    def setUp(self):
        self.spec = load_environment_spec(SPEC_PATH)
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_hook_allows_when_tier_passes(self):
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "quick-validation",
                HookEvent.AFTER_WRITE,
                make_validation_hook(
                    self.spec,
                    "quick",
                    repo_root=self.tmp.name,
                    executor=_passing_executor,
                ),
            )
        )
        result = registry.run(HookEvent.AFTER_WRITE)
        self.assertTrue(result.permitted)

    def test_hook_denies_with_reason_when_tier_fails(self):
        first_command = self.spec.validation.quick[0]
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "quick-validation",
                HookEvent.AFTER_WRITE,
                make_validation_hook(
                    self.spec,
                    "quick",
                    repo_root=self.tmp.name,
                    executor=_failing_executor(first_command),
                ),
            )
        )
        result = registry.run(HookEvent.AFTER_WRITE)
        self.assertFalse(result.permitted)
        self.assertTrue(result.denied)
        self.assertIn(first_command, result.blocking_reasons[0])

    def test_hook_uses_declared_tier_not_a_different_one(self):
        # "full" tier's first command differs from "quick"'s; failing "full"
        # while "quick" passes proves the hook actually reads the requested
        # tier's own command list rather than an arbitrary one.
        full_first = self.spec.validation.full[0]
        registry = HookRegistry()
        registry.register(
            HookSpec(
                "full-validation",
                HookEvent.AFTER_WRITE,
                make_validation_hook(
                    self.spec,
                    "full",
                    repo_root=self.tmp.name,
                    executor=_failing_executor(full_first),
                ),
            )
        )
        result = registry.run(HookEvent.AFTER_WRITE)
        self.assertTrue(result.denied)


if __name__ == "__main__":
    unittest.main()
