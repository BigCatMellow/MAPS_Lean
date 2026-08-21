import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from runtime.helpers import (
    AiderHelper,
    HelperContinuityStore,
    HelperError,
    HelperRunStore,
    OllamaHelper,
)


FAKE_OLLAMA = r'''#!/usr/bin/env python3
import os, sys
log = os.environ.get("HELPER_FAKE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write("OLLAMA " + repr(sys.argv[1:]) + "\n")
if sys.argv[1:] == ["ls"]:
    print("NAME ID SIZE")
elif len(sys.argv) >= 3 and sys.argv[1] == "run":
    prompt = sys.stdin.read()
    print("response:" + prompt)
else:
    raise SystemExit(3)
'''

FAKE_AIDER = r'''#!/usr/bin/env python3
import os, sys
log = os.environ.get("HELPER_FAKE_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write("AIDER " + repr(sys.argv[1:]) + "\n")
print("edited")
'''

FAKE_GIT = r'''#!/usr/bin/env python3
import os, sys
if os.environ.get("HELPER_FAKE_DIRTY") == "1":
    target = sys.argv[-1]
    print(" M " + target)
'''


def make_executable(path: Path, text: str):
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def task(status="ACTIVE", outputs=None):
    return {
        "task_id": "TASK-1",
        "status": status,
        "output_paths": outputs or ["work/helper-output.md", "src"],
    }


class BoundedHelperTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        self.bin = Path(self.td.name) / "bin"
        self.bin.mkdir()
        self.ollama = self.bin / "ollama"
        self.aider = self.bin / "aider"
        self.git = self.bin / "git"
        make_executable(self.ollama, FAKE_OLLAMA)
        make_executable(self.aider, FAKE_AIDER)
        make_executable(self.git, FAKE_GIT)
        self.log = Path(self.td.name) / "calls.log"
        os.environ["HELPER_FAKE_LOG"] = str(self.log)
        self.addCleanup(os.environ.pop, "HELPER_FAKE_LOG", None)
        self.run_store = HelperRunStore(Path(self.td.name) / "helper-runs.json")
        self.continuity_store = HelperContinuityStore(
            Path(self.td.name) / "helper-continuity.json"
        )

    def test_ollama_writes_only_scoped_output_and_records_result(self):
        helper = OllamaHelper(executable=self.ollama, run_store=self.run_store)
        result = helper.run(
            task=task(), repo=self.repo, model="qwen3:8b", prompt="summarize",
            output_path="work/helper-output.md", scope_summary="bounded summary",
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual((self.repo / "work/helper-output.md").read_text().strip(), "response:summarize")
        records = json.loads(self.run_store.path.read_text())
        self.assertEqual(records[0]["task_id"], "TASK-1")

    def test_ollama_rejects_out_of_scope_output(self):
        helper = OllamaHelper(executable=self.ollama, run_store=self.run_store)
        with self.assertRaises(HelperError):
            helper.run(task=task(), repo=self.repo, model="qwen3:8b", prompt="x",
                       output_path="README.md", scope_summary="x")

    def test_helper_requires_active_parent_task(self):
        helper = OllamaHelper(executable=self.ollama, run_store=self.run_store)
        with self.assertRaises(HelperError):
            helper.run(task=task(status="READY"), repo=self.repo, model="qwen3:8b",
                       prompt="x", output_path="work/helper-output.md", scope_summary="x")

    def test_aider_uses_one_shot_safe_flags_and_scoped_target(self):
        helper = AiderHelper(executable=self.aider, git_executable=self.git, run_store=self.run_store)
        result = helper.run(task=task(), repo=self.repo, targets=["src/a.py"],
                            message="add docstring", scope_summary="edit one file",
                            model="ollama/qwen3")
        self.assertEqual(result.status, "completed")
        line = [line for line in self.log.read_text().splitlines() if line.startswith("AIDER")][-1]
        self.assertIn("'--message'", line)
        self.assertIn("'--no-auto-commits'", line)
        self.assertIn("'--no-dirty-commits'", line)
        self.assertNotIn("'--yes'", line)
        self.assertIn("'src/a.py'", line)

    def test_aider_rejects_out_of_scope_target(self):
        helper = AiderHelper(executable=self.aider, git_executable=self.git)
        with self.assertRaises(HelperError):
            helper.run(task=task(), repo=self.repo, targets=["README.md"],
                       message="change", scope_summary="bad")

    def test_aider_rejects_dirty_target(self):
        os.environ["HELPER_FAKE_DIRTY"] = "1"
        self.addCleanup(os.environ.pop, "HELPER_FAKE_DIRTY", None)
        helper = AiderHelper(executable=self.aider, git_executable=self.git)
        with self.assertRaises(HelperError):
            helper.run(task=task(), repo=self.repo, targets=["src/a.py"],
                       message="change", scope_summary="bounded")

    def test_aider_has_no_generic_argument_escape_hatch(self):
        source = Path(__file__).parents[1] / "runtime" / "helpers" / "aider.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("extra_args", text)
        self.assertNotIn('"--yes"', text)
        self.assertNotIn('"--yes-always"', text)
        self.assertIn('"--no-auto-commits"', text)
        self.assertIn('"--no-dirty-commits"', text)

    def test_helper_source_has_no_task_authority_calls(self):
        helper_dir = Path(__file__).parents[1] / "runtime" / "helpers"
        text = "\n".join(path.read_text(encoding="utf-8") for path in helper_dir.glob("*.py"))
        lowered = text.lower()
        for forbidden in (
            "claim_task(", "promote_ready(", "submit_task(",
            "record_review(", "record_operator_approval(",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_helper_continuity_reuses_exact_unexpired_match_only(self):
        now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
        record = self.continuity_store.register(
            task_id="TASK-1",
            project_id="default",
            helper="ollama:qwen3",
            purpose="summarize logs",
            context_key="rev:abc",
            session_ref="ollama-session-1",
            ttl_seconds=600,
            now=now,
        )

        reusable = self.continuity_store.resolve(
            task_id="TASK-1",
            project_id="default",
            helper="ollama:qwen3",
            purpose="summarize logs",
            context_key="rev:abc",
            now=now + timedelta(seconds=60),
        )
        self.assertTrue(reusable["reusable"])
        self.assertEqual(reusable["record"]["continuity_id"], record.continuity_id)
        self.assertEqual(reusable["record"]["session_ref"], "ollama-session-1")

        changed_context = self.continuity_store.resolve(
            task_id="TASK-1",
            project_id="default",
            helper="ollama:qwen3",
            purpose="summarize logs",
            context_key="rev:def",
            now=now + timedelta(seconds=60),
        )
        self.assertFalse(changed_context["reusable"])
        self.assertEqual(changed_context["reason"], "NO_MATCH")

    def test_helper_continuity_expires_and_invalidates_fail_closed(self):
        now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
        record = self.continuity_store.register(
            task_id="TASK-1",
            project_id="default",
            helper="aider",
            purpose="edit src",
            context_key="rev:abc",
            session_ref="aider-session-1",
            ttl_seconds=10,
            now=now,
        )

        expired = self.continuity_store.resolve(
            task_id="TASK-1",
            project_id="default",
            helper="aider",
            purpose="edit src",
            context_key="rev:abc",
            now=now + timedelta(seconds=11),
        )
        self.assertFalse(expired["reusable"])
        self.assertEqual(expired["reason"], "EXPIRED")

        self.assertTrue(
            self.continuity_store.invalidate(
                record.continuity_id,
                reason="task changed",
                now=now + timedelta(seconds=2),
            )["ok"]
        )
        invalidated = self.continuity_store.resolve(
            task_id="TASK-1",
            project_id="default",
            helper="aider",
            purpose="edit src",
            context_key="rev:abc",
            now=now + timedelta(seconds=3),
        )
        self.assertFalse(invalidated["reusable"])
        self.assertEqual(invalidated["reason"], "INVALIDATED")

    def test_helper_continuity_malformed_store_fails_closed(self):
        now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
        self.continuity_store.path.write_text(
            json.dumps(
                [
                    {
                        "task_id": "TASK-1",
                        "project_id": "default",
                        "helper": "aider",
                        "purpose": "edit src",
                        "context_key": "rev:abc",
                        "status": "active",
                        "expires_at": "2026-08-21T12:10:00Z",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = self.continuity_store.resolve(
            task_id="TASK-1",
            project_id="default",
            helper="aider",
            purpose="edit src",
            context_key="rev:abc",
            now=now,
        )

        self.assertFalse(result["reusable"])
        self.assertEqual(result["reason"], "MALFORMED_STORE")

    def test_helper_continuity_rejects_non_object_and_invalid_timestamp(self):
        now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)
        for payload in (
            ["not an object"],
            [
                {
                    "continuity_id": "HC-123456789abc",
                    "task_id": "TASK-1",
                    "project_id": "default",
                    "helper": "aider",
                    "purpose": "edit src",
                    "context_key": "rev:abc",
                    "session_ref": "aider-session-1",
                    "status": "active",
                    "created_at": "not-a-time",
                    "expires_at": "2026-08-21T12:10:00Z",
                }
            ],
        ):
            with self.subTest(payload=payload):
                self.continuity_store.path.write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )
                result = self.continuity_store.resolve(
                    task_id="TASK-1",
                    project_id="default",
                    helper="aider",
                    purpose="edit src",
                    context_key="rev:abc",
                    now=now,
                )
                self.assertFalse(result["reusable"])
                self.assertEqual(result["reason"], "MALFORMED_STORE")


if __name__ == "__main__":
    unittest.main()
