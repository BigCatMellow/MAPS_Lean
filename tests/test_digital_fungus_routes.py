from pathlib import Path
import unittest

from tools.digital_fungus import (
    FIRST_RUN,
    ROUTE_TARGETS,
    analyze,
    estimated_tokens,
    least_read_cost_route,
)


ROOT = Path(__file__).resolve().parents[1]
MAX_COMMON_ROUTE_TOKEN_PROXY = 2_200


class DigitalFungusRouteCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyze(ROOT)

    def test_token_proxy_is_stable_and_explicitly_rough(self):
        self.assertEqual(estimated_tokens("a"), 1)
        self.assertEqual(estimated_tokens("a" * 4), 1)
        self.assertEqual(estimated_tokens("a" * 5), 2)

    def test_route_optimizer_prefers_lower_read_cost_over_fewer_hops(self):
        adjacency = {
            "start": {"large", "small"},
            "large": {"target"},
            "small": {"middle"},
            "middle": {"target"},
            "target": set(),
        }
        token_costs = {
            "start": 999,
            "large": 100,
            "small": 1,
            "middle": 1,
            "target": 1,
        }

        route = least_read_cost_route("start", "target", adjacency, token_costs)

        self.assertIsNotNone(route)
        self.assertEqual(route["path"], ["start", "small", "middle", "target"])
        self.assertEqual(route["hops"], 3)
        self.assertEqual(route["added_estimated_tokens"], 3)

    def test_first_run_has_direct_routes_to_navigation_hubs(self):
        routes = self.report["navigation_routes"]

        self.assertEqual(routes["start"], FIRST_RUN)
        self.assertEqual(set(routes["targets"]), set(ROUTE_TARGETS))
        for target, route in routes["targets"].items():
            self.assertIsNotNone(route, f"FIRST_RUN cannot reach navigation hub {target}")
            self.assertEqual(
                route["hops"],
                1,
                f"Routine navigation to {target} should be one direct hop, not a chain-read",
            )
            self.assertEqual(route["path"], [FIRST_RUN, target])
            self.assertLessEqual(
                route["added_estimated_tokens"],
                MAX_COMMON_ROUTE_TOKEN_PROXY,
                f"Direct hub {target} became too expensive to use as a routine router",
            )

        self.assertEqual(
            self.report["summary"]["navigation_targets_reachable"], len(ROUTE_TARGETS)
        )
        self.assertEqual(self.report["summary"]["max_navigation_route_hops"], 1)
        self.assertLessEqual(
            self.report["summary"]["max_navigation_route_added_estimated_tokens"],
            MAX_COMMON_ROUTE_TOKEN_PROXY,
        )

    def test_valid_work_directory_links_are_not_reported_broken(self):
        directory_routes = {
            (row["source"], row["target"]) for row in self.report["directory_routes"]
        }
        self.assertIn(("work/README.md", "work/tasks/"), directory_routes)
        self.assertIn(("work/README.md", "work/research/"), directory_routes)

        false_broken = [
            row
            for row in self.report["broken_links"]
            if row["source"] == "work/README.md" and row["target"].endswith("/")
        ]
        self.assertEqual(false_broken, [])


if __name__ == "__main__":
    unittest.main()
