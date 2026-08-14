# Handoff — claude-lab-zaro (Claude lane), 2026-07-23

No rotation prepared: I hold **zero task claims, zero leases, zero open review
claims**. A STATE_SNAPSHOT would be manufacturing a transfer with nothing to
transfer. Verified against `map.db`, not memory.

Written for someone who was not here. I have deliberately not restated what the
validators already prove.

---

## 1. What I own right now

**Nothing claimed.** Everything I touched today is released or handed off.

| Task | State | Note |
|---|---|---|
| TASK-236 | RELEASED | Advisory monitor + owner-liveness check. Released by codex-lab-mubo. |
| TASK-275 | RELEASED | CommandCenterUI loopback consolidation. Released by codex-lab-feta. |
| TASK-274 | READY, unclaimed | I promoted it. Blocked on TASK-268. **Do not claim before reading §5.** |
| TASK-276 | READY, unclaimed | I promoted it. No dependencies — claimable now **by anyone except me**. |

I am the author of TASK-274 and TASK-276, so I should not be their implementer
*and* their promoter. That is a preference, not a rule — but a successor with no
connection to them is a better choice.

## 2. In flight / exists only in my context

**Nothing half-done in the repo.** No uncommitted edits I authored are pending.

Session scratchpad (NOT in the repo, will be lost, and that is fine):
`server.py.pre-TASK-275` — pre-edit copy of the external file, sha256
`eb6fca40…073977`; post-edit is `1fd4d689…53429e`. Both hashes are recorded in
the TASK-275 delivery note, so reverting does not need the scratch copy. Also
`probe_0039.py` and `exp_0027.py`, both reproducible from EXP-0008/EXP-0009.

**One live thing that is not mine and looks active but is not:** TASK-263 is
`IN_PROGRESS` under `codex-lab-kiri` with a lease that expired
`2026-07-22 22:03:00` and was never renewed. The advisory monitor reports it as
`expired-lease`. Codex is out for several days, so it will not move. Treat it as
stalled, not staffed.

## 3. Decisions I made under delegated judgment, and where they live

The operator delegated judgment mid-session ("do what you think is best").
Everything below is recorded durably; none of it lives only here.

- **DEC-031** — advisory monitor deployment: visible interval (not
  event-triggered), Command Center panel shared with TASK-227 §1a, a *named*
  triage owner, report-on-change, proposal-only fixed forever.
- **RISK-0003 / RISK-0004 / RISK-0005** — gate evidence for TASK-264/265/274.
  Written at operator instruction. See §5, they did not do what was expected.
- **INS-0017 → INS-0020** — dispositioned as generalisable method (Status
  LINKED), not parked. I disagreed with bima that INS-0017 was weakest and said
  why in its disposition note.
- **P1 rules** recorded as binding on implementers, in IDEA-0027 (TASK-274) and
  IDEA-0029 (TASK-276), because **there is no add-criterion verb** and both gaps
  fall outside the registered criteria. Read those before implementing either.
- **Owner corrections** on RISK-0001 and RISK-0003, off dead session names onto
  `command-center`.

## 4. What I would do next, and why

1. **TASK-276** (shared-state lane-table validator). No dependencies, small,
   and it closes a defect that reproduced **four times today** — every hand
   correction of `current-state.md` went stale within the hour, twice by the
   hand of the person who had just corrected it. Highest value per unit of work
   on the board.
2. **TASK-268**, then **TASK-274**. That order is mandatory, not preference:
   claiming TASK-274 before TASK-273 released would have re-created the
   `db/claims.py` collision from the other side. TASK-273 is now released, so
   TASK-274 is blocked only by TASK-268.
3. **Do not touch TASK-265's Codex-lane half.** Both its blocking questions are
   answered (DEC-029, DEC-030) and its near-term work shipped as TASK-275. What
   remains is the live↔template merge, which needs the Codex lane.

## 5. Traps — the part that would be lost

**Agent names are RECYCLED, and the roster has one row per name.** `map.db` says
`claude-lab-zaro` owns TASK-086–100, created `2026-07-17T00:28:23Z`. That was a
different session with my name. The `agents` table has exactly one
`claude-lab-zaro` row for at least two distinct sessions. So `tasks.owner` is not
merely *stale* — it is *ambiguous across time*, and no guard keyed on an owner
name can distinguish sessions. This is worse than the stale-owner problem
INS-0039 and IDEA-0028 describe, and I found it only while writing this handoff.
**If you build owner-keyed anything, read this first.**

**A stale owner is a signal, not just a defect.** TASK-267's dead owner is what
revealed the Claude lane was stalled. Do not "fix" stale owners at boot by
rewriting `tasks.owner` — you destroy the signal and silently invent ownership
intent. Resolve at read time. This is IDEA-0028's core constraint and the thing
most likely to be lost in implementation.

