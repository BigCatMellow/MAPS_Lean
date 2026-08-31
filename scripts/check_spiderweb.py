from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date
import json
from pathlib import Path
import re
from typing import Iterable
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_PREFIXES = (
    "legacy/",
    "migration/legacy-runtime-source/",
    "migration/legacy-knowledge-source/",
    "archive/",
    "work/context/",
)
IGNORED_DIRS = {
    ".git",
    ".venv",
    ".maps",
    ".hcom",
    "__pycache__",
    "node_modules",
}
ROOT_ANCHORS = {
    "AGENTS.md",
    "README.md",
    "docs/FIRST_RUN.md",
    "playbook/INDEX.md",
    "state/CURRENT.md",
    "work/coordination/README.md",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
ID_FIELD_RE = re.compile(
    r"(?im)^\s*[-*]\s*ID\s*:\s*`?([A-Z][A-Z0-9_]*-[A-Za-z0-9_.-]+)`?\s*$"
)
HEADING_ID_RE = re.compile(
    r"(?im)^#\s+((?:TASK|DEC|IDEA|INSIGHT|SYN|EXP|AGI|REPAIR|RISK)-[A-Za-z0-9_.-]+)(?:\b|:)"
)
PENDING_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?(?:result|status)\s*:\s*`?pending`?\s*$")
DATED_END_RE = re.compile(
    r"(?im)(?:\bend(?:s|_date)?\b|\bthrough\b|\buntil\b)[^\n]{0,48}?"
    r"(\d{4}-\d{2}-\d{2})"
)
SUPERSEDED_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:status|disposition)\s*:\s*`?SUPERSEDED`?\s*$"
)
NOT_PROMOTED_RE = re.compile(r"(?im)^\s*Not promoted\.\s*$")
CURRENT_DISPOSITION_RE = re.compile(
    r"(?im)^##\s+(?:Current disposition|Reconciliation|Disposition)\s*$"
)


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    detail: str
    severity: str = "ADVISORY"
    target: str | None = None


@dataclass
class Artifact:
    path: str
    text: str
    declared_ids: tuple[str, ...]
    outgoing_active: set[str]
    outgoing_historical: set[str]
    incoming_active: set[str]


@dataclass(frozen=True)
class ScanResult:
    root: str
    as_of: str
    include_historical: bool
    files_scanned: int
    active_edges: int
    historical_edges: int
    findings: tuple[Finding, ...]
    artifacts: tuple[dict[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "as_of": self.as_of,
            "include_historical": self.include_historical,
            "files_scanned": self.files_scanned,
            "active_edges": self.active_edges,
            "historical_edges": self.historical_edges,
            "findings": [asdict(item) for item in self.findings],
            "artifacts": list(self.artifacts),
        }


def _is_historical(rel: str) -> bool:
    return any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in HISTORICAL_PREFIXES)


def iter_markdown_files(root: Path, *, include_historical: bool = False) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        rel_path = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel_path.parts):
            continue
        rel = rel_path.as_posix()
        if not include_historical and _is_historical(rel):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def _strip_destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    if " " in raw:
        raw = raw.split(None, 1)[0]
    return raw


def resolve_local_link(root: Path, source: Path, raw: str) -> Path | None:
    destination = _strip_destination(raw)
    if not destination or destination.startswith("#"):
        return None
    lowered = destination.lower()
    if lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
        return None

    destination = unquote(destination.split("#", 1)[0].split("?", 1)[0])
    if not destination:
        return None

    if destination.startswith("/"):
        target = root / destination.lstrip("/")
    else:
        target = source.parent / destination
    try:
        resolved = target.resolve(strict=False)
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def declared_ids(text: str) -> tuple[str, ...]:
    ids = set(ID_FIELD_RE.findall(text))
    ids.update(HEADING_ID_RE.findall(text))
    return tuple(sorted(ids))


def _pending_end_date(text: str) -> date | None:
    if not PENDING_RE.search(text):
        return None
    parsed: list[date] = []
    for value in DATED_END_RE.findall(text):
        try:
            parsed.append(date.fromisoformat(value))
        except ValueError:
            continue
    return max(parsed) if parsed else None


