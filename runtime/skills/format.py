from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Iterable


_FRONTMATTER_DELIMITER = "---"
_TOP_LEVEL_KEY = re.compile(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$")
_REQUIRED_KEYS = ("name", "description")
_BLOCK_SCALARS = {"|", "|-", "|+", ">", ">-", ">+"}

# SEC4 capability-declaration manifest
# (`work/notes/2026-09-01-sec4-capability-declaration-manifest-design.md`,
# `…-slice2-design.md`). A Skill bundle MAY carry a top-level `capabilities`
# sidecar: one capability token per line (`#` comments and blank lines ignored),
# drawn from the roadmap `04-agentic-security.md` s5.1 vocabulary. It is
# descriptive supply-chain metadata only -- it feeds the gate report (slice 1)
# and the `_select_skills` capability intersection (slice 2), and is never read
# by a runtime guard or written into `task_policy`. The parser lives here (not
# in `gate.py`) so both `SkillDescriptor` discovery and `gate.assess_skill` can
# consume it without an import cycle (`gate` imports `format`, never the reverse).
_CAPABILITY_MANIFEST_FILENAME = "capabilities"
_CAPABILITY_TOKENS = frozenset(
    {
        "filesystem-read",
        "filesystem-write",
        "shell",
        "network-read",
        "network-general",
        "github-read",
        "github-write",
        "database-read",
        "database-write",
        "process-stop",
        "external-deploy",
    }
)
_SECRET_USE_RE = re.compile(r"^secret-use:[a-z0-9][a-z0-9-]*$")

_MANIFEST_MALFORMED = object()


def _parse_capability_manifest(payload: bytes) -> "frozenset[str] | object":
    """Parse a `capabilities` sidecar into a set of declared tokens.

    Returns ``_MANIFEST_MALFORMED`` for non-UTF-8 content or any line that is
    not a blank/comment and not a recognized capability token. An empty result
    (file present, only comments) is a deliberate "declares nothing" assertion,
    distinct from an absent manifest.
    """

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return _MANIFEST_MALFORMED
    tokens: set[str] = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line in _CAPABILITY_TOKENS or _SECRET_USE_RE.match(line):
            tokens.add(line)
        else:
            return _MANIFEST_MALFORMED
    return frozenset(tokens)


def _declared_capabilities_tuple(payload: bytes | None) -> tuple[str, ...]:
    """Sorted declared-capability tuple for `SkillDescriptor`.

    ``()`` when the sidecar is absent OR malformed -- a malformed manifest is
    already `QUARANTINE`d by the slice-1 gate, so such a Skill never reaches the
    slice-2 intersection as non-DENY; representing it as "declares nothing" here
    is safe and keeps the descriptor field a plain string tuple.
    """

    if payload is None:
        return ()
    parsed = _parse_capability_manifest(payload)
    if parsed is _MANIFEST_MALFORMED:
        return ()
    return tuple(sorted(parsed))


class SkillParseError(ValueError):
    """A Skill directory cannot be represented safely by the v1 format layer."""


class SkillChangedError(SkillParseError):
    """A Skill changed after discovery and must be rediscovered before use."""


@dataclass(frozen=True, slots=True)
class SkillDescriptor:
    """Compact discovery metadata for one installed Skill.

    The descriptor intentionally contains no procedure body and no authority or
    approval state. `content_sha256` identifies the complete directory contents.
    """

    skill_id: str
    name: str
    description: str
    root: Path
    skill_file: Path
    content_sha256: str
    declared_metadata_keys: tuple[str, ...]
    resource_paths: tuple[str, ...]
    script_paths: tuple[str, ...]
    reference_paths: tuple[str, ...]
    asset_paths: tuple[str, ...]
    example_paths: tuple[str, ...]
    # SEC4 slice 2: sorted tokens from the optional `capabilities` sidecar
    # (`()` when absent or malformed). Descriptive metadata, not authority.
    declared_capabilities: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SkillDocument:
    """Activated Skill procedure paired with the descriptor it was loaded from."""

    descriptor: SkillDescriptor
    body: str


def _decode_scalar(raw: str, *, path: Path, key: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise SkillParseError(
                f"{path}: invalid quoted value for frontmatter key {key!r}"
            )
        # YAML single-quoted strings escape a quote by doubling it.
        return value[1:-1].replace("''", "'").strip()
    if value.startswith('"'):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise SkillParseError(
                f"{path}: invalid quoted value for frontmatter key {key!r}"
            ) from exc
        if not isinstance(parsed, str):
            raise SkillParseError(
                f"{path}: frontmatter key {key!r} must be text"
            )
        return parsed.strip()
    return value


def _parse_frontmatter_lines(
    lines: list[str], *, path: Path
) -> tuple[dict[str, str], tuple[str, ...]]:
    """Extract only top-level fields needed for discovery.

    Unknown/nested YAML-like metadata is tolerated but not interpreted. This is
    intentionally narrower than a general YAML loader: v1 needs standard
    discovery fields without adding a parser dependency or turning custom
    metadata into executable/authoritative state.
    """

    values: dict[str, str] = {}
    keys: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if line[:1].isspace():
            # Nested/list metadata belongs to a preceding custom field. v1 does
            # not interpret it during discovery.
            index += 1
            continue

        match = _TOP_LEVEL_KEY.match(line.rstrip("\r\n"))
        if match is None:
            # General YAML can express constructs v1 does not need. Ignore an
            # unknown top-level construct rather than pretending to understand
            # it, while required keys still must be parseable below.
            index += 1
            continue

        key = match.group(1)
        raw_value = match.group(2).strip()
        if key in keys:
            raise SkillParseError(f"{path}: duplicate frontmatter key {key!r}")
        keys.append(key)

        if raw_value in _BLOCK_SCALARS:
            block: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if candidate.strip() and not candidate[:1].isspace():
                    break
                if candidate.strip():
                    block.append(candidate.strip())
                elif block:
                    block.append("")
                index += 1
            if key in _REQUIRED_KEYS:
                if raw_value.startswith("|"):
                    values[key] = "\n".join(block).strip()
                else:
                    values[key] = " ".join(part for part in block if part).strip()
            continue

        if key in _REQUIRED_KEYS:
            values[key] = _decode_scalar(raw_value, path=path, key=key)
        index += 1

    for key in _REQUIRED_KEYS:
        if not values.get(key, "").strip():
            raise SkillParseError(
                f"{path}: frontmatter requires non-empty {key!r}"
            )
    return values, tuple(keys)


def _parse_skill_payload(
    payload: bytes, *, path: Path
) -> tuple[dict[str, str], tuple[str, ...], str]:
    """Parse discovery metadata and body from one immutable byte snapshot."""

    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SkillParseError(f"{path}: SKILL.md must be UTF-8 text") from exc

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != _FRONTMATTER_DELIMITER:
        raise SkillParseError(f"{path}: SKILL.md must begin with '---' frontmatter")

    frontmatter: list[str] = []
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == _FRONTMATTER_DELIMITER:
            values, keys = _parse_frontmatter_lines(frontmatter, path=path)
            body = "".join(lines[index + 1 :]).lstrip("\r\n")
            return values, keys, body
        frontmatter.append(line)
    raise SkillParseError(f"{path}: SKILL.md frontmatter is not closed with '---'")


def _read_frontmatter(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    if path.is_symlink() or not path.is_file():
        raise SkillParseError(f"{path}: SKILL.md must be a regular file")
    values, keys, _ = _parse_skill_payload(path.read_bytes(), path=path)
    return values, keys


def _read_body(path: Path) -> str:
    """Legacy helper retained for discovery/body-separation tests.

    Activation does not use this function; it parses the body from the exact
    bytes included in the verified directory snapshot.
    """

    if path.is_symlink() or not path.is_file():
        raise SkillParseError(f"{path}: SKILL.md must be a regular file")
    _, _, body = _parse_skill_payload(path.read_bytes(), path=path)
    return body


def _regular_files(skill_root: Path) -> tuple[Path, ...]:
    if skill_root.is_symlink() or not skill_root.is_dir():
        raise SkillParseError(f"{skill_root}: Skill root must be a regular directory")

    files: list[Path] = []
    for path in skill_root.rglob("*"):
        if path.is_symlink():
            raise SkillParseError(f"{path}: symlinks are not supported in Skill v1")
        if path.is_file():
            files.append(path)
    return tuple(sorted(files, key=lambda item: item.relative_to(skill_root).as_posix()))


def _hash_snapshot(skill_root: Path, snapshot: Iterable[tuple[Path, bytes]]) -> str:
    digest = hashlib.sha256()
    for path, payload in snapshot:
        relative = path.relative_to(skill_root).as_posix().encode("utf-8")
        digest.update(b"FILE\0")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


def _directory_hash(skill_root: Path, files: Iterable[Path] | None = None) -> str:
    selected = tuple(files) if files is not None else _regular_files(skill_root)
    snapshot = tuple((path, path.read_bytes()) for path in selected)
    return _hash_snapshot(skill_root, snapshot)


def _verified_snapshot(
    descriptor: SkillDescriptor,
) -> tuple[tuple[tuple[Path, bytes], ...], str]:
    """Read activation bytes once and verify that exact snapshot identity."""

    files = _regular_files(descriptor.root)
    snapshot: list[tuple[Path, bytes]] = []
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise SkillChangedError(
                f"{descriptor.root}: Skill content changed after discovery; rediscover before use"
            )
        snapshot.append((path, path.read_bytes()))
    frozen = tuple(snapshot)
    digest = _hash_snapshot(descriptor.root, frozen)
    if digest != descriptor.content_sha256:
        raise SkillChangedError(
            f"{descriptor.root}: Skill content changed after discovery; rediscover before use"
        )
    return frozen, digest


def _group(paths: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    needle = prefix + "/"
    return tuple(path for path in paths if path.startswith(needle))


def _descriptor_for_root(skill_root: Path) -> SkillDescriptor:
    if skill_root.is_symlink():
        raise SkillParseError(f"{skill_root}: symlinked Skill directories are not supported")
    skill_root = skill_root.resolve()
    skill_file = skill_root / "SKILL.md"
    values, metadata_keys = _read_frontmatter(skill_file)
    files = _regular_files(skill_root)
    relative_files = tuple(path.relative_to(skill_root).as_posix() for path in files)
    resources = tuple(path for path in relative_files if path != "SKILL.md")
    manifest_payload = (
        (skill_root / _CAPABILITY_MANIFEST_FILENAME).read_bytes()
        if _CAPABILITY_MANIFEST_FILENAME in relative_files
        else None
    )

    return SkillDescriptor(
        skill_id=skill_root.name,
        name=values["name"],
        description=values["description"],
        root=skill_root,
        skill_file=skill_file,
        content_sha256=_directory_hash(skill_root, files),
        declared_metadata_keys=metadata_keys,
        resource_paths=resources,
        script_paths=_group(resources, "scripts"),
        reference_paths=_group(resources, "references"),
        asset_paths=_group(resources, "assets"),
        example_paths=_group(resources, "examples"),
        declared_capabilities=_declared_capabilities_tuple(manifest_payload),
    )


def discover_skills(skills_root: str | Path) -> tuple[SkillDescriptor, ...]:
    """Discover immediate child Skill directories without loading procedure bodies."""

    root = Path(skills_root)
    if not root.exists():
        return ()
    if root.is_symlink() or not root.is_dir():
        raise SkillParseError(f"{root}: skills root must be a regular directory")

    descriptors: list[SkillDescriptor] = []
    names: dict[str, Path] = {}
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_symlink():
            raise SkillParseError(f"{child}: symlinked Skill directories are not supported")
        if not child.is_dir() or not (child / "SKILL.md").exists():
            continue
        descriptor = _descriptor_for_root(child)
        prior = names.get(descriptor.name)
        if prior is not None:
            raise SkillParseError(
                f"duplicate Skill name {descriptor.name!r}: {prior} and {child}"
            )
        names[descriptor.name] = child
        descriptors.append(descriptor)
    return tuple(descriptors)


def load_skill(descriptor: SkillDescriptor) -> SkillDocument:
    """Activate one Skill from the exact bytes matching its discovered identity."""

    snapshot, digest = _verified_snapshot(descriptor)
    by_relative = {
        path.relative_to(descriptor.root).as_posix(): payload
        for path, payload in snapshot
    }
    skill_payload = by_relative.get("SKILL.md")
    if skill_payload is None:
        raise SkillChangedError(
            f"{descriptor.root}: Skill content changed after discovery; rediscover before use"
        )

    values, metadata_keys, body = _parse_skill_payload(
        skill_payload,
        path=descriptor.skill_file,
    )
    relative_files = tuple(sorted(by_relative))
    resources = tuple(path for path in relative_files if path != "SKILL.md")
    current = SkillDescriptor(
        skill_id=descriptor.root.name,
        name=values["name"],
        description=values["description"],
        root=descriptor.root,
        skill_file=descriptor.skill_file,
        content_sha256=digest,
        declared_metadata_keys=metadata_keys,
        resource_paths=resources,
        script_paths=_group(resources, "scripts"),
        reference_paths=_group(resources, "references"),
        asset_paths=_group(resources, "assets"),
        example_paths=_group(resources, "examples"),
        declared_capabilities=_declared_capabilities_tuple(
            by_relative.get(_CAPABILITY_MANIFEST_FILENAME)
        ),
    )
    if (
        current.skill_id != descriptor.skill_id
        or current.name != descriptor.name
        or current.description != descriptor.description
        or current.declared_metadata_keys != descriptor.declared_metadata_keys
        or current.resource_paths != descriptor.resource_paths
        or current.declared_capabilities != descriptor.declared_capabilities
    ):
        raise SkillChangedError(
            f"{descriptor.root}: Skill identity changed after discovery"
        )
    return SkillDocument(descriptor=current, body=body)
