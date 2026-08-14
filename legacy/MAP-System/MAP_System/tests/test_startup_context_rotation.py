#!/usr/bin/env python3
"""Focused contract tests for TASK-272 startup continuity orientation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCHERS = (
    ROOT / "MAP_System/templates/install/bin/ai-command-center-lab-claude",
    ROOT / "MAP_System/templates/install/bin/ai-command-center-lab-codex",
)


def prompt_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index("PROMPT='") + len("PROMPT='")
    end = text.index("'\n\nexec ", start)
    return text[start:end]


def test_launcher_startup_context_contract(path: Path) -> None:
    prompt = prompt_text(path)
    validate = "context_rotation.py validate"
    advise = "context_rotation.py advise --agent <your-exact-current-hcom-identity>"
    route = "graph/runner.py"

    assert "exact current hcom identity" in prompt
    assert validate in prompt
    assert advise in prompt
    assert "continuity ledger" in prompt
    assert "advisory and read-only" in prompt
    assert "never use advise --notify" in prompt
    assert "exactly one hcom message" in prompt
    assert "continuity validity" in prompt
    assert "checkpoint/rotation recommendation" in prompt
    assert "resume plan" in prompt
    assert "request priorities in that same message" in prompt
    assert prompt.index(validate) < prompt.index(advise) < prompt.index(route)


def main() -> int:
    for launcher in LAUNCHERS:
        test_launcher_startup_context_contract(launcher)
        print(f"PASS {launcher.name}")
    print(f"PASS: {len(LAUNCHERS)}/{len(LAUNCHERS)} launcher startup contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
