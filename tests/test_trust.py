import unittest

from runtime.skills.lifecycle import SkillLifecycleState
from runtime.trust import (
    MemoryTrustClass,
    TrustClassError,
    operational_learning_trust_class,
    skill_lifecycle_trust_class,
)

ROADMAP_CLASSES = [
    "UNTRUSTED_INPUT",
    "OBSERVATION",
    "CLAIM",
    "CANDIDATE_LESSON",
    "REVIEWED_GUIDANCE",
    "APPROVED_SKILL",
    "ACTIVE_INSTRUCTION",
    "CANONICAL_POLICY",
    "SUPERSEDED",
    "RETIRED",
    "QUARANTINED",
]

# The 3 real status strings validated by runtime.operational_learning._STATUSES.
OPERATIONAL_LEARNING_STATUSES = ["CANDIDATE", "ACTIVE", "RETIRED"]


class MemoryTrustClassVocabularyTests(unittest.TestCase):
    def test_exactly_the_11_roadmap_classes_exist(self) -> None:
        actual = {member.name for member in MemoryTrustClass}
        self.assertEqual(actual, set(ROADMAP_CLASSES))
        self.assertEqual(len(MemoryTrustClass), 11)

    def test_member_values_match_names(self) -> None:
        for member in MemoryTrustClass:
            self.assertEqual(member.value, member.name)


class SkillLifecycleStateMappingTests(unittest.TestCase):
    def test_every_lifecycle_state_maps_to_a_memory_trust_class(self) -> None:
        for state in SkillLifecycleState:
            result = skill_lifecycle_trust_class(state)
            self.assertIsInstance(result, MemoryTrustClass)

    def test_exact_mapping_values(self) -> None:
        expected = {
            SkillLifecycleState.DISCOVERED: MemoryTrustClass.OBSERVATION,
            SkillLifecycleState.VALIDATED: MemoryTrustClass.REVIEWED_GUIDANCE,
            SkillLifecycleState.QUARANTINED: MemoryTrustClass.QUARANTINED,
            SkillLifecycleState.APPROVED: MemoryTrustClass.APPROVED_SKILL,
            SkillLifecycleState.ACTIVE: MemoryTrustClass.ACTIVE_INSTRUCTION,
            SkillLifecycleState.SUPERSEDED: MemoryTrustClass.SUPERSEDED,
            SkillLifecycleState.RETIRED: MemoryTrustClass.RETIRED,
        }
        self.assertEqual(set(expected), set(SkillLifecycleState))
        for state, expected_class in expected.items():
            self.assertEqual(skill_lifecycle_trust_class(state), expected_class)

    def test_rejects_non_lifecycle_state(self) -> None:
        with self.assertRaises(TrustClassError):
            skill_lifecycle_trust_class("ACTIVE")  # type: ignore[arg-type]


class OperationalLearningMappingTests(unittest.TestCase):
    def test_every_real_status_maps_to_a_memory_trust_class(self) -> None:
        for status in OPERATIONAL_LEARNING_STATUSES:
            result = operational_learning_trust_class(status)
            self.assertIsInstance(result, MemoryTrustClass)

    def test_exact_mapping_values(self) -> None:
        self.assertEqual(
            operational_learning_trust_class("CANDIDATE"),
            MemoryTrustClass.CANDIDATE_LESSON,
        )
        self.assertEqual(
            operational_learning_trust_class("ACTIVE"),
            MemoryTrustClass.REVIEWED_GUIDANCE,
        )
        self.assertEqual(
            operational_learning_trust_class("RETIRED"), MemoryTrustClass.RETIRED
        )

    def test_raises_for_unrecognized_status(self) -> None:
        with self.assertRaises(TrustClassError):
            operational_learning_trust_class("BOGUS")

    def test_raises_for_non_string(self) -> None:
        with self.assertRaises(TrustClassError):
            operational_learning_trust_class(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
