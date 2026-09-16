from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbook"
INDEX = PLAYBOOK / "INDEX.md"
AGENTS = ROOT / "AGENTS.md"


class ProtocolDiscoverabilityTests(unittest.TestCase):
    def test_trigger_router_covers_entire_active_playbook_surface(self):
        index = INDEX.read_text(encoding="utf-8")
        self.assertIn("## Route by situation", index)

        router = index.split("## Route by situation", 1)[1].split(
            "## Core workflow methods", 1
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
        index = INDEX.read_text(encoding="utf-8")

        for boundary in (
            "Diagnostics such as Spiderweb do not repair",
            "E/I capture does not authorize",
            "Skills/tools do not grant permission",
            "review does not replace the orchestration operator's ownership",
        ):
            self.assertIn(boundary, index)

    def test_root_contract_makes_brevity_and_learning_explicit(self):
        agents = AGENTS.read_text(encoding="utf-8")

        for invariant in (
            "Brevity over grammar. Tokens are a resource.",
            "Default to the shortest complete answer or record.",
            "Mistakes must teach the system.",
            "Repair and Learning",
            "Default to the shortest complete response.",
        ):
            self.assertIn(invariant, agents)


if __name__ == "__main__":
    unittest.main()
