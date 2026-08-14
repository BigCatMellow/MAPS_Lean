#!/usr/bin/env python3
"""Focused current-context metric tests for TASK-271."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MAP_System.scripts.agent_token_status import _claude_metrics  # noqa: E402


def _write(path: Path, events: list[dict]) -> None:
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")


def test_claude_latest_prompt_is_not_cumulative_transcript_total() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "claude.jsonl"
        _write(path, [
            {
                "uuid": "one",
                "timestamp": "2026-07-22T10:00:00Z",
                "message": {"model": "claude-test", "usage": {
                    "input_tokens": 10,
                    "cache_creation_input_tokens": 100,
                    "cache_read_input_tokens": 1000,
                    "output_tokens": 20,
                }},
            },
            {
                "uuid": "two",
                "timestamp": "2026-07-22T10:01:00Z",
                "message": {"model": "claude-test", "usage": {
                    "input_tokens": 5,
                    "cache_creation_input_tokens": 200,
                    "cache_read_input_tokens": 2000,
                    "output_tokens": 30,
                }},
            },
        ])
        metrics = _claude_metrics(path)

    assert metrics["latest_context_tokens"] == 2205
    assert metrics["peak_context_tokens"] == 2205
    assert metrics["total_tokens"] == 3365
    assert metrics["context_metric"] == "latest_prompt_input_estimate"


def test_claude_rate_limit_record_does_not_replace_last_good_context() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "claude.jsonl"
        _write(path, [
            {
                "uuid": "good",
                "timestamp": "2026-07-22T10:00:00Z",
                "message": {"usage": {
                    "input_tokens": 3,
                    "cache_creation_input_tokens": 7,
                    "cache_read_input_tokens": 90,
                    "output_tokens": 4,
                }},
            },
            {
                "uuid": "limited",
                "timestamp": "2026-07-22T10:01:00Z",
                "isApiErrorMessage": True,
                "error": "rate_limit",
                "message": {
                    "usage": {"input_tokens": 0},
                    "content": [{"text": "usage limit"}],
                },
            },
        ])
        metrics = _claude_metrics(path)

    assert metrics["latest_context_tokens"] == 100
    assert metrics["turns"] == 1
if __name__ == "__main__":
    test_claude_latest_prompt_is_not_cumulative_transcript_total()
    print("PASS Claude latest prompt differs from cumulative transcript total")
    test_claude_rate_limit_record_does_not_replace_last_good_context()
    print("PASS rate-limit record preserves last good context estimate")
