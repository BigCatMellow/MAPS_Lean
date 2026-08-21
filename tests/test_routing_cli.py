from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.routing.cli import main, read_environment_reports
from runtime.state import TaskStore


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_REF = "runtime/environment/specs/maps-runtime-ci.json"


def report(state: str = "INCOMPATIBLE", *, spec_hash: str = "spec-hash") -> dict:
    return {
        "state": state,
        "reasons": ["missing_python"],
        "warnings": [],
        "environment_spec_hash": spec_hash,
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

    def test_route_cli_accepts_fresh_environment_report_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db = root / "maps.db"
            checkpoint = root / "langgraph.db"
            halt = root / "halt.json"
            workers = root / "workers.json"
            reports = root / "reports.json"
            store = TaskStore(db)
            self.assertTrue(store.create_task(task_id="TASK-1", project_id="default").ok)
            from runtime.environment.spec import load_environment_spec

            spec = load_environment_spec(REPO_ROOT / SPEC_REF)
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
            reports.write_text(
                json.dumps(
                    {
                        "environment_report_envelopes": {
                            "TASK-1": {
                                "task_id": "TASK-1",
                                "project_id": "default",
                                "spec_ref": SPEC_REF,
                                "task_revision": store.compute_task_revision("TASK-1"),
                                "produced_at": datetime.now(timezone.utc).isoformat(),
                                "max_age_seconds": 900,
                                "report": report(spec_hash=spec.sha256),
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
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
                            "--repo-root",
                            str(REPO_ROOT),
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
            self.assertEqual(json.loads(stdout.getvalue())["route"], "policy_gate")

    def test_route_cli_ignores_stale_environment_report_envelope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db = root / "maps.db"
            workers = root / "workers.json"
            reports = root / "reports.json"
            store = TaskStore(db)
            self.assertTrue(store.create_task(task_id="TASK-1", project_id="default").ok)
            from runtime.environment.spec import load_environment_spec

            spec = load_environment_spec(REPO_ROOT / SPEC_REF)
            workers.write_text(json.dumps({"workers": []}), encoding="utf-8")
            reports.write_text(
                json.dumps(
                    {
                        "environment_report_envelopes": {
                            "TASK-1": {
                                "task_id": "TASK-1",
                                "project_id": "default",
                                "spec_ref": SPEC_REF,
                                "task_revision": store.compute_task_revision("TASK-1"),
                                "produced_at": "2026-08-21T00:00:00Z",
                                "max_age_seconds": 1,
                                "report": report(spec_hash=spec.sha256),
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            parsed = read_environment_reports(
                str(reports),
                store=store,
                repo_root=str(REPO_ROOT),
            )

            self.assertEqual(parsed, {})


if __name__ == "__main__":
    unittest.main()