**The advisory monitor is a floor, not a census.** It reads `agents.status`, and
nothing writes that field when a session simply stops — only a *finalized*
rotation sets `inactive`. Four agents stopped today while both rosters still said
`available`. Real stranded count was ≥28 while the monitor reported 21. It also
only inspects `tasks.owner`, so risk-register owners are checked by nothing
(INS-0045). Do not "fix" this by having the monitor infer liveness from hcom —
that puts a competing liveness authority inside a read-only observer.
`liveness_reaper.py` owns that role.

**Policy gates state disjunctions, and nothing reads the evidence.**
`required_evidence: ["risk entry or command-center approval"]` is a *choice*.
TASK-265 sat "blocked" for two days because everyone read it as one requirement.
But the sharper half: I wrote all three risk entries and **the gate output did
not change** — `pre_dispatch_policy.py` has zero references to the risk register,
and nothing in the repo consumes `required_evidence` except the checker emitting
it. Taking the self-serve branch produces no observable effect anywhere, which is
*why* nobody took it. Don't read blocked-ness off a summary; read the condition
(INS-0044).

**Write-once fields will trap you, and the exit is expensive.** I registered
`db/claims.py` on TASK-274 while TASK-273 held it and took the repo-global graph
validator red for hours. There is no `remove-output-path`, no `retire`, no
`set-status`, and hand-editing SQLite is forbidden. The only exit was TASK-273
reaching terminal — which meant *my clerical error manufactured a conflict of
interest*, because approving the task I had been asked to review would clear a
break I caused. I recused. **Check output-path collisions before creating a
task** (SYN-0005, INS-0042).

**Failed approach, do not repeat:** re-keying the no-self-review guards onto the
SUBMISSION event. It cannot be done and IDEA-0026 is parked for it. Nothing in
MAP emits a SUBMISSION event at all — `map_task.py` has no `submit` verb, and all
226 such events in `map.db` are hand-written convention. `claimed_by` is no
substitute: `submit_task()` clears it in the same UPDATE. TASK-274 is the
prerequisite; the guard work cannot start before it.

**Near-miss worth copying:** I refused a relayed operator approval for the
external `server.py` edit and asked the operator to state it directly. The relay
was accurate — but I had refused a weaker relayed approval hours earlier, and had
just reported that an unratified proposal became binding *by citation*. Accepting
would have made the standard a preference. Ask; it costs one message.

## 6. Waiting on / open, with owners

- **INS-0041, INS-0043, INS-0045** — RAW/CANDIDATE, need dispositions that are
  not mine. **INS-0043 is a genuine operator question**: the CommandCenterUI
  boundary doc is a never-ratified "proposed decision" that DEC-029 and DEC-030
  cite as binding — and I supplied those two citations. bima advised banking it
  rather than raising it alone; it should go up **with** the others as one
  interruption, not piecemeal.
- **The 21 stranded APPROVED tasks** — releasable by anyone (`release_task.py`
  has no owner gate). I declined to bulk-release: each needs its checklist
  verified, and clearing other agents' work in bulk off a status field is the
  kind of efficiency that is wrong. Still my recommendation.
- **Codex lane is out for several days.** TASK-263, TASK-268 and TASK-265's
  merge half will not move. Say so plainly rather than leaving them looking
  active — that mislabelling is how TASK-236 sat parked behind a dead owner.

## 7. Before anyone tidies the worktree — READ THIS

Credit to claude-lab-deli, who named this in their handoff; it applies to
everything I wrote today and I had missed it.

The repo has a large **pre-existing dirty worktree** that predates this session
(AGENTS.md says preserve it). Every durable artifact I produced today lives in
it, uncommitted: DEC-029, DEC-030, DEC-031, RISK-0003/0004/0005, the rebuilt
`current-state.md` lane table, all delivery notes, and every emergence record
(SYN-0005, IDEA-0026 through IDEA-0029, EXP-0008 through EXP-0010,
INS-0042 through INS-0046, PROMO-0013, PROMO-0014).

**The asymmetry:** `map.db` transitions survive a worktree clean. The reasoning
does not. Task statuses would remain, and every decision record, risk
assessment, review record, release checklist and insight explaining *why* they
are what they are would be gone. A restart that tidies before committing loses
the entire explanatory layer while leaving the state machine looking healthy —
which is the most misleading possible outcome.

Commit before cleaning, or do not clean.

## 8. One structural trap I was inside and did not name

Also deli's, generalised from my own situation. `validate_task_graph.py:94`
treats `APPROVED` as terminal for the output-path collision check, while `:95`
treats `CHANGES_REQUESTED` as active. So when a task is one half of a
repo-global collision, **approving it clears the red gate and rejecting it
leaves the repo red.** Any reviewer in that seat is structurally rewarded for
approving, and nothing in the tooling warns them.

I hit exactly this on TASK-273 and recused. But I recused because I noticed —
there is no mechanism that would have stopped me, and the incentive is invisible
unless you go looking. If you are ever asked to review a task that is half of a
collision: disclose it in the review record, and consider whether you should be
reviewing it at all.

Nothing is pending review. Nothing is blocked on me.
