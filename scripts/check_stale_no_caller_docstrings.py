"""Fail CI when a `runtime/**` docstring or comment still claims a symbol has
"no production caller" after a production caller was in fact added.

Why this exists (CLAUDE.md rule 20 -- a repeating failure gets a mechanical
safeguard, not another reactive fix). Twice an implementation PR added the
first production caller of a store/service method but left the method's
docstring asserting it has none:

- `runtime/recovery/production.py` -- `record_run_environment_evidence` said
  "zero production writers", false since PR #204; fixed reactively in #206.
- `runtime/state/skill_lifecycle_storage.py` --
  `record_skill_lifecycle_transition()` said "still has no production caller",
  false since PR #205 (`maps skill` CLI verbs), still stale at the time this
  check was written.

Memory: `feedback_stale_no_production_caller_docstrings`.

Dotted-resolution strengthening (3rd occurrence -- the 1st to slip past this
guard, found by reviewer `ledo` on PR #310, 2026-09-06). When the backticked
symbol is dotted (`` `Class.method` `` / `` `Class.method()` ``) the check now
KEEPS the class: a caller counts only if it is an attribute call `recv.method(
...)` whose bare-name receiver `recv` plausibly names an instance of `Class`
(case-insensitive substring either way -- `service` matches `HarnessService`;
`self`, `adapter`, `backend` do not). Attribute-chain receivers (`self.x`,
`a.b.c`) are excluded from the dotted match -- the noqa hatch covers the rare
real caller reachable only that way. Previously the class prefix was dropped,
so `` `HarnessService.send()` `` resolved to the bare symbol `send` and every
unrelated `.send(` in `runtime/` counted, forcing a blanket noqa that blinded
the check to a genuine new caller. Non-dotted claims are unaffected.

What it does (deliberately conservative -- a curated phrase list, one symbol
per hit, and only a real syntactic call counts):

1. Scan every non-test `runtime/**/*.py` for one of `STALE_PHRASES`, collapsing
   whitespace across line breaks so a phrase wrapped over two lines is found
   once (attributed to the line it starts on).
2. Extract the symbol the phrase is about: the closest backticked
   `` `symbol` `` / `` `symbol()` `` token that appears *before* the phrase on
   its line (or, failing that, on an earlier line of the same block), else the
   nearest enclosing `def <name>(`. A dotted `` `Class.method` `` resolves to
   the final attribute.
3. Parse every non-test `runtime/**/*.py` and look for an `ast.Call` whose
   callee name is that symbol -- excluding calls lexically inside the
   symbol's own function body (so plain recursion is not "a caller"). Calls
   in the *same module* as the docstring do count. If any is found, FAIL and
   name `file:line`, the phrase, and the offending caller.

False-positive escape hatch: put `# noqa: stale-caller-check` on or within a
dozen lines of the phrase (same docstring / comment block). Use it when the
claim is genuinely narrower than a bare-name match can see -- e.g. it is
about `Foo.bar` and `bar` is also an unrelated method elsewhere, or the
claim is explicitly historical ("had zero callers before this module").
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "runtime"

# Curated -- only phrasing that asserts *a symbol* has no production/runtime
# call or write site. Kept narrow on purpose: design notes about a dormant
# enum member with "no firing site" must NOT trip this.
STALE_PHRASES = (
    "no production caller",
    "no production callers",
    "zero production callers",
    "has no production writer",
    "have no production writer",
    "zero production writers",
    "no production writer",
    "no runtime caller",
    "no non-test caller",
    "no non-test callers",
    "not called in production",
    "no real production caller",
)

NOQA = "# noqa: stale-caller-check"

_BACKTICK_SYMBOL = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]*)(?:\(\))?`")
_DEF_LINE = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _symbol_for(lines: list[str], idx: int, phrase: str) -> tuple[str | None, str | None]:
    """Best-effort (method, class) the stale phrase (which *begins* on line
    `idx`) is documenting.

    Prefers the closest backticked token that sits *before* the phrase; a
    backtick after the phrase on the same line (e.g. "... has no production
    caller, unlike `OtherThing`") is ignored.

    `class` is non-None only when the winning backticked token is dotted
    (`` `Class.method` ``) -- callers are then matched against the receiver
    (see `_callers`). The returned `method` is always the bare final
    attribute, so failure messages and the recursion exclusion are unchanged.
    """
    first_word = phrase.split()[0]
    for j in range(idx, max(idx - 12, -1), -1):
        line = lines[j]
        if j != idx and not line.strip():
            break
        cut = len(line)
        if j == idx:
            pos = line.lower().find(phrase)
            if pos == -1:  # phrase wraps onto the next line
                pos = line.lower().find(f" {first_word} ")
                if pos == -1:
                    pos = line.lower().rfind(first_word)
            if pos != -1:
                cut = pos
        before = [m for m in _BACKTICK_SYMBOL.finditer(line) if m.start() < cut]
        if before:
            # last one before the phrase == closest to it
            token = before[-1].group(1)
            parts = token.split(".")
            if len(parts) >= 2:
                return parts[-1], parts[-2]
            return parts[-1], None
    # Fall back to the nearest enclosing `def` (never a dotted claim).
    for j in range(idx, -1, -1):
        m = _DEF_LINE.match(lines[j])
        if m:
            return m.group(1), None
    return None, None


def _phrase_line_starts(lines: list[str], phrase: str) -> list[int]:
    """Source line indexes on which `phrase` begins, after collapsing
    whitespace across line breaks so a phrase wrapped over two lines is found
    once, attributed to the line it starts on."""
    flat: list[str] = []
    origin: list[int] = []
    for i, ln in enumerate(lines):
        seg = re.sub(r"\s+", " ", ln.strip())
        if not seg:
            continue
        if flat:
            flat.append(" ")
            origin.append(i)
        for ch in seg:
            flat.append(ch)
            origin.append(i)
    text = "".join(flat).lower()
    out: list[int] = []
    k = text.find(phrase)
    while k != -1:
        out.append(origin[k])
        k = text.find(phrase, k + 1)
    return out


def _runtime_sources(runtime_dir: Path):
    for p in sorted(runtime_dir.rglob("*.py")):
        if "tests" in p.parts:
            continue
        try:
            src = p.read_text(encoding="utf-8")
            yield p, src.splitlines(), ast.parse(src, filename=str(p))
        except (SyntaxError, UnicodeDecodeError):  # pragma: no cover
            continue


def _callee_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _self_body_ranges(tree: ast.AST, symbol: str) -> list[tuple[int, int]]:
    """Line ranges of every `def <symbol>` body -- calls inside these are
    recursion, not a production caller."""
    ranges = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            ranges.append((node.lineno, getattr(node, "end_lineno", node.lineno)))
    return ranges


# Note: caller detection is purely AST (`ast.Call` nodes). An earlier version
# grepped `"<symbol>("` and then re-filtered hits with a call-shape regex; the
# regex was dead code (the grep already excluded bare mentions) and grep could
# not see a call inside the symbol's own defining file. AST fixes both and
# needs no such regex -- a bare mention, a string literal, or `x = symbol` is
# simply not a Call node.
def _receiver_matches_class(func: ast.expr, cls: str) -> bool:
    """True when `func` is `ast.Attribute` whose receiver is a bare `ast.Name`
    that plausibly refers to an instance of `cls`.

    Conservative heuristic (no type inference): the receiver id and the class
    name, both lowercased, must be substrings of one another. So `service`
    matches `HarnessService`, but `self`, `adapter`, `backend` and any
    attribute-chain receiver (`self.adapter`, `a.b.c`) do NOT -- those stay the
    noqa hatch's job.
    """
    if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
        return False
    recv = func.value.id.lower()
    target = cls.lower()
    return recv in target or target in recv


def _callers(symbol: str, runtime_dir: Path, receiver_class: str | None = None) -> list[str]:
    hits: list[str] = []
    for path, src_lines, tree in _runtime_sources(runtime_dir):
        skip = _self_body_ranges(tree, symbol)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _callee_name(node.func) != symbol:
                continue
            if receiver_class is not None and not _receiver_matches_class(
                node.func, receiver_class
            ):
                continue
            if any(lo <= node.lineno <= hi for lo, hi in skip):
                continue
            text = ""
            if 0 <= node.lineno - 1 < len(src_lines):
                text = src_lines[node.lineno - 1].strip()
            hits.append(f"{path}:{node.lineno}: {text}")
    return hits


def scan(runtime_dir: Path = RUNTIME_DIR, repo_root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    for path in sorted(runtime_dir.rglob("*.py")):
        if "tests" in path.parts:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for phrase in STALE_PHRASES:
            for idx in _phrase_line_starts(lines, phrase):
                # Escape hatch: NOQA on a nearby line -- typically the closing
                # `"""` of the same docstring, which may be several wrapped
                # sentences (and blank lines) below the phrase.
                if any(NOQA in lines[k]
                       for k in range(max(idx - 3, 0), min(idx + 13, len(lines)))):
                    continue
                symbol, receiver_class = _symbol_for(lines, idx, phrase)
                if not symbol:
                    continue
                callers = _callers(symbol, runtime_dir, receiver_class)
                if not callers:
                    continue
                rel = path.relative_to(repo_root)
                failures.append(
                    f"{rel}:{idx + 1}: says {phrase!r} about `{symbol}` but it "
                    f"has {len(callers)} production caller(s):\n    "
                    + "\n    ".join(callers)
                    + f"\n  Fix the docstring, or add `{NOQA}` if the claim is "
                    "genuinely narrower than the checker can see."
                )
    return failures


def main() -> int:
    failures = scan()
    if failures:
        print("Stale 'no production caller' docstring(s) found:\n")
        print("\n\n".join(failures))
        return 1
    print("check_stale_no_caller_docstrings: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
