from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"
FIRST_RUN = ROOT / "docs" / "FIRST_RUN.md"
README = ROOT / "README.md"
WIKI_SOURCE = ROOT / "docs" / "wiki"
WIKI_SYNC = ROOT / ".github" / "workflows" / "sync-wiki.yml"

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

    def test_wiki_home_is_agent_onboarding_not_parallel_authority(self):
        home = normalized_text(WIKI_SOURCE / "Home.md")
        lower = home.lower()

        self.assertIn("orientation surface for a fresh agent", lower)
        self.assertIn("not an authority store", lower)
        self.assertIn("docs/FIRST_RUN.md", home)
        self.assertIn("AGENTS.md", home)
        self.assertIn("orchestration operator", lower)
        self.assertIn("agent slots", lower)
        self.assertIn("delegation transfers execution, never ownership", lower)
        self.assertIn("a finished child task is a reconciliation point", lower)
        self.assertIn("target authority + approved roadmap/task + one relevant MAPS_L method", home)

    def test_wiki_walkthrough_teaches_parent_continuation_and_true_escalation(self):
        walkthrough = normalized_text(WIKI_SOURCE / "First-Task-Walkthrough.md")
        lower = walkthrough.lower()

        self.assertIn("define the parent done condition", lower)
        self.assertIn("orchestration operator keeps parent ownership", lower)
        self.assertIn("genuinely complete or a true authority boundary", lower)
        self.assertIn("not a request for permission to continue inside approved scope", lower)
        self.assertIn("not the default response to ordinary uncertainty", lower)

    def test_wiki_capability_page_requires_live_verification(self):
        capability = normalized_text(WIKI_SOURCE / "Capability-Status.md")
        lower = capability.lower()

        self.assertIn("pin a dated subsystem inventory", lower)
        self.assertIn("production call path / real behavior", lower)
        self.assertIn("CAPABILITY_CHECKLIST.md", capability)
        self.assertIn("real caller/path, not only a unit test", lower)
        self.assertIn("current roadmap/checklist", lower)

    def test_wiki_source_has_no_known_stale_contract_language(self):
        wiki_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(WIKI_SOURCE.glob("*.md"))
        )
        stale_phrases = [
            "Negative operating contract",
            "f02ed62",
            "pass #7",
            "75 test modules",
            "No destructive/irreversible action without explicit operator approval",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, wiki_text)

    def test_wiki_sync_projects_reviewed_source_from_main(self):
        sync = WIKI_SYNC.read_text(encoding="utf-8")
        self.assertIn("- main", sync)
        self.assertIn("docs/wiki/**", sync)
        self.assertIn("cp docs/wiki/*.md wiki-out/", sync)
        self.assertIn("Sync agent onboarding wiki from main", sync)


if __name__ == "__main__":
    unittest.main()
