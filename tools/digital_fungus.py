#!/usr/bin/env python3
"""Read-only Markdown knowledge-graph and route-cost analyzer for MAP Lean.

It understands ordinary Markdown links and Obsidian-style wikilinks. It never
edits a source note: reports are written only when --output-dir is supplied.
Token counts are rough planning proxies, not model-specific tokenizer results.
"""

from __future__ import annotations

import argparse
import heapq
import json
import posixpath
import re
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
WIKILINK = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
INLINE_FILE_REFERENCE = re.compile(r"`([^`\n]+\.md(?:#[^`]*)?)`")
SKIP_PARTS = {".git", ".obsidian", "__pycache__", ".venv"}
FIRST_RUN = "docs/FIRST_RUN.md"
TOKEN_PROXY_CHARS = 4
ROUTE_TARGETS = (
    "playbook/INDEX.md",
    "work/README.md",
    "work/roadmaps/README.md",
    "work/coordination/README.md",
    "state/CURRENT.md",
)


@dataclass(frozen=True)
class Link:
    source: str
    raw_target: str
    target: str | None
    kind: str


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
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


def estimated_tokens(text: str) -> int:
    """Stable rough token proxy for route comparison, not billing."""
    return max(1, (len(text) + TOKEN_PROXY_CHARS - 1) // TOKEN_PROXY_CHARS)


def _local_candidate(raw: str, source: str) -> str | None:
    target = unquote(raw.strip().strip("<>")).split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "file:")):
        return None
    if target.startswith("/"):
        candidate = target.lstrip("/")
    else:
        candidate = (Path(source).parent / target).as_posix()
    return posixpath.normpath(candidate)


def normalize_target(raw: str, source: str, root: Path, files: set[str]) -> str | None:
    candidate = _local_candidate(raw, source)
    if candidate is None:
        return None
    target = unquote(raw.strip().strip("<>")).split("#", 1)[0].strip()
    if candidate in files:
        return candidate
    if not candidate.endswith(".md") and f"{candidate}.md" in files:
        return f"{candidate}.md"
    if "/" not in target:
        matches = [path for path in files if Path(path).stem == target]
        if len(matches) == 1:
            return matches[0]
    return None


def valid_directory_target(raw: str, source: str, root: Path) -> str | None:
    """Resolve a valid local directory route without making it a graph-note node."""
    candidate = _local_candidate(raw, source)
    if candidate is None:
        return None
    path = root / candidate
    if path.is_dir():
        return candidate.rstrip("/") + "/"
    return None


def extract_links(path: Path, root: Path, files: set[str]) -> list[Link]:
    source = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
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


def least_read_cost_route(
    start: str,
    target: str,
    adjacency: dict[str, set[str]],
    token_costs: dict[str, int],
) -> dict | None:
    """Find the linked route with the lowest added read-cost proxy.

    The start document is assumed open already; each later note contributes its
    rough token estimate.
    """
    if start not in adjacency or target not in adjacency:
        return None
    if start == target:
        return {"path": [start], "hops": 0, "added_estimated_tokens": 0}

    queue: list[tuple[int, int, str, tuple[str, ...]]] = [(0, 0, start, (start,))]
    best: dict[str, tuple[int, int]] = {start: (0, 0)}
    while queue:
        cost, hops, node, path = heapq.heappop(queue)
        if best.get(node) != (cost, hops):
            continue
        if node == target:
            return {
                "path": list(path),
                "hops": hops,
                "added_estimated_tokens": cost,
            }
        for nxt in sorted(adjacency[node]):
            candidate = (cost + token_costs[nxt], hops + 1)
            if candidate < best.get(nxt, (10**18, 10**18)):
                best[nxt] = candidate
                heapq.heappush(queue, (*candidate, nxt, path + (nxt,)))
    return None


