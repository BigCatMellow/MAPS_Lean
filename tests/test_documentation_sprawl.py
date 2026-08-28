from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"
FIRST_RUN = ROOT / "docs" / "FIRST_RUN.md"
README = ROOT / "README.md"


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class DocumentationSprawlGuardTests(unittest.TestCase):
    def test_every_playbook_markdown_file_is_indexed(self):
        """A new active playbook method must become visible in the one index."""

        index = INDEX.read_text(encoding="utf-8")
        missing = []
        for path in sorted(PLAYBOOK.glob("*.md")):
            if path.name == "INDEX.md":
                continue
            if path.name not in index:
                missing.append(path.name)
        self.assertEqual(
            missing,
            [],
            "Unindexed playbook files create silent process sprawl. "
            f"Index, merge, narrow, or retire: {missing}",
        )

    def test_entrypoints_name_one_repository_wide_contract(self):
        agents = normalized_text(AGENTS)
        readme = normalized_text(README)
        first_run = normalized_text(FIRST_RUN)
        index = normalized_text(INDEX).lower()

        self.assertIn("single repository-wide operating contract", agents)
        self.assertIn("single repository-wide operating contract", readme)
        self.assertIn("single repository-wide operating contract", first_run)
        self.assertIn("navigation, not a second operating contract", index)

    def test_agents_owns_anti_sprawl_rule(self):
        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("## Authority, precedence, and anti-sprawl", agents)
        self.assertIn("### Documentation sprawl invariant", agents)
        self.assertIn("One concept, one owner document", agents)


if __name__ == "__main__":
    unittest.main()
