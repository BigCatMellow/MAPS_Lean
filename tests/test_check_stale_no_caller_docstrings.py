"""Tests for scripts/check_stale_no_caller_docstrings.py (CLAUDE.md rule 20
mechanical safeguard against stale "no production caller" docstrings)."""

import importlib.util
import pathlib
import tempfile
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_stale_no_caller_docstrings.py"
)
_spec = importlib.util.spec_from_file_location("check_stale_no_caller", _MODULE_PATH)
csc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csc)  # type: ignore[union-attr]


def _runtime_tree(root: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    rt = root / "runtime"
    for rel, body in files.items():
        p = rt / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return rt


class CheckStaleNoCallerTests(unittest.TestCase):
    def _scan(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            rt = _runtime_tree(root, files)
            return csc.scan(runtime_dir=rt, repo_root=root)

    def test_stale_claim_with_planted_caller_fails(self):
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` still has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": (
                "from runtime.state.store import S\n"
                "def go(s):\n"
                "    return s.record_thing()\n"
            ),
        })
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("record_thing", failures[0])
        self.assertIn("cli.py", failures[0])

    def test_claim_split_across_lines_is_caught(self):
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` still has no production\n'
                '    caller; a later task will add one."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(len(failures), 1, failures)

    def test_no_caller_passes(self):
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller yet."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go():\n    return 0\n",
        })
        self.assertEqual(failures, [])

    def test_only_test_caller_passes(self):
        # A caller living under a tests/ path does not count.
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller."""\n'
                '    return 1\n'
            ),
            "tests/test_store.py": "def t(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(failures, [])

    def test_noqa_escape_hatch_suppresses(self):
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller.\n'
                '\n'
                '    Narrower than grep sees.\n'
                '    """  # noqa: stale-caller-check\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(failures, [])

    def test_bare_mention_is_not_a_caller(self):
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "# see record_thing for details\nX = 'record_thing'\n",
        })
        self.assertEqual(failures, [])

    def test_repo_checkout_is_clean(self):
        self.assertEqual(csc.scan(), [], "repo has an unsuppressed stale claim")


if __name__ == "__main__":
    unittest.main()
