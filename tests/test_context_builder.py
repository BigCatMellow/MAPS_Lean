from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.cli import main as cli_main
from runtime.context_builder import build_context_plan
from runtime.skills import (
    SkillCatalog,
    SkillCatalogSource,
    SkillSourceKind,
    build_project_skill_catalog,
    build_skill_catalog,
)
from runtime.state import TaskStore
from runtime.trust import MemoryTrustClass, TrustClassError


class ContextBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "AGENTS.md").write_text("active authority", encoding="utf-8")
        (self.root / "src.py").write_text("print('ok')\n", encoding="utf-8")
        (self.root / "docs" / "spec.md").write_text("specification\n", encoding="utf-8")
        (self.root / "unrelated.txt").write_text("do not include\n", encoding="utf-8")
        self.db = self.root / "maps.db"
        self.store = TaskStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def create_task(self) -> str:
        dependency = self.store.create_task(task_id="TASK-DEP", title="Dependency")
        self.assertTrue(dependency.ok)
        created = self.store.create_task(task_id="TASK-CONTEXT")
        self.assertTrue(created.ok)
        updated = self.store.update_contract(
            "TASK-CONTEXT",
            {
                "title": "Build context",
                "outcome": "Required context is explicit.",
                "task_type": "RESEARCH",
                "owner": "owner-a",
                "risk": "LOW",
                "decision_authority": "Read-only context planning.",
                "verification": "Inspect exact references and hashes.",
                "evidence_expected": "Context plan JSON.",
                "review_required": "OWNER_CHECK",
                "escalation": "Stop on ambiguous authority.",
                "inputs": [
                    "src.py",
                    "Operator supplied API contract",
                    "https://example.com/external-spec",
                ],
                "sources": [
                    "AGENTS.md",
                    "docs/spec.md",
                    "missing.yaml",
                    "../outside.txt",
                    "docs",
                ],
                "dependencies": ["TASK-DEP"],
                "output_paths": ["context-plan.json"],
                "non_goals": ["Do not scan the repository."],
                "acceptance_criteria": ["Only explicit context is planned."],
                "stop_conditions": ["A required source is outside the repo."],
            },
        )
        self.assertTrue(updated.ok, updated)
        return "TASK-CONTEXT"

    def test_plan_uses_explicit_relationships_and_exact_hashes(self):
        task_id = self.create_task()
        before_task = self.store.get_task(task_id)
        before_events = self.store.list_events(task_id)

        plan = build_context_plan(self.store, task_id, repo_root=self.root)

        self.assertIsNotNone(plan)
        self.assertEqual(plan["task_id"], task_id)
        self.assertTrue(plan["task_revision"])
        self.assertFalse(plan["coverage"]["semantic_retrieval_used"])
        self.assertFalse(plan["coverage"]["repository_scan_used"])
        self.assertFalse(plan["coverage"]["file_contents_included"])

        self.assertEqual(len(plan["authority"]), 1)
        authority = plan["authority"][0]
        self.assertEqual(authority["path"], "AGENTS.md")
        self.assertEqual(authority["role"], "authority")

        by_value = {item["value"]: item for item in plan["required"]}
        self.assertEqual(by_value["src.py"]["status"], "available")
        expected_hash = hashlib.sha256((self.root / "src.py").read_bytes()).hexdigest()
        self.assertEqual(by_value["src.py"]["sha256"], expected_hash)
        self.assertEqual(by_value["docs/spec.md"]["status"], "available")
        self.assertEqual(
            by_value["Operator supplied API contract"]["status"],
            "descriptive_reference",
        )
        self.assertEqual(
            by_value["https://example.com/external-spec"]["status"],
            "external_reference",
        )
        self.assertEqual(by_value["missing.yaml"]["status"], "missing")
        self.assertEqual(by_value["../outside.txt"]["status"], "outside_repo")
        self.assertEqual(by_value["docs"]["status"], "directory_not_expanded")

        serialized = json.dumps(plan)
        self.assertNotIn("unrelated.txt", serialized)
        self.assertNotIn("do not include", serialized)
        self.assertNotIn("print('ok')", serialized)
        self.assertEqual(self.store.get_task(task_id), before_task)
        self.assertEqual(self.store.list_events(task_id), before_events)

    def test_budget_classes_are_assigned_per_item_type(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)

        for item in plan["authority"]:
            self.assertEqual(item["budget_class"], "MUST_LOAD")
        self.assertTrue(plan["required"])
        for item in plan["required"]:
            self.assertEqual(item["budget_class"], "MUST_LOAD")
        self.assertTrue(plan["dependencies"])
        for item in plan["dependencies"]:
            self.assertEqual(item["budget_class"], "SHOULD_LOAD")
        # unresolved items inherit their originating authority/required
        # item's budget_class (same dict object) rather than being
        # independently reclassified as unavailable.
        self.assertTrue(plan["unresolved"])
        for item in plan["unresolved"]:
            self.assertEqual(item["budget_class"], "MUST_LOAD")

        self.assertTrue(plan["coverage"]["budget_classification_present"])

    def test_missing_dependency_is_tagged_should_load(self):
        task_id = self.create_task()
        updated = self.store.update_contract(
            task_id,
            {"dependencies": ["TASK-DEP", "TASK-MISSING"]},
        )
        self.assertTrue(updated.ok, updated)
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        missing = next(
            item for item in plan["dependencies"] if item["task_id"] == "TASK-MISSING"
        )
        self.assertEqual(missing["status"], "MISSING")
        self.assertEqual(missing["budget_class"], "SHOULD_LOAD")

    def test_guidance_and_withheld_guidance_budget_classes(self):
        task_id = self.create_task()
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                self._lesson("LESSON-ACTIVE"), created_by="observer-a"
            ).ok
        )
        self.store.promote_operational_lesson(
            "LESSON-ACTIVE",
            decision_ref="decision:active",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )
        other = self._lesson("LESSON-OTHER-PROJECT")
        other["applicability"] = {
            "global": False,
            "project_ids": ["some-other-project"],
            "task_types": [],
            "risk_levels": [],
            "path_prefixes": [],
        }
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                other, created_by="observer-a"
            ).ok
        )
        self.store.promote_operational_lesson(
            "LESSON-OTHER-PROJECT",
            decision_ref="decision:other",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertTrue(plan["guidance"])
        for item in plan["guidance"]:
            self.assertEqual(item["budget_class"], "SHOULD_LOAD")
            self.assertEqual(item["trust_class"], MemoryTrustClass.REVIEWED_GUIDANCE.value)
        self.assertTrue(plan["withheld_guidance"])
        for item in plan["withheld_guidance"]:
            self.assertEqual(item["budget_class"], "ON_DEMAND")
            self.assertEqual(item["trust_class"], MemoryTrustClass.REVIEWED_GUIDANCE.value)
        self.assertTrue(plan["coverage"]["memory_trust_classification_present"])

    def test_unassessed_skill_is_withheld_from_default_load_set(self):
        """Roadmap 6.22: the trust gate demotes OBSERVATION Skills.

        This replaces the previous assertion that every matched Skill is
        SHOULD_LOAD. `UNASSESSED` provenance maps to `OBSERVATION`, which
        #148's class/action table says must not influence loaded
        instructions, so the gate withholds it. This strengthens the S6 exit
        gate ("unrelated Skills demonstrably stay out of context") rather
        than weakening it: unrelated Skills are still absent entirely, and
        matched-but-unvetted Skills are now out of the default load set too.
        """

        task_id = self.create_task()
        catalog = self._catalog_with_matching_and_unrelated_skill()
        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )
        self.assertTrue(plan["skills"])
        for item in plan["skills"]:
            self.assertEqual(item["trust_class"], MemoryTrustClass.OBSERVATION.value)
            self.assertEqual(item["budget_class"], "ON_DEMAND")
            self.assertEqual(item["withheld_reason"], "TRUST_CLASS_NOT_DEFAULT_LOADABLE")
        # The gate made a real decision, not just an annotation.
        coverage = plan["coverage"]
        self.assertTrue(coverage["memory_trust_gate_applied"])
        self.assertEqual(coverage["memory_trust_gate_admitted"], 0)
        self.assertEqual(coverage["memory_trust_gate_withheld"], len(plan["skills"]))
        self.assertEqual(coverage["memory_trust_gate_denied"], 0)

    def test_no_default_loaded_plan_item_carries_a_non_loadable_trust_class(self):
        """The invariant #148 asserts and nothing previously enforced."""

        task_id = self.create_task()
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                self._lesson("LESSON-ACTIVE"), created_by="observer-a"
            ).ok
        )
        self.store.promote_operational_lesson(
            "LESSON-ACTIVE",
            decision_ref="decision:active",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )
        catalog = self._catalog_with_matching_and_unrelated_skill()
        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )
        loadable = {
            MemoryTrustClass.CANONICAL_POLICY.value,
            MemoryTrustClass.ACTIVE_INSTRUCTION.value,
            MemoryTrustClass.APPROVED_SKILL.value,
            MemoryTrustClass.REVIEWED_GUIDANCE.value,
        }
        default_loaded = [
            item
            for item in [*plan["guidance"], *plan["withheld_guidance"], *plan["skills"]]
            if item["budget_class"] == "SHOULD_LOAD"
        ]
        self.assertTrue(default_loaded)
        for item in default_loaded:
            self.assertIn(item["trust_class"], loadable)

    def test_dependency_state_and_boundaries_are_projected(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["dependencies"][0]["task_id"], "TASK-DEP")
        self.assertEqual(plan["dependencies"][0]["status"], "NEEDS_SHAPING")
        self.assertEqual(
            plan["boundaries"]["acceptance_criteria"],
            ["Only explicit context is planned."],
        )
        unresolved = {item["value"] for item in plan["unresolved"]}
        self.assertEqual(unresolved, {"missing.yaml", "../outside.txt", "docs"})

    def test_invalid_repo_root_is_rejected(self):
        task_id = self.create_task()
        with self.assertRaises(ValueError):
            build_context_plan(
                self.store,
                task_id,
                repo_root=self.root / "does-not-exist",
            )

    def test_cli_context_emits_json(self):
        task_id = self.create_task()
        output = StringIO()
        with redirect_stdout(output):
            code = cli_main(
                [
                    "--db",
                    str(self.db),
                    "context",
                    task_id,
                    "--repo-root",
                    str(self.root),
                ]
            )
        self.assertEqual(code, 0)
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["task_id"], task_id)
        self.assertFalse(plan["coverage"]["semantic_retrieval_used"])

    @staticmethod
    def _lesson(lesson_id: str, *, status: str = "CANDIDATE") -> dict:
        return {
            "lesson_version": 1,
            "lesson_id": lesson_id,
            "status": status,
            "claim": f"Guidance for {lesson_id}.",
            "source_kind": "TASK_OUTCOME",
            "source_refs": [f"outcome:{lesson_id}"],
            "applicability": {
                "global": True,
                "project_ids": [],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": [],
            },
            "created_by": "observer-a",
            "created_at": "2026-08-17T19:00:00Z",
            "promotion": None,
            "superseded_by": None,
            "retirement": None,
        }

    def test_guidance_is_empty_when_no_lessons_exist(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["guidance"], [])
        self.assertEqual(plan["withheld_guidance"], [])

    def test_only_active_lesson_is_surfaced_as_guidance_only(self):
        task_id = self.create_task()
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                self._lesson("LESSON-CAND"), created_by="observer-a"
            ).ok
        )
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                self._lesson("LESSON-RETIRED"), created_by="observer-a"
            ).ok
        )
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                self._lesson("LESSON-ACTIVE"), created_by="observer-a"
            ).ok
        )
        self.store.promote_operational_lesson(
            "LESSON-RETIRED",
            decision_ref="decision:retired",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )
        self.store.retire_operational_lesson(
            "LESSON-RETIRED",
            decision_ref="decision:retire",
            retired_by="operator-a",
            retired_at="2026-08-18T19:00:00Z",
        )
        self.store.promote_operational_lesson(
            "LESSON-ACTIVE",
            decision_ref="decision:active",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        guidance_ids = {item["lesson_id"] for item in plan["guidance"]}
        self.assertEqual(guidance_ids, {"LESSON-ACTIVE"})
        item = plan["guidance"][0]
        self.assertEqual(item["authority"], "GUIDANCE_ONLY")
        self.assertEqual(item["trust_class"], MemoryTrustClass.REVIEWED_GUIDANCE.value)
        self.assertEqual(item["promotion_decision_ref"], "decision:active")
        self.assertEqual(item["source_refs"], ["outcome:LESSON-ACTIVE"])
        serialized = json.dumps(plan)
        self.assertNotIn("LESSON-CAND", serialized)
        self.assertNotIn("LESSON-RETIRED", serialized)

    def test_active_lesson_with_non_matching_applicability_is_withheld(self):
        task_id = self.create_task()
        lesson = self._lesson("LESSON-OTHER-PROJECT")
        lesson["applicability"] = {
            "global": False,
            "project_ids": ["some-other-project"],
            "task_types": [],
            "risk_levels": [],
            "path_prefixes": [],
        }
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                lesson, created_by="observer-a"
            ).ok
        )
        self.store.promote_operational_lesson(
            "LESSON-OTHER-PROJECT",
            decision_ref="decision:other",
            promoted_by="operator-a",
            starts_at="2026-08-17T19:00:00Z",
            review_at="2099-08-20T19:00:00Z",
        )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["guidance"], [])
        withheld = {item["lesson_id"]: item["reason"] for item in plan["withheld_guidance"]}
        self.assertEqual(withheld.get("LESSON-OTHER-PROJECT"), "NOT_APPLICABLE")
        trust = {
            item["lesson_id"]: item["trust_class"] for item in plan["withheld_guidance"]
        }
        self.assertEqual(
            trust.get("LESSON-OTHER-PROJECT"),
            MemoryTrustClass.REVIEWED_GUIDANCE.value,
        )
        # The gate never promotes an already-withheld item, even though
        # REVIEWED_GUIDANCE is a loadable class in the admission table.
        item = plan["withheld_guidance"][0]
        self.assertEqual(item["budget_class"], "ON_DEMAND")
        self.assertEqual(item["withheld_reason"], "WITHHELD_UPSTREAM")
        self.assertEqual(plan["coverage"]["memory_trust_gate_admitted"], 0)
        self.assertEqual(plan["coverage"]["memory_trust_gate_withheld"], 1)

    def test_stale_lessons_stay_withheld_with_trust_metadata(self):
        task_id = self.create_task()
        for lesson_id, review_at, expires_at in (
            ("LESSON-REVIEW", "2026-08-20T19:00:00Z", None),
            ("LESSON-EXPIRED", "2099-08-20T19:00:00Z", "2026-08-20T19:00:00Z"),
        ):
            self.assertTrue(
                self.store.record_operational_lesson_candidate(
                    self._lesson(lesson_id), created_by="observer-a"
                ).ok
            )
            self.store.promote_operational_lesson(
                lesson_id,
                decision_ref=f"decision:{lesson_id}",
                promoted_by="operator-a",
                starts_at="2026-08-17T19:00:00Z",
                review_at=review_at,
                expires_at=expires_at,
            )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)

        self.assertEqual(plan["guidance"], [])
        withheld = {item["lesson_id"]: item for item in plan["withheld_guidance"]}
        self.assertEqual(withheld["LESSON-REVIEW"]["reason"], "REVIEW_DUE")
        self.assertEqual(withheld["LESSON-EXPIRED"]["reason"], "EXPIRED")
        for item in withheld.values():
            self.assertEqual(item["trust_class"], MemoryTrustClass.REVIEWED_GUIDANCE.value)
            self.assertTrue(item["stale_trust_metadata"])
            # stale_trust_metadata is now a gate input that demotes, not a
            # decorative flag.
            self.assertEqual(item["budget_class"], "ON_DEMAND")
            self.assertEqual(item["withheld_reason"], "TRUST_METADATA_STALE")
        self.assertTrue(plan["coverage"]["memory_trust_classification_present"])

    def test_malformed_lesson_record_fails_closed_without_breaking_plan(self):
        task_id = self.create_task()

        class _BrokenLessonsStore(TaskStore):
            def list_active_operational_lessons(self):
                return [
                    {
                        "lesson_version": 1,
                        "lesson_id": "LESSON-BROKEN",
                        "status": "ACTIVE",
                        "claim": "",  # invalid: must be non-empty text
                        "source_kind": "TASK_OUTCOME",
                        "source_refs": ["outcome:LESSON-BROKEN"],
                        "applicability": {
                            "global": True,
                            "project_ids": [],
                            "task_types": [],
                            "risk_levels": [],
                            "path_prefixes": [],
                        },
                        "created_by": "observer-a",
                        "created_at": "2026-08-17T19:00:00Z",
                        "promotion": {
                            "decision_ref": "decision:broken",
                            "promoted_by": "operator-a",
                            "starts_at": "2026-08-17T19:00:00Z",
                            "review_at": "2026-08-20T19:00:00Z",
                            "expires_at": None,
                        },
                        "superseded_by": None,
                        "retirement": None,
                    }
                ]

        broken_store = _BrokenLessonsStore(self.db)
        plan = build_context_plan(broken_store, task_id, repo_root=self.root)
        baseline = build_context_plan(self.store, task_id, repo_root=self.root)

        self.assertIsNotNone(plan)
        self.assertEqual(plan["guidance"], [])
        self.assertEqual(plan["withheld_guidance"], [])
        self.assertEqual(plan["task_id"], task_id)
        self.assertEqual(plan["authority"], baseline["authority"])
        self.assertEqual(plan["required"], baseline["required"])


    @staticmethod
    def _write_skill(skills_root: Path, directory: str, *, name: str, description: str) -> None:
        skill_dir = skills_root / directory
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\nProcedure body.\n",
            encoding="utf-8",
        )

    def _catalog_with_matching_and_unrelated_skill(self) -> SkillCatalog:
        skills_root = self.root / "skills-src"
        skills_root.mkdir()
        self._write_skill(
            skills_root,
            "context-plan-builder",
            name="context-plan-builder",
            description=(
                "Reference guidance for assembling a task context plan during "
                "RESEARCH work."
            ),
        )
        self._write_skill(
            skills_root,
            "database-migration",
            name="database-migration",
            description=(
                "Procedure for safely running PostgreSQL schema migrations in "
                "production clusters."
            ),
        )
        source = SkillCatalogSource(
            source_id="local",
            root=skills_root,
            kind=SkillSourceKind.LOCAL,
        )
        return build_skill_catalog([source])

    def _plan_with_skill_trust_class(self, replacement):
        """Build a plan with `_skill_trust_class` swapped for `replacement`.

        Every catalog entry's `lifecycle_state` is `None` until a store is
        wired into `build_skill_catalog`, so the LOAD and DENY rows of the
        admission table are unreachable through real catalog data.
        Substituting the projection helper is the only way to exercise the
        gate's other outcomes at the real seam.
        """

        task_id = self.create_task()
        catalog = self._catalog_with_matching_and_unrelated_skill()
        with patch("runtime.context_builder._skill_trust_class", replacement):
            return build_context_plan(
                self.store, task_id, repo_root=self.root, skill_catalog=catalog
            )

    def test_quarantined_skill_is_denied_and_absent_from_the_plan(self):
        plan = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.QUARANTINED
        )
        self.assertEqual(plan["skills"], [])
        coverage = plan["coverage"]
        self.assertEqual(coverage["memory_trust_gate_denied"], 1)
        self.assertEqual(coverage["memory_trust_gate_reasons"]["TRUST_CLASS_DENIED"], 1)
        # Denied means absent, not merely demoted: no Skill text in the plan.
        serialized = json.dumps(plan)
        self.assertNotIn("context-plan-builder", serialized)

    def test_unmappable_skill_trust_state_is_denied_not_silently_skipped(self):
        def _raise(state):
            raise TrustClassError("no mapping")

        plan = self._plan_with_skill_trust_class(_raise)
        self.assertEqual(plan["skills"], [])
        coverage = plan["coverage"]
        self.assertEqual(coverage["memory_trust_gate_denied"], 1)
        self.assertEqual(
            coverage["memory_trust_gate_reasons"]["TRUST_CLASS_UNRESOLVED"], 1
        )

    def test_approved_skill_is_admitted_to_the_default_load_set(self):
        plan = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.APPROVED_SKILL
        )
        self.assertEqual(len(plan["skills"]), 1)
        entry = plan["skills"][0]
        self.assertEqual(entry["budget_class"], "SHOULD_LOAD")
        self.assertNotIn("withheld_reason", entry)
        self.assertEqual(plan["coverage"]["memory_trust_gate_admitted"], 1)
        self.assertEqual(plan["coverage"]["memory_trust_gate_denied"], 0)

    # --- roadmap 6.9 / S6 slice 1: progressive body loading ------------------

    def test_load_classified_skill_carries_hash_verified_body(self):
        plan = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.APPROVED_SKILL
        )
        entry = plan["skills"][0]
        self.assertIn("Procedure body.", entry["body"])
        self.assertEqual(len(entry["body_sha256"]), 64)
        self.assertNotIn("body_withheld_reason", entry)
        self.assertEqual(plan["coverage"]["skill_bodies_loaded"], 1)
        # the unrelated Skill contributes nothing -- S6 exit gate
        self.assertEqual(len(plan["skills"]), 1)
        self.assertNotIn("database-migration", json.dumps(plan))

    def test_withheld_skill_has_no_body(self):
        # default: no store subject row -> OBSERVATION -> WITHHOLD / ON_DEMAND
        task_id = self.create_task()
        catalog = self._catalog_with_matching_and_unrelated_skill()
        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )
        entry = plan["skills"][0]
        self.assertEqual(entry["budget_class"], "ON_DEMAND")
        self.assertIn("withheld_reason", entry)
        self.assertNotIn("body", entry)
        self.assertEqual(plan["coverage"]["skill_bodies_loaded"], 0)

    def test_denied_skill_has_no_body(self):
        plan = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.QUARANTINED
        )
        self.assertEqual(plan["skills"], [])
        self.assertEqual(plan["coverage"]["skill_bodies_loaded"], 0)

    def test_body_activation_failure_is_fail_closed(self):
        task_id = self.create_task()
        catalog = self._catalog_with_matching_and_unrelated_skill()
        # mutate the Skill's bytes after discovery so the pre-read hash
        # re-verification in load_skill rejects the content.
        matched_dir = self.root / "skills-src" / "context-plan-builder"
        (matched_dir / "SKILL.md").write_text(
            "---\nname: context-plan-builder\ndescription: Reference guidance "
            "for assembling a task context plan during RESEARCH work.\n---\n"
            "Tampered body.\n",
            encoding="utf-8",
        )
        with patch(
            "runtime.context_builder._skill_trust_class",
            lambda state: MemoryTrustClass.APPROVED_SKILL,
        ):
            plan = build_context_plan(
                self.store, task_id, repo_root=self.root, skill_catalog=catalog
            )
        self.assertIsNotNone(plan)
        entry = plan["skills"][0]
        self.assertNotIn("body", entry)
        self.assertIn("body_withheld_reason", entry)
        self.assertEqual(plan["coverage"]["skill_bodies_loaded"], 0)

    def test_maps_context_plan_has_no_skill_bodies(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["skills"], [])
        self.assertEqual(plan["coverage"]["skill_bodies_loaded"], 0)

    # --- 6.9 / S6 slice 2: execution-resource manifest --------------------

    def _catalog_with_resourced_matching_skill(self) -> SkillCatalog:
        skills_root = self.root / "skills-src"
        skills_root.mkdir()
        self._write_skill(
            skills_root,
            "context-plan-builder",
            name="context-plan-builder",
            description=(
                "Reference guidance for assembling a task context plan during "
                "RESEARCH work."
            ),
        )
        skill = skills_root / "context-plan-builder"
        (skill / "scripts").mkdir()
        (skill / "scripts" / "check.py").write_text("print('c')\n", encoding="utf-8")
        (skill / "references").mkdir()
        (skill / "references" / "guide.md").write_text("# guide\n", encoding="utf-8")
        source = SkillCatalogSource(
            source_id="local", root=skills_root, kind=SkillSourceKind.LOCAL
        )
        return build_skill_catalog([source])

    def test_load_skill_carries_execution_resource_manifest_without_content(self):
        task_id = self.create_task()
        catalog = self._catalog_with_resourced_matching_skill()
        with patch(
            "runtime.context_builder._skill_trust_class",
            lambda state: MemoryTrustClass.APPROVED_SKILL,
        ):
            plan = build_context_plan(
                self.store, task_id, repo_root=self.root, skill_catalog=catalog
            )
        entry = plan["skills"][0]
        manifest = entry["execution_resources"]
        by_path = {r["path"]: r for r in manifest}
        self.assertEqual(
            sorted(by_path), ["references/guide.md", "scripts/check.py"]
        )
        self.assertEqual(by_path["scripts/check.py"]["kind"], "script")
        self.assertEqual(by_path["references/guide.md"]["kind"], "reference")
        self.assertEqual(by_path["scripts/check.py"]["size_bytes"], len(b"print('c')\n"))
        # no file content anywhere in the manifest or the plan
        for r in manifest:
            self.assertEqual(set(r), {"path", "kind", "size_bytes"})
        self.assertNotIn("print('c')", json.dumps(plan))
        self.assertNotIn("# guide", json.dumps(plan))
        self.assertEqual(plan["coverage"]["skill_execution_resources_listed"], 1)

    def test_load_skill_with_no_resources_has_no_manifest_key(self):
        plan = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.APPROVED_SKILL
        )
        entry = plan["skills"][0]
        self.assertNotIn("execution_resources", entry)
        self.assertEqual(plan["coverage"]["skill_execution_resources_listed"], 0)

    def test_withheld_skill_gets_no_execution_manifest(self):
        # default None-state Skill -> OBSERVATION -> WITHHOLD / ON_DEMAND
        task_id = self.create_task()
        catalog = self._catalog_with_resourced_matching_skill()
        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )
        self.assertNotIn("execution_resources", plan["skills"][0])
        self.assertEqual(plan["coverage"]["skill_execution_resources_listed"], 0)

    def test_denied_skill_gets_no_execution_manifest(self):
        denied = self._plan_with_skill_trust_class(
            lambda state: MemoryTrustClass.QUARANTINED
        )
        self.assertEqual(denied["skills"], [])
        self.assertEqual(
            denied["coverage"]["skill_execution_resources_listed"], 0
        )

    def test_execution_manifest_build_failure_is_fail_closed(self):
        task_id = self.create_task()
        catalog = self._catalog_with_resourced_matching_skill()
        with patch(
            "runtime.context_builder._skill_trust_class",
            lambda state: MemoryTrustClass.APPROVED_SKILL,
        ), patch(
            "runtime.context_builder._execution_resource_manifest",
            side_effect=OSError("boom"),
        ):
            plan = build_context_plan(
                self.store, task_id, repo_root=self.root, skill_catalog=catalog
            )
        self.assertIsNotNone(plan)
        entry = plan["skills"][0]
        self.assertNotIn("execution_resources", entry)
        self.assertEqual(entry["execution_resources_withheld_reason"], "OSError")
        self.assertEqual(plan["coverage"]["skill_execution_resources_listed"], 0)

    def test_skills_default_empty_without_catalog(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["skills"], [])

    def test_skills_empty_when_catalog_has_no_matching_skill(self):
        task_id = self.create_task()
        skills_root = self.root / "skills-src-unrelated"
        skills_root.mkdir()
        self._write_skill(
            skills_root,
            "database-migration",
            name="database-migration",
            description=(
                "Procedure for safely running PostgreSQL schema migrations in "
                "production clusters."
            ),
        )
        catalog = build_skill_catalog(
            [SkillCatalogSource(source_id="local", root=skills_root, kind=SkillSourceKind.LOCAL)]
        )
        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )
        self.assertEqual(plan["skills"], [])

    def test_matching_skill_is_selected_and_unrelated_skill_stays_out_of_context(self):
        task_id = self.create_task()
        catalog = self._catalog_with_matching_and_unrelated_skill()

        plan = build_context_plan(
            self.store, task_id, repo_root=self.root, skill_catalog=catalog
        )

        skill_ids = {item["skill_id"] for item in plan["skills"]}
        self.assertEqual(skill_ids, {"context-plan-builder"})
        self.assertNotIn("database-migration", skill_ids)

        entry = plan["skills"][0]
        self.assertEqual(entry["name"], "context-plan-builder")
        self.assertEqual(entry["source_id"], "local")
        self.assertIsNone(entry["lifecycle_state"])
        self.assertEqual(entry["trust_class"], MemoryTrustClass.OBSERVATION.value)
        self.assertIn("context", entry["selection_reason"])
        self.assertTrue(entry["catalog_key"])
        self.assertTrue(plan["coverage"]["memory_trust_classification_present"])

        # Exit gate: the unrelated Skill must not merely be "not selected" --
        # it must be demonstrably absent from the serialized plan entirely,
        # including anywhere content could leak (e.g. instructions/boundaries).
        serialized = json.dumps(plan)
        self.assertNotIn("database-migration", serialized)
        self.assertNotIn("PostgreSQL", serialized)

        # Skill selection is attributed evidence, never spliced into
        # instruction-bearing fields.
        self.assertNotIn("skills", plan["boundaries"])

    def test_skills_not_loaded_when_catalog_omitted_even_with_lessons(self):
        task_id = self.create_task()
        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertIn("skills", plan)
        self.assertEqual(plan["skills"], [])


