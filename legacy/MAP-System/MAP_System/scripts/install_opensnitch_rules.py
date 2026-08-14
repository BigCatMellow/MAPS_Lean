#!/usr/bin/env python3
"""Validate and install the MAP-owned OpenSnitch rules without touching others."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any


MAP_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = MAP_ROOT / "templates" / "install" / "opensnitch"
DEFAULT_RULES_DIR = Path("/etc/opensnitchd/rules")
RULE_FILES = (
    "map-kudu-ruki-ssh.json",
    "map-kudu-hcom-relay.json",
)


class RuleError(RuntimeError):
    """Raised when a managed rule is unsafe or malformed."""


def load_rule(path: Path) -> dict[str, Any]:
    try:
        rule = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuleError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(rule, dict):
        raise RuleError(f"{path}: rule must be a JSON object")
    return rule


def operator_terms(operator: dict[str, Any]) -> list[dict[str, Any]]:
    if operator.get("type") != "list":
        return [operator]
    terms = operator.get("list")
    if not isinstance(terms, list) or not terms:
        try:
            terms = json.loads(operator.get("data", ""))
        except (TypeError, json.JSONDecodeError) as exc:
            raise RuleError("compound operator has no valid term list") from exc
    if not all(isinstance(term, dict) for term in terms):
        raise RuleError("compound operator terms must be objects")
    return terms


def validate_rule(filename: str, rule: dict[str, Any]) -> None:
    expected_name = filename.removesuffix(".json")
    for key, expected in (
        ("name", expected_name),
        ("enabled", True),
        ("precedence", True),
        ("action", "allow"),
        ("duration", "always"),
    ):
        if rule.get(key) != expected:
            raise RuleError(f"{filename}: {key} must be {expected!r}")

    operator = rule.get("operator")
    if not isinstance(operator, dict):
        raise RuleError(f"{filename}: operator must be an object")
    terms = operator_terms(operator)
    actual = {
        (term.get("type"), term.get("operand"), str(term.get("data")))
        for term in terms
    }

    if filename == "map-kudu-ruki-ssh.json":
        required = {
            ("simple", "process.path", "/usr/bin/ssh"),
            ("simple", "dest.ip", "192.168.1.153"),
            ("simple", "dest.port", "22"),
        }
        if actual != required:
            raise RuleError(
                f"{filename}: SSH terms must be exactly process, RUKI IP, and port 22"
            )
    elif filename == "map-kudu-hcom-relay.json":
        required = {
            ("simple", "process.path", "/home/mellow/.local/bin/hcom"),
        }
        if actual != required:
            raise RuleError(f"{filename}: hcom must be restricted to its exact path")
    else:
        raise RuleError(f"unmanaged rule filename: {filename}")


def validated_payloads(template_dir: Path = TEMPLATE_DIR) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    for filename in RULE_FILES:
        rule = load_rule(template_dir / filename)
        validate_rule(filename, rule)
        payloads[filename] = (
            json.dumps(rule, indent=2, sort_keys=False) + "\n"
        ).encode("utf-8")
    return payloads


def install_payloads(payloads: dict[str, bytes], rules_dir: Path) -> tuple[int, int]:
    rules_dir.mkdir(parents=True, exist_ok=True)
    changed = 0
    unchanged = 0
    for filename, payload in payloads.items():
        target = rules_dir / filename
        if target.is_file() and target.read_bytes() == payload:
            unchanged += 1
            continue

        descriptor, staged_name = tempfile.mkstemp(
            prefix=f".{filename}.", dir=rules_dir
        )
        staged = Path(staged_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            staged.chmod(
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
            )
            os.replace(staged, target)
            changed += 1
        finally:
            staged.unlink(missing_ok=True)
    return changed, unchanged


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rules-dir",
        type=Path,
        default=DEFAULT_RULES_DIR,
        help="OpenSnitch rules directory (default: /etc/opensnitchd/rules)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate templates without writing anything",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        payloads = validated_payloads()
        if args.check:
            print(f"validated={len(payloads)}")
            return 0
        if args.rules_dir == DEFAULT_RULES_DIR and os.geteuid() != 0:
            raise RuleError(
                "installing into /etc requires root; run this script with pkexec or sudo"
            )
        changed, unchanged = install_payloads(payloads, args.rules_dir)
    except (OSError, RuleError) as exc:
        print(f"OpenSnitch rule install error: {exc}", file=sys.stderr)
        return 1
    print(f"changed={changed} unchanged={unchanged} rules_dir={args.rules_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
