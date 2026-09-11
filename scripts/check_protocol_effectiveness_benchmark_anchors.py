"""Fail closed if a resolved PR #341 benchmark finding loses its owner clause.

AGENTS.md invariant 13 requires a mechanical safeguard after a repeated failure
pattern. PR #341 correction passes twice regressed previously resolved review
findings, so this check pins every resolved B/M/N/F/G finding to an owning file
and a required textual anchor in the benchmark package.

The manifest is deliberately data-driven so reviewers can inspect the mapping.
This script hard-codes the complete finding-ID set reached by the r4 review so a
future edit cannot silently "fix" the check by deleting a manifest entry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


EXPECTED_IDS = {
    "B1", "B2", "B3",
    *(f"M{i}" for i in range(1, 13)),
    *(f"N{i}" for i in range(1, 11)),
    *(f"F{i}" for i in range(1, 10)),
    *(f"G{i}" for i in range(1, 11)),
}

MANIFEST_REL = Path("work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json")


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

    seen: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for entry in findings:
        if not isinstance(entry, dict):
            return False, f"finding entry must be an object, got {entry!r}"
        finding_id = entry.get("id")
        owner_file = entry.get("owner_file")
        anchor = entry.get("anchor")
        if not all(isinstance(value, str) and value for value in (finding_id, owner_file, anchor)):
            return False, f"finding entry needs non-empty id/owner_file/anchor: {entry!r}"
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
    for finding_id in sorted(EXPECTED_IDS):
        entry = seen[finding_id]
        owner_rel = Path(entry["owner_file"])
        if owner_rel.is_absolute() or ".." in owner_rel.parts:
            failures.append(f"{finding_id}: unsafe owner path {owner_rel}")
            continue
        owner_path = repo_root / owner_rel
        if not owner_path.is_file():
            failures.append(f"{finding_id}: owner file missing: {owner_rel}")
            continue
        text = owner_path.read_text(encoding="utf-8")
        if entry["anchor"] not in text:
            failures.append(
                f"{finding_id}: required anchor missing from {owner_rel}: {entry['anchor']!r}"
            )

    if failures:
        return False, "resolved-finding anchor regression:\n- " + "\n- ".join(failures)

    return True, f"protocol benchmark finding anchors OK ({len(EXPECTED_IDS)} findings)"


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ok, message = check(repo_root)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
