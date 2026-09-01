from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re

from runtime.state.observability import redact_sensitive_text

from .format import (
    SkillChangedError,
    SkillDescriptor,
    _parse_skill_payload,
    _verified_snapshot,
)


class SkillGateSeverity(str, Enum):
    INFO = "INFO"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class SkillGateDisposition(str, Enum):
    CLEAR = "CLEAR"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    QUARANTINE = "QUARANTINE"


@dataclass(frozen=True, slots=True)
class SkillGateFinding:
    code: str
    severity: SkillGateSeverity
    path: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "path": self.path,
            "summary": self.summary,
        }


@dataclass(frozen=True, slots=True)
class SkillGateReport:
    skill_name: str
    content_sha256: str
    disposition: SkillGateDisposition
    findings: tuple[SkillGateFinding, ...]
    scanned_files: int
    scanned_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_name": self.skill_name,
            "content_sha256": self.content_sha256,
            "disposition": self.disposition.value,
            "findings": [finding.to_dict() for finding in self.findings],
            "scanned_files": self.scanned_files,
            "scanned_bytes": self.scanned_bytes,
        }


_MAX_TEXT_SCAN_BYTES = 1024 * 1024
_SHORT_DESCRIPTION_CHARS = 40
_LARGE_SKILL_BODY_CHARS = 32_000

_AUTHORITY_OVERRIDE_RE = re.compile(
    r"(?i)(?:"
    r"\bignore\b.{0,120}\b(?:AGENTS\.md|policy|policies|system instructions|operator)\b"
    r"|\boverride\b.{0,120}\b(?:AGENTS\.md|policy|policies|operator)\b"
    r"|\b(?:operator )?(?:approval|permission)\s+(?:is|has been)\s+granted\b"
    r")",
    re.DOTALL,
)
_NETWORK_PIPE_EXEC_RE = re.compile(
    r"(?i)\b(?:curl|wget)\b[^\n|]{0,400}\|\s*(?:sh|bash|zsh|python(?:3)?)\b"
)
_PRIVILEGE_RE = re.compile(
    r"(?i)(?:\bsudo\b|\bchmod\s+777\b|\bchown\b|\bmount\b)"
)
_DESTRUCTIVE_RE = re.compile(
    r"(?i)(?:\brm\s+-[A-Za-z]*r[A-Za-z]*f\b|\bDROP\s+(?:DATABASE|TABLE)\b)"
)
_CREDENTIAL_HARVEST_RE = re.compile(
    r"(?i)(?:\bprintenv\b|/proc/(?:self|\d+)/environ|\bos\.environ\b|\bprocess\.env\b)"
)
_NETWORK_ACCESS_RE = re.compile(
    r"(?i)(?:\b(?:curl|wget)\b|\brequests\.(?:get|post|put|delete|request)\b|https?://)"
)
_ROLEPLAY_RE = re.compile(
    r"(?i)(?:\bpretend\s+you\s+are\b|\bact\s+as\s+(?:an?\s+)?(?:world[- ]class|expert)\b|\bexpert\s+persona\b)"
)
_SENSITIVE_FILENAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}
_SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}

# SEC4 capability-declaration manifest, slice 1
# (`work/notes/2026-09-01-sec4-capability-declaration-manifest-design.md`).
# A Skill bundle MAY carry a top-level `capabilities` sidecar: one capability
# token per line (`#` comments and blank lines ignored), drawn from the
# roadmap `04-agentic-security.md` s5.1 vocabulary. It is descriptive
# supply-chain metadata only -- it feeds the gate report and nothing else,
# and is never read by a runtime guard or written into `task_policy`.
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

# Which REVIEW-severity static detector evidences which declared capability
# class. BLOCK-severity detectors (`NETWORK_PIPE_EXEC`, `SENSITIVE_LITERAL`,
# `AUTHORITY_OVERRIDE_CLAIM`, `SENSITIVE_RESOURCE_NAME`) are intrinsically
# dangerous and a manifest can never bless them, so they are not listed.
_DETECTOR_CAPABILITY = {
    "SCRIPT_NETWORK_ACCESS": "network-general",
    "CREDENTIAL_ENVIRONMENT_ACCESS": "secret-use:environment",
    "DESTRUCTIVE_OPERATION": "filesystem-write",
    "PRIVILEGE_OPERATION": "shell",
    "EXECUTABLE_RESOURCE_PRESENT": "shell",
}
# A declared token that also satisfies a detected capability class (coarse for
# slice 1: a declared `network-read` covers a generic network detection).
_SATISFYING_TOKENS = {
    "network-general": frozenset({"network-general", "network-read"}),
}

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


