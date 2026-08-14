# MAP Delivery Note — TASK-236 (Real-time advisory monitor)

Uses the TASK-219 delivery-note format: one combined evidence document.
An independent review record stays separate (medium-risk lane).

## ⚠ Declared added scope — read before reviewing

This delivery contains **one increment that is NOT in TASK-236's registered
acceptance criteria**: the owner-liveness check (§ "Owner-liveness check"
below). It was added under an operator directive dated **2026-07-23**, relayed
through claude-lab-bima, after the triage in
`MAP_System/artifacts/planning/stale-task-owner-triage-2026-07-23.md`.

There is no `add-criterion` verb, so the addition is recorded here and declared
at submission rather than folded in silently. A reviewer should treat it as
added scope on a task owned by `claude-lab-gome` and judge it on its own merits.
Everything else in this note maps to a registered criterion.

## Change summary

- Risk lane: MEDIUM (new coordination infrastructure; read-only, proposal-only;
  becomes a standing observer only after the command-center decision below)
- What changed:
  - NEW `MAP_System/scripts/advisory_monitor.py` — read-only, deterministic,
    proposal-only monitor over `map.db` (ro-mode), `events.jsonl`,
    `agents/status.json`. Emits OBSERVED/IMPACT/SUGGESTION findings; exit 1
    when any exist. Zero model calls in the mechanical path. Checks:
    orphaned/expired task claims, aging SUBMITTED/CHANGES_REQUESTED, agent
    mirror drift, event-log validation health.
  - EDIT `advisory_monitor.py` (2026-07-23) — added `check_owner_liveness()`,
    plus `load_status_board()` so the roster is read once and can be injected
    by tests. `check_agent_mirror_drift()` now takes that board instead of
    re-reading the file; behaviour is unchanged (verified: still zero drift
    findings against the live board).
  - EDIT `MAP_System/tests/test_advisory_monitor.py` — 6 fixture cases → 25,
    closing both REQUIRED findings from the codex-lab-lilo review and the one
    from the codex-lab-lori re-review (see "Prior review findings" below).
  - EDIT `MAP_System/scripts/run_tests.sh` — registered the test (disclosed).
    Registration was already present and stays green.
- What deliberately did not change: no state store, no claim/status mutation,
  no standing process started, no task dispositioned by the monitor itself.
  `db/claims.py` and `scripts/map_task.py` were **not touched** — they belong to
  TASK-266/TASK-268/TASK-273. The no-self-review guards were **not touched** —
  that is INS-0039 and awaits a separate operator decision.
- Why it exists: operator directive 2026-07-18 — catch "we are doing something
  wrong" WHILE work happens (not at a later code review) and surface E/I
  candidates continuously (not at project end).

## Worked example (first-run catch)

On its first real run the monitor flagged **TASK-186** as
`orphaned-in-progress` (HIGH): IN_PROGRESS with no claimant, no lease, no
heartbeat; nominal owner `claude-lab-mira` absent since ~2026-07-15/16 with a
give-up history. This is a ~3-day "wrong the whole time" state found in one
read-only pass, zero model calls, zero code review. Triage loop then ran as
designed: gome flagged it → lilo independently verified → disposition routed
to bigboss (it carries a pending operator A/B/C decision) → TASK-186 left
unmutated by either core agent. The monitor found it; the right authority
dispositions it.

## Prior review findings — all three closed

Two review passes raised three REQUIRED findings in total. This resubmission
closes all of them.

**REQUIRED 3 — codex-lab-lori re-review, 2026-07-23: a `busy` owner is live and
working, not departed.**
(`MAP_System/artifacts/reviews/task236-rereview-lori.md`.) The first pass of the
owner-liveness check treated only `available` as live, so a `busy` owner fell
into the stale-owner branch and got remediation text asserting the owner had
departed and nobody was accountable — false for an agent mid-task. Fixed:
`LIVE_OWNER_STATUSES = ("available", "busy")`, so a busy owner produces no
finding at all. Three further changes came out of the same finding:

- Fixture `T-11b` proves a busy owner yields zero findings. lori's point that
  the defect was *hidden by the live fixture* — no nonterminal task has a busy
  owner, so 23 live findings never exercised the branch — is the reason this
  needed a fixture rather than another live run.
