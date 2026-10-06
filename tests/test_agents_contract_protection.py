from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CHECKS = ROOT / "docs" / "CHECKS_AND_BALANCES.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class AgentsContractProtectionTests(unittest.TestCase):
    def test_all_global_invariants_survive_compaction(self):
        text = AGENTS.read_text(encoding="utf-8")
        section = text.split("## Hard operating invariants", 1)[1].split(
            "## Scope-level authorization", 1
        )[0]

        expected = (
            "Smallest coherent change.",
            "Brevity over grammar. Tokens are a resource.",
            "Do not guess across a material boundary.",
            "Do not silently expand scope.",
            "Capability is not permission.",
            "One fact / one authority.",
            "No process for process's sake.",
            "Evidence outranks prose.",
            "Do not idle while authorized actionable work remains.",
            "Do not manufacture work after success.",
            "Leave repeatable work independently operable.",
            "One owner, independent review.",
            "Mistakes must teach the system.",
            "No hype; agreement must be earned.",
            "Close handoff loops.",
            "Methods are replaceable, not sacred.",
        )
        for marker in expected:
            self.assertIn(f"**{marker}**", section)

        numbers = re.findall(r"(?m)^(\d+)\. \*\*", section)
        self.assertEqual(numbers, [str(i) for i in range(1, len(expected) + 1)])

    def test_contract_cannot_casually_authorize_its_own_mutation(self):
        agents = normalized(AGENTS)
        for marker in (
            "Substantive changes to `AGENTS.md` are **high-risk authority changes**, not ordinary documentation.",
            "explicitly authorized contract/authority scope",
            "cannot bootstrap permission to rewrite this contract",
            "invariant loss",
            "authority drift",
            "exact substantive head",
            "genuinely independent review",
            "never reasons to weaken a necessary global invariant",
        ):
            self.assertIn(marker, agents)

    def test_no_hype_keeps_substantive_challenge_semantics(self):
        agents = normalized(AGENTS)
        for marker in (
            "tradeoffs",
            "unsupported assumptions",
            "counterarguments",
            "push back when that would improve the result",
            "agreement is appropriate when it survives scrutiny",
        ):
            self.assertIn(marker, agents)

    def test_learning_routes_real_friction_classes_to_owner(self):
        agents = normalized(AGENTS)
        for marker in (
            "failures",
            "friction",
            "wrong assumptions",
            "tool/environment gaps",
            "review-caught defect classes",
            "Repair and Learning",
            "mechanical safeguard",
        ):
            self.assertIn(marker, agents)

    def test_checks_classifies_operating_contract_changes_as_high_risk(self):
        checks = normalized(CHECKS)
        self.assertIn("Low | Ordinary documentation", checks)
        self.assertIn("High | Operating-contract/authority changes", checks)
        self.assertIn("Substantive `AGENTS.md` changes are always High risk", checks)
        self.assertIn("generic documentation or refactor scope does not qualify", checks)
        self.assertIn("no self-authorization", checks)


if __name__ == "__main__":
    unittest.main()
