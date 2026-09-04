# Design note: E/I reframe — Imagine → Capture → Promote, with a trajectory-check anchor

- Status: **DESIGN NOTE ONLY** — no implementation in this note's PR. Proposes edits to
  `playbook/EMERGENCE.md`, `playbook/ROADMAP_TRAJECTORY_CHECK.md`,
  `playbook/REPAIR_AND_LEARNING.md`, `playbook/INDEX.md` (one boundary line), and a
  first backlog sweep of `work/insights/` + `work/ideas/`. Companion decision record:
  `work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md` (skeleton,
  `PROPOSED`).
- Provenance: assembled by `maps-lean-mimi` (session-27 coordinator) from two
  operator-directed drafts authored by `maps-lean-tuba` (pr278-reviewer lane,
  2026-09-03), preserved at `/home/home/maps-ei-handoff/`
  (`ei-reframe-design-DRAFT.md`, `ei-phase3-and-DEC003-DRAFT.md`). Implementation and
  review of this note MUST be independent of `tuba`.
- Source of truth: `playbook/EMERGENCE.md`, `playbook/ROADMAP_TRAJECTORY_CHECK.md`,
  `playbook/REPAIR_AND_LEARNING.md` §"Relationship to operational lessons",
  `playbook/INDEX.md` §"Adding or changing a method", `scripts/emergence.py`,
  `work/insights/*`, `work/ideas/*`,
  `tests/test_documentation_sprawl.py` (`PLAYBOOK_SURFACE_BUDGET = 24`).
- Review: verification-only (design note; changes nothing executable). Not to be
  authored/merged by the reviewer lane — routed by the coordinator as a normal
  design → impl PR pair.

---

## 1. Problem statement

E/I (Emergence and Improvement, `playbook/EMERGENCE.md`) has flatlined.

