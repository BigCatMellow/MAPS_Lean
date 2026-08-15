from pathlib import Path
import tempfile
import unittest

from runtime.environment import inspect_local_environment, parse_environment_spec
from runtime.environment.fingerprint import inspect_local_environment as direct_inspect_local_environment


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
            outside = root / "outside-secret.txt"
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


if __name__ == "__main__":
    unittest.main()
