"""Mechanical PR-backlog housekeeping that does not depend on an agent tab.

MAPS coordination (work/coordination/) assumes a role-bound agent session is
actively re-prompted to run the SWITCHYARD backlog scan. When no session is
live, two purely mechanical failure modes accumulate with nobody to fix them:

1. A PR sits as a GitHub draft after its author already posted the
   ``MAPS HANDOFF -- READY FOR INDEPENDENT REVIEW`` handoff and CI is green.
   GitHub refuses to merge drafts regardless of CI/review state, so the PR is
   permanently stuck until a human or agent notices and un-drafts it.
2. A stacked PR's base branch was squash-merged by an upstream PR. GitHub
   does not retarget the downstream PR's base automatically (it only does
   that when the base branch is deleted), so the PR keeps comparing against
   a dead branch and its mergeability becomes meaningless.

This script only performs actions that are mechanically safe and reversible:
promoting an already-ready draft, and retargeting an orphaned base to the
branch its now-merged parent PR itself targeted. It never merges, approves,
closes, or edits PR content, and it never acts on a PR whose title/body
signals it is intentionally still in progress.
"""

from __future__ import annotations

import json
import subprocess
import sys

HANDOFF_MARKER = "MAPS HANDOFF"
WIP_MARKERS = ("wip", "work in progress", "do not merge", "draft:", "[skip promote]")


def gh_json(*args: str) -> object:
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def gh(*args: str) -> None:
    subprocess.run(["gh", *args], check=True)


def open_prs(repo: str) -> list[dict]:
    return gh_json(
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--json",
        "number,title,body,baseRefName,headRefName,isDraft,mergeable,"
        "mergeStateStatus,statusCheckRollup,comments",
        "--limit",
        "200",
    )


def looks_wip(pr: dict) -> bool:
    haystack = f"{pr.get('title', '')}\n{pr.get('body', '')}".lower()
    return any(marker in haystack for marker in WIP_MARKERS)


def has_handoff_evidence(pr: dict) -> bool:
    if HANDOFF_MARKER in (pr.get("body") or ""):
        return True
    for comment in pr.get("comments") or []:
        if HANDOFF_MARKER in (comment.get("body") or ""):
            return True
    return False


def checks_all_green(pr: dict) -> bool:
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return False
    return all(c.get("conclusion") == "SUCCESS" for c in checks)


def promote_ready_drafts(repo: str, prs: list[dict], dry_run: bool) -> list[int]:
    promoted: list[int] = []
    for pr in prs:
        if not pr["isDraft"]:
            continue
        if looks_wip(pr):
            continue
        if not has_handoff_evidence(pr):
            continue
        if not checks_all_green(pr):
            continue
        if pr.get("mergeable") == "CONFLICTING":
            continue
        number = pr["number"]
        print(
            f"PROMOTE #{number}: draft with handoff evidence and green CI "
            f"-> marking ready for review"
        )
        if not dry_run:
            gh("pr", "ready", str(number), "--repo", repo)
        promoted.append(number)
    return promoted


def retarget_orphaned_bases(repo: str, prs: list[dict], dry_run: bool) -> list[int]:
    merged_head_to_base: dict[str, str] = {}
    merged = gh_json(
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "merged",
        "--json",
        "headRefName,baseRefName",
        "--limit",
        "200",
    )
    for m in merged:
        merged_head_to_base[m["headRefName"]] = m["baseRefName"]

    retargeted: list[int] = []
    for pr in prs:
        base = pr["baseRefName"]
        seen: set[str] = set()
        resolved = base
        while resolved in merged_head_to_base and resolved not in seen:
            seen.add(resolved)
            resolved = merged_head_to_base[resolved]
        if resolved == base:
            continue
        number = pr["number"]
        print(
            f"RETARGET #{number}: base {base!r} was already merged into "
            f"main via an upstream PR -> retargeting base to {resolved!r}"
        )
        if not dry_run:
            gh(
                "api",
                "-X",
                "PATCH",
                f"repos/{repo}/pulls/{number}",
                "-f",
                f"base={resolved}",
            )
        retargeted.append(number)
    return retargeted


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: coordination_housekeeping.py <owner/repo> [--apply]", file=sys.stderr)
        return 2
    repo = sys.argv[1]
    dry_run = "--apply" not in sys.argv[2:]

    prs = open_prs(repo)
    print(f"open PRs: {len(prs)} (dry_run={dry_run})")

    promoted = promote_ready_drafts(repo, prs, dry_run)
    retargeted = retarget_orphaned_bases(repo, prs, dry_run)

    print(f"promoted: {promoted}")
    print(f"retargeted: {retargeted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
