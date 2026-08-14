#!/usr/bin/env python3
"""Contradiction checks for TASK-303's canonical MAP authority hierarchy."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "MAP_System"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class AuthorityHierarchyContractTest(unittest.TestCase):
    def test_project_brief_is_the_complete_canonical_view(self) -> None:
        text = read("MAP_System/shared/project-brief.md")
        for expected in (
            "This is MAP's canonical authority hierarchy",
            "Operator — `bigboss` / Command Center",
            "One designated coordinator per run",
            "accountable owner and independent reviewer",
            "Bounded support — Pi, Librarian, visible helpers, and local assistants",
            "Session continuity is a separate axis from authority",
            "Control systems are not roles",
        ):
            self.assertIn(expected, text)

    def test_governing_rules_link_and_preserve_the_hierarchy(self) -> None:
        root_rules = read("AGENTS.md")
        map_rules = read("MAP_System/AGENTS.md")
        self.assertIn("What is the canonical MAP authority hierarchy?", root_rules)
        for expected in (
            "`bigboss` / operator / Command Center",
            "One operator-designated coordinator",
            "eligible peer core agents",
            "one accountable owner and a different independent",
            "Pi, Librarian, visible helpers, and local assistants",
            "systems and open terminals do not become authorities",
        ):
            self.assertIn(expected, map_rules)

    def test_fixed_roster_prompts_distinguish_visibility_from_authority(self) -> None:
        launchers = {
            name: read(f"MAP_System/templates/install/bin/{name}")
            for name in (
                "ai-command-center-lab-codex",
                "ai-command-center-lab-claude",
                "ai-command-center-lab-pi",
                "ai-command-center-lab-librarian",
            )
        }
        for text in launchers.values():
            self.assertIn("canonical MAP authority hierarchy", text)
            self.assertIn("bigboss/operator", text)
            self.assertIn("explicitly designated", text)
            self.assertIn("conflict-separated independent reviewers", text)

        for bounded in ("ai-command-center-lab-pi", "ai-command-center-lab-librarian"):
            self.assertIn("grants no task, review, release, routing, policy", launchers[bounded])

        lua = read("MAP_System/templates/install/wezterm/ai-command-center-lab.lua")
        self.assertIn("Visibility is not authority", lua)
        self.assertIn("one run coordinator", lua)
        self.assertIn("task owners", lua)
        self.assertIn("independent reviewers", lua)

    def test_rotation_does_not_transfer_authority_before_finalize(self) -> None:
        guide = read("MAP_System/notes/context-rotation-guide.md")
        lifecycle = read("MAP_System/notes/command-center-orchestrator-lifecycle.md")
        for text in (guide, lifecycle):
            self.assertIn("`prepare`", text)
            self.assertIn("`ack`", text)
            self.assertIn("`finalize`", text)
            self.assertIn("transfers no authority", text)
        self.assertIn("Only this successful finalization makes the replacement", guide)
        self.assertIn("continues a designated coordinator role only after finalization", lifecycle)

    def test_active_surfaces_reject_known_contradictions(self) -> None:
        active_surfaces = "\n".join(
            read(path)
            for path in (
                "MAP_System/shared/project-brief.md",
                "MAP_System/AGENTS.md",
                "MAP_System/notes/context-rotation-guide.md",
                "MAP_System/notes/command-center-orchestrator-lifecycle.md",
                "MAP_System/templates/install/bin/ai-command-center-lab-codex",
                "MAP_System/templates/install/bin/ai-command-center-lab-claude",
                "MAP_System/templates/install/bin/ai-command-center-lab-pi",
                "MAP_System/templates/install/bin/ai-command-center-lab-librarian",
                "MAP_System/templates/install/wezterm/ai-command-center-lab.lua",
            )
        ).lower()
        for contradiction in (
            "sole core orchestrator",
            "codex is always the coordinator",
            "claude is always the reviewer",
            "pi may own tasks",
            "librarian may approve",
            "ack transfers authority",
            "prepare transfers authority",
        ):
            self.assertNotIn(contradiction, active_surfaces)


if __name__ == "__main__":
    unittest.main()
