#!/usr/bin/env python3
"""Read-only Markdown knowledge-graph analyzer for MAP Lean.

It understands ordinary Markdown links and Obsidian-style wikilinks. It never
edits a source note: reports are written only when --output-dir is supplied.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
WIKILINK = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
INLINE_FILE_REFERENCE = re.compile(r"`([^`\n]+\.md(?:#[^`]*)?)`")
SKIP_PARTS = {".git", ".obsidian", "__pycache__", ".venv"}
FIRST_RUN = "docs/FIRST_RUN.md"


@dataclass(frozen=True)
class Link:
    source: str
    raw_target: str
    target: str | None
    kind: str


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
    )


def classify(path: str) -> str:
    if path.startswith("legacy/"):
        return "legacy"
    if path.startswith("archive/"):
        return "archive"
    if path.startswith("work/tasks/"):
        return "task"
    if path.startswith("work/reviews/"):
        return "review"
    if path.startswith("work/handoffs/"):
        return "handoff"
    if path.startswith("work/decisions/"):
        return "decision"
    if path.startswith("playbook/"):
        return "method"
    if path.startswith("docs/"):
        return "guide"
    if path.startswith("templates/"):
        return "template"
    if path.startswith("state/"):
        return "state"
    return "root"


def normalize_target(raw: str, source: str, root: Path, files: set[str]) -> str | None:
    target = unquote(raw.strip().strip("<>")).split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "file:")):
        return None
    if target.startswith("/"):
        candidate = target.lstrip("/")
    else:
        candidate = (Path(source).parent / target).as_posix()
    candidate = posixpath.normpath(candidate)
    # Obsidian resolves a bare title by vault-wide filename. Resolve only when
    # unique, otherwise leave it unresolved instead of silently guessing.
    if candidate in files:
        return candidate
    if not candidate.endswith(".md") and f"{candidate}.md" in files:
        return f"{candidate}.md"
    if "/" not in target:
        matches = [path for path in files if Path(path).stem == target]
        if len(matches) == 1:
            return matches[0]
    return None


def extract_links(path: Path, root: Path, files: set[str]) -> list[Link]:
    source = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    # Link-looking examples in code blocks are teaching material, not graph
    # edges. This intentionally excludes inline-code examples such as
    # `[[wikilinks]]` from the live topology.
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    links: list[Link] = []
    for match in MARKDOWN_LINK.finditer(text):
        raw = match.group(1).split(' "', 1)[0]
        links.append(Link(source, raw, normalize_target(raw, source, root, files), "markdown"))
    for match in WIKILINK.finditer(text):
        raw = match.group(1).split("|", 1)[0].strip()
        links.append(Link(source, raw, normalize_target(raw, source, root, files), "wikilink"))
    return links


def resolve_plain_reference(raw: str, source: str, root: Path, files: set[str]) -> str | None:
    """Resolve a code-styled file mention without treating it as a graph edge."""
    for candidate_raw in (raw, (Path(source).parent / raw).as_posix()):
        candidate = unquote(candidate_raw.split("#", 1)[0]).lstrip("./")
        if candidate in files:
            return candidate
    return None


def plain_file_mentions(path: Path, root: Path, files: set[str]) -> list[tuple[str, str]]:
    source = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    mentions = []
    for match in INLINE_FILE_REFERENCE.finditer(text):
        target = resolve_plain_reference(match.group(1), source, root, files)
        if target:
            mentions.append((source, target))
    return mentions


def reachable(start: str, adjacency: dict[str, set[str]], removed: str | None = None) -> set[str]:
    if start == removed or start not in adjacency:
        return set()
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for target in adjacency[node]:
            if target != removed and target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def analyze(root: Path) -> dict:
    paths = markdown_files(root)
    files = {path.relative_to(root).as_posix() for path in paths}
    links = [link for path in paths for link in extract_links(path, root, files)]
    plain_mentions = [mention for path in paths for mention in plain_file_mentions(path, root, files)]
    adjacency: dict[str, set[str]] = {path: set() for path in files}
    incoming: dict[str, set[str]] = {path: set() for path in files}
    broken = []
    for link in links:
        if link.target is None:
            raw = link.raw_target.split("#", 1)[0]
            if raw and not raw.startswith(("http://", "https://", "mailto:", "file:")):
                broken.append({"source": link.source, "target": link.raw_target, "kind": link.kind})
            continue
        adjacency[link.source].add(link.target)
        incoming[link.target].add(link.source)

    # These references are deliberately *not* edges: they are useful evidence
    # of navigation prose that Obsidian's graph cannot show yet.
    actual_edges = {(source, target) for source, targets in adjacency.items() for target in targets}
    unlinked_mentions = sorted(
        {pair for pair in plain_mentions if pair not in actual_edges},
        key=lambda pair: (pair[0], pair[1]),
    )

    active = sorted(path for path in files if classify(path) not in {"legacy", "archive"})
    active_orphans = [
        path for path in active
        if not adjacency[path] and not incoming[path]
    ]
    hubs = sorted(
        (
            {"path": path, "incoming": len(incoming[path]), "outgoing": len(adjacency[path]),
             "kind": classify(path)}
            for path in active
        ),
        key=lambda row: (row["incoming"] + row["outgoing"], row["incoming"], row["path"]),
        reverse=True,
    )[:12]
    first_run_reach = reachable(FIRST_RUN, adjacency)
    active_reach = sorted(path for path in first_run_reach if path in active)
    resilience = []
    baseline = len(active_reach)
    if baseline:
        for candidate in active_reach:
            if candidate == FIRST_RUN:
                continue
            after = reachable(FIRST_RUN, adjacency, candidate)
            lost = sorted(path for path in active_reach if path not in after and path != candidate)
            if lost:
                resilience.append({"removed": candidate, "active_notes_lost": lost, "loss_count": len(lost)})
    resilience.sort(key=lambda row: (row["loss_count"], row["removed"]), reverse=True)
    kind_counts = Counter(classify(path) for path in files)
    return {
        "root": str(root),
        "method": {
            "read_only": True,
            "parses": ["Markdown links", "Obsidian wikilinks"],
            "active_zone": "all Markdown except legacy/ and archive/",
            "high_resistance": ["legacy/", "archive/"],
            "limitations": [
                "Link topology is not semantic relevance or truth.",
                "Bare wikilinks resolve only when the filename is unique.",
                "External URLs are ignored as graph edges.",
                "No proposed link is applied automatically.",
            ],
        },
        "summary": {
            "notes": len(files), "active_notes": len(active), "links": len(links),
            "resolved_edges": sum(len(value) for value in adjacency.values()),
            "broken_links": len(broken),
            "active_broken_links": sum(not row["source"].startswith("legacy/") for row in broken),
            "unlinked_file_mentions": len(unlinked_mentions),
            "active_unlinked_file_mentions": sum(not source.startswith("legacy/") for source, _ in unlinked_mentions),
            "active_orphans": len(active_orphans),
            "first_run_active_reach": len(active_reach), "kinds": dict(sorted(kind_counts.items())),
        },
        "broken_links": broken,
        "unlinked_file_mentions": [
            {"source": source, "target": target, "source_kind": classify(source)}
            for source, target in unlinked_mentions
        ],
        "active_orphans": active_orphans,
        "hubs": hubs,
        "first_run_reachability": {"start": FIRST_RUN, "active_notes": active_reach},
        "resilience": resilience[:10],
    }


def markdown_report(data: dict) -> str:
    summary = data["summary"]
    lines = [
        "# Digital Fungus Report",
        "",
        "## Purpose",
        "",
        "A read-only knowledge-graph pass over MAP Lean. It models active notes as",
        "the growth zone and treats `legacy/` / `archive/` as reachable but",
        "high-resistance reference territory. Findings are proposals for human",
        "review, not automatic link edits.",
        "",
        "## Snapshot",
        "",
        f"- Notes scanned: {summary['notes']} ({summary['active_notes']} active)",
        f"- Resolved internal edges: {summary['resolved_edges']}",
        f"- Unresolved internal links: {summary['broken_links']} ({summary['active_broken_links']} active)",
        f"- Unlinked file mentions: {summary['unlinked_file_mentions']} ({summary['active_unlinked_file_mentions']} active)",
        f"- Active orphans: {summary['active_orphans']}",
        f"- Active notes reachable from `docs/FIRST_RUN.md`: {summary['first_run_active_reach']}",
        "",
        "## Findings",
        "",
    ]
    active_broken = [row for row in data["broken_links"] if not row["source"].startswith("legacy/")]
    legacy_broken = len(data["broken_links"]) - len(active_broken)
    if active_broken:
        lines += ["### Unresolved internal links", ""]
        lines += [f"- `{row['source']}` → `{row['target']}` ({row['kind']})" for row in active_broken[:30]]
        lines.append("")
    else:
        lines += ["### Unresolved internal links", "", "None found in active Lean material by this parser.", ""]
    if legacy_broken:
        lines += [f"Legacy/reference material has {legacy_broken} unresolved candidate links; treat these as historical cleanup evidence, not an onboarding defect.", ""]
    active_mentions = [row for row in data["unlinked_file_mentions"] if row["source_kind"] != "legacy"]
    lines += ["### Unlinked navigational references", ""]
    if active_mentions:
        lines += ["These code-styled paths are readable to an agent but invisible as graph edges in Obsidian. Review them as candidates for real links:", ""]
        lines += [f"- `{row['source']}` mentions `{row['target']}`" for row in active_mentions[:30]]
    else:
        lines += ["None found in active Lean material."]
    lines.append("")
    lines += ["### Active orphans", ""]
    lines += [f"- `{path}`" for path in data["active_orphans"][:40]] or ["None."]
    lines += ["", "### High-traffic active notes", "", "| Note | Incoming | Outgoing | Kind |", "| --- | ---: | ---: | --- |"]
    lines += [f"| `{row['path']}` | {row['incoming']} | {row['outgoing']} | {row['kind']} |" for row in data["hubs"]]
    lines += ["", "### First-run resilience", ""]
    if data["resilience"]:
        lines += [f"- Removing `{row['removed']}` makes {row['loss_count']} active note(s) unreachable from FIRST_RUN: " + ", ".join(f"`{item}`" for item in row["active_notes_lost"][:8]) for row in data["resilience"]]
    else:
        lines += ["No single intermediate active note disconnected another active note from FIRST_RUN in this directed-link pass."]
    lines += ["", "## Interpretation", "", "- A link is a navigational claim, not proof that a note is current or authoritative.", "- Prioritize fixing broken links and onboarding-path gaps before adding visual density.", "- Review orphan notes before linking them: some should remain intentionally isolated templates or records.", "- Use Obsidian Graph/Local Graph to inspect the same link topology visually; standard Markdown links and wikilinks are both parsed.", "", "## Limitations", ""]
    lines += [f"- {item}" for item in data["method"]["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, help="Write JSON and Markdown reports here.")
    parser.add_argument("--prefix", default="TASK-003-digital-fungus", help="Output filename prefix when --output-dir is used.")
    args = parser.parse_args()
    root = args.root.resolve()
    data = analyze(root)
    if args.output_dir:
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        (output / f"{args.prefix}-findings.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        (output / f"{args.prefix}-report.md").write_text(markdown_report(data), encoding="utf-8")
    print(json.dumps(data["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
