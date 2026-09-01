"""SEC4 capability-declaration manifest, slice 2 — the declared ⊆ permitted check.

`work/notes/2026-09-01-sec4-capability-manifest-slice2-design.md` §4/§5.

Maps each roadmap `04-agentic-security.md` §5.1 capability token to the
`task_policy` boolean(s) that must be set for a Skill *declaring* that token to
be surfaced into a task's context plan. This is a **composition at plan-assembly
time**, not authority: `task_policy` is read as the task's already-decided
envelope, the Skill manifest is read as the Skill's declaration, and the check
is `declared ⊆ permitted`. The manifest is never written back into `task_policy`,
never reaches a `HookRegistry` guard, and this module holds no state.

Coarse / whole-Skill, matching slice 1's granularity. `broad_architecture` and
`paid_execution` are unmapped — a known gap (no capability token corresponds to
either). A path-scoped `filesystem-write:<relative-path>` declaration is
*accepted* (capability-granularity slice) and permitted identically to bare
`filesystem-write` — a strict narrowing of an already-baseline capability;
*enforcing* the declared path against the task's output paths, and per-host
`network-general` scoping, remain later slices.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

# Always permitted, regardless of envelope: read-only access plus `shell` and
# `filesystem-write`. `shell` — the harness itself runs in a shell; elevated
# shell (`sudo`, `chmod 777`) is slice 1's `PRIVILEGE_OPERATION` REVIEW finding.
# `filesystem-write` — normal implementation work; the *destructive* subset is
# slice 1's `DESTRUCTIVE_OPERATION` REVIEW finding. Gating either on an envelope
# boolean would DENY every ordinary implementation Skill.
_BASELINE: frozenset[str] = frozenset(
    {
        "filesystem-read",
        "filesystem-write",
        "shell",
        "network-read",
        "github-read",
        "database-read",
    }
)

# token -> task_policy flags that must ALL be truthy for it to be permitted.
_REQUIRES: dict[str, tuple[str, ...]] = {
    "network-general": ("external_side_effect",),
    "github-write": ("external_side_effect",),
    "database-write": ("external_side_effect",),
    "process-stop": ("destructive_action",),
    "external-deploy": ("external_side_effect", "destructive_action"),
}

_SECRET_USE_PREFIX = "secret-use:"
# A path-scoped `filesystem-write:<relative-path>` declaration (capability-
# granularity slice) is a strict narrowing of the unscoped `filesystem-write`,
# which is already baseline-permitted -- it can never need *more* permission
# than the broader form, so it is baseline too. Enforcing the declared path
# against the task's output paths is a later slice, not wired here.
_FILESYSTEM_WRITE_PREFIX = "filesystem-write:"


def _required_flags(token: str) -> tuple[str, ...] | None:
    """`task_policy` flags a declared token needs, or ``None`` when the token is
    unrecognized (treated as never-permitted — fail closed)."""

    if token in _BASELINE:
        return ()
    if token.startswith(_FILESYSTEM_WRITE_PREFIX):
        return ()
    if token.startswith(_SECRET_USE_PREFIX):
        return ("security_sensitive",)
    return _REQUIRES.get(token)


def capabilities_within_envelope(
    declared: Iterable[str],
    policy: Mapping[str, Any] | None,
) -> tuple[bool, tuple[str, ...]]:
    """Return ``(ok, offending_tokens)``.

    A declared token is *offending* when it is unrecognized, or when a
    `task_policy` flag it requires is not truthy in ``policy``. A missing
    ``policy`` map is treated as all-false — fail closed for every consequential
    token, baseline tokens still pass.
    """

    pol = policy or {}
    offending: list[str] = []
    for token in dict.fromkeys(declared):  # de-dupe, preserve order
        flags = _required_flags(token)
        if flags is None or any(not pol.get(flag) for flag in flags):
            offending.append(token)
    return (not offending, tuple(sorted(offending)))
