#!/usr/bin/env python3
"""Read-only local assistant capability health check."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any


LOCAL_OLLAMA_HOST = "127.0.0.1:11434"

# Installed is not the same as approved. qwen3.5:4b has a recorded bounded
# MAP Steward JSON-advisory drill; it remains draft-only and core-reviewed.
APPROVED_DRAFT_MODELS = ("qwen3.5:4b",)
REQUIRED_MODELS = APPROVED_DRAFT_MODELS
MODEL_LANES = {
    "qwen3.5:4b": {
        "authority": "draft-only",
        "evidence": "MAP Steward bounded JSON advisory drill",
        "lane": "visible_bounded_advisory",
    },
}


@dataclass(frozen=True)
class CommandResult:
    found: bool
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


def run_command(argv: list[str], *, timeout: float = 5.0) -> CommandResult:
    executable = shutil.which(argv[0])
    if not executable:
        return CommandResult(found=False, error=f"{argv[0]} not found")
    try:
        env = os.environ.copy()
        if argv[0] == "ollama":
            env["OLLAMA_HOST"] = LOCAL_OLLAMA_HOST
        result = subprocess.run(
            [executable, *argv[1:]],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            found=True,
            returncode=None,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            error=f"{argv[0]} timed out after {timeout:g}s",
        )
    return CommandResult(
        found=True,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def parse_ollama_models(text: str) -> list[str]:
    models: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("name "):
            continue
        models.append(stripped.split()[0])
    return models


def check_ollama(timeout: float) -> dict[str, Any]:
    result = run_command(["ollama", "list"], timeout=timeout)
    models = parse_ollama_models(result.stdout) if result.found and result.returncode == 0 else []
    installed = set(models)
    return {
        "tool": "ollama",
        "type": "model-runtime",
        "found": result.found,
        "reachable": result.found and result.returncode == 0,
        "returncode": result.returncode,
        "error": result.error,
        "host": LOCAL_OLLAMA_HOST,
        "installed_models": models,
        "models": [
            {
                "name": model,
                "required": True,
                "available": model in installed,
                **MODEL_LANES[model],
            }
            for model in APPROVED_DRAFT_MODELS
        ],
    }


def check_aider(timeout: float) -> dict[str, Any]:
    result = run_command(["aider", "--version"], timeout=timeout)
    version = result.stdout.strip() or result.stderr.strip()
    return {
        "tool": "aider",
        "type": "edit-workbench",
        "found": result.found,
        "reachable": result.found and result.returncode == 0,
        "returncode": result.returncode,
        "version": version if result.returncode == 0 else "",
        "error": result.error,
        "authority": "edit-helper",
    }


def build_report(timeout: float) -> dict[str, Any]:
    ollama = check_ollama(timeout)
    aider = check_aider(timeout)
    missing_models = [
        model["name"]
        for model in ollama["models"]
        if not model["available"]
    ]
    approved_available = [
        model["name"]
        for model in ollama["models"]
        if model["available"]
    ]
    return {
        "status": "ok" if ollama["reachable"] and not missing_models else "attention",
        "policy": {
            "runtime_status": "helper-capability-only",
            "core_agent_status": "not-registered",
            "final_authority": "core-agents-and-command-center",
            "starts_sessions": False,
        },
        "ollama": ollama,
        "aider": aider,
        "missing_models": missing_models,
        "required_models": list(APPROVED_DRAFT_MODELS),
        "approved_draft_models": approved_available,
        "advisory_lane": {
            "status": "available" if approved_available else "unavailable",
            "models": approved_available,
            "visibility": "operator-visible terminal only",
            "authority": "draft-only under named core review",
        },
    }


def print_text(report: dict[str, Any]) -> None:
    print("Local Assistant Health")
    print(f"status: {report['status']}")
    print(f"runtime_status: {report['policy']['runtime_status']}")
    print(f"core_agent_status: {report['policy']['core_agent_status']}")
    print(f"starts_sessions: {str(report['policy']['starts_sessions']).lower()}")
    print("")
    ollama = report["ollama"]
    print(f"ollama: {'reachable' if ollama['reachable'] else 'unavailable'} ({ollama['host']})")
    if ollama.get("error"):
        print(f"  error: {ollama['error']}")
    for model in ollama["models"]:
        state = "available" if model["available"] else "missing"
        print(f"  {model['name']}: {state} ({model['lane']}; {model['authority']})")
    advisory = report["advisory_lane"]
    print(f"advisory lane: {advisory['status']} ({', '.join(advisory['models']) or 'none'})")
    print("")
    aider = report["aider"]
    print(f"aider: {'available' if aider['found'] else 'missing'}")
    if aider.get("version"):
        print(f"  version: {aider['version']}")
    if aider.get("error"):
        print(f"  error: {aider['error']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.timeout)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
