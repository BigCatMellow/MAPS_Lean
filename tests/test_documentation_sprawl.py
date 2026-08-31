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
TASK_LIFECYCLE = PLAYBOOK / "TASK_LIFECYCLE.md"
TASK_TEMPLATE = ROOT / "templates" / "task.md"
DECISION_TEMPLATE = ROOT / "templates" / "decision.md"
WIKI_SOURCE = ROOT / "docs" / "wiki"
WIKI_SYNC = ROOT / ".github" / "workflows" / "sync-wiki.yml"
PILOT_SKILL = ROOT / ".claude" / "skills" / "pilot" / "SKILL.md"

# Conscious-friction guards. These are not claims that the exact numbers are
# inherently optimal; changing them requires an explicit reviewed tradeoff.
# Raised 23 -> 24 for playbook/SPIDERWEB_AUDIT.md: a genuinely distinct
# reusable method (bounded advisory durable-record relationship audit) that
# does not belong to an existing concept owner.
PLAYBOOK_SURFACE_BUDGET = 24
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
        self.assertIn("information-routing maintenance pass", agents)
        self.assertIn("playbook/INFORMATION_LIFECYCLE.md#information-routing-maintenance-pass", agents)

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
            if path.is_dir() and f"({path.name}/" not in index
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

    def test_information_lifecycle_owns_repeatable_route_maintenance(self):
        lifecycle = normalized_text(INFORMATION_LIFECYCLE).lower()
        self.assertIn("information-routing maintenance pass", lifecycle)
        self.assertIn("when navigation cost has plausibly degraded", lifecycle)
        self.assertIn("python3 tools/digital_fungus.py --root .", lifecycle)
        self.assertIn("consolidate before adding", lifecycle)
        self.assertIn("connect or retire islands", lifecycle)
        self.assertIn("compact without semantic loss", lifecycle)
        self.assertIn("remeasure", lifecycle)
        self.assertIn("keep the maintenance change only when it produces a real routing benefit", lifecycle)
        self.assertIn("do not create a second graph registry", lifecycle)

    def test_playbook_index_routes_maintenance_without_retired_context_doc(self):
        index = INDEX.read_text(encoding="utf-8")
        self.assertIn("Keep project information trustworthy and cheap to retrieve over time", index)
        self.assertIn("[INFORMATION_LIFECYCLE.md](INFORMATION_LIFECYCLE.md)", index)
        self.assertIn("[Current state](../state/CURRENT.md)", index)
        self.assertNotIn("../docs/CONTEXT.md", index)

    def test_repeatable_work_requires_operational_independence(self):
        """Anchor on structural markers and rule IDs, not exact prose.

        Guards the actual completion-semantic invariant: a triggered gate is
        part of DONE/parent success, whole-gate ``N/A`` cannot cover a
        repeatable process merely because automation is infeasible, and the
        task template still demands a reproduction package / manual fallback.
        """

        agents_raw = AGENTS.read_text(encoding="utf-8")
        lifecycle_raw = TASK_LIFECYCLE.read_text(encoding="utf-8")
        task = TASK_TEMPLATE.read_text(encoding="utf-8")

        # AGENTS.md routes to the owning gate from a hard invariant.
        self.assertIn("## Hard operating invariants", agents_raw)
        self.assertIn(
            "playbook/TASK_LIFECYCLE.md#operational-independence-gate", agents_raw
        )

        # TASK_LIFECYCLE.md owns the gate with stable headings + rule IDs.
        self.assertIn("## Operational independence gate", lifecycle_raw)
        self.assertIn("### Gate rules", lifecycle_raw)
        for rule_id in ("OIG-DONE", "OIG-NA-WHOLE", "OIG-NA-AUTO"):
            self.assertIn(rule_id, lifecycle_raw)
        # Gate stays REQUIRED as a marked term, and DONE cites OIG-DONE.
        self.assertIn("**REQUIRED**", lifecycle_raw)
        self.assertIn(
            "operational-independence requirement (`OIG-DONE`)",
            " ".join(lifecycle_raw.split()),
        )

        # Task template keeps the structured fields and the tightened N/A rules.
        self.assertIn("- Operational independence:", task)
        self.assertIn("- Reproduction package:", task)
        self.assertIn("TASK_LIFECYCLE.md#operational-independence-gate", task)
        self.assertIn("OIG-NA-WHOLE", task)
        self.assertIn("OIG-NA-AUTO", task)

    def test_na_escape_hatch_cannot_silently_become_permissive(self):
        """OIG-NA-AUTO must keep a mandatory manual fallback when automation is N/A."""

        lifecycle = normalized_text(TASK_LIFECYCLE)
        # The narrow automation-only N/A clause must still force a manual package.
        auto_rule = next(
            block for block in lifecycle.split("`OIG-")
            if block.startswith("NA-AUTO`")
        )
        self.assertIn("MUST still carry", auto_rule)
        self.assertIn("manual reproduction instructions", auto_rule)
        # Whole-gate N/A must explicitly exclude "automation infeasible".
        whole_rule = next(
            block for block in lifecycle.split("`OIG-")
            if block.startswith("NA-WHOLE`")
        )
        self.assertIn("not", whole_rule.lower())
        self.assertIn("whole-gate", whole_rule.lower())

    def test_agents_keeps_single_owner_independent_review_invariant(self):
        """Global task-owner invariant (CLAUDE.md rule 17) survives compaction."""

        agents = normalized_text(AGENTS).lower()
        self.assertIn("one accountable", agents)
        self.assertIn("no owner approves their own substantive work", agents)

    def test_pilot_skill_is_open_format_and_named_for_direct_invocation(self):
        skill = PILOT_SKILL.read_text(encoding="utf-8")
        lower = skill.lower()

        self.assertTrue(skill.startswith("---\nname: pilot\n"))
        self.assertIn("description:", skill)
        self.assertIn("explicitly invokes Pilot/MAPS_L", skill)
        self.assertIn("/pilot the Pokemon project", skill)
        self.assertIn("$ARGUMENTS", skill)
        self.assertIn("~/.claude/skills/pilot/", skill)
        self.assertFalse((ROOT / "skills" / "pilot" / "SKILL.md").exists())

    def test_pilot_skill_remains_a_thin_adapter_not_parallel_contract(self):
        skill = normalized_text(PILOT_SKILL)
        lower = skill.lower()

        self.assertIn("thin invocation adapter", lower)
        self.assertIn("does not define a second maps_l operating contract", lower)
        self.assertIn("own instructions and approved scope govern its authority", lower)
        self.assertIn("playbook/index.md", lower)
        self.assertIn("method-only", lower)
        self.assertIn("orchestrated", lower)
        self.assertIn("runtime-backed", lower)
        self.assertIn("advance automatically while authorized parent work remains", lower)
        self.assertIn("human only for a true boundary crossing", lower)

        # The skill routes to canonical owners instead of copying AGENTS.md wholesale.
        self.assertNotIn("## Hard operating invariants", PILOT_SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("## Scope-level authorization", PILOT_SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("## MAPS_L orchestration operator invariant", PILOT_SKILL.read_text(encoding="utf-8"))

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
        self.assertIn("default response to ordinary uncertainty", lower)
        self.assertIn("decide inside authority first", lower)

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
