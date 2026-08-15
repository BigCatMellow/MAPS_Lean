from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.environment import (
    CompatibilityState,
    EnvironmentFingerprint,
    EnvironmentKind,
    NetworkMode,
    ObservationState,
    VersionObservation,
    load_environment_spec,
    parse_environment_spec,
)
from runtime.state import TaskStore


SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "runtime"
    / "environment"
    / "specs"
    / "maps-runtime-ci.json"
)


def contract():
    return {
        "title": "Environment evidence task",
        "outcome": "Environment evidence is attributable to the run",
        "task_type": "IMPLEMENTATION",
        "owner": "owner",
        "risk": "MEDIUM",
        "decision_authority": "Implementation choices inside declared scope",
        "verification": "Run deterministic tests",
        "evidence_expected": "Passing test output",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "Stop on scope, authority, or safety uncertainty",
        "inputs": ["input"],
        "sources": ["source"],
        "dependencies": [],
        "output_paths": ["src"],
        "non_goals": ["No unrelated changes"],
        "acceptance_criteria": ["environment evidence is preserved"],
        "stop_conditions": ["required evidence is missing"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


class RunEnvironmentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "runtime").mkdir()
        (self.repo / "runtime" / "requirements.txt").write_text(
            "langgraph\n", encoding="utf-8"
        )
        self.store = TaskStore(self.root / "maps.db")
        created = self.store.create_task(task_id="TASK-ENV")
        self.assertTrue(created.ok, created.message)
        shaped = self.store.update_contract("TASK-ENV", contract())
        self.assertTrue(shaped.ok, shaped.message)
        self.assertTrue(self.store.promote_ready("TASK-ENV").ok)
        self.assertTrue(
            self.store.claim_task("TASK-ENV", "worker", lease_seconds=600).ok
        )
        run = self.store.create_run_manifest(
            "TASK-ENV",
            "worker",
            repo_root=self.repo,
            created_by="dispatcher",
            readable_paths=["."],
            writable_paths=["src"],
            base_revision="abc123",
        )
        self.assertTrue(run.ok, run.message)
        self.run = run.task
        self.spec = load_environment_spec(SPEC_PATH)

    def fingerprint(
        self,
        *,
        spec=None,
        python_state=ObservationState.OBSERVED,
        python_version="3.12.4",
        bash_state=ObservationState.OBSERVED,
        network_mode=NetworkMode.REQUIRED_GENERAL,
        dependency_hash="a" * 64,
    ):
        selected = spec or self.spec
        python = VersionObservation(
            python_state,
            python_version if python_state == ObservationState.OBSERVED else None,
        )
        bash = VersionObservation(
            bash_state,
            "5.2.26" if bash_state == ObservationState.OBSERVED else None,
        )
        return EnvironmentFingerprint(
            environment_spec_hash=selected.sha256,
            environment_kind=EnvironmentKind.LOCAL,
            runtimes={"python": python},
            tools={
                "bash": bash,
                "git": VersionObservation(ObservationState.OBSERVED, "2.45.1"),
                "python": VersionObservation(
                    ObservationState.OBSERVED,
                    python_version or "3.12.4",
                ),
            },
            repo_revision="abc123",
            worktree_dirty=False,
            dependency_hashes={
                "runtime/requirements.txt": dependency_hash,
            },
            network_mode=network_mode,
            allowed_domains=(),
            service_availability={},
            secret_availability={},
            observed_at="2026-08-15T17:00:00Z",
        )

    def record(self, fingerprint=None, *, spec=None, reference=None):
        return self.store.record_run_environment_evidence(
            self.run["run_id"],
            spec=spec or self.spec,
            fingerprint=fingerprint or self.fingerprint(spec=spec),
            spec_ref="runtime/environment/specs/maps-runtime-ci.json",
            recorded_by="observer",
            reference=reference,
        )

    def test_compatible_evidence_is_append_only_run_evidence(self):
        before = self.store.get_task("TASK-ENV")
        manifest_before = self.store.get_run_manifest(self.run["run_id"])

        result = self.record()

        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.task["compatibility_state"], "COMPATIBLE")
        self.assertEqual(result.task["environment_spec_hash"], self.spec.sha256)
        self.assertEqual(result.task["spec_snapshot"], self.spec.to_dict())
        self.assertEqual(
            result.task["compatibility_snapshot"]["state"],
            CompatibilityState.COMPATIBLE.value,
        )

        after = self.store.get_task("TASK-ENV")
        manifest_after = self.store.get_run_manifest(self.run["run_id"])
        for field in ("status", "claimed_by", "lease_expires_at", "heartbeat_at"):
            self.assertEqual(after[field], before[field])
        self.assertEqual(manifest_after, manifest_before)

    def test_trace_includes_environment_evidence_under_exact_run(self):
        evidence = self.record()
        self.assertTrue(evidence.ok)
        trace = self.store.trace_task("TASK-ENV")
        self.assertIsNotNone(trace)
        runs = trace["runs"]
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["run_id"], self.run["run_id"])
        self.assertEqual(len(runs[0]["environment_evidence"]), 1)
        self.assertEqual(
            runs[0]["environment_evidence"][0]["id"],
            evidence.task["id"],
        )
        self.assertTrue(
            trace["coverage"]["canonical_task_db"][
                "run_environment_evidence_included"
            ]
        )

    def test_unknown_and_incompatible_observations_can_be_recorded(self):
        unknown = self.record(
            self.fingerprint(bash_state=ObservationState.UNKNOWN)
        )
        self.assertTrue(unknown.ok)
        self.assertEqual(unknown.task["compatibility_state"], "UNKNOWN")

        incompatible = self.record(
            self.fingerprint(python_version="3.11.9")
        )
        self.assertTrue(incompatible.ok)
        self.assertEqual(incompatible.task["compatibility_state"], "INCOMPATIBLE")

        task = self.store.get_task("TASK-ENV")
        self.assertEqual(task["status"], "ACTIVE")
        self.assertEqual(task["claimed_by"], "worker")

    def test_multiple_observations_append_instead_of_replace(self):
        first = self.record()
        second = self.record(self.fingerprint(python_version="3.12.5"))
        self.assertTrue(first.ok)
        self.assertTrue(second.ok)
        rows = self.store.list_run_environment_evidence(self.run["run_id"])
        self.assertEqual([row["id"] for row in rows], [first.task["id"], second.task["id"]])
        self.assertNotEqual(first.task["fingerprint_sha256"], second.task["fingerprint_sha256"])

    def test_reference_fingerprint_identity_is_preserved(self):
        reference = self.fingerprint(python_version="3.12.4")
        observed = self.fingerprint(python_version="3.12.5")
        result = self.record(observed, reference=reference)
        self.assertTrue(result.ok)
        self.assertEqual(
            result.task["reference_fingerprint_sha256"],
            reference.sha256,
        )
        self.assertEqual(
            result.task["compatibility_snapshot"]["reference_fingerprint_sha256"],
            reference.sha256,
        )
        self.assertEqual(
            result.task["compatibility_state"],
            "COMPATIBLE_WITH_WARNINGS",
        )

    def test_missing_run_is_rejected_without_creating_evidence(self):
        result = self.store.record_run_environment_evidence(
            "RUN-does-not-exist",
            spec=self.spec,
            fingerprint=self.fingerprint(),
            spec_ref="runtime/environment/specs/maps-runtime-ci.json",
            recorded_by="observer",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "RUN_NOT_FOUND")

    def test_spec_fingerprint_hash_mismatch_is_rejected(self):
        bad = EnvironmentFingerprint(
            environment_spec_hash="0" * 64,
            environment_kind=EnvironmentKind.LOCAL,
            runtimes=self.fingerprint().runtimes,
            tools=self.fingerprint().tools,
            repo_revision="abc123",
            worktree_dirty=False,
            dependency_hashes={"runtime/requirements.txt": "a" * 64},
            network_mode=NetworkMode.REQUIRED_GENERAL,
            allowed_domains=(),
            service_availability={},
            secret_availability={},
            observed_at="2026-08-15T17:00:00Z",
        )
        result = self.record(bad)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH")
        self.assertEqual(
            self.store.list_run_environment_evidence(self.run["run_id"]),
            [],
        )

    def test_sensitive_spec_snapshot_is_rejected_not_redacted(self):
        data = self.spec.to_dict()
        data["setup"]["commands"] = [
            "API_KEY=supersecret python -m pip install package"
        ]
        sensitive_spec = parse_environment_spec(data)
        result = self.record(
            self.fingerprint(spec=sensitive_spec),
            spec=sensitive_spec,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "SENSITIVE_ENVIRONMENT_EVIDENCE")
        self.assertEqual(
            self.store.list_run_environment_evidence(self.run["run_id"]),
            [],
        )

    def test_reference_and_actor_are_required(self):
        fingerprint = self.fingerprint()
        missing_ref = self.store.record_run_environment_evidence(
            self.run["run_id"],
            spec=self.spec,
            fingerprint=fingerprint,
            spec_ref=" ",
            recorded_by="observer",
        )
        self.assertFalse(missing_ref.ok)
        self.assertEqual(missing_ref.code, "INVALID_ENVIRONMENT_EVIDENCE")

        missing_actor = self.store.record_run_environment_evidence(
            self.run["run_id"],
            spec=self.spec,
            fingerprint=fingerprint,
            spec_ref="runtime/environment/specs/maps-runtime-ci.json",
            recorded_by=" ",
        )
        self.assertFalse(missing_actor.ok)
        self.assertEqual(missing_actor.code, "INVALID_ENVIRONMENT_EVIDENCE")

    def test_environment_rows_are_sqlite_immutable(self):
        result = self.record()
        evidence_id = result.task["id"]
        for sql in (
            "UPDATE run_environment_evidence SET compatibility_state='UNKNOWN' WHERE id=?",
            "DELETE FROM run_environment_evidence WHERE id=?",
        ):
            with self.store._connect() as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql, (evidence_id,))

    def test_event_records_state_without_snapshot_contents(self):
        result = self.record()
        self.assertTrue(result.ok)
        events = self.store.list_events("TASK-ENV")
        matching = [event for event in events if event["event_type"] == "RUN_ENVIRONMENT_RECORDED"]
        self.assertEqual(len(matching), 1)
        self.assertIn("COMPATIBLE", matching[0]["summary"])
        self.assertNotIn("setup", matching[0]["summary"])
        self.assertNotIn("fingerprint_snapshot", matching[0]["summary"])


if __name__ == "__main__":
    unittest.main()
