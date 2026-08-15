from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from runtime.skills import (
    SkillChangedError,
    SkillParseError,
    discover_skills,
    load_skill,
)


VALID_SKILL = """---
name: safe-release
description: Safely verify and prepare a release.
metadata:
  maps-risk: medium
license: MIT
---
# Safe release

Run the documented checks before release.
"""


class SkillFormatTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name) / "skills"
        self.root.mkdir()

    def make_skill(self, directory="safe-release", text=VALID_SKILL):
        skill = self.root / directory
        skill.mkdir()
        (skill / "SKILL.md").write_text(text, encoding="utf-8")
        return skill

    def test_discovery_returns_compact_metadata_without_loading_body(self):
        self.make_skill()

        with patch("runtime.skills.format._read_body", side_effect=AssertionError("body loaded")):
            descriptors = discover_skills(self.root)

        self.assertEqual(len(descriptors), 1)
        descriptor = descriptors[0]
        self.assertEqual(descriptor.skill_id, "safe-release")
        self.assertEqual(descriptor.name, "safe-release")
        self.assertEqual(
            descriptor.description,
            "Safely verify and prepare a release.",
        )
        self.assertIn("metadata", descriptor.declared_metadata_keys)
        self.assertIn("license", descriptor.declared_metadata_keys)
        self.assertFalse(hasattr(descriptor, "body"))

    def test_activation_loads_body_only_after_hash_verification(self):
        self.make_skill()
        descriptor = discover_skills(self.root)[0]

        document = load_skill(descriptor)

        self.assertIn("# Safe release", document.body)
        self.assertEqual(document.descriptor.content_sha256, descriptor.content_sha256)

    def test_block_scalar_description_is_supported(self):
        self.make_skill(
            text="""---
name: migration
description: >-
  Perform a safe database migration
  with explicit verification.
---
Procedure body.
"""
        )

        descriptor = discover_skills(self.root)[0]

        self.assertEqual(
            descriptor.description,
            "Perform a safe database migration with explicit verification.",
        )

    def test_yaml_style_single_quote_escape_is_supported(self):
        self.make_skill(
            text="""---
name: quoted
description: 'Don''t bypass review.'
---
Body.
"""
        )

        descriptor = discover_skills(self.root)[0]

        self.assertEqual(descriptor.description, "Don't bypass review.")

    def test_missing_or_unclosed_frontmatter_is_rejected(self):
        self.make_skill(text="name: bad\ndescription: bad\n")
        with self.assertRaises(SkillParseError):
            discover_skills(self.root)

        (self.root / "safe-release" / "SKILL.md").write_text(
            "---\nname: bad\ndescription: bad\n",
            encoding="utf-8",
        )
        with self.assertRaises(SkillParseError):
            discover_skills(self.root)

    def test_required_fields_must_be_non_empty(self):
        self.make_skill(
            text="""---
name: x
description:
---
Body.
"""
        )

        with self.assertRaises(SkillParseError):
            discover_skills(self.root)

    def test_duplicate_frontmatter_key_is_rejected(self):
        self.make_skill(
            text="""---
name: x
name: y
description: duplicate
---
Body.
"""
        )

        with self.assertRaises(SkillParseError):
            discover_skills(self.root)

    def test_duplicate_skill_names_across_directories_are_rejected(self):
        self.make_skill("one")
        text = VALID_SKILL.replace("# Safe release", "# Another copy")
        self.make_skill("two", text=text)

        with self.assertRaises(SkillParseError):
            discover_skills(self.root)

    def test_resource_inventory_is_explicit_and_non_executing(self):
        skill = self.make_skill()
        for relative, content in (
            ("scripts/check.py", "print('check')\n"),
            ("references/release.md", "reference\n"),
            ("assets/template.txt", "asset\n"),
            ("examples/good.yaml", "example: true\n"),
            ("notes.txt", "other\n"),
        ):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        descriptor = discover_skills(self.root)[0]

        self.assertEqual(
            descriptor.resource_paths,
            (
                "assets/template.txt",
                "examples/good.yaml",
                "notes.txt",
                "references/release.md",
                "scripts/check.py",
            ),
        )
        self.assertEqual(descriptor.script_paths, ("scripts/check.py",))
        self.assertEqual(descriptor.reference_paths, ("references/release.md",))
        self.assertEqual(descriptor.asset_paths, ("assets/template.txt",))
        self.assertEqual(descriptor.example_paths, ("examples/good.yaml",))

    def test_hash_is_stable_for_same_paths_and_bytes(self):
        first_root = self.root / "set-a"
        second_root = self.root / "set-b"
        first_root.mkdir()
        second_root.mkdir()

        def build(parent: Path, reverse: bool):
            skill = parent / "same"
            skill.mkdir()
            entries = [
                ("SKILL.md", VALID_SKILL),
                ("references/b.txt", "b\n"),
                ("references/a.txt", "a\n"),
            ]
            if reverse:
                entries.reverse()
            for relative, text in entries:
                path = skill / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

        build(first_root, False)
        build(second_root, True)

        first = discover_skills(first_root)[0]
        second = discover_skills(second_root)[0]

        self.assertEqual(first.content_sha256, second.content_sha256)

    def test_resource_change_invalidates_discovered_descriptor(self):
        skill = self.make_skill()
        reference = skill / "references" / "guide.md"
        reference.parent.mkdir()
        reference.write_text("v1\n", encoding="utf-8")
        descriptor = discover_skills(self.root)[0]

        reference.write_text("v2\n", encoding="utf-8")

        with self.assertRaises(SkillChangedError):
            load_skill(descriptor)

    def test_directory_without_skill_file_is_ignored(self):
        (self.root / "notes").mkdir()
        (self.root / "notes" / "README.md").write_text("not a skill\n", encoding="utf-8")

        self.assertEqual(discover_skills(self.root), ())

    def test_missing_skills_root_is_empty(self):
        self.assertEqual(discover_skills(self.root / "missing"), ())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_symlinked_resource_is_rejected(self):
        skill = self.make_skill()
        outside = Path(self.td.name) / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        link = skill / "references" / "outside.txt"
        link.parent.mkdir()
        link.symlink_to(outside)

        with self.assertRaises(SkillParseError):
            discover_skills(self.root)


if __name__ == "__main__":
    unittest.main()
