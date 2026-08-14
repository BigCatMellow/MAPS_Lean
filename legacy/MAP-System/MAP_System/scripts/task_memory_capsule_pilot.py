#!/usr/bin/env python3
"""Development-only retrieval-capsule parser and evidence-selection pilot.

The pilot augments TASK-261's frozen query-global selector with a small,
validated Markdown metadata block.  It never changes task authority, the
frozen retriever, or the frozen selector, and it treats documents without a
capsule as ordinary fallback sources.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts import task_fingerprint_pilot as base  # noqa: E402
from MAP_System.scripts import task_memory_fts as memory  # noqa: E402
from MAP_System.scripts import task_memory_packet_selector as frozen  # noqa: E402


DEFAULT_SPEC = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-fts5-rrf-holdout-queries-2026-07-19.json"
)
DEFAULT_TASK261 = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-evidence-verifier-development-2026-07-19.json"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "experiments" /
    "task-memory-capsule-development-2026-07-19.json"
)

HEADING = "## Retrieval capsule"
REQUIRED_FIELDS = (
    "Purpose",
    "Proves",
    "Applies to",
    "Does not provide",
    "Evidence type",
    "Status",
)
EVIDENCE_TYPES = {
    "governing_rule",
    "procedure",
    "decision",
    "implementation",
    "test_evidence",
    "measured_outcome",
    "research",
    "current_state",
    "release_record",
    "task_scope",
}
STATUS_VALUES = {"current", "historical", "draft", "superseded"}
TYPE_TO_ROLE = {
    "governing_rule": "guide",
    "procedure": "guide",
    "decision": "decision",
    "implementation": "implementation",
    "test_evidence": "test",
    "measured_outcome": "outcome",
    "research": "research",
    "current_state": "current_state",
    "release_record": "release",
    "task_scope": "task_scope",
}
STATUS_BONUS = {
    "current": 2.0,
    "historical": -1.0,
    "draft": -3.0,
    "superseded": -12.0,
}
WORD_RE = re.compile(r"\b[\w][\w'-]*\b", re.UNICODE)
FIELD_RE = re.compile(r"^- ([A-Za-z ]+):\s*(.*?)\s*$")

PILOT_DOCUMENTS = (
    "MAP_System/AGENTS.md",
    "MAP_System/notes/practice-scenario-runbook.md",
    "MAP_System/artifacts/tests/rns-persistent-supervisor.md",
    "MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md",
    "Projects/ClearFront/artifacts/tests/task-214-combat-parity.md",
    "MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md",
)

PRE_CAPSULE_HASHES = {
    "MAP_System/AGENTS.md":
        "2ae3f82bd279e9f103924e9e9f64367463fe8284ae7619744597b3c3f9e4da4c",
    "MAP_System/notes/practice-scenario-runbook.md":
        "d16d97c75c7d94143e385632ba1feb2ce1c2d6b54f3ceb2195821c5f8fcca139",
    "MAP_System/artifacts/tests/rns-persistent-supervisor.md":
        "471b440bb9aee50517b9c8b0eb95c738fce4ac6fc6790ca40999ee810bf2ccc5",
    "MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md":
        "7a356737f43b6e98856cfcc7af27648d4faa9b28ad438936cfd5f40beffb342c",
    "Projects/ClearFront/artifacts/tests/task-214-combat-parity.md":
        "12a9dff284b067a4b20cbe082540c705013fe87d1e63d366046965b2eb57491f",
    "MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md":
        "147a3e9260d81301c4828e3c27d08ba740eb975e105266ae2236b0b4f2d8e614",
}

FROZEN_TASK261_HASHES = {
    "MAP_System/scripts/task_memory_packet_selector.py":
        "1c33ed6c84189168e1cb1abc793495f3beeaebac872bb57d8d1a5d2f4e68b8f6",
    "MAP_System/tests/test_task_memory_packet_selector.py":
        "cbadf1c6a6dcb2e108fc769d2a0556d0368b22f05a26a5828a5ba907b1544d86",
    "MAP_System/artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.json":
        "537a2128fcc63116e62440cc59553f5f6af633674f89f6fab313ec0480bec725",
    "MAP_System/artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.md":
        "414d419948f67a17c511fdd1b7b0d197aab2f6f387f6d360bafb171461d36693",
}


@dataclass(frozen=True)
class Capsule:
    fields: dict[str, str]
    heading_line: int
    word_count: int

    @property
    def evidence_type(self) -> str:
        return self.fields["Evidence type"]

    @property
    def status(self) -> str:
        return self.fields["Status"]


def parse_capsule_text(text: str) -> tuple[Capsule | None, list[str]]:
    """Parse one strict capsule; absence is a valid fallback."""
    lines = text.splitlines()
    headings = []
    in_fence = False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.strip() == HEADING:
            headings.append(index)
    if not headings:
        return None, []
    if len(headings) > 1:
        return None, ["duplicate Retrieval capsule headings"]

    heading_index = headings[0]
    errors: list[str] = []
    if heading_index + 1 > 40:
        errors.append("Retrieval capsule must begin within the first 40 lines")

    parsed: list[tuple[str, str]] = []
    seen: set[str] = set()
    active_field: int | None = None
    for line in lines[heading_index + 1:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped:
            continue
        match = FIELD_RE.match(stripped)
        if match:
            name, value = match.groups()
            if name in seen:
                errors.append(f"duplicate field: {name}")
            seen.add(name)
            parsed.append((name, value.strip()))
            active_field = len(parsed) - 1
            continue
        if line.startswith(("  ", "\t")) and active_field is not None:
            name, value = parsed[active_field]
            parsed[active_field] = (name, f"{value} {stripped}".strip())
            continue
        if set(REQUIRED_FIELDS).issubset(seen):
            break
        errors.append(f"unexpected capsule content: {stripped[:60]}")

    names = [name for name, _value in parsed]
    unknown = [name for name in names if name not in REQUIRED_FIELDS]
    missing = [name for name in REQUIRED_FIELDS if name not in seen]
    if unknown:
        errors.append("unknown field(s): " + ", ".join(unknown))
    if missing:
        errors.append("missing field(s): " + ", ".join(missing))
    if not unknown and not missing and names != list(REQUIRED_FIELDS):
        errors.append("capsule fields are out of order")

    fields = dict(parsed)
    for name in REQUIRED_FIELDS:
        if name in fields and not fields[name]:
            errors.append(f"empty field: {name}")
    if fields.get("Evidence type") and fields["Evidence type"] not in EVIDENCE_TYPES:
        errors.append(f"invalid evidence type: {fields['Evidence type']}")
    if fields.get("Status") and fields["Status"] not in STATUS_VALUES:
        errors.append(f"invalid status: {fields['Status']}")
    boundary_words = WORD_RE.findall(fields.get("Does not provide", ""))
    if fields.get("Does not provide") and len(boundary_words) < 4:
        errors.append("Does not provide must state a meaningful boundary")

    word_count = sum(len(WORD_RE.findall(value)) for value in fields.values())
    if parsed and not 60 <= word_count <= 120:
        errors.append(f"capsule word count {word_count} is outside 60-120")
    if errors:
        return None, errors
    return Capsule(fields=fields, heading_line=heading_index + 1, word_count=word_count), []


def parse_capsule_path(path: Path) -> tuple[Capsule | None, list[str]]:
    if not path.is_file() or path.suffix.lower() not in {".md", ".markdown"}:
        return None, []
    try:
        return parse_capsule_text(path.read_text(encoding="utf-8", errors="replace"))
    except OSError as exc:
        return None, [f"could not read capsule source: {exc}"]


def capsule_tokens(capsule: Capsule, fields: Iterable[str]) -> set[str]:
    return set(base.words(" ".join(capsule.fields[name] for name in fields)))


def augment_candidates(
    candidates: Iterable[dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:
    """Add separate capsule signals while preserving fallback candidates."""
    query_tokens = set(base.words(query))
    role_demand = frozen.requested_roles(query)
    augmented = []
    for raw in candidates:
        item = dict(raw)
        source_path = memory.resolve_path(item["path"])
        capsule, errors = parse_capsule_path(source_path)
        item["capsule"] = None
        item["capsule_errors"] = errors
        item["capsule_provenance"] = "fallback"
        if capsule:
            positive = capsule_tokens(capsule, ("Purpose", "Proves", "Applies to"))
            boundary = capsule_tokens(capsule, ("Does not provide",))
            positive_overlap = query_tokens.intersection(positive)
            boundary_overlap = query_tokens.intersection(boundary)
            mapped_role = TYPE_TO_ROLE[capsule.evidence_type]
            mapped_role_fit = role_demand.get(mapped_role, 0.0)
            adjustment = (
                len(positive_overlap) * 3.25
                + mapped_role_fit * 8.0
                - len(boundary_overlap) * 4.0
                + STATUS_BONUS[capsule.status]
            )
            item["base_score"] = round(float(item.get("base_score", 0.0)) + adjustment, 6)
            item["role_fit"] = round(max(float(item.get("role_fit", 0.0)), mapped_role_fit), 4)
            item["capsule"] = {
                "fields": capsule.fields,
                "heading_line": capsule.heading_line,
                "word_count": capsule.word_count,
                "mapped_role": mapped_role,
                "matched_positive_terms": sorted(positive_overlap),
                "matched_boundary_terms": sorted(boundary_overlap),
                "score_adjustment": round(adjustment, 6),
            }
            item["capsule_provenance"] = "validated_capsule"
        augmented.append(item)
    return augmented


def select_evidence(
    conn: sqlite3.Connection,
    query: str,
    task_ids: Iterable[str],
    *,
    limit: int = frozen.SOURCE_LIMIT,
) -> dict[str, Any]:
    started = time.perf_counter()
    task_ids = list(dict.fromkeys(task_ids))
    fallback_candidates = frozen.evidence_candidates(conn, query, task_ids)
    candidates = augment_candidates(fallback_candidates, query)
    sources = frozen.allocate_evidence(candidates, limit=limit)
    return {
        "query": query,
        "selected_task_ids": task_ids,
        "budget": limit,
        "sources": sources,
        "capsule_candidate_count": sum(
            item["capsule_provenance"] == "validated_capsule" for item in candidates
        ),
        "fallback_candidate_count": sum(
            item["capsule_provenance"] == "fallback" for item in candidates
        ),
        "selection_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def evaluate(
    conn: sqlite3.Connection,
    spec: dict[str, Any],
    recorded_task261: dict[str, Any],
) -> dict[str, Any]:
    recorded_hits = recorded_task261["metrics"]["query_global_hits"]
    fallback_hits = capsule_hits = total = 0
    selected_capsules = 0
    per_query = []
    times = []
    for query in spec["queries"]:
        task_ids = query.get("expected_task_ids", [])
        if not task_ids:
            continue
        fallback = frozen.select_evidence(conn, query["question"], task_ids)
        capsule = select_evidence(conn, query["question"], task_ids)
        expected = [memory.normalize_path(path) for path in query["expected_source_paths"]]
        fallback_paths = {source["path"] for source in fallback["sources"]}
        capsule_paths = {source["path"] for source in capsule["sources"]}
        fallback_found = [path for path in expected if path in fallback_paths]
        capsule_found = [path for path in expected if path in capsule_paths]
        fallback_hits += len(fallback_found)
        capsule_hits += len(capsule_found)
        total += len(expected)
        selected_capsules += sum(
            source["capsule_provenance"] == "validated_capsule"
            for source in capsule["sources"]
        )
        times.append(capsule["selection_ms"])
        per_query.append({
            "id": query["id"],
            "expected_sources": expected,
            "recorded_task261_hits": next(
                len(item["query_global_visible_expected_sources"])
                for item in recorded_task261["metrics"]["per_query"]
                if item["id"] == query["id"]
            ),
            "current_fallback_hits": len(fallback_found),
            "capsule_hits": len(capsule_found),
            "capsule_visible_expected_sources": capsule_found,
            "capsule_hidden_expected_sources": [path for path in expected if path not in capsule_paths],
            "capsule_selected_sources": [
                {
                    "path": source["path"],
                    "provenance": source["capsule_provenance"],
                    "evidence_type": (
                        source["capsule"]["fields"]["Evidence type"]
                        if source.get("capsule") else None
                    ),
                }
                for source in capsule["sources"]
            ],
            "selection_ms": capsule["selection_ms"],
        })
    sorted_times = sorted(times)
    return {
        "evaluation_mode": "known TASK-260/TASK-261 task-conditioned development",
        "recorded_task261_hits": recorded_hits,
        "recorded_task261_visibility": round(recorded_hits / total, 4),
        "current_fallback_hits_after_document_edits": fallback_hits,
        "current_fallback_visibility_after_document_edits": round(fallback_hits / total, 4),
        "capsule_hits": capsule_hits,
        "capsule_visibility": round(capsule_hits / total, 4),
        "expected_sources": total,
        "selected_capsule_sources": selected_capsules,
        "selected_sources": len(per_query) * frozen.SOURCE_LIMIT,
        "median_selection_ms": sorted_times[len(sorted_times) // 2] if sorted_times else 0.0,
        "per_query": per_query,
    }


def validate_pilot_documents(repo: Path = REPO) -> dict[str, Any]:
    results = []
    for display in PILOT_DOCUMENTS:
        path = repo / display
        capsule, errors = parse_capsule_path(path)
        results.append({
            "path": display,
            "pre_capsule_sha256": PRE_CAPSULE_HASHES[display],
            "valid": capsule is not None and not errors,
            "errors": errors,
            "word_count": capsule.word_count if capsule else None,
            "evidence_type": capsule.evidence_type if capsule else None,
            "status": capsule.status if capsule else None,
            "sha256": base.sha256(path) if path.is_file() else None,
        })
    return {
        "documents": results,
        "valid": all(item["valid"] for item in results),
    }


def frozen_hashes() -> dict[str, Any]:
    result = {}
    for display, expected in FROZEN_TASK261_HASHES.items():
        path = REPO / display
        actual = base.sha256(path)
        result[display] = {
            "expected": expected,
            "actual": actual,
            "unchanged": actual == expected,
        }
    return result


def generate(spec_path: Path, task261_path: Path, output: Path) -> dict[str, Any]:
    documents = validate_pilot_documents()
    if not documents["valid"]:
        failures = [
            f"{item['path']}: {', '.join(item['errors']) or 'capsule missing'}"
            for item in documents["documents"] if not item["valid"]
        ]
        raise SystemExit("invalid pilot capsules:\n- " + "\n- ".join(failures))
    frozen_state = frozen_hashes()
    if not all(item["unchanged"] for item in frozen_state.values()):
        raise SystemExit("TASK-261 frozen input changed; refusing capsule evaluation")

    spec = base.load_json(spec_path)
    task261 = base.load_json(task261_path)
    with tempfile.TemporaryDirectory(prefix="map-task262-") as temp_dir:
        db_path = Path(temp_dir) / "capsules.db"
        build = memory.build_database(db_path, spec["corpus_task_ids"])
        with sqlite3.connect(db_path) as conn:
            metrics = evaluate(conn, spec, task261)
    payload = {
        "experiment": "TASK-262",
        "authority": "none; descriptive metadata and development projection only",
        "capsule_contract": {
            "required_fields": list(REQUIRED_FIELDS),
            "evidence_types": sorted(EVIDENCE_TYPES),
            "status_values": sorted(STATUS_VALUES),
            "word_range": [60, 120],
            "source_budget": frozen.SOURCE_LIMIT,
        },
        "pilot_documents": documents,
        "authoring_cost": {
            "documents": len(documents["documents"]),
            "capsule_words_total": sum(
                item["word_count"] or 0 for item in documents["documents"]
            ),
            "capsule_words_median": sorted(
                item["word_count"] or 0 for item in documents["documents"]
            )[len(documents["documents"]) // 2],
            "body_rewrite": "none; additive capsule blocks only",
        },
        "frozen_task261_hashes": frozen_state,
        "build": build,
        "metrics": metrics,
    }
    base.write_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--task261", type=Path, default=DEFAULT_TASK261)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = generate(args.spec, args.task261, args.output)
    print(json.dumps({
        "recorded_task261": payload["metrics"]["recorded_task261_visibility"],
        "current_fallback": payload["metrics"]["current_fallback_visibility_after_document_edits"],
        "capsule": payload["metrics"]["capsule_visibility"],
        "valid_capsules": sum(
            item["valid"] for item in payload["pilot_documents"]["documents"]
        ),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
