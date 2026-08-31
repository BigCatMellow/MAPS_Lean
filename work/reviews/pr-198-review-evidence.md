# PR #198 — memory-trust tool-call gate design note — independent review evidence

reviewer: maps-lean-lola
head_sha: 16da3479276db945c3b31bb697f9fca10eb31519
independent: true
summary: APPROVE (design-only). All 6 dispatch questions answered. The load-bearing claim holds — `HookEvent.BEFORE_SEND` is a live, fired production hook event (`runtime/harness/service.py:275`), fail-closed via `_require_canonical_enforcement` and already a `CanonicalRunGuard` subscription point. `BEFORE_TOOL`/`AFTER_TOOL` confirmed as zero-firing-site enum members (correctly a MUST-NOT). The guard re-derives the verdict via `admit_memory_evidence()` and does not trust the payload's stated `admission`. Provenance flow is specified as a contract, not hand-waved. Judgment on the missing `send()` caller: the seam genuinely exists — "first slice" is the right framing, matching the merged SEC3 (#194) and SEC4 (#192) guard-ahead-of-caller precedent. One recommended (non-blocking) addition noted in §7.

## Method

Own detached worktree at PR #198 head (`d20440c`, rebased to `b976d4b` onto
`origin/main` = `5b76458` to bind this evidence). `git fetch origin main` first.
Every callsite claim in the note re-verified by direct `/usr/bin/grep` / file
read at HEAD (rule 14). Design-only review — no mutation testing per dispatch.

## 1. Six dispatch questions — all answered

| Q | Where | Verdict |
|---|---|---|
| Tool-call definition + seam | §1a/1b/1c | Answered. MAPS_Lean does not sit in the driven agent's tool loop; the orchestrator-side analog is `HarnessService.send()` payload injection, gated at `BEFORE_SEND`. |
| Block vs warn vs allow per trust class + reuse `admit_memory_evidence()` | §Q2 | Answered. `MemoryAdmission` → `HookDirective` projection: `LOAD`→ALLOW, `WITHHOLD`→ALLOW if referenced / DENY if embedded, `DENY`→DENY, missing annotation→DENY. DENY-only, no warn tier in slice 1. No new table — calls the existing pure function. |
| Smallest first slice (rule 8) | §Q3 | Answered. One guard (`MemoryProvenanceGuard`), one event (`BEFORE_SEND`), one composition line in `build_canonical_harness_service`. New `HookEnforcement.MEMORY_PROVENANCE` enum member. |
| Provenance flow | §Q4 | Answered — see §3 below. |
| Interaction with plan-level gate | §Q5 | Answered. Strictly downstream, defense-in-depth, same decision function + mappings, two enforcement points, no divergent policy. |
| STOP / MUST-NOT for impl | §Q6 | Answered. 11 MUST-NOTs + 3 STOP conditions, each concrete. |

## 2. Load-bearing claim — `BEFORE_SEND` is live — CONFIRMED

`/usr/bin/grep -rn "BEFORE_SEND\|before_send" runtime/`:

- `runtime/harness/hooks.py:20` — `BEFORE_SEND = "before_send"` (enum member).
- `runtime/harness/service.py:270` — `self._require_canonical_enforcement(HookEvent.BEFORE_SEND, "send")` inside `HarnessService.send()` (fail-closed: a consequential op with no guard is refused).
- `runtime/harness/service.py:275-284` — `self.hooks.run(HookEvent.BEFORE_SEND, self._context("send", …, details={"payload": dict(payload)}))`; `if not before.permitted: return self._hook_block("send", before)` **before** `adapter.send(...)`. The payload is in the hook context exactly as the note claims.
- `runtime/policy/harness_guard.py:243` — `CanonicalRunGuard` registers on `(RUN_STARTING, BEFORE_SEND, BEFORE_RESUME, SESSION_STOPPING)`. So `BEFORE_SEND` is a **live subscription point with an existing guard**.

Read `service.py:255-287` directly — matches the note's §1b description line-for-line (fires the event, fail-closes, payload visible). **The seam is real; the seam-choice does not collapse.**

## 3. Rejected alternative — `BEFORE_TOOL` / `AFTER_TOOL` — CONFIRMED zero firing sites

`/usr/bin/grep -rn "BEFORE_TOOL\|AFTER_TOOL\|before_tool\|after_tool" runtime/`
→ **only** `runtime/harness/hooks.py:14-15` (the two enum definitions). No
`hooks.run(HookEvent.BEFORE_TOOL, …)` anywhere. Firing one needs an
adapter-loop interception point that does not exist. The note is correct to
make proposing/firing them a MUST-NOT for slice 1 (§1a, §Q6 MUST-NOT 1).

## 4. Judgment call — the missing `HarnessService.send()` production caller

Dispatch point 4 asks whether the seam genuinely exists or whether the missing
`send()` caller should make this a new-seam-justification note.

**My judgment: the seam genuinely exists. "First slice" is the correct
framing.**

