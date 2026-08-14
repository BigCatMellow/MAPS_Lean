#!/usr/bin/env python3
"""Reproducible extractor for the ClearFront self-extracting HTML bundle.

The bundle (source/game-card-combat-effects/Clearfront.html) is a generated
"artifact bundler" page, not editable source: a small loader script unpacks
a JSON __bundler/manifest (UUID -> base64/gzip asset) and a JSON
__bundler/template (the actual game HTML, with UUID placeholders) into
blob: URLs at runtime. See TASK-207 and
handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md.

This script performs the same substitution statically and ahead of time:
every manifest asset is decoded to a real file under baseline/assets/, and
every UUID placeholder in the template is replaced with a relative path to
that file, producing a plain, directly-editable baseline/index.html.

Usage:
    python3 extract_bundle.py [--source PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

# Everything the extractor generates under --out. Staged runs replace exactly
# these paths and never touch anything else living in the output directory.
GENERATED_OUTPUTS = ("assets", "index.html", "extraction_report.txt")

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

DEFAULT_SOURCE = (
    Path(__file__).resolve().parent.parent
    / "source"
    / "game-card-combat-effects"
    / "Clearfront.html"
)
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "baseline"

MIME_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "font/woff2": ".woff2",
    "font/woff": ".woff",
    "font/ttf": ".ttf",
    "application/font-woff2": ".woff2",
    "application/font-woff": ".woff",
    "text/css": ".css",
    "application/javascript": ".js",
    "text/javascript": ".js",
    "application/json": ".json",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/ogg": ".ogg",
    "video/mp4": ".mp4",
}


def guess_ext(mime: str) -> str:
    return MIME_EXT.get(mime.lower(), ".bin")


def extract_script(html: str, script_type: str) -> str:
    pattern = r'<script type="' + re.escape(script_type) + r'">(.*?)</script>'
    match = re.search(pattern, html, re.S)
    if not match:
        raise ValueError(f"missing <script type={script_type!r}> block in bundle")
    return match.group(1)


def safe_asset_path(assets_dir: Path, uuid: str, ext: str) -> Path:
    """Resolve the on-disk path for one manifest asset, refusing anything
    that would escape assets_dir.

    The manifest key becomes a filename; if it can be anything other than a
    canonical UUID, a crafted key such as "../../escaped" writes outside
    assets_dir (TASK-207 review, codex-lab-lilo, REQUIRED finding). The
    manifest's own format contract is UUID keys, so validate that directly
    rather than trying to sanitize an arbitrary string.
    """
    if not UUID_RE.match(uuid):
        raise ValueError(f"manifest key is not a canonical UUID: {uuid!r}")
    candidate = (assets_dir / f"{uuid}{ext}").resolve()
    if not candidate.is_relative_to(assets_dir.resolve()):
        raise ValueError(f"resolved asset path escapes assets_dir: {candidate}")
    return candidate


def commit_outputs(staging: Path, out: Path) -> None:
    """Move the staged generated outputs into place, replacing prior ones.

    Called only after the staged extraction fully validated. Replacing each
    generated path wholesale (never merging) keeps the output a pure function
    of the bundle; doing it from a completed staging tree means a failure at
    any earlier point leaves the previous known-good baseline byte-identical
    (TASK-207 rereview, codex-lab-lilo, REQUIRED finding: a failed rerun must
    not leave a mixed old-index/new-assets tree).
    """
    out.mkdir(parents=True, exist_ok=True)
    for name in GENERATED_OUTPUTS:
        src = staging / name
        dst = out / name
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        elif dst.exists() or dst.is_symlink():
            dst.unlink()
        shutil.move(str(src), str(dst))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help=(
            "Do not fail on an unresolved ext_resource, a leftover raw UUID, "
            "or a missing <head> tag; emit the incomplete baseline with a "
            "warning instead. Off by default: an incomplete baseline is a "
            "silent content-loss bug, not a normal outcome (TASK-207 review, "
            "codex-lab-lilo, RECOMMENDED finding)."
        ),
    )
    args = parser.parse_args()

    html = args.source.read_text(encoding="utf-8")

    manifest = json.loads(extract_script(html, "__bundler/manifest"))
    ext_resources = json.loads(extract_script(html, "__bundler/ext_resources"))
    template = json.loads(extract_script(html, "__bundler/template"))

    # Stage the whole extraction in a fresh sibling directory and only swap
    # it into --out after every validation passes. A failed run must leave
    # any prior baseline byte-identical, never a mixed tree (TASK-207
    # rereview, codex-lab-lilo, REQUIRED finding). The fresh staging dir also
    # keeps the output a pure function of the bundle: stale files from an
    # earlier run can never survive into the committed result (first-review
    # REQUIRED finding).
    args.out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{args.out.name}-staging-", dir=args.out.parent))
    try:
        run_extraction(args, manifest, ext_resources, template, staging)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def run_extraction(args, manifest, ext_resources, template: str, staging: Path) -> None:
    assets_dir = staging / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    uuid_to_relpath: dict[str, str] = {}
    report_lines: list[str] = []
    report_lines.append(f"source: {args.source}")
    report_lines.append(f"manifest entries: {len(manifest)}")

    for uuid, entry in manifest.items():
        mime = entry["mime"]
        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = gzip.decompress(raw)
        ext = guess_ext(mime)
        dest = safe_asset_path(assets_dir, uuid, ext)
        dest.write_bytes(raw)
        relpath = f"assets/{dest.name}"
        uuid_to_relpath[uuid] = relpath
        digest = hashlib.sha256(raw).hexdigest()[:12]
        report_lines.append(
            f"  {uuid}  mime={mime}  compressed={bool(entry.get('compressed'))}"
            f"  bytes={len(raw)}  sha256[:12]={digest}  -> {relpath}"
        )

    report_lines.append(f"ext_resources entries: {len(ext_resources)}")
    resource_map: dict[str, str] = {}
    incomplete_reasons: list[str] = []
    for entry in ext_resources:
        uuid = entry["uuid"]
        rid = entry["id"]
        if uuid in uuid_to_relpath:
            resource_map[rid] = uuid_to_relpath[uuid]
            report_lines.append(f"  id={rid!r} -> uuid={uuid} -> {uuid_to_relpath[uuid]}")
        else:
            msg = f"ext_resource id={rid!r} references unknown uuid={uuid}"
            report_lines.append(f"  WARNING: {msg}")
            incomplete_reasons.append(msg)

    # Mirror the loader's substitution: replace every literal UUID occurrence
    # in the template text with the asset's relative path (string-level,
    # matching template.split(uuid).join(blobUrl) in the bundle's own code).
    for uuid, relpath in uuid_to_relpath.items():
        template = template.replace(uuid, relpath)

    # A resolved reference reads "assets/<uuid>.ext" by construction, so the
    # UUID substring is always still present in the file's own path — only
    # flag a UUID that appears *without* the "assets/" prefix immediately
    # before it, i.e. one that was never substituted.
    remaining_uuids = [
        u for u in uuid_to_relpath
        if re.search(r"(?<!assets/)" + re.escape(u), template)
    ]
    if remaining_uuids:
        msg = f"{len(remaining_uuids)} UUID(s) still present after substitution: {remaining_uuids}"
        report_lines.append(f"WARNING: {msg}")
        incomplete_reasons.append(msg)
    else:
        report_lines.append("OK: zero raw manifest UUIDs remain in the emitted HTML")

    # Mirror the loader's SRI/CORS strip for blob-origin scripts.
    template = re.sub(r'\s+integrity="[^"]*"', "", template, flags=re.I)
    template = re.sub(r'\s+crossorigin="[^"]*"', "", template, flags=re.I)

    # Mirror the loader's window.__resources injection (id -> relative path
    # instead of id -> blob URL, since this is a static file, not a blob).
    resource_script = (
        "<script>window.__resources = "
        + json.dumps(resource_map).replace("</", "<\\/")
        + ";</script>"
    )
    head_match = re.search(r"<head[^>]*>", template, re.I)
    if head_match:
        i = head_match.end()
        template = template[:i] + resource_script + template[i:]
    else:
        msg = "no <head> tag found; window.__resources not injected"
        report_lines.append(f"WARNING: {msg}")
        incomplete_reasons.append(msg)

    if incomplete_reasons and not args.allow_incomplete:
        report_lines.append(
            f"FAILED: {len(incomplete_reasons)} incompleteness issue(s) found; "
            "refusing to emit a silently-lossy baseline. Re-run with "
            "--allow-incomplete to emit it anyway. No output was committed; "
            "any prior baseline under --out is untouched."
        )
        print("\n".join(report_lines))
        raise SystemExit(1)

    (staging / "index.html").write_text(template, encoding="utf-8")
    report_lines.append(f"emitted: {args.out / 'index.html'}  bytes={len(template)}")
    (staging / "extraction_report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    # Everything validated in staging; swap the generated outputs into place.
    commit_outputs(staging, args.out)
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
