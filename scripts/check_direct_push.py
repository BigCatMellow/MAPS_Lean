"""Loudly flag any commit pushed to `main` with no associated merged PR.

Roadmap: 2nd occurrence of the `feedback_no_direct_main_push` pattern
(commit `ce198ae`, `work/notes/2026-09-12-roadmap-trajectory-check-29.md`
§2) -- branch protection on this repo's plan can be (and twice has been)
bypassed by an admin identity, so this cannot be a merge gate. It is
instead a post-hoc, loud, best-effort alert on `push` to `main`: it cannot
stop a direct push (the push has already landed by the time this workflow
runs), but it makes the violation visible immediately -- a failed
GitHub Actions run on `main`, naming the exact offending SHA and author --
instead of relying on an agent noticing and self-reporting it (or a human
finding it during the next roadmap trajectory check, as happened both
times so far).

Detection method: GitHub's "list pull requests associated with a commit"
API (`GET /repos/{owner}/{repo}/commits/{sha}/pulls`), queried via `gh api`.
This is the correct primitive for this check -- unlike a text/issue search,
it has no indexing lag and returns exactly the PR(s) GitHub itself
considers the commit to belong to (including squash-merged commits, which
this repo's merge tooling -- `scripts/opcmd_merge.py` -- always produces).
Verified empirically against this repo: PR #347's squash commit `5d6d567`
returns `{"number": 347, "merged_at": "..."}`; the direct-push commit
`ce198ae` returns an empty list.

A commit is flagged as a violation iff:
  * it has exactly one parent (a merge commit is always PR-covered already
    -- `review-evidence.yml` gates every PR merge -- so 2+-parent commits
    are skipped rather than redundantly re-checked here), AND
  * the associated-pulls API returns zero pull requests with a non-null
    `merged_at`.

This cannot be a merge gate (the push already landed), but the workflow
that runs it is still a real `push`-triggered GitHub Actions job with its
own pass/fail status on `main` -- a non-zero exit here fails that run and
shows up loudly as a red check against the commit, in notifications, and in
the repo's Actions tab, which is the "loud alert" this exists to provide.
It cannot revert the push or block anything retroactively.
`review-evidence.yml`'s existing `pull_request` trigger already handles the
actual PR-gating case; this script only ever runs against a `push` event to
`main`, after the fact.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run(args: list[str]) -> str:
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    return result.stdout


def _pushed_commits(repo_root: Path, before: str, after: str) -> list[str]:
    """Return the SHAs newly reachable from `after` but not `before`.

    A `before` of all zeros (GitHub's sentinel for "branch just created")
    means there is no prior state to diff against -- returns an empty list
    rather than treating the entire branch history as newly pushed.
    """
    if set(before) == {"0"}:
        return []
    output = _run(
        ["git", "-C", str(repo_root), "rev-list", f"{before}..{after}"]
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def _parent_count(repo_root: Path, sha: str) -> int:
    output = _run(
        ["git", "-C", str(repo_root), "rev-list", "--parents", "-n", "1", sha]
    )
    return len(output.split()) - 1


def _commit_summary(repo_root: Path, sha: str) -> tuple[str, str]:
    """Return (author, subject) for `sha`, best-effort."""
    output = _run(
        ["git", "-C", str(repo_root), "show", "-s", "--format=%an|%s", sha]
    )
    author, _, subject = output.strip().partition("|")
    return author, subject


def _has_merged_pr(repo: str, sha: str) -> bool:
    """True iff GitHub associates `sha` with at least one merged PR."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/commits/{sha}/pulls"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # A transient API/auth failure must not be reported as a violation --
        # fail open on the *detection* (loud) side, since this check is
        # advisory-only and a false VIOLATION would be a worse failure mode
        # than a missed one for a best-effort alert.
        return True
    try:
        pulls = json.loads(result.stdout)
    except json.JSONDecodeError:
        return True
    if not isinstance(pulls, list):
        return True
    return any(isinstance(p, dict) and p.get("merged_at") for p in pulls)


def find_violations(
    repo_root: Path, repo: str, before: str, after: str
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for sha in _pushed_commits(repo_root, before, after):
        if _parent_count(repo_root, sha) != 1:
            continue  # merge commit -- already PR-covered by review-evidence.yml
        if _has_merged_pr(repo, sha):
            continue
        author, subject = _commit_summary(repo_root, sha)
        violations.append({"sha": sha, "author": author, "subject": subject})
    return violations


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", help="git sha before the push (github.event.before)")
    parser.add_argument("after", help="git sha after the push (github.event.after)")
    parser.add_argument("--repo", required=True, help="OWNER/REPO, e.g. github.repository")
    parser.add_argument(
        "--repo-root", default=".", help="local git checkout to inspect (default: cwd)"
    )
    args = parser.parse_args(argv)

    violations = find_violations(
        Path(args.repo_root), args.repo, args.before, args.after
    )

    if not violations:
        print("No direct-to-main pushes found in this range.")
        return 0

    print(f"VIOLATION: {len(violations)} commit(s) on main with no associated merged PR:")
    for v in violations:
        print(f"  {v['sha']}  by {v['author']}  \"{v['subject']}\"")
    print(
        "See feedback_no_direct_main_push (memory) / "
        "work/notes/2026-09-12-roadmap-trajectory-check-29.md §2: "
        "main should always be reached via a merged PR, even for docs-only "
        "notes. Branch protection can be admin-bypassed, so this check is "
        "advisory-only -- it cannot undo the push, only surface it loudly."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
