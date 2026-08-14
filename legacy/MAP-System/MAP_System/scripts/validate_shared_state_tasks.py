#!/usr/bin/env python3
"""Validate the active-lane table in current-state.md against map.db.

TASK-276 / INS-0040. Hand-maintained shared state is the one MAP mirror with no
checker: `validate_shared_state.py` checks the nine HPOM metadata fields,
`validate_task_mirrors.py` checks SQLite against `tasks/*.json` and the task
graph, and nothing checks whether the status CLAIMS in the body of
`shared/current-state.md` are true. That table is the status surface humans and
agents read first, and it drifted from `map.db` four times in one day.

SCOPE IS DELIBERATELY NARROW. Only the numbered rows of the designated
active-lane table are matched. INS-0040 records that a validator regexing every
`TASK-NNN` mention across `shared/` would fire constantly on legitimate
historical prose, decision-era context, and timestamped snapshots, then be
disabled -- leaving the project worse off than with no check at all. Free prose
is never matched, and neither is any other table in the file.

Parsing rules are IDEA-0029's P1 block, decided before implementation:

1. The leading uppercase token of the state cell is the status compared against
   `tasks.status` (`READY, policy-gated` compares as `READY`).
2. The trailing annotation is preserved and reported, never silently dropped.
3. An unrecognised status token is an ERROR, not a skip.
4. Coverage is guarded by row count, not just by zero rows: every numbered row
   in the table must parse to a comparable status, and any shortfall is an
   ERROR. A zero-row match is also an ERROR.

Usage:
    python3 MAP_System/scripts/validate_shared_state_tasks.py
        [--state-file PATH] [--db PATH] [--heading TEXT]

Exit codes:
    0  every row in the designated table matches map.db
    1  drift, a malformed row, or a coverage/format failure
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = ROOT / "shared" / "current-state.md"
DEFAULT_DB = ROOT / "map.db"

# The table is designated by its heading. The heading carries a revision
# timestamp, so match the prefix and not the whole line.
DEFAULT_HEADING = "## Active Execution Lanes"

# Canonical status vocabulary. Kept in sync with CANONICAL_STATUSES in
# scripts/validate_task_schema.py, which is the source of truth;
# tests/test_validate_shared_state_tasks.py fails if the two sets diverge.
CANONICAL_STATUSES = {
    "READY", "IN_PROGRESS", "SUBMITTED", "REVIEW", "CHANGES_REQUESTED",
    "BLOCKED", "CONFLICT", "APPROVED", "RELEASED", "DONE", "RETIRED",
}

# A candidate row is any table row in the region whose first cell is a row
# number. Deliberately wider than "row number AND task id": a numbered row that
# has lost its task id must be an error, not an uncounted skip (rule 4).
CANDIDATE_ROW = re.compile(r"^\|\s*\d+\s*\|")
TASK_ID = re.compile(r"TASK-\d+")
STATUS_TOKEN = re.compile(r"^([A-Z][A-Z_]*)")


@dataclass(frozen=True)
class Finding:
    """One problem with the designated table. `kind` is DRIFT or ERROR."""

    kind: str
    file: str
    line: int | None
    task_id: str | None
    claimed: str | None
    actual: str | None
    annotation: str
    message: str

    def format(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        parts = [f"{self.kind} {where}"]
        if self.task_id:
            parts.append(self.task_id)
        detail = self.message
        if self.claimed is not None and self.actual is not None:
            detail = f"claims {self.claimed}, map.db has {self.actual}"
        if self.annotation:
            detail += f" (row annotation: {self.annotation!r})"
        parts.append(detail)
        return ": ".join(parts)


def find_table_region(lines: list[str], heading: str) -> tuple[int, int] | None:
    """Return (start, end) line indices of the designated table's section.

    The region runs from the heading to the next Markdown heading of any level,
    which is what keeps the adjacent "Worker / Model Fit" table out of scope.
    """
    start = None
    for index, line in enumerate(lines):
        if line.startswith(heading):
            start = index
            break
    if start is None:
        return None

    for index in range(start + 1, len(lines)):
        if lines[index].startswith("#"):
            return start, index
    return start, len(lines)


def strip_cell(cell: str) -> str:
    """Drop Markdown emphasis and code ticks so cell text can be compared."""
    return cell.strip().strip("`*_ ").strip()


def parse_row(line: str) -> tuple[str | None, str | None, str, str | None]:
    """Parse one candidate row.

    Returns (task_id, status_token, annotation, error). `error` is None when the
    row parsed cleanly.
    """
    cells = [strip_cell(cell) for cell in line.strip().strip("|").split("|")]
    if len(cells) < 3:
        return None, None, "", "malformed row: fewer than 3 cells"

    task_match = TASK_ID.search(cells[1])
    if not task_match:
        return None, None, "", f"malformed row: no TASK-NNN id in task cell {cells[1]!r}"
    task_id = task_match.group(0)

    state_cell = cells[2]
    if not state_cell:
        return task_id, None, "", "malformed row: empty state cell"

    token_match = STATUS_TOKEN.match(state_cell)
    if not token_match:
        return task_id, None, "", f"malformed row: no leading status token in {state_cell!r}"
    token = token_match.group(1)

    # Rule 2: keep the annotation. It is operator-meaningful context about a
    # gate, not a claim about lifecycle state, so it is reported but not
    # compared.
    annotation = state_cell[len(token):].strip().lstrip(",").strip()

    if token not in CANONICAL_STATUSES:
        return task_id, None, annotation, f"unrecognised status token {token!r}"

    return task_id, token, annotation, None


def load_statuses(db_path: Path) -> dict[str, str]:
    """Read task statuses from map.db. Read-only; this validator never writes."""
    uri = f"file:{db_path}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        return {row[0]: row[1] for row in conn.execute("SELECT task_id, status FROM tasks")}


def validate(
    state_path: Path,
    db_path: Path,
    heading: str = DEFAULT_HEADING,
) -> list[Finding]:
    """Compare every numbered row of the designated table against map.db."""
    display = str(state_path)

    def error(message: str, *, line: int | None = None, task_id: str | None = None,
              annotation: str = "") -> Finding:
        return Finding("ERROR", display, line, task_id, None, None, annotation, message)

    try:
        text = state_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [error(f"unreadable state file: {exc}")]

    lines = text.splitlines()
    region = find_table_region(lines, heading)
    if region is None:
        return [error(f"designated table heading not found: {heading!r}")]

    start, end = region
    candidates = [
        (index + 1, lines[index])
        for index in range(start, end)
        if CANDIDATE_ROW.match(lines[index])
    ]

    # Criterion 3: a format change that matches nothing must fail loudly rather
    # than silently approve.
    if not candidates:
        return [error(
            f"no numbered rows matched under {heading!r} -- the table format changed "
            "or the table is gone; refusing to report a silent pass",
            line=start + 1,
        )]

    try:
        actual_statuses = load_statuses(db_path)
    except sqlite3.Error as exc:
        return [error(f"cannot read map.db read-only at {db_path}: {exc}")]

    findings: list[Finding] = []
    compared = 0

    for line_no, line in candidates:
        task_id, claimed, annotation, parse_error = parse_row(line)
        if parse_error is not None:
            findings.append(error(parse_error, line=line_no, task_id=task_id,
                                  annotation=annotation))
            continue

        assert task_id is not None and claimed is not None
        actual = actual_statuses.get(task_id)
        if actual is None:
            findings.append(error(f"{task_id} is not in map.db", line=line_no,
                                  task_id=task_id, annotation=annotation))
            continue

        compared += 1
        if claimed != actual:
            findings.append(Finding(
                "DRIFT", display, line_no, task_id, claimed, actual, annotation,
                "status claim does not match map.db",
            ))

    # Rule 4: coverage is measured, not assumed. The per-row errors above
    # already explain any shortfall; this is the summary that makes shrinking
    # coverage visible even if a future code path skips a row quietly.
    if compared < len(candidates):
        findings.append(error(
            f"coverage shortfall: {len(candidates)} numbered row(s) in the table, "
            f"{compared} compared against map.db",
            line=start + 1,
        ))

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument(
        "--heading",
        default=DEFAULT_HEADING,
        help=f"heading prefix designating the table (default: {DEFAULT_HEADING!r})",
    )
    args = parser.parse_args(argv)

    findings = validate(Path(args.state_file), Path(args.db), args.heading)

    for finding in findings:
        print(f"  {finding.format()}")

    drift = sum(1 for finding in findings if finding.kind == "DRIFT")
    errors = sum(1 for finding in findings if finding.kind == "ERROR")

    if not findings:
        print(f"  OK   {args.state_file}: active-lane table matches map.db")
        return 0

    print(f"\n{drift} drifted row(s). {errors} error(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
