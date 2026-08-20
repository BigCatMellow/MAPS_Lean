# Roadmap 06 — Portable Deployment (MAPS on external projects)

- State: `DRAFT`

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: define how MAPS's control-plane discipline (task truth, harness,
hcom, review-evidence) can be installed and used against an **external
project's repository** — a codebase that is not MAPS_Lean itself, has its own
language/stack/conventions, and did not previously use MAPS at all.

**Parent master roadmap:** `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`

**Sibling roadmaps:** `01-harness-mechanics.md`, `02-procedural-knowledge-and-skills.md`,
`03-environment-and-reproducibility.md`, `04-agentic-security.md`,
`05-learning-and-evaluation.md`

## Why letter prefix `D`

Roadmaps 01–05 use phase prefixes `H` (Harness), `S` (Skills), `E`
(Environment), `SEC` (Security), `L` (Learning) — confirmed by grepping phase
IDs across `work/roadmaps/agent-harness-capabilities/*.md` and
`work/roadmaps/CAPABILITY_CHECKLIST.md`; the only other letters that appear
(`F`, `T`) are metric/tier labels inside prose (`F1` score, `T0`–`T3` trust
tiers), not phase-ID prefixes, so they are not actually taken. `D` is unused
and reads naturally as **Deployment/Distribution** — this roadmap is about
deploying/distributing MAPS's control plane to a target outside MAPS_Lean,
which is a distinct concern from how the harness, skills, environment,
security, or learning subsystems work once MAPS is already running somewhere.
Phases below are `D1`, `D2`, ...

---

## Current reality

- Checked facts:
  - `scripts/install_maps.sh` computes its target root as
    `ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` — i.e. **the
    parent directory of the script's own location**, not the caller's current
    working directory and not an operator-supplied path. There is no `--target`,
    `--path`, or equivalent flag. Concretely: this script cannot currently be
    pointed at a different repository at all. It only ever sets up
    `.venv/`, `.maps/state/`, `.hcom/` inside the MAPS_Lean clone that contains
    it. The "wherever it's run" framing only holds in the narrow sense that a
    given *clone location* of MAPS_Lean can be anywhere on disk — it does not
    mean an arbitrary unrelated project can be targeted.
  - `--apply` mode runs `"$PY" -m pip install -r "$ROOT/runtime/requirements.txt"`
    — a hard dependency on MAPS_Lean's own `runtime/` package tree existing
    alongside the script. There is no packaged/importable distribution of
    `runtime/` (no `pyproject.toml`/`setup.py`/wheel build checked in this
    clone) that an external project could `pip install` without vendoring or
    cloning MAPS_Lean's `runtime/` source directly.
  - `docs/FRESH_INSTALL.md`'s smoke command (`runtime.smoke`) explicitly "does
    not... touch the real project task database" and runs against a temporary
    directory — it verifies the control-plane *mechanism* works, not that it
    is usable as a control plane *for a different project's actual tasks*.
  - `playbook/CONTROL_PLANE.md` and `docs/CONTROL_PLANE_SETUP.md` describe
    `.maps/state/maps.db`, `.maps/state/langgraph-checkpoints.db`, and
    `.hcom/` as project-local state, and describe a "Target layout" that
    nests `.maps/` under a `MAPS_Lean/` tree containing `runtime/`, `tests/`,
    etc. — i.e. the documented setup assumes the *code implementing the
    control plane* (Python `runtime/state`, `runtime/harness`,
    `runtime/communication`, etc.) and the *project the control plane governs*
    are the same repository. Nothing in either doc distinguishes "the repo
    MAPS's own code lives in" from "the repo MAPS is managing tasks for."
  - `runtime/state/` (SQLite schema/API), the task/roadmap/review Markdown
    conventions (`work/tasks/*.md`, `work/roadmaps/*.md`,
    `work/reviews/pr-<N>-review-evidence.md`), `AGENTS.md`, and
    `scripts/check_review_evidence.py` are all written assuming the repo they
    operate in **is** MAPS_Lean: paths are relative to this repo's root, the
    task template (`templates/task.md`) and roadmap template
    (`templates/roadmap.md`) are stored in and read from `templates/` here,
    and the review-evidence CI gate (`scripts/check_review_evidence.py`,
    wired via GitHub branch protection per `docs/CHECKS_AND_BALANCES.md`) is
    a MAPS_Lean-repo-specific script and workflow, not something that exists
    or is referenced from any other repository.
  - Checked the master roadmap's §6 capability inventory (`work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`,
    all 34 items) and all five sub-roadmaps' phase lists (`grep`'d for
    `external project`, `other repo`, `another repo`, `target repo`,
    `target project`, `arbitrary project`, `foreign repo`, `non-MAPS`,
    `portable install` across `work/roadmaps/`, `docs/`, `playbook/` — zero
    hits). §6.26 "Portable Run Records / trajectories" is about exporting a
    single run's evidence as a portable artifact, not about installing the
    control plane elsewhere. §6.13/6.14 (`EnvironmentSpec`/fingerprint) describe
    reproducing a *task's* execution environment, not relocating MAPS's own
    authority store to a different project. Nothing in the existing five
    roadmaps or the master inventory covers installing/targeting MAPS at an
    external project's repo. This is a genuine gap, not a duplicate.
