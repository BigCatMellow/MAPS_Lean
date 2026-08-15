from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re

from runtime.state.observability import redact_sensitive_text

from .format import SkillDescriptor, load_skill


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


def _scan_resource(root: Path, relative: str, *, is_script: bool) -> tuple[list[SkillGateFinding], int]:
    path = root / relative
    findings: list[SkillGateFinding] = []
    size = path.stat().st_size
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

    payload = path.read_bytes()
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


def assess_skill(descriptor: SkillDescriptor) -> SkillGateReport:
    """Statically assess one already-discovered Skill without executing resources.

    The report is advisory gate evidence. `CLEAR` is not approval, and neither
    `REVIEW_REQUIRED` nor `QUARANTINE` mutates any persistent trust state.
    """

    document = load_skill(descriptor)
    findings: list[SkillGateFinding] = []
    scanned_bytes = descriptor.skill_file.stat().st_size

    if len(descriptor.description.strip()) < _SHORT_DESCRIPTION_CHARS:
        findings.append(
            _finding(
                "DESCRIPTION_TOO_VAGUE",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Description is too short to provide reliable activation guidance.",
            )
        )
    if _ROLEPLAY_RE.search(descriptor.description) or _ROLEPLAY_RE.search(document.body):
        findings.append(
            _finding(
                "ROLEPLAY_HEAVY_INSTRUCTIONS",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Skill relies on persona/roleplay language instead of only procedural guidance.",
            )
        )
    if len(document.body) > _LARGE_SKILL_BODY_CHARS:
        findings.append(
            _finding(
                "SKILL_BODY_TOO_LARGE",
                SkillGateSeverity.REVIEW,
                "SKILL.md",
                "Skill body is large enough to undermine progressive disclosure/context economy.",
            )
        )
    findings.extend(_scan_text("SKILL.md", document.body, is_script=False))

    script_paths = set(descriptor.script_paths)
    for relative in descriptor.resource_paths:
        resource_findings, size = _scan_resource(
            descriptor.root,
            relative,
            is_script=relative in script_paths,
        )
        findings.extend(resource_findings)
        scanned_bytes += size

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
        content_sha256=descriptor.content_sha256,
        disposition=disposition,
        findings=tuple(findings),
        scanned_files=1 + len(descriptor.resource_paths),
        scanned_bytes=scanned_bytes,
    )
