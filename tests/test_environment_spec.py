from __future__ import annotations

import copy
from pathlib import Path
import unittest

from runtime.environment import (
    EnvironmentSpecError,
    NetworkMode,
    load_environment_spec,
    parse_environment_spec,
)


SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "environment"
    / "specs"
    / "maps-runtime-ci.json"
)


class EnvironmentSpecTests(unittest.TestCase):
    def base_data(self):
        return load_environment_spec(SPEC_PATH).to_dict()

    def test_current_runtime_ci_spec_loads_and_is_hash_bound(self):
        spec = load_environment_spec(SPEC_PATH)
        self.assertEqual(spec.environment_id, "maps-runtime-ci")
        self.assertEqual(spec.version, 1)
        self.assertEqual(spec.runtimes["python"], "3.12")
        self.assertEqual(spec.network_mode, NetworkMode.REQUIRED_GENERAL)
        self.assertEqual(spec.required_secret_names, ())
        self.assertEqual(spec.dependency_inputs, ("runtime/requirements.txt",))
        self.assertEqual(len(spec.sha256), 64)
        self.assertIn(
            "python -m unittest discover -s tests -v",
            spec.validation.normal[-1],
        )

    def test_semantically_unordered_fields_do_not_change_hash(self):
        data = self.base_data()
        data["required_tools"] = list(reversed(data["required_tools"]))
        data["runtimes"] = {"python": "3.12"}
        data["services"] = []
        data["secrets"]["required_names"] = []
        data["artifacts"]["dependency_inputs"] = list(
            reversed(data["artifacts"]["dependency_inputs"])
        )
        first = parse_environment_spec(self.base_data())
        second = parse_environment_spec(data)
        self.assertEqual(first.sha256, second.sha256)

    def test_command_order_is_semantic_and_changes_hash(self):
        data = self.base_data()
        data["validation"]["quick"] = list(reversed(data["validation"]["quick"]))
        first = parse_environment_spec(self.base_data())
        second = parse_environment_spec(data)
        self.assertNotEqual(first.sha256, second.sha256)

    def test_unknown_fields_fail_closed(self):
        data = self.base_data()
        data["mystery"] = {"silently": "ignored"}
        with self.assertRaisesRegex(EnvironmentSpecError, "unknown fields"):
            parse_environment_spec(data)

    def test_secret_values_cannot_be_smuggled_as_required_names(self):
        data = self.base_data()
        data["secrets"]["required_names"] = ["GITHUB_TOKEN=secret-value"]
        with self.assertRaisesRegex(EnvironmentSpecError, "identifier"):
            parse_environment_spec(data)

    def test_secret_object_rejects_value_fields(self):
        data = self.base_data()
        data["secrets"]["values"] = {"GITHUB_TOKEN": "secret"}
        with self.assertRaisesRegex(EnvironmentSpecError, "unknown fields"):
            parse_environment_spec(data)

    def test_dependency_inputs_must_be_safe_repo_relative_paths(self):
        for bad in ("../outside.lock", "/tmp/lock", "..\\outside.lock", "."):
            data = self.base_data()
            data["artifacts"]["dependency_inputs"] = [bad]
            with self.subTest(path=bad):
                with self.assertRaisesRegex(EnvironmentSpecError, "repo-relative|portable"):
                    parse_environment_spec(data)

    def test_restricted_network_requires_explicit_domains(self):
        data = self.base_data()
        data["network"] = {
            "mode": "REQUIRED_RESTRICTED",
            "allowed_domains": [],
        }
        with self.assertRaisesRegex(EnvironmentSpecError, "requires at least one"):
            parse_environment_spec(data)

    def test_not_required_network_cannot_carry_hidden_allowlist(self):
        data = self.base_data()
        data["network"] = {
            "mode": "NOT_REQUIRED",
            "allowed_domains": ["example.com"],
        }
        with self.assertRaisesRegex(EnvironmentSpecError, "cannot declare"):
            parse_environment_spec(data)

    def test_restricted_domains_are_names_not_urls(self):
        data = self.base_data()
        data["network"] = {
            "mode": "REQUIRED_RESTRICTED",
            "allowed_domains": ["https://example.com/api"],
        }
        with self.assertRaisesRegex(EnvironmentSpecError, "domain names"):
            parse_environment_spec(data)

    def test_all_validation_tiers_are_explicit(self):
        data = self.base_data()
        del data["validation"]["normal"]
        with self.assertRaisesRegex(EnvironmentSpecError, "missing tiers"):
            parse_environment_spec(data)

    def test_boolean_version_is_not_accepted_as_integer(self):
        data = self.base_data()
        data["version"] = True
        with self.assertRaisesRegex(EnvironmentSpecError, "integer 1"):
            parse_environment_spec(data)

    def test_parser_does_not_mutate_caller_data(self):
        data = self.base_data()
        before = copy.deepcopy(data)
        parse_environment_spec(data)
        self.assertEqual(data, before)


if __name__ == "__main__":
    unittest.main()