- Evidence/source paths: `scripts/install_maps.sh`, `docs/FRESH_INSTALL.md`,
  `playbook/CONTROL_PLANE.md`, `docs/CONTROL_PLANE_SETUP.md`,
  `docs/CHECKS_AND_BALANCES.md`, `scripts/check_review_evidence.py`,
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6,
  `work/roadmaps/agent-harness-capabilities/{01..05}-*.md`.
- Important assumptions (not yet verified, flagged below as open questions):
  whether a target external project needs its own independent SQLite task
  database at all, whether the review-evidence CI gate pattern generalizes
  to non-GitHub-Actions targets, and how much of MAPS's Python-specific
  `runtime/` package a non-Python target project can realistically depend on.

## Definition of DONE

- Finished result: an operator can point a fresh agent at an arbitrary
  external repository X (not MAPS_Lean, previously unmanaged by MAPS) and,
  using only documented MAPS mechanisms:
  1. install a working, X-scoped task/review/roadmap discipline (not a copy
     of MAPS_Lean's own task database — X's own task truth, however heavy or
     light v1 decides that needs to be, per the open question below);
  2. shape one real task against X using the same task-record contract
     (`templates/task.md`-equivalent, or a documented lighter substitute)
     that MAPS uses for itself;
  3. carry that task through implement → independent review → merge on X's
     own repository, using MAPS's review-evidence discipline (or a documented,
     equivalent-strength adaptation of it) rather than ad hoc chat approval;
  4. do all of the above without MAPS_Lean's own `.maps/state/maps.db`,
     `work/tasks/`, or `work/reviews/` ever being touched by X's work — X's
     control-plane state and MAPS_Lean's must stay fully separate stores
     (extension of "One fact, one authority," master roadmap §4.1).
- Final proof: a real, observable pilot — one external repository, one real
  (not synthetic/toy) task, taken end-to-end through the flow above, with the
  resulting PR/merge on X and the review-evidence artifact both inspectable
  as evidence. A dry run against a throwaway/synthetic repo is useful
  intermediate evidence but does not itself satisfy DONE.
