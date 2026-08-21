from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.state import TaskStore
from runtime.status import build_status


def ready_contract(output_path: str, *, review_required: str = "OWNER_CHECK") -> dict:
    return {
        "title": f"Task for {output_path}",
        "outcome": "Observable result.",
        "task_type": "IMPLEMENTATION",
        "owner": "owner-a",
        "risk": "LOW",
        "decision_authority": "Implementation inside declared scope.",
        "verification": "Run deterministic test.",
        "evidence_expected": "Passing test output.",
        "review_required": review_required,
        "escalation": "Stop on scope changes.",
        "inputs": ["README.md"],
        "sources": ["AGENTS.md"],
        "dependencies": [],
        "output_paths": [output_path],
        "non_goals": ["Do not widen scope."],
        "acceptance_criteria": ["Result is verified."],
        "stop_conditions": ["Required evidence is unavailable."],
    }


class StatusProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def create_ready(self, task_id: str, *, review_required: str = "OWNER_CHECK") -> None:
        self.assertTrue(self.store.create_task(task_id=task_id).ok)
        self.assertTrue(
            self.store.update_contract(
                task_id,
                ready_contract(f"{task_id}.out", review_required=review_required),
            ).ok
        )
        self.assertTrue(self.store.promote_ready(task_id, actor="shaper").ok)

    def complete(self, task_id: str) -> None:
        self.create_ready(task_id)
        self.assertTrue(self.store.claim_task(task_id, "owner-a").ok)
        self.assertTrue(self.store.submit_task(task_id, "owner-a", "verified").ok)
        self.assertTrue(self.store.claim_review(task_id, "owner-a").ok)
        self.assertTrue(
            self.store.record_review(
                task_id,
                "owner-a",
                "APPROVED",
                "owner check passed",
            ).ok
        )

    def test_status_counts_attention_and_is_read_only(self):
        now = datetime(2026, 8, 15, 13, 0, tzinfo=timezone.utc)

        self.create_ready("TASK-STALE")
        self.assertTrue(
            self.store.claim_task(
                "TASK-STALE",
                "worker-a",
                now=now,
                lease_seconds=30,
            ).ok
        )

        self.create_ready("TASK-REVIEW", review_required="INDEPENDENT_REVIEW")
        self.assertTrue(self.store.claim_task("TASK-REVIEW", "worker-b").ok)
        self.assertTrue(
            self.store.submit_task("TASK-REVIEW", "worker-b", "tests passed").ok
        )

        self.complete("TASK-FAILED-LATER")
        self.assertTrue(
            self.store.record_outcome(
                "TASK-FAILED-LATER",
                "FAILURE",
                source="operator report",
                actor_class="OPERATOR",
                actor_id="operator-1",
                failure_class="regression",
                escaped_defect=True,
            ).ok
        )

        before_stale = self.store.get_task("TASK-STALE")
        before_events = self.store.list_events("TASK-STALE")
        result = build_status(
            self.store,
            now=now + timedelta(seconds=31),
            recent_limit=3,
        )
        self.assertEqual(self.store.get_task("TASK-STALE"), before_stale)
        self.assertEqual(self.store.list_events("TASK-STALE"), before_events)

        self.assertEqual(result["tasks"]["by_status"]["ACTIVE"], 1)
        self.assertEqual(result["tasks"]["by_status"]["READY_FOR_REVIEW"], 1)
        self.assertEqual(result["tasks"]["by_status"]["DONE"], 1)
        self.assertEqual(result["active"][0]["lease_state"], "EXPIRED")

        attention = {(item["type"], item["task_id"]) for item in result["attention"]}
        self.assertIn(("STALE_LEASE", "TASK-STALE"), attention)
        self.assertIn(("REVIEW_NEEDED", "TASK-REVIEW"), attention)
        self.assertIn(("POST_COMPLETION_FAILURE", "TASK-FAILED-LATER"), attention)
        post_completion_failure = next(
            item
            for item in result["attention"]
            if item["type"] == "POST_COMPLETION_FAILURE"
        )
        self.assertEqual(post_completion_failure["failure_class"], "regression")
        self.assertEqual(post_completion_failure["incident_class"], "UNKNOWN")

        self.assertLessEqual(len(result["recent"]), 3)
        self.assertTrue(all("summary" not in item for item in result["recent"]))
        self.assertFalse(result["coverage"]["communication_hcom"])
        self.assertFalse(result["coverage"]["recovery_state"])
        self.assertFalse(result["coverage"]["helper_run_state"])

    def test_latest_success_clears_post_completion_failure_attention(self):
        self.complete("TASK-CORRECTED")
        first = self.store.record_outcome(
            "TASK-CORRECTED",
            "FAILURE",
            source="initial report",
            failure_class="regression",
        )
        self.assertTrue(first.ok)
        first_id = self.store.list_outcomes("TASK-CORRECTED")[0]["id"]
        self.assertTrue(
            self.store.record_outcome(
                "TASK-CORRECTED",
                "SUCCESS",
                source="verified correction",
                supersedes_outcome_id=first_id,
            ).ok
        )
        result = build_status(self.store)
        attention = {(item["type"], item["task_id"]) for item in result["attention"]}
        self.assertNotIn(("POST_COMPLETION_FAILURE", "TASK-CORRECTED"), attention)

    def test_limit_validation_and_cli(self):
        self.store.create_task(task_id="TASK-ONE")
        with self.assertRaises(ValueError):
            build_status(self.store, recent_limit=0)
        with self.assertRaises(ValueError):
            build_status(self.store, recent_limit=101)

        output = StringIO()
        with redirect_stdout(output):
            code = cli_main(
                ["--db", str(self.db), "status", "--recent-limit", "1"]
            )
        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["tasks"]["total"], 1)
        self.assertLessEqual(len(payload["recent"]), 1)


if __name__ == "__main__":
    unittest.main()
