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
    SkillTrustState,
    build_skill_catalog,
    load_catalog_skill,
)


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

    def test_catalog_preserves_explicit_provenance_and_unassessed_trust(self):
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
        self.assertEqual(entry.provenance.trust_state, SkillTrustState.UNASSESSED)
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

    def test_catalog_has_no_way_to_mark_discovery_as_approved(self):
        source = self.source("local")
        self.add_skill(source, "one", "one")
        entry = build_skill_catalog([source]).require_unique("one")

        self.assertEqual(tuple(SkillTrustState), (SkillTrustState.UNASSESSED,))
        self.assertEqual(entry.provenance.trust_state, SkillTrustState.UNASSESSED)


if __name__ == "__main__":
    unittest.main()
