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

    def test_string_literal_named_like_a_call_is_not_a_caller(self):
        # A non-call expression that mentions the name, even followed by "(".
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "MSG = 'call record_thing() to persist'\nGETTER = record_thing\n",
        })
        self.assertEqual(failures, [])

    # --- item 1: same-module caller blind spot -----------------------------

    def test_same_module_caller_is_caught(self):
        # The stale claim and the new caller live in the SAME file. The old
        # defining-file exclusion missed this; it must now be caught.
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """`record_thing()` has no production caller."""\n'
                '    return 1\n'
                '\n'
                'def use_it(s):\n'
                '    return s.record_thing()\n'
            ),
        })
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("record_thing", failures[0])
        self.assertIn("store.py:6", failures[0])

    def test_bare_function_call_is_a_caller(self):
        # Callee is an ast.Name (module-level function), not an attribute.
        failures = self._scan({
            "util.py": (
                'def helper():\n'
                '    """`helper()` has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "from runtime.util import helper\ndef go():\n    return helper()\n",
        })
        self.assertEqual(len(failures), 1, failures)

    def test_symbol_from_enclosing_def_when_no_backtick(self):
        # No backticked token near the phrase -> resolve via the enclosing def.
        failures = self._scan({
            "state/store.py": (
                'def record_thing(self):\n'
                '    """This method still has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(len(failures), 1, failures)

    def test_two_stale_claims_same_phrase_one_file_both_reported(self):
        failures = self._scan({
            "state/store.py": (
                'def alpha(self):\n'
                '    """`alpha()` has no production caller."""\n'
                '    return 1\n'
                '\n'
                'def beta(self):\n'
                '    """`beta()` has no production caller."""\n'
                '    return 2\n'
            ),
            "cli.py": "def go(s):\n    s.alpha()\n    return s.beta()\n",
        })
        self.assertEqual(len(failures), 2, failures)

    def test_recursive_self_call_is_not_a_caller(self):
        # A call to the symbol inside its own body is recursion, not a caller.
        failures = self._scan({
            "state/store.py": (
                'def walk(n):\n'
                '    """`walk()` has no production caller."""\n'
                '    if n:\n'
                '        return walk(n - 1)\n'
                '    return 0\n'
            ),
        })
        self.assertEqual(failures, [])

    def test_sibling_method_call_in_same_class_is_a_caller(self):
        failures = self._scan({
            "state/store.py": (
                'class Store:\n'
                '    def record_thing(self):\n'
                '        """`record_thing()` has no production caller."""\n'
                '        return 1\n'
                '\n'
                '    def flush(self):\n'
                '        return self.record_thing()\n'
            ),
        })
        self.assertEqual(len(failures), 1, failures)

    # --- item 2 (M1): multi-backtick symbol resolution --------------------

    def test_multi_backtick_resolves_to_closest_symbol(self):
        # Phrase follows `get_state`; `record_thing` (earlier on the line) has
        # a caller but is NOT what the phrase is about -> stays clean.
        failures = self._scan({
            "state/store.py": (
                'def get_state(self):\n'
                '    """`record_thing()` writes; `get_state()` has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(failures, [], failures)

    def test_multi_backtick_flags_when_closest_symbol_has_caller(self):
        failures = self._scan({
            "state/store.py": (
                'def get_state(self):\n'
                '    """`record_thing()` writes; `get_state()` has no production caller."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.get_state()\n",
        })
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("`get_state`", failures[0])

    def test_dotted_backtick_symbol_resolves_to_final_attr(self):
        failures = self._scan({
            "state/store.py": (
                'class Store:\n'
                '    def record_thing(self):\n'
                '        """`Store.record_thing()` has no production caller."""\n'
                '        return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("`record_thing`", failures[0])

    def test_backtick_after_phrase_is_ignored(self):
        # "... has no production caller (unlike `record_thing()`)" -- the
        # trailing backtick must not be mistaken for the subject.
        failures = self._scan({
            "state/store.py": (
                'def get_state(self):\n'
                '    """`get_state()` has no production caller (unlike `record_thing()`)."""\n'
                '    return 1\n'
            ),
            "cli.py": "def go(s):\n    return s.record_thing()\n",
        })
        self.assertEqual(failures, [], failures)

    def test_repo_checkout_is_clean(self):
        self.assertEqual(csc.scan(), [], "repo has an unsuppressed stale claim")


if __name__ == "__main__":
    unittest.main()
