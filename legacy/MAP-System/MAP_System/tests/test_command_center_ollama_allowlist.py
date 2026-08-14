"""Regression checks for the CommandCenterUI local-model allowlist gate (TASK-265/DEC-033).

The 2026-07-21 untracked edit to the live app/server.py dropped this gate
entirely -- every installed Ollama model became launchable through the UI,
not just a reviewed set (artifacts/audits/task254-untracked-edit-2026-07-21.md).
It went unnoticed for a week because nothing checked for it mechanically.
These tests exist so the next regression is caught here, not in a future
audit.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LIVE_SERVER = ROOT.parents[1] / "CommandCenterUI" / "app" / "server.py"
TEMPLATE_SERVER = ROOT / "MAP_System" / "templates" / "install" / "command-center-ui" / "app" / "server.py"


def _load_server_module(path: Path):
    os.environ.setdefault("COMMAND_CENTER_UI_WORKSPACE", str(ROOT))
    spec = importlib.util.spec_from_file_location(f"cc_server_{path.stat().st_mtime_ns}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OllamaAllowlistGateTests(unittest.TestCase):
    """Exercises the live server.py's actual code, not a copy of its logic."""

    @classmethod
    def setUpClass(cls):
        if not LIVE_SERVER.exists():
            raise unittest.SkipTest(f"live CommandCenterUI not present at {LIVE_SERVER}")
        cls.module = _load_server_module(LIVE_SERVER)

    def test_visible_ollama_models_is_qwen_only(self):
        self.assertEqual(list(self.module.VISIBLE_OLLAMA_MODELS.keys()), ["qwen3.5:4b"])

    def test_local_agent_defs_gates_by_allowlist(self):
        installed = [
            {"name": "qwen3.5:4b", "size": "4GB"},
            {"name": "deepseek-r1:8b", "size": "8GB"},
            {"name": "qwen3.5:9b", "size": "9GB"},
            {"name": "qwen2.5-coder:7b", "size": "7GB"},
            {"name": "nomic-embed-text", "size": "500MB"},
        ]
        original = self.module.ollama_models
        self.module.ollama_models = lambda: installed
        try:
            defs = self.module.local_agent_defs()
        finally:
            self.module.ollama_models = original
        exposed = {key for key in defs if key.startswith("ollama-model-")}
        self.assertEqual(exposed, {"ollama-model-qwen3-5-4b"})

    def test_local_agent_defs_exposes_nothing_when_only_allowlist_absent(self):
        """The gate must fail closed: if the one allowlisted model is not
        installed, no ollama-model- entries should appear -- not "expose
        whatever is installed instead"."""
        original = self.module.ollama_models
        self.module.ollama_models = lambda: [{"name": "deepseek-r1:8b", "size": "8GB"}]
        try:
            defs = self.module.local_agent_defs()
        finally:
            self.module.ollama_models = original
        exposed = {key for key in defs if key.startswith("ollama-model-")}
        self.assertEqual(exposed, set())

    def test_ollama_model_uses_is_not_used_as_a_gate(self):
        """OLLAMA_MODEL_USES is inert description text (DEC-033) -- it must
        not itself be capable of exposing a model VISIBLE_OLLAMA_MODELS
        excludes."""
        broader = set(self.module.OLLAMA_MODEL_USES.keys())
        allowlisted = set(self.module.VISIBLE_OLLAMA_MODELS.keys())
        self.assertFalse(
            broader - allowlisted <= allowlisted,
            "OLLAMA_MODEL_USES should list models beyond the allowlist for this test to be meaningful",
        )
        original = self.module.ollama_models
        self.module.ollama_models = lambda: [{"name": name, "size": ""} for name in broader]
        try:
            defs = self.module.local_agent_defs()
        finally:
            self.module.ollama_models = original
        exposed_models = {v["model"] for k, v in defs.items() if k.startswith("ollama-model-")}
        self.assertEqual(exposed_models, allowlisted & broader)


class TemplateLiveGateParityTests(unittest.TestCase):
    """The mechanical drift check TASK-265's acceptance criteria asks for:
    fails loudly if the security-relevant lines diverge between live and
    template, instead of relying on the next manual audit to notice."""

    def test_both_copies_define_visible_ollama_models_as_qwen_only(self):
        for label, path in (("live", LIVE_SERVER), ("template", TEMPLATE_SERVER)):
            if not path.exists():
                self.skipTest(f"{label} copy not present at {path}")
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                'VISIBLE_OLLAMA_MODELS = {\n    "qwen3.5:4b":',
                text,
                f"{label} copy's VISIBLE_OLLAMA_MODELS allowlist has drifted from qwen3.5:4b-only",
            )

    def test_both_copies_gate_local_agent_defs_on_the_allowlist(self):
        for label, path in (("live", LIVE_SERVER), ("template", TEMPLATE_SERVER)):
            if not path.exists():
                self.skipTest(f"{label} copy not present at {path}")
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                "description = VISIBLE_OLLAMA_MODELS.get(model_name)\n        if description is None:\n            continue",
                text,
                f"{label} copy's local_agent_defs() no longer gates on VISIBLE_OLLAMA_MODELS",
            )


if __name__ == "__main__":
    unittest.main()
