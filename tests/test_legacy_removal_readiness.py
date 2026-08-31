"""Guard tests for scripts/check_legacy_removal_readiness.py.

Focus: the historical-exclude file allowlist must suppress FORBIDDEN_TEXT
path-literal hits for the named files (which carry `legacy/` strings as a
historical-exclusion list, not as runtime dependencies) while leaving the
AST legacy-import check and every other file's scanning intact.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "check_legacy_removal_readiness",
    ROOT / "scripts" / "check_legacy_removal_readiness.py",
)
guard = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(guard)


class HistoricalExcludeFilesTest(unittest.TestCase):
    def test_allowlisted_spiderweb_files_do_not_trip_guard(self) -> None:
        failures = guard.active_dependency_failures()
        for rel in guard.HISTORICAL_EXCLUDE_FILES:
            offending = [f for f in failures if f.startswith(f"{rel}:")]
            self.assertEqual(offending, [], f"{rel} should be allowlisted: {offending}")

    def test_allowlist_is_scoped_to_the_two_spiderweb_files(self) -> None:
        self.assertEqual(
            set(guard.HISTORICAL_EXCLUDE_FILES),
            {"scripts/check_spiderweb.py", "tests/test_spiderweb_audit.py"},
        )

    def test_repository_currently_passes_the_guard(self) -> None:
        self.assertEqual(guard.active_dependency_failures(), [])


if __name__ == "__main__":
    unittest.main()
