from __future__ import annotations

from contextlib import closing, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.incident_taxonomy import IncidentClass
from runtime.state import TaskStore


def ready_contract(output_path: str) -> dict:
    return {
        "title": "Outcome test task",
        "outcome": "The requested behavior is observable.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner-a",
        "risk": "LOW",
        "decision_authority": "Implementation choices inside declared scope.",
        "verification": "Run deterministic tests.",
        "evidence_expected": "Passing test output.",
        "review_required": "OWNER_CHECK",
        "escalation": "Stop on scope or authority changes.",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["Do not change task lifecycle semantics."],
        "acceptance_criteria": ["Outcome evidence is append-only."],
        "stop_conditions": ["Canonical task evidence is unavailable."],
    }


class OutcomeFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def complete_task(self, task_id: str, *, with_run: bool = False) -> str | None:
        self.assertTrue(
            self.store.update_contract(task_id, ready_contract(f"{task_id}.out")).ok
        )
        self.assertTrue(self.store.promote_ready(task_id, actor="shaper").ok)
        self.assertTrue(self.store.claim_task(task_id, "owner-a").ok)
        run_id = None
        if with_run:
            run = self.store.create_run_manifest(
                task_id,
                "owner-a",
                repo_root=self.root,
                created_by="owner-a",
            )
            self.assertTrue(run.ok, run)
            run_id = run.task["run_id"]
        self.assertTrue(
            self.store.submit_task(task_id, "owner-a", "tests passed").ok
        )
        self.assertTrue(self.store.claim_review(task_id, "owner-a").ok)
        approved = self.store.record_review(
            task_id,
            "owner-a",
            "APPROVED",
            "owner check passed",
        )
        self.assertTrue(approved.ok, approved)
        self.assertEqual(approved.task["status"], "DONE")
        return run_id

    def create_done(self, task_id: str, *, with_run: bool = False) -> str | None:
        created = self.store.create_task(task_id=task_id)
        self.assertTrue(created.ok, created)
        return self.complete_task(task_id, with_run=with_run)

    def test_outcome_requires_done_task(self):
        task_id = self.store.create_task(task_id="TASK-NOT-DONE").task["task_id"]
        result = self.store.record_outcome(
            task_id,
            "SUCCESS",
            source="operator observation",
            actor_class="OPERATOR",
            actor_id="operator-1",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "OUTCOME_REQUIRES_DONE")

    def test_outcome_is_append_only_provenance_and_does_not_change_authority(self):
        task_id = "TASK-OUTCOME"
        run_id = self.create_done(task_id, with_run=True)
        before = self.store.get_task(task_id)

        result = self.store.record_outcome(
            task_id,
            "FAILURE",
            source="operator report token=source-secret",
            actor_class="OPERATOR",
            actor_id="operator-1",
            run_id=run_id,
            failure_class="regression",
            escaped_defect=True,
            rework_count=1,
            operator_intervention_count=1,
            notes="password=outcome-secret discovered after release",
        )
        self.assertTrue(result.ok, result)
        after = self.store.get_task(task_id)
        self.assertEqual(after["status"], "DONE")
        self.assertEqual(after["owner"], before["owner"])
        self.assertEqual(after["review_required"], before["review_required"])

        records = self.store.list_outcomes(task_id)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["outcome_status"], "FAILURE")
        self.assertEqual(record["actor_class"], "OPERATOR")
        self.assertEqual(record["actor_id"], "operator-1")
        self.assertEqual(record["run_id"], run_id)
        self.assertEqual(record["failure_class"], "regression")
        self.assertEqual(record["incident_class"], "UNKNOWN")
        self.assertTrue(record["escaped_defect"])
        self.assertTrue(record["task_revision"])
        self.assertNotIn("source-secret", record["source"])
        self.assertNotIn("outcome-secret", record["notes"])

        trace = self.store.trace_task(task_id)
        serialized = json.dumps(trace)
        self.assertEqual(len(trace["outcomes"]), 1)
        self.assertEqual(trace["outcomes"][0]["incident_class"], "UNKNOWN")
        self.assertNotIn("source-secret", serialized)
        self.assertNotIn("outcome-secret", serialized)

    def test_incident_class_projection_preserves_canonical_and_legacy_failure_text(self):
        canonical_task = "TASK-CANONICAL-INCIDENT"
        legacy_task = "TASK-LEGACY-INCIDENT"
        blank_task = "TASK-BLANK-INCIDENT"
        self.create_done(canonical_task)
        self.create_done(legacy_task)
        self.create_done(blank_task)

        canonical = self.store.record_outcome(
            canonical_task,
            "FAILURE",
            source="operator report",
            failure_class=IncidentClass.TOOL_FAILURE,
        )
        self.assertTrue(canonical.ok, canonical)
        self.assertEqual(
            canonical.task["outcome_record"]["failure_class"], IncidentClass.TOOL_FAILURE
        )
        self.assertEqual(
            canonical.task["outcome_record"]["incident_class"], IncidentClass.TOOL_FAILURE
        )

        legacy = self.store.record_outcome(
            legacy_task,
            "FAILURE",
            source="operator report",
            failure_class=" legacy-regression ",
        )
        self.assertTrue(legacy.ok, legacy)
        self.assertEqual(legacy.task["outcome_record"]["failure_class"], "legacy-regression")
        self.assertEqual(legacy.task["outcome_record"]["incident_class"], "UNKNOWN")
        trace = self.store.trace_task(legacy_task)
        self.assertEqual(trace["outcomes"][0]["incident_class"], "UNKNOWN")

        blank = self.store.record_outcome(
            blank_task,
            "FAILURE",
            source="operator report",
        )
        self.assertTrue(blank.ok, blank)
        self.assertEqual(blank.task["outcome_record"]["failure_class"], "UNKNOWN")
        self.assertEqual(blank.task["outcome_record"]["incident_class"], "UNKNOWN")

    def test_outcome_rows_are_sqlite_immutable(self):
        task_id = "TASK-IMMUTABLE"
        self.create_done(task_id)
        result = self.store.record_outcome(
            task_id,
            "SUCCESS",
            source="verified downstream",
            actor_class="SYSTEM",
            actor_id="integration-test",
        )
        self.assertTrue(result.ok, result)
        outcome_id = self.store.list_outcomes(task_id)[0]["id"]

        with closing(self.store._connect()) as conn:
            with self.assertRaises(sqlite3.DatabaseError):
                conn.execute(
                    "UPDATE task_outcomes SET outcome_status = 'FAILURE' WHERE id = ?",
                    (outcome_id,),
                )
            with self.assertRaises(sqlite3.DatabaseError):
                conn.execute("DELETE FROM task_outcomes WHERE id = ?", (outcome_id,))

    def test_supersession_appends_and_cannot_cross_tasks(self):
        first_task = "TASK-FIRST"
        second_task = "TASK-SECOND"
        self.create_done(first_task)
        self.create_done(second_task)

        first = self.store.record_outcome(
            first_task,
            "UNKNOWN",
            source="initial observation",
        )
        self.assertTrue(first.ok, first)
        first_id = self.store.list_outcomes(first_task)[0]["id"]

        corrected = self.store.record_outcome(
            first_task,
            "SUCCESS",
            source="later verification",
            actor_class="SYSTEM",
            actor_id="verification-job",
            supersedes_outcome_id=first_id,
        )
        self.assertTrue(corrected.ok, corrected)
        records = self.store.list_outcomes(first_task)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]["supersedes_outcome_id"], first_id)
        self.assertEqual(records[0]["outcome_status"], "UNKNOWN")

        cross_task = self.store.record_outcome(
            second_task,
            "SUCCESS",
            source="bad supersession attempt",
            supersedes_outcome_id=first_id,
        )
        self.assertFalse(cross_task.ok)
        self.assertEqual(cross_task.code, "CROSS_TASK_OUTCOME_SUPERSESSION")

    def test_run_binding_must_belong_to_same_task(self):
        first_task = "TASK-RUN-A"
        second_task = "TASK-RUN-B"
        run_id = self.create_done(first_task, with_run=True)
        self.create_done(second_task)
        result = self.store.record_outcome(
            second_task,
            "SUCCESS",
            source="operator report",
            run_id=run_id,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "OUTCOME_RUN_MISMATCH")

    def test_cli_records_and_lists_outcomes(self):
        task_id = "TASK-CLI-OUTCOME"
        self.create_done(task_id)

        output = StringIO()
        with redirect_stdout(output):
            code = cli_main(
                [
                    "--db",
                    str(self.db),
                    "outcome-record",
                    task_id,
                    "SUCCESS",
                    "--source",
                    "operator verification",
                    "--actor-class",
                    "OPERATOR",
                    "--actor-id",
                    "operator-1",
                ]
            )
        self.assertEqual(code, 0)
        recorded = json.loads(output.getvalue())
        self.assertEqual(recorded["code"], "OUTCOME_RECORDED")
        self.assertEqual(recorded["task"]["outcome_record"]["incident_class"], "UNKNOWN")

        output = StringIO()
        with redirect_stdout(output):
            code = cli_main(["--db", str(self.db), "outcomes", task_id])
        self.assertEqual(code, 0)
        records = json.loads(output.getvalue())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["outcome_status"], "SUCCESS")
        self.assertEqual(records[0]["incident_class"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
