from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.routing.cli import main, read_environment_reports


def report(state: str = "INCOMPATIBLE") -> dict:
    return {
        "state": state,
        "reasons": ["missing_python"],
        "warnings": [],
        "environment_spec_hash": "spec-hash",
        "fingerprint_sha256": "fingerprint-hash",
    }


class RoutingCliTests(unittest.TestCase):
    def test_read_environment_reports_accepts_wrapped_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "reports.json"
            path.write_text(
                json.dumps({"environment_reports": {"TASK-1": report()}}),
                encoding="utf-8",
            )

            parsed = read_environment_reports(str(path))

            self.assertEqual(parsed["TASK-1"].state.value, "INCOMPATIBLE")

    def test_route_cli_uses_environment_reports_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db = root / "maps.db"
            checkpoint = root / "langgraph.db"
            halt = root / "halt.json"
            workers = root / "workers.json"
            reports = root / "reports.json"
            workers.write_text(
                json.dumps(
                    {
                        "workers": [
                            {
                                "worker_id": "core",
                                "worker_class": "core",
                                "supported_task_types": ["*"],
                                "max_risk": "HIGH",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            reports.write_text(json.dumps({"TASK-1": report()}), encoding="utf-8")
            stdout = io.StringIO()

            def fake_route_project(*args, **kwargs):
                environment_reports = kwargs["environment_reports"]
                self.assertEqual(
                    environment_reports["TASK-1"].state.value,
                    "INCOMPATIBLE",
                )
                return {
                    "route": "policy_gate",
                    "task_id": "TASK-1",
                    "worker_id": None,
                    "reasons": ["environment_incompatible"],
                }

            with patch("runtime.routing.cli.route_project", side_effect=fake_route_project):
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "--db",
                            str(db),
                            "--halt-path",
                            str(halt),
                            "route",
                            "--workers-json",
                            str(workers),
                            "--checkpoint-db",
                            str(checkpoint),
                            "--environment-reports-json",
                            str(reports),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["route"], "policy_gate")
            self.assertEqual(payload["task_id"], "TASK-1")
            self.assertEqual(payload["reasons"], ["environment_incompatible"])

    def test_route_cli_rejects_malformed_environment_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workers = root / "workers.json"
            reports = root / "reports.json"
            workers.write_text(json.dumps({"workers": []}), encoding="utf-8")
            reports.write_text(
                json.dumps({"TASK-1": {"state": "INCOMPATIBLE"}}),
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--db",
                        str(root / "maps.db"),
                        "route",
                        "--workers-json",
                        str(workers),
                        "--environment-reports-json",
                        str(reports),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("environment report hashes must be strings", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
