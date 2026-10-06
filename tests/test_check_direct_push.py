import importlib.util
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_direct_push.py"
)
_spec = importlib.util.spec_from_file_location("check_direct_push", _MODULE_PATH)
cdp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cdp)  # type: ignore[union-attr]


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(root: pathlib.Path, name: str, message: str, *, author: str = "t") -> str:
    (root / name).write_text(message, encoding="utf-8")
    _git(root, "add", name)
    _git(root, "-c", f"user.name={author}", "-c", "user.email=t@example.com", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _init_repo(root: pathlib.Path) -> str:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    return _commit(root, "f0.txt", "init")


class PushedCommitsTests(unittest.TestCase):
    def test_zero_before_returns_empty(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            shas = cdp._pushed_commits(root, "0" * 40, head)
            self.assertEqual(shas, [])

    def test_range_returns_new_commits_oldest_last(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = _init_repo(root)
            mid = _commit(root, "f1.txt", "mid")
            after = _commit(root, "f2.txt", "after")
            shas = cdp._pushed_commits(root, before, after)
            self.assertEqual(shas, [after, mid])


class ParentCountTests(unittest.TestCase):
    def test_root_commit_has_zero_parents(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            self.assertEqual(cdp._parent_count(root, head), 0)

    def test_normal_commit_has_one_parent(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            _init_repo(root)
            second = _commit(root, "f1.txt", "second")
            self.assertEqual(cdp._parent_count(root, second), 1)

    def test_merge_commit_has_two_parents(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            _init_repo(root)
            _git(root, "checkout", "-q", "-b", "side")
            _commit(root, "side.txt", "side change")
            _git(root, "checkout", "-q", "-")
            _commit(root, "main.txt", "main change")
            _git(root, "merge", "-q", "--no-ff", "side", "-m", "merge side")
            merge_sha = _git(root, "rev-parse", "HEAD")
            self.assertEqual(cdp._parent_count(root, merge_sha), 2)


class FindViolationsTests(unittest.TestCase):
    def test_no_merged_pr_is_a_violation(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = _init_repo(root)
            after = _commit(root, "f1.txt", "docs: direct push", author="BigCat Mellow")
            with mock.patch.object(cdp, "_has_merged_pr", return_value=False):
                violations = cdp.find_violations(root, "o/r", before, after)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["sha"], after)
            self.assertEqual(violations[0]["author"], "BigCat Mellow")

    def test_merged_pr_is_not_a_violation(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = _init_repo(root)
            after = _commit(root, "f1.txt", "squash merge of #99")
            with mock.patch.object(cdp, "_has_merged_pr", return_value=True):
                violations = cdp.find_violations(root, "o/r", before, after)
            self.assertEqual(violations, [])

    def test_merge_commit_is_skipped_without_calling_the_api(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = _init_repo(root)
            _git(root, "checkout", "-q", "-b", "side")
            _commit(root, "side.txt", "side change")
            _git(root, "checkout", "-q", "-")
            _commit(root, "main.txt", "main change")
            _git(root, "merge", "-q", "--no-ff", "side", "-m", "merge side")
            merge_sha = _git(root, "rev-parse", "HEAD")
            with mock.patch.object(cdp, "_has_merged_pr", return_value=True) as mocked:
                cdp.find_violations(root, "o/r", before, merge_sha)
            checked_shas = [call.args[1] for call in mocked.call_args_list]
            self.assertNotIn(merge_sha, checked_shas)

    def test_empty_range_has_no_violations(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            with mock.patch.object(cdp, "_has_merged_pr") as mocked:
                violations = cdp.find_violations(root, "o/r", "0" * 40, head)
            mocked.assert_not_called()
            self.assertEqual(violations, [])


class MainExitCodeTests(unittest.TestCase):
    def test_exits_nonzero_on_violation(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            before = _init_repo(root)
            after = _commit(root, "f1.txt", "docs: direct push")
            with mock.patch.object(cdp, "_has_merged_pr", return_value=False):
                code = cdp.main(
                    [before, after, "--repo", "o/r", "--repo-root", str(root)]
                )
            self.assertEqual(code, 1)

    def test_exits_zero_when_clean(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            code = cdp.main(
                ["0" * 40, head, "--repo", "o/r", "--repo-root", str(root)]
            )
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