`python3 scripts/emergence.py list` — until the 2026-09-03 Emergence pass (#279),
**5 records, every one dated 2026-08-19**: 3 insights, 2 ideas. **Zero captured
between** — across ~100 merged PRs, 21 roadmap trajectory checks, dozens of
sessions, and a continuously-growing FRICTION_LOG. The 2026-08-19 burst was a
single session that happened to be working *on* the emergence script itself
(`IDEA-20615e4d`'s own source line confirms it). The #279 pass (13 records) was
also operator-directed and one-off — it does not establish a cadence.

This is not a creativity shortage. E/I is **structurally unanchored**:

| Every other epistemic protocol has… | E/I has… |
|---|---|
| a **trigger** — FRICTION_LOG: "an entry is REQUIRED when [named conditions]" | "notice freely" — no moment that obliges or prompts a pass |
| a **cadence** — trajectory check runs at every work-arc boundary | none |
| a **consumption venue** — FRICTION_LOG is walked every trajectory pass; each open entry MUST reach a disposition | none — captured records just sit; `check_spiderweb.py` flags them `ORPHAN_CANDIDATE` |
| **loop closure** — capture → severity → recurrence → countermeasure → verified close | file a structured record → nothing ever happens to it |

Two compounding factors:

- **Defensive framing.** `EMERGENCE.md` opens "Discovery is valuable, but it must
  not hijack an assigned task" and closes "notice freely, act carefully, promote
  deliberately." The whole doc is about *restraining* emergence. There is no
  generative prompt anywhere — nothing that asks "what did you notice that isn't
  your task? what was harder than it should have been? what would 10× this?"
- **Cost with no payoff.** `emergence.py capture` requires a structured record
  (observation / source / value / smallest test). In autonomy / "stop at done"
  mode, a channel that costs real work to file into and returns nothing gets
  optimised away — correctly, by the local incentives.

Net effect: the generative half of E/I's own model (`observe → connect →
synthesize → name → test → promote`) has been amputated in practice. The front
two verbs never fire on their own. Some E/I-shaped output *is* still happening —
it lands in design notes, in the trajectory check's "named new evidence"
sections, in Tenth-Seat reviews — but it is never routed to a scannable,
sweepable backlog, so it cannot be systematically promoted, reconciled, or
killed.

## 2. Decision: reframe in place, do NOT add a playbook file

The operator's framing question was: keep current E/I as-is, add a separate
"Imagination" file, and have E/I run both?

**Recommendation: one file, three explicit phases. No new playbook file.**

Reasons:

1. **`playbook/INDEX.md` §"Adding or changing a method"** requires naming why the
   existing concept owner *cannot* coherently own the addition. It can:
   `EMERGENCE.md`'s own model already contains the generative half
   (`observe → connect → synthesize`). The generativity is missing from
   *practice*, not from the *owner's scope*.
2. **`tests/test_documentation_sprawl.py::PLAYBOOK_SURFACE_BUDGET = 24`, and the
   active surface is already at 24.** A new file mechanically fails
   `test_playbook_surface_does_not_grow_silently` unless the budget is raised
   with a documented justification — and "split one method into two" is exactly
   the sprawl that test exists to catch. Restructuring in place is 0 surface
   growth.
3. **"E/I runs both" is itself the argument against two files.** If one protocol,
   one cadence, and one script own both phases, they belong in one document. Two
   files = two things to read, maintain, and drift.
4. The divergent/convergent tension the operator correctly identified is real,
   but it is handled by **naming it as two phases with different rules inside one
   doc**, not by physical separation.

## 3. Proposed `playbook/EMERGENCE.md` — full redraft

Keeps every current guardrail; adds the generative phase on top and a
consumption pointer at the bottom. Target length ~50 lines (from 22).

> # Emergence and Improvement (E/I)
>
> Discovery is valuable. It must be *elicited* deliberately, *captured* cheaply,
> and *promoted* carefully — and it must not hijack an assigned task.
>
> ```text
> IMAGINE → CAPTURE → PROMOTE
> (diverge)  (converge)  (decide)
> ```
>
> ## Phase 1 — Imagine (divergent)
>
> Run at a cadence, not continuously. The trajectory check is the standing
> anchor (see `ROADMAP_TRAJECTORY_CHECK.md` §"Emergence pass"); an operator may
> also call one at a phase boundary or on demand.
>
> This phase has **no filing discipline** — the goal is volume and range. Ask,
> against the work of the arc (or the project as a whole):
>
> - What recurred that is *not* a defect — a rough edge, a workaround that keeps
>   reappearing, a step that is always slower than it should be?
> - What did a PR, a review, or an incident *reveal* about the system that is
>   captured nowhere?
> - What are we not doing that a competent outsider would expect us to?
> - What would make this 10× cheaper / faster / safer — even if it sounds
>   disproportionate right now?
> - What did we decide once, long ago, that nobody has re-examined against
>   current reality?
>
> Speculation is explicitly allowed here. Get candidates onto the table first;
> judge them in Capture.
>
> ## Phase 2 — Capture (convergent)
>
> Take the candidates worth keeping and file each as a concise record in
> `work/insights/`, `work/ideas/`, or `work/experiments/` (use
> `scripts/emergence.py capture`). Include: the observation, its source/context,
> its potential value, and the **smallest next test**.
>
> - **Insight:** a notable observation.
> - **Synthesis:** a meaningful connection between observations.
> - **Idea:** a bounded possible improvement.
> - **Experiment:** a safe, small test.
>
> Filing is not endorsement. A captured record is a candidate, not a commitment.
>
> ## Phase 3 — Promote (deliberate)
>
> Promotion turns a captured record into real work: a `work/tasks/` contract, a
> `work/decisions/DEC-NNN` record, or an in-scope line on an existing roadmap
> item. It is never an automated step, and only a promoted item may expand
> implementation scope.
>
> **Propose vs. dispose.** The Emergence pass (`ROADMAP_TRAJECTORY_CHECK.md`
> §"Emergence pass") *proposes* a disposition for each open record with a
> one-line rationale. The orchestration operator — or a coordinator acting under
> delegated authority for the bounded / low-risk cases — *disposes*. This is the
> same split as friction-log escalation: the pass surfaces and recommends; it
> does not authorize.
>
> **Ripeness bar.** Promote a record when its "smallest next test" is concrete
> AND either (a) the value is clear and the change is bounded (→ task contract),
> or (b) it names a choice only the operator can make and that choice now blocks
> progress (→ decision record), or (c) it is in-scope work on an item already on
> the roadmap (→ roadmap line). Otherwise leave it **incubating** — a valid
> state, but every pass must record *why* it is still incubating, not silently
> skip it.
>
> **After disposition.** Update the record's `## Promotion` section in place
> (append-only): from "Not promoted" to a dated line linking the task / DEC /
> roadmap item it became (promote), or to a dated disposition line stating what
> later reality changed (stale) or what supersedes it (kill). A promoted or
> stale / killed record stops consuming sweep attention; the file is never
> deleted.
>
> ## Consumption
>
> `ROADMAP_TRAJECTORY_CHECK.md` §"Emergence pass" sweeps the `work/insights/` +
> `work/ideas/` backlog every pass: each open record is **promoted**, marked
> **stale**, **killed**, or explicitly **incubated with a reason**. A record
> incubated across **N = 3** consecutive passes with no movement is named in the
> pass's operator section. This mirrors the FRICTION_LOG consumption duty and
> uses the same N = 3 ladder.
>
> Rule: **imagine widely, file cheaply, promote deliberately, sweep every arc.**

Notes on the redraft:

- Phases 2 and 3 keep the *current* doc's substance — nothing that works today
  is lost. Phase 3 gains the who-decides / what-it-produces / ripeness-bar /
  after-state detail the current one-paragraph version omits.
- The `scripts/emergence.py` capture record already ends with a "## Promotion —
  Not promoted…" section; no script change is required. (Optional follow-up: a
  `--stale <reason>` / `--kill <reason>` convenience to append the disposition
  line; not needed for v1 — an editor does it. Logged as a near-term IDEA, not
  in this note's scope.)

## 4. Proposed `playbook/ROADMAP_TRAJECTORY_CHECK.md` — new section

Insert after §"Friction-log consumption (every pass)", same shape:

> ## Emergence pass (every pass)
>
> Every trajectory-check pass runs a short E/I pass (`EMERGENCE.md` Phase 1 +
> Consumption):
>
> 1. **Imagine.** Spend a bounded slice on `EMERGENCE.md` Phase 1's prompts
>    against this arc. File anything worth keeping via `scripts/emergence.py
>    capture`. Zero new records is a valid outcome and is recorded as such — but
>    a pass that finds *nothing* worth imagining about, arc after arc, is itself
>    a `TENTH_SEAT_REVIEW.md` §7 signal.
> 2. **Sweep.** Walk `work/insights/` + `work/ideas/`. For every open record, the
>    pass writes a proposed disposition + one-line rationale into the trajectory
>    note:
>    - **promote** — name the artifact it should become (`work/tasks/<name>.md`
>      contract, `DEC-NNN`, or a specific roadmap item + line). The pass does not
>      create the artifact or authorize the work; it recommends. Operator /
>      coordinator disposes per the `EMERGENCE.md` Phase 3 authority split.
>    - **stale** — append a dated disposition line to the record; observation
>      preserved as history.
>    - **kill** — superseded / tried-and-rejected / no longer useful; say by what.
>    - **incubate** — stays open; the pass records the reason it is not yet ripe.
>    A record marked **incubate** across **N = 3** consecutive passes with no
>    movement is an operator-escalation item, named in the operator section; the
>    pass does not record a clean result until it is listed. (Same ladder as
>    friction-log consumption.)
> 3. Record in the trajectory note that the pass ran and what it produced / swept
>    (even "0 imagined, backlog all current").
>
> Capture discipline and the phase model are owned by `EMERGENCE.md`. This is the
> consumption half, mirroring friction-log consumption above. Nothing here grants
> the Emergence pass authority to create tasks, open DECs, or edit the roadmap on
> its own — it produces recommendations in the trajectory note.

And add to §"Relationship to task-level steering" the one-liner that E/I is the
generative counterpart to the corrective triage loop.

## 5. Wire the dangling REPAIR_AND_LEARNING → EMERGENCE thread

`REPAIR_AND_LEARNING.md` §"Relationship to operational lessons" already says a
triaged recurrence whose lesson *generalises* is "a candidate operational lesson
… the promotion path is `EMERGENCE.md`" — but nothing operationalises it. Add one
sentence to the trajectory friction-log-consumption step: when a friction entry's
lesson generalises beyond its own fix, the pass also files a `work/insights/`
record (Phase 2) so it enters the sweep, not only the FRICTION_LOG close.

## 6. First backlog sweep (part of the impl PR, or the first #22-arc sweep)

The current records, with proposed dispositions. The impl PR appends the dated
disposition lines only for the STALE / superseded ones (append-only, `##
Promotion` section); the PROMOTE-to-DEC-003 records are dispositioned by DEC-003
itself; the rest stay open with a recorded incubation reason.

| Record | Proposed disposition | Evidence / becomes |
|---|---|---|
| `INSIGHT-e0b448a6` — `RecoverySupervisor.tick()` has zero production invocation | **STALE** | `run_recovery_tick` constructs a supervisor and calls `tick()` since PR #165 (CAPABILITY_CHECKLIST H5 history). Append dated line. |
| `INSIGHT-75785aae` — Harness layer has zero production callers of `HarnessService` | **STALE** | `build_canonical_harness_service` composition root + first `--enforce-canonical-run` pass, PR #277 (`a4f2dc8`). Append dated line. |
| `IDEA-20615e4d` — Standardise per-agent isolated git worktrees | **STALE (superseded)** | `playbook/WORKTREE_ISOLATION.md` + AGENTS.md worktree convention. Append a "superseded by WORKTREE_ISOLATION.md" line. |
| `INSIGHT-29a10ad4` — `check_review_evidence.py` head_sha walk-back stops silently at merge commits | **PROMOTE (small)** | Still accurate; pattern recurs on every trajectory-check evidence rebind (incl. #278). Becomes a 1-line docstring addition to `check_review_evidence.py`. Paired with `IDEA-968eb261`. |
| `INSIGHT-102296b5` — enforcement may be structurally unexercisable under the current operating mode | **PROMOTE → DEC-003** | Same question as `INSIGHT-651d8c62` from the other side; bundled. |
| `INSIGHT-651d8c62` — 7-row cluster "one step from DONE" for ~13 passes | **PROMOTE → DEC-003** | This note's companion decision record. |
| `INSIGHT-45727354` — FRICTION_LOG behavioral-close is a rule-20 carve-out | **INCUBATE** | Pairs with #22 friction-log consumption; promote to a `REPAIR_AND_LEARNING.md` clause if the audit in its "smallest next test" shows behavioral-close is common. |
| `INSIGHT-68a53a28` — the trajectory check has become part of the dev loop | **INCUBATE** | Feed into #22's own retrospective; promote only if #22 confirms the pattern (measure passes #12–#21). |
| `IDEA-582cc671` — zero-diff re-review tier in `MODEL_CAPABILITY_ROUTING.md` | **PROMOTE (operator decision)** | Recurrence condition hit many times incl. #278's rebind. Separate operator decision on the re-review tier. |
| `IDEA-968eb261` — `check_review_evidence.py` tolerate pure rebase-onto-main | **PROMOTE** | `work/tasks/` contract, paired with `INSIGHT-29a10ad4`. |
| `IDEA-9e7014fa` — fix `coordination_housekeeping.py` (crashes on `gh pr list`) | **PROMOTE** | `work/tasks/` contract + a FRICTION_LOG tool-gap entry. Session-27 near-term. |
| `IDEA-a134ad7c` — exclude `.claude/worktrees/` from `check_spiderweb.py` by default | **PROMOTE** | `work/tasks/` contract. Session-27 near-term. |
| `IDEA-bc6cd243` — stale-worktree prune + age-annotated report | **PROMOTE** | `work/tasks/` contract. Session-27 near-term (paired with the ~40 dead worktree registrations). |

## 7. Scope / non-goals

- **In scope:** the 4 playbook edits above; the first backlog sweep (append-only
  disposition lines to the 3 STALE records); the DEC-003 skeleton file.
- **Not in scope:** any new playbook file; a daemon / scheduled "imagination
  agent" (`EMERGENCE.md` and `SPIDERWEB_AUDIT.md` both explicitly forbid this —
  the anchor is the *existing* trajectory-check cadence, no new machinery);
  auto-promotion of any record; a `scripts/emergence.py` change; a
  `MODEL_CAPABILITY_ROUTING.md` re-review-tier change (that is `IDEA-582cc671`'s
  own promotion decision); creating the `work/tasks/` contracts for the PROMOTE
  IDEAs (the coordinator disposes those separately); filling the DEC-003
  recommendation / authorization (the coordinator does that with the operator).
- **Sprawl budget:** 0 new playbook files; `PLAYBOOK_SURFACE_BUDGET` stays 24.
  `EMERGENCE.md` grows ~22 → ~50 lines; `ROADMAP_TRAJECTORY_CHECK.md` gains one
  section. `test_documentation_sprawl.py` still passes (surface count unchanged).
- **INDEX.md:** the existing `EMERGENCE.md` row boundary ("Discovery capture
  only") is now too narrow — update to "Elicit, capture, and route improvement
  ideas; generation cadence is the trajectory check, promotion stays
  deliberate."

## 8. Review plan

Verification-only (no executable change). Reviewer confirms: the redraft loses no
current guardrail (grep for "not an automated step" / equivalent, "hijack",
"deliberate", "Filing is not endorsement"); the trajectory-check section mirrors
the friction-log consumption shape and does not create a second authority store
(the pass recommends, operator/coordinator disposes); the sweep dispositions in
§6 are evidence-backed; `test_documentation_sprawl.py` + `test_playbook_index_*`
still green; INDEX.md boundary line updated; DEC-003 skeleton is well-formed
against `work/decisions/DEC-001`/`DEC-002` shape.

## 9. Resume prompt (for the impl dispatch)

You are implementing the E/I reframe from
`work/notes/2026-09-03-emergence-imagination-reframe-design.md` (this note, once
merged). Deliverable: one PR on `feat/emergence-imagination-reframe` editing
`playbook/EMERGENCE.md` (full redraft per §3), `playbook/ROADMAP_TRAJECTORY_CHECK.md`
(new §"Emergence pass" per §4 + one line in §"Relationship to task-level
steering"), `playbook/REPAIR_AND_LEARNING.md` (one sentence per §5),
`playbook/INDEX.md` (one boundary line per §7), and appending dated disposition
lines to the 3 STALE records in §6 (`INSIGHT-e0b448a6`, `INSIGHT-75785aae`,
`IDEA-20615e4d`). MUST NOT: add a playbook file; raise `PLAYBOOK_SURFACE_BUDGET`;
change `scripts/emergence.py`; touch `MODEL_CAPABILITY_ROUTING.md`;
promote / kill any record not marked STALE in §6; create the `work/tasks/`
contracts. Acceptance: `python3 -m unittest tests.test_documentation_sprawl`
green; `python3 -m unittest discover -s tests` green (CI `test` gate); every
current `EMERGENCE.md` guardrail still present; the new trajectory section names
`EMERGENCE.md` as the discipline owner. Independent review = verification-only.
Two-phase; do not push your own review evidence.
