from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from runtime.cli import main as cli_main
from runtime.context_builder import build_context_plan
from runtime.skills import (
    SkillCatalog,
    SkillCatalogSource,
    SkillSourceKind,
    build_skill_catalog,
)
from runtime.state import TaskStore


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
            review_at="2026-08-20T19:00:00Z",
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
            review_at="2026-08-20T19:00:00Z",
        )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        guidance_ids = {item["lesson_id"] for item in plan["guidance"]}
        self.assertEqual(guidance_ids, {"LESSON-ACTIVE"})
        item = plan["guidance"][0]
        self.assertEqual(item["authority"], "GUIDANCE_ONLY")
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
            review_at="2026-08-20T19:00:00Z",
        )

        plan = build_context_plan(self.store, task_id, repo_root=self.root)
        self.assertEqual(plan["guidance"], [])
        withheld = {item["lesson_id"]: item["reason"] for item in plan["withheld_guidance"]}
        self.assertEqual(withheld.get("LESSON-OTHER-PROJECT"), "NOT_APPLICABLE")

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
        self.assertEqual(entry["trust_state"], "UNASSESSED")
        self.assertIn("context", entry["selection_reason"])
        self.assertTrue(entry["catalog_key"])

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


if __name__ == "__main__":
    unittest.main()
