import unittest

from runtime.evaluation import IncidentCategory


class FrozenRegressionCaseTaxonomyTests(unittest.TestCase):
    def test_initial_learning_roadmap_taxonomy_is_complete(self):
        expected = {
            "TOOL_FAILURE",
            "CONTEXT_OMISSION",
            "CONTEXT_POISONING",
            "RUNAWAY_LOOP",
            "ROUTING_ERROR",
            "SKILL_ROUTING_ERROR",
            "SKILL_PROCEDURE_ERROR",
            "HELPER_FAILURE",
            "HELPER_NO_PROGRESS",
            "RECOVERY_FAILURE",
            "DUPLICATE_EXECUTION",
            "ENVIRONMENT_DRIFT",
            "REVIEW_MISS",
            "STALE_REVIEW_EVIDENCE",
            "VALIDATOR_FALSE_POSITIVE",
            "VALIDATOR_FALSE_NEGATIVE",
            "AUTHORITY_VIOLATION_ATTEMPT",
            "SECURITY_BOUNDARY_FAILURE",
            "OPERATOR_FRICTION_INTERVENTION",
            "ACI_AMBIGUITY",
            "SUPPLY_CHAIN_DEFECT",
            "UNKNOWN",
        }

        self.assertEqual({item.value for item in IncidentCategory}, expected)


if __name__ == "__main__":
    unittest.main()
