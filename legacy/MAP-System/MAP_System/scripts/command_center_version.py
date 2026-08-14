#!/usr/bin/env python3
"""Deterministic version/parity manifest for the CommandCenterUI managed bundle.

TASK-306: Biggie (KUDU) is the live-tested source for the CommandCenterUI
redesign. This script generates and verifies a checksum manifest for the
*managed* program files only -- never host credentials, MAP authority
config, hcom/runtime state, logs, caches, or unrelated project content.

Three kinds of files exist under a CommandCenterUI bundle root:

- MANAGED_FILES: the versioned program surface. Checked byte-for-byte.
- EXCLUDED_RUNTIME_PATTERNS: host-local state generated at run time
  (runtime/, __pycache__/). Never part of the manifest, never flagged.
- EXCLUDED_HOST_RENDERED: files that legitimately differ per host by design
  (CommandCenterUI.desktop's Exec= line points at an absolute install path).
  Present on disk, deliberately excluded from checksum comparison.
- EXCLUDED_LEGACY_OUT_OF_SCOPE: pre-existing template content TASK-306 did
  not touch (the old chat.html/app.html/index.html/studio.html UI and its
  assets). Left in place rather than deleted (see AGENTS.md file-ownership:
  task output_paths did not include removing them); explicitly excluded so
  the "extra managed file" check does not treat pre-existing, undeclared
  content as a regression.

Anything found under a bundle root that is not in one of these four buckets
is a real "extra managed file" and fails verification -- that is the point:
an unaccounted-for new file is exactly the kind of silent drift this script
exists to catch.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE_ROOT = ROOT / "templates" / "install" / "command-center-ui"
DEFAULT_MANIFEST = DEFAULT_BUNDLE_ROOT / "version.json"

MANAGED_FILES = (
    "AGENTS.md",
    ".gitignore",
    "launch-command-center-ui.sh",
    "run-command-center-app.sh",
    "README.md",
    "app/server.py",
    "app/window.py",
    "src/bcmagent.svg",
    "src/orchestrator.css",
    "src/orchestrator.html",
    "src/orchestrator.js",
)

EXCLUDED_RUNTIME_PATTERNS = (
    "runtime/*",
    "runtime/**",
    "**/__pycache__/*",
    "__pycache__/*",
    "*.pyc",
    # Live-Biggie-only: the retired pre-orchestrator UI, moved aside (not
    # deleted) on 2026-07-29 rather than committed to the template. Host-
    # local housekeeping, not part of the managed bundle on either side.
    "_legacy-ui-removed-2026-07-29/*",
    "_legacy-ui-removed-2026-07-29/**",
)

# CommandCenterUI.desktop's Exec= line is rendered per-install (an absolute
# path on the target host); the template's own copy is the portable form.
# Both are legitimate and never expected to be byte-identical.
EXCLUDED_HOST_RENDERED = (
    "CommandCenterUI.desktop",
)

# Pre-existing template content from before TASK-306; not part of the live
# Biggie canonical bundle and not in TASK-306's output_paths. Left in place,
# not checked. A future task can retire these deliberately.
EXCLUDED_LEGACY_OUT_OF_SCOPE = (
    "src/app.html",
    "src/app.js",
    "src/app-live.css",
    "src/app-live.js",
    "src/assets/pasted-1782846261949-0.png",
    "src/assets/pasted-1782846275994-0.png",
    "src/assets/pasted-1782846286125-0.png",
    "src/chat.css",
    "src/chat.html",
    "src/chat.js",
    "src/index.html",
    "src/studio.css",
    "src/studio.html",
    "src/studio.js",
    "src/styles.css",
)

ALL_EXCLUDED_LITERAL = set(EXCLUDED_HOST_RENDERED) | set(EXCLUDED_LEGACY_OUT_OF_SCOPE)


class VersionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def is_runtime_excluded(rel_path: str) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in EXCLUDED_RUNTIME_PATTERNS)


def compute_managed_checksums(bundle_root: Path) -> dict[str, dict]:
    """Checksum every MANAGED_FILES entry under bundle_root. Raises if any is missing."""
    entries: dict[str, dict] = {}
    missing = []
    for rel in MANAGED_FILES:
        path = bundle_root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        entries[rel] = {"sha256": sha256_file(path), "size": path.stat().st_size}
    if missing:
        raise VersionError("managed files missing from bundle: " + ", ".join(sorted(missing)))
    return entries


def scan_unaccounted_files(bundle_root: Path) -> list[str]:
    """Any real file under bundle_root not in MANAGED_FILES, not runtime-excluded,
    and not in the literal excluded sets. A non-empty result is real drift:
    an untracked file appeared that this manifest does not know about."""
    managed = set(MANAGED_FILES)
    unaccounted = []
    for path in sorted(bundle_root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(bundle_root)).replace("\\", "/")
        if rel == "version.json":
            continue
        if rel in managed or rel in ALL_EXCLUDED_LITERAL:
            continue
        if is_runtime_excluded(rel):
            continue
        unaccounted.append(rel)
    return unaccounted


def generate(bundle_root: Path, version_id: str, *, source_host: str, source_path: str, now: datetime | None = None) -> dict:
    unaccounted = scan_unaccounted_files(bundle_root)
    if unaccounted:
        raise VersionError(
            "refusing to generate a manifest while unaccounted-for files exist: "
            + ", ".join(unaccounted)
            + " -- add them to MANAGED_FILES or an EXCLUDED_* set deliberately"
        )
    generated_at = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "version": version_id,
        "generated_at": generated_at,
        "source_host": source_host,
        "source_path": source_path,
        "managed_files": compute_managed_checksums(bundle_root),
        "excluded_runtime_patterns": list(EXCLUDED_RUNTIME_PATTERNS),
        "excluded_host_rendered": list(EXCLUDED_HOST_RENDERED),
        "excluded_legacy_out_of_scope": list(EXCLUDED_LEGACY_OUT_OF_SCOPE),
    }


def verify(bundle_root: Path, manifest: dict) -> list[str]:
    """Return a list of human-readable issues; empty list means clean parity.

    Covers all four required failure modes:
    - missing: a managed file the manifest expects is absent from bundle_root.
    - changed / stale installed: present but checksum differs (the same
      signal whether bundle_root is the source template or a deployed
      install that has drifted out of date).
    - extra managed: a real file exists under bundle_root that is not in
      MANAGED_FILES and not covered by any excluded set.
    """
    issues: list[str] = []
    manifest_files = manifest.get("managed_files", {})

    for rel in MANAGED_FILES:
        if rel not in manifest_files:
            issues.append(f"manifest missing entry for managed file: {rel}")
            continue
        path = bundle_root / rel
        if not path.is_file():
            issues.append(f"missing: {rel}")
            continue
        actual = sha256_file(path)
        expected = manifest_files[rel]["sha256"]
        if actual != expected:
            issues.append(f"changed: {rel} (expected sha256 {expected[:12]}…, got {actual[:12]}…)")

    for rel in manifest_files:
        if rel not in MANAGED_FILES:
            issues.append(f"manifest lists a file no longer in MANAGED_FILES: {rel}")

    unaccounted = scan_unaccounted_files(bundle_root)
    for rel in unaccounted:
        issues.append(f"extra managed (unaccounted-for file): {rel}")

    return issues


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Compute and write version.json from a bundle root")
    gen.add_argument("--bundle-root", type=Path, default=DEFAULT_BUNDLE_ROOT)
    gen.add_argument("--out", type=Path, default=DEFAULT_MANIFEST)
    gen.add_argument("--version", required=True, help="Version identifier, e.g. 2026-07-29-orchestrator-v1")
    gen.add_argument("--source-host", default="Biggie (KUDU, mellow@192.168.1.177)")
    gen.add_argument("--source-path", default="/home/mellow/Projects/CommandCenterUI")

    ver = sub.add_parser("verify", help="Verify a bundle root against a manifest")
    ver.add_argument("--bundle-root", type=Path, default=DEFAULT_BUNDLE_ROOT)
    ver.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)

    args = parser.parse_args(argv)

    if args.command == "generate":
        try:
            manifest = generate(
                args.bundle_root, args.version,
                source_host=args.source_host, source_path=args.source_path,
            )
        except VersionError as exc:
            print(f"generate failed: {exc}", file=sys.stderr)
            return 1
        write_manifest(args.out, manifest)
        print(f"wrote {args.out} ({len(manifest['managed_files'])} managed files)")
        return 0

    if args.command == "verify":
        if not args.manifest.is_file():
            print(f"manifest not found: {args.manifest}", file=sys.stderr)
            return 1
        manifest = load_manifest(args.manifest)
        issues = verify(args.bundle_root, manifest)
        if issues:
            print(f"PARITY FAILED ({len(issues)} issue(s)):", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            return 1
        print(f"OK: {args.bundle_root} matches manifest ({len(manifest.get('managed_files', {}))} managed files)")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
