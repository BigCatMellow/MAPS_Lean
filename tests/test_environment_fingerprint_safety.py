from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.environment import inspect_local_environment, parse_environment_spec
from runtime.environment.fingerprint import inspect_local_environment as direct_inspect_local_environment
from runtime.environment import safety as safety_module


def spec_for_dependency(path: str):
    return parse_environment_spec(
        {
            "environment_id": "symlink-containment-test",
            "version": 1,
            "repository": {
                "base_revision": None,
                "require_clean_worktree": False,
            },
            "runtimes": {"python": "3.12"},
            "required_tools": ["python"],
            "setup": {"commands": []},
            "maintenance": {"commands": []},
            "validation": {"quick": [], "normal": [], "full": []},
            "network": {"mode": "NOT_REQUIRED", "allowed_domains": []},
            "services": [],
            "secrets": {"required_names": []},
            "artifacts": {"dependency_inputs": [path]},
        }
    )


class EnvironmentFingerprintSafetyTests(unittest.TestCase):
    def test_direct_module_import_uses_containment_checked_implementation(self):
        self.assertIs(direct_inspect_local_environment, inspect_local_environment)

    def test_dependency_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside-data.txt"
            outside.write_text("must not be read\n", encoding="utf-8")
            link = repo / "dependency.txt"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            def must_not_probe(_argv):
                raise AssertionError("environment probes ran before containment validation")

            for inspect in (inspect_local_environment, direct_inspect_local_environment):
                with self.assertRaisesRegex(ValueError, "outside repository boundary"):
                    inspect(
                        spec_for_dependency("dependency.txt"),
                        repo_root=repo,
                        command_runner=must_not_probe,
                    )

    def test_dependency_replacement_after_precheck_cannot_redirect_hash_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            dependency = repo / "dependency.txt"
            dependency.write_text("inside\n", encoding="utf-8")
            outside = root / "outside-data.txt"
            outside.write_text("outside\n", encoding="utf-8")
            spec = spec_for_dependency("dependency.txt")
            original_validate = safety_module._validate_dependency_containment

            def validate_then_replace(current_spec, repo_root):
                validated_root = original_validate(current_spec, repo_root)
                dependency.unlink()
                try:
                    dependency.symlink_to(outside)
                except OSError as exc:
                    self.skipTest(f"symlink creation unavailable: {exc}")
                return validated_root

            def must_not_probe(_argv):
                raise AssertionError("environment probes ran before safe dependency open")

            with patch.object(
                safety_module,
                "_validate_dependency_containment",
                side_effect=validate_then_replace,
            ):
                with self.assertRaisesRegex(ValueError, "opened safely"):
                    inspect_local_environment(
                        spec,
                        repo_root=repo,
                        command_runner=must_not_probe,
                    )

    def test_regular_dependency_is_hashed_from_repo_anchored_descriptor(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            dependency = repo / "dependency.txt"
            dependency.write_text("inside\n", encoding="utf-8")

            def runner(argv):
                from runtime.environment.fingerprint import CommandResult

                if argv[0] == "git":
                    if argv[-2:] == ("rev-parse", "HEAD"):
                        return CommandResult(True, 0, "abc123")
                    return CommandResult(True, 0, "")
                return CommandResult(True, 0, "Python 3.12.1")

            result = inspect_local_environment(
                spec_for_dependency("dependency.txt"),
                repo_root=repo,
                command_runner=runner,
            )
            self.assertEqual(len(result.dependency_hashes["dependency.txt"]), 64)


if __name__ == "__main__":
    unittest.main()