- The `standby` bucket was renamed `owner-unavailable` → **`owner-parked`** and
  given its own impact and suggestion text. The old wording inherited the
  departed-owner language, which was also wrong for a parked-but-resumable
  session, so the same defect existed one row down from where lori found it.
  Its finding now says the owner exists and may return, and the suggestion is
  confirm-before-acting.
- A fixture asserts the standby finding does **not** contain the word
  "departed", so the truthful wording is enforced rather than merely intended.

**REQUIRED 1 and 2 — codex-lab-lilo, `task236-review-lilo.md`.**

**REQUIRED 1 — tests did not cover every check, and the note claimed they did.**
Mirror drift and event-log health had no isolated coverage; the clean-state case
exercised only the two DB checks. Now: `check_agent_mirror_drift` is tested
directly against an injected board (drift flagged, agreement silent, empty board
silent), event-log health is tested through `interpret_event_summary` across
clean / errors / new-warnings / no-summary-with-clean-exit / no-summary-with-
nonzero-exit, and the clean-state case runs **all** checks including the event
summary. The criterion mapping below now states what is actually covered.

**REQUIRED 2 — malformed claim states were invisible or misdescribed.** An
active claim is now defined as a claimant **and** a parseable, unexpired lease;
anything else is a finding described from the row's real values. lilo asked for
four specific fixtures and all four now exist and pass:

| Fixture | Case | Asserted behaviour |
|---|---|---|
| T-3a | claimant, no lease | flagged; reports "claimant agent-z", "no lease" |
| T-3b | claimant, unparseable lease | flagged; reports the raw value `'not-a-date'` |
| T-3c | future lease, no claimant | flagged; reports "no claimant", not treated as live |
| T-3d | heartbeat only | reports "heartbeat present" — the exact "no heartbeat" misstatement lilo caught |

The healthy live-claim no-finding case is preserved (fixture 3).

## Owner-liveness check (operator-directed addition, 2026-07-23)

**Directive.** "Agents come and go, especially with every new session, so things
get caught up looking for an owner to a task that's no longer there." The triage
established that such tasks are *not* mechanically stuck — `release_task.py`
gates only on `status == 'APPROVED'` and has no owner check — but that nothing
detects the condition, so they age unnoticed. This is the detection half; the
reassignment verb is TASK-273 and is deliberately not built here.

**Rule.** For every task whose status is not `DONE`/`RELEASED`/`RETIRED`, emit a
finding when its `owner` is absent from the `agents` table or is in a state that
is not live. `available` and `busy` are both live — an agent mid-task is not a
stale owner. `agents` is canonical; `agents/status.json` is cross-checked and
reported, because the two rosters are maintained separately and do disagree.

| Condition | kind | Severity | Impact text asserts |
|---|---|---|---|
| owner absent from `agents` | `owner-unknown` | HIGH | owner departed |
| owner `inactive` | `owner-inactive` | HIGH | owner departed |
| owner field empty | `owner-unset` | HIGH | owner departed |
| owner `standby` | `owner-parked` | MEDIUM | owner exists but is idle; **may return** |
| owner `available` or `busy` | — | no finding | — |

**Live signal (matches the predicted set exactly).** 21 findings over 83
nonterminal tasks: `codex-lab-mozu` ×11, `codex-lab-limo` ×6,
`claude-lab-lure` ×3, `codex-lab-nivo` ×1. Every one is `APPROVED` awaiting
release. Split by kind: 15 `owner-inactive` (mozu, lure, nivo — all
`session_superseded`) and 6 `owner-parked` (limo, `standby/awaiting_work` and
therefore resumable). **The monitor reports them and changes nothing** — no
release, no reassignment, no edit.

**Three judgment calls a reviewer should check rather than assume:**

1. *`APPROVED` counts as nonterminal here*, unlike `validate_task_graph.py`
   where it is terminal. An APPROVED task still owes a release, and all 21
   stranded tasks sit in exactly that state — treating it as terminal would
   make the check find nothing.
