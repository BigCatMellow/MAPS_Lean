"""Tests for scripts/check_coverage_note_pins.py (Part B of the
invariant-prose-drift rule-20 safeguard)."""

import importlib.util
import pathlib
import tempfile
import textwrap
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_coverage_note_pins.py"
)
_spec = importlib.util.spec_from_file_location("check_coverage_note_pins", _MODULE_PATH)
ccnp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ccnp)  # type: ignore[union-attr]


_CB_TEMPLATE = '''\
def build_context_plan(store, task_id):
    return {{
        "task_id": task_id,
        "coverage": {{
            "explicit_task_relationships": True,
            "note": (
                "v1 identifies exact inputs to read; it does not search"
            ),
            "budget_classification_note": (
                "no new retrieval mechanism"
            ),{extra}
        }},
    }}
'''


def _write(root: pathlib.Path, name: str, body: str) -> pathlib.Path:
    p = root / name
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


class CheckCoverageNotePinsTests(unittest.TestCase):
    def _run(self, extra_note: str, pin_body: str):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            cb = _write(root, "context_builder.py", _CB_TEMPLATE.format(extra=extra_note))
            pin = _write(root, "test_context_builder.py", pin_body)
            return ccnp.find_unpinned(cb, (pin,))

    def test_pinned_notes_pass(self):
        failures = self._run(
            extra_note="",
            pin_body='''
                def test_notes(self):
                    cov = plan["coverage"]
                    assert cov["note"]
                    assert cov["budget_classification_note"]
            ''',
        )
        self.assertEqual(failures, [])

    def test_unpinned_note_fails(self):
        failures = self._run(
            extra_note='\n            "memory_trust_gate_note": ("every ... passed admit_memory_evidence"),',
            pin_body='''
                def test_notes(self):
                    cov = plan["coverage"]
                    assert cov["note"]
                    assert cov["budget_classification_note"]
            ''',
        )
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("memory_trust_gate_note", failures[0])

    def test_noqa_suppresses(self):
        failures = self._run(
            extra_note=(
                '\n            "memory_trust_gate_note": (  # noqa: coverage-note-pin\n'
                '                "an intentionally unpinned note"\n'
                '            ),'
            ),
            pin_body='''
                def test_notes(self):
                    cov = plan["coverage"]
                    assert cov["note"]
                    assert cov["budget_classification_note"]
            ''',
        )
        self.assertEqual(failures, [])

    def test_substring_key_is_not_a_pin(self):
        # A test string that merely *contains* the note name is not a pin;
        # only a subscript by the exact key counts.
        failures = self._run(
            extra_note="",
            pin_body='''
                def test_notes(self):
                    # mentions "note" and "budget_classification_note" in prose only
                    describe = "the note and budget_classification_note fields"
                    assert describe
            ''',
        )
        self.assertEqual(len(failures), 2, failures)

    def test_repo_tree_is_clean(self):
        self.assertEqual(ccnp.find_unpinned(), [])


if __name__ == "__main__":
    unittest.main()
