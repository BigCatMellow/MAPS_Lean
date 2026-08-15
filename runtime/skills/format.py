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


def _read_frontmatter(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    if path.is_symlink() or not path.is_file():
        raise SkillParseError(f"{path}: SKILL.md must be a regular file")

    frontmatter: list[str] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        first = handle.readline()
        if first.rstrip("\r\n") != _FRONTMATTER_DELIMITER:
            raise SkillParseError(f"{path}: SKILL.md must begin with '---' frontmatter")
        for line in handle:
            if line.rstrip("\r\n") == _FRONTMATTER_DELIMITER:
                return _parse_frontmatter_lines(frontmatter, path=path)
            frontmatter.append(line)
    raise SkillParseError(f"{path}: SKILL.md frontmatter is not closed with '---'")


def _read_body(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig") as handle:
        if handle.readline().rstrip("\r\n") != _FRONTMATTER_DELIMITER:
            raise SkillParseError(f"{path}: SKILL.md must begin with '---' frontmatter")
        for line in handle:
            if line.rstrip("\r\n") == _FRONTMATTER_DELIMITER:
                return handle.read().lstrip("\r\n")
    raise SkillParseError(f"{path}: SKILL.md frontmatter is not closed with '---'")


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


def _directory_hash(skill_root: Path, files: Iterable[Path] | None = None) -> str:
    digest = hashlib.sha256()
    selected = tuple(files) if files is not None else _regular_files(skill_root)
    for path in selected:
        relative = path.relative_to(skill_root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(b"FILE\0")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


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
    """Activate one previously discovered Skill after verifying content identity."""

    current = _descriptor_for_root(descriptor.root)
    if current.content_sha256 != descriptor.content_sha256:
        raise SkillChangedError(
            f"{descriptor.root}: Skill content changed after discovery; rediscover before use"
        )
    if (
        current.skill_id != descriptor.skill_id
        or current.name != descriptor.name
        or current.description != descriptor.description
    ):
        # The content hash should already catch this; keep the explicit identity
        # check so future hash/refactoring mistakes fail closed.
        raise SkillChangedError(
            f"{descriptor.root}: Skill identity changed after discovery"
        )
    return SkillDocument(descriptor=current, body=_read_body(current.skill_file))
