from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "playbook" / "INDEX.md"


class ProtocolDiscoverabilityTests(unittest.TestCase):
    def test_trigger_router_keeps_deep_protocols_discoverable(self):
        index = INDEX.read_text(encoding="utf-8")

        self.assertIn("## Route by situation", index)

        required_routes = {
            "EXECUTION_INTEGRITY.md": "Exact run context/scope",
            "REPAIR_AND_LEARNING.md": "failure, drift, wrong assumption",
            "EMERGENCE.md": "cross-root connection",
            "SPIDERWEB_AUDIT.md": "Durable information looks isolated",
            "TENTH_SEAT_REVIEW.md": "consensus looks unusually clean",
            "INFORMATION_CLASSES.md": "Skills, flows, tools",
            "INFORMATION_LIFECYCLE.md": "hard to retrieve, duplicated, stale",
            "CONTROL_PLANE.md": "SQLite/LangGraph/RnS/hcom",
        }

        for method, trigger_text in required_routes.items():
            self.assertIn(method, index)
            self.assertIn(trigger_text, index)

    def test_router_preserves_authority_boundaries(self):
        index = INDEX.read_text(encoding="utf-8")

        for boundary in (
            "Diagnostics such as Spiderweb do not repair",
            "E/I capture does not authorize",
            "Skills/tools do not grant permission",
            "review does not replace the orchestration operator's ownership",
        ):
            self.assertIn(boundary, index)


if __name__ == "__main__":
    unittest.main()