def analyze(root: Path) -> dict:
    paths = markdown_files(root)
    files = {path.relative_to(root).as_posix() for path in paths}
    texts = {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8", errors="replace")
        for path in paths
    }
    token_costs = {path: estimated_tokens(text) for path, text in texts.items()}
    links = [link for path in paths for link in extract_links(path, root, files)]
    plain_mentions = [mention for path in paths for mention in plain_file_mentions(path, root, files)]
    adjacency: dict[str, set[str]] = {path: set() for path in files}
    incoming: dict[str, set[str]] = {path: set() for path in files}
    broken = []
    directory_routes = []

    for link in links:
        if link.target is None:
            directory = valid_directory_target(link.raw_target, link.source, root)
            if directory:
                directory_routes.append(
                    {"source": link.source, "target": directory, "kind": link.kind}
                )
                continue
            raw = link.raw_target.split("#", 1)[0]
            if raw and not raw.startswith(("http://", "https://", "mailto:", "file:")):
                broken.append({"source": link.source, "target": link.raw_target, "kind": link.kind})
            continue
        adjacency[link.source].add(link.target)
        incoming[link.target].add(link.source)

    actual_edges = {(source, target) for source, targets in adjacency.items() for target in targets}
    unlinked_mentions = sorted(
        {pair for pair in plain_mentions if pair not in actual_edges},
        key=lambda pair: (pair[0], pair[1]),
    )

    active = sorted(path for path in files if classify(path) not in {"legacy", "archive"})
    active_orphans = [path for path in active if not adjacency[path] and not incoming[path]]
    hubs = sorted(
        (
            {
                "path": path,
                "incoming": len(incoming[path]),
                "outgoing": len(adjacency[path]),
                "kind": classify(path),
            }
            for path in active
        ),
        key=lambda row: (row["incoming"] + row["outgoing"], row["incoming"], row["path"]),
        reverse=True,
    )[:12]

    first_run_reach = reachable(FIRST_RUN, adjacency)
    active_reach = sorted(path for path in first_run_reach if path in active)
    resilience = []
    if active_reach:
        for candidate in active_reach:
            if candidate == FIRST_RUN:
                continue
            after = reachable(FIRST_RUN, adjacency, candidate)
            lost = sorted(path for path in active_reach if path not in after and path != candidate)
            if lost:
                resilience.append(
                    {"removed": candidate, "active_notes_lost": lost, "loss_count": len(lost)}
                )
    resilience.sort(key=lambda row: (row["loss_count"], row["removed"]), reverse=True)

    navigation_routes = {
        target: (
            least_read_cost_route(FIRST_RUN, target, adjacency, token_costs)
            if target in files
            else None
        )
        for target in ROUTE_TARGETS
    }
    reachable_routes = [route for route in navigation_routes.values() if route is not None]
    max_route_tokens = max(
        (route["added_estimated_tokens"] for route in reachable_routes), default=0
    )
    max_route_hops = max((route["hops"] for route in reachable_routes), default=0)
    kind_counts = Counter(classify(path) for path in files)

    return {
        "root": str(root),
        "method": {
            "read_only": True,
            "parses": ["Markdown links", "Obsidian wikilinks"],
            "active_zone": "all Markdown except legacy/ and archive/",
            "high_resistance": ["legacy/", "archive/"],
            "token_proxy": f"ceil(UTF-8 text characters / {TOKEN_PROXY_CHARS}); comparison only",
            "limitations": [
                "Link topology is not semantic relevance or truth.",
                "Estimated tokens are a rough cross-model planning proxy, not billing data.",
                "A cheapest linked path is not proof that the destination is the correct authority.",
                "Directory links are valid navigation but are not note-graph edges.",
                "Bare wikilinks resolve only when the filename is unique.",
                "External URLs are ignored as graph edges.",
                "No proposed link is applied automatically.",
            ],
        },
        "summary": {
            "notes": len(files),
            "active_notes": len(active),
            "links": len(links),
            "resolved_edges": sum(len(value) for value in adjacency.values()),
            "directory_routes": len(directory_routes),
            "broken_links": len(broken),
            "active_broken_links": sum(not row["source"].startswith("legacy/") for row in broken),
            "unlinked_file_mentions": len(unlinked_mentions),
            "active_unlinked_file_mentions": sum(
                not source.startswith("legacy/") for source, _ in unlinked_mentions
            ),
            "active_orphans": len(active_orphans),
            "first_run_active_reach": len(active_reach),
            "active_estimated_tokens": sum(token_costs[path] for path in active),
            "navigation_targets": len(ROUTE_TARGETS),
            "navigation_targets_reachable": len(reachable_routes),
            "max_navigation_route_hops": max_route_hops,
            "max_navigation_route_added_estimated_tokens": max_route_tokens,
            "kinds": dict(sorted(kind_counts.items())),
        },
        "note_estimated_tokens": dict(sorted(token_costs.items())),
        "navigation_routes": {"start": FIRST_RUN, "targets": navigation_routes},
        "directory_routes": directory_routes,
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
        "A read-only knowledge-graph and route-cost pass over MAP Lean. It models",
        "active notes as the growth zone and treats `legacy/` / `archive/` as",
        "reachable but high-resistance reference territory. Findings are navigation",
        "evidence for review, not automatic link edits or authority claims.",
        "",
        "## Snapshot",
        "",
        f"- Notes scanned: {summary['notes']} ({summary['active_notes']} active)",
        f"- Resolved internal edges: {summary['resolved_edges']}",
        f"- Valid directory routes: {summary['directory_routes']}",
        f"- Unresolved internal links: {summary['broken_links']} ({summary['active_broken_links']} active)",
        f"- Unlinked file mentions: {summary['unlinked_file_mentions']} ({summary['active_unlinked_file_mentions']} active)",
        f"- Active orphans: {summary['active_orphans']}",
        f"- Active notes reachable from `docs/FIRST_RUN.md`: {summary['first_run_active_reach']}",
        f"- Rough active-corpus token proxy: {summary['active_estimated_tokens']}",
        f"- Navigation targets reachable: {summary['navigation_targets_reachable']}/{summary['navigation_targets']}",
        f"- Highest target-route hop count: {summary['max_navigation_route_hops']}",
        f"- Highest target-route added token proxy: {summary['max_navigation_route_added_estimated_tokens']}",
        "",
        "## Navigation routes",
        "",
        "Token values below estimate additional notes opened after FIRST_RUN using",
        f"`ceil(characters/{TOKEN_PROXY_CHARS})`; they are comparative, not billing values.",
        "",
        "| Target | Hops | Added token proxy | Cheapest linked route |",
        "| --- | ---: | ---: | --- |",
    ]
    for target, route in data["navigation_routes"]["targets"].items():
        if route is None:
            lines.append(f"| `{target}` | — | — | unreachable |")
        else:
            path = " → ".join(f"`{item}`" for item in route["path"])
            lines.append(
                f"| `{target}` | {route['hops']} | {route['added_estimated_tokens']} | {path} |"
            )

    lines += ["", "## Findings", ""]
    active_broken = [row for row in data["broken_links"] if not row["source"].startswith("legacy/")]
    legacy_broken = len(data["broken_links"]) - len(active_broken)
    if active_broken:
        lines += ["### Unresolved internal links", ""]
        lines += [
            f"- `{row['source']}` → `{row['target']}` ({row['kind']})"
            for row in active_broken[:30]
        ]
        lines.append("")
    else:
        lines += [
            "### Unresolved internal links",
            "",
            "None found in active Lean material by this parser.",
            "",
        ]
    if legacy_broken:
        lines += [
            f"Legacy/reference material has {legacy_broken} unresolved candidate links; "
            "treat these as historical cleanup evidence, not an onboarding defect.",
            "",
        ]

    active_mentions = [
        row for row in data["unlinked_file_mentions"] if row["source_kind"] != "legacy"
    ]
    lines += ["### Unlinked navigational references", ""]
    if active_mentions:
        lines += [
            "These code-styled paths are readable to an agent but invisible as graph edges. "
            "Review them as candidates for real links:",
            "",
        ]
        lines += [
            f"- `{row['source']}` mentions `{row['target']}`" for row in active_mentions[:30]
        ]
    else:
        lines += ["None found in active Lean material."]
    lines.append("")

    lines += ["### Active orphans", ""]
    lines += [f"- `{path}`" for path in data["active_orphans"][:40]] or ["None."]
    lines += [
        "",
        "### High-traffic active notes",
        "",
        "| Note | Incoming | Outgoing | Kind |",
        "| --- | ---: | ---: | --- |",
    ]
    lines += [
        f"| `{row['path']}` | {row['incoming']} | {row['outgoing']} | {row['kind']} |"
        for row in data["hubs"]
    ]

    lines += ["", "### First-run resilience", ""]
    if data["resilience"]:
        lines += [
            f"- Removing `{row['removed']}` makes {row['loss_count']} active note(s) "
            "unreachable from FIRST_RUN: "
            + ", ".join(f"`{item}`" for item in row["active_notes_lost"][:8])
            for row in data["resilience"]
        ]
    else:
        lines += [
            "No single intermediate active note disconnected another active note from "
            "FIRST_RUN in this directed-link pass."
        ]

    lines += [
        "",
        "## Interpretation",
        "",
        "- A link is a navigational claim, not proof that a note is current or authoritative.",
        "- Prefer direct low-cost routes to canonical owners over additional graph density.",
        "- Valid directory links are navigation endpoints, not broken note links.",
        "- Prioritize broken links and onboarding gaps before adding topical links.",
        "- Review orphan notes before linking them: some are intentionally isolated records/templates.",
        "- Standard Markdown links and wikilinks are both parsed.",
        "",
        "## Limitations",
        "",
    ]
    lines += [f"- {item}" for item in data["method"]["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, help="Write JSON and Markdown reports here.")
    parser.add_argument(
        "--prefix",
        default="TASK-003-digital-fungus",
        help="Output filename prefix when --output-dir is used.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    data = analyze(root)
    if args.output_dir:
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        (output / f"{args.prefix}-findings.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        (output / f"{args.prefix}-report.md").write_text(
            markdown_report(data), encoding="utf-8"
        )
    print(json.dumps(data["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
