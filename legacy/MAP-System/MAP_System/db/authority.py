"""Fail-closed guard for hosts that mirror a remote MAP database authority."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_DB = ROOT / "map.db"
DEFAULT_CONFIG = Path.home() / ".config" / "map-authority.json"


class RemoteAuthorityRequired(RuntimeError):
    """Raised when a mirror host attempts to mutate its production database."""


def config_path() -> Path:
    override = os.environ.get("MAP_AUTHORITY_CONFIG", "").strip()
    return Path(override).expanduser() if override else DEFAULT_CONFIG


def load_authority_config(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path).expanduser() if path is not None else config_path()
    if not target.exists():
        return {"mode": "standalone"}
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RemoteAuthorityRequired(
            f"MAP authority configuration is unreadable: {target}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RemoteAuthorityRequired(
            f"MAP authority configuration must be a JSON object: {target}"
        )
    mode = payload.get("mode", "standalone")
    if mode not in {"standalone", "authority", "mirror"}:
        raise RemoteAuthorityRequired(
            f"Unsupported MAP authority mode {mode!r} in {target}"
        )
    return payload


def is_production_db(path: str | Path) -> bool:
    candidate = Path(path).expanduser()
    try:
        return candidate.resolve(strict=False) == PRODUCTION_DB.resolve(strict=False)
    except OSError:
        return candidate.absolute() == PRODUCTION_DB.absolute()


def guard_production_write(
    path: str | Path,
    *,
    config: dict[str, Any] | None = None,
) -> None:
    """Reject production-DB writes on a configured mirror host.

    Isolated fixture databases remain writable so tests and experiments retain
    their existing behavior. A malformed configuration also fails closed.
    """

    if not is_production_db(path):
        return
    authority = config if config is not None else load_authority_config()
    if authority.get("mode") == "mirror":
        host = authority.get("authority_host", "configured authority")
        raise RemoteAuthorityRequired(
            "This host is a read-only MAP mirror. "
            f"Run the lifecycle operation through `map-authority` on {host}."
        )