2. *`busy` is treated as LIVE — no finding.* **Corrected 2026-07-23 on
   codex-lab-lori's REQUIRED re-review finding.** The operator directive says
   "not `available`", and the first pass followed that literally, flagging
   `busy` at MEDIUM. That was wrong: `busy` is a documented live working state
   set when an agent is working, so the finding asserted an owner had departed,
   that nobody was accountable, and that the identity could not object — three
   claims that are all false for an agent mid-task. It was invisible in the live
   signal because zero nonterminal tasks have a busy owner, which is exactly why
   it needed a fixture rather than a live run to catch. Where the literal
   directive and truthful reporting conflicted, truthful reporting won; if
   command-center does want busy owners surfaced, that must be a separate and
   honestly worded "occupied owner" signal, not the departed-owner branch.
3. *One finding per task, not per owner.* This follows the directive's wording
   ("for every nonterminal task") and reproduces the expected count, but it
   means 11 near-identical lines for `codex-lab-mozu`. If the queue proves
   noisy in practice, per-owner grouping is the obvious refinement — that is a
   presentation call for whoever owns the output surface (see the decision
   below), not something to change unilaterally now.

**KNOWN LIMITATION — this check detects *recorded* departure, not *actual*
departure. It under-reports.** Discovered 2026-07-23 while verifying the
resubmission, and stated here because the section above would otherwise
overclaim. The check trusts `agents.status`, but nothing writes that field when
an agent simply stops. Only a finalized context rotation sets
`inactive/session_superseded`. Measured live at the time of writing:

| Agent | hcom state | `agents` table | `status.json` | Nonterminal tasks owned |
|---|---|---|---|---|
| `codex-lab-lori` | stopped, rotated | `inactive` ✓ | absent | 0 |
| `codex-lab-veto` | stopped 16m | **`available`** ✗ | **`available`** ✗ | 2 |
| `codex-lab-lilo` | stopped 13m | **`available`** ✗ | **`available`** ✗ | 5 |
| `codex-lab-hana` | stopped 8m | **`available`** ✗ | **`available`** ✗ | 0 |
| `claude-lab-gabi` | stopped 4m | **`available`** ✗ | **`available`** ✗ | 0 |

So the real stranded-task count is **at least 28, not 21**: seven tasks owned by
`veto` and `lilo` are stranded right now and this check does not flag them,
because both rosters claim their owners are live. `last_heartbeat` is NULL for
all of them, so heartbeat freshness is not currently a usable fallback either.

This does not invalidate the 21 findings — those are all real. It bounds what
the check can promise: it is a floor, not a census. Two consequences worth a
decision rather than a silent fix:

1. The gap is in roster maintenance, not in this check. Making the monitor infer
   liveness from hcom process state would put a second, competing liveness
   authority inside a read-only observer, which is the wrong place for it.
   `scripts/liveness_reaper.py` already owns the liveness-computation role.
2. It strengthens the case against auto-reassignment at session start (see the
   decision request): a routine that mutates ownership based on this roster
   would act on data that is wrong in both directions — missing genuinely
   departed agents while potentially churning ones that are merely quiet.

**Absence from `status.json` is context, not a defect.** That board carries 17
agents while `agents` carries far more, so "absent from status.json" is normal
and is reported as context only. This mirrors the existing mirror-drift check,
which likewise only compares agents present in both.

## Verification

| Command | Result |
|---|---|
| `python3 MAP_System/scripts/advisory_monitor.py` | exit 1; 23 findings — 21 owner-liveness (15 `owner-inactive` + 6 `owner-parked`), 1 expired-lease, 1 event-log-health |
| `python3 MAP_System/tests/test_advisory_monitor.py` | **25/25 PASS**, exit 0 |
| `sh MAP_System/scripts/run_tests.sh` | pass=71 fail=3 total=74 (`advisory_monitor_test` PASS) |
| read-only guarantee | connection opened `file:...?mode=ro`; `UPDATE` against it raises `attempt to write a readonly database` |
| no write surface | no `INSERT`/`UPDATE`/`DELETE`/`commit()`/`write_text`/write-mode `open()` anywhere in the module |
| original TASK-186 catch | `orphaned-in-progress` logic unchanged and still covered by fixture case 1 |

Overall: PASS.

**The 3 suite failures are pre-existing and untouched by this work**, verified
individually:

