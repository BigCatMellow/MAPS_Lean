import unittest

from runtime.incident_taxonomy import IncidentClass, classify_failure_text

ROADMAP_MEMBERS = [
    "TOOL_FAILURE",
    "CONTEXT_OMISSION",
    "CONTEXT_POISONING",
    "ROUTING_ERROR",
    "SKILL_ROUTING_ERROR",
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
    "ACI_AMBIGUITY",
    "SUPPLY_CHAIN_DEFECT",
    "OPERATOR_FRICTION_INTERVENTION",
    "UNKNOWN",
]


class TestIncidentClassVocabulary(unittest.TestCase):
    def test_exact_membership_matches_roadmap(self):
        self.assertEqual(
            {member.name for member in IncidentClass},
            set(ROADMAP_MEMBERS),
        )

    def test_member_count_is_nineteen(self):
        self.assertEqual(len(list(IncidentClass)), 19)

    def test_each_member_value_equals_its_name(self):
        for member in IncidentClass:
            self.assertEqual(member.value, member.name)

    def test_is_str_enum(self):
        self.assertTrue(issubclass(IncidentClass, str))
        self.assertEqual(IncidentClass.TOOL_FAILURE, "TOOL_FAILURE")

    def test_unknown_is_first_class_member(self):
        self.assertIn(IncidentClass.UNKNOWN, list(IncidentClass))
        self.assertEqual(IncidentClass.UNKNOWN.value, "UNKNOWN")


class TestClassifyFailureText(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(
            classify_failure_text("TOOL_FAILURE"), IncidentClass.TOOL_FAILURE
        )

    def test_case_insensitive_match(self):
        self.assertEqual(
            classify_failure_text("context_poisoning"),
            IncidentClass.CONTEXT_POISONING,
        )

    def test_whitespace_tolerant_match(self):
        self.assertEqual(
            classify_failure_text("  routing_error  "), IncidentClass.ROUTING_ERROR
        )

    def test_unrecognized_text_returns_unknown(self):
        self.assertEqual(classify_failure_text("SOMETHING_MADE_UP"), IncidentClass.UNKNOWN)

    def test_empty_string_returns_unknown(self):
        self.assertEqual(classify_failure_text(""), IncidentClass.UNKNOWN)

    def test_non_string_input_returns_unknown_not_raise(self):
        self.assertEqual(classify_failure_text(None), IncidentClass.UNKNOWN)  # type: ignore[arg-type]
        self.assertEqual(classify_failure_text(123), IncidentClass.UNKNOWN)  # type: ignore[arg-type]

    def test_never_raises(self):
        for bogus in ["", "unknown-ish", "tool failure", None, 42, object()]:
            try:
                classify_failure_text(bogus)  # type: ignore[arg-type]
            except Exception as exc:  # pragma: no cover - failure path
                self.fail(f"classify_failure_text raised for {bogus!r}: {exc}")


if __name__ == "__main__":
    unittest.main()
