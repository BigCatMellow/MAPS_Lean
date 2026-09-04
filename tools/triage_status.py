#!/usr/bin/env python3
"""Read-only advisory status report for the triage / continuous-improvement loop.

Slice 2 of the triage standard
(`work/notes/2026-09-03-triage-core-standard-design.md` §5.5, §8). It scans
`work/coordination/FRICTION_LOG.md` (and Drift+ repair records under
`work/notes/`) and reports what a `playbook/ROADMAP_TRAJECTORY_CHECK.md` pass
must address. It NEVER edits a source file.

It is the mechanical backstop for the staleness bound in
`ROADMAP_TRAJECTORY_CHECK.md` §"Friction-log consumption": an entry that has been
`verified: UNVERIFIED` (or `countermeasure: none yet`) across N consecutive
trajectory passes is an automatic operator-escalation item. Without this the
bound is a remembered instruction, which §1 of the design note shows is not
enough.

Heuristics (advisory, deliberately simple):
- an entry is CLOSED when its body carries a ``**CLOSED`` marker line (the
  convention: a trajectory pass appends ``**CLOSED - <how>**`` as the final
  follow-up);
- an open entry is UNRESOLVED when its ``verified:`` field / any follow-up still
  says ``UNVERIFIED`` or its ``countermeasure:`` is ``none yet``;
- passes-seen = distinct ``trajectory check #<n>`` references in the entry body;
- an unresolved entry is OVERDUE when passes-seen >= N (default 3) or its age
  from the ``opened:`` anchor (falling back to the header date) exceeds
  --stale-days (default 21).

Exit status is 0 by default (advisory). ``--strict`` exits 1 when any entry is
overdue, for an optional future CI slice -- off by default per the design note
(§5.5 rejects CI-blocking now).
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

FRICTION_LOG = "work/coordination/FRICTION_LOG.md"
REPAIR_NOTE_GLOB = "work/notes/*repair*.md"
DEFAULT_STALE_PASSES = 3
DEFAULT_STALE_DAYS = 21
DRIFT_OR_WORSE = ("DRIFT", "BLOCKING", "STRUCTURAL")

_ENTRY_HEADER = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s+[—-]\s+(.+?)\s*$")
_OPENED = re.compile(r"^\s*-\s*opened:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_VERIFIED = re.compile(r"^\s*-\s*verified:\s*(.+?)\s*$", re.IGNORECASE)
_COUNTERMEASURE = re.compile(r"^\s*-\s*countermeasure[^:]*:\s*(.+?)\s*$", re.IGNORECASE)
_PASS_REF = re.compile(r"trajectory check #(\d+)", re.IGNORECASE)
_CLOSED_MARKER = re.compile(r"\*\*\s*CLOSED", re.IGNORECASE)
_SEVERITY = re.compile(r"^\s*-\s*severity:\s*`?([A-Za-z]+)`?", re.IGNORECASE)


@dataclass
class Entry:
    date: str
    title: str
    body: list[str] = field(default_factory=list)

    @property
    def opened(self) -> str:
        for line in self.body:
            m = _OPENED.match(line)
            if m:
                return m.group(1)
        return self.date

    @property
    def closed(self) -> bool:
        return any(_CLOSED_MARKER.search(line) for line in self.body)

    @property
    def unresolved(self) -> bool:
        if self.closed:
            return False
        text = "\n".join(self.body)
        if re.search(r"\bUNVERIFIED\b", text):
            return True
        for line in self.body:
            m = _COUNTERMEASURE.match(line)
            if m and m.group(1).strip().lower().startswith("none yet"):
                return True
        return False

    @property
    def passes_seen(self) -> int:
        return len({int(n) for n in _PASS_REF.findall("\n".join(self.body))})

    def age_days(self, today: date) -> int:
        try:
            opened = datetime.strptime(self.opened, "%Y-%m-%d").date()
        except ValueError:
            return 0
        return (today - opened).days

    def is_overdue(self, today: date, stale_passes: int, stale_days: int) -> bool:
        if not self.unresolved:
            return False
        return self.passes_seen >= stale_passes or self.age_days(today) > stale_days


@dataclass
class RepairNote:
    path: str
    severity: str
    has_countermeasure: bool
    has_regression_case: bool

    @property
    def incomplete(self) -> bool:
        return self.severity.upper() in DRIFT_OR_WORSE and not (
            self.has_countermeasure and self.has_regression_case
        )


def parse_friction_log(text: str) -> list[Entry]:
    entries: list[Entry] = []
    current: Entry | None = None
    for line in text.splitlines():
        header = _ENTRY_HEADER.match(line)
        if header:
            current = Entry(date=header.group(1), title=header.group(2))
            entries.append(current)
        elif current is not None:
            current.body.append(line)
    return entries


def parse_repair_note(path: Path) -> RepairNote:
    text = path.read_text(encoding="utf-8")
    severity = ""
    for line in text.splitlines():
        m = _SEVERITY.match(line)
        if m:
            severity = m.group(1)
            break
    lowered = text.lower()
    return RepairNote(
        path=str(path),
        severity=severity,
        has_countermeasure=("countermeasure" in lowered or "prevention" in lowered),
        has_regression_case=(
            "regression" in lowered or "freeze-case" in lowered or "frozen" in lowered
        ),
    )


@dataclass
class Report:
    total: int
    closed: int
    open_entries: list[Entry]
    unresolved: list[Entry]
    overdue: list[Entry]
    incomplete_repair_notes: list[RepairNote]

    def to_dict(self) -> dict:
        return {
            "friction_log": {
                "total": self.total,
                "closed": self.closed,
                "open": len(self.open_entries),
                "unresolved": [e.title for e in self.unresolved],
                "overdue": [
                    {
                        "title": e.title,
                        "opened": e.opened,
                        "passes_seen": e.passes_seen,
                    }
                    for e in self.overdue
                ],
            },
            "repair_notes_incomplete": [n.path for n in self.incomplete_repair_notes],
        }


def build_report(
    root: Path,
    *,
    today: date | None = None,
    stale_passes: int = DEFAULT_STALE_PASSES,
    stale_days: int = DEFAULT_STALE_DAYS,
) -> Report:
    today = today or date.today()
    log_path = root / FRICTION_LOG
    entries = parse_friction_log(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    closed = [e for e in entries if e.closed]
    open_entries = [e for e in entries if not e.closed]
    unresolved = [e for e in open_entries if e.unresolved]
    overdue = [
        e for e in unresolved if e.is_overdue(today, stale_passes, stale_days)
    ]
    repair_notes = [parse_repair_note(p) for p in sorted(root.glob(REPAIR_NOTE_GLOB))]
    incomplete = [n for n in repair_notes if n.incomplete]
    return Report(
        total=len(entries),
        closed=len(closed),
        open_entries=open_entries,
        unresolved=unresolved,
        overdue=overdue,
        incomplete_repair_notes=incomplete,
    )


def render(report: Report, stale_passes: int) -> str:
    lines = ["# Triage status (advisory - read-only)", ""]
    fl = report
    lines.append(
        f"FRICTION_LOG: {fl.total} entries - {fl.closed} closed, "
        f"{len(fl.open_entries)} open ({len(fl.unresolved)} unresolved)."
    )
    lines.append("")
    if fl.overdue:
        lines.append(
            f"## OVERDUE - operator-escalation candidates (>= {stale_passes} passes "
            "or past --stale-days)"
        )
        lines.append(
            "A trajectory pass MUST name each of these in its operator section and "
            "MUST NOT record a clean result until they are listed."
        )
        for e in fl.overdue:
            lines.append(
                f"- {e.title} (opened {e.opened}, {e.passes_seen} passes seen)"
            )
        lines.append("")
    unresolved_not_overdue = [e for e in fl.unresolved if e not in fl.overdue]
    if unresolved_not_overdue:
        lines.append("## Unresolved - needs a disposition this pass")
        for e in unresolved_not_overdue:
            lines.append(
                f"- {e.title} (opened {e.opened}, {e.passes_seen}/{stale_passes} passes)"
            )
        lines.append("")
    if fl.incomplete_repair_notes:
        lines.append("## Drift+ repair records missing a countermeasure or regression case")
        for n in fl.incomplete_repair_notes:
            lines.append(f"- {n.path} (severity {n.severity or 'UNKNOWN'})")
        lines.append("")
    if not (fl.overdue or unresolved_not_overdue or fl.incomplete_repair_notes):
        lines.append("Nothing open. The triage loop is current.")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path("."), help="repo root")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--stale-passes", type=int, default=DEFAULT_STALE_PASSES,
        help=f"passes UNVERIFIED before overdue (default {DEFAULT_STALE_PASSES})",
    )
    parser.add_argument(
        "--stale-days", type=int, default=DEFAULT_STALE_DAYS,
        help=f"age in days before overdue (default {DEFAULT_STALE_DAYS})",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="exit 1 when any entry is overdue (default: always exit 0)",
    )
    args = parser.parse_args(argv)

    report = build_report(
        args.root.resolve(),
        stale_passes=args.stale_passes,
        stale_days=args.stale_days,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render(report, args.stale_passes))
    return 1 if (args.strict and report.overdue) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
