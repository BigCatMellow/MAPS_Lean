from __future__ import annotations

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
ACTIVE_ROOTS = ("runtime", "tests", "scripts", ".github")
ROOT_FILES = (
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "Makefile",
)
EXECUTABLE_SUFFIXES = {
    ".py",
    ".sh",
    ".bash",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".ini",
    ".cfg",
    ".txt",
}
HISTORICAL_SUFFIXES = EXECUTABLE_SUFFIXES | {".md"}

# These are executable/runtime dependency markers, not a ban on historical
# discussion of legacy in documentation/review records.
FORBIDDEN_TEXT = (
    ("legacy path", re.compile(r"(?<![A-Za-z0-9_])legacy/")),
    ("runtime preservation snapshot", re.compile(r"migration/legacy-runtime-source")),
    ("knowledge preservation snapshot", re.compile(r"migration/legacy-knowledge-source")),
    ("old MAP_System path", re.compile(r"\bMAP_System\b")),
    ("old MultiAgentProject path", re.compile(r"\bMultiAgentProject\b")),
)

HISTORICAL_EXCLUDES = (
    "legacy/",
    "migration/legacy-runtime-source/",
    "migration/legacy-knowledge-source/",
)


def active_files() -> list[Path]:
    files: set[Path] = set()
    for root_name in ACTIVE_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if (
                path.is_file()
                and path.resolve() != SELF
                and path.suffix.lower() in EXECUTABLE_SUFFIXES
            ):
                files.add(path)
    for name in ROOT_FILES:
        path = ROOT / name
        if path.is_file():
            files.add(path)
    return sorted(files)


def python_legacy_imports(path: Path, text: str) -> list[str]:
    if path.suffix != ".py":
        return []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return [f"cannot AST-parse active Python file: {exc}"]
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "legacy" or alias.name.startswith("legacy."):
                    hits.append(f"imports legacy module {alias.name!r} on line {node.lineno}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "legacy" or module.startswith("legacy."):
                hits.append(f"imports from legacy module {module!r} on line {node.lineno}")
    return hits


def _negative_test_assertion(rel: str, text: str, match_start: int) -> bool:
    """Allow tests whose only reference is an explicit absence assertion."""
    if not rel.startswith("tests/"):
        return False
    line_start = text.rfind("\n", 0, match_start) + 1
    line_end = text.find("\n", match_start)
    if line_end < 0:
        line_end = len(text)
    return "assertNotIn(" in text[line_start:line_end]


def active_dependency_failures() -> list[str]:
    failures: list[str] = []
    for path in active_files():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for detail in python_legacy_imports(path, text):
            failures.append(f"{rel}: {detail}")
        for label, pattern in FORBIDDEN_TEXT:
            for match in pattern.finditer(text):
                if _negative_test_assertion(rel, text, match.start()):
                    continue
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{rel}:{line}: {label}: {match.group(0)!r}")

    # Symlinks can hide a runtime dependency without leaving a textual import.
    for root_name in ACTIVE_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_symlink():
                continue
            rel = path.relative_to(ROOT).as_posix()
            try:
                target = path.resolve(strict=True)
            except FileNotFoundError:
                failures.append(f"{rel}: broken active symlink")
                continue
            try:
                target_rel = target.relative_to(ROOT).as_posix()
            except ValueError:
                failures.append(f"{rel}: active symlink escapes repository -> {target}")
                continue
            if target_rel == "legacy" or target_rel.startswith("legacy/"):
                failures.append(f"{rel}: active symlink targets legacy -> {target_rel}")
    return sorted(set(failures))


def historical_reference_summary() -> list[str]:
    refs: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.resolve() == SELF:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(
            rel == prefix.rstrip("/") or rel.startswith(prefix)
            for prefix in HISTORICAL_EXCLUDES
        ):
            continue
        if path.suffix.lower() not in HISTORICAL_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "legacy/" in text:
            refs.append(rel)
    return sorted(set(refs))


def main() -> int:
    active = active_files()
    failures = active_dependency_failures()
    historical = historical_reference_summary()

    print("MAPS legacy-removal dependency gate")
    print("===================================")
    print(f"active executable/config files scanned: {len(active)}")
    if failures:
        print("\nACTIVE LEGACY DEPENDENCIES: FAIL")
        for item in failures:
            print(f"- {item}")
    else:
        print("\nACTIVE LEGACY DEPENDENCIES: PASS")
        print("- no active runtime/test/script/workflow import or path dependency found")

    print("\nHistorical/provenance files still mentioning `legacy/` (allowed):")
    if historical:
        for item in historical:
            print(f"- {item}")
    else:
        print("- none")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
