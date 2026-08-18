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

Both mechanisms bind to exact-head/exact-identity evidence rather than
mutable text or branch names:

- ``has_handoff_evidence`` only accepts a handoff *comment* posted at or
  after the current head commit's timestamp. A handoff comment left before
  a force-push added new, unreviewed commits no longer counts as evidence
  for the new head.
- ``retarget_orphaned_bases`` refuses to guess when a head branch name maps
  to more than one distinct base across merged PRs (a reused branch name).
  It only auto-retargets when the branch name's merge history is
  unambiguous, and always reports the exact merged PR number it relied on.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

HANDOFF_MARKER = "MAPS HANDOFF"
WIP_MARKERS = ("wip", "work in progress", "do not merge", "draft:", "[skip promote]")


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


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
        "number,title,body,baseRefName,headRefName,headRefOid,isDraft,mergeable,"
        "mergeStateStatus,statusCheckRollup,comments,commits",
        "--limit",
        "200",
    )


def looks_wip(pr: dict) -> bool:
    haystack = f"{pr.get('title', '')}\n{pr.get('body', '')}".lower()
    return any(marker in haystack for marker in WIP_MARKERS)


def _head_commit_timestamp(pr: dict) -> datetime | None:
    commits = pr.get("commits") or []
    head_oid = pr.get("headRefOid")
    if head_oid:
        # Only trust a commit that is explicitly the current head. If the
        # commits list is truncated/stale and doesn't contain headRefOid,
        # fail closed rather than guessing from an older listed commit --
        # that guess is exactly the stale-evidence gap this binding exists
        # to close.
        for commit in commits:
            if commit.get("oid") == head_oid:
                ts = commit.get("committedDate") or commit.get("authoredDate")
                return _parse_ts(ts) if ts else None
        return None
    if commits:
        ts = commits[-1].get("committedDate") or commits[-1].get("authoredDate")
        if ts:
            return _parse_ts(ts)
    return None


def has_handoff_evidence(pr: dict) -> bool:
    head_ts = _head_commit_timestamp(pr)
    if head_ts is None:
        # No reliable commit timestamp to bind against -- refuse to trust
        # any evidence rather than silently accepting a possibly-stale one.
        return False
    for comment in pr.get("comments") or []:
        if HANDOFF_MARKER not in (comment.get("body") or ""):
            continue
        created_at = comment.get("createdAt")
        if not created_at:
            continue
        if _parse_ts(created_at) >= head_ts:
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


def _build_merge_map(merged: list[dict]) -> dict[str, tuple[str, int] | None]:
    """Map merged headRefName -> (baseRefName, PR number), or None if the
    branch name was reused across merges with different bases (ambiguous:
    the name alone no longer identifies a single merge, so it is unsafe to
    resolve automatically)."""
    by_head: dict[str, tuple[str, int]] = {}
    ambiguous: set[str] = set()
    for m in merged:
        head = m["headRefName"]
        entry = (m["baseRefName"], m["number"])
        if head in by_head and by_head[head][0] != entry[0]:
            ambiguous.add(head)
            continue
        by_head[head] = entry
    result: dict[str, tuple[str, int] | None] = {h: v for h, v in by_head.items()}
    for head in ambiguous:
        result[head] = None
    return result


def retarget_orphaned_bases(repo: str, prs: list[dict], dry_run: bool) -> list[int]:
    merged = gh_json(
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "merged",
        "--json",
        "number,headRefName,baseRefName",
        "--limit",
        "200",
    )
    merge_map = _build_merge_map(merged)

    retargeted: list[int] = []
    for pr in prs:
        base = pr["baseRefName"]
        number = pr["number"]
        seen: set[str] = set()
        resolved = base
        via_prs: list[int] = []
        blocked_reason: str | None = None
        while resolved in merge_map and resolved not in seen:
            entry = merge_map[resolved]
            if entry is None:
                blocked_reason = (
                    f"base {resolved!r} was merged more than once under "
                    f"different parent bases (reused branch name)"
                )
                break
            seen.add(resolved)
            resolved, merged_pr_number = entry
            via_prs.append(merged_pr_number)
        else:
            if resolved in merge_map:
                # Loop exited because `resolved` was already in `seen`,
                # i.e. the chain cycled back on itself.
                blocked_reason = (
                    f"base-resolution chain from {base!r} revisited "
                    f"{resolved!r} (cycle in merge history)"
                )

        if blocked_reason is not None:
            print(
                f"SKIP #{number}: {blocked_reason} -> refusing to guess, "
                f"needs human resolution"
            )
            continue
        if resolved == base:
            continue
        print(
            f"RETARGET #{number}: base {base!r} was already merged into "
            f"main via upstream PR(s) {via_prs} -> retargeting base to "
            f"{resolved!r}"
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
