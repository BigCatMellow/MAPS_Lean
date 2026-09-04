import importlib.util
import pathlib
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "coordination_housekeeping.py"
)
_spec = importlib.util.spec_from_file_location("coordination_housekeeping", _MODULE_PATH)
housekeeping = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(housekeeping)  # type: ignore[union-attr]


def _pr(head_oid="sha-new", commits=None, comments=None):
    return {
        "headRefOid": head_oid,
        "commits": commits or [],
        "comments": comments or [],
    }


class HandoffEvidenceTests(unittest.TestCase):
    def test_no_commits_means_no_evidence(self):
        pr = _pr(commits=[], comments=[
            {"body": "MAPS HANDOFF -- READY", "createdAt": "2026-08-17T10:00:00Z"}
        ])
        self.assertFalse(housekeeping.has_handoff_evidence(pr))

    def test_comment_before_head_commit_does_not_count(self):
        # Handoff posted, then a force-push landed a new head commit after it.
        pr = _pr(
            head_oid="sha-new",
            commits=[{"oid": "sha-new", "committedDate": "2026-08-17T12:00:00Z"}],
            comments=[
                {"body": "MAPS HANDOFF -- READY", "createdAt": "2026-08-17T10:00:00Z"}
            ],
        )
        self.assertFalse(housekeeping.has_handoff_evidence(pr))

    def test_comment_after_head_commit_counts(self):
        pr = _pr(
            head_oid="sha-new",
            commits=[{"oid": "sha-new", "committedDate": "2026-08-17T10:00:00Z"}],
            comments=[
                {"body": "MAPS HANDOFF -- READY", "createdAt": "2026-08-17T12:00:00Z"}
            ],
        )
        self.assertTrue(housekeeping.has_handoff_evidence(pr))

    def test_head_oid_not_in_commits_list_fails_closed(self):
        # commits list is stale/truncated and doesn't contain the real head
        # -- must NOT fall back to guessing from an older listed commit.
        pr = _pr(
            head_oid="sha-real-head-not-listed",
            commits=[{"oid": "sha-old", "committedDate": "2026-08-17T09:00:00Z"}],
            comments=[
                {"body": "MAPS HANDOFF -- READY", "createdAt": "2026-08-17T12:00:00Z"}
            ],
        )
        self.assertFalse(housekeeping.has_handoff_evidence(pr))

    def test_body_marker_alone_no_longer_counts(self):
        pr = {
            "headRefOid": "sha-new",
            "commits": [{"oid": "sha-new", "committedDate": "2026-08-17T10:00:00Z"}],
            "comments": [],
            "body": "MAPS HANDOFF -- READY FOR INDEPENDENT REVIEW",
        }
        self.assertFalse(housekeeping.has_handoff_evidence(pr))


