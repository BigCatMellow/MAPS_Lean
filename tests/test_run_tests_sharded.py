"""Tests for ``scripts/run_tests_sharded.py``.

Drives the runner against a small fixture tree written to a tmp dir -- no
dependence on the real suite's timing, no network.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "scripts" / "run_tests_sharded.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("_rts", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, mod)
    spec.loader.exec_module(mod)
    return mod

OK_MOD = "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n"
BAD_MOD = "import unittest\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.assertEqual(1, 2)\n"
SLOW_MOD = "import time, unittest\n\nclass T(unittest.TestCase):\n    def test_slow(self):\n        time.sleep(10)\n"


class ShardedRunnerTest(unittest.TestCase):
    def _fixture(self, tmp: str, mods: dict[str, str]) -> Path:
        pkg = Path(tmp) / "footests"
        pkg.mkdir()
        for name, body in mods.items():
            (pkg / f"{name}.py").write_text(textwrap.dedent(body))
        return Path(tmp)

    def _run(self, cwd: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RUNNER), "--tests-dir", "footests",
             "--heartbeat", "1", *args],
            cwd=str(cwd), capture_output=True, text=True, timeout=120,
        )

    def test_all_pass_exit_zero(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_a": OK_MOD, "test_b": OK_MOD})
            cp = self._run(root)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            self.assertIn("PASS", cp.stdout)
            self.assertIn("footests.test_a", cp.stdout)
            self.assertIn("2 passed", cp.stdout)

    def test_k_filter_runs_single_module(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_a": OK_MOD, "test_b": OK_MOD})
            cp = self._run(root, "-k", "test_a")
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            self.assertIn("footests.test_a", cp.stdout)
            self.assertNotIn("footests.test_b", cp.stdout)

    def test_failing_module_exit_nonzero_others_still_run(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(
                tmp, {"test_a": OK_MOD, "test_bad": BAD_MOD, "test_c": OK_MOD})
            cp = self._run(root)
            self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
            self.assertIn("FAIL    footests.test_bad", cp.stdout)
            # the other two modules still ran and passed
            self.assertIn("PASS    footests.test_a", cp.stdout)
            self.assertIn("PASS    footests.test_c", cp.stdout)
            self.assertIn("failing modules:", cp.stdout)

    def test_timeout_module_reported_and_nonzero_others_run(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(
                tmp, {"test_slow": SLOW_MOD, "test_a": OK_MOD})
            cp = self._run(root, "--timeout-per-module", "1")
            self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
            self.assertIn("TIMEOUT footests.test_slow", cp.stdout)
            self.assertIn("PASS    footests.test_a", cp.stdout)

    def test_heartbeat_line_for_running_module(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_slow": SLOW_MOD})
            cp = self._run(root, "--timeout-per-module", "3")
            self.assertIn("running", cp.stdout)

    def test_no_match_exit_two(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_a": OK_MOD})
            cp = self._run(root, "-k", "nonexistent")
            self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)

    def test_output_streamed_not_dumped_at_end(self):
        # progress markers precede the summary in stdout order
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_a": OK_MOD, "test_b": OK_MOD})
            cp = self._run(root)
            first_pass = cp.stdout.index("PASS")
            summary = cp.stdout.index("summary:")
            self.assertLess(first_pass, summary)

    def test_parallel_jobs_all_pass(self):
        with TemporaryDirectory() as tmp:
            root = self._fixture(
                tmp, {"test_a": OK_MOD, "test_b": OK_MOD, "test_c": OK_MOD})
            cp = self._run(root, "--jobs", "3")
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            self.assertIn("3 passed", cp.stdout)


    def test_missing_warmup_import_is_swallowed(self):
        # A shard whose WARMUP_IMPORTS entry does not exist must still run its
        # module and exit cleanly (ImportError swallowed, not fatal).
        rts = _load_runner()
        code = rts._SHARD_PRELUDE.format(
            warmups=["no_such_pkg_xyz"], module="footests.test_a")
        with TemporaryDirectory() as tmp:
            root = self._fixture(tmp, {"test_a": OK_MOD})
            cp = subprocess.run([sys.executable, "-c", code], cwd=tmp,
                                capture_output=True, text=True, timeout=30)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_warmup_imports_empty_by_default(self):
        # The runtime.environment <-> runtime.state circular import that used
        # to require a "runtime.state" warmup was fixed at its root (see
        # work/coordination/FRICTION_LOG.md, 2026-09-04 entry); the extension
        # point stays available but is empty unless a future shard needs it.
        rts = _load_runner()
        self.assertEqual(rts.WARMUP_IMPORTS, ())


if __name__ == "__main__":
    unittest.main()
