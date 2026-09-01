# PR #228 review evidence — Roadmap trajectory check #14

reviewer: maps-lean-nava
head_sha: 1df0fd3a3cebf3ef34afbfa1717eccdf1ece515f
independent: true
summary: APPROVE — verification-only review; arc is range-derived (8c5455b..HEAD = #221/#223/#224/#225/#226/#227), every status/code citation checks against merged code at HEAD, the §2 substantive finding (the SEC4 capability DENY at context_builder.py:399-406 runs before the trust gate, never calls admit_memory_evidence, yet records into the shared memory_trust_gate tally that coverage["memory_trust_gate_note"] describes as admit_memory_evidence-only) is REAL and I confirm my own #225 review missed it, scoreboard re-derives to 16/13/6 (7th consecutive), Tenth-Seat Trigger 2 correctly does not fire (substantive finding present), no checklist status flip (0 checklist changes), CONTINUE is defensible, and the proposed check-#15 next-3 are sound.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Arc derived from commit range, not hand-listed | PASS. `git log --oneline --grep='Roadmap trajectory check' main | head -1` → `8c5455b … (#222)`. `git log --oneline 8c5455b..e0c43c8` → `#226`, `#227`, `#225`, `#224`, `#223`, `#221`. Note's arc block matches verbatim; 6 PRs enumerated by range. |
| 2 | Every status/code citation vs merged code at HEAD (rule 14) — esp. §2 defect + "check-#13 §5 next-3 all landed" | PASS. **§2 defect — verified real:** the SEC4 DENY (`if not within: tally.record(MemoryAdmission.DENY, "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE"); continue`) at `context_builder.py:399-406`, after `if not matched: continue` and before `lifecycle_state = …` / `admit_memory_evidence(...)` — bypasses `admit_memory_evidence` and writes into `tally` (same `_AdmissionTally` → `memory_trust_gate_denied` / `_reasons`). `coverage["memory_trust_gate_note"]` still says "every memory-like item passed admit_memory_evidence(); its MemoryTrustClass alone decides … Denied items … counted here" — a direct contradiction for a capability-DENY'd Skill. **check-#13 §5 next-3:** (1) 6.9/S6 body loading → #221; (2) SEC4 capability manifest slice 2 → #225 (`capability_policy.py`, `_select_skills` intersection — at `_select_skills` rather than the activation seam #13 §5 named, per #223's re-scoping, disclosed in §1d); (3) 6.21 next verb → #226 (`_latest_completed_review_for` replaces `_review_by_id`, `next_step: {state: "REVIEW_RECORDED"}`). All landed. Other §1 spot-checks (`_review_by_id` gone, `authorized_operators` absent, no `record_review`/schema change in #226) confirmed. |
| 3 | Scoreboard re-derived = 16/13/6 (7th consecutive) from the master-inventory §7 table | PASS. `awk '/^\| 6\.[0-9]/' work/roadmaps/CAPABILITY_CHECKLIST.md | grep -oE 'DONE\|IN PROGRESS\|NOT STARTED' | sort | uniq -c` → `16 DONE / 13 IN PROGRESS / 6 NOT STARTED`. IN PROGRESS list identical to check #12's 13. Checks #8–#14 = 7 consecutive passes at 16/13/6. |
| 4 | Tenth-Seat Trigger 2 correctly did NOT fire; §7 warning-signs worked through; check-#15 caveat recorded | PASS. Trigger 2 armed for #14 (#12 + #13 both substantive). Does not fire because §2 is a "changed picture" finding (a provably-wrong claim in merged `runtime/` code). §7's three signs each addressed in §4. §7 recorded for #15: Trigger 2 re-arms, §2 must land by #15 or be re-flagged. |
| 5 | Friction entry 3 → VERIFIED justified; entry 5 recurrence | PASS. Entry 3's bar ("a coordinator arc completing without a disruptive mid-arc rotation under the new threshold") met — session 16 ran #221→#227 + checks #13/#14 with no disruptive rotation; both #13 follow-up bullets discharged. PARTIAL → VERIFIED justified, follow-up line appended. Entry 5: 3rd consecutive no-recurrence arc, stays open per its own clause. `FRICTION_LOG.md` diff is two appended follow-up blocks, no past-entry edits. |
| 6 | NO checklist status flip (0 checklist changes) | PASS. `git show HEAD --stat` = exactly 2 files: the trajectory note (+361), `FRICTION_LOG.md` (+10). `CAPABILITY_CHECKLIST.md` not touched. |
| 7 | Action CONTINUE defensible | PASS. All 6 arc PRs verify; the one defect (§2) is LOW severity with a clean next-3 follow-up; check-#12's REPRIORITIZE next-3 all landed this arc (the RESEARCH/STOP tripwire "next-3 untouched AND ask #1 unanswered" not met); scoreboard-holding is the designed shape; no status flip warranted or missed; operator ask #1 unchanged. Not REPRIORITIZE, not STOP. |
| 8 | Proposed next-3 for #15 sound | PASS. (1) §2 fix + scope a `_select_skills` doc-drift CI safeguard; (2) `maps flow handoff` impl (#227 DISPATCHABLE); (3) 6.9/S6 slice 2 OR SEC4 activation-time intersection. All three advance IN PROGRESS rows without the operator. |

## Disclosure — this PR's §2 finding is against my own #225 review

The §2 defect is accurate and I confirm my PR #225 review did not catch it: I verified the capability DENY's placement and reason-string surfacing but did not read the `memory_trust_gate_note` prose ~230 lines away in `build_context_plan`'s return, which the DENY now contradicts. Same failure shape as memory `feedback_review_test_set_too_narrow` (adjacent invariant-describing text not swept when the invariant changed); memory updated with this second instance. Severity LOW, note characterises it correctly. This finding being real is exactly why Trigger 2 does not fire.

## Non-blocking

- §3 (6.24 row framing trails its own slice-2 evidence text) — the note correctly declines to edit. No action.
- `runtime.smoke` → `"ok": true`, exit 0 at `e0c43c8`.

## Verdict

APPROVE.
