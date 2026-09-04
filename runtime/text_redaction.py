"""Best-effort secret redaction, kept dependency-free.

Deliberately has no import from `runtime.state` or `runtime.environment`:
both packages need `redact_sensitive_text`, and either one importing it from
the other's package would recreate the `runtime.environment` <->
`runtime.state` circular import (see
`work/coordination/FRICTION_LOG.md` "circular import runtime/environment
<-> runtime/state/environment"). This module is a shared leaf both sides can
depend on safely.
"""

from __future__ import annotations

import re

_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----.*?"
    r"-----END (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----",
    re.DOTALL,
)
_KNOWN_TOKEN_RE = re.compile(
    r"\b(?:"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r")\b"
)
_BEARER_RE = re.compile(
    r"(?i)\b(authorization\s*:\s*bearer\s+)([^\s,;]+)"
)
_NAMED_SECRET_RE = re.compile(
    r"(?i)\b("
    r"api[_-]?key|(?:access|auth|session)[_-]?token|token|"
    r"client[_-]?secret|api[_-]?secret|secret|password|passwd"
    r")\b(\s*[:=]\s*)([^\s,;]+)"
)


def redact_sensitive_text(value: str) -> str:
    """Best-effort redaction for durable diagnostic/telemetry text."""

    text = _PRIVATE_KEY_RE.sub("[REDACTED:PRIVATE_KEY]", value)
    text = _KNOWN_TOKEN_RE.sub("[REDACTED:TOKEN]", text)
    text = _BEARER_RE.sub(r"\1[REDACTED:TOKEN]", text)
    text = _NAMED_SECRET_RE.sub(r"\1\2[REDACTED:SECRET]", text)
    return text
