"""Regression test for the runtime/environment <-> runtime/state circular import.

See work/coordination/FRICTION_LOG.md (2026-09-04 entry). Importing
`runtime.environment.spec` used to fail with an ImportError when no prior
import had already fully initialized `runtime.state` in the same process
(`python -m unittest tests.test_environment_spec` run alone reproduced it;
`unittest discover -s tests` masked it because an earlier module happened to
import `runtime.state` first). This test runs in a brand-new subprocess with
no warmup import, so it would have caught the original bug.
"""

from __future__ import annotations

import subprocess
import sys
import unittest


class EnvironmentSpecImportIsolationTests(unittest.TestCase):
    def test_environment_spec_imports_without_warmup(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", "import runtime.environment.spec"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
        )

    def test_environment_spec_test_module_runs_without_warmup(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "tests.test_environment_spec"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()
