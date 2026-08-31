from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from .format import SkillDescriptor, SkillDocument, discover_skills, load_skill
from .lifecycle import SkillLifecycleState

if TYPE_CHECKING:  # pragma: no cover - typing only
    from runtime.state.common import MutationResult
    from runtime.state.skill_lifecycle_storage import SkillLifecycleStorageMixin


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


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be non-empty text")
    return value.strip()


def _catalog_key(source_id: str, descriptor: SkillDescriptor) -> str:
    """The one content-addressed catalog-key formula.

    Used by both `SkillCatalogEntry.catalog_key` and `build_skill_catalog`'s
    pre-entry lifecycle-state lookup so the two can never drift.
    """

    return (
        f"{source_id}:{descriptor.skill_id}"
        f"@sha256:{descriptor.content_sha256}"
    )


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
    # The Skill's composed lifecycle state, read one-directionally from the
    # durable store (`runtime.state.skill_lifecycle_storage`) at catalog-build
    # time when a store is supplied. `None` means "no subject row" -- i.e.
    # discovered but not yet gate-assessed. This field is never authored here;
    # `runtime.skills.lifecycle.SkillLifecycleState` is the single source of
    # truth and `runtime.trust.skill_lifecycle_trust_class` is the only
    # projection onward to `MemoryTrustClass`.
    lifecycle_state: SkillLifecycleState | None = None


@dataclass(frozen=True, slots=True)
class SkillCatalogEntry:
    descriptor: SkillDescriptor
    provenance: SkillProvenance

    @property
    def catalog_key(self) -> str:
        return _catalog_key(self.provenance.source_id, self.descriptor)


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

        # The fingerprint is deliberately a pure function of filesystem
        # content + provenance identity only. Lifecycle/approval state is NOT
        # folded in: it lives in the durable store, not in the catalog's
        # identity, and re-approving a Skill must not churn the fingerprint
        # (SEC4 Half 2, design note 2026-08-31 Q7 -- the fingerprint has no
        # consumers that need approval-sensitivity, and staying content-only
        # keeps it reproducible from a checkout alone).
        digest = hashlib.sha256()
        for entry in ordered:
            fields = (
                entry.provenance.source_id,
                entry.provenance.source_kind.value,
                entry.provenance.source_ref,
                entry.provenance.declared_revision or "",
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


def build_skill_catalog(
    sources: Iterable[SkillCatalogSource],
    *,
    store: "SkillLifecycleStorageMixin | None" = None,
) -> SkillCatalog:
    """Discover Skills across `sources` into an immutable catalog.

    When `store` is given, each entry's `provenance.lifecycle_state` is
    populated by a one-directional read of the durable lifecycle store
    (`store.get_skill_lifecycle_state(catalog_key)`); `None` for any Skill
    with no subject row. With `store=None` (every caller today) every entry
    is `lifecycle_state=None`, identical in behavior to before this wiring.
    """

    selected = tuple(sources)
    seen_source_ids: set[str] = set()
    for source in selected:
        if source.source_id in seen_source_ids:
            raise SkillCatalogError(f"duplicate source_id: {source.source_id}")
        seen_source_ids.add(source.source_id)

    entries: list[SkillCatalogEntry] = []
    for source in sorted(selected, key=lambda item: item.source_id):
        source_ref = source.source_ref or str(source.root.resolve())
        for descriptor in discover_skills(source.root):
            catalog_key = _catalog_key(source.source_id, descriptor)
            lifecycle_state = (
                store.get_skill_lifecycle_state(catalog_key)
                if store is not None
                else None
            )
            provenance = SkillProvenance(
                source_id=source.source_id,
                source_kind=source.kind,
                source_ref=source_ref,
                declared_revision=source.declared_revision,
                lifecycle_state=lifecycle_state,
            )
            entries.append(
                SkillCatalogEntry(
                    descriptor=descriptor,
                    provenance=provenance,
                )
            )
    return SkillCatalog(entries=tuple(entries))


def register_skill_catalog(
    catalog: SkillCatalog,
    store: "SkillLifecycleStorageMixin",
    *,
    now=None,
) -> "list[MutationResult]":
    """Record a durable lifecycle subject for every catalog entry that lacks one.

    This is the production caller of `record_skill_lifecycle_subject()`
    (SEC4 Half 2, design note 2026-08-31 Q4): subject creation is
    gate-driven and happens at catalog-build time. Each not-yet-recorded
    entry is assessed through the existing `assess_skill()` gate, and its
    starting lifecycle state is derived from that report inside the store.
    Idempotent: entries whose content-addressed `catalog_key` already has a
    subject row are skipped, so a re-run after a partial repo change only
    assesses the genuinely new revisions.

    Returns the list of `MutationResult`s for the subjects it recorded.
    """

    from .gate_hardened import assess_skill

    results = []
    for entry in catalog.entries:
        if store.get_skill_lifecycle_subject(entry.catalog_key) is not None:
            continue
        report = assess_skill(entry.descriptor)
        results.append(
            store.record_skill_lifecycle_subject(entry, report, now=now)
        )
    return results


_NON_ACTIVATABLE_LIFECYCLE_STATES = frozenset(
    {
        SkillLifecycleState.QUARANTINED,
        SkillLifecycleState.RETIRED,
        SkillLifecycleState.SUPERSEDED,
    }
)


def load_catalog_skill(
    entry: SkillCatalogEntry,
    store: "SkillLifecycleStorageMixin | None" = None,
) -> SkillDocument:
    """Activate exactly the catalog entry selected by the caller.

    Catalog lookup does not authorize activation. `load_skill` still verifies the
    discovered directory hash immediately before reading the procedure body.

    When `store` is given, this is the first real refusal wired to the
    durable lifecycle state (SEC4 Half 2): activation is declined with
    `SkillCatalogError` if the Skill's composed state is `QUARANTINED`,
    `RETIRED`, or `SUPERSEDED`. `APPROVED`/`ACTIVE`/`VALIDATED` and the
    "no subject row" case (`None`) are all allowed through -- this refusal
    is a structural authority gate, not an operator-identity check (that
    stays deferred; see the module docstring of
    `runtime.state.skill_lifecycle_storage`). With `store=None` (every
    caller today) behavior is unchanged.
    """

    if store is not None:
        state = store.get_skill_lifecycle_state(entry.catalog_key)
        if state in _NON_ACTIVATABLE_LIFECYCLE_STATES:
            raise SkillCatalogError(
                f"Skill {entry.descriptor.name!r} ({entry.catalog_key}) is "
                f"{state.value}; activation refused"
            )

    return load_skill(entry.descriptor)
