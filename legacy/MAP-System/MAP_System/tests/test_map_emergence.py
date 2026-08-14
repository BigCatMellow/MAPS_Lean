#!/usr/bin/env python3
"""Tests for MAP emergence artifact tooling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCRIPT = ROOT / "scripts" / "map_emergence.py"


def seed_emergence_tree(base: Path) -> Path:
    root = base / "MAP_System"
    emergence = root / "emergence"
    shutil.copytree(ROOT / "emergence" / "templates", emergence / "templates")
    for folder in ["insights", "synthesis", "ideas", "experiments", "promotions"]:
        (emergence / folder).mkdir(parents=True)
    return root


def run_cmd(*args: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_create_all_kinds_and_rebuild_index() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        created = []
        for kind in ["insight", "synthesis", "idea", "experiment", "promotion"]:
            result = run_cmd(
                "create",
                kind,
                "--project",
                "MAP",
                "--owner",
                "codex-test",
                "--summary",
                f"Test {kind} summary",
                "--date",
                "2026-06-29",
                "--slug",
                f"test-{kind}",
                root=root,
            )
            assert result.returncode == 0, result.stderr
            created.append(result.stdout.strip())

        result = run_cmd("rebuild-index", root=root)
        assert result.returncode == 0, result.stderr
        index = (root / "emergence" / "INDEX.md").read_text(encoding="utf-8")
        assert "INS-0001" in index
        assert "SYN-0001" in index
        assert "IDEA-0001" in index
        assert "EXP-0001" in index
        assert "PROMO-0001" in index
        assert "Test idea summary" in index
        assert len(created) == 5


def test_validate_rejects_unresolved_placeholders() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        bad = root / "emergence" / "insights" / "INS-0001-bad.md"
        bad.write_text((ROOT / "emergence" / "templates" / "INSIGHT_TEMPLATE.md").read_text(encoding="utf-8"), encoding="utf-8")

        result = run_cmd("validate", root=root)

        assert result.returncode == 1
        assert "unresolved template placeholders" in result.stderr


def test_validate_accepts_created_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        create = run_cmd(
            "create",
            "idea",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "A useful command center idea",
            "--date",
            "2026-06-29",
            root=root,
        )
        assert create.returncode == 0, create.stderr

        result = run_cmd("validate", root=root)

        assert result.returncode == 0, result.stderr
        assert "OK emergence artifacts valid (1 checked)" in result.stdout


def test_created_artifact_uses_compact_sections_and_wikilinks_paths() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        (root / "emergence" / "README.md").write_text("# Emergence\n", encoding="utf-8")

        create = run_cmd(
            "create",
            "insight",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "Capture uses MAP_System/emergence/README.md",
            "--date",
            "2026-06-29",
            "--slug",
            "compact-link",
            root=root,
        )

        assert create.returncode == 0, create.stderr
        path = root.parent / create.stdout.strip()
        text = path.read_text(encoding="utf-8")
        assert "- obs: Capture uses [[emergence/README]]" in text
        assert "What did the agent notice?" not in text


def test_rebuild_index_compacts_resolvable_emergence_references() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        insight = run_cmd(
            "create",
            "insight",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "Seed insight",
            "--date",
            "2026-06-29",
            "--slug",
            "seed",
            root=root,
        )
        assert insight.returncode == 0, insight.stderr

        idea = run_cmd(
            "create",
            "idea",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "Follow INS-0001 with a deliberately long index-facing summary that should stay compact by pointing to the full artifact",
            "--date",
            "2026-06-29",
            "--slug",
            "follow",
            root=root,
        )
        assert idea.returncode == 0, idea.stderr

        rebuild = run_cmd("rebuild-index", root=root)
        assert rebuild.returncode == 0, rebuild.stderr
        index = (root / "emergence" / "INDEX.md").read_text(encoding="utf-8")
        assert "[[emergence/insights/INS-0001-seed]]" in index
        assert "..." in index
        assert "pointing to the full artifact" not in index
        assert "- mode: compact registry" in index


def test_reference_compaction_prefers_full_markdown_paths_over_embedded_ids() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        insight = run_cmd(
            "create",
            "insight",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "Seed insight",
            "--date",
            "2026-06-29",
            "--slug",
            "seed",
            root=root,
        )
        assert insight.returncode == 0, insight.stderr

        idea = run_cmd(
            "create",
            "idea",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "See emergence/insights/INS-0001-seed.md",
            "--date",
            "2026-06-29",
            "--slug",
            "path-ref",
            root=root,
        )
        assert idea.returncode == 0, idea.stderr
        path = root.parent / idea.stdout.strip()
        text = path.read_text(encoding="utf-8")
        assert "[[emergence/insights/INS-0001-seed]]" in text
        assert "[[emergence/insights/INS-0001-seed]]-seed.md" not in text


def test_reference_compaction_resolves_bare_emergence_artifact_filenames() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        insight = run_cmd(
            "create",
            "insight",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "Seed insight",
            "--date",
            "2026-06-29",
            "--slug",
            "seed",
            root=root,
        )
        assert insight.returncode == 0, insight.stderr

        idea = run_cmd(
            "create",
            "idea",
            "--project",
            "MAP",
            "--owner",
            "codex-test",
            "--summary",
            "See INS-0001-seed.md",
            "--date",
            "2026-06-29",
            "--slug",
            "bare-file-ref",
            root=root,
        )
        assert idea.returncode == 0, idea.stderr
        path = root.parent / idea.stdout.strip()
        text = path.read_text(encoding="utf-8")
        assert "[[emergence/insights/INS-0001-seed]]" in text
        assert "[[emergence/insights/INS-0001-seed]]-seed.md" not in text


def test_compact_existing_record_dry_run_apply_and_idempotent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        path = root / "emergence" / "insights" / "INS-0001-prose.md"
        path.write_text(
            "\n".join([
                "# Insight Record",
                "",
                "Insight ID: INS-0001",
                "Project: MAP",
                "Related task: NONE",
                "Detected by: codex-test",
                "Date: 2026-07-14",
                "Status: RAW",
                "",
                "## Short description",
                "",
                "A long observation that should become a labeled bullet.",
                "",
                "## Recommended next action",
                "",
                "Choose one:",
                "",
                "- [ ] Ignore — not worth preserving",
                "- [x] Create idea card — needs more development",
                "",
                "## Notes",
                "",
                "-",
                "",
            ]),
            encoding="utf-8",
        )
        original = path.read_text(encoding="utf-8")

        dry_run = run_cmd("compact", "INS-0001", root=root)
        assert dry_run.returncode == 0, dry_run.stderr
        assert "would-change" in dry_run.stdout
        assert path.read_text(encoding="utf-8") == original

        apply = run_cmd("compact", "INS-0001", "--apply", root=root)
        assert apply.returncode == 0, apply.stderr
        text = path.read_text(encoding="utf-8")
        assert "- obs: A long observation that should become a labeled bullet." in text
        assert "- [x] Create idea card" in text
        assert "Choose one:" not in text
        assert "## Notes\n\n- note:" in text

        second = run_cmd("compact", "INS-0001", "--apply", root=root)
        assert second.returncode == 0, second.stderr
        assert "unchanged" in second.stdout


def test_compact_all_active_skips_closed_records() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        active = root / "emergence" / "ideas" / "IDEA-0001-active.md"
        active.write_text(
            "# Idea Card\n\n"
            "Idea ID: IDEA-0001\nProject: MAP\nSource insight or synthesis: NONE\n"
            "Owner: codex-test\nDate: 2026-07-14\nStatus: CANDIDATE\n\n"
            "## Idea\n\nNeeds compacting.\n",
            encoding="utf-8",
        )
        closed = root / "emergence" / "ideas" / "IDEA-0002-closed.md"
        closed.write_text(
            "# Idea Card\n\n"
            "Idea ID: IDEA-0002\nProject: MAP\nSource insight or synthesis: NONE\n"
            "Owner: codex-test\nDate: 2026-07-14\nStatus: REJECTED\n\n"
            "## Idea\n\nDo not compact.\n",
            encoding="utf-8",
        )

        result = run_cmd("compact", "--all-active", "--apply", root=root)
        assert result.returncode == 0, result.stderr
        assert "- idea: Needs compacting." in active.read_text(encoding="utf-8")
        assert "Do not compact." in closed.read_text(encoding="utf-8")
        assert "- idea: Do not compact." not in closed.read_text(encoding="utf-8")


def test_compact_synthesis_piece_sections() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        path = root / "emergence" / "synthesis" / "SYN-0001-pieces.md"
        path.write_text(
            "# Synthesis Note\n\n"
            "Synthesis ID: SYN-0001\nProject: MAP\nRelated insights:\n- INS-0001\n\n"
            "Date: 2026-07-14\nCreated by: codex-test\nStatus: CLARIFIED\n\n"
            "## Pieces being combined\n\n"
            "### Piece A\n\n"
            "First long piece.\n\n"
            "### Piece B\n\n"
            "Second long piece.\n",
            encoding="utf-8",
        )

        result = run_cmd("compact", "SYN-0001", "--apply", root=root)
        assert result.returncode == 0, result.stderr
        text = path.read_text(encoding="utf-8")
        assert "### Piece A\n\n- a: First long piece." in text
        assert "### Piece B\n\n- b: Second long piece." in text

        second = run_cmd("compact", "SYN-0001", "--apply", root=root)
        assert second.returncode == 0, second.stderr
        assert "unchanged" in second.stdout


def test_short_lab_contract() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        insight = run_cmd(
            "insight",
            "Short capture text",
            "--owner",
            "codex-test",
            "--related-task",
            "TASK-X",
            root=root,
        )
        assert insight.returncode == 0, insight.stderr
        idea = run_cmd(
            "idea",
            "Short idea text",
            "--owner",
            "codex-test",
            "--source",
            "INS-0001",
            root=root,
        )
        assert idea.returncode == 0, idea.stderr
        promote = run_cmd(
            "promote",
            "IDEA-0001",
            "--owner",
            "command-center",
            "--summary",
            "Promote short idea",
            root=root,
        )
        assert promote.returncode == 0, promote.stderr

        listing = run_cmd("list", root=root)
        assert listing.returncode == 0, listing.stderr
        assert "Short capture text" in listing.stdout
        assert "Short idea text" in listing.stdout
        assert "Promote short idea" in listing.stdout

        validate = run_cmd("validate", root=root)
        assert validate.returncode == 0, validate.stderr


def seed_coverage_record(root: Path, *, kind: str, slug: str, date: str, status: str | None = None) -> None:
    args = [
        "create",
        kind,
        "--project",
        "MAP",
        "--owner",
        "codex-test",
        "--summary",
        f"Coverage {slug}",
        "--date",
        date,
        "--slug",
        slug,
    ]
    if status:
        args += ["--status", status]
    result = run_cmd(*args, root=root)
    assert result.returncode == 0, result.stderr


def test_coverage_flags_never_reviewed_open_records() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        seed_coverage_record(root, kind="insight", slug="old-open", date="2020-01-01")

        result = run_cmd("coverage", "--json", root=root)
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["overdue"] == 1
        assert payload["never_reviewed"] == 1
        entry = payload["entries"][0]
        assert entry["artifact_id"] == "INS-0001"
        assert entry["never_reviewed"] is True
        assert entry["review_count"] == 0
        assert entry["age_days"] > 14


def test_coverage_skips_closed_records() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        seed_coverage_record(
            root, kind="insight", slug="closed", date="2020-01-01", status="PROMOTED"
        )

        result = run_cmd("coverage", "--json", root=root)
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["open_records"] == 0
        assert payload["overdue"] == 0


def test_coverage_mark_reviewed_clears_debt_and_counts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        seed_coverage_record(root, kind="insight", slug="old-open", date="2020-01-01")

        marked = run_cmd(
            "coverage", "--mark-reviewed", "INS-0001", "--reviewer", "claude-test", root=root
        )
        assert marked.returncode == 0, marked.stderr

        result = run_cmd("coverage", "--json", root=root)
        payload = json.loads(result.stdout)
        assert payload["overdue"] == 0, "record reviewed today must not be overdue"

        state = json.loads((root / "emergence" / "coverage.json").read_text(encoding="utf-8"))
        record = state["records"]["INS-0001"]
        assert record["review_count"] == 1
        assert record["reviewed_by"] == "claude-test"

        # Reviewing again increments rather than overwriting the count.
        run_cmd("coverage", "--mark-reviewed", "INS-0001", root=root)
        state = json.loads((root / "emergence" / "coverage.json").read_text(encoding="utf-8"))
        assert state["records"]["INS-0001"]["review_count"] == 2


def test_coverage_mark_reviewed_rejects_unknown_id() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        result = run_cmd("coverage", "--mark-reviewed", "INS-9999", root=root)
        assert result.returncode == 1
        assert "unknown emergence record" in result.stderr


def test_coverage_treats_unparseable_date_as_overdue() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        seed_coverage_record(root, kind="insight", slug="bad-date", date="2026-01-01")
        record = next((root / "emergence" / "insights").glob("*.md"))
        record.write_text(
            record.read_text(encoding="utf-8").replace("Date: 2026-01-01", "Date: sometime"),
            encoding="utf-8",
        )

        result = run_cmd("coverage", "--json", "--strict", root=root)
        assert result.returncode == 1, "strict must exit non-zero while records are overdue"
        payload = json.loads(result.stdout)
        assert payload["overdue"] == 1
        assert payload["entries"][0]["age_days"] is None


def test_coverage_closed_statuses_are_kind_aware() -> None:
    """Regression for soba's TASK review: the shared closed-status set is not a
    single ladder. COMPLETE/REVIEWED end an experiment but were absent from it,
    and APPROVED ends a promotion while sitting mid-ladder for an experiment."""
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        for slug, status in [("done", "COMPLETE"), ("checked", "REVIEWED"), ("mid", "APPROVED")]:
            seed_coverage_record(
                root, kind="experiment", slug=slug, date="2020-01-01", status=status
            )
        seed_coverage_record(
            root, kind="promotion", slug="signed", date="2020-01-01", status="APPROVED"
        )

        payload = json.loads(run_cmd("coverage", "--json", "--limit", "0", root=root).stdout)
        open_ids = {entry["artifact_id"] for entry in payload["entries"]}

        assert payload["open_records"] == 1, (
            "only the mid-ladder APPROVED experiment should still accrue debt; "
            f"got {payload['open_records']} open: {open_ids}"
        )
        assert open_ids == {"EXP-0003"}, open_ids


def test_coverage_interval_is_configurable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = seed_emergence_tree(Path(tmp))
        today = datetime.now(timezone.utc).date()
        seed_coverage_record(
            root, kind="idea", slug="recent", date=(today - timedelta(days=5)).isoformat()
        )

        default = json.loads(run_cmd("coverage", "--json", root=root).stdout)
        assert default["overdue"] == 0, "5-day-old record is inside the default 14-day interval"

        tightened = json.loads(
            run_cmd("coverage", "--json", "--interval-days", "3", root=root).stdout
        )
        assert tightened["overdue"] == 1


def main() -> int:
    for test in [
        test_create_all_kinds_and_rebuild_index,
        test_validate_rejects_unresolved_placeholders,
        test_validate_accepts_created_artifact,
        test_created_artifact_uses_compact_sections_and_wikilinks_paths,
        test_rebuild_index_compacts_resolvable_emergence_references,
        test_reference_compaction_prefers_full_markdown_paths_over_embedded_ids,
        test_reference_compaction_resolves_bare_emergence_artifact_filenames,
        test_compact_existing_record_dry_run_apply_and_idempotent,
        test_compact_all_active_skips_closed_records,
        test_compact_synthesis_piece_sections,
        test_short_lab_contract,
        test_coverage_flags_never_reviewed_open_records,
        test_coverage_skips_closed_records,
        test_coverage_mark_reviewed_clears_debt_and_counts,
        test_coverage_mark_reviewed_rejects_unknown_id,
        test_coverage_treats_unparseable_date_as_overdue,
        test_coverage_closed_statuses_are_kind_aware,
        test_coverage_interval_is_configurable,
    ]:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