class CoverageNoteConsistencyTests(unittest.TestCase):
    """Part A of the invariant-prose-drift rule-20 safeguard
    (`work/notes/2026-09-01-invariant-prose-drift-safeguard-design.md` §3).

    Every self-describing ``*_note`` string in ``build_context_plan``'s
    ``coverage`` dict is asserted here against the ``coverage`` dict that the
    *same* plan produced — so a `_select_skills` / coverage-assembly change
    that makes a note lie fails CI, close to the diff.

    This test also subscripts each note key by name (``coverage["<key>"]``),
    which is what ``scripts/check_coverage_note_pins.py`` (Part B) checks for.

    Robustness ceiling (design §3): it catches (i) a note reverting to a
    known-bad unqualified claim and (ii) a structural note<->coverage
    inconsistency it is written to check — NOT an arbitrary future false note.
    Part B stops a new note being born unchecked.

    Generalizes and replaces PR #229's
    ``test_skill_capability_manifest.py::test_coverage_note_acknowledges_the_pre_trust_gate_capability_deny``
    (one consistency test, in the module's own test file — not two).
    """

    _CAPABILITY_REASON = "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE"

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name) / "repo"
        (self.repo / ".claude" / "skills").mkdir(parents=True)
        (self.repo / "AGENTS.md").write_text("active authority\n", encoding="utf-8")
        self.store = TaskStore(self.repo / "maps.db")

    def _add_skill(self, name, description, capabilities=None):
        skill = self.repo / ".claude" / "skills" / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n"
            "1. Do the bounded work.\n",
            encoding="utf-8",
        )
        if capabilities is not None:
            (skill / "capabilities").write_text(capabilities, encoding="utf-8")

    def _multi_path_plan(self):
        """A plan that exercises every admission path a coverage note describes:
        a capability-envelope DENY (pre-trust-gate), a real trust-gate decision,
        and memory-like guidance carrying trust metadata."""
        # capability-envelope DENY: declares process-stop, task is not destructive.
        self._add_skill(
            "research-stopper",
            "RESEARCH context planning that can stop a runaway process.",
            capabilities="process-stop\n",
        )
        # a plain matched Skill -> goes through the trust gate for a real decision.
        self._add_skill(
            "research-plain",
            "RESEARCH context planning with a plain deterministic procedure.",
        )
        self.assertTrue(self.store.create_task(task_id="T").ok)
        self.assertTrue(
            self.store.update_contract(
                "T",
                {
                    "title": "Research context assembly",
                    "outcome": "Context is explicit.",
                    "task_type": "RESEARCH",
                    "owner": "owner-a",
                    "risk": "LOW",
                    "decision_authority": "Read-only context planning.",
                    "verification": "Inspect references.",
                    "evidence_expected": "Context plan JSON.",
                    "review_required": "OWNER_CHECK",
                    "escalation": "Stop on ambiguity.",
                    "inputs": ["AGENTS.md"],
                    "sources": ["AGENTS.md"],
                    "dependencies": [],
                    "output_paths": ["research-context.json"],
                    "non_goals": ["Do not scan the repository."],
                    "acceptance_criteria": ["Only explicit context is planned."],
                    "stop_conditions": ["A required source is outside the repo."],
                    "policy": {
                        "requires_operator_approval": False,
                        "destructive_action": False,
                        "external_side_effect": False,
                        "security_sensitive": False,
                        "broad_architecture": False,
                        "paid_execution": False,
                    },
                },
            ).ok
        )
        # a stale operational lesson -> withheld_guidance carrying trust metadata.
        lesson = {
            "lesson_version": 1,
            "lesson_id": "LESSON-STALE",
            "status": "CANDIDATE",
            "claim": "Prefer the deterministic path.",
            "source_kind": "TASK_OUTCOME",
            "source_refs": ["outcome:LESSON-STALE"],
            "applicability": {
                "global": True,
                "project_ids": [],
                "task_types": [],
                "risk_levels": [],
                "path_prefixes": [],
            },
            "created_by": "observer-a",
            "created_at": "2026-08-17T19:00:00Z",
            "promotion": None,
            "superseded_by": None,
            "retirement": None,
        }
        self.assertTrue(
            self.store.record_operational_lesson_candidate(
                lesson, created_by="observer-a"
            ).ok
        )
        self.assertTrue(
            self.store.promote_operational_lesson(
                "LESSON-STALE",
                decision_ref="decision:LESSON-STALE",
                promoted_by="operator-a",
                starts_at="2026-08-17T19:00:00Z",
                review_at="2026-08-20T19:00:00Z",
                expires_at=None,
            ).ok
        )
        catalog = build_project_skill_catalog(self.repo, self.store)
        return build_context_plan(
            self.store, "T", repo_root=self.repo, skill_catalog=catalog
        )

    def test_every_coverage_note_is_consistent_with_its_own_plan(self):
        plan = self._multi_path_plan()
        coverage = plan["coverage"]

        # --- note ------------------------------------------------------
        note = coverage["note"]
        self.assertIn("does not", note)
        self.assertFalse(coverage["semantic_retrieval_used"])
        self.assertFalse(coverage["repository_scan_used"])
        self.assertFalse(coverage["file_contents_included"])

        # --- budget_classification_note ------------------------------
        budget_note = coverage["budget_classification_note"]
        self.assertIn("No new retrieval mechanism", budget_note)
        # the claim is verified by the same "no search" flags ...
        self.assertFalse(coverage["semantic_retrieval_used"])
        self.assertFalse(coverage["repository_scan_used"])
        # ... and the "tagged by the memory trust gate" half:
        self.assertIn("memory trust gate", budget_note)
        self.assertTrue(coverage["memory_trust_gate_applied"])

        # --- memory_trust_classification_note -----------------------
        mtc_note = coverage["memory_trust_classification_note"]
        self.assertIn("fails closed", mtc_note)
        self.assertTrue(coverage["memory_trust_classification_present"])
        # "without suppressing canonical authority or required task context":
        self.assertTrue(plan["authority"])
        self.assertIn("required", plan)
        # metadata "when present": the stale lesson is withheld with trust class.
        self.assertTrue(plan["withheld_guidance"])
        self.assertTrue(
            all("trust_class" in item for item in plan["withheld_guidance"])
        )

        # --- memory_trust_gate_note (the one that drifted, PR #225) ---
        gate_note = coverage["memory_trust_gate_note"]
        reasons = coverage["memory_trust_gate_reasons"]
        # the plan really did exercise both paths:
        self.assertEqual(reasons.get(self._CAPABILITY_REASON), 1)
        self.assertGreaterEqual(coverage["memory_trust_gate_denied"], 1)
        self.assertTrue(
            any(r.startswith("TRUST_CLASS_") for r in reasons),
            f"expected a trust-class reason in {reasons}",
        )
        # A non-trust reason is present -> the note MUST be qualified. PR #225's
        # note ("every memory-like item passed admit_memory_evidence(); its
        # MemoryTrustClass alone decides ...") had none of these and this test
        # would have failed it.
        self.assertIn("reaches the trust gate", gate_note)
        self.assertNotIn(
            "every memory-like item passed admit_memory_evidence", gate_note
        )
        self.assertIn(self._CAPABILITY_REASON, gate_note)
        self.assertIn("outside the trust gate", gate_note)
        self.assertIn("capabilities_within_envelope", gate_note)


if __name__ == "__main__":
    unittest.main()