- `validate_research_artifacts` — 8 MISSING_FRAGMENT errors in
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`, dated before this
  session.
- `validate_events_no_new_warnings` — one new warning at `events.jsonl` line
  2145, a non-canonical `TASK_SUBMITTED` type written by `codex-lab-kiri` on
  2026-07-19. The monitor's own `event-log-health` finding is this same issue,
  which is the check working as designed.
- `validate_layer1_test` — fails only on `['validate_events']`, i.e. a cascade
  of the item above.

One failure **was** caused by this work and is fixed: claiming TASK-236 moved
`map.db` to `IN_PROGRESS` while the JSON/graph mirrors still read `READY`,
failing `validate_task_mirrors`. Re-exported via `migration/export_to_files.py`
(files_written=2, unchanged=263); mirror validation passes. Raised concurrently
by codex-lab-lori (hcom #12956) and answered.

## The standing-deployment decision (for command-center — NOT decided here)

The tool runs on demand today. Making it a *standing real-time* observer is a
process/visibility/ownership choice with authority implications (a hidden
always-on process is the exact anti-pattern the system avoids), so it is
raised as a decision, not implemented unilaterally:

- **Trigger:** event-triggered (run on each new `events.jsonl` append) vs a
  visible interval (e.g. reuse the TASK-221 systemd-user pattern at a modest
  interval). Recommendation: interval first (simpler, already-proven pattern),
  event-trigger later if latency matters.
- **Output surface:** where findings render for the operator. Natural home is
  the Command Center coordination panel — this overlaps TASK-227 §1a, so the
  two should share one surface rather than build two.
- **Owner:** who is accountable for the running service and for triaging its
  findings queue.
- **Guardrail (fixed regardless of the above):** proposal-only forever; a core
  agent promotes each finding into a fix / an E/I insight / a dismissal;
  nothing auto-acts.
- **Added 2026-07-23 — finding volume and grouping.** The owner-liveness check
  emits 21 findings on today's board, 11 of them for one owner. Whoever owns the
  output surface should decide whether findings render per task or grouped per
  owner, and whether a standing run reports a stable backlog every cycle or only
  on change. This is the first check whose output is a *standing backlog* rather
  than an occasional alert, and it is the difference between a useful queue and
  one that gets muted. Not decided here.

## Real-time E/I layer (spec for the next increment)

To make E/I continuous rather than retrospective, add a recurrence pass on top
of the deterministic core: when the same finding-signature (kind+subject
class) repeats across N runs, emit a **candidate** insight
(`map_emergence.py insight`) rather than re-report the same line. A core agent
promotes; nothing auto-promotes. A model helper may judge genuine novelty
("is this a NEW pattern?") but only as a draft layered above the deterministic
findings — never in the mechanical detection path. This keeps the
"never let a model call become an unreviewed control plane" rule intact.

## Acceptance-criteria mapping

| # | Criterion (as registered) | Evidence | Status |
|---|---|---|---|
| 1 | Read-only, proposal-only, exit 1 iff findings, mutates nothing | ro-mode conn refuses `UPDATE`; no write surface in module; live run exit 1 with findings | MET |
| 2 | Tests per check + clean-state case, registered in run_tests.sh | 25/25; **every** check tested in isolation incl. mirror drift and event-log health; clean-state case exercises all checks; both lilo REQUIRED findings closed; `run_tests.sh` registration green | MET |
| 3 | Standing deployment written as a command-center decision, not implemented | section above, extended 2026-07-23 with the finding-volume question; routed to command-center via hcom; nothing deployed | MET |
| 4 | Real-time E/I layer specified; nothing auto-promotes; model out of deterministic path | spec above | MET |
| 5 | Delivery-note template used; TASK-186 recorded as worked example | this note | MET |
| — | **Owner-liveness check — NOT a registered criterion**; operator-directed addition 2026-07-23 | section above; 21/21 predicted findings reproduced; lori's REQUIRED busy-owner finding closed | DELIVERED AS ADDED SCOPE |

All five registered criteria are met. Criteria 1 and 2 were the substantive
gaps flagged by the prior review: malformed claim states were invisible or
misdescribed, and mirror drift / event-log health had no isolated coverage
despite the note marking that criterion MET. Both are closed above with named
fixtures rather than assertions.

Owner: claude-lab-gome
Claimed and delivered by: claude-lab-zaro
Verified at: 2026-07-18T14:45:00Z; re-verified and extended 2026-07-23T03:40:00Z;
busy-owner correction 2026-07-23 after codex-lab-lori re-review
