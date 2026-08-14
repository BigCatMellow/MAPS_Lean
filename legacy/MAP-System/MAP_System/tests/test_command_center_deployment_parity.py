#!/usr/bin/env python3
"""TASK-306: focused tests for MAP_System/scripts/command_center_version.py.

Proves the deployment-parity manifest correctly identifies missing, changed,
and extra managed files; leaves runtime/host-rendered/legacy-out-of-scope
files unflagged; and that the live Biggie bundle currently matches the
repo-owned installer template byte-for-byte for every managed file.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import command_center_version as ccv  # noqa: E402

LIVE_BUNDLE_ROOT = Path("/home/mellow/Projects/CommandCenterUI")
TEMPLATE_BUNDLE_ROOT = ROOT / "templates" / "install" / "command-center-ui"


def _make_minimal_bundle(root: Path) -> None:
    for rel in ccv.MANAGED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"placeholder content for {rel}\n", encoding="utf-8")


def test_generate_verify_round_trip_clean() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        manifest = ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))
        assert len(manifest["managed_files"]) == len(ccv.MANAGED_FILES)
        issues = ccv.verify(root, manifest)
        assert issues == [], issues


def test_verify_detects_changed_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        manifest = ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))
        (root / "src" / "orchestrator.js").write_text("tampered\n", encoding="utf-8")
        issues = ccv.verify(root, manifest)
        assert any(i.startswith("changed: src/orchestrator.js") for i in issues), issues


def test_verify_detects_missing_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        manifest = ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))
        (root / "src" / "orchestrator.js").unlink()
        issues = ccv.verify(root, manifest)
        assert any(i == "missing: src/orchestrator.js" for i in issues), issues


def test_verify_detects_extra_unaccounted_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        manifest = ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))
        (root / "src" / "mystery.js").write_text("surprise\n", encoding="utf-8")
        issues = ccv.verify(root, manifest)
        assert any(i == "extra managed (unaccounted-for file): src/mystery.js" for i in issues), issues


def test_generate_refuses_with_unaccounted_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        (root / "src" / "mystery.js").write_text("surprise\n", encoding="utf-8")
        try:
            ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))
        except ccv.VersionError as exc:
            assert "mystery.js" in str(exc)
        else:
            raise AssertionError("generate() should refuse with an unaccounted-for file present")


def test_excluded_runtime_and_legacy_files_never_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_minimal_bundle(root)
        manifest = ccv.generate(root, "test-v1", source_host="test-host", source_path=str(root))

        (root / "runtime").mkdir()
        (root / "runtime" / "gate-audit.jsonl").write_text("{}\n", encoding="utf-8")
        (root / "app" / "__pycache__").mkdir(parents=True)
        (root / "app" / "__pycache__" / "server.cpython-312.pyc").write_bytes(b"\x00")
        (root / "CommandCenterUI.desktop").write_text("[Desktop Entry]\nExec=/host/path\n", encoding="utf-8")
        (root / "src" / "chat.html").write_text("<html></html>\n", encoding="utf-8")
        (root / "_legacy-ui-removed-2026-07-29").mkdir()
        (root / "_legacy-ui-removed-2026-07-29" / "chat.js").write_text("old\n", encoding="utf-8")

        issues = ccv.verify(root, manifest)
        assert issues == [], issues


def test_live_biggie_bundle_matches_template_manifest() -> None:
    """The actual point of TASK-306: prove the repo-owned installer template
    is byte-for-byte identical to the live-tested Biggie source, for every
    managed file, using the real checked-in manifest."""
    if not LIVE_BUNDLE_ROOT.is_dir():
        print(f"SKIP (no live bundle at {LIVE_BUNDLE_ROOT} on this host)")
        return
    manifest_path = TEMPLATE_BUNDLE_ROOT / "version.json"
    assert manifest_path.is_file(), f"missing manifest: {manifest_path}"
    manifest = ccv.load_manifest(manifest_path)

    template_issues = ccv.verify(TEMPLATE_BUNDLE_ROOT, manifest)
    assert template_issues == [], ("template drifted from its own manifest", template_issues)

    live_issues = ccv.verify(LIVE_BUNDLE_ROOT, manifest)
    assert live_issues == [], ("live Biggie bundle diverged from the template manifest", live_issues)


def main() -> int:
    tests = [
        test_generate_verify_round_trip_clean,
        test_verify_detects_changed_file,
        test_verify_detects_missing_file,
        test_verify_detects_extra_unaccounted_file,
        test_generate_refuses_with_unaccounted_files,
        test_excluded_runtime_and_legacy_files_never_flagged,
        test_live_biggie_bundle_matches_template_manifest,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
