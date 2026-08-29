from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"
FIRST_RUN = ROOT / "docs" / "FIRST_RUN.md"
README = ROOT / "README.md"
WORK = ROOT / "work"
WORK_INDEX = WORK / "README.md"
ROADMAP_INDEX = WORK / "roadmaps" / "README.md"
INFORMATION_LIFECYCLE = PLAYBOOK / "INFORMATION_LIFECYCLE.md"
TASK_TEMPLATE = ROOT / "templates" / "task.md"
DECISION_TEMPLATE = ROOT / "templates" / "decision.md"

# Conscious-friction guards. These are not claims that the exact numbers are
# inherently optimal; changing them requires an explicit reviewed tradeoff.
PLAYBOOK_SURFACE_BUDGET = 23
AGENTS_BYTE_BUDGET = 10_000
ROOT_README_BYTE_BUDGET = 4_000
FIRST_RUN_BYTE_BUDGET = 3_000


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
        self.assertIn("shortest useful route", agents)

    def test_always_read_entry_surfaces_have_explicit_size_budgets(self):
        budgets = {
            AGENTS: AGENTS_BYTE_BUDGET,
            README: ROOT_README_BYTE_BUDGET,
            FIRST_RUN: FIRST_RUN_BYTE_BUDGET,
        }
        for path, budget in budgets.items():
            size = len(path.read_bytes())
            self.assertLessEqual(
                size,
                budget,
                f"{path.relative_to(ROOT)} grew to {size} bytes (budget {budget}). "
                "Prefer links/routing to copied explanation; raise the budget only "
                "for an explicit reviewed reason.",
            )

    def test_work_index_routes_every_top_level_record_directory(self):
        index = WORK_INDEX.read_text(encoding="utf-8")
        missing = [
            path.name
            for path in sorted(WORK.iterdir())
            if path.is_dir() and f"({path.name}/)" not in index
        ]
        self.assertEqual(
            missing,
            [],
            "Top-level work record classes must be discoverable from work/README.md "
            f"without directory search. Missing: {missing}",
        )

    def test_first_run_routes_to_stable_navigation_hubs(self):
        first_run = FIRST_RUN.read_text(encoding="utf-8")
        for destination in (
            "../playbook/INDEX.md",
            "../work/README.md",
            "../work/roadmaps/README.md",
            "../work/coordination/README.md",
            "../state/CURRENT.md",
        ):
            self.assertIn(destination, first_run)

    def test_large_roadmaps_have_a_question_router_before_their_content(self):
        roadmap_index = normalized_text(ROADMAP_INDEX).lower()
        self.assertIn("route by question", roadmap_index)
        self.assertIn("do not open every roadmap", roadmap_index)
        self.assertIn("live github", roadmap_index)
        self.assertIn("capability checklist", roadmap_index)
        self.assertIn("master capability roadmap", roadmap_index)

    def test_information_lifecycle_owns_no_island_relationship_rule(self):
        lifecycle = normalized_text(INFORMATION_LIFECYCLE).lower()
        self.assertIn("nothing durable should be an island", lifecycle)
        self.assertIn("link, do not duplicate", lifecycle)
        self.assertIn("shortest reliable retrieval", lifecycle)
        self.assertIn("standard relative markdown links", lifecycle)

        self.assertIn("Related records:", TASK_TEMPLATE.read_text(encoding="utf-8"))
        decision = DECISION_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("Related task/roadmap:", decision)
        self.assertIn("Source/evidence:", decision)
        self.assertIn("Supersedes / superseded by:", decision)


if __name__ == "__main__":
    unittest.main()
