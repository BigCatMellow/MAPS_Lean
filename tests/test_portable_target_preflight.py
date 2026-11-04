"""Contract tests for the read-only portable target preflight (no network)."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "portable_target_preflight", ROOT / "scripts" / "portable_target_preflight.py"
)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def init_repo(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    return path


class PortableTargetPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = pathlib.Path(self.temp.name)
        self.target = init_repo(self.workspace / "target")

    def test_empty_target_reports_missing_without_mutation(self):
        before = list(self.target.iterdir())
        result = preflight.inspect(str(ROOT), str(self.target))
        self.assertEqual(result["mode"], "READ_ONLY_PREFLIGHT")
        self.assertFalse(result["initialized"])
        self.assertEqual(
            set(result["target_layout"].values()), {"missing"}
        )
        self.assertEqual(before, list(self.target.iterdir()))
        self.assertFalse((self.target / ".maps").exists())

    def test_existing_target_reports_present_without_rewriting(self):
        maps = self.target / ".maps"
        for name in ("tasks", "reviews", "handoffs"):
            (maps / name).mkdir(parents=True, exist_ok=True)
        (maps / "README.md").write_text("my policy", encoding="utf-8")
        (maps / "roadmap.md").write_text("my plan", encoding="utf-8")
        result = preflight.inspect(str(ROOT), str(self.target))
        self.assertTrue(result["initialized"])
        self.assertEqual((maps / "README.md").read_text(), "my policy")
        self.assertEqual((maps / "roadmap.md").read_text(), "my plan")

    def test_self_target_refused(self):
        with self.assertRaisesRegex(preflight.PreflightError, "must differ"):
            preflight.inspect(str(ROOT), str(ROOT))

    def test_nested_directory_refused(self):
        subdir = self.target / "nested"
        subdir.mkdir()
        with self.assertRaisesRegex(preflight.PreflightError, "top level"):
            preflight.inspect(str(ROOT), str(subdir))

    def test_non_git_target_refused(self):
        outside = self.workspace / "not-a-repo"
        outside.mkdir()
        with self.assertRaisesRegex(preflight.PreflightError, "Git worktree"):
            preflight.inspect(str(ROOT), str(outside))

    def test_missing_target_refused(self):
        with self.assertRaisesRegex(preflight.PreflightError, "inaccessible root"):
            preflight.inspect(str(ROOT), str(self.workspace / "missing"))

    def test_symlinked_maps_directory_refused(self):
        outside = self.workspace / "outside"
        outside.mkdir()
        try:
            (self.target / ".maps").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this platform")
        with self.assertRaisesRegex(preflight.PreflightError, "symlink"):
            preflight.inspect(str(ROOT), str(self.target))
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlinked_target_root_refused(self):
        linked = self.workspace / "linked-target"
        try:
            linked.symlink_to(self.target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this platform")
        with self.assertRaisesRegex(preflight.PreflightError, "canonical"):
            preflight.inspect(str(ROOT), str(linked))

    def test_wrong_convention_type_refused(self):
        maps = self.target / ".maps"
        maps.mkdir()
        (maps / "tasks").write_text("not a directory", encoding="utf-8")
        with self.assertRaisesRegex(preflight.PreflightError, "unexpected"):
            preflight.inspect(str(ROOT), str(self.target))

    def test_missing_maps_portable_template_refused(self):
        fake_maps = init_repo(self.workspace / "fake-maps")
        with self.assertRaisesRegex(preflight.PreflightError, "missing MAPS portable template"):
            preflight.inspect(str(fake_maps), str(self.target))

    def test_explicit_roots_required(self):
        with self.assertRaisesRegex(preflight.PreflightError, "explicit"):
            preflight.inspect("", str(self.target))


if __name__ == "__main__":
    unittest.main()
