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


class DigitalFungusRouteCostTests(unittest.TestCase):
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
        report = analyze(ROOT)
        routes = report["navigation_routes"]

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

        self.assertEqual(report["summary"]["navigation_targets_reachable"], len(ROUTE_TARGETS))
        self.assertEqual(report["summary"]["max_navigation_route_hops"], 1)


if __name__ == "__main__":
    unittest.main()
