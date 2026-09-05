"""Verify a committed, exact-head-bound review-evidence file exists for a PR.

Part of issue #61's independent-review-enforcement work (Option B from
work/notes/2026-08-17-independent-review-enforcement-design.md). This does
NOT prove a distinct identity wrote the review -- the same GitHub account
can commit the evidence file. What it does mechanically guarantee: a
review-shaped artifact exists, is part of the PR's own tree (not a mutable
comment), and is bound to the exact commit SHA of the reviewed code -- a
stale file left over from an earlier, different code state fails closed
automatically.

Required file: work/reviews/pr-<N>-review-evidence.md
Required fields (simple "key: value" lines, one per line, order-insensitive):
    reviewer: <non-empty identity string>
    head_sha: <the reviewed code commit -- see below>
    independent: true
    summary: <non-empty text>

Why head_sha isn't just "git rev-parse HEAD" of the checked-out commit:
a commit that adds/updates the evidence file necessarily changes its own
tree, so its own resulting SHA can never be predicted (let alone written
into that same commit's own tracked content) before the commit exists --
that's a hash self-reference no amount of git plumbing can satisfy, not a
bug in the reviewer's workflow. So this check instead walks HEAD backward
past any trailing run of commits whose entire diff touches only
work/reviews/ (evidence-only commits), and compares head_sha against the
first commit reached that changes anything else -- the actual reviewed
code state. A merge commit is never walked past. If a "would-be evidence"
commit also touches other files, it is NOT treated as evidence-only, so it
can't be used to sneak unreviewed changes in under an old head_sha.

Expected consequence, not a bug: because the walk-back stops at every merge
commit, each main-sync merge (or rebase) on a long-lived PR branch produces
a fresh reviewed-code head and therefore requires a fresh review-evidence
commit bound to it. That rebind churn (see
work/notes/2026-08-18-review-evidence-resync-classifier-friction.md and
INSIGHT-29a10ad4) is the price of the safety property above -- do NOT
"fix" it by loosening the walk-back to cross merge commits, which would
reopen exactly the hole this docstring describes.

Additive revalidation exception (does NOT touch the walk-back above): if
the evidence's head_sha does not equal the resolved reviewed-code head,
it can still pass if (a) head_sha is an ancestor of the reviewed-code head
and (b) the diff between head_sha and the reviewed-code head is empty --
i.e. literally nothing changed between what was reviewed and now, so there
is no unreviewed content to sneak in. This is unlike the walk-back hole,
which was about evidence-only commits masking real changes; a zero-diff
ancestor has no room to hide anything. See
playbook/MODEL_CAPABILITY_ROUTING.md's "Revalidation review tier" section.
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


def _reviewed_code_head(repo_root: Path, start: str) -> str:
    """Walk `start` backward past trailing evidence-only commits.

    A commit is "evidence-only" if it has exactly one parent and every path
    it changes relative to that parent is under work/reviews/. Merge commits
    and root commits are never walked past. See module docstring for why
    this indirection exists.
    """
    current = start
    while True:
        rev_list = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "--parents", "-n", "1", current],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()
        parents = rev_list[1:]
        if len(parents) != 1:
            return current  # root commit or merge commit -- stop here

        parent = parents[0]
        changed = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--name-only", parent, current],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        if changed and all(path.startswith("work/reviews/") for path in changed):
            current = parent
            continue
        return current


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", ancestor, descendant],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _diff_is_empty(repo_root: Path, old: str, new: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-only", old, new],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ""


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
    reviewed_head = _reviewed_code_head(repo_root, actual_head)
    claimed_head = fields["head_sha"].strip()
    if claimed_head != reviewed_head:
        if _is_ancestor(repo_root, claimed_head, reviewed_head) and _diff_is_empty(
            repo_root, claimed_head, reviewed_head
        ):
            return True, (
                f"review-evidence OK for {evidence_path}: revalidated by "
                f"tree-equality (head_sha {claimed_head} is an ancestor of "
                f"reviewed code head {reviewed_head} with an empty diff "
                f"between them -- nothing changed since the reviewed state)"
            )
        return False, (
            f"review-evidence head_sha ({claimed_head!r}) does not match "
            f"the reviewed code state ({reviewed_head!r}, resolved from "
            f"current HEAD {actual_head!r} by skipping any trailing "
            f"evidence-only commits) -- stale evidence from a prior code "
            f"state does not satisfy this check"
        )

    return True, f"review-evidence OK for {evidence_path}: code head {reviewed_head}"


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