- Who can perform/inspect final proof: the operator, or an independent
  reviewer following the same review-evidence discipline this roadmap intends
  to port (self-certification by the implementing agent does not count, per
  `docs/CHECKS_AND_BALANCES.md`'s "do not self-approve substantive work").

## Boundaries

- In scope:
  - auditing exactly which parts of the current control plane are
    MAPS_Lean-repo-coupled versus genuinely portable;
  - designing (not yet building) an installer/CLI surface that can target an
    explicit external path rather than always resolving to its own script
    location;
  - designing a first, bounded version of task/review/roadmap discipline that
    a single external project can adopt;
  - designing how review-evidence-equivalent enforcement could work outside
    MAPS_Lean's specific GitHub-branch-protection setup;
  - identifying, not resolving, the packaging/distribution question (vendor
    `runtime/` vs. installable package vs. sibling-clone reference).
- Not doing (explicitly out of scope for this roadmap's v1):
  - solving every possible target language/stack combination — v1 may be
    scoped to Python-stack (or even zero-stack, convention-only) targets, and
    stack-specific onboarding packs for other ecosystems are later,
    `TRIGGERED` work (see D4);
  - assuming the full SQLite task-DB schema and API (`runtime/state/`) must be
    ported wholesale into every target project — a lighter, file-convention-only
    discipline (Markdown task files + a naming/status convention, no database)
    may be sufficient for v1; this is the highest-risk unknown, named below,
    and is **not resolved by this roadmap**;
  - multi-project/fleet management (one control plane governing many external
    projects at once) — this roadmap covers one external project at a time;
  - migrating or automating existing (non-MAPS) task trackers/CI in the
    target project — MAPS discipline is additive, not a replacement for
    whatever the target project already uses, unless the operator decides
    otherwise for a specific project;
  - building or shipping any runtime code — this roadmap is a design
    document only, consistent with this repo's convention that design-only
    tasks precede implementation for anything touching authority/policy
    questions (task truth and review discipline are exactly that).
- Effort limit: this roadmap itself (the design work) is a single bounded
  design task (see `work/tasks/portable-deployment-roadmap-design.md`). Any
  future phase below that starts consuming more than a few sessions without
  a working pilot should trigger a roadmap-trajectory checkpoint
  (`playbook/ROADMAP_TRAJECTORY_CHECK.md`) before continuing.
- Highest-risk unknown: **does an external target project need its own
  independent SQLite task-truth instance (full port of `runtime/state/`'s
  schema/API), or is a lighter, file-convention-only version of the
  discipline (status fields in Markdown task files, no database, no atomic
  claim/lease guarantees) sufficient for v1?** This is a genuine architecture
  fork, not a detail: the SQLite path buys atomic claims/leases/no-self-review
  enforcement but requires porting and running real database code inside a
  repo MAPS does not own and may have very different tooling/CI norms; the
  file-convention path is far cheaper to adopt but gives up mechanical
  enforcement (a human or agent could violate no-self-review by not noticing
  a status field) unless a lightweight validator hook is also designed.
  **This roadmap does not resolve this — it is recorded as an open question
  requiring an explicit operator decision (see below).** **RESOLVED
  2026-08-19: file-convention-only**, per the operator decisions recorded in
  Mission meeting below and in
  [`work/notes/2026-08-19-portable-deployment-operator-decisions.md`](../../notes/2026-08-19-portable-deployment-operator-decisions.md).
  The mechanical no-self-review enforcement gap this leaves is accepted for
  v1 (decision 3, best-effort review discipline) rather than closed by a
  validator hook — `D2a` may still design a lightweight validator if cheap,
  but it is not a v1 requirement.

## Backward plan

Work from DONE toward the present.

1. Immediately before DONE: an external project X has one real task that went
   through shape → implement → independent review → merge using documented,
   working MAPS-portable mechanisms, and the evidence is inspectable.
2. Before that: the chosen v1 discipline (full SQLite port or file-convention,
   per the operator's resolution of the highest-risk unknown) is implemented
   and smoke-verified against a real external repo, not just a synthetic
   fixture.
3. Before that: an installer/CLI surface exists that can target an explicit
   external path (`--target-repo <path>` or equivalent) instead of always
   resolving to its own script location, and a portability audit has
   confirmed which `runtime/` modules can run unmodified outside MAPS_Lean's
   own tree versus which are hard-coupled to it.
4. Before that: the operator has resolved the open questions listed below
   (SQLite-vs-convention, packaging/distribution model, review-evidence
   portability, v1 language/stack scope, and state-location) enough to commit
   to one concrete v1 design instead of two competing ones.
5. Current state: none of the above exists. `scripts/install_maps.sh` cannot
   target any repository other than the one it ships in; no design decision
   has been made; this roadmap document is the first artifact in the chain.

## Mission meeting

- Required: `YES` — this roadmap touches authority/policy questions (what
  counts as task truth and enforced review for a project MAPS does not own),
  which this repo's own convention requires design-first treatment for, and
  the backward plan depends on operator decisions this roadmap cannot make
  for itself.
- Questions to settle: the five open questions listed in "Boundaries" and
  "Mission meeting → Operator decisions needed" below; whether a synthetic
  throwaway repo or an operator-nominated real repo should be the first pilot
  target; whether v1 should assume the target repo grants MAPS write access
  to its own tree (committing `.maps/`/`work/` equivalents into X) or keep
  all MAPS-side state out of X entirely (referenced by path from a
  MAPS-owned control location).
- Assumptions accepted/rejected: none yet — this document is the input to
  that meeting, not a record of it having happened.
- Unresolved questions + owner: all five items below → operator. **RESOLVED
  2026-08-19** — see
  [`work/notes/2026-08-19-portable-deployment-operator-decisions.md`](../../notes/2026-08-19-portable-deployment-operator-decisions.md)
  for the full record.
- Operator decisions needed:
  1. SQLite task-truth port vs. lightweight file-convention-only discipline
     for v1 (the highest-risk unknown, above). **Decided: lightweight
     file-convention-only** — Markdown files + status convention + git, no
     database, no atomic claim/lease guarantees.
  2. Distribution model: vendor/copy `runtime/` into each target project,
     build an installable Python package other projects `pip install`, or
     keep MAPS_Lean as a sibling clone that a lightweight adapter in the
     target project calls out to. **Decided: sibling-clone + lightweight
     adapter.** No packaged/pip-installable distribution for v1.
  3. How strictly the review-evidence/CI enforcement pattern
     (`scripts/check_review_evidence.py` + GitHub branch protection) must be
     replicated in the target project versus treated as best-effort guidance
     — material because not every target repo uses GitHub, or CI at all.
     **Decided: best-effort discipline, not a hard CI gate**, for v1. The
     GitHub Actions pattern may optionally be offered/documented if the
     target project happens to use GitHub, but is not required for v1
     success.
  4. v1 language/stack scope: is v1 explicitly Python-stack-only (since
     `runtime/` is Python), or must the first pilot handle a non-Python
     target project's build/test tooling too? **Decided: stack-agnostic.**
     Decision 1 means no MAPS Python runtime code needs to run inside the
     target project for v1, so there is no reason to restrict to
     Python-stack targets.
  5. Where does the target project's MAPS-managed state live: committed
     inside the external repo itself (visible to and possibly confusing for
     that repo's own contributors) versus kept in a separate MAPS-owned
     location that references the external repo by path (keeps X's tree
     untouched but adds an indirection RnS/hcom/task tooling must resolve
     correctly). **Decided: committed inside the external repo itself**,
     under a clearly-named directory (e.g. `.maps/`), visible to that
     repo's own contributors.
- Roadmap changes: `D2` (previously a single placeholder "implement the
  operator-chosen v1 discipline" item, blocked on all five decisions above)
  is split into three concrete design/planning phases — `D2a`, `D2b`, `D2c`
  — now that the architecture fork is resolved. See "First wave selected"
  and Phase 1 below. This split is scoping, not implementation: all three
  remain design/planning tasks per this roadmap's own boundary against
  building or shipping runtime code.
- First pilot target selected: **Chain Shovel**, a real external game-dev
  project (unrelated to MAPS_Lean) with an already-identified bounded bug
  (ES-module-split + logger issue). Chosen over a synthetic/throwaway repo
  because Definition of DONE requires a real, observable pilot; recorded in
  the same decision note linked above. Running the pilot itself is `D3`,
  still future work.
- First wave selected: `D0` (portability audit) and `D1` (installer targeting
  design) only; both are research/design tasks that do not depend on the
  open questions above being resolved yet. **Now that the five operator
  decisions are recorded, the next wave is `D2a`, `D2b`, `D2c`** (see Phase 1)
  — all three are design/planning tasks, not implementation, and do not by
  themselves authorize running the Chain Shovel pilot (`D3`).

## First wave

- [x] `D0-portability-audit` — produce a written audit of every `runtime/`
  module `install_maps.sh`/`runtime.smoke` touch, classified as
  "path-relative to MAPS_Lean only," "Python-stdlib-portable," or "needs a
  real interface boundary before another repo could import it" — Owner:
  research agent (RESEARCH task, no code changes). Completed in
  `work/notes/2026-08-20-portable-deployment-d0-portability-audit.md`.
- [x] `D1-installer-targeting-design` — design (Markdown design note, not
  code) an explicit `--target-repo <path>` surface for
  `scripts/install_maps.sh`'s successor/extension, including what it must
  refuse to do (e.g. never silently write into MAPS_Lean's own `.maps/state/`
  when a target is given) — Owner: design agent (PLANNING task, no code
  changes), depends on `D0`. Completed in
  `work/notes/2026-08-20-portable-deployment-d1-installer-targeting-design.md`.

Both are read-only/design-only and do not require the operator decisions
above to start; every later task in Phase 1+ does.

## Phase 0 — Foundation

- [x] `D0` — Portability audit (see First wave).
- [x] `D1` — Installer targeting design (see First wave).
- [x] Operator resolves the five open questions in "Mission meeting."

## Phase 1 — Delivery (bounded v1)

`D2` is split into three design/planning phases, now that the operator's
2026-08-19 decisions (see Mission meeting, and the decision note linked
there) have resolved the architecture fork. All three are design documents
— Markdown design notes and template drafts, not code — consistent with
this roadmap's boundary against building or shipping runtime code. `D3`
(actual pilot execution) remains the only phase that produces a real PR
against an external repo, and is blocked on all three.

- [x] `D2a-file-convention-design` — design the exact v1 file-convention
  shape for a target repo's `.maps/` directory: the status vocabulary for
  task files (a lighter equivalent of `templates/task.md`'s `Status`/`AGI
  status` fields), the directory layout for tasks/reviews/roadmap-equivalent
  documents, and what a "review-evidence" Markdown artifact looks like under
  the best-effort (non-CI-gated) enforcement model decided above. Output:
  `work/notes/2026-08-20-portable-deployment-d2a-file-convention.md` plus
  draft templates under `templates/portable-deployment/`, not a working
  installer. Owner: design agent (PLANNING task, no code changes). Depends
  on the operator decisions (resolved).
- [x] `D2b-adapter-design` — design the sibling-clone adapter: what small
  script/tooling lives inside the target project's own tree and calls out
  to a sibling MAPS_Lean clone (e.g. to reuse `templates/`, run
  `scripts/check_review_evidence.py`-equivalent checks optionally, or read
  playbook guidance), what interface boundary it crosses, and what it must
  refuse to do (e.g. never write into MAPS_Lean's own `.maps/state/` or
  `work/tasks/`). Output: a design note, not a working adapter script.
  Owner: design agent (PLANNING task, no code changes). Depends on `D2a`
  (the adapter has to know what it's adapting to). Completed in
  `work/notes/2026-08-20-portable-deployment-d2b-sibling-adapter-design.md`.
- [x] `D2c-chain-shovel-pilot-plan` — write the concrete plan for running
  `D3` against Chain Shovel: which real task will be shaped (the
  ES-module-split + logger bug), what the `.maps/` layout will look like in
  that repo specifically, who/what performs independent review given Chain
  Shovel's own CI/hosting setup (not assumed to be GitHub Actions), and what
  "done" looks like for that one pilot task. Output: a design/plan note, not
  a pilot run — actually executing against Chain Shovel's repo is `D3`, a
  separate future task this session does not perform (no repo access here).
  Owner: design agent (PLANNING task, no code changes, no repo access).
  Depends on `D2a` and `D2b`. Completed in
  `work/notes/2026-08-20-portable-deployment-d2c-chain-shovel-pilot-plan.md`;
  target-specific facts are explicit D3 preflight gates, not assumptions.
- [ ] `D3` — First real pilot: Chain Shovel, one real task (the
  ES-module-split + logger bug), shape → implement → independent review →
  merge, using only the `D2a`/`D2b` v1 mechanism per the `D2c` plan. This is
  the roadmap's final proof (see Definition of DONE). Not started; blocked
  on target access/authority and an AGI-ready execution task under the D2c
  plan; no external-project pilot has been attempted.

## Phase 2 — Integration and final proof

- [ ] Integrate pilot findings back into this roadmap and
  `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- [ ] Independent review of the full D2/D3 delta (code + the pilot's actual
  external-repo evidence, not just MAPS_Lean-side diffs).
- [ ] Perform the Definition-of-DONE final proof: inspect the merged
  external-repo PR and its review-evidence artifact.

## Later, explicitly `TRIGGERED` (not v1)

- `D4` — Stack-specific onboarding packs for non-Python target ecosystems,
  triggered only once a real non-Python pilot is requested; do not
  pre-build support for stacks with no concrete target yet.
- `D5` — Cross-project review/CI portability beyond GitHub Actions (e.g.
  GitLab CI, no-CI repos), triggered only once a real target using a
  different CI system is requested.
- `D6` — Multi-project/fleet management (one control plane, many external
  projects concurrently) — explicitly out of scope until single-project v1
  is proven; premature multi-project design risks the same
  second-task-authority mistake the master roadmap's §4.1 warns against.

## Checkpoints

- Checkpoint: after Phase 0 (`D0`/`D1` complete, operator decisions recorded).
  - Evidence reviewed: portability audit findings, installer-targeting design
    note, recorded operator decisions.
  - Decision: `CONTINUE | CHANGE | CUT SCOPE | RESEARCH | STOP` (to be made at
    that checkpoint, not pre-decided here).
  - Reason: the open questions materially change what Phase 1 builds; do not
    start D2 implementation before they are answered.
  - Next action: proceed to D2 only with an operator-recorded decision on all
    five questions, or scope D2 down to whichever subset is resolved.
  - Re-plan if: the audit finds the "lightweight file-convention" path is
    infeasible for mechanical no-self-review enforcement, or finds the SQLite
    path is infeasible to run inside a plausible external target's own CI.
- Checkpoint: after `D3` (first real pilot attempted).
  - Evidence reviewed: pilot's actual merged PR, review-evidence artifact,
    and any friction/blockers hit during the pilot.
  - Decision: `CONTINUE | CHANGE | CUT SCOPE | RESEARCH | STOP`.
  - Reason: the pilot is the first real-world test of every design decision
    made in Phase 0; treat its friction as evidence, not as noise to
    explain away.
  - Next action: if the pilot succeeds cleanly, promote `D2`'s pattern from
    "one bounded v1" toward documented general guidance; if it does not,
    re-open the Phase 0 open questions with the pilot's evidence before
    trying a second external project.
  - Re-plan if: the pilot reveals the chosen state-location model
    (committed-in-X vs. referenced-by-path) causes real confusion/conflict
    for X's own contributors, or the review-evidence substitute proves too
    weak to actually prevent self-approval in practice.
