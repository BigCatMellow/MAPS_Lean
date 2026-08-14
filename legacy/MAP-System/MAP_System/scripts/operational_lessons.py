#!/usr/bin/env python3
"""Validate and project promoted operational lessons into startup context."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "agents" / "operational-lessons.json"
VALID_STATUS = {"active", "retired", "superseded"}
REQUIRED = {
    "lesson_id", "title", "status", "scopes", "summary", "owner",
    "source_paths", "activated_at", "review_trigger", "review_after",
    "supersedes", "superseded_by",
}


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def load_store(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("lessons"), list):
        raise ValueError("store must have schema_version=1 and lessons list")
    return data


def validate(data: dict, repo: Path = ROOT.parent) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    active_titles: dict[str, str] = {}
    by_id = {x.get("lesson_id"): x for x in data["lessons"] if isinstance(x, dict)}
    for index, lesson in enumerate(data["lessons"]):
        where = lesson.get("lesson_id", f"index {index}") if isinstance(lesson, dict) else f"index {index}"
        if not isinstance(lesson, dict):
            errors.append(f"{where}: lesson must be an object")
            continue
        missing = sorted(REQUIRED - set(lesson))
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
            continue
        lid = lesson["lesson_id"]
        if lid in seen:
            errors.append(f"{lid}: duplicate id")
        seen.add(lid)
        if lesson["status"] not in VALID_STATUS:
            errors.append(f"{lid}: invalid status {lesson['status']}")
        if not lesson["scopes"] or not all(isinstance(x, str) and x for x in lesson["scopes"]):
            errors.append(f"{lid}: scopes must contain non-empty strings")
        if not lesson["source_paths"]:
            errors.append(f"{lid}: source_paths cannot be empty")
        for source in lesson["source_paths"]:
            if not (repo / source).exists():
                errors.append(f"{lid}: missing source {source}")
        for field in ("activated_at", "review_after"):
            try:
                parse_time(lesson[field])
            except (TypeError, ValueError) as exc:
                errors.append(f"{lid}: invalid {field}: {exc}")
        if lesson["status"] == "superseded" and not lesson["superseded_by"]:
            errors.append(f"{lid}: superseded lesson needs superseded_by")
        if lesson["superseded_by"] and lesson["superseded_by"] not in by_id:
            errors.append(f"{lid}: unknown superseded_by {lesson['superseded_by']}")
        if lesson["status"] == "active":
            key = lesson["title"].strip().casefold()
            if key in active_titles:
                errors.append(f"{lid}: active title conflicts with {active_titles[key]}")
            active_titles[key] = lid
    return errors


def relevant(lesson: dict, scopes: set[str]) -> bool:
    lesson_scopes = set(lesson["scopes"])
    return lesson["status"] == "active" and ("all" in lesson_scopes or not scopes or bool(scopes & lesson_scopes))


def orientation(data: dict, scopes: set[str], now: datetime) -> dict:
    lessons = []
    for lesson in data["lessons"]:
        if not relevant(lesson, scopes):
            continue
        review_after = parse_time(lesson["review_after"])
        lessons.append({
            "lesson_id": lesson["lesson_id"],
            "title": lesson["title"],
            "summary": lesson["summary"],
            "review_due": bool(review_after and review_after <= now),
            "review_trigger": lesson["review_trigger"],
            "source_paths": lesson["source_paths"],
        })
    return {"scopes": sorted(scopes), "active_lessons": lessons}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "orientation", "list"))
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--scope", action="append", default=[])
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = load_store(args.store)
        errors = validate(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}))
        return 1
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2 if args.pretty else None))
        return 1
    if args.command == "validate":
        result = {"ok": True, "lessons": len(data["lessons"])}
    elif args.command == "list":
        result = data
    else:
        result = orientation(data, set(args.scope), datetime.now(timezone.utc))
        result["ok"] = True
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
