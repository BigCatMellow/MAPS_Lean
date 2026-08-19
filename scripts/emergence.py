#!/usr/bin/env python3
"""Lightweight capture tool for the Emergence and Improvement (E/I) protocol.

Implements only what `playbook/EMERGENCE.md` calls for: a way to capture a
concise record of an insight, idea, or experiment -- observation, source/
context, potential value, and the smallest next test -- as a markdown file
under `work/<kind>s/`. It deliberately does NOT implement:

- Sequential ID allocation, file locks, or compaction. Each record gets a
  UUID-derived ID (`<PREFIX>-<8 hex>`), which makes collision races
  structurally impossible without any lock file -- a simpler mechanism than
  the counter-plus-lock approach it replaces.
- Promotion. `EMERGENCE.md` states "only an approved/promoted item can
  expand implementation scope" and promotion is a deliberate human decision
  that turns a captured idea into a real task doc via
  `playbook/TASK_LIFECYCLE.md`. This script has no `promote` command --
  promoting something means writing a task doc by hand, not running a tool.
- Staleness checks, validation passes, or an index/graph file. Records are
  plain markdown files; `list` reads them back directly from disk.

Usage:
    scripts/emergence.py capture insight --title "..." --observation "..." \
        --source "..." --value "..." --next-test "..."
    scripts/emergence.py list [insight|idea|experiment]
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KIND_PREFIXES = {
    "insight": "INSIGHT",
    "idea": "IDEA",
    "experiment": "EXPERIMENT",
}


def _kind_dir(kind: str) -> Path:
    return ROOT / "work" / f"{kind}s"


def _new_id(kind: str) -> str:
    prefix = KIND_PREFIXES[kind]
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _slugify(title: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:60] or "untitled"


def capture(
    kind: str,
    title: str,
    observation: str,
    source: str,
    value: str,
    next_test: str,
) -> Path:
    if kind not in KIND_PREFIXES:
        raise ValueError(
            f"unknown kind {kind!r}; must be one of {sorted(KIND_PREFIXES)}"
        )
    record_id = _new_id(kind)
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    out_dir = _kind_dir(kind)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{date_str}-{_slugify(title)}-{record_id}.md"
    out_path = out_dir / filename

    body = (
        f"# {record_id}: {title}\n\n"
        f"- Kind: `{kind}`\n"
        f"- Date: `{date_str}`\n"
        f"- ID: `{record_id}`\n\n"
        f"## Observation\n\n{observation}\n\n"
        f"## Source / context\n\n{source}\n\n"
        f"## Potential value\n\n{value}\n\n"
        f"## Smallest next test\n\n{next_test}\n\n"
        "## Promotion\n\n"
        "Not promoted. Promotion is a deliberate decision made by a human or "
        "task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an "
        "automated step of this script.\n"
    )
    out_path.write_text(body, encoding="utf-8")
    return out_path


def list_records(kind: str | None = None) -> list[dict[str, str]]:
    kinds = [kind] if kind else list(KIND_PREFIXES)
    records: list[dict[str, str]] = []
    for k in kinds:
        d = _kind_dir(k)
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            title = ""
            record_id = ""
            date_str = ""
            if lines and lines[0].startswith("# "):
                header = lines[0][2:]
                if ": " in header:
                    record_id, title = header.split(": ", 1)
                else:
                    record_id = header
            for line in lines:
                if line.startswith("- Date: "):
                    date_str = line.split("`")[1] if "`" in line else ""
                if line.startswith("- ID: ") and not record_id:
                    record_id = line.split("`")[1] if "`" in line else ""
            records.append(
                {
                    "id": record_id,
                    "title": title,
                    "kind": k,
                    "date": date_str,
                    "path": str(path),
                }
            )
    return records


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture and list Emergence and Improvement (E/I) records."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    cap = sub.add_parser("capture", help="capture a new insight/idea/experiment")
    cap.add_argument("kind", choices=sorted(KIND_PREFIXES))
    cap.add_argument("--title", required=True)
    cap.add_argument("--observation", required=True)
    cap.add_argument("--source", required=True)
    cap.add_argument("--value", required=True)
    cap.add_argument("--next-test", required=True)

    lst = sub.add_parser("list", help="list captured records")
    lst.add_argument(
        "kind", nargs="?", choices=sorted(KIND_PREFIXES), default=None
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "capture":
        path = capture(
            args.kind,
            args.title,
            args.observation,
            args.source,
            args.value,
            args.next_test,
        )
        print(f"captured {args.kind}: {path.relative_to(ROOT)}")
        return 0

    if args.command == "list":
        records = list_records(args.kind)
        if not records:
            print("(no records)")
            return 0
        for r in records:
            print(f"{r['id']}\t{r['kind']}\t{r['date']}\t{r['title']}")
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