def scan_repository(
    root: Path,
    *,
    include_historical: bool = False,
    as_of: date | None = None,
    include_thin: bool = True,
) -> ScanResult:
    root = root.resolve()
    as_of = as_of or date.today()
    paths = iter_markdown_files(root, include_historical=include_historical)
    path_map = {path.resolve(): path.relative_to(root).as_posix() for path in paths}

    artifacts: dict[str, Artifact] = {}
    findings: list[Finding] = []
    id_locations: dict[str, list[str]] = {}

    for path in paths:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        ids = declared_ids(text)
        artifact = Artifact(
            path=rel,
            text=text,
            declared_ids=ids,
            outgoing_active=set(),
            outgoing_historical=set(),
            incoming_active=set(),
        )
        artifacts[rel] = artifact
        for stable_id in ids:
            id_locations.setdefault(stable_id, []).append(rel)

        for raw in MARKDOWN_LINK_RE.findall(text):
            target = resolve_local_link(root, path, raw)
            if target is None:
                continue
            target_rel = target.relative_to(root).as_posix()
            if not target.exists():
                findings.append(
                    Finding(
                        code="BROKEN_LINK",
                        path=rel,
                        detail=f"local Markdown target does not exist: {target_rel}",
                        severity="BROKEN",
                        target=target_rel,
                    )
                )
                continue

            target_scan_rel = path_map.get(target)
            if target_scan_rel:
                artifact.outgoing_active.add(target_scan_rel)
            elif _is_historical(target_rel):
                artifact.outgoing_historical.add(target_rel)

    for rel, artifact in artifacts.items():
        for target in artifact.outgoing_active:
            artifacts[target].incoming_active.add(rel)

    for stable_id, locations in sorted(id_locations.items()):
        if len(locations) > 1:
            findings.append(
                Finding(
                    code="DUPLICATE_STABLE_ID",
                    path=locations[0],
                    detail=f"{stable_id} is declared in {len(locations)} files: {', '.join(locations)}",
                    severity="BROKEN",
                )
            )

    for rel, artifact in artifacts.items():
        if rel not in ROOT_ANCHORS:
            active_degree = len(artifact.outgoing_active | artifact.incoming_active)
            if active_degree == 0:
                if artifact.outgoing_historical:
                    findings.append(
                        Finding(
                            code="HISTORICAL_ONLY",
                            path=rel,
                            detail="no active Markdown relationships; outgoing links point only to historical material",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            code="ORPHAN_CANDIDATE",
                            path=rel,
                            detail="no inbound or outbound active Markdown relationships",
                        )
                    )
            elif include_thin and active_degree == 1:
                findings.append(
                    Finding(
                        code="THIN_CONNECTION",
                        path=rel,
                        detail="only one active Markdown relationship; review whether the artifact has enough context",
                        severity="INFO",
                    )
                )

        if (
            (rel.startswith("work/ideas/") or rel.startswith("work/insights/"))
            and NOT_PROMOTED_RE.search(artifact.text)
            and not CURRENT_DISPOSITION_RE.search(artifact.text)
        ):
            findings.append(
                Finding(
                    code="UNRECONCILED_CAPTURE",
                    path=rel,
                    detail="record still says 'Not promoted' and has no current disposition/reconciliation section",
                )
            )

        if SUPERSEDED_RE.search(artifact.text) and not (
            artifact.outgoing_active or artifact.outgoing_historical
        ):
            findings.append(
                Finding(
                    code="SUPERSEDED_WITHOUT_LINK",
                    path=rel,
                    detail="record says SUPERSEDED but does not link to a replacement or durable context",
                )
            )

        pending_end = _pending_end_date(artifact.text)
        if pending_end and pending_end < as_of:
            findings.append(
                Finding(
                    code="OVERDUE_PENDING_EXPERIMENT",
                    path=rel,
                    detail=f"pending experiment/result has an end date {pending_end.isoformat()} before {as_of.isoformat()}",
                )
            )

    artifact_rows = tuple(
        {
            "path": rel,
            "declared_ids": list(artifact.declared_ids),
            "incoming_active": sorted(artifact.incoming_active),
            "outgoing_active": sorted(artifact.outgoing_active),
            "outgoing_historical": sorted(artifact.outgoing_historical),
        }
        for rel, artifact in sorted(artifacts.items())
    )

    active_edges = sum(len(item.outgoing_active) for item in artifacts.values())
    historical_edges = sum(len(item.outgoing_historical) for item in artifacts.values())

    return ScanResult(
        root=str(root),
        as_of=as_of.isoformat(),
        include_historical=include_historical,
        files_scanned=len(paths),
        active_edges=active_edges,
        historical_edges=historical_edges,
        findings=tuple(sorted(findings, key=lambda item: (item.path, item.code, item.detail))),
        artifacts=artifact_rows,
    )


def _render_text(result: ScanResult) -> str:
    lines = [
        "MAPS Spiderweb Audit",
        "====================",
        f"files scanned: {result.files_scanned}",
        f"active Markdown edges: {result.active_edges}",
        f"historical edges: {result.historical_edges}",
        f"as of: {result.as_of}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
        return "\n".join(lines)

    counts: dict[str, int] = {}
    for finding in result.findings:
        counts[finding.code] = counts.get(finding.code, 0) + 1
    lines.append("Finding counts:")
    for code, count in sorted(counts.items()):
        lines.append(f"- {code}: {count}")
    lines.append("")
    for finding in result.findings:
        target = f" -> {finding.target}" if finding.target else ""
        lines.append(f"[{finding.severity}] {finding.code}: {finding.path}{target}")
        lines.append(f"  {finding.detail}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Advisory audit of durable Markdown relationships in MAPS_Lean."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--include-historical", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--no-thin", action="store_true")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="return non-zero only for objective broken-link or duplicate-ID findings",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    result = scan_repository(
        args.root,
        include_historical=args.include_historical,
        as_of=args.as_of,
        include_thin=not args.no_thin,
    )
    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(_render_text(result))

    if args.fail_on_broken and any(
        item.severity == "BROKEN" for item in result.findings
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
