from __future__ import annotations

from . import gate as _gate_module
from .format import SkillDescriptor
from .gate import (
    SkillGateDisposition,
    SkillGateFinding,
    SkillGateReport,
    SkillGateSeverity,
    assess_skill as _assess_skill,
)


def assess_skill(descriptor: SkillDescriptor) -> SkillGateReport:
    """Assess a Skill through the complete single-snapshot gate implementation."""

    return _assess_skill(descriptor)


# Ensure direct imports from runtime.skills.gate receive the complete hardened
# implementation after package initialization. The captured implementation above
# already scans body, frontmatter, metadata, and resources from one verified
# byte snapshot, so this wrapper performs no additional filesystem reads.
_gate_module.assess_skill = assess_skill