def _declared_covers(capability: str, declared: "frozenset[str]") -> bool:
    return bool(declared & _SATISFYING_TOKENS.get(capability, frozenset({capability})))


def _apply_capability_manifest(
    findings: list[SkillGateFinding],
    by_relative: dict[str, bytes],
) -> list[SkillGateFinding]:
    """Reconcile the static detector findings against the `capabilities` sidecar.

    - no manifest, but a capability-bearing detector fired -> one
      ``CAPABILITY_MANIFEST_ABSENT`` (REVIEW); detector findings unchanged.
    - manifest unreadable / unknown token -> ``CAPABILITY_MANIFEST_MALFORMED``
      (BLOCK); reconciliation is skipped (an unreadable manifest is not trusted).
    - manifest present: a detected capability it covers downgrades that
      detector finding to ``DECLARED_CAPABILITY_USE`` (INFO); a detected
      capability it omits adds ``UNDECLARED_CAPABILITY`` (BLOCK); a declared
      token nothing evidences adds ``OVER_DECLARED_CAPABILITY`` (INFO).
    """

    manifest = (
        _parse_capability_manifest(by_relative[_CAPABILITY_MANIFEST_FILENAME])
        if _CAPABILITY_MANIFEST_FILENAME in by_relative
        else None
    )

    capability_findings = [f for f in findings if f.code in _DETECTOR_CAPABILITY]
    detected = {_DETECTOR_CAPABILITY[f.code] for f in capability_findings}

    if manifest is _MANIFEST_MALFORMED:
        return findings + [
            _finding(
                "CAPABILITY_MANIFEST_MALFORMED",
                SkillGateSeverity.BLOCK,
                _CAPABILITY_MANIFEST_FILENAME,
                "Capability manifest is not UTF-8 text or contains an "
                "unrecognized capability token.",
            )
        ]

    if manifest is None:
        if not detected:
            return findings
        return findings + [
            _finding(
                "CAPABILITY_MANIFEST_ABSENT",
                SkillGateSeverity.REVIEW,
                _CAPABILITY_MANIFEST_FILENAME,
                "Skill exercises capability classes ("
                + ", ".join(sorted(detected))
                + ") but declares no `capabilities` manifest.",
            )
        ]

    assert isinstance(manifest, frozenset)
    covered = {cap for cap in detected if _declared_covers(cap, manifest)}
    undeclared = detected - covered

    reconciled: list[SkillGateFinding] = []
    for finding in findings:
        capability = _DETECTOR_CAPABILITY.get(finding.code)
        if capability is not None and capability in covered:
            reconciled.append(
                _finding(
                    "DECLARED_CAPABILITY_USE",
                    SkillGateSeverity.INFO,
                    finding.path,
                    f"Declared capability {capability!r} is exercised here "
                    "(matches the `capabilities` manifest).",
                )
            )
        else:
            reconciled.append(finding)

    for capability in sorted(undeclared):
        reconciled.append(
            _finding(
                "UNDECLARED_CAPABILITY",
                SkillGateSeverity.BLOCK,
                _CAPABILITY_MANIFEST_FILENAME,
                f"Skill exercises {capability!r} but the `capabilities` "
                "manifest does not declare it.",
            )
        )

    over_declared = {
        token
        for token in manifest
        if not any(
            token in _SATISFYING_TOKENS.get(cap, frozenset({cap})) for cap in detected
        )
    }
    for token in sorted(over_declared):
        reconciled.append(
            _finding(
                "OVER_DECLARED_CAPABILITY",
                SkillGateSeverity.INFO,
                _CAPABILITY_MANIFEST_FILENAME,
                f"Declared capability {token!r} is not evidenced by any static "
                "check; review whether the declaration is over-broad.",
            )
        )
    return reconciled


