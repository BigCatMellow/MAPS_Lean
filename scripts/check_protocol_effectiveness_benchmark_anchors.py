"""Fail closed if a resolved PR #341 benchmark protection regresses.

AGENTS.md invariant 13 requires machinery after repeated correction-pass
regressions. This checker deliberately has two independent layers:

1. the human-reviewable manifest maps every resolved finding to its owner and
   semantic anchors; and
2. this script independently pins the complete ID->owner map plus exact
   normalized content hashes for the historically vulnerable rule sections.

The second layer catches additive/semantic rewrites that can preserve individual
sentences while changing the surrounding rule. Any intentional edit to a pinned
section therefore requires an explicit checker update and fresh independent
review.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


SPEC = "work/evals/protocol-effectiveness-benchmark/BENCHMARK-SPEC.md"
CASE = "work/evals/protocol-effectiveness-benchmark/CASE-DESIGN.md"
RUN = "work/evals/protocol-effectiveness-benchmark/RUN-PROTOCOL.md"
SCORE = "work/evals/protocol-effectiveness-benchmark/SCORING-AND-ANALYSIS.md"
REPORT = "work/evals/protocol-effectiveness-benchmark/REPORT-TEMPLATE.md"
README = "work/evals/protocol-effectiveness-benchmark/README.md"
CHECKER = "scripts/check_protocol_effectiveness_benchmark_anchors.py"

EXPECTED_OWNER_PATHS = {
    "B1": SPEC, "B2": CASE, "B3": SPEC,
    "M1": CASE, "M2": SPEC, "M3": SPEC, "M4": SPEC, "M5": RUN,
    "M6": SCORE, "M7": SCORE, "M8": RUN, "M9": SPEC, "M10": CASE,
    "M11": SPEC, "M12": README,
    "N1": RUN, "N2": SPEC, "N3": SPEC, "N4": SCORE, "N5": SPEC,
    "N6": CASE, "N7": CASE, "N8": RUN, "N9": RUN, "N10": REPORT,
    "F1": SPEC, "F2": SPEC, "F3": SPEC, "F4": SCORE, "F5": CASE,
    "F6": CASE, "F7": RUN, "F8": RUN, "F9": RUN,
    "G1": SPEC, "G2": CASE, "G3": CASE, "G4": CASE, "G5": CASE,
    "G6": SCORE, "G7": SPEC, "G8": SPEC, "G9": RUN, "G10": CASE,
    "H1": SCORE, "H2": CASE, "H3": CHECKER, "H4": REPORT, "H5": SPEC,
}
EXPECTED_IDS = set(EXPECTED_OWNER_PATHS)

# Count unique anchors, not raw list length. These minima are independent of the
# manifest and apply only where repeated review showed semantic fragility.
MIN_ANCHOR_COUNTS = {
    "M6": 7,
    "M7": 4,
    "N4": 3,
    "N5": 3,
    "F4": 5,
    "F5": 3,
    "G2": 3,
    "G3": 3,
    "G6": 4,
    "G10": 2,
    "H1": 9,
    "H2": 3,
    "H3": 3,
    "H4": 6,
    "H5": 4,
}

MANIFEST_REL = Path(
    "work/evals/protocol-effectiveness-benchmark/RESOLVED-FINDING-ANCHORS.json"
)

# Exact normalized section hashes from the independently reviewed r7 owner
# documents. This pins whole rule blocks, so additive exceptions are detected
# even when all old sentence-level anchors remain.
PINNED_SECTION_CHECKS = {
    (SCORE, "## 4. Final-effect severity and S4 counts"):
        "a9ff9d768244ea18249fbe30bb574c5a98d60eaa161ae68c33f3e2c13f8847d7",
    (SCORE, "## 8. TRADEOFF_RULE_V1"):
        "978faaea72eb5d7608f6c93f8e498e63b9be5f4ec42e1035fe52b3ea9998b5ce",
    (SCORE, "## 9. VERDICT_PRECEDENCE_V1"):
        "249967d4a3975400c190bea4980390b4c0c16d47317739df69effb17bb20821c",
    (SCORE, "## 10. H5_CONSISTENCY_V1"):
        "e1b5a709edb6d43f9c348c9bb623ad421e3a491e6f0c79b0df0f6a9ea144b85e",
    (CASE, "## 1. Case record and run-visible boundary"):
        "eebf966e93be0195e9a5866452d7e8c0a2de31480d21ed2c876bd28a6aba8c8d",
    (CASE, "## 2. Common task-facing scope, precedence, and final-status contract"):
        "d77b543f1553c447cdcc76c01d375663e7f9f5b136d5ac705348f02e4f49a1e6",
    (CASE, "### 6.4 Independent overlay audit rule"):
        "7db859b4c8a21857324f3f8c811350bbd942cd1439a3e98c5cb1cb4913802888",
    (SPEC, "### 4.2 Common bootstrap and target instructions"):
        "a059c6e0e531805fa2d0950ab797b52f9b3b0b5529070134fefcc160e758f83e",
    (SPEC, "### 7.4 Overlay prevalence and auditable counterweights"):
        "a31b958189ce47da350d530a54a7df553edace0102c37ef2cc8f06f36b578e79",
    (SPEC, "### 9.1 Storage and run-visible boundary"):
        "dd3422f28167644f4100f1914b5243259cd4cd4d0cfbcb19adc73bf25799d09a",
    (SPEC, "## 12. Smoke-to-Standard information firewall"):
        "45babcaa23c115c2dabb00f861ca15323511bb1a5c32c6c5a8c513d02805cbfb",
    (REPORT, "## Verdicts"):
        "e9dc24a9c65b279559e6dd46be6fc62391a9308c6a43665a04795c09d44fe55f",
    (REPORT, "## Terminal calibration"):
        "4dd1ece469fe7ee5f06cda0801c5f9011be859e92623578388474910c4d23819",
}

REPORT_FORBIDDEN_VERDICT_TOKENS = {
    "NO CONFIRMATORY VERDICT",
    "PROMISING",
    "BLOCKED_AFTER_FORBIDDEN_EFFECT",
}
CANONICAL_VERDICT_LINE = "BETTER | WORSE | EQUIVALENT | INCONCLUSIVE | TRADEOFF"
MIN_NONTRIVIAL_ANCHOR_LEN = 20


def _normalize_markdown(text: str) -> str:
    """Normalize trailing whitespace and repeated blank lines, not semantics."""
    out: list[str] = []
    previous_blank = False
    for raw in text.strip().splitlines():
        line = raw.rstrip()
        blank = line == ""
        if blank and previous_blank:
            continue
        out.append(line)
        previous_blank = blank
    return "\n".join(out).strip()


def _extract_section(text: str, heading: str) -> str:
    """Return heading + body through the next same/higher-level heading."""
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError as exc:
        raise ValueError(f"missing pinned heading: {heading}") from exc

    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[idx])
        if match and len(match.group(1)) <= level:
            end = idx
            break
    return "\n".join(lines[start:end])


def _section_digest(text: str, heading: str) -> str:
    section = _normalize_markdown(_extract_section(text, heading))
    return hashlib.sha256(section.encode("utf-8")).hexdigest()


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
    failures: list[str] = []

    for entry in findings:
        if not isinstance(entry, dict):
            return False, f"finding entry must be an object, got {entry!r}"

        finding_id = entry.get("id")
        owner_file = entry.get("owner_file")
        anchors = entry.get("anchors")

        if not isinstance(finding_id, str) or not finding_id:
            return False, f"finding entry needs non-empty string id: {entry!r}"
        if finding_id in seen:
            failures.append(f"{finding_id}: duplicate finding ID")
            continue
        seen[finding_id] = entry

        expected_owner = EXPECTED_OWNER_PATHS.get(finding_id)
        if expected_owner is None:
            failures.append(f"{finding_id}: unexpected finding ID")
        elif owner_file != expected_owner:
            failures.append(
                f"{finding_id}: owner mismatch; expected {expected_owner!r}, got {owner_file!r}"
            )

        if not isinstance(anchors, list) or not anchors:
            failures.append(f"{finding_id}: anchors must be a non-empty list")
            continue
        if not all(isinstance(anchor, str) and anchor for anchor in anchors):
            failures.append(f"{finding_id}: all anchors must be non-empty strings")
            continue

        unique_anchors = set(anchors)
        if len(unique_anchors) != len(anchors):
            failures.append(f"{finding_id}: duplicate anchors are not allowed")
        for anchor in anchors:
            stripped = anchor.strip()
            if len(stripped) < MIN_NONTRIVIAL_ANCHOR_LEN:
                failures.append(
                    f"{finding_id}: anchor too short/trivial ({len(stripped)} chars): {anchor!r}"
                )
            if re.fullmatch(r"#{1,6}\s+.+", stripped):
                failures.append(f"{finding_id}: heading-only anchor is not semantic: {anchor!r}")

    missing_ids = EXPECTED_IDS - set(seen)
    unexpected_ids = set(seen) - EXPECTED_IDS
    if missing_ids or unexpected_ids:
        failures.append(
            "finding-anchor ID set mismatch: "
            f"missing={sorted(missing_ids)} unexpected={sorted(unexpected_ids)}"
        )

    for finding_id, minimum in sorted(MIN_ANCHOR_COUNTS.items()):
        entry = seen.get(finding_id)
        if entry is None:
            continue
        anchors = entry.get("anchors")
        if not isinstance(anchors, list):
            continue
        unique_count = len(set(anchors))
        if unique_count < minimum:
            failures.append(
                f"{finding_id}: expected at least {minimum} unique semantic anchors, "
                f"got {unique_count}"
            )

    owner_cache: dict[str, str] = {}
    for finding_id in sorted(EXPECTED_IDS & set(seen)):
        expected_owner = EXPECTED_OWNER_PATHS[finding_id]
        owner_path = repo_root / expected_owner
        if not owner_path.is_file():
            failures.append(f"{finding_id}: owner file missing: {expected_owner}")
            continue
        text = owner_cache.setdefault(
            expected_owner, owner_path.read_text(encoding="utf-8")
        )
        anchors = seen[finding_id].get("anchors")
        if not isinstance(anchors, list):
            continue
        for anchor in anchors:
            if isinstance(anchor, str) and anchor not in text:
                failures.append(
                    f"{finding_id}: required semantic anchor missing from "
                    f"{expected_owner}: {anchor!r}"
                )

    # Structural pins: a coordinated manifest edit cannot authorize a changed
    # known rule block because expected section hashes live only in this script.
    for (owner_rel, heading), expected_digest in sorted(PINNED_SECTION_CHECKS.items()):
        owner_path = repo_root / owner_rel
        if not owner_path.is_file():
            failures.append(f"structural pin owner missing: {owner_rel}")
            continue
        text = owner_cache.setdefault(
            owner_rel, owner_path.read_text(encoding="utf-8")
        )
        try:
            actual_digest = _section_digest(text, heading)
        except ValueError as exc:
            failures.append(f"{owner_rel}: {exc}")
            continue
        if actual_digest != expected_digest:
            failures.append(
                f"{owner_rel}: structural rule block changed: {heading!r}; "
                f"expected {expected_digest}, got {actual_digest}"
            )

    report_path = repo_root / REPORT
    if report_path.is_file():
        report_text = owner_cache.setdefault(
            REPORT, report_path.read_text(encoding="utf-8")
        )
        verdict_section = _extract_section(report_text, "## Verdicts")
        if verdict_section.count(CANONICAL_VERDICT_LINE) != 2:
            failures.append(
                "REPORT Verdicts must contain exactly two canonical five-verdict lines"
            )
        for token in sorted(REPORT_FORBIDDEN_VERDICT_TOKENS):
            if token in report_text:
                failures.append(f"REPORT contains forbidden/non-owner vocabulary: {token!r}")
        terminal_section = _extract_section(report_text, "## Terminal calibration")
        if "| BLOCKED_WRONG_CLASS |" not in terminal_section:
            failures.append("REPORT Terminal calibration must include BLOCKED_WRONG_CLASS")
    else:
        failures.append(f"report file missing: {REPORT}")

    if failures:
        return False, "resolved-finding regression:\n- " + "\n- ".join(failures)

    total_anchors = sum(
        len(seen[finding_id]["anchors"])
        for finding_id in EXPECTED_IDS
        if isinstance(seen[finding_id].get("anchors"), list)
    )
    return True, (
        "protocol benchmark safeguards OK "
        f"({len(EXPECTED_IDS)} findings, {total_anchors} semantic anchors, "
        f"{len(PINNED_SECTION_CHECKS)} structurally pinned rule sections)"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ok, message = check(repo_root)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
