from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "install_opensnitch_rules.py"
)
SPEC = importlib.util.spec_from_file_location("install_opensnitch_rules", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OpenSnitchRuleInstallerTests(unittest.TestCase):
    def test_managed_rules_have_expected_narrow_scope(self) -> None:
        payloads = MODULE.validated_payloads()
        self.assertEqual(set(payloads), set(MODULE.RULE_FILES))

        ssh = json.loads(payloads["map-kudu-ruki-ssh.json"])
        ssh_terms = {
            (term["operand"], term["data"])
            for term in MODULE.operator_terms(ssh["operator"])
        }
        self.assertEqual(
            ssh_terms,
            {
                ("process.path", "/usr/bin/ssh"),
                ("dest.ip", "192.168.1.153"),
                ("dest.port", "22"),
            },
        )

        hcom = json.loads(payloads["map-kudu-hcom-relay.json"])
        self.assertEqual(hcom["operator"]["operand"], "process.path")
        self.assertEqual(
            hcom["operator"]["data"], "/home/mellow/.local/bin/hcom"
        )

    def test_install_is_idempotent_and_preserves_unrelated_rules(self) -> None:
        payloads = MODULE.validated_payloads()
        with tempfile.TemporaryDirectory() as temp:
            rules_dir = Path(temp)
            unrelated = rules_dir / "user-owned-rule.json"
            unrelated.write_text('{"keep": true}\n', encoding="utf-8")

            self.assertEqual(
                MODULE.install_payloads(payloads, rules_dir),
                (2, 0),
            )
            self.assertEqual(
                MODULE.install_payloads(payloads, rules_dir),
                (0, 2),
            )
            self.assertEqual(
                unrelated.read_text(encoding="utf-8"),
                '{"keep": true}\n',
            )

    def test_validation_rejects_broadened_ssh_destination(self) -> None:
        rule = json.loads(
            MODULE.validated_payloads()["map-kudu-ruki-ssh.json"]
        )
        rule["operator"]["list"][1]["data"] = "192.168.1.0/24"
        with self.assertRaises(MODULE.RuleError):
            MODULE.validate_rule("map-kudu-ruki-ssh.json", rule)


if __name__ == "__main__":
    unittest.main()
