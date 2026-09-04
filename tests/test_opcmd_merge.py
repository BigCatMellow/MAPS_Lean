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
            if "--sql" in cmd:
                sql = cmd[cmd.index("--sql") + 1]
                if sql.startswith("id="):
                    events = [self.authz_event] if self.authz_event else []
                elif sql.startswith("id >") or sql.startswith("id>"):
                    events = self.post_authz_events
                else:
                    events = []
            elif "--last" in cmd:
                # liveness check: newest message event
                pool = [e for e in ([self.authz_event] + self.post_authz_events) if e]
                events = [max(pool, key=lambda e: e["id"])] if pool else []
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

    # F1: a prohibiting authz message must NOT pass, even though #N is present.
    def test_authz_pure_prohibition_refused(self):  # CASE B
        runner = FakeRunner(
            authz_event=_msg_event(540, "bigboss", "do not merge #42 yet")
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "540", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("not to merge", err)
        self.assertNotIn("gh pr merge 42", out)
        self.assertFalse(runner.merge_invoked)

    def test_authz_mixed_authorize_and_prohibit_refused(self):  # CASE A
        runner = FakeRunner(
            authz_event=_msg_event(
                541, "bigboss", "merge #40 now. do not merge #42, it needs a rebase"
            )
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "541", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertFalse(runner.merge_invoked)
        # ...but the same message DOES authorize #40
        runner40 = FakeRunner(authz_event=runner.authz_event)
        rc2, out2, err2 = self._run_main(
            ["--pr", "40", "--authz", "541", "--dry-run"], runner40
        )
        self.assertEqual(rc2, 0, err2)
        self.assertIn("gh pr merge 40 --squash", out2)

    def test_authz_with_hold_token_refused(self):
        runner = FakeRunner(
            authz_event=_msg_event(542, "bigboss", "merge #42 -- wait, HOLD")
        )
        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "542", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)

    # O4: real hcom ts is naive (no Z, no offset) -- exercise that path.
    def test_naive_timestamp_stale_batch_designation_refused(self):
        naive_old = (
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=30)
        ).replace(tzinfo=None, microsecond=0).isoformat()  # e.g. "2026-09-02T20:07:31"
        self.assertNotIn("+", naive_old)
        runner = FakeRunner(
            authz_event=_msg_event(
                543, "bigboss", "you are the merge seat for the batch", ts=naive_old
            )
        )
        rc, out, err = self._run_main(
            ["--pr", "7", "--authz", "543", "--dry-run"], runner
        )
        self.assertEqual(rc, 2)
        self.assertIn("stale", err)

    def test_liveness_check_stale_stream_refused(self):
        # newest message in the stream is older than the authz id -> wrong store
        runner = FakeRunner(authz_event=_msg_event(600, "bigboss", "merge #42"))
        # override: liveness returns an older event
        old_ev = _msg_event(10, "bigboss", "something old")
        orig = runner.__call__

        def patched(cmd):
            if cmd[:2] == ["hcom", "events"] and "--last" in cmd:
                runner.calls.append(list(cmd))
                return 0, json.dumps(old_ev) + "\n", ""
            return orig(cmd)

        rc, out, err = self._run_main(
            ["--pr", "42", "--authz", "600", "--dry-run"], patched
        )
        self.assertEqual(rc, 3)
        self.assertIn("wrong store", err)

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


# --- dormancy check (F2, PR #287 review) ---
#
# The earlier version walked every prose .md and flagged any file mentioning
# scripts/opcmd_merge.py near the words python/subprocess -- so the review-evidence
# file's own summary line tripped it, and so would any trajectory note / handoff /
# friction entry. Narrowed to files that could *actually invoke* the script.

_INVOCATION_MARKERS = (
    "subprocess",
    "check_call",
    "check_output",
    "Popen",
    "os.system",
    "run(",
    "import opcmd_merge",
    "from opcmd_merge",
)


