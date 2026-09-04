"""Tests for scripts/opcmd_merge.py -- the mechanical pre-merge authz gate.

Design: work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md (§3.1, §7).

The four §7 acceptance behaviors are pinned:
  1. --dry-run + valid authz (operator, text names #N) -> prints merge cmd + quote, exit 0
  2. authz `from` is a coordinator/agent seat -> exit non-zero, no merge cmd printed
  3. a post-authz operator HOLD present -> exit non-zero
  4. #N absent from authz text, no batch designation -> exit non-zero

No network: the hcom/gh subprocess runner is monkeypatched. The script is also
verified to be dormant (nothing in the repo calls it).
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import pathlib
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_MODULE_PATH = _ROOT / "scripts" / "opcmd_merge.py"
_spec = importlib.util.spec_from_file_location("opcmd_merge", _MODULE_PATH)
om = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(om)  # type: ignore[union-attr]


def _now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _msg_event(msg_id, sender, text, ts=None):
    return {
        "data": {"from": sender, "intent": "request", "text": text},
        "id": msg_id,
        "instance": sender,
        "ts": ts or _now_iso(),
        "type": "message",
    }


class FakeRunner:
    """Stands in for opcmd_merge.run_command. Records calls, no subprocess."""

    def __init__(self, authz_event=None, post_authz_events=None, head_sha="deadbeef"):
        self.authz_event = authz_event
        self.post_authz_events = post_authz_events or []
        self.head_sha = head_sha
        self.calls = []

    def __call__(self, cmd):
        self.calls.append(list(cmd))
        if cmd[:2] == ["hcom", "events"]:
            sql = cmd[cmd.index("--sql") + 1]
            if sql.startswith("id="):
                events = [self.authz_event] if self.authz_event else []
            elif sql.startswith("id >") or sql.startswith("id>"):
                events = self.post_authz_events
            else:
                events = []
            return 0, "\n".join(json.dumps(e) for e in events) + "\n", ""
        if cmd[:3] == ["gh", "pr", "view"]:
            return 0, self.head_sha + "\n", ""
        if cmd[:3] == ["gh", "pr", "merge"]:
            return 0, "merged\n", ""
        return 1, "", f"unexpected cmd: {cmd}"

    @property
    def merge_invoked(self):
        return any(c[:3] == ["gh", "pr", "merge"] for c in self.calls)


class OpcmdMergeGateTest(unittest.TestCase):
    def setUp(self):
        self._orig_runner = om.run_command
        self.addCleanup(lambda: setattr(om, "run_command", self._orig_runner))

    def _run_main(self, argv, runner):
        om.run_command = runner
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = om.main(argv)
        return rc, out.getvalue(), err.getvalue()

    # 1. valid authz + --dry-run -> exit 0, prints merge cmd + authz quote
    def test_dry_run_valid_authz_passes(self):
        runner = FakeRunner(
            authz_event=_msg_event(
                500, "bigboss", "go ahead and merge #42 now, CI is green"
            )
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "500", "--dry-run", "--caller", "gule"], runner
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("gh pr merge 42 --squash", out)
        self.assertIn("merge #42 now", out)  # authz quote echoed
        self.assertIn("GATE PASSED", out)
        self.assertFalse(runner.merge_invoked, "dry-run must not invoke gh pr merge")

    # 2. authz from a coordinator/agent seat -> non-zero, no merge cmd printed
    def test_coordinator_sender_refused(self):
        runner = FakeRunner(
            authz_event=_msg_event(501, "miso", "merge #42, it's review-cleared")
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "501", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertNotIn("gh pr merge 42", out)
        self.assertIn("not an operator identity", err)
        self.assertFalse(runner.merge_invoked)

    # 3. post-authz operator HOLD -> non-zero
    def test_post_authz_hold_refused(self):
        runner = FakeRunner(
            authz_event=_msg_event(502, "bigboss", "merge #42"),
            post_authz_events=[
                _msg_event(510, "bigboss", "HOLD -- do not merge anything, found a bug")
            ],
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "502", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("HOLD", err)
        self.assertFalse(runner.merge_invoked)

    # 4. #N absent, no batch designation -> non-zero
    def test_pr_not_named_refused(self):
        runner = FakeRunner(
            authz_event=_msg_event(503, "bigboss", "looks good, nice work team")
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "503", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("does not name #42", err)
        self.assertNotIn("gh pr merge 42", out)

    # --- supporting behavior ---

    def test_missing_authz_message_refused(self):
        runner = FakeRunner(authz_event=None)
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "999", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("not found", err)

    def test_fresh_batch_designation_passes(self):
        runner = FakeRunner(
            authz_event=_msg_event(
                504, "bigboss", "you are the merge seat for the queue tonight"
            )
        )
        rc, out, err = self._run_main(
            ["--pr", "7", "--authz", "504", "--dry-run"], runner
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("batch-designation", out)

    def test_stale_batch_designation_refused(self):
        old_ts = (
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=30)
        ).isoformat()
        runner = FakeRunner(
            authz_event=_msg_event(
                505, "bigboss", "you are the merge seat for the batch", ts=old_ts
            )
        )
        rc, out, err = self._run_main(
            ["--pr", "7", "--authz", "505", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("stale", err)

    def test_dont_merge_specific_pr_refused(self):
        runner = FakeRunner(
            authz_event=_msg_event(506, "bigboss", "merge #42"),
            post_authz_events=[
                _msg_event(520, "bigboss", "actually don't merge #42, needs a rebase")
            ],
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "506", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)

    def test_non_dry_run_appends_ledger_and_merges(self):
        import tempfile, os

        runner = FakeRunner(authz_event=_msg_event(507, "bigboss", "merge #42"))
        with tempfile.TemporaryDirectory() as td:
            ledger = os.path.join(td, "work", "coordination", "merge-ledger.jsonl")
            om.run_command = runner
            entry = om.gate(
                pr=42,
                authz_id="507",
                caller="gule",
                merge_args=["--admin"],
                dry_run=False,
                ledger_path=ledger,
            )
            self.assertTrue(entry["merged"])
            self.assertTrue(runner.merge_invoked)
            self.assertIn(["gh", "pr", "merge", "42", "--squash", "--admin"], runner.calls)
            with open(ledger, encoding="utf-8") as fh:
                rows = [json.loads(l) for l in fh if l.strip()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["pr"], 42)
            self.assertEqual(rows[0]["authz_from"], "bigboss")
            self.assertEqual(rows[0]["authz_id"], 507)

    def test_hold_before_authz_is_ignored(self):
        # a HOLD that predates the authz id must not block (only id > authz scanned)
        runner = FakeRunner(
            authz_event=_msg_event(508, "bigboss", "clear to merge #42 now"),
            post_authz_events=[],
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "508", "--dry-run"], runner
        )
        self.assertEqual(rc, 0, err)


class DormancyTest(unittest.TestCase):
    def test_no_repo_file_invokes_the_script(self):
        hits = []
        for path in _ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".yml", ".yaml", ".sh", ".md"}:
                continue
            if path.name in {"opcmd_merge.py", "test_opcmd_merge.py"}:
                continue
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "opcmd_merge" in text and "scripts/opcmd_merge.py" in text and "design" not in path.name:
                # a design-note mention is fine; an invocation is not
                for line in text.splitlines():
                    if "opcmd_merge.py" in line and ("python" in line or "subprocess" in line or "run(" in line):
                        hits.append(f"{path}: {line.strip()}")
        self.assertEqual(hits, [], f"script must stay dormant; found: {hits}")


if __name__ == "__main__":
    unittest.main()
