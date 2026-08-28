from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"
FIRST_RUN = ROOT / "docs" / "FIRST_RUN.md"
README = ROOT / "README.md"

# This is a conscious-friction guard, not a claim that 23 is a magic number.
# A genuinely new distinct method may raise the budget, but doing so requires an
# explicit code-review-visible change instead of allowing quiet file growth.
PLAYBOOK_SURFACE_BUDGET = 23


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def active_playbook_files() -> list[Path]:
    return [
        path
        for path in sorted(PLAYBOOK.glob("*.md"))
        if path.name != "INDEX.md"
    ]


class DocumentationSprawlGuardTests(unittest.TestCase):
    def test_every_playbook_markdown_file_is_indexed(self):
        """A new active playbook surface must become visible in the one index."""

        index = INDEX.read_text(encoding="utf-8")
        missing = [
            path.name
            for path in active_playbook_files()
            if path.name not in index
        ]
        self.assertEqual(
            missing,
            [],
            "Unindexed playbook files create silent process sprawl. "
            f"Index, merge, narrow, move to the correct non-playbook area, or retire: {missing}",
        )

    def test_playbook_surface_does_not_grow_silently(self):
        files = active_playbook_files()
        self.assertLessEqual(
            len(files),
            PLAYBOOK_SURFACE_BUDGET,
            "Active playbook surface exceeded its explicit budget. Prefer merging "
            "with the existing concept owner or moving non-method material to its "
            "proper area. If a genuinely distinct reusable method is necessary, "
            "raise PLAYBOOK_SURFACE_BUDGET deliberately in the same reviewed change. "
            f"Current files ({len(files)}): {[path.name for path in files]}",
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

    def test_operating_contract_is_hard_invariants_not_soft_defaults(self):
        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("## Hard operating invariants", agents)
        self.assertNotIn("Negative operating contract", agents)
        self.assertNotIn("## Negative operating contract", agents)

    def test_agents_owns_anti_sprawl_rule(self):
        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("## Authority, precedence, and anti-sprawl", agents)
        self.assertIn("### Documentation sprawl invariant", agents)
        self.assertIn("One concept, one owner document", agents)


if __name__ == "__main__":
    unittest.main()
