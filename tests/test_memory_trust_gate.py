"""Tests for the memory trust admission gate (roadmap 6.22).

Covers `work/notes/2026-08-25-memory-trust-enforcement-gate-design.md`:
the gate makes a real LOAD/WITHHOLD/DENY decision, the per-producer
WITHHOLD-vs-DENY split for the unknown case is preserved, it fails closed on
missing/unrecognized trust classes, and no policy engine or second authority
database was introduced to do it.
"""

from __future__ import annotations

import io
from pathlib import Path
import re
import tokenize
import unittest

from runtime.policy.memory_trust_gate import (
    MemoryAdmission,
    MemoryTrustGateError,
    admit_memory_evidence,
)
from runtime.trust import MemoryTrustClass

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _code_only(source: str) -> str:
    """Strip comments and string literals so the guards scan real code.

    The design note's non-goals are *about* thresholds, rules, and stores; the
    modules discuss them in prose. Scanning raw text would match the prose.
    """

    pieces: list[str] = []
    readline = io.StringIO(source).readline
    for token in tokenize.generate_tokens(readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        pieces.append(token.string)
    return "\n".join(pieces)


class AdmissionTableTests(unittest.TestCase):
    """The fixed table derived from PR #148's class/action table."""

    LOADABLE = {
        MemoryTrustClass.CANONICAL_POLICY,
        MemoryTrustClass.APPROVED_SKILL,
        MemoryTrustClass.REVIEWED_GUIDANCE,
    }
    WITHHELD = {
        MemoryTrustClass.CANDIDATE_LESSON,
        MemoryTrustClass.CLAIM,
        MemoryTrustClass.OBSERVATION,
        MemoryTrustClass.SUPERSEDED,
        MemoryTrustClass.RETIRED,
        # #148 admits ACTIVE_INSTRUCTION only if a loader proves the source
        # active; no such prover exists, so it must not load here.
        MemoryTrustClass.ACTIVE_INSTRUCTION,
    }
    DENIED = {
        MemoryTrustClass.UNTRUSTED_INPUT,
        MemoryTrustClass.QUARANTINED,
    }

    def _admit(self, trust_class, *, stale=False, unknown=MemoryAdmission.WITHHOLD):
        return admit_memory_evidence(trust_class, stale=stale, unknown_admission=unknown)

    def test_every_class_has_an_explicit_admission(self):
        covered = self.LOADABLE | self.WITHHELD | self.DENIED
        self.assertEqual(covered, set(MemoryTrustClass))

    def test_admission_matches_the_table(self):
        for trust_class in self.LOADABLE:
            with self.subTest(trust_class=trust_class):
                self.assertIs(self._admit(trust_class).admission, MemoryAdmission.LOAD)
        for trust_class in self.WITHHELD:
            with self.subTest(trust_class=trust_class):
                self.assertIs(self._admit(trust_class).admission, MemoryAdmission.WITHHOLD)
        for trust_class in self.DENIED:
            with self.subTest(trust_class=trust_class):
                self.assertIs(self._admit(trust_class).admission, MemoryAdmission.DENY)

    def test_table_is_not_enum_declaration_order(self):
        """SUPERSEDED/RETIRED/QUARANTINED are declared after CANONICAL_POLICY.

        A `class >= threshold` implementation over `Enum` order would admit
        all three; the explicit table must not.
        """

        members = list(MemoryTrustClass)
        canonical_index = members.index(MemoryTrustClass.CANONICAL_POLICY)
        for later in (
            MemoryTrustClass.SUPERSEDED,
            MemoryTrustClass.RETIRED,
            MemoryTrustClass.QUARANTINED,
        ):
            self.assertGreater(members.index(later), canonical_index)
            self.assertIsNot(self._admit(later).admission, MemoryAdmission.LOAD)

    def test_raw_string_values_are_accepted(self):
        self.assertIs(
            self._admit(MemoryTrustClass.REVIEWED_GUIDANCE.value).admission,
            MemoryAdmission.LOAD,
        )
        self.assertIs(
            self._admit("  OBSERVATION  ").admission, MemoryAdmission.WITHHOLD
        )

    def test_stale_demotes_load_and_never_promotes(self):
        decision = self._admit(MemoryTrustClass.REVIEWED_GUIDANCE, stale=True)
        self.assertIs(decision.admission, MemoryAdmission.WITHHOLD)
        self.assertEqual(decision.code, "TRUST_METADATA_STALE")
        # stale never lifts a WITHHOLD or a DENY.
        self.assertIs(
            self._admit(MemoryTrustClass.OBSERVATION, stale=True).admission,
            MemoryAdmission.WITHHOLD,
        )
        self.assertIs(
            self._admit(MemoryTrustClass.QUARANTINED, stale=True).admission,
            MemoryAdmission.DENY,
        )

    def test_non_bool_stale_is_treated_as_stale(self):
        for value in (None, "no", 0.0, object()):
            with self.subTest(value=value):
                self.assertIs(
                    self._admit(MemoryTrustClass.REVIEWED_GUIDANCE, stale=value).admission,
                    MemoryAdmission.WITHHOLD,
                )


class FailClosedTests(unittest.TestCase):
    UNUSABLE = (None, "", "   ", "NOT_A_CLASS", "reviewed_guidance", 7, object(), [])

    def test_unknown_class_never_loads(self):
        for value in self.UNUSABLE:
            for unknown in (MemoryAdmission.WITHHOLD, MemoryAdmission.DENY):
                with self.subTest(value=value, unknown=unknown):
                    decision = admit_memory_evidence(
                        value, stale=False, unknown_admission=unknown
                    )
                    self.assertIs(decision.admission, unknown)
                    self.assertEqual(decision.code, "TRUST_CLASS_UNRESOLVED")
                    self.assertIsNone(decision.trust_class)

    def test_unknown_admission_of_load_is_rejected(self):
        with self.assertRaises(MemoryTrustGateError):
            admit_memory_evidence(
                MemoryTrustClass.OBSERVATION,
                stale=False,
                unknown_admission=MemoryAdmission.LOAD,
            )

    def test_unknown_admission_must_be_a_memory_admission(self):
        for bogus in ("WITHHOLD", None, 1):
            with self.subTest(bogus=bogus):
                with self.assertRaises(MemoryTrustGateError):
                    admit_memory_evidence(
                        MemoryTrustClass.OBSERVATION,
                        stale=False,
                        unknown_admission=bogus,  # type: ignore[arg-type]
                    )

    def test_producer_split_is_preserved(self):
        """Lessons WITHHOLD, Skills DENY -- the split #166 corrected.

        Both defaults come from the *call sites* in `context_builder`, so
        assert the constants themselves rather than only the gate's behavior.
        """

        from runtime.context_builder import (
            _UNKNOWN_LESSON_ADMISSION,
            _UNKNOWN_SKILL_ADMISSION,
        )

        self.assertIs(_UNKNOWN_LESSON_ADMISSION, MemoryAdmission.WITHHOLD)
        self.assertIs(_UNKNOWN_SKILL_ADMISSION, MemoryAdmission.DENY)
        self.assertIsNot(_UNKNOWN_LESSON_ADMISSION, _UNKNOWN_SKILL_ADMISSION)


class NonGoalTests(unittest.TestCase):
    """Source-level guards over the design note's stated non-goals (§3)."""

    def _sources(self) -> list[tuple[Path, str]]:
        return [
            (path, _code_only(path.read_text(encoding="utf-8")))
            for path in (
                _REPO_ROOT / "runtime" / "policy" / "memory_trust_gate.py",
                _REPO_ROOT / "runtime" / "context_builder.py",
            )
        ]

    def test_no_policy_engine_or_configurable_threshold(self):
        forbidden = re.compile(
            r"(?<![.\w])(eval|exec)\s*\(|"
            r"\b(rule_engine|policy_engine|RuleEngine|PolicyEngine|Rule)\b|"
            r"\bthreshold\b|\bconfigparser\b|\bos\.environ\b",
            re.IGNORECASE,
        )
        for path, text in self._sources():
            with self.subTest(path=path.name):
                self.assertIsNone(forbidden.search(text), f"policy-engine smell in {path}")

    def test_no_second_authority_database(self):
        forbidden = re.compile(
            r"\bsqlite3\b|\bsqlalchemy\b|\bCREATE TABLE\b|"
            r"\.write_text\(|\.mkdir\(|\bshelve\b|\bpickle\b",
            re.IGNORECASE,
        )
        for path, text in self._sources():
            with self.subTest(path=path.name):
                self.assertIsNone(forbidden.search(text), f"persistence smell in {path}")

    def test_gate_module_declares_no_daemon_or_hook_plumbing(self):
        text = (_REPO_ROOT / "runtime" / "policy" / "memory_trust_gate.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("threading", "asyncio", "subprocess", "HookEvent", "HookEnforcement"):
            self.assertNotIn(forbidden, text)

    def test_trust_module_enum_and_mappings_are_unchanged_in_shape(self):
        """Non-goal: no new enum members, no re-mapped subsystem statuses."""

        self.assertEqual(
            [member.value for member in MemoryTrustClass],
            [
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
            ],
        )

    def test_context_builder_loading_is_load_gated_and_never_reads_content(self):
        """Roadmap 6.9 / S6: `_select_skills` may attach a Skill's body
        (slice 1, #221) and an execution-resource *manifest* (slice 2, #237)
        to the plan, but only under these constraints:

        * both are gated on the trust-gate `MemoryAdmission.LOAD` decision --
          a `WITHHOLD` / `ON_DEMAND` / `DENY` (or `None`-state) Skill gets
          neither;
        * the body comes only through the hash-verifying `load_catalog_skill`
          (never a bare `load_skill(` call);
        * the execution-resource manifest is a *listing* -- `script_paths` /
          `reference_paths` / `example_paths` / `asset_paths` are legitimate
          slice-2 vocabulary now (superseding slice 1's blanket ban on those
          names) -- but `_select_skills` never reads resource *content*: no
          `load_skill_resource(` call (the new slice-2 content-pulling
          primitive, meant for a downstream consumer only) appears here.
        """
        text = (_REPO_ROOT / "runtime" / "context_builder.py").read_text(encoding="utf-8")
        # activation goes through load_catalog_skill (re-verifies the directory
        # hash before reading the body), not a bare load_skill() call.
        self.assertNotIn("load_skill(", text)
        self.assertIn("load_catalog_skill(", text)
        # both the body attach and the manifest attach are gated on LOAD.
        self.assertIn(
            "decision.admission is MemoryAdmission.LOAD and store is not None",
            text,
        )
        # the execution-resource manifest lists paths -- legitimate since #237.
        for execution_level_attr in (
            "script_paths",
            "reference_paths",
            "example_paths",
            "asset_paths",
        ):
            self.assertIn(execution_level_attr, text)
        # but content is never read here -- that is load_skill_resource's job,
        # invoked only by a downstream consumer, never by _select_skills.
        self.assertNotIn("load_skill_resource(", text)


if __name__ == "__main__":
    unittest.main()