class RetargetOrphanedBasesTests(unittest.TestCase):
    def test_unambiguous_chain_resolves(self):
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "main"},
        ]
        merge_map = housekeeping._build_merge_map(merged)
        self.assertEqual(merge_map["agent/a"], ("main", 10))

    def test_reused_branch_name_is_ambiguous(self):
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "main"},
            {"number": 20, "headRefName": "agent/a", "baseRefName": "other"},
        ]
        merge_map = housekeeping._build_merge_map(merged)
        self.assertIsNone(merge_map["agent/a"])

    def test_retarget_skips_ambiguous_base(self):
        prs = [{"number": 99, "baseRefName": "agent/a"}]
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "main"},
            {"number": 20, "headRefName": "agent/a", "baseRefName": "other"},
        ]

        original_gh_json = housekeeping.gh_json
        housekeeping.gh_json = lambda *a, **k: merged
        try:
            retargeted = housekeeping.retarget_orphaned_bases(
                "owner/repo", prs, dry_run=True
            )
        finally:
            housekeeping.gh_json = original_gh_json
        self.assertEqual(retargeted, [])

    def test_retarget_resolves_unambiguous_chain(self):
        prs = [{"number": 99, "baseRefName": "agent/a"}]
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "main"},
        ]

        original_gh_json = housekeeping.gh_json
        housekeeping.gh_json = lambda *a, **k: merged
        try:
            retargeted = housekeeping.retarget_orphaned_bases(
                "owner/repo", prs, dry_run=True
            )
        finally:
            housekeeping.gh_json = original_gh_json
        self.assertEqual(retargeted, [99])

    def test_retarget_resolves_multi_hop_chain(self):
        # PR #99's base agent/a was merged into agent/b, which was itself
        # later merged into main.
        prs = [{"number": 99, "baseRefName": "agent/a"}]
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "agent/b"},
            {"number": 11, "headRefName": "agent/b", "baseRefName": "main"},
        ]

        original_gh_json = housekeeping.gh_json
        housekeeping.gh_json = lambda *a, **k: merged
        try:
            retargeted = housekeeping.retarget_orphaned_bases(
                "owner/repo", prs, dry_run=True
            )
        finally:
            housekeeping.gh_json = original_gh_json
        self.assertEqual(retargeted, [99])

    def test_retarget_skips_cycle(self):
        # Pathological/corrupt input: a merge-history cycle must not spin
        # forever and must not be silently treated as "nothing to do"
        # without any diagnostic.
        prs = [{"number": 99, "baseRefName": "agent/a"}]
        merged = [
            {"number": 10, "headRefName": "agent/a", "baseRefName": "agent/b"},
            {"number": 11, "headRefName": "agent/b", "baseRefName": "agent/a"},
        ]

        original_gh_json = housekeeping.gh_json
        housekeeping.gh_json = lambda *a, **k: merged
        try:
            retargeted = housekeeping.retarget_orphaned_bases(
                "owner/repo", prs, dry_run=True
            )
        finally:
            housekeeping.gh_json = original_gh_json
        self.assertEqual(retargeted, [])


class OpenPrsQueryTests(unittest.TestCase):
    def test_bulk_query_omits_comments_and_commits_and_enriches_per_pr(self):
        calls: list[tuple] = []

        def fake_gh_json(*args):
            calls.append(args)
            if args[:2] == ("pr", "list"):
                return [{"number": 7}]
            # per-PR enrichment
            return {
                "comments": [{"body": "hi"}],
                "commits": [{"oid": "abc"}],
            }

        original = housekeeping.gh_json
        housekeeping.gh_json = fake_gh_json
        try:
            prs = housekeeping.open_prs("owner/repo")
        finally:
            housekeeping.gh_json = original

        list_call = next(c for c in calls if c[:2] == ("pr", "list"))
        fields = list_call[list_call.index("--json") + 1]
        self.assertNotIn("comments", fields)
        self.assertNotIn("commits", fields)
        self.assertTrue(any(c[:2] == ("pr", "view") for c in calls))
        self.assertEqual(prs[0]["comments"], [{"body": "hi"}])
        self.assertEqual(prs[0]["commits"], [{"oid": "abc"}])


class WorktreeReportTests(unittest.TestCase):
    _PORCELAIN = (
        "worktree /repo\nHEAD aaa\nbranch refs/heads/main\n\n"
        "worktree /repo/.claude/worktrees/live\nHEAD bbb\nbranch refs/heads/feat\n\n"
        "worktree /tmp/claude-dead/wt\nHEAD ccc\ndetached\nprunable gitdir file points to non-existent location\n"
    )

    def test_parse_worktree_list(self):
        entries = housekeeping.parse_worktree_list(self._PORCELAIN)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0]["branch"], "main")
        self.assertIsNone(entries[2]["branch"])
        self.assertTrue(entries[2]["missing"])

    def test_annotate_flags_stale_and_gone(self):
        from datetime import datetime, timezone

        now = datetime(2026, 9, 3, tzinfo=timezone.utc)
        ages = {
            "/repo": "2026-09-03T00:00:00+00:00",
            "/repo/.claude/worktrees/live": "2026-07-01T00:00:00+00:00",
        }
        rows = housekeeping.annotate_worktrees(
            housekeeping.parse_worktree_list(self._PORCELAIN),
            ages.get,
            now,
            stale_days=14,
        )
        by_path = {r["path"]: r for r in rows}
        self.assertFalse(by_path["/repo"]["stale"])
        self.assertTrue(by_path["/repo/.claude/worktrees/live"]["stale"])
        self.assertTrue(by_path["/tmp/claude-dead/wt"]["gone"])
        self.assertFalse(by_path["/tmp/claude-dead/wt"]["stale"])


if __name__ == "__main__":
    unittest.main()
