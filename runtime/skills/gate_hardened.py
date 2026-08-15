from __future__ import annotations

from .format import SkillDescriptor
from .gate import (
    SkillGateDisposition,
    SkillGateFinding,
    SkillGateReport,
    SkillGateSeverity,
    _ROLEPLAY_RE,
    _finding,
    _scan_text,
    assess_skill as _assess_skill,
)


def _frontmatter_text(descriptor: SkillDescriptor) -> str:
    raw = descriptor.skill_file.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    if not lines or lines[0] != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:index])
    return ""


def assess_skill(descriptor: SkillDescriptor) -> SkillGateReport:
    """Assess a hash-verified Skill including its complete frontmatter surface."""

    report = _assess_skill(descriptor)
    frontmatter = _frontmatter_text(descriptor)
    additional: list[SkillGateFinding] = []
    if frontmatter:
        additional.extend(
            _scan_text("SKILL.md:frontmatter", frontmatter, is_script=False)
        )
        if _ROLEPLAY_RE.search(frontmatter):
            additional.append(
                _finding(
                    "ROLEPLAY_HEAVY_METADATA",
                    SkillGateSeverity.REVIEW,
                    "SKILL.md:frontmatter",
                    "Skill frontmatter contains persona/roleplay language requiring review.",
                )
            )

    custom_keys = sorted(
        set(descriptor.declared_metadata_keys) - {"name", "description"}
    )
    if custom_keys:
        additional.append(
            _finding(
                "CUSTOM_METADATA_PRESENT",
                SkillGateSeverity.REVIEW,
                "SKILL.md:frontmatter",
                "Custom Skill metadata is present and requires review before trust or routing use.",
            )
        )

    findings = {
        (item.code, item.severity.value, item.path, item.summary): item
        for item in (*report.findings, *additional)
    }
    severity_rank = {
        SkillGateSeverity.INFO: 0,
        SkillGateSeverity.REVIEW: 1,
        SkillGateSeverity.BLOCK: 2,
    }
    ordered = tuple(
        sorted(
            findings.values(),
            key=lambda item: (
                -severity_rank[item.severity],
                item.code,
                item.path,
                item.summary,
            ),
        )
    )
    if any(item.severity == SkillGateSeverity.BLOCK for item in ordered):
        disposition = SkillGateDisposition.QUARANTINE
    elif any(item.severity == SkillGateSeverity.REVIEW for item in ordered):
        disposition = SkillGateDisposition.REVIEW_REQUIRED
    else:
        disposition = SkillGateDisposition.CLEAR

    return SkillGateReport(
        skill_name=report.skill_name,
        content_sha256=report.content_sha256,
        disposition=disposition,
        findings=ordered,
        scanned_files=report.scanned_files,
        scanned_bytes=report.scanned_bytes,
    )