def _finding(
    code: str,
    severity: SkillGateSeverity,
    path: str,
    summary: str,
) -> SkillGateFinding:
    return SkillGateFinding(code=code, severity=severity, path=path, summary=summary)


def _scan_text(path: str, text: str, *, is_script: bool) -> list[SkillGateFinding]:
    findings: list[SkillGateFinding] = []
    if redact_sensitive_text(text) != text:
        findings.append(
            _finding(
                "SENSITIVE_LITERAL",
                SkillGateSeverity.BLOCK,
                path,
                "Likely credential or secret literal is present.",
            )
        )
    if _AUTHORITY_OVERRIDE_RE.search(text):
        findings.append(
            _finding(
                "AUTHORITY_OVERRIDE_CLAIM",
                SkillGateSeverity.BLOCK,
                path,
                "Content attempts to override MAPS/operator authority or claim approval.",
            )
        )
    if _NETWORK_PIPE_EXEC_RE.search(text):
        findings.append(
            _finding(
                "NETWORK_PIPE_EXEC",
                SkillGateSeverity.BLOCK,
                path,
                "Remote content is piped directly into an interpreter or shell.",
            )
        )
    if _PRIVILEGE_RE.search(text):
        findings.append(
            _finding(
                "PRIVILEGE_OPERATION",
                SkillGateSeverity.REVIEW,
                path,
                "Content references elevated or broad host privileges.",
            )
        )
    if _DESTRUCTIVE_RE.search(text):
        findings.append(
            _finding(
                "DESTRUCTIVE_OPERATION",
                SkillGateSeverity.REVIEW,
                path,
                "Content references a destructive operation requiring contextual review.",
            )
        )
    if _CREDENTIAL_HARVEST_RE.search(text):
        findings.append(
            _finding(
                "CREDENTIAL_ENVIRONMENT_ACCESS",
                SkillGateSeverity.REVIEW,
                path,
                "Content reads broad process/environment credential surfaces.",
            )
        )
    if is_script and _NETWORK_ACCESS_RE.search(text):
        findings.append(
            _finding(
                "SCRIPT_NETWORK_ACCESS",
                SkillGateSeverity.REVIEW,
                path,
                "Executable Skill resource appears to access the network.",
            )
        )
    return findings


def _scan_resource(
    relative: str,
    payload: bytes,
    *,
    is_script: bool,
) -> tuple[list[SkillGateFinding], int]:
    path = Path(relative)
    findings: list[SkillGateFinding] = []
    size = len(payload)
    name = path.name.lower()
    if name in _SENSITIVE_FILENAMES or path.suffix.lower() in _SENSITIVE_SUFFIXES:
        findings.append(
            _finding(
                "SENSITIVE_RESOURCE_NAME",
                SkillGateSeverity.BLOCK,
                relative,
                "Resource name indicates credential/private-key material.",
            )
        )
    if is_script:
        findings.append(
            _finding(
                "EXECUTABLE_RESOURCE_PRESENT",
                SkillGateSeverity.REVIEW,
                relative,
                "Skill contains a script resource; executable content requires review before use.",
            )
        )
    if size > _MAX_TEXT_SCAN_BYTES:
        findings.append(
            _finding(
                "RESOURCE_TOO_LARGE_TO_SCAN",
                SkillGateSeverity.REVIEW,
                relative,
                "Resource exceeds the bounded static text-scan limit.",
            )
        )
        return findings, size

    if b"\x00" in payload:
        findings.append(
            _finding(
                "BINARY_RESOURCE_PRESENT",
                SkillGateSeverity.REVIEW,
                relative,
                "Binary resource requires explicit review; static text checks were not applied.",
            )
        )
        return findings, size
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        findings.append(
            _finding(
                "NON_UTF8_RESOURCE_PRESENT",
                SkillGateSeverity.REVIEW,
                relative,
                "Non-UTF-8 resource requires explicit review; static text checks were not applied.",
            )
        )
        return findings, size
    findings.extend(_scan_text(relative, text, is_script=is_script))
    return findings, size


def _frontmatter_text(payload: bytes, *, path: Path) -> str:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SkillChangedError(f"{path}: verified SKILL.md is not UTF-8 text") from exc
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:index])
    return ""


