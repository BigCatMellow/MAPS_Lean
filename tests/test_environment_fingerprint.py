from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from runtime.environment import (
    CommandResult,
    CompatibilityState,
    NetworkMode,
    ObservationState,
    evaluate_environment_compatibility,
    inspect_local_environment,
    load_environment_spec,
    parse_environment_spec,
    version_satisfies,
)


SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "environment"
    / "specs"
    / "maps-runtime-ci.json"
)


class FakeRunner:
    def __init__(self, *, versions=None, revision="abc123", dirty=False):
        self.versions = {
            "python": "3.12.4",
            "git": "2.45.1",
            "bash": "5.2.26",
        }
        self.versions.update(versions or {})
        self.revision = revision
        self.dirty = dirty

    def __call__(self, argv):
        args = tuple(argv)
        if len(args) == 2 and args[1] == "--version":
            value = self.versions.get(args[0], "MISSING")
            if value == "MISSING":
                return CommandResult(found=False, returncode=None)
            if value is None:
                return CommandResult(found=True, returncode=0, stdout="version unknown")
            return CommandResult(
                found=True,
                returncode=0,
                stdout=f"{args[0]} version {value}",
            )
        if args and args[0] == "git" and args[-2:] == ("rev-parse", "HEAD"):
            return CommandResult(found=True, returncode=0, stdout=self.revision)
        if args and args[0] == "git" and args[-2:] == ("status", "--porcelain"):
            return CommandResult(
                found=True,
                returncode=0,
                stdout=" M changed.txt" if self.dirty else "",
            )
        return CommandResult(found=True, returncode=1, stdout="")


class EnvironmentFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name)
        (self.repo / "runtime").mkdir()
        (self.repo / "runtime" / "requirements.txt").write_text(
            "langgraph\n", encoding="utf-8"
        )
        self.spec = load_environment_spec(SPEC_PATH)

    def fingerprint(
        self,
        *,
        runner=None,
        spec=None,
        network_mode=NetworkMode.REQUIRED_GENERAL,
        allowed_domains=(),
        services=None,
        secrets=None,
        instant=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
    ):
        return inspect_local_environment(
            spec or self.spec,
            repo_root=self.repo,
            command_runner=runner or FakeRunner(),
            network_mode=network_mode,
            allowed_domains=allowed_domains,
            service_availability=services,
            secret_availability=secrets,
            now=lambda: instant,
        )

    def test_version_constraint_support_is_narrow_and_explicit(self):
        self.assertTrue(version_satisfies("3.12.7", "3.12"))
        self.assertTrue(version_satisfies("3.12.7", ">=3.12,<3.13"))
        self.assertFalse(version_satisfies("3.11.9", ">=3.12,<3.13"))
        self.assertIsNone(version_satisfies("3.12.7", "~=3.12"))

    def test_compatible_local_environment(self):
        observed = self.fingerprint()
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.COMPATIBLE)
        self.assertTrue(report.compatible)
        self.assertEqual(report.reasons, ())
        self.assertEqual(report.warnings, ())

    def test_fingerprint_hash_excludes_observation_timestamp(self):
        first = self.fingerprint(
            instant=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        )
        second = self.fingerprint(
            instant=datetime(2026, 8, 15, 13, 0, tzinfo=timezone.utc)
        )
        self.assertNotEqual(first.observed_at, second.observed_at)
        self.assertEqual(first.sha256, second.sha256)

    def test_missing_required_tool_is_incompatible(self):
        observed = self.fingerprint(runner=FakeRunner(versions={"bash": "MISSING"}))
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.INCOMPATIBLE)
        self.assertIn("TOOL_MISSING:bash", report.reasons)

    def test_unknown_required_tool_version_stays_unknown(self):
        observed = self.fingerprint(runner=FakeRunner(versions={"bash": None}))
        self.assertEqual(observed.tools["bash"].state, ObservationState.UNKNOWN)
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.UNKNOWN)
        self.assertIn("TOOL_VERSION_UNKNOWN:bash", report.reasons)

    def test_incompatible_runtime_is_not_treated_as_drift_warning(self):
        observed = self.fingerprint(runner=FakeRunner(versions={"python": "3.11.9"}))
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.INCOMPATIBLE)
        self.assertIn("RUNTIME_INCOMPATIBLE:python", report.reasons)

    def test_dirty_required_worktree_is_drifted(self):
        observed = self.fingerprint(runner=FakeRunner(dirty=True))
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.DRIFTED)
        self.assertIn("WORKTREE_DIRTY", report.reasons)

    def test_unknown_required_network_does_not_become_compatible(self):
        observed = self.fingerprint(network_mode=NetworkMode.UNKNOWN)
        report = evaluate_environment_compatibility(self.spec, observed)
        self.assertEqual(report.state, CompatibilityState.UNKNOWN)
        self.assertIn("NETWORK_MODE_UNKNOWN", report.reasons)

    def test_changed_dependency_input_is_drift_against_reference(self):
        reference = self.fingerprint()
        (self.repo / "runtime" / "requirements.txt").write_text(
            "langgraph\nchanged-package\n", encoding="utf-8"
        )
        observed = self.fingerprint()
        report = evaluate_environment_compatibility(
            self.spec,
            observed,
            reference=reference,
        )
        self.assertEqual(report.state, CompatibilityState.DRIFTED)
        self.assertIn(
            "DEPENDENCY_INPUT_CHANGED:runtime/requirements.txt",
            report.reasons,
        )

    def test_compatible_runtime_patch_change_is_warning_against_reference(self):
        reference = self.fingerprint(runner=FakeRunner(versions={"python": "3.12.4"}))
        observed = self.fingerprint(runner=FakeRunner(versions={"python": "3.12.5"}))
        report = evaluate_environment_compatibility(
            self.spec,
            observed,
            reference=reference,
        )
        self.assertEqual(report.state, CompatibilityState.COMPATIBLE_WITH_WARNINGS)
        self.assertIn("RUNTIME_VERSION_CHANGED:python", report.warnings)

    def test_spec_hash_mismatch_is_explicit_drift(self):
        observed = self.fingerprint()
        data = self.spec.to_dict()
        data["maintenance"]["commands"] = ["python -m compileall runtime"]
        changed_spec = parse_environment_spec(data)
        report = evaluate_environment_compatibility(changed_spec, observed)
        self.assertEqual(report.state, CompatibilityState.DRIFTED)
        self.assertIn("ENVIRONMENT_SPEC_HASH_MISMATCH", report.reasons)

    def test_restricted_network_can_warn_on_broader_access(self):
        data = self.spec.to_dict()
        data["network"] = {
            "mode": "REQUIRED_RESTRICTED",
            "allowed_domains": ["pypi.org"],
        }
        restricted = parse_environment_spec(data)
        observed = self.fingerprint(
            spec=restricted,
            network_mode=NetworkMode.REQUIRED_GENERAL,
        )
        report = evaluate_environment_compatibility(restricted, observed)
        self.assertEqual(report.state, CompatibilityState.COMPATIBLE_WITH_WARNINGS)
        self.assertIn("NETWORK_BROADER_THAN_REQUIRED", report.warnings)

    def test_restricted_network_missing_domain_is_incompatible(self):
        data = self.spec.to_dict()
        data["network"] = {
            "mode": "REQUIRED_RESTRICTED",
            "allowed_domains": ["pypi.org", "files.pythonhosted.org"],
        }
        restricted = parse_environment_spec(data)
        observed = self.fingerprint(
            spec=restricted,
            network_mode=NetworkMode.REQUIRED_RESTRICTED,
            allowed_domains=["pypi.org"],
        )
        report = evaluate_environment_compatibility(restricted, observed)
        self.assertEqual(report.state, CompatibilityState.INCOMPATIBLE)
        self.assertTrue(
            any(reason.startswith("NETWORK_DOMAINS_MISSING:") for reason in report.reasons)
        )

    def test_secret_capability_is_boolean_evidence_not_secret_value(self):
        data = self.spec.to_dict()
        data["secrets"]["required_names"] = ["github-read"]
        secured = parse_environment_spec(data)
        observed = self.fingerprint(spec=secured, secrets={"github-read": True})
        rendered = str(observed.to_dict())
        self.assertIn("github-read", rendered)
        self.assertNotIn("token", rendered.lower())
        report = evaluate_environment_compatibility(secured, observed)
        self.assertEqual(report.state, CompatibilityState.COMPATIBLE)

    def test_missing_secret_capability_is_incompatible(self):
        data = self.spec.to_dict()
        data["secrets"]["required_names"] = ["github-read"]
        secured = parse_environment_spec(data)
        observed = self.fingerprint(spec=secured, secrets={"github-read": False})
        report = evaluate_environment_compatibility(secured, observed)
        self.assertEqual(report.state, CompatibilityState.INCOMPATIBLE)
        self.assertIn("SECRET_CAPABILITY_MISSING:github-read", report.reasons)

    def test_unsupplied_secret_capability_remains_unknown(self):
        data = self.spec.to_dict()
        data["secrets"]["required_names"] = ["github-read"]
        secured = parse_environment_spec(data)
        observed = self.fingerprint(spec=secured)
        report = evaluate_environment_compatibility(secured, observed)
        self.assertEqual(report.state, CompatibilityState.UNKNOWN)
        self.assertIn("SECRET_CAPABILITY_UNKNOWN:github-read", report.reasons)

    def test_undeclared_capability_observation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "undeclared names"):
            self.fingerprint(secrets={"not-declared": True})


if __name__ == "__main__":
    unittest.main()
