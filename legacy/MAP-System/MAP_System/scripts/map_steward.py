#!/usr/bin/env python3
"""Read-only local MAP Steward attention packet and optional Ollama summary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO))

from MAP_System.scripts.operational_lessons import load_store, orientation, validate

GRAPH = ROOT / "workflow" / "task_graph.json"
AGENTS = ROOT / "agents" / "status.json"
LESSONS = ROOT / "agents" / "operational-lessons.json"
SENTINEL = ROOT / "agents" / "emergence-sentinel-state.json"
QUEUE = ROOT / "emergence" / "candidates"
STATE = ROOT / "agents" / "map-steward-state.json"
MODEL = "qwen3.5:4b"


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def collect() -> dict:
    graph = read_json(GRAPH, {"tasks": []})
    tasks = graph.get("tasks", [])
    actionable = [
        {k: task.get(k) for k in ("task_id", "title", "status", "owner")}
        for task in tasks if task.get("status") in {"READY", "IN_PROGRESS", "SUBMITTED", "CHANGES_REQUESTED", "BLOCKED"}
    ]
    agents = read_json(AGENTS, {"agents": {}}).get("agents", {})
    unavailable = [
        {"name": name, "status": item.get("status"), "reason": item.get("reason"), "resume_after": item.get("resume_after")}
        for name, item in agents.items() if item.get("status") not in {"available"}
    ]
    lesson_data = load_store(LESSONS)
    lesson_errors = validate(lesson_data)
    lesson_packet = orientation(lesson_data, {"startup", "helper-routing", "review-routing"}, datetime.now(timezone.utc))
    candidates = []
    for path in sorted(QUEUE.glob("CAND-*.json")):
        item = read_json(path, {})
        if item.get("status") == "new":
            candidates.append({k: item.get(k) for k in ("candidate_id", "signal_type", "subject", "summary", "detected_at")})
    return {
        "generated_at": stamp(),
        "actionable_tasks": actionable,
        "unavailable_agents": unavailable,
        "active_lessons": lesson_packet["active_lessons"],
        "lesson_errors": lesson_errors,
        "emergence_sentinel": read_json(SENTINEL, {}),
        "new_ei_candidates": candidates,
    }


def deterministic_recommendations(packet: dict) -> list[dict]:
    recommendations = []
    changed = [x for x in packet["actionable_tasks"] if x["status"] == "CHANGES_REQUESTED"]
    submitted = [x for x in packet["actionable_tasks"] if x["status"] == "SUBMITTED"]
    if changed:
        recommendations.append({"priority": "high", "kind": "rework", "text": f"{len(changed)} task(s) need rework.", "refs": [x["task_id"] for x in changed]})
    if submitted:
        recommendations.append({"priority": "normal", "kind": "review", "text": f"{len(submitted)} submitted task(s) need independent review.", "refs": [x["task_id"] for x in submitted]})
    if packet["lesson_errors"]:
        recommendations.append({"priority": "high", "kind": "memory", "text": "Operational lesson validation failed.", "refs": packet["lesson_errors"]})
    due = [x for x in packet["active_lessons"] if x["review_due"]]
    if due:
        recommendations.append({"priority": "normal", "kind": "memory", "text": f"{len(due)} operational lesson(s) are due for review.", "refs": [x["lesson_id"] for x in due]})
    if packet["new_ei_candidates"]:
        recommendations.append({"priority": "normal", "kind": "emergence", "text": f"{len(packet['new_ei_candidates'])} E/I candidate(s) await visible curation.", "refs": [x["candidate_id"] for x in packet["new_ei_candidates"]]})
    if not recommendations:
        recommendations.append({"priority": "low", "kind": "status", "text": "No immediate steward action detected.", "refs": []})
    return recommendations


def model_prompt(packet: dict, deterministic: list[dict]) -> str:
    bounded = {"packet": packet, "deterministic_recommendations": deterministic}
    return (
        "You are the local MAP Steward. Analyze only this bounded JSON packet. "
        "Return JSON object with key recommendations, an array of at most 5 objects "
        "with priority, kind, text, refs. Do not invent facts, issue commands, approve, "
        "promote, message, or claim work. Keep recommendations advisory.\n" +
        json.dumps(bounded, separators=(",", ":"))
    )


def parse_model_output(text: str) -> list[dict]:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("model output has no JSON object")
    data = json.loads(text[start:end + 1])
    recs = data.get("recommendations")
    if not isinstance(recs, list) or len(recs) > 5:
        raise ValueError("model recommendations must be an array of at most 5")
    clean = []
    for item in recs:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) for k in ("priority", "kind", "text")):
            raise ValueError("malformed recommendation")
        refs = item.get("refs", [])
        if not isinstance(refs, list) or not all(isinstance(x, str) for x in refs):
            raise ValueError("recommendation refs must be strings")
        clean.append({"priority": item["priority"], "kind": item["kind"], "text": item["text"], "refs": refs})
    return clean


def ask_ollama(prompt: str, timeout: float, runner=None) -> list[dict]:
    if runner is not None:
        proc = runner(
            ["ollama", "run", MODEL, "--format", "json", "--think", "false"],
            input=prompt, text=True, capture_output=True, timeout=timeout, check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "ollama failed").strip()[:300])
        return parse_model_output(proc.stdout)
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "think": False, "format": "json",
    }).encode("utf-8")
    request = Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        envelope = json.loads(response.read().decode("utf-8"))
    return parse_model_output(envelope.get("response", ""))


def write_state(state: dict, path: Path = STATE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def run(use_model: bool, timeout: float, state_path: Path = STATE, model_runner=None, resume: bool = False) -> dict:
    current = read_json(state_path, {})
    if current.get("stop_requested") and not resume:
        current.update({"status": "stopped"})
        write_state(current, state_path)
        return current
    packet = collect()
    base = deterministic_recommendations(packet)
    state = {"schema_version": 1, "status": "working", "last_run": packet["generated_at"], "mode": "model" if use_model else "deterministic", "model": MODEL if use_model else None, "last_error": None, "inputs": {k: len(v) if isinstance(v, list) else v for k, v in packet.items() if k != "generated_at"}, "recommendations": base, "stop_requested": False}
    write_state(state, state_path)
    if use_model:
        try:
            state["recommendations"] = ask_ollama(model_prompt(packet, base), timeout, model_runner)
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
            state["mode"] = "deterministic-fallback"
            state["last_error"] = str(exc)
    state["status"] = "idle"
    write_state(state, state_path)
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="store_true", help="Use local Ollama; run this only in an operator-visible terminal")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Explicitly clear a prior Stop and run")
    args = parser.parse_args(argv)
    result = run(args.model, args.timeout, args.state, resume=args.resume)
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
