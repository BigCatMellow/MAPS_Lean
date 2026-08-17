from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from pathlib import Path
from typing import Iterable

from .format import SkillDescriptor, SkillDocument, discover_skills, load_skill


class SkillCatalogError(ValueError):
    pass


class SkillNotFoundError(SkillCatalogError):
    pass


class SkillAmbiguousError(SkillCatalogError):
    pass


class SkillSourceKind(str, Enum):
    BUNDLED = "BUNDLED"
    LOCAL = "LOCAL"
    THIRD_PARTY = "THIRD_PARTY"


class SkillTrustState(str, Enum):
    # S3 intentionally does not implement approval. A future reviewed trust
    # lifecycle may add states; catalog discovery itself can only say UNASSESSED.
    UNASSESSED = "UNASSESSED"


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be non-empty text")
    return value.strip()


@dataclass(frozen=True, slots=True)
class SkillCatalogSource:
    source_id: str
    root: Path
    kind: SkillSourceKind
    source_ref: str | None = None
    declared_revision: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _required_text(self.source_id, "source_id"))
        object.__setattr__(self, "root", Path(self.root))
        if self.source_ref is not None:
            object.__setattr__(
                self,
                "source_ref",
                _required_text(self.source_ref, "source_ref"),
            )
        if self.declared_revision is not None:
            object.__setattr__(
                self,
                "declared_revision",
                _required_text(self.declared_revision, "declared_revision"),
            )


@dataclass(frozen=True, slots=True)
class SkillProvenance:
    source_id: str
    source_kind: SkillSourceKind
    source_ref: str
    declared_revision: str | None
    trust_state: SkillTrustState = SkillTrustState.UNASSESSED


@dataclass(frozen=True, slots=True)
class SkillCatalogEntry:
    descriptor: SkillDescriptor
    provenance: SkillProvenance

    @property
    def catalog_key(self) -> str:
        return (
            f"{self.provenance.source_id}:{self.descriptor.skill_id}"
            f"@sha256:{self.descriptor.content_sha256}"
        )


@dataclass(frozen=True, slots=True)
class SkillNameConflict:
    name: str
    catalog_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkillCatalog:
    entries: tuple[SkillCatalogEntry, ...]
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        ordered = tuple(
            sorted(
                self.entries,
                key=lambda entry: (
                    entry.descriptor.name,
                    entry.provenance.source_id,
                    entry.descriptor.skill_id,
                    entry.descriptor.content_sha256,
                ),
            )
        )
        object.__setattr__(self, "entries", ordered)

        digest = hashlib.sha256()
        for entry in ordered:
            fields = (
                entry.provenance.source_id,
                entry.provenance.source_kind.value,
                entry.provenance.source_ref,
                entry.provenance.declared_revision or "",
                entry.provenance.trust_state.value,
                entry.descriptor.skill_id,
                entry.descriptor.name,
                entry.descriptor.content_sha256,
            )
            digest.update("\0".join(fields).encode("utf-8"))
            digest.update(b"\0")
        object.__setattr__(self, "fingerprint", digest.hexdigest())

    def find(self, name: str) -> tuple[SkillCatalogEntry, ...]:
        target = _required_text(name, "name")
        return tuple(entry for entry in self.entries if entry.descriptor.name == target)

    def require_unique(self, name: str) -> SkillCatalogEntry:
        matches = self.find(name)
        if not matches:
            raise SkillNotFoundError(f"Skill {name!r} is not present in the catalog")
        if len(matches) != 1:
            raise SkillAmbiguousError(
                f"Skill {name!r} is ambiguous across {len(matches)} catalog entries"
            )
        return matches[0]

    @property
    def conflicts(self) -> tuple[SkillNameConflict, ...]:
        names = sorted({entry.descriptor.name for entry in self.entries})
        conflicts: list[SkillNameConflict] = []
        for name in names:
            matches = self.find(name)
            if len(matches) > 1:
                conflicts.append(
                    SkillNameConflict(
                        name=name,
                        catalog_keys=tuple(entry.catalog_key for entry in matches),
                    )
                )
        return tuple(conflicts)


def build_skill_catalog(sources: Iterable[SkillCatalogSource]) -> SkillCatalog:
    selected = tuple(sources)
    seen_source_ids: set[str] = set()
    for source in selected:
        if source.source_id in seen_source_ids:
            raise SkillCatalogError(f"duplicate source_id: {source.source_id}")
        seen_source_ids.add(source.source_id)

    entries: list[SkillCatalogEntry] = []
    for source in sorted(selected, key=lambda item: item.source_id):
        source_ref = source.source_ref or str(source.root.resolve())
        provenance = SkillProvenance(
            source_id=source.source_id,
            source_kind=source.kind,
            source_ref=source_ref,
            declared_revision=source.declared_revision,
        )
        for descriptor in discover_skills(source.root):
            entries.append(
                SkillCatalogEntry(
                    descriptor=descriptor,
                    provenance=provenance,
                )
            )
    return SkillCatalog(entries=tuple(entries))


def load_catalog_skill(entry: SkillCatalogEntry) -> SkillDocument:
    """Activate exactly the catalog entry selected by the caller.

    Catalog lookup does not authorize activation. `load_skill` still verifies the
    discovered directory hash immediately before reading the procedure body.
    """

    return load_skill(entry.descriptor)