def assess_skill(descriptor: SkillDescriptor) -> SkillGateReport:
    """Statically assess exactly one hash-verified Skill byte snapshot.

    The report is advisory gate evidence. `CLEAR` is not approval, and neither
    `REVIEW_REQUIRED` nor `QUARANTINE` mutates any persistent trust state.
    Every body/frontmatter/resource finding is derived from the same byte
    snapshot whose hash is reported as `content_sha256`.
    """

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
    resource_paths = tuple(path for path in sorted(by_relative) if path != "SKILL.md")
    if (
        values["name"] != descriptor.name
        or values["description"] != descriptor.description
        or metadata_keys != descriptor.declared_metadata_keys
        or resource_paths != descriptor.resource_paths
    ):
        raise SkillChangedError(
            f"{descriptor.root}: Skill identity changed after discovery"
        )

    findings: list[SkillGateFinding] = []
    scanned_bytes = sum(len(payload) for payload in by_relative.values())

    if len(descriptor.description.strip()) < _SHORT_DESCRIPTION_CHARS:
        findings.append(
            _finding(
                "DESCRIPTION_TOO_VAGUE",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Description is too short to provide reliable activation guidance.",
            )
        )
    if _ROLEPLAY_RE.search(descriptor.description) or _ROLEPLAY_RE.search(body):
        findings.append(
            _finding(
                "ROLEPLAY_HEAVY_INSTRUCTIONS",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Skill relies on persona/roleplay language instead of only procedural guidance.",
            )
        )
    if len(body) > _LARGE_SKILL_BODY_CHARS:
        findings.append(
            _finding(
                "SKILL_BODY_TOO_LARGE",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Skill body is large enough to undermine progressive disclosure/context economy.",
            )
        )
    findings.extend(_scan_text("SKILL.md", body, is_script=False))

    frontmatter = _frontmatter_text(skill_payload, path=descriptor.skill_file)
    if frontmatter:
        findings.extend(
            _scan_text("SKILL.md:frontmatter", frontmatter, is_script=False)
        )
        if _ROLEPLAY_RE.search(frontmatter):
            findings.append(
                _finding(
                    "ROLEPLAY_HEAVY_METADATA",
                    SkillGateSeverity.REVIEW,
                    "SKILL.md:frontmatter",
                    "Skill frontmatter contains persona/roleplay language requiring review.",
                )
            )
    custom_keys = sorted(set(metadata_keys) - {"name", "description"})
    if custom_keys:
        findings.append(
            _finding(
                "CUSTOM_METADATA_PRESENT",
                SkillGateSeverity.REVIEW,
                "SKILL.md:frontmatter",
                "Custom Skill metadata is present and requires review before trust or routing use.",
            )
        )

    script_paths = set(descriptor.script_paths)
    for relative in descriptor.resource_paths:
        payload = by_relative.get(relative)
        if payload is None:
            raise SkillChangedError(
                f"{descriptor.root}: Skill content changed after discovery; rediscover before use"
            )
        resource_findings, _ = _scan_resource(
            relative,
            payload,
            is_script=relative in script_paths,
        )
        findings.extend(resource_findings)

    findings = _apply_capability_manifest(findings, by_relative)

    findings = list(
        {
            (item.code, item.severity.value, item.path, item.summary): item
            for item in findings
        }.values()
    )
    severity_rank = {
        SkillGateSeverity.INFO: 0,
        SkillGateSeverity.REVIEW: 1,
        SkillGateSeverity.BLOCK: 2,
    }
    findings.sort(
        key=lambda item: (
            -severity_rank[item.severity],
            item.code,
            item.path,
            item.summary,
        )
    )
    if any(item.severity == SkillGateSeverity.BLOCK for item in findings):
        disposition = SkillGateDisposition.QUARANTINE
    elif any(item.severity == SkillGateSeverity.REVIEW for item in findings):
        disposition = SkillGateDisposition.REVIEW_REQUIRED
    else:
        disposition = SkillGateDisposition.CLEAR

    return SkillGateReport(
        skill_name=descriptor.name,
        content_sha256=digest,
        disposition=disposition,
        findings=tuple(findings),
        scanned_files=len(by_relative),
        scanned_bytes=scanned_bytes,
    )
