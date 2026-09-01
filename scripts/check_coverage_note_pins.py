"""Fail CI when a self-describing ``*_note`` string in
``runtime/context_builder.py::build_context_plan``'s returned ``coverage`` dict
is not referenced by any test -- i.e. it has no test that would break if the
note became a lie.

Why this exists (CLAUDE.md rule 20 -- a repeating failure gets a *mechanical*
countermeasure, and rule 13 -- bounded, one small check not a framework). The
"invariant-describing prose drift" pattern
(``work/notes/2026-09-01-invariant-prose-drift-safeguard-design.md``) has hit
twice; once (PR #225 -> ``coverage["memory_trust_gate_note"]``) it was pinned by
nothing and the independent review did not re-read a coverage note 230 lines
from the diff. Part A of the safeguard is a consistency test; this is Part B --
the forcing function that a *new* coverage note cannot be born unpinned.

It is the ``scripts/check_stale_no_caller_docstrings.py`` mould: AST-scoped,
a ``# noqa`` escape hatch, wired as one ``run:`` step in
``.github/workflows/review-evidence.yml``. It does **not** validate a note's
content (golden-string matching -- brittle, rejected in design); it enforces
the weaker, robust invariant: every ``coverage`` note is referenced by at least
one test string literal.

Scope: deliberately ``context_builder.py`` only (rule 13) -- the one file the
pattern has bitten twice.

Escape hatch: ``# noqa: coverage-note-pin`` on the note's line.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_BUILDER = REPO_ROOT / "runtime" / "context_builder.py"
PIN_FILES = (
    REPO_ROOT / "tests" / "test_context_builder.py",
    REPO_ROOT / "tests" / "test_memory_trust_gate.py",
    REPO_ROOT / "tests" / "test_skill_capability_manifest.py",
)

NOQA = "# noqa: coverage-note-pin"


def _is_note_key(name: str) -> bool:
    return name == "note" or name.endswith("_note")


def _coverage_notes(cb_path: Path) -> list[tuple[str, int]]:
    """(-note key name, 1-indexed line) for every string-valued ``*_note`` key
    in the ``coverage`` dict returned by ``build_context_plan``."""
    tree = ast.parse(cb_path.read_text(encoding="utf-8"), filename=str(cb_path))
    fn = next(
        (
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "build_context_plan"
        ),
        None,
    )
    if fn is None:  # pragma: no cover - build_context_plan always exists
        raise SystemExit(
            "check_coverage_note_pins: build_context_plan not found in "
            f"{cb_path} -- the coverage-dict location assumption is stale"
        )

    notes: list[tuple[str, int]] = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if not (isinstance(key, ast.Constant) and key.value == "coverage"):
                continue
            if not isinstance(value, ast.Dict):
                continue
            for ck, cv in zip(value.keys, value.values):
                if not (isinstance(ck, ast.Constant) and isinstance(ck.value, str)):
                    continue
                if not _is_note_key(ck.value):
                    continue
                if isinstance(cv, ast.Constant) and isinstance(cv.value, str):
                    notes.append((ck.value, ck.lineno))
    return notes


def _pinned_keys(pin_paths: tuple[Path, ...]) -> set[str]:
    """Every string used as a subscript key (``x["..."]``) anywhere in the pin
    files. A coverage note is "pinned" when a test reads it by key -- e.g.
    ``plan["coverage"]["memory_trust_gate_note"]`` -- so match the exact key
    string, not any substring (``"note"`` would otherwise match half the
    English in the file)."""
    seen: set[str] = set()
    for p in pin_paths:
        if not p.exists():
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                if isinstance(node.slice.value, str):
                    seen.add(node.slice.value)
    return seen


def find_unpinned(
    cb_path: Path = CONTEXT_BUILDER,
    pin_paths: tuple[Path, ...] = PIN_FILES,
) -> list[str]:
    cb_lines = cb_path.read_text(encoding="utf-8").splitlines()
    pinned = _pinned_keys(pin_paths)
    failures: list[str] = []
    for name, lineno in _coverage_notes(cb_path):
        # noqa on the key line or the line just above it
        window = cb_lines[max(lineno - 2, 0):lineno]
        if any(NOQA in ln for ln in window):
            continue
        # Pinned = some test reads this note by its exact key, e.g.
        # `plan["coverage"]["memory_trust_gate_note"]`.
        if name in pinned:
            continue
        try:
            rel = cb_path.relative_to(REPO_ROOT)
        except ValueError:  # pragma: no cover
            rel = cb_path
        failures.append(
            f"{rel}:{lineno}: coverage note {name!r} is not referenced by any "
            "test in "
            + ", ".join(p.name for p in pin_paths)
            + f" -- add a consistency assertion for it (Part A) or `{NOQA}` on "
            "its line if it is genuinely not an invariant claim."
        )
    return failures


def main() -> int:
    failures = find_unpinned()
    if failures:
        print("Unpinned context-builder coverage note(s):\n")
        print("\n\n".join(failures))
        return 1
    print("check_coverage_note_pins: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
