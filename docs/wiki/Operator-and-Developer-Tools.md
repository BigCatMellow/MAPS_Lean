# Operator and Developer Tools

This page routes to useful current tooling. It is not a replacement for the
tool's `--help`, repository instructions, or the owning playbook.

Back to [[Home]].

## First run and fresh clone

For repository work, begin with
[`docs/FIRST_RUN.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md):
read `AGENTS.md`, recover the approved roadmap/task, then select one relevant
method from the playbook index.

For a new runtime installation, use the preview-first route in
[`docs/FRESH_INSTALL.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FRESH_INSTALL.md):

```bash
bash scripts/install_maps.sh
bash scripts/install_maps.sh --apply --run-smoke
```

The preview performs no writes. The installer creates project-local `.venv/`,
`.maps/state/`, and `.hcom/` state. hcom installation is optional and separate.
The smoke test uses a temporary directory and does not send messages or control
real provider sessions.

Windows currently uses the manual control-plane setup route rather than the
Bash installer.

## CLI discovery

The current top-level runtime CLI is:

```bash
python -m runtime.cli --help
```

Its important surface groups include task creation/shaping/claim/submission,
trace and status, context planning, runs and session binding, recovery, flow,
review, outcomes, operators, Skills, and frozen regression cases.

Use the subcommand's live `--help` before executing a state-changing or
enforcement path. The Wiki explains intent and boundaries; the CLI defines the
current accepted arguments.

## Local test runner

CI's authoritative test is still the normal full unit-test discovery. For
local work, use:

```bash
python scripts/run_tests_sharded.py
```

The sharded runner executes each top-level test module in its own subprocess,
streams progress and heartbeats, imposes a per-module timeout, and returns a
non-zero exit if any module fails, errors, or times out. This prevents long
silent foreground runs from being mistaken for a hung process.

Useful options include repeated `-k` module filters, `--timeout-per-module`,
`--heartbeat`, and opt-in `--jobs`. Parallel jobs are not the default because
some tests touch shared fixtures. The runner is a local aid; CI `test` remains
the gate.

## Coordination housekeeping

[`scripts/coordination_housekeeping.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/scripts/coordination_housekeeping.py)
handles two narrow, mechanical GitHub backlog problems:

- promote a draft only when current-head handoff evidence exists and CI is
  green; and
- retarget a stacked PR whose base branch was squash-merged, but only when the
  prior branch history identifies one unambiguous new base.

It never merges, approves, closes, or edits PR content. Normal invocation is a
dry run; `--apply` performs only those bounded changes. The scheduled workflow
is a safety floor, not a substitute for a live integration/backlog rescan.

## Stale-worktree reporting

The same script can inspect local worktrees:

```bash
python scripts/coordination_housekeeping.py --stale-worktrees
python scripts/coordination_housekeeping.py --stale-worktrees --stale-days 14
```

Report mode labels missing-directory registrations and live worktrees whose
last commit is older than the threshold. `--apply` runs `git worktree prune`
for missing-directory registrations only. It never removes a live worktree
directory or deletes a branch.

Writable dispatched work must still follow
[`playbook/WORKTREE_ISOLATION.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/WORKTREE_ISOLATION.md).

## Spiderweb information-integrity checks

Spiderweb is an advisory scan for broken routing, isolated durable records,
duplicate IDs, stale pending records, and similar information-structure risks.
It does not create task truth or automatically repair findings.

Run the current checker through
[`scripts/check_spiderweb.py`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/scripts/check_spiderweb.py).
By default it excludes:

- `.git`, `.venv`, `.maps`, `.hcom`, caches, and `node_modules`;
- historical/archive and imported context roots; and
- `.claude/worktrees/`, because local worktree copies would create duplicate
  records and false broken-link findings.

Worktrees can be included deliberately with `--include-worktrees`. Spiderweb
findings remain advisory evidence until current sources confirm a real defect
and a separately authorized repair path handles it.

## Merge gate

Repository `main` merges use:

```bash
python scripts/opcmd_merge.py --pr NUMBER --authz HCOM_MESSAGE_ID
```

Use `--dry-run` to verify authorization/HOLD checks and print the intended
merge without writing the ledger or merging. See
[[Review, Authority and Merge Safety]] for the governance boundary.

## Useful source routes

| Need | Source |
| --- | --- |
| Select a method | [`playbook/INDEX.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/INDEX.md) |
| Runtime responsibility/setup | [`playbook/CONTROL_PLANE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/CONTROL_PLANE.md) |
| Find a durable work record | [`work/README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/README.md) |
| Capability/roadmap question | [`work/roadmaps/README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/README.md) |
| Live role-bound PR coordination | [`work/coordination/README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/coordination/README.md), then GitHub |
| Cross-session continuation | [`state/CURRENT.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/state/CURRENT.md), linked handoff, then GitHub |

Do not browse large directories when one of these routes already names the
authoritative owner.
