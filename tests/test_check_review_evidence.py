import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_review_evidence.py"
)
_spec = importlib.util.spec_from_file_location("check_review_evidence", _MODULE_PATH)
crv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crv)  # type: ignore[union-attr]


def _init_repo(root: pathlib.Path) -> str:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


class CheckReviewEvidenceTests(unittest.TestCase):
    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            _init_repo(root)
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("missing required", msg)

    def test_valid_evidence_at_exact_head_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {head}\n"
                f"independent: true\n"
                f"summary: reviewed the diff, no findings\n",
                encoding="utf-8",
            )
            ok, msg = crv.check("99", root)
            self.assertTrue(ok, msg)

    def test_stale_head_sha_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                "reviewer: SENTINEL-A\n"
                "head_sha: 0000000000000000000000000000000000000\n"
                "independent: true\n"
                "summary: stale\n",
                encoding="utf-8",
            )
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("does not match", msg)

    def test_missing_fields_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\nhead_sha: {head}\n", encoding="utf-8"
            )
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("missing fields", msg)

    def test_independent_not_true_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {head}\n"
                f"independent: false\n"
                f"summary: not independent\n",
                encoding="utf-8",
            )
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("independent", msg)

    def test_evidence_committed_as_trailing_commit_referencing_parent_passes(self):
        # A commit that adds/updates the evidence file can never predict its
        # own resulting SHA (that's a hash self-reference), so the natural
        # workflow is: finish code at commit A, then commit the evidence
        # file on top referencing A. The check must resolve past that
        # trailing evidence-only commit and match against A.
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            code_head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {code_head}\n"
                f"independent: true\n"
                f"summary: reviewed at the code head, not this commit\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", "work/reviews/pr-99-review-evidence.md"], cwd=root, check=True
            )
            subprocess.run(
                ["git", "commit", "-q", "-m", "add review evidence"], cwd=root, check=True
            )
            ok, msg = crv.check("99", root)
            self.assertTrue(ok, msg)

    def test_multiple_evidence_only_commits_all_walked_back(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            code_head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            evidence_file = reviews / "pr-99-review-evidence.md"
            evidence_file.write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {code_head}\n"
                f"independent: true\n"
                f"summary: draft\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "evidence draft"], cwd=root, check=True)

            evidence_file.write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {code_head}\n"
                f"independent: true\n"
                f"summary: revised summary, still evidence-only\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "evidence revision"], cwd=root, check=True)

            ok, msg = crv.check("99", root)
            self.assertTrue(ok, msg)

    def test_evidence_commit_that_also_touches_other_files_is_not_walked_past(self):
        # If the trailing commit changes anything outside work/reviews/, it
        # must not be treated as evidence-only -- otherwise unreviewed code
        # changes could be smuggled in under an old head_sha.
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            code_head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {code_head}\n"
                f"independent: true\n"
                f"summary: sneaky\n",
                encoding="utf-8",
            )
            (root / "f.txt").write_text("y", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "evidence + unrelated code change"],
                cwd=root,
                check=True,
            )
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("does not match", msg)

    def test_merge_commit_is_not_walked_past(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            code_head = _init_repo(root)
            base_branch = subprocess.run(
                ["git", "branch", "--show-current"], cwd=root, check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(
                ["git", "checkout", "-q", "-b", "feature"], cwd=root, check=True
            )
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: SENTINEL-A\n"
                f"head_sha: {code_head}\n"
                f"independent: true\n"
                f"summary: evidence on a branch\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "evidence"], cwd=root, check=True)
            subprocess.run(["git", "checkout", "-q", base_branch], cwd=root, check=True)
            (root / "g.txt").write_text("z", encoding="utf-8")
            subprocess.run(["git", "add", "g.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "other work"], cwd=root, check=True)
            subprocess.run(
                ["git", "merge", "-q", "--no-ff", "-m", "merge", "feature"],
                cwd=root,
                check=True,
            )
            # HEAD is now a merge commit; head_sha claiming code_head must
            # fail because a merge commit is never walked past.
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)
            self.assertIn("does not match", msg)

    def test_empty_reviewer_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            head = _init_repo(root)
            reviews = root / "work" / "reviews"
            reviews.mkdir(parents=True)
            (reviews / "pr-99-review-evidence.md").write_text(
                f"reviewer: \n"
                f"head_sha: {head}\n"
                f"independent: true\n"
                f"summary: x\n",
                encoding="utf-8",
            )
            ok, msg = crv.check("99", root)
            self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
