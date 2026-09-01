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

What it does (deliberately conservative -- a curated phrase list, one symbol
per hit, and only a real `symbol(` call counts):

1. Scan every `runtime/**/*.py` line for one of `STALE_PHRASES`.
2. Extract the symbol the phrase is about: the nearest backticked
   `` `symbol` `` / `` `symbol()` `` token earlier in the same docstring
   paragraph, else the nearest enclosing `def <name>(`.
3. Run `/usr/bin/grep -rn "<symbol>(" runtime/ --include='*.py'`, excluding
   the defining file and any `tests/` path. If a call site is found, FAIL and
   name `file:line`, the phrase, and the offending caller.

False-positive escape hatch: put `# noqa: stale-caller-check` on or within a
couple of lines of the phrase (same docstring / comment block). Use it when
the claim is genuinely narrower than a bare-name grep can see -- e.g. it is
about `Foo.bar` and `bar` is also an unrelated method elsewhere, or the
claim is explicitly historical ("had zero callers before this module").
"""

from __future__ import annotations

import re
import subprocess
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


def _symbol_for(lines: list[str], idx: int) -> str | None:
    """Best-effort symbol the stale phrase on line `idx` is documenting."""
    # 1. Nearest backticked symbol at or above the phrase, within the same
    #    contiguous non-blank block (a docstring paragraph / comment block).
    for j in range(idx, max(idx - 12, -1), -1):
        line = lines[j]
        if j != idx and not line.strip():
            break
        matches = _BACKTICK_SYMBOL.findall(line)
        if matches:
            # last one on the line == closest to the phrase
            return matches[-1].split(".")[-1]
    # 2. Fall back to the nearest enclosing `def`.
    for j in range(idx, -1, -1):
        m = _DEF_LINE.match(lines[j])
        if m:
            return m.group(1)
    return None


def _grep(symbol: str, runtime_dir: Path) -> str:
    for exe in ("/usr/bin/grep", "grep"):
        try:
            return subprocess.run(
                [exe, "-rn", f"{symbol}(", str(runtime_dir), "--include=*.py"],
                capture_output=True, text=True, check=False,
            ).stdout
        except FileNotFoundError:  # pragma: no cover
            continue
    raise RuntimeError("grep not found on PATH")


def _callers(symbol: str, defining_file: Path, runtime_dir: Path) -> list[str]:
    out = _grep(symbol, runtime_dir)
    hits = []
    for raw in out.splitlines():
        try:
            fpath, lineno, text = raw.split(":", 2)
        except ValueError:
            continue
        p = Path(fpath).resolve()
        if p == defining_file.resolve():
            continue
        if "tests" in p.parts:
            continue
        stripped = text.strip()
        if _DEF_LINE.match(stripped) or stripped.startswith(("#", "*", '"', "'")):
            continue
        # require it to look like an actual call, not a bare mention
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(symbol)}\s*\(", text):
            hits.append(f"{fpath}:{lineno}: {stripped}")
    return hits


def scan(runtime_dir: Path = RUNTIME_DIR, repo_root: Path = REPO_ROOT) -> list[str]:
    failures: list[str] = []
    for path in sorted(runtime_dir.rglob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            # Phrases wrap across lines in real docstrings ("...no production\n
            # caller..."), so match against this line joined with the next,
            # whitespace-collapsed.
            nxt = lines[idx + 1] if idx + 1 < len(lines) else ""
            prev = lines[idx - 1] if idx > 0 else ""
            window = re.sub(r"\s+", " ", f"{line} {nxt}".lower())
            prev_window = re.sub(r"\s+", " ", f"{prev} {line}".lower())
            phrase = next((p for p in STALE_PHRASES if p in window), None)
            if phrase is None:
                continue
            # Attribute each occurrence to exactly one line: if the previous
            # line's own 2-line window already contained this phrase, it was
            # (or will be) reported there.
            if phrase in prev_window:
                continue
            # Escape hatch: NOQA on a nearby line -- typically the closing
            # `"""` of the same docstring, which may be several wrapped
            # sentences (and blank lines) below the phrase.
            if any(NOQA in lines[k]
                   for k in range(max(idx - 3, 0), min(idx + 13, len(lines)))):
                continue
            symbol = _symbol_for(lines, idx)
            if not symbol:
                continue
            callers = _callers(symbol, path, runtime_dir)
            if callers:
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