- `/usr/bin/grep -rn "\.send(" runtime/` → `HarnessService.send` has **no**
  production caller (only `AdapterContractMixin` in `contract.py:51` and the
  adapter's internal `backend.send`). The note states this plainly (§1c, §7).
- **But the same is true of the two guards MAPS_Lean has already merged**:
  - `/usr/bin/grep -rn "\.stop(" runtime/` → `HarnessService.stop()` (SEC3's
    `BEFORE_DESTRUCTIVE_ACTION` firing site, PR #194 `d810509`) has **no**
    production caller either — only `contract.py:55` + adapter internal.
  - `load_catalog_skill()` (SEC4's "first real refusal", PR #192) has no
    production caller — the checklist SEC4 row says so verbatim.
- MAPS_Lean's established, reviewed, merged pattern is therefore
  **guard-ahead-of-caller, composed default-off, first production exposure
  gates the status flip**. This note follows that precedent faithfully.
- The distinction that matters: a *caller*-maturity gap is not a *seam* gap.
  `BEFORE_SEND` is a fired event (§2), with an existing fail-closed
  enforcement requirement, an existing guard, and an existing composition
  root. Adding `HookEnforcement.MEMORY_PROVENANCE` is identical-in-kind to
  SEC3 adding `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` (verified:
  `HookEnforcement` currently has exactly `CANONICAL_RUN` +
  `DESTRUCTIVE_EXTERNAL_ACTION`, `hooks.py:51-52`) — not a schema change.
- The dispatch's own STOP condition ("no seam → justify a new seam") is not
  triggered because `BEFORE_SEND` is not a new seam.

The note ships against a synthetic-payload test, ahead of the caller, exactly
as SEC3 did — and §7 + §Q6 STOP condition 1 correctly say that being forced to
build a production `send()` caller or a payload assembler *as part of this
slice* is a STOP-and-escalate. That guard rail is in place.

## 5. Guard re-derives, does not trust the payload — CONFIRMED

§Q4: "The guard **re-derives** the admission from `trust_class` via
`admit_memory_evidence()` rather than trusting the assembler's stated
`admission` — the annotation is an identifier + class claim, and the
authoritative decision stays in the one pure function (rule 12: no second
derivation)." §Q3 repeats it ("do **not** trust the assembler's stated
`admission` — re-derive it, fail-closed"). The Resume prompt's test list
includes "decision re-derived not trusted from the annotation".

Verified `admit_memory_evidence(trust_class, *, stale, unknown_admission)` is
pure and deterministic (`runtime/policy/memory_trust_gate.py:99-156`), and that
`unknown_admission` **must not be `LOAD`** (raises `MemoryTrustGateError`) — so
the fail-closed posture the note describes for the unknown/unannotated case is
enforced by the function itself. The note's projection onto `HookDirective` and
its DENY-only stance (no `REQUIRE_APPROVAL`) match `DestructiveExternalActionGuard`'s
own documented rationale (`destructive_action_guard.py:25-30`: nothing catches
`APPROVAL_REQUIRED` and resumes, so it would be a worse-labelled DENY).

## 6. Diff in-bounds — CONFIRMED

`git show` on the note commit: two files —
`work/notes/2026-08-31-memory-trust-tool-call-gate-design.md` (new, +388) and
`work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1). The 6.22 change is a single
appended sentence ("Tool-call gate design pending: …") on the evidence text;
`| 6.22 | Memory trust classes | IN PROGRESS |` is unchanged — **no status
flip**. No `runtime/`, no `schema.sql`, no test file. Within the output
boundary.

## 7. Recommended (non-blocking) addition

The `WITHHOLD` → "ALLOW iff referenced / DENY iff embedded" branch (§Q2 row 2)
depends on the assembler setting the annotation's `"embedded": bool` field
honestly, and MUST-NOT 6 correctly forbids the guard from sniffing payload text
to check. The fail-closed `MEMORY_PROVENANCE_UNVERIFIED` branch catches a
*missing* annotation but not a *false* `embedded: False` on text that is in
fact embedded. This is the same residual trust SEC3 carries (the caller
declares `destructive: bool` honestly), so it is acceptable for slice 1 — but
the note should **state it explicitly** as a known limitation ("slice 1 trusts
the assembler for `embedded` accuracy; a content-hash binding of annotation to
payload body is a candidate follow-up") rather than leave it implicit. A
one-paragraph addition to §Q4 or the "Deferred" list. Not a blocker.

## Verdict

**APPROVE.** Design-only, in-bounds, no status flip. All 6 questions answered.
`BEFORE_SEND` confirmed as a live fired production hook event with an existing
guard-composition pattern; `BEFORE_TOOL`/`AFTER_TOOL` confirmed inert and
correctly a MUST-NOT. Provenance flow specified as an enforceable contract with
fail-closed backstop, guard re-derives rather than trusts the payload. The
missing `send()` caller does not sink the note: the seam exists, and
guard-ahead-of-caller is the merged MAPS_Lean precedent (SEC3 #194, SEC4 #192).
One recommended non-blocking addition (§7). No CHANGES REQUESTED.
