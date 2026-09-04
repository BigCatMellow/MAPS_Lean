#!/usr/bin/env python3
"""Sharded, self-bounding local test runner for the MAPS_Lean suite.

Why this exists
---------------
``python -m unittest discover -s tests`` is the authoritative check (CI runs it
in ``runtime-stack-tests.yml``), but locally the full suite runs for minutes with
no intermediate output. A dispatched worker that needs a local result before
pushing has, in practice, either run it foreground and hit a timeout (looks
hung), or backgrounded it and sat on a ``Monitor`` / wait-loop reading a
buffered-empty file -- burning its context lane and delivering nothing. See
``work/coordination/FRICTION_LOG.md`` (2026-09-03) and
``work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md``.

This runner removes the incentive to background the suite: it shards discovery by
top-level test module, runs each module as its own ``python -m unittest``
subprocess with a per-module timeout, and streams one line per module (plus a
heartbeat for a still-running module) to unbuffered stdout. Continuous output ->
never looks hung -> no reason to background it or ``Monitor`` it. The exit code
is trustworthy: non-zero iff any module failed, errored, or timed out, so there
is no need to pipe to ``tail`` for readability
(``feedback_pipe_to_tail_masks_exit_code``).

It is advisory. CI ``test`` remains the gate.

Each shard imports ``WARMUP_IMPORTS`` before loading its module, to reproduce an
import side effect that full alphabetical discovery provides and per-module
isolation otherwise loses (a latent circular import -- see that constant's
comment). The real fix is a separate PR.

Usage
-----
Run from the repo root (it discovers ``tests/`` relative to the cwd and exits 2
if it cannot find it).

    python scripts/run_tests_sharded.py [-k PATTERN] [--timeout-per-module SEC]
                                        [--jobs N] [--tests-dir DIR]

    -k PATTERN                substring filter on the module name (repeatable)
    --timeout-per-module SEC  per-module wall-clock cap (default 300)
    --jobs N                  parallel modules (default 1; parallel is opt-in
                              because some modules touch shared .maps/ fixtures)
    --tests-dir DIR           directory to discover test_*.py in (default: tests)
    --heartbeat SEC           heartbeat interval for a running module (default 30)

Stdlib only.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"
TIMEOUT = "TIMEOUT"

# Each shard runs its module in its own subprocess, in isolation. That isolation
# exposes a latent circular import (runtime/environment/__init__.py <->
# runtime/state/environment.py) that the full alphabetical `unittest discover -s
# tests` masks -- under discover, an earlier module imports `runtime.state`
# fully before any test_environment_* module is loaded, so the cycle resolves.
# Importing `runtime.state` first reproduces that ordering and makes the four
# test_environment_* modules pass in isolation too. Kept unconditional for
# determinism; only a genuinely-absent module is swallowed (ModuleNotFoundError)
# -- a present-but-broken warmup module raises ImportError and fails the shard
# loudly rather than masquerading as the known cycle.
# See work/coordination/FRICTION_LOG.md (2026-09-04 circular-import entry) and
# work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md ("Known
# limitation"). The real fix -- breaking the cycle -- is a separate PR.
WARMUP_IMPORTS = ("runtime.state",)

# Prelude injected into every shard subprocess: best-effort warmup, then run the
# named module via unittest and exit with its status code.
_SHARD_PRELUDE = (
    "import sys\n"
    "for _m in {warmups!r}:\n"
    "    try:\n"
    "        __import__(_m)\n"
    "    except ModuleNotFoundError:\n"
    "        pass\n"
    "import unittest\n"
    "unittest.main(module=None, argv=['run_tests_sharded', {module!r}, '-v'])\n"
)


def _shard_cmd(module: str) -> list[str]:
    code = _SHARD_PRELUDE.format(warmups=list(WARMUP_IMPORTS), module=module)
    return [sys.executable, "-c", code]


_emit_lock = threading.Lock()


def _emit(line: str) -> None:
    """Write one line to stdout and flush immediately (never buffer to end).

    Locked so a heartbeat thread and a result line cannot interleave mid-flush
    under ``--jobs > 1``.
    """
    with _emit_lock:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


def discover_modules(tests_dir: Path, patterns: list[str]) -> list[str]:
    """Return sorted dotted module names (``tests.test_foo``) under *tests_dir*.

    Mirrors ``unittest discover -s tests`` for this repo: no ``tests/__init__.py``,
    no custom ``load_tests`` -- discovery is just ``tests/test_*.py``.
    """
    names = []
    for path in sorted(tests_dir.glob("test_*.py")):
        stem = path.stem
        if patterns and not any(p in stem for p in patterns):
            continue
        names.append(f"{tests_dir.name}.{stem}")
    return names


@dataclass
class ModuleResult:
    module: str
    status: str
    duration: float
    output: str


def _run_one(module: str, timeout: float, repo_root: Path,
             heartbeat: float) -> ModuleResult:
    start = time.monotonic()
    proc = subprocess.Popen(
        _shard_cmd(module),
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    done = threading.Event()

    def _beat() -> None:
        while not done.wait(heartbeat):
            elapsed = time.monotonic() - start
            _emit(f"...     {module:<45} running {elapsed:5.0f}s")

    beater = threading.Thread(target=_beat, daemon=True)
    beater.start()

    try:
        out, _ = proc.communicate(timeout=timeout)
        status = PASS if proc.returncode == 0 else FAIL
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()
        status = TIMEOUT
    except Exception as exc:  # pragma: no cover - defensive
        try:
            proc.kill()
        except Exception:
            pass
        out = f"{type(exc).__name__}: {exc}"
        status = ERROR
    finally:
        done.set()
        beater.join(timeout=1)

    duration = time.monotonic() - start
    return ModuleResult(module, status, duration, out or "")


def run(modules: list[str], timeout: float, jobs: int, repo_root: Path,
        heartbeat: float) -> list[ModuleResult]:
    results: list[ModuleResult] = []
    total = len(modules)

    def _record(res: ModuleResult) -> None:
        tag = res.status if res.status != PASS else PASS
        note = f"(>{timeout:.0f}s)" if res.status == TIMEOUT else f"({res.duration:5.1f}s)"
        _emit(f"{tag:<7} {res.module:<45} {note}")

    if jobs <= 1:
        for i, module in enumerate(modules, 1):
            _emit(f"[{i}/{total}] {module} ...")
            res = _run_one(module, timeout, repo_root, heartbeat)
            _record(res)
            results.append(res)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            futs = {
                pool.submit(_run_one, m, timeout, repo_root, heartbeat): m
                for m in modules
            }
            for fut in concurrent.futures.as_completed(futs):
                res = fut.result()
                _record(res)
                results.append(res)

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sharded, self-bounding local test runner (advisory; CI is the gate).",
    )
    parser.add_argument("-k", dest="patterns", action="append", default=[],
                        metavar="PATTERN",
                        help="substring filter on module name (repeatable)")
    parser.add_argument("--timeout-per-module", dest="timeout", type=float,
                        default=300.0, metavar="SEC")
    parser.add_argument("--jobs", type=int, default=1, metavar="N")
    parser.add_argument("--tests-dir", default="tests", metavar="DIR")
    parser.add_argument("--heartbeat", type=float, default=30.0, metavar="SEC")
    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_absolute():
        tests_dir = repo_root / tests_dir
    if not tests_dir.is_dir():
        _emit(f"error: tests dir not found: {tests_dir}")
        return 2

    modules = discover_modules(tests_dir, args.patterns)
    if not modules:
        _emit(f"error: no test modules matched under {tests_dir}"
              + (f" for -k {args.patterns}" if args.patterns else ""))
        return 2

    _emit(f"running {len(modules)} module(s), "
          f"timeout {args.timeout:.0f}s/module, jobs {args.jobs}")
    started = time.monotonic()
    results = run(modules, args.timeout, args.jobs, repo_root, args.heartbeat)
    wall = time.monotonic() - started

    bad = [r for r in results if r.status != PASS]
    passed = len(results) - len(bad)
    _emit("")
    _emit(f"summary: {len(results)} modules, {passed} passed, "
          f"{len(bad)} failed/errored/timed-out  ({wall:.0f}s wall)")
    if bad:
        _emit("failing modules:")
        for r in bad:
            _emit(f"  {r.status:<7} {r.module}")
        _emit("")
        _emit("--- output from failing modules ---")
        for r in bad:
            _emit(f"===== {r.module} ({r.status}) =====")
            _emit(r.output.rstrip())
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