def _is_executable_repo_file(path):
    """True if `path` is code/CI/shell that could shell out to the script.

    Excludes `work/` wholesale (review evidence, notes, handoffs, friction log)
    and every `*.md` (all prose) -- they name the script without running it.
    """
    if ".git" in path.parts or "work" in path.parts:
        return False
    if path.suffix == ".md":
        return False
    if path.name in {"opcmd_merge.py", "test_opcmd_merge.py"}:
        return False
    parts = path.parts
    if path.suffix == ".py" and any(
        p in parts for p in ("scripts", "runtime", "tests", "tools")
    ):
        return True
    if path.suffix in {".yml", ".yaml"} and ".github" in parts:
        return True
    if path.suffix == ".sh":
        return True
    return False


def _dormancy_hits(named_texts):
    """named_texts: iterable of (name, text) or (name, text, is_shell).

    A shell script naming the script IS an invocation (shell files don't discuss
    it in prose); a Python/YAML line counts only with an explicit invocation
    marker (subprocess/Popen/import/...).
    """
    hits = []
    for item in named_texts:
        name, text = item[0], item[1]
        is_shell = item[2] if len(item) > 2 else str(name).endswith(".sh")
        for line in text.splitlines():
            if "opcmd_merge" not in line:
                continue
            if is_shell or any(m in line for m in _INVOCATION_MARKERS):
                hits.append(f"{name}: {line.strip()}")
    return hits


def _walk_repo_dormancy_hits(root):
    named_texts = []
    for path in root.rglob("*"):
        if not path.is_file() or not _is_executable_repo_file(path):
            continue
        try:
            named_texts.append(
                (str(path.relative_to(root)), path.read_text(encoding="utf-8", errors="ignore"))
            )
        except OSError:
            continue
    return _dormancy_hits(named_texts)


class DormancyTest(unittest.TestCase):
    def test_no_executable_repo_file_invokes_the_script(self):
        self.assertEqual(
            _walk_repo_dormancy_hits(_ROOT), [], "script must stay dormant"
        )

    def test_prose_mention_in_work_dir_does_not_trip_the_walk(self):
        # F2: a real work/reviews/-style .md naming the script next to the word
        # "subprocess" must not be seen as an invocation by the actual walk.
        import os, uuid

        rel = pathlib.Path("work") / "reviews" / f"_fixture-{uuid.uuid4().hex}.md"
        fpath = _ROOT / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(
            "reviewer: sana\nsummary: touched scripts/opcmd_merge.py; tests mock "
            "the hcom/gh subprocess runner; python -m unittest green\n",
            encoding="utf-8",
        )
        self.addCleanup(lambda: fpath.exists() and os.remove(fpath))
        self.assertEqual(_walk_repo_dormancy_hits(_ROOT), [])

    def test_work_and_md_paths_are_excluded(self):
        self.assertFalse(_is_executable_repo_file(_ROOT / "work" / "reviews" / "pr-287-review-evidence.md"))
        self.assertFalse(_is_executable_repo_file(_ROOT / "work" / "notes" / "x.md"))
        self.assertFalse(_is_executable_repo_file(_ROOT / "README.md"))

    def test_real_invocation_would_trip_the_walk(self):
        # a fixture .py under scripts/ that shells out to the script SHOULD be caught
        import os, uuid

        rel = pathlib.Path("scripts") / f"_fixture_caller_{uuid.uuid4().hex}.py"
        fpath = _ROOT / rel
        fpath.write_text(
            'import subprocess\nsubprocess.run(["python", "scripts/opcmd_merge.py", "--pr", "1"])\n',
            encoding="utf-8",
        )
        self.addCleanup(lambda: fpath.exists() and os.remove(fpath))
        hits = _walk_repo_dormancy_hits(_ROOT)
        self.assertTrue(hits, "a real subprocess invocation must be detected")
        self.assertIn(str(rel), hits[0])

    def test_import_of_the_module_would_trip(self):
        self.assertTrue(_dormancy_hits([("tests/x.py", "from opcmd_merge import gate\n")]))

    def test_shell_script_naming_the_script_trips(self):
        self.assertTrue(
            _dormancy_hits([("scripts/x.sh", "python scripts/opcmd_merge.py --pr 1\n")])
        )


if __name__ == "__main__":
    unittest.main()
