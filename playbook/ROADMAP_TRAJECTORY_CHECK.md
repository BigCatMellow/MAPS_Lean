# Roadmap Trajectory Check: Are We Still On Track

[PROGRAM_STEERING.md](PROGRAM_STEERING.md) asks whether one candidate task is the
right work now. This method asks the larger question: **given what the project has
learned, is the roadmap itself still pointing toward DONE?**

This is roadmap maintenance under [`AGENTS.md`](../AGENTS.md), not a second
approval layer or authority store.

## When to run it

Run at natural work-arc boundaries, not after every task:

- after a meaningful batch/phase;
- when evidence contradicts a roadmap assumption;
- when a discovered blocker changes several planned items;
- when the remaining checklist is mostly conditional/blocked; or
- when repeated task-level steering suggests the priority model itself is stale.

## The check

**Derive the work arc from a commit range, never a hand-listed set of PR
numbers.** The arc is `<last-check-commit>..HEAD`, where `<last-check-commit>` is
the squash-merge commit on `main` of the previous `Roadmap trajectory check #N`
PR (find it with `git log --oneline --grep='Roadmap trajectory check' main | head -1`).
Enumerate the arc with `git log --oneline <last-check-commit>..HEAD` and check
every PR in that output. Hand-listing PRs (e.g. "PRs #194–#207") silently drops
any PR merged outside the guessed range — this happened to check #11, which was
dispatched as "#202–#207" but actually owed "#194–#207".

1. **Re-verify reality.** Enumerate the arc as above, then spot-check current
   roadmap/checklist claims across it against the actual merged code, tests, PRs,
   artifacts, or other authoritative evidence.
2. **Name what changed.** Record new evidence that materially changes assumptions,
   dependencies, risk, priority, scope, or the route to DONE.
3. **Choose a trajectory action.** `CONTINUE`, `REPRIORITIZE`, `RESEARCH`,
   `CUT SCOPE`, `ADD IN-SCOPE WORK`, or `STOP`. Use a challenger/helper when a
   consequential choice is genuinely uncertain.
4. **Apply the decision.** The orchestration operator updates the roadmap/status
   truth and continues when the change remains inside the approved envelope.
   Human reauthorization is required only when the proposed trajectory materially
   changes the approved objective/scope/permission envelope or requires a
   human-only preference/authority decision.
5. **Leave compact evidence.** A short trajectory note may record what was checked,
   what changed, and why. The note is evidence; update the canonical roadmap or
   checklist itself when the plan/status changes.

## Friction-log consumption (every pass)

Every trajectory-check pass must skim
[`work/coordination/FRICTION_LOG.md`](../work/coordination/FRICTION_LOG.md) for
entries with `verified: UNVERIFIED` or `countermeasure: none yet`. For each such
entry, do one of:

- **close it** — confirm the countermeasure is live and append a dated
  `follow-up` line saying how it was verified;
- **verify it against real system state** — check the named file/mechanism
  actually exists and behaves as claimed, then record the result; or
- **escalate it** — surface it as in-scope trajectory work or an operator
  decision.

Record in the trajectory note that the log was reviewed and what was found
(even "nothing open"). This is the consumption half of the continuous-improvement
("triage") loop; capture is owned by
[`REPAIR_AND_LEARNING.md`](REPAIR_AND_LEARNING.md).

## Roadmap/status truth rule

Keep **one canonical live status view per program**. Do not accumulate parallel
per-session or per-sub-roadmap status trackers.

A status claim such as `DONE`, `IN PROGRESS`, or `BLOCKED` is a consequential
fact when future orchestration will rely on it. Therefore:

- support material status changes with a short evidence pointer (PR, path, test,
  artifact, or equivalent);
- update the canonical status view in the same work arc as the change it reports;
- do not mark work `DONE` from formatting/prose review alone;
- for consequential/broad status updates, use an independent spot-check of sample
  claims against real evidence; and
- do not let the session that changed implementation silently turn its own
  unsupported summary into program truth.

This rule belongs here because it protects roadmap trust. Worker selection for
the check itself belongs in
[MODEL_CAPABILITY_ROUTING.md](MODEL_CAPABILITY_ROUTING.md).

## What this is not

- Not a replacement for the program's canonical roadmap/checklist.
- Not another mutable task or authority store.
- Not a reason to pause for human approval before continuing.
- Not permission to create unrelated new scope because it looks valuable.
- Not a requirement to write a trajectory note after every task.

A trajectory note preserves reasoning/evidence. The canonical roadmap/checklist
owns the actual plan/status.

## Relationship to task-level steering

```text
AGI_STANDARD.md              → is this task clear enough to execute?
PROGRAM_STEERING.md          → is this the right task now?
ROADMAP_TRAJECTORY_CHECK.md  → is the roadmap still right given current evidence?
```

All three are orchestration methods. None is a routine human approval gate.

When a pass finds nothing substantive after passes that found something,
[`TENTH_SEAT_REVIEW.md`](TENTH_SEAT_REVIEW.md) Trigger 2 activates and its §7
"signs this has gone wrong" duty falls to whoever runs the next pass — read it
before recording a clean result.
