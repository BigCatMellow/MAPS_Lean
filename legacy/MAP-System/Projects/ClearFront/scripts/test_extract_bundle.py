#!/usr/bin/env python3
"""Regression tests for extract_bundle.py's security/correctness fixes.

Covers the REQUIRED findings from TASK-207's review
(artifacts/reviews/task207-review-lilo.md, codex-lab-lilo):
- a non-UUID manifest key must not be able to write outside assets_dir
- a stale file left in a previous output dir must not survive a rerun
- an unresolved ext_resource / leftover placeholder must fail closed
  unless --allow-incomplete is passed

Run: python3 scripts/test_extract_bundle.py
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "extract_bundle.py"


def make_bundle(path: Path, manifest: dict, ext_resources: list, template: str) -> None:
    html = (
        "<!DOCTYPE html><html><body>\n"
        '<script type="__bundler/manifest">' + json.dumps(manifest) + "</script>\n"
        '<script type="__bundler/ext_resources">' + json.dumps(ext_resources) + "</script>\n"
        '<script type="__bundler/template">' + json.dumps(template) + "</script>\n"
        "</body></html>"
    )
    path.write_text(html, encoding="utf-8")


def run(source: Path, out: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--source", str(source), "--out", str(out), *(extra_args or [])],
        capture_output=True,
        text=True,
    )


def test_path_traversal_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / "bundle.html"
        payload = base64.b64encode(b"evil").decode()
        make_bundle(
            source,
            manifest={"../../escaped": {"mime": "image/png", "compressed": False, "data": payload}},
            ext_resources=[],
            template="<html><head></head><body>../../escaped</body></html>",
        )
        out = td / "out"
        result = run(source, out)
        assert result.returncode != 0, f"expected failure, got 0. stdout={result.stdout}"
        escaped = td / "escaped.png"
        assert not escaped.exists(), "traversal wrote outside assets_dir"
        print("PASS test_path_traversal_rejected")


def test_stale_output_removed() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / "bundle.html"
        uuid = "11111111-2222-3333-4444-555555555555"
        payload = base64.b64encode(b"real-asset").decode()
        make_bundle(
            source,
            manifest={uuid: {"mime": "image/png", "compressed": False, "data": payload}},
            ext_resources=[{"id": "thing", "uuid": uuid}],
            template=f"<html><head></head><body>{uuid}</body></html>",
        )
        out = td / "out"
        assets_dir = out / "assets"
        assets_dir.mkdir(parents=True)
        stale = assets_dir / "stale.bin"
        stale.write_bytes(b"leftover from a previous bundle")

        result = run(source, out)
        assert result.returncode == 0, f"expected success, got {result.returncode}. stdout={result.stdout}\nstderr={result.stderr}"
        assert not stale.exists(), "stale file survived a rerun"
        print("PASS test_stale_output_removed")


def test_incomplete_fails_closed_by_default() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / "bundle.html"
        uuid = "11111111-2222-3333-4444-555555555555"
        payload = base64.b64encode(b"real-asset").decode()
        # ext_resources references a uuid that isn't in the manifest.
        make_bundle(
            source,
            manifest={uuid: {"mime": "image/png", "compressed": False, "data": payload}},
            ext_resources=[{"id": "thing", "uuid": "99999999-9999-9999-9999-999999999999"}],
            template=f"<html><head></head><body>{uuid}</body></html>",
        )
        out = td / "out"

        result = run(source, out)
        assert result.returncode != 0, f"expected failure, got 0. stdout={result.stdout}"
        assert not (out / "index.html").exists(), "incomplete baseline was emitted without --allow-incomplete"

        result2 = run(source, out, extra_args=["--allow-incomplete"])
        assert result2.returncode == 0, f"expected success with --allow-incomplete, got {result2.returncode}"
        assert (out / "index.html").exists()
        print("PASS test_incomplete_fails_closed_by_default")


def snapshot_tree(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_failed_rerun_preserves_prior_output() -> None:
    """TASK-207 rereview REQUIRED finding: a failed rerun into an existing
    valid output must leave that output entirely byte-identical, not a
    mixed old-index/new-assets tree."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        uuid = "11111111-2222-3333-4444-555555555555"
        payload = base64.b64encode(b"real-asset").decode()

        good = td / "good.html"
        make_bundle(
            good,
            manifest={uuid: {"mime": "image/png", "compressed": False, "data": payload}},
            ext_resources=[{"id": "thing", "uuid": uuid}],
            template=f"<html><head></head><body>{uuid}</body></html>",
        )
        out = td / "out"
        result = run(good, out)
        assert result.returncode == 0, f"setup extraction failed: {result.stdout}\n{result.stderr}"
        before = snapshot_tree(out)
        assert before, "setup extraction produced no output"

        bad = td / "bad.html"
        other_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        make_bundle(
            bad,
            manifest={other_uuid: {"mime": "image/png", "compressed": False, "data": payload}},
            ext_resources=[{"id": "thing", "uuid": "99999999-9999-9999-9999-999999999999"}],
            template=f"<html><head></head><body>{other_uuid}</body></html>",
        )
        result2 = run(bad, out)
        assert result2.returncode != 0, f"expected failure, got 0. stdout={result2.stdout}"
        after = snapshot_tree(out)
        assert after == before, (
            "failed rerun modified the prior output tree:\n"
            f"before={sorted(before)}\nafter={sorted(after)}"
        )
        leftovers = [p for p in out.parent.iterdir() if p.name.startswith(f".{out.name}-staging-")]
        assert not leftovers, f"staging directory leaked: {leftovers}"
        print("PASS test_failed_rerun_preserves_prior_output")


def test_successful_rerun_replaces_output() -> None:
    """Complement to the atomicity test: a successful rerun with a different
    bundle must fully replace the generated outputs (no merging)."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out = td / "out"
        for i, uuid in enumerate(
            ["11111111-2222-3333-4444-555555555555", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"]
        ):
            bundle = td / f"bundle{i}.html"
            payload = base64.b64encode(f"asset-{i}".encode()).decode()
            make_bundle(
                bundle,
                manifest={uuid: {"mime": "image/png", "compressed": False, "data": payload}},
                ext_resources=[{"id": "thing", "uuid": uuid}],
                template=f"<html><head></head><body>{uuid}</body></html>",
            )
            result = run(bundle, out)
            assert result.returncode == 0, f"extraction {i} failed: {result.stdout}\n{result.stderr}"
        assets = sorted(p.name for p in (out / "assets").iterdir())
        assert assets == ["aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.png"], (
            f"old generated assets survived a successful rerun: {assets}"
        )
        print("PASS test_successful_rerun_replaces_output")


def main() -> None:
    test_path_traversal_rejected()
    test_stale_output_removed()
    test_incomplete_fails_closed_by_default()
    test_failed_rerun_preserves_prior_output()
    test_successful_rerun_replaces_output()
    print("ALL PASS")


if __name__ == "__main__":
    main()
