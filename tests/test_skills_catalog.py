from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.skills import (
    SkillAmbiguousError,
    SkillCatalogError,
    SkillCatalogSource,
    SkillNotFoundError,
    SkillSourceKind,
    build_project_skill_catalog,
    build_skill_catalog,
    load_catalog_skill,
    register_skill_catalog,
)
from runtime.skills.catalog import _catalog_key
from runtime.skills.gate import SkillGateDisposition
from runtime.skills.lifecycle import SkillLifecycleState
from runtime.state import TaskStore


SKILL = """---
name: {name}
description: Procedure for {name}.
---
# {name}

Procedure body.
"""


class SkillCatalogTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)

    def source(self, source_id, kind=SkillSourceKind.LOCAL, **kwargs):
        root = self.root / source_id
        root.mkdir()
        return SkillCatalogSource(
            source_id=source_id,
            root=root,
            kind=kind,
            **kwargs,
        )

    @staticmethod
    def add_skill(source: SkillCatalogSource, directory: str, name: str):
        skill = source.root / directory
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            SKILL.format(name=name),
            encoding="utf-8",
        )
        return skill

    def test_catalog_preserves_explicit_provenance_and_unassessed_lifecycle(self):
        bundled = self.source(
            "bundled",
            SkillSourceKind.BUNDLED,
            source_ref="repo://skills/bundled",
            declared_revision="commit-123",
        )
        self.add_skill(bundled, "release", "release")

        catalog = build_skill_catalog([bundled])
        entry = catalog.require_unique("release")

        self.assertEqual(entry.provenance.source_id, "bundled")
        self.assertEqual(entry.provenance.source_kind, SkillSourceKind.BUNDLED)
        self.assertEqual(entry.provenance.source_ref, "repo://skills/bundled")
        self.assertEqual(entry.provenance.declared_revision, "commit-123")
        self.assertIsNone(entry.provenance.lifecycle_state)
        self.assertIn(entry.descriptor.content_sha256, entry.catalog_key)

    def test_catalog_build_does_not_load_skill_bodies(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")

        with patch("runtime.skills.format._read_body", side_effect=AssertionError("body loaded")):
            catalog = build_skill_catalog([source])

        self.assertEqual(catalog.require_unique("one").descriptor.name, "one")

    def test_catalog_order_and_fingerprint_are_source_input_order_independent(self):
        alpha = self.source("alpha")
        beta = self.source("beta")
        self.add_skill(alpha, "a", "a")
        self.add_skill(beta, "b", "b")

        first = build_skill_catalog([beta, alpha])
        second = build_skill_catalog([alpha, beta])

        self.assertEqual(first.entries, second.entries)
        self.assertEqual(first.fingerprint, second.fingerprint)

    def test_content_change_changes_catalog_fingerprint(self):
        source = self.source("local")
        skill = self.add_skill(source, "one", "one")
        first = build_skill_catalog([source])

        reference = skill / "references" / "guide.md"
        reference.parent.mkdir()
        reference.write_text("new reference\n", encoding="utf-8")
        second = build_skill_catalog([source])

        self.assertNotEqual(first.fingerprint, second.fingerprint)

    def test_duplicate_source_ids_are_rejected(self):
        first = self.source("one")
        second_root = self.root / "other"
        second_root.mkdir()
        second = SkillCatalogSource(
            source_id="one",
            root=second_root,
            kind=SkillSourceKind.LOCAL,
        )

        with self.assertRaises(SkillCatalogError):
            build_skill_catalog([first, second])

    def test_same_name_across_sources_is_preserved_as_explicit_conflict(self):
        first = self.source("one")
        second = self.source("two")
        self.add_skill(first, "deploy-a", "deploy")
        self.add_skill(second, "deploy-b", "deploy")

        catalog = build_skill_catalog([first, second])

        self.assertEqual(len(catalog.find("deploy")), 2)
        self.assertEqual(len(catalog.conflicts), 1)
        self.assertEqual(catalog.conflicts[0].name, "deploy")
        with self.assertRaises(SkillAmbiguousError):
            catalog.require_unique("deploy")

    def test_missing_skill_is_not_inferred(self):
        source = self.source("empty")
        catalog = build_skill_catalog([source])

        with self.assertRaises(SkillNotFoundError):
            catalog.require_unique("probably-this-one")

    def test_catalog_activation_reuses_hash_drift_guard(self):
        source = self.source("local")
        skill = self.add_skill(source, "one", "one")
        catalog = build_skill_catalog([source])
        entry = catalog.require_unique("one")

        document = load_catalog_skill(entry)
        self.assertIn("Procedure body", document.body)

        (skill / "SKILL.md").write_text(
            SKILL.format(name="one") + "\nchanged\n",
            encoding="utf-8",
        )
        from runtime.skills import SkillChangedError

        with self.assertRaises(SkillChangedError):
            load_catalog_skill(entry)

    def test_default_source_ref_is_resolved_root_path(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")

        entry = build_skill_catalog([source]).require_unique("one")

        self.assertEqual(entry.provenance.source_ref, str(source.root.resolve()))

    def test_catalog_build_without_store_leaves_lifecycle_state_none(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")
        entry = build_skill_catalog([source]).require_unique("one")

        # No store supplied -> no durable read -> "not yet assessed".
        self.assertIsNone(entry.provenance.lifecycle_state)

    def test_fingerprint_is_content_only_not_lifecycle_sensitive(self):
        # Two catalogs over the same content: one built with a store that has
        # recorded (and would report) a lifecycle state, one without. The
        # fingerprint must be identical -- approval state is not part of the
        # catalog's identity (design note 2026-08-31 Q7).
        source = self.source("local")
        self.add_skill(source, "one", "one")
        plain = build_skill_catalog([source])

        store = _temp_store(self)
        entry = plain.require_unique("one")
        assessed = build_skill_catalog(
            [SkillCatalogSource(source_id="local", root=source.root, kind=SkillSourceKind.LOCAL)],
            store=store,
        )
        register_skill_catalog(assessed, store)
        rebuilt = build_skill_catalog(
            [SkillCatalogSource(source_id="local", root=source.root, kind=SkillSourceKind.LOCAL)],
            store=store,
        )
        self.assertIsNotNone(rebuilt.require_unique("one").provenance.lifecycle_state)
        self.assertEqual(plain.fingerprint, rebuilt.fingerprint)

    def test_register_skill_catalog_records_subjects_and_is_idempotent(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")
        store = _temp_store(self)
        catalog = build_skill_catalog([source])
        entry = catalog.require_unique("one")

        first = register_skill_catalog(catalog, store)
        self.assertEqual(len(first), 1)
        self.assertTrue(first[0].ok)
        state = store.get_skill_lifecycle_state(entry.catalog_key)
        self.assertIn(
            state, (SkillLifecycleState.VALIDATED, SkillLifecycleState.QUARANTINED)
        )

        second = register_skill_catalog(catalog, store)
        self.assertEqual(second, [])
        self.assertEqual(
            len(store.list_skill_lifecycle_subjects()), 1
        )

    def test_load_catalog_skill_refuses_non_activatable_state(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")
        store = _temp_store(self)
        catalog = build_skill_catalog([source])
        entry = catalog.require_unique("one")
        register_skill_catalog(catalog, store)

        # VALIDATED (or QUARANTINED) is the gate-derived start. Drive it to
        # RETIRED via a QUARANTINED subject, or straight to a refused state.
        state = store.get_skill_lifecycle_state(entry.catalog_key)
        if state is SkillLifecycleState.VALIDATED:
            store.record_skill_lifecycle_transition(
                entry.catalog_key,
                SkillLifecycleState.APPROVED,
                decision_ref="test",
                decided_by="operator",
            )
            store.record_skill_lifecycle_transition(
                entry.catalog_key, SkillLifecycleState.ACTIVE, decision_ref="test"
            )
            store.record_skill_lifecycle_transition(
                entry.catalog_key, SkillLifecycleState.RETIRED, decision_ref="test"
            )
        else:
            store.record_skill_lifecycle_transition(
                entry.catalog_key, SkillLifecycleState.RETIRED, decision_ref="test"
            )

        with self.assertRaises(SkillCatalogError):
            load_catalog_skill(entry, store)

        # Without the store, activation is not gated on lifecycle state.
        self.assertIsNotNone(load_catalog_skill(entry))

    def test_load_catalog_skill_allows_activatable_and_unassessed(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")
        store = _temp_store(self)
        catalog = build_skill_catalog([source])
        entry = catalog.require_unique("one")

        # No subject row yet -> None -> allowed.
        self.assertIsNotNone(load_catalog_skill(entry, store))

        register_skill_catalog(catalog, store)
        if store.get_skill_lifecycle_state(entry.catalog_key) is SkillLifecycleState.VALIDATED:
            self.assertIsNotNone(load_catalog_skill(entry, store))


def _temp_store(test_case):
    td = tempfile.TemporaryDirectory()
    test_case.addCleanup(td.cleanup)
    return TaskStore(Path(td.name) / "state.db")


class CatalogKeyFormatTests(unittest.TestCase):
    """`catalog_key` is a persistence key -- pin its exact string layout so a
    reordering / separator change is caught (the round-trip tests only assert
    the content hash is a substring)."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        root = Path(self.td.name) / "bundled"
        root.mkdir()
        (root / "one").mkdir()
        (root / "one" / "SKILL.md").write_text(SKILL.format(name="one"), encoding="utf-8")
        self.source = SkillCatalogSource(
            source_id="bundled", root=root, kind=SkillSourceKind.BUNDLED
        )

    def test_catalog_key_exact_format_is_pinned(self):
        catalog = build_skill_catalog([self.source])
        entry = catalog.require_unique("one")
        d = entry.descriptor
        expected = f"bundled:{d.skill_id}@sha256:{d.content_sha256}"
        self.assertEqual(_catalog_key("bundled", d), expected)
        self.assertEqual(entry.catalog_key, expected)

    def test_catalog_key_orders_source_id_before_skill_id(self):
        catalog = build_skill_catalog([self.source])
        d = catalog.require_unique("one").descriptor
        key = _catalog_key("bundled", d)
        self.assertTrue(key.startswith(f"bundled:{d.skill_id}@sha256:"))
        self.assertLess(key.index("bundled"), key.index(d.skill_id))
        self.assertEqual(key.count(":"), 2)  # source_id:skill_id + @sha256:


class BuildProjectSkillCatalogTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.repo = Path(self.td.name) / "repo"
        self.repo.mkdir()

    def _add(self, name: str):
        skill = self.repo / ".claude" / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(SKILL.format(name=name), encoding="utf-8")

    def test_discovers_bundled_source_and_records_subjects_idempotently(self):
        self._add("one")
        store = _temp_store(self)
        catalog = build_project_skill_catalog(self.repo, store)
        entry = catalog.require_unique("one")
        self.assertEqual(entry.provenance.source_id, "bundled")
        self.assertEqual(entry.provenance.source_kind, SkillSourceKind.BUNDLED)
        self.assertIsNotNone(store.get_skill_lifecycle_state(entry.catalog_key))

        build_project_skill_catalog(self.repo, store)  # idempotent
        self.assertEqual(len(store.list_skill_lifecycle_subjects()), 1)

    def test_missing_skills_dir_yields_empty_catalog_and_no_writes(self):
        store = _temp_store(self)
        catalog = build_project_skill_catalog(self.repo, store)
        self.assertEqual(catalog.entries, ())
        self.assertEqual(store.list_skill_lifecycle_subjects(), [])


if __name__ == "__main__":
    unittest.main()
