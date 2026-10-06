#!/usr/bin/env python3
"""Pre-dispatch freshness check for roadmap-row task briefs.

Before dispatching a task framed as "do X per row <N>" or "implement note
<path>", run this to catch the recurring failure mode where the dispatch
brief cites a design/exercise note as "current state" while the roadmap row
itself has a *later* "Updated <date>" entry the brief never read — i.e. the
work the brief wants done was already done. See memory
feedback_dispatched_already_merged_work.md (3 occurrences: session 13, 27,
and the 6.22 withhold/deny dispatch this script exists because of).

This is a read-only advisory check, not a CI gate — there's no way to know
a dispatch brief's cited note automatically, so it's meant to be run by
hand (or by an agent) immediately before dispatching, not wired into CI.

Usage:
    scripts/check_dispatch_freshness.py <row-id> [--cited-note PATH]

Examples:
    scripts/check_dispatch_freshness.py 6.22
    scripts/check_dispatch_freshness.py 6.4 --cited-note work/notes/2026-09-09-6.4-destructive-action-first-exposure.md

Behavior:
    - Extracts the target row from work/roadmaps/CAPABILITY_CHECKLIST.md.
    - Finds every "Updated YYYY-MM-DD" (or "Re-verified YYYY-MM-DD")
      occurrence within that row's cell, prints them in order, and reports
      the latest one.
    - If --cited-note is given, parses the date out of its filename
      (YYYY-MM-DD prefix convention) and compares: if the row has an
      "Updated" entry dated *after* the note, prints a loud warning to read
      that update before dispatching anything from the note.
    - Exit code 1 on a detected staleness warning, 0 otherwise (including
      when the row/note isn't found — this is advisory, fail open).
"""
import argparse
import re
import sys
from pathlib import Path

CHECKLIST = Path(__file__).resolve().parent.parent / "work/roadmaps/CAPABILITY_CHECKLIST.md"
DATE_RE = re.compile(r"\b(?:Updated|Re-verified)\s+(\d{4}-\d{2}-\d{2})\b")
NOTE_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def find_row_cell(text: str, row_id: str) -> str | None:
    prefix = f"| {row_id} |"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row_id", help='Roadmap row id, e.g. "6.22"')
    ap.add_argument("--cited-note", help="Path to the note a dispatch brief cites as current state")
    args = ap.parse_args()

    if not CHECKLIST.exists():
        print(f"[advisory] {CHECKLIST} not found — skipping check.", file=sys.stderr)
        return 0

    text = CHECKLIST.read_text()
    cell = find_row_cell(text, args.row_id)
    if cell is None:
        print(f"[advisory] row '{args.row_id}' not found in {CHECKLIST.name} — skipping check.", file=sys.stderr)
        return 0

    dates = DATE_RE.findall(cell)
    status_match = re.match(rf"\| {re.escape(args.row_id)} \| [^|]+ \| ([^|]+) \|", cell)
    status = status_match.group(1).strip() if status_match else "?"

    print(f"Row {args.row_id} — status: {status}")
    if dates:
        print(f"Update dates found in row (in document order): {', '.join(dates)}")
        print(f"LATEST update in row: {dates[-1]}")
    else:
        print("No 'Updated <date>' / 'Re-verified <date>' markers found in this row.")

    if args.cited_note:
        note_path = Path(args.cited_note)
        m = NOTE_DATE_RE.search(note_path.name)
        if not m:
            print(f"[advisory] could not parse a date out of note filename '{note_path.name}'.", file=sys.stderr)
            return 0
        note_date = m.group(1)
        print(f"Cited note date (from filename): {note_date}")
        later = [d for d in dates if d > note_date]
        if later:
            print(
                f"\n*** WARNING: row {args.row_id} has update(s) dated AFTER the cited note "
                f"({', '.join(later)} > {note_date}). Read that later update in the row "
                f"before dispatching anything from the note — the work it describes may "
                f"already be done. ***",
                file=sys.stderr,
            )
            return 1
        print("Cited note is at or after the row's latest update — no staleness detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
