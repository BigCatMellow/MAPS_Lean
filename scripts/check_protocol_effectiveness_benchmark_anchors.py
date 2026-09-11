"""Fail closed if a resolved PR #341 benchmark finding loses its owner clauses.

AGENTS.md invariant 13 requires a mechanical safeguard after a repeated failure
pattern. PR #341 correction passes repeatedly regressed previously resolved
review findings, including semantic rewrites that preserved section headings.
This check therefore pins every resolved B/M/N/F/G/H finding to an owning file
and one or more required rule-bearing textual anchors.

The manifest is deliberately data-driven so reviewers can inspect the mapping.
This script independently hard-codes the complete finding-ID set plus minimum
anchor counts for the highest-risk semantic surfaces. A future edit cannot
silently "fix" the check by deleting a finding or weakening a critical finding
back to one broad heading/prefix.
"""

from __future__ import annotations

import json
from pathlib import Path


EXPECTED_IDS = {
    "B1", "B2", "B3",
    *(f"M{i}" for i in range(1, 13)),
    *(f"N{i}" for i in range(1, 11)),
    *(f"F{i}" for i in range(1, 10)),
    *(f"G{i}" for i in range(1, 11)),
    *(f"H{i}" for i in range(1, 6)),
}

# These minima are intentionally independent of the manifest. They protect the
# rule surfaces that prior mutation probes or real review regressions showed to
# be vulnerable to semantic rewrite while headings/prefixes remained intact.
MIN_ANCHOR_COUNTS = {
    "M6": 7,
    "M7": 4,
    "N4": 4,
    "N5": 3,
    "F4": 6,
    "F5": 3,
    "G2": 3,
    "G3": 2,
    "G6": 5,
    "G10": 2,
    "H1": 9,
    "H2": 3,
    "H4": 6,
    "H5": 5,
}

MANIFEST_REL = Path(
    "work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json"
)


def check(repo_root: Path) -> tuple[bool, str]:
    manifest_path = repo_root / MANIFEST_REL
    if not manifest_path.is_file():
        return False, f"missing benchmark finding-anchor manifest: {manifest_path}"

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"cannot parse {manifest_path}: {exc}"

    findings = payload.get("findings")
    if not isinstance(findings, list):
        return False, "finding-anchor manifest 'findings' must be a list"

    seen: dict[str, dict[str, object]] = {}
    duplicates: list[str] = []
    for entry in findings:
        if not isinstance(entry, dict):
            return False, f"finding entry must be an object, got {entry!r}"
        finding_id = entry.get("id")
        owner_file = entry.get("owner_file")
        anchors = entry.get("anchors")
        if not isinstance(finding_id, str) or not finding_id:
            return False, f"finding entry needs non-empty string id: {entry!r}"
        if not isinstance(owner_file, str) or not owner_file:
            return False, f"finding entry needs non-empty string owner_file: {entry!r}"
        if not isinstance(anchors, list) or not anchors:
            return False, f"finding entry needs non-empty anchors list: {entry!r}"
        if not all(isinstance(anchor, str) and anchor for anchor in anchors):
            return False, f"finding anchors must all be non-empty strings: {entry!r}"
        if finding_id in seen:
            duplicates.append(finding_id)
        seen[finding_id] = entry

    if duplicates:
        return False, f"duplicate finding IDs in anchor manifest: {sorted(set(duplicates))}"

    missing_ids = EXPECTED_IDS - set(seen)
    unexpected_ids = set(seen) - EXPECTED_IDS
    if missing_ids or unexpected_ids:
        return False, (
            "finding-anchor ID set mismatch: "
            f"missing={sorted(missing_ids)} unexpected={sorted(unexpected_ids)}"
        )

    failures: list[str] = []
    for finding_id, minimum in sorted(MIN_ANCHOR_COUNTS.items()):
        anchors = seen[finding_id]["anchors"]
        assert isinstance(anchors, list)
        if len(anchors) < minimum:
            failures.append(
                f"{finding_id}: expected at least {minimum} semantic anchors, got {len(anchors)}"
            )

    for finding_id in sorted(EXPECTED_IDS):
        entry = seen[finding_id]
        owner_rel = Path(str(entry["owner_file"]))
        if owner_rel.is_absolute() or ".." in owner_rel.parts:
            failures.append(f"{finding_id}: unsafe owner path {owner_rel}")
            continue
        owner_path = repo_root / owner_rel
        if not owner_path.is_file():
            failures.append(f"{finding_id}: owner file missing: {owner_rel}")
            continue
        text = owner_path.read_text(encoding="utf-8")
        anchors = entry["anchors"]
        assert isinstance(anchors, list)
        for anchor in anchors:
            assert isinstance(anchor, str)
            if anchor not in text:
                failures.append(
                    f"{finding_id}: required semantic anchor missing from "
                    f"{owner_rel}: {anchor!r}"
                )

    if failures:
        return False, "resolved-finding anchor regression:\n- " + "\n- ".join(failures)

    counts = ", ".join(
        f"{finding_id}:{len(seen[finding_id]['anchors'])}"
        for finding_id in sorted(EXPECTED_IDS)
    )
    total_anchors = sum(len(seen[finding_id]["anchors"]) for finding_id in EXPECTED_IDS)
    return True, (
        f"protocol benchmark finding anchors OK "
        f"({len(EXPECTED_IDS)} findings, {total_anchors} semantic anchors)\n"
        f"anchor counts: {counts}"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ok, message = check(repo_root)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
