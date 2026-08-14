#!/usr/bin/env python3
"""Render the designated active-lane table from canonical SQLite state.

The set and ordering of lanes, plus human rationale and gate text, live in
``shared/active-lane-annotations.json``. Lifecycle fields always come from
``map.db``. Free prose in ``current-state.md`` is preserved and never parsed as
task state.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "map.db"
DEFAULT_ANNOTATIONS = ROOT / "shared" / "active-lane-annotations.json"
DEFAULT_STATE_FILE = ROOT / "shared" / "current-state.md"

BEGIN_MARKER = "<!-- BEGIN GENERATED ACTIVE LANES -->"
END_MARKER = "<!-- END GENERATED ACTIVE LANES -->"
STALE_STATUSES = {"DONE", "RELEASED", "RETIRED"}


class RenderError(RuntimeError):
    """The projection inputs are invalid or the generated region is missing."""


@dataclass(frozen=True)
class Diagnostic:
    kind: str
    task_id: str
    detail: str

    def format(self) -> str:
        return f"{self.kind} annotation {self.task_id}: {self.detail}"


def load_annotations(path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RenderError(f"cannot read annotation source {path}: {exc}") from exc

    if payload.get("schema_version") != 1:
        raise RenderError("annotation source must use schema_version 1")
    lanes = payload.get("lanes")
    if not isinstance(lanes, dict):
        raise RenderError("annotation source field 'lanes' must be an object keyed by task ID")

    normalized: dict[str, dict[str, Any]] = {}
    seen_orders: dict[int, str] = {}
    for task_id, annotation in lanes.items():
        if not isinstance(task_id, str) or not task_id.startswith("TASK-"):
            raise RenderError(f"invalid annotation task key: {task_id!r}")
        if not isinstance(annotation, dict):
            raise RenderError(f"annotation for {task_id} must be an object")
        order = annotation.get("order")
        if not isinstance(order, int) or order < 1:
            raise RenderError(f"annotation for {task_id} needs a positive integer order")
        if order in seen_orders:
            raise RenderError(
                f"duplicate annotation order {order}: {seen_orders[order]} and {task_id}"
            )
        seen_orders[order] = task_id
        for field in ("rationale", "gate"):
            value = annotation.get(field, "")
            if not isinstance(value, str):
                raise RenderError(f"annotation {task_id}.{field} must be a string")
        normalized[task_id] = annotation
    return normalized


def load_tasks(db_path: Path) -> dict[str, dict[str, Any]]:
    uri = f"file:{db_path}?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT task_id, status, owner, claimed_by
                FROM tasks
                ORDER BY task_id
                """
            ).fetchall()
    except sqlite3.Error as exc:
        raise RenderError(f"cannot read canonical database {db_path}: {exc}") from exc
    return {row["task_id"]: dict(row) for row in rows}


def markdown_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", r"\|")


def code_or_none(value: str | None, *, suffix: str = "") -> str:
    if not value:
        return "none"
    return f"`{markdown_cell(value)}`{suffix}"


def annotation_text(annotation: dict[str, Any]) -> str:
    parts = [
        markdown_cell(annotation.get("rationale", "")),
        markdown_cell(annotation.get("gate", "")),
    ]
    return " ".join(part for part in parts if part) or "No annotation recorded."


NON_FRESH_STATES = {"STALE", "UNAVAILABLE", "INVALID"}


def authority_line(authority: dict[str, Any] | None) -> str | None:
    """One line naming authority host, revision, and freshness (TASK-310).

    Returns None when no authority object was supplied, so every existing
    caller/test that doesn't pass one renders exactly as before. `main()` is
    the only caller that supplies a real one, computed once per render so a
    live, ticking `freshness_age_seconds` never leaks into the generated
    block (that would make every render "changed", defeating `--check`).
    """
    if authority is None:
        return None
    freshness = authority.get("freshness", "UNAVAILABLE")
    mode = authority.get("mode", "unknown")
    host = authority.get("authority_host") or "self"
    revision = authority.get("authority_revision") or "none"
    last_sync = authority.get("last_successful_sync_at") or "never"
    if freshness in NON_FRESH_STATES:
        return (
            f"**Authority freshness: `{freshness}`** — do not treat this table as "
            f"current or globally healthy. mode=`{mode}` host=`{host}` "
            f"revision=`{revision}` last_sync=`{last_sync}` "
            f"error=`{markdown_cell(str(authority.get('last_error') or 'none'))}`"
        )
    return (
        f"Authority freshness: `{freshness}` — mode=`{mode}` host=`{host}` "
        f"revision=`{revision}` last_sync=`{last_sync}`"
    )


