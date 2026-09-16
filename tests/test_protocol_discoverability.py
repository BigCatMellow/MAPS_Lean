from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"


def normalized(text: str) -> str:
    return " ".join(text.split())


class ProtocolDiscoverabilityTests(unittest.TestCase):
    def test_trigger_router_covers_entire_active_playbook_surface(self):
        index = INDEX.read_text(encoding="utf-8")
        self.assertIn("## Route by situation", index)

        router = index.split("## Route by situation", 1)[1].split(
            "### Related non-playbook routes", 1
        )[0]
        missing = [
            path.name
            for path in sorted(PLAYBOOK.glob("*.md"))
            if path.name != "INDEX.md" and path.name not in router
        ]
        self.assertEqual(
            missing,
            [],
            "Every active playbook method must be discoverable by trigger, not only "
            f"listed elsewhere in the index. Missing: {missing}",
        )

    def test_router_preserves_authority_boundaries(self):
        index = normalized(INDEX.read_text(encoding="utf-8"))

        for boundary in (
            "Diagnostics such as Spiderweb do not repair",
            "E/I capture does not authorize",
            "Skills/tools do not grant permission",
            "review does not replace the orchestration operator's ownership",
        ):
            self.assertIn(boundary, index)

    def test_router_preserves_distinctions_that_change_method_choice(self):
        """Compaction may remove repetition, not method-selection semantics."""

        index = normalized(INDEX.read_text(encoding="utf-8"))
        for distinction in (
            "Per-task steering; not roadmap redesign.",
            "Roadmap/work-arc correction; not routine task selection.",
            "Mandatory triage: capture → severity → recurrence → mechanical safeguard → live verify",
            "may challenge or supersede mechanisms",
            "drift repair stays with Repair & Learning",
            "topic similarity, link count/density, or the derived graph are not authority",
            "Information type; not lifecycle status and does not create authority.",
            "Active/retired/archive lifecycle plus routing maintenance; not information-type classification.",
            "plausible output is not production proof",
            "Representation only; not canonical task truth.",
            "does not create implementation authority",
            "does not create a second approval system",
        ):
            self.assertIn(distinction, index)

    def test_root_contract_makes_brevity_learning_and_evolution_explicit(self):
        agents = normalized(AGENTS.read_text(encoding="utf-8"))

        for invariant in (
            "Brevity over grammar. Tokens are a resource.",
            "Default to the shortest complete answer or record.",
            "Do not delete decision-relevant meaning merely to hit a size/token target",
            "Mistakes must teach the system.",
            "Repair and Learning",
            "Methods are replaceable, not sacred.",
            "Past success is evidence, not permanent authority.",
            "Default to the shortest complete response.",
        ):
            self.assertIn(invariant, agents)


if __name__ == "__main__":
    unittest.main()
