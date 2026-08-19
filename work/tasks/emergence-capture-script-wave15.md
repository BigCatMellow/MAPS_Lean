# Task: Lean-native Emergence (E/I) capture script

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `Claude / implementation agent`
- Risk: `LOW`
- Goal: give the Emergence and Improvement protocol (`playbook/EMERGENCE.md`) a small, working capture tool that fits this Lean runtime, and actually use it on this arc's own recent work.

## Inputs and source of truth

- Inputs: `playbook/EMERGENCE.md` (the whole spec for this task -- observe/connect/synthesize/name/test/promote; capture "the observation, source/context, potential value, and the smallest next test"); `legacy/MAP-System/MAP_System/scripts/map_emergence.py` (read for background only, not ported -- see below); `runtime/README.md` and the roadmap's non-goals ("no second mutable task/session authority database"; active runtime code must not import from `legacy/`).
- Authoritative source: `playbook/EMERGENCE.md` itself defines the only fields and workflow this script implements. Promotion decisions are governed by `playbook/TASK_LIFECYCLE.md`, which this script does not touch.

## Why the legacy script was not ported

`legacy/MAP-System/MAP_System/scripts/map_emergence.py` (1185 lines) is built around a decommissioned "task_graph" file concept this Lean runtime replaced with SQLite state under `runtime/state/`, and carries ID-allocation locks (`fcntl`), staleness checks, compaction, and an index/graph file -- all machinery tied to that legacy structure. This repo's own convention forbids a second mutable task/session authority store and forbids active runtime code importing from `legacy/`. `scripts/emergence.py` is a new, independent implementation: plain files under `work/<kind>s/`, UUID-derived IDs (no lock needed -- collisions are structurally avoided rather than prevented by mutual exclusion), and no promotion/staleness/compaction commands at all, since `EMERGENCE.md` says promotion is a deliberate decision, not an automated step.

## Design note: what was deliberately left out

- No `synthesis` or `promotion` kind. `EMERGENCE.md` describes the fields for insight/idea/experiment records (observation, source, value, next test); synthesis and promotion are named as steps in the observe->promote chain, not additional record shapes with distinct required fields the spec describes. Promotion in particular is explicitly a human/task-lifecycle act ("only an approved/promoted item can expand implementation scope"), so it has no `emergence.py` command -- promoting something means writing a task doc under `work/tasks/` by hand.
- No index file, ID registry, or lock. `list` reads `work/<kind>s/*.md` directly from disk each time; there is nothing to keep in sync.
- No validation/staleness pass. Nothing in `EMERGENCE.md` asks for one; adding it would be scope creep past what the protocol calls for.

## Change boundary

- MAY CHANGE: `scripts/emergence.py` (new), `tests/test_emergence_capture.py` (new), this task file, and the captured record files this task itself generates under `work/insights/`, `work/ideas/`.
- MUST NOT CHANGE: anything under `legacy/`; `runtime/state/*`; any existing task/session store; no import of `legacy/` code.
- OPERATOR APPROVAL REQUIRED: turning any captured idea/insight in this PR into an actual implementation task -- that is a promotion decision per `TASK_LIFECYCLE.md`, out of scope here.

## Decision authority

- Owner may decide: exact markdown record shape, ID format (`<PREFIX>-<8 hex>`), directory layout (`work/insights/`, `work/ideas/`, `work/experiments/`), CLI argument names.
- Owner must escalate: any request to add a promotion/auto-task-creation command, or to make captured records feed back into `runtime/state/` (that would create the second mutable authority store the roadmap forbids).

## Acceptance criteria

- [x] `scripts/emergence.py capture <kind> --title ... --observation ... --source ... --value ... --next-test ...` writes a well-formed markdown file to `work/<kind>s/` with a stable, collision-safe UUID-derived ID, for `kind` in `insight`/`idea`/`experiment`.
- [x] `capture` rejects an unknown `kind` (both at the CLI level via argparse `choices`, and at the `capture()` function level via `ValueError`).
- [x] `scripts/emergence.py list [kind]` reads existing records back read-only (id, title, kind, date), with no kind argument listing all three folders.
- [x] No promotion, staleness, validation, or compaction command exists.
- [x] No import from `legacy/`.
- [x] `tests/test_emergence_capture.py` covers: well-formed capture, stable ID format, list round-trip, no ID collisions across many captures, rejection of an unknown kind. All pass.
- [x] The script was actually used: 4 genuine records captured from this arc's own recent work (see below), committed as real content in this PR.
- [x] Full test suite passes.

## What was captured, and why

- `work/insights/...-INSIGHT-29a10ad4.md` -- `check_review_evidence.py`'s `head_sha` walk-back deliberately stops at merge commits (correct, but it's the direct cause of PR #109 needing four review-evidence rebinds across its sync cycles). Worth naming explicitly so a future session doesn't "fix" the walk-back into a real hole.
- `work/insights/...-INSIGHT-75785aae.md` -- `grep -rn "HarnessService(" .` (excluding `legacy/`) finds zero production callers outside `tests/`; several roadmap waves (H4/H5/L6/SEC4, PRs #100/#101/#106/#107/#112) built out the Harness contract/adapter layer without ever wiring a real caller. Not necessarily wrong, but worth flagging as a named risk before adding more surface area.
- `work/ideas/...-IDEA-582cc671.md` -- name a "zero-diff-confirmed re-review" effort tier in `playbook/MODEL_CAPABILITY_ROUTING.md`, since three of PR #109's four review-evidence cycles were full from-scratch re-reviews of a pure main-sync merge that could have been a fast re-attestation instead.
- `work/ideas/...-IDEA-20615e4d.md` -- this task's own process notes required an isolated worktree to avoid colliding with other concurrent agent sessions sharing `~/Projects/MAPS_Lean`; worth checking whether that's ever actually bitten a session, and if so, standardizing the isolated-worktree convention somewhere more durable than one task's briefing.

`EXP-A` skill-routing benchmark and false-positive activation from `_select_skills`'s token-overlap rule were considered but skipped: no PR or `work/notes/` doc for that benchmark had landed as of this task (checked `gh pr list` and `work/notes/`), so there was no real evidence yet to capture against, and inventing a synthetic false-positive case would not be a genuine observation.

## Verification

- `python3 -m unittest tests.test_emergence_capture -v`
- `python3 -m unittest discover -s tests -v` (full suite)

## Follow-up (not in this PR)

- None of the four captured records are promoted. Any of them becoming a real task requires a separate deliberate promotion decision per `TASK_LIFECYCLE.md`.
