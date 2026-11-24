"""Create-only portable initializer tests using isolated disposable Git roots."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "portable_target_init", ROOT / "scripts" / "portable_target_init.py"
)
assert SPEC and SPEC.loader
initializer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(initializer)


def git_repo(path):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    return path


class PortableTargetInitializeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = pathlib.Path(self.temp.name)
        self.target = git_repo(self.workspace / "target")

    def test_default_preview_is_nonmutating(self):
        original = tuple(self.target.iterdir())
        report = initializer.initialize(str(ROOT), str(self.target))
        self.assertEqual(report["mode"], "PREVIEW")
        self.assertEqual(report["created"], [])
        self.assertIn(".maps/roadmap.md", report["planned_paths"])
        self.assertEqual(original, tuple(self.target.iterdir()))
        self.assertFalse((self.target / ".maps").exists())

    def test_apply_creates_only_convention_files(self):
        report = initializer.initialize(str(ROOT), str(self.target), apply=True)
        maps = self.target / ".maps"
        self.assertEqual(report["mode"], "APPLY")
        self.assertTrue((maps / "README.md").is_file())
        self.assertTrue((maps / "roadmap.md").is_file())
        for folder in ("tasks", "reviews", "handoffs"):
            self.assertTrue((maps / folder).is_dir())
            self.assertEqual(list((maps / folder).iterdir()), [])
        self.assertFalse((self.target / ".venv").exists())
        self.assertFalse((self.target / ".hcom").exists())
        self.assertFalse((self.target / "runtime").exists())
        self.assertNotIn(".maps/state", report["planned_paths"])

    def test_second_apply_is_idempotent_and_preserves_content(self):
        initializer.initialize(str(ROOT), str(self.target), apply=True)
        roadmap = self.target / ".maps" / "roadmap.md"
        roadmap.write_text("TARGET-OWNED ROADMAP", encoding="utf-8")
        result = initializer.initialize(str(ROOT), str(self.target), apply=True)
        self.assertEqual(result["created"], [])
        self.assertEqual(roadmap.read_text(encoding="utf-8"), "TARGET-OWNED ROADMAP")
        self.assertEqual(len(result["existing"]), 6)

    def test_partial_existing_convention_is_preserved(self):
        maps = self.target / ".maps"
        maps.mkdir()
        (maps / "README.md").write_text("TARGET OWNED", encoding="utf-8")
        initializer.initialize(str(ROOT), str(self.target), apply=True)
        self.assertEqual((maps / "README.md").read_text(), "TARGET OWNED")
        self.assertTrue((maps / "roadmap.md").exists())
        self.assertTrue((maps / "tasks").is_dir())

    def test_non_git_target_refused_before_write(self):
        other = self.workspace / "nongit"
        other.mkdir()
        with self.assertRaisesRegex(initializer.PreflightError, "Git worktree"):
            initializer.initialize(str(ROOT), str(other), apply=True)
        self.assertEqual(list(other.iterdir()), [])

    def test_self_target_refused(self):
        with self.assertRaisesRegex(initializer.PreflightError, "must differ"):
            initializer.initialize(str(ROOT), str(ROOT), apply=True)

    def test_target_nested_path_refused(self):
        nested = self.target / "child"
        nested.mkdir()
        with self.assertRaisesRegex(initializer.PreflightError, "top level"):
            initializer.initialize(str(ROOT), str(nested), apply=True)
        self.assertFalse((nested / ".maps").exists())

    def test_symlink_convention_refused_without_writing_outside(self):
        outside = self.workspace / "outside"
        outside.mkdir()
        try:
            (self.target / ".maps").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(initializer.PreflightError, "symlink"):
            initializer.initialize(str(ROOT), str(self.target), apply=True)
        self.assertEqual(list(outside.iterdir()), [])

    def test_invalid_existing_directory_type_refused(self):
        maps = self.target / ".maps"
        maps.mkdir()
        (maps / "reviews").write_text("not a directory", encoding="utf-8")
        with self.assertRaisesRegex(initializer.PreflightError, "unexpected"):
            initializer.initialize(str(ROOT), str(self.target), apply=True)
        self.assertFalse((maps / "roadmap.md").exists())

    def test_existing_readme_can_never_be_overwritten(self):
        maps = self.target / ".maps"
        maps.mkdir()
        readme = maps / "README.md"
        readme.write_text("SENSITIVE TARGET RULE", encoding="utf-8")
        initializer.initialize(str(ROOT), str(self.target), apply=True)
        self.assertEqual(readme.read_text(), "SENSITIVE TARGET RULE")


if __name__ == "__main__":
    unittest.main()
