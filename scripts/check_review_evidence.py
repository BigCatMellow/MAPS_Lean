"""Verify a committed, exact-head-bound review-evidence file exists for a PR.

Part of issue #61's independent-review-enforcement work (Option B from
work/notes/2026-08-17-independent-review-enforcement-design.md). This does
NOT prove a distinct identity wrote the review -- the same GitHub account
can commit the evidence file. What it does mechanically guarantee: a
review-shaped artifact exists, is part of the PR's own tree (not a mutable
comment), and is bound to the exact commit SHA being merged -- a stale file
left over from an earlier, different head fails closed automatically.

Required file: work/reviews/pr-<N>-review-evidence.md
Required fields (simple "key: value" lines, one per line, order-insensitive):
    reviewer: <non-empty identity string>
    head_sha: <must equal the exact current HEAD commit>
    independent: true
    summary: <non-empty text>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_FIELD_RE = re.compile(r"^([a-z_]+):\s*(.+)$")
_REQUIRED_FIELDS = {"reviewer", "head_sha", "independent", "summary"}


def _current_head_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _parse_evidence(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = _FIELD_RE.match(line.strip())
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def check(pr_number: str, repo_root: Path) -> tuple[bool, str]:
    evidence_path = repo_root / "work" / "reviews" / f"pr-{pr_number}-review-evidence.md"
    if not evidence_path.is_file():
        return False, f"missing required review-evidence file: {evidence_path}"

    fields = _parse_evidence(evidence_path.read_text(encoding="utf-8"))
    missing = _REQUIRED_FIELDS - set(fields)
    if missing:
        return False, f"review-evidence file missing fields: {sorted(missing)}"

    if not fields["reviewer"]:
        return False, "review-evidence 'reviewer' must be non-empty"
    if not fields["summary"]:
        return False, "review-evidence 'summary' must be non-empty"
    if fields["independent"].strip().lower() != "true":
        return False, "review-evidence 'independent' must be exactly 'true'"

    actual_head = _current_head_sha(repo_root)
    claimed_head = fields["head_sha"].strip()
    if claimed_head != actual_head:
        return False, (
            f"review-evidence head_sha ({claimed_head!r}) does not match "
            f"actual current HEAD ({actual_head!r}) -- stale evidence from a "
            f"prior commit does not satisfy this check"
        )

    return True, f"review-evidence OK for {evidence_path} at head {actual_head}"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_review_evidence.py <pr_number>", file=sys.stderr)
        return 2
    pr_number = sys.argv[1].strip()
    if not pr_number.isdigit():
        print(f"error: pr_number must be numeric, got {pr_number!r}", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    ok, message = check(pr_number, repo_root)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
