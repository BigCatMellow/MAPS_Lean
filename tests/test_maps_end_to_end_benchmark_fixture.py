from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


PROTOCOL = (
    Path(__file__).resolve().parents[1]
    / "work"
    / "evals"
    / "maps-end-to-end-benchmark-v1.json"
)


class MapsEndToEndBenchmarkFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.scenarios = {scenario["id"]: scenario for scenario in cls.data["scenarios"]}

    def test_protocol_identity_and_result_states(self):
        self.assertEqual(self.data["version"], "maps-end-to-end-benchmark-v1")
        self.assertEqual(
            self.data["status"],
            "FROZEN_PROTOCOL_NOT_RUNTIME_AUTHORITY",
        )
        self.assertEqual(
            set(self.data["result_states"]),
            {"PASS", "FAIL", "UNKNOWN", "NOT_RUN"},
        )

    def test_scenario_ids_are_unique_and_layered(self):
        scenarios = self.data["scenarios"]
        self.assertEqual(len(scenarios), len(self.scenarios))
        for scenario in scenarios:
            self.assertRegex(scenario["id"], r"^E2E-L[23]-[0-9]{3}$")
            self.assertIn(
                scenario["layer"],
                {"LAYER_2_CONTROLLED", "LAYER_3_PRODUCTION_OUTCOME"},
            )
            self.assertTrue(scenario["required"], scenario["id"])

    def test_layer_two_and_layer_three_evidence_classes_do_not_blur(self):
        classes = self.data["evidence_classes"]
        self.assertTrue(classes["LAYER_2_CONTROLLED"]["synthetic_fixture_allowed"])
        self.assertFalse(classes["LAYER_3_PRODUCTION_OUTCOME"]["synthetic_fixture_allowed"])
        for scenario in self.data["scenarios"]:
            if scenario["layer"] == "LAYER_2_CONTROLLED":
                self.assertIsInstance(scenario["synthetic_fixture"], dict, scenario["id"])
            else:
                self.assertIsNone(scenario["synthetic_fixture"], scenario["id"])
                self.assertIn("eligibility", scenario, scenario["id"])
                self.assertTrue(scenario["eligibility"]["requires_real_task"], scenario["id"])
                self.assertTrue(scenario["eligibility"]["requires_real_run"], scenario["id"])

    def test_required_real_external_or_operator_visible_case_is_real_layer_three(self):
        completion = self.data["benchmark_completion"]
        self.assertTrue(completion["requires_real_external_or_operator_visible_case"])
        scenario_id = completion["real_external_or_operator_visible_scenario"]
        self.assertIn(scenario_id, self.scenarios)
        scenario = self.scenarios[scenario_id]
        self.assertEqual(scenario["layer"], "LAYER_3_PRODUCTION_OUTCOME")
        self.assertTrue(scenario["external_operator_visible"])
        self.assertIsNone(scenario["synthetic_fixture"])
        eligibility = scenario["eligibility"]
        self.assertTrue(eligibility["requires_operator_or_user_visible_result"])
        self.assertTrue(eligibility["requires_existing_task_authority_for_external_effect"])

    def test_completion_lists_exact_required_scenarios(self):
        completion = self.data["benchmark_completion"]
        layer_2 = {
            scenario["id"]
            for scenario in self.data["scenarios"]
            if scenario["layer"] == "LAYER_2_CONTROLLED" and scenario["required"]
        }
        layer_3 = {
            scenario["id"]
            for scenario in self.data["scenarios"]
            if scenario["layer"] == "LAYER_3_PRODUCTION_OUTCOME" and scenario["required"]
        }
        self.assertEqual(set(completion["required_layer_2_scenarios"]), layer_2)
        self.assertEqual(set(completion["required_layer_3_scenarios"]), layer_3)

    def test_properties_are_unique_structured_and_each_scenario_has_a_blocker(self):
        seen: set[str] = set()
        property_re = re.compile(r"^[a-z][a-z0-9_.:-]{1,127}$")
        for scenario in self.data["scenarios"]:
            properties = scenario["properties"]
            self.assertTrue(properties, scenario["id"])
            self.assertTrue(any(prop["kind"] == "BLOCKER" for prop in properties), scenario["id"])
            local_ids: set[str] = set()
            for prop in properties:
                prop_id = prop["id"]
                self.assertRegex(prop_id, property_re)
                self.assertNotIn(prop_id, local_ids, scenario["id"])
                local_ids.add(prop_id)
                self.assertNotIn(prop_id, seen, prop_id)
                seen.add(prop_id)
                self.assertIn(prop["kind"], {"BLOCKER", "QUALITY"})
                self.assertTrue(prop["required"], prop_id)
                self.assertTrue(prop["evidence"].strip(), prop_id)

    def test_incomplete_evidence_cannot_become_pass(self):
        rule = self.data["scenario_status_rule"]
        self.assertIn("UNKNOWN", rule["incomplete"])
        self.assertIn("NOT_RUN", rule["incomplete"])
        self.assertIn("cannot be counted as PASS", rule["incomplete"])
        self.assertIn("BLOCKER", rule["fail"])

    def test_layer_three_preserves_outcome_and_operator_provenance(self):
        outcome = self.scenarios["E2E-L3-002"]
        prop_ids = {prop["id"] for prop in outcome["properties"]}
        self.assertIn("outcome.completion_not_rewritten", prop_ids)
        self.assertIn("outcome.provenance_explicit", prop_ids)
        self.assertIn("operator.intervention_not_inferred_from_chat", prop_ids)
        self.assertIn("metrics.activity_not_success_proxy", prop_ids)

    def test_no_private_reasoning_or_automatic_promotion_contract(self):
        privacy = self.data["privacy_and_observability"]
        self.assertFalse(privacy["private_chain_of_thought_required"])
        self.assertFalse(privacy["raw_private_prompt_required"])
        self.assertFalse(self.data["promotion"]["automatic"])
        self.assertIn("proposal", self.data["promotion"]["path"])
        self.assertIn(
            "independent review/operator gate where required",
            self.data["promotion"]["path"],
        )


if __name__ == "__main__":
    unittest.main()