def build_projection(
    tasks: dict[str, dict[str, Any]],
    annotations: dict[str, dict[str, Any]],
    authority: dict[str, Any] | None = None,
) -> tuple[str, list[Diagnostic]]:
    rows: list[str] = []
    diagnostics: list[Diagnostic] = []

    ordered = sorted(
        annotations.items(),
        key=lambda item: (item[1]["order"], item[0]),
    )
    rendered_order = 0
    for task_id, annotation in ordered:
        task = tasks.get(task_id)
        if task is None:
            diagnostics.append(Diagnostic("ORPHAN", task_id, "task is absent from map.db"))
            continue
        if task["status"] in STALE_STATUSES:
            diagnostics.append(
                Diagnostic("STALE", task_id, f"canonical status is {task['status']}")
            )
            continue

        rendered_order += 1
        rows.append(
            "| "
            + " | ".join(
                [
                    str(rendered_order),
                    task_id,
                    task["status"],
                    code_or_none(task["owner"]),
                    code_or_none(task["claimed_by"], suffix=" recorded"),
                    annotation_text(annotation),
                ]
            )
            + " |"
        )

    if diagnostics:
        diagnostic_lines = "\n".join(f"- `{item.format()}`" for item in diagnostics)
    else:
        diagnostic_lines = "- none"

    if not rows:
        rows.append(
            "| — | — | — | — | — | No active annotated lanes; see diagnostics below. |"
        )

    line = authority_line(authority)
    header_lines = [
        BEGIN_MARKER,
        "## Active Execution Lanes — generated",
        "",
        "Lifecycle fields below are generated from read-only `map.db`. Lane selection,",
        "ordering, rationale, and gate text come from",
        "`shared/active-lane-annotations.json`; the renderer never parses surrounding",
        "prose as lifecycle truth.",
        "",
    ]
    if line is not None:
        header_lines.extend([line, ""])
    block = "\n".join(
        [
            *header_lines,
            "| Order | Task | State | Durable owner | `claimed_by` / current worker | Why now / gate |",
            "|---|---|---|---|---|---|",
            *rows,
            "",
            "Projection diagnostics:",
            "",
            diagnostic_lines,
            END_MARKER,
        ]
    )
    return block, diagnostics


def replace_generated_block(source: str, block: str) -> str:
    if source.count(BEGIN_MARKER) != 1 or source.count(END_MARKER) != 1:
        raise RenderError(
            "state file must contain exactly one generated active-lane marker pair"
        )
    start = source.index(BEGIN_MARKER)
    end = source.index(END_MARKER, start) + len(END_MARKER)
    return source[:start] + block + source[end:]


def render_text(
    state_text: str,
    db_path: Path,
    annotations_path: Path,
    authority: dict[str, Any] | None = None,
) -> tuple[str, list[Diagnostic]]:
    annotations = load_annotations(annotations_path)
    tasks = load_tasks(db_path)
    block, diagnostics = build_projection(tasks, annotations, authority)
    return replace_generated_block(state_text, block), diagnostics


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def render_file(
    state_path: Path,
    db_path: Path,
    annotations_path: Path,
    *,
    check: bool = False,
    authority: dict[str, Any] | None = None,
) -> tuple[bool, list[Diagnostic]]:
    try:
        source = state_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RenderError(f"cannot read state file {state_path}: {exc}") from exc
    rendered, diagnostics = render_text(source, db_path, annotations_path, authority)
    changed = rendered != source
    if changed and not check:
        atomic_write(state_path, rendered)
    return changed, diagnostics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report whether regeneration is needed without writing",
    )
    args = parser.parse_args(argv)

    try:
        if str(ROOT.parent) not in sys.path:
            sys.path.insert(0, str(ROOT.parent))
        from MAP_System.scripts.map_authority import authority_status, load_authority_config

        authority = authority_status(load_authority_config())
    except Exception as exc:  # noqa: BLE001 -- never let this block the render itself
        # Per the freshness contract, "cannot parse this contract" is itself a
        # fail-closed state (UNAVAILABLE/INVALID), never a silently omitted line.
        authority = {"freshness": "UNAVAILABLE", "last_error": str(exc)[:200]}

    try:
        changed, diagnostics = render_file(
            args.state_file,
            args.db,
            args.annotations,
            check=args.check,
            authority=authority,
        )
    except RenderError as exc:
        print(f"ERROR {exc}")
        return 2

    for diagnostic in diagnostics:
        print(diagnostic.format())
    if args.check and changed:
        print(f"DRIFT {args.state_file} needs active-lane regeneration")
        return 1
    print(f"OK {args.state_file}: {'updated' if changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
